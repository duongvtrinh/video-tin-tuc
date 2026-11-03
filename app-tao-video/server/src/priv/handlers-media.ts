// Handlers media: tìm ứng viên Wikimedia/stock, gợi ý từ khóa, tải file đã chọn, tạo media AI, render thử template và đọc file media (nguyên khối + theo chunk 2 MiB).
// Chỉ privileged.ts import file này; kiểu tham số/kết quả lấy thẳng từ
// contract tương ứng (ArgsOf/ResOf) để handler không lệch contract.
import type { Factory } from "@space/privileged";
import type { z } from "@hatch/space-sdk";

type ArgsOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["request"]>;
type ResOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["response"]>;

import { closeSync, copyFileSync, existsSync, fstatSync, mkdirSync, openSync, readFileSync, readSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { BIN, FACTORY, HOME, PY3, SEARCH_MEDIA, VENV_PY, brollFileName, mimeForPath, projDir, rand6, randomSuffix, readJson, run, runCaptureJson, sceneImageFileName, withPlanWriteLock, writeJson } from "./core";

export async function searchMedia({ layer, summary, enKeywords, extraKeywords, mediaType, durationSec }: ArgsOf<"searchMedia">): Promise<ResOf<"searchMedia">> {
    const args =
      layer === "wikimedia"
        ? [PY3, SEARCH_MEDIA, "wikimedia", "--summary", summary, "--media-type", mediaType,
           ...(durationSec > 0 ? ["--duration", String(durationSec)] : []),
           ...(extraKeywords ? ["--extra-keywords", extraKeywords] : [])]
        : [PY3, SEARCH_MEDIA, "stock", "--en-keywords", enKeywords, "--media-type", mediaType,
           ...(durationSec > 0 ? ["--duration", String(durationSec)] : [])];
    const { code, out } = await run(args, { timeoutMs: 170_000, cwd: HOME });
    const start = out.indexOf("{");
    if (start < 0) {
      return { candidates: [], queriesTried: [], note: `Lớp tìm kiếm không trả kết quả (mã ${code}): ${out.slice(-300)}` };
    }
    const parsed = JSON.parse(out.slice(start)) as {
      candidates?: Array<Record<string, unknown>>;
      queries_tried?: string[];
      skipped?: string;
      note?: string;
    };
    const candidates = (parsed.candidates ?? []).slice(0, 24).map((c) => ({
      title: String(c["title"] ?? ""),
      pageUrl: String(c["page_url"] ?? ""),
      fileUrl: String(c["file_url"] ?? ""),
      thumbUrl: String(c["thumb_url"] ?? c["file_url"] ?? ""),
      mime: String(c["mime"] ?? ""),
      width: typeof c["width"] === "number" ? c["width"] : null,
      height: typeof c["height"] === "number" ? c["height"] : null,
      durationSec: typeof c["duration_sec"] === "number" ? c["duration_sec"] : null,
      license: String(c["license"] ?? ""),
      author: String(c["author"] ?? "").replace(/<[^>]+>/g, ""),
      score: typeof c["score"] === "number" ? c["score"] : null,
      verdict: String(c["verdict"] ?? ""),
      source: layer === "wikimedia" ? "Wikipedia / Wikimedia Commons" : "Stock (Pixabay/Pexels)",
    }));
    const note =
      parsed.skipped ??
      parsed.note ??
      (candidates.length === 0
        ? "Không có ứng viên nào đạt lọc metadata ở lớp này — thử thêm từ khóa bổ sung hoặc chuyển lớp tiếp theo."
        : "");
    return { candidates, queriesTried: parsed.queries_tried ?? [], note: String(note) };
  }

export async function suggestKeywords({ summary }: ArgsOf<"suggestKeywords">): Promise<ResOf<"suggestKeywords">> {
    const helper = join(HOME, "workspace/company-os/media-search/.app_suggest.py");
    if (!existsSync(helper)) {
      writeFileSync(
        helper,
        [
          "import json, sys",
          "sys.path.insert(0, sys.path[1] if len(sys.path) > 1 else '.')",
          "import importlib.util",
          "spec = importlib.util.spec_from_file_location('sm', sys.argv[2])",
          "sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)",
          "summary = sys.argv[3]",
          "cluster = sm.match_cluster(summary) if hasattr(sm, 'match_cluster') else None",
          "if cluster is None:",
          "    # Fallback: find cluster whose any phrase appears in the summary text",
          "    low = summary.lower()",
          "    for c in sm.CONCEPT_CLUSTERS:",
          "        phrases = c.get('vi', []) + c.get('en', [])",
          "        if any(p.lower() in low for p in phrases):",
          "            cluster = c; break",
          "print(json.dumps({'cluster': cluster}, ensure_ascii=False))",
          "",
        ].join("\n"),
        "utf8",
      );
    }
    try {
      const parsed = (await runCaptureJson(
        [PY3, helper, join(HOME, "workspace/company-os/media-search"), SEARCH_MEDIA, summary],
        60_000,
      )) as { cluster: { id?: string; vi?: string[]; en?: string[] } | null };
      const cluster = parsed.cluster;
      if (!cluster) {
        return { clusterId: null, viPhrases: [], enPhrases: [], noCluster: true };
      }
      return {
        clusterId: cluster.id ?? null,
        viPhrases: cluster.vi ?? [],
        enPhrases: cluster.en ?? [],
        noCluster: false,
      };
    } catch {
      return { clusterId: null, viPhrases: [], enPhrases: [], noCluster: true };
    }
  }

export async function pickMedia({ projectId, sceneOrder, partId, fileUrl, mediaType, source, pageUrl, license, author, score, verdict, runnerUpScore }: ArgsOf<"pickMedia">): Promise<ResOf<"pickMedia">> {
    const dir = projDir(projectId);
    const planPath = join(dir, "broll-plan.json");
    type PlanShape = {
      scenes?: Array<{
        order?: number;
        imageFile?: string;
        mediaSource?: unknown;
        parts?: Array<{ id: string; broll?: Record<string, unknown> }>;
      }>;
    };
    const plan0 = readJson<PlanShape | null>(planPath, null);
    if (!plan0) throw new Error("Project chưa có plan");
    const ext = mediaType === "video" ? "mp4" : (fileUrl.split("?")[0]?.split(".").pop()?.toLowerCase() ?? "jpg");
    const safeExt = ["jpg", "jpeg", "png", "webp", "mp4", "webm"].includes(ext) ? ext : "jpg";
    const mediaSource = {
      source,
      ...(pageUrl ? { pageUrl } : {}),
      ...(license ? { license } : {}),
      ...(author ? { author } : {}),
      ...(score !== null ? { score } : {}),
      // Picking from the candidate grid means the file was visually
      // inspected in the app — record that, plus the verdict and the
      // runner-up score, as provenance in the plan for the automated
      // pipeline.
      ...(verdict ? { verdict } : {}),
      ...(runnerUpScore !== null && runnerUpScore !== undefined
        ? { runnerUpScore }
        : {}),
      visuallyChecked: true,
    };
    // Tên file tất định theo (project, cảnh, part): tính trước từ bản
    // plan hiện tại, tải file (việc chậm) ngoài khóa, rồi mới vào khóa
    // đọc lại plan và ghi — để nhiều lần gọi song song cho cùng project
    // không ghi đè mất cập nhật của nhau.
    let fileName = "";
    let destDir = "";
    if (partId) {
      const scene = (plan0.scenes ?? []).find((s) => s.order === sceneOrder);
      const part = scene?.parts?.find((p) => p.id === partId);
      if (!part) throw new Error(`Không thấy part ${partId}`);
      const partIdx = (scene?.parts ?? []).indexOf(part) + 1;
      fileName = brollFileName(projectId, sceneOrder, partIdx, safeExt);
      destDir = join(dir, "build/media/broll");
    } else {
      const scene = (plan0.scenes ?? []).find((s) => s.order === sceneOrder);
      if (!scene) throw new Error(`Không thấy cảnh ${sceneOrder}`);
      fileName = `seg_${sceneOrder}_${rand6(projectId, "img", sceneOrder)}.${safeExt}`;
      destDir = join(dir, "build/media/images");
    }
    mkdirSync(destDir, { recursive: true });
    const res = await fetch(fileUrl);
    if (!res.ok) throw new Error(`Tải file thất bại: HTTP ${res.status}`);
    writeFileSync(join(destDir, fileName), Buffer.from(await res.arrayBuffer()));
    await withPlanWriteLock(projectId, () => {
      const plan = readJson<PlanShape | null>(planPath, null);
      if (!plan) throw new Error("Project chưa có plan");
      if (partId) {
        const scene = (plan.scenes ?? []).find((s) => s.order === sceneOrder);
        const part = scene?.parts?.find((p) => p.id === partId);
        if (!part) throw new Error(`Không thấy part ${partId}`);
        part.broll = {
          ...(part.broll ?? {}),
          mediaType,
          keepAudio: false,
          file: fileName,
          mediaSource,
        };
      } else {
        const scene = (plan.scenes ?? []).find((s) => s.order === sceneOrder);
        if (!scene) throw new Error(`Không thấy cảnh ${sceneOrder}`);
        scene.imageFile = fileName;
        scene.mediaSource = mediaSource;
      }
      writeJson(planPath, plan);
    });
    return { fileName };
  }

export async function generateAiMedia({ projectId, sceneOrder, partId, prompt, mediaType }: ArgsOf<"generateAiMedia">): Promise<ResOf<"generateAiMedia">> {
    const dir = projDir(projectId);
    const planPath = join(dir, "broll-plan.json");
    type PlanShape = {
      scenes?: Array<{
        order?: number;
        imageFile?: string;
        mediaSource?: unknown;
        parts?: Array<{ id: string; broll?: Record<string, unknown> }>;
      }>;
    };
    const plan0 = readJson<PlanShape | null>(planPath, null);
    if (!plan0) throw new Error("Project chưa có plan");
    const isVideo = mediaType === "video";
    if (!partId && isVideo) throw new Error("Ảnh cảnh không thể là video — hãy gắn video vào b-roll của part");
    // Tên file tất định theo (project, cảnh, part): tính trước để phần
    // tạo media (việc chậm, hàng chục giây) chạy SONG SONG cho nhiều
    // cảnh/part; chỉ đoạn ghi plan ở cuối mới vào khóa theo project.
    let fileName = "";
    let destDir = "";
    if (partId) {
      const scene = (plan0.scenes ?? []).find((s) => s.order === sceneOrder);
      const part = scene?.parts?.find((p) => p.id === partId);
      if (!part) throw new Error(`Không thấy part ${partId}`);
      const partIdx = (scene?.parts ?? []).indexOf(part) + 1;
      fileName = brollFileName(projectId, sceneOrder, partIdx, isVideo ? "mp4" : "jpg");
      destDir = join(dir, "build/media/broll");
    } else {
      const scene = (plan0.scenes ?? []).find((s) => s.order === sceneOrder);
      if (!scene) throw new Error(`Không thấy cảnh ${sceneOrder}`);
      fileName = sceneImageFileName(projectId, sceneOrder);
      destDir = join(dir, "build/media/images");
    }
    const cmd = [
      "/opt/hatch/bin/media-generation",
      "--media-subagent-output-type",
      mediaType,
      "--orientation",
      "vertical",
      "--conversation-json",
      JSON.stringify([{ text: prompt }]),
    ];
    const { code, out } = await run(cmd, { timeoutMs: 590_000, cwd: HOME });
    if (code !== 0) throw new Error(`Tạo media AI thất bại (mã ${code}): ${out.slice(-300)}`);
    const start = out.indexOf("{");
    const parsed = JSON.parse(out.slice(start)) as { media_paths?: string[] };
    const src = parsed.media_paths?.[0];
    if (!src || !existsSync(src)) throw new Error("Công cụ tạo media không trả về file");
    const mediaSource = { source: "AI (fallback)", reason: "Không tìm được file đạt yêu cầu ở Wikipedia/stock", visuallyChecked: false, prompt };
    const dest = join(destDir, fileName);
    mkdirSync(destDir, { recursive: true });
    if (isVideo) {
      copyFileSync(src, dest);
    } else {
      const conv = await run(["ffmpeg", "-y", "-v", "error", "-i", src, dest], { timeoutMs: 120_000 });
      if (conv.code !== 0) copyFileSync(src, dest);
    }
    await withPlanWriteLock(projectId, () => {
      const plan = readJson<PlanShape | null>(planPath, null);
      if (!plan) throw new Error("Project chưa có plan");
      if (partId) {
        const scene = (plan.scenes ?? []).find((s) => s.order === sceneOrder);
        const part = scene?.parts?.find((p) => p.id === partId);
        if (!part) throw new Error(`Không thấy part ${partId}`);
        part.broll = { ...(part.broll ?? {}), mediaType, keepAudio: false, file: fileName, mediaSource };
      } else {
        const scene = (plan.scenes ?? []).find((s) => s.order === sceneOrder);
        if (!scene) throw new Error(`Không thấy cảnh ${sceneOrder}`);
        scene.imageFile = fileName;
        scene.mediaSource = mediaSource;
      }
      writeJson(planPath, plan);
    });
    return { fileName };
  }

export async function renderTemplatePreview({ templateId, inputs }: ArgsOf<"renderTemplatePreview">): Promise<ResOf<"renderTemplatePreview">> {
    const outPath = join(FACTORY, `.app-tmp-template-${templateId}-${randomSuffix()}.png`);
    // The template engine consumes text inputs; coerce any numeric/boolean
    // values (e.g. bar-chart w1..w4 written as numbers by the pipeline).
    const strInputs: Record<string, string> = {};
    for (const [k, v] of Object.entries(inputs ?? {})) {
      strInputs[k] = v === null || v === undefined ? "" : String(v);
    }
    const { code, out } = await run(
      [VENV_PY, join(BIN, "render_template.py"), templateId, JSON.stringify(strInputs), "720", "1280", outPath],
      { timeoutMs: 110_000 },
    );
    if (code !== 0 || !existsSync(outPath)) {
      throw new Error(`Render template thất bại: ${out.slice(-300)}`);
    }
    const b64 = readFileSync(outPath).toString("base64");
    rmSync(outPath, { force: true });
    return { pngBase64: b64 };
  }

export async function getMediaUrl({ projectId, relPath }: ArgsOf<"getMediaUrl">): Promise<ResOf<"getMediaUrl">> {
    const dir = projDir(projectId);
    const clean = relPath.replace(/^\/+/, "");
    if (clean.includes("..")) throw new Error("Đường dẫn không hợp lệ");
    const full = join(dir, clean);
    if (!existsSync(full)) throw new Error(`Không thấy file ${clean}`);
    const mime = mimeForPath(full);
    const buf = readFileSync(full);
    // Inline data URLs are only safe for small files: base64 inflates the
    // payload by ~4/3 and the whole thing rides in ONE action response,
    // which the daemon truncates once it grows too large (a 41.5 MB MP4
    // became a ~55 MB response and died with "response was truncated").
    // Fail fast with a clear message instead; large files must go through
    // getMediaChunk, which the client uses for video/MP4 and downloads.
    if (buf.length > 4_000_000) {
      throw new Error(
        "File quá lớn để tải nội tuyến trong một phản hồi — hãy dùng đường tải theo từng phần (áp dụng cho video/MP4 và nút Tải MP4).",
      );
    }
    return { dataUrl: `data:${mime};base64,${buf.toString("base64")}` };
  }

export async function getMediaChunk({ projectId, relPath, offset, length }: ArgsOf<"getMediaChunk">): Promise<ResOf<"getMediaChunk">> {
    const dir = projDir(projectId);
    const clean = relPath.replace(/^\/+/, "");
    if (clean.includes("..")) throw new Error("Đường dẫn không hợp lệ");
    // Factory audio assets (BGM tracks and SFX files live in the repo, not
    // inside a project folder) are served through the same chunked path
    // under the "__factory__/" prefix so the preview player can stream a
    // large BGM file in 2 MiB chunks exactly like a rendered MP4.
    const full = clean.startsWith("__factory__/")
      ? join(FACTORY, clean.slice("__factory__/".length))
      : join(dir, clean);
    if (!existsSync(full)) throw new Error(`Không thấy file ${clean}`);
    const mime = mimeForPath(full);
    const fd = openSync(full, "r");
    try {
      const totalSize = fstatSync(fd).size;
      const start = Math.min(Math.max(offset, 0), totalSize);
      const want = Math.min(Math.max(length, 1), 2_097_152, totalSize - start);
      if (want <= 0) {
        return { base64: "", offset: start, chunkBytes: 0, totalSize, eof: true, mime };
      }
      const buf = Buffer.alloc(want);
      const bytesRead = readSync(fd, buf, 0, want, start);
      return {
        base64: buf.subarray(0, bytesRead).toString("base64"),
        offset: start,
        chunkBytes: bytesRead,
        totalSize,
        eof: start + bytesRead >= totalSize,
        mime,
      };
    } finally {
      closeSync(fd);
    }
  }
