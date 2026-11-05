// Handlers media: tìm ứng viên Wikimedia/stock, gợi ý từ khóa, tải file đã chọn, tạo media AI, render thử template và đọc file media (nguyên khối + theo chunk 2 MiB).
// Chỉ privileged.ts import file này; kiểu tham số/kết quả lấy thẳng từ
// contract tương ứng (ArgsOf/ResOf) để handler không lệch contract.
import type { Factory } from "@space/privileged";
import type { z } from "@hatch/space-sdk";

type ArgsOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["request"]>;
type ResOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["response"]>;

import { closeSync, copyFileSync, existsSync, fstatSync, mkdirSync, openSync, readFileSync, readSync, rmSync, statSync, writeFileSync } from "node:fs";
import { basename, dirname, join } from "node:path";
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
    // B40 (06/11/2026, lệnh CEO, lựa chọn A): parse lỗi thì trả note rõ
    // thay vì ném lỗi thô — output có thể lẫn dòng cảnh báo chứa "{".
    let parsed: {
      candidates?: Array<Record<string, unknown>>;
      queries_tried?: string[];
      skipped?: string;
      note?: string;
    };
    try {
      parsed = JSON.parse(out.slice(start)) as typeof parsed;
    } catch {
      return { candidates: [], queriesTried: [], note: `Không đọc được kết quả tìm kiếm (mã ${code}): ${out.slice(-300)}` };
    }
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
    // B6 (05/11/2026, lệnh CEO): thư mục media-search lấy từ chính
    // SEARCH_MEDIA (đã sửa đường dẫn ở A25) để chỉ còn một nguồn chuẩn
    // duy nhất — đường cũ ~/workspace/company-os/... không tồn tại nên
    // lần gọi đầu tiên lỗi 500 ở writeFileSync ngoài try/catch.
    const mediaSearchDir = dirname(SEARCH_MEDIA);
    const helper = join(mediaSearchDir, ".app_suggest.py");
    const noCluster = { clusterId: null, viPhrases: [], enPhrases: [], noCluster: true } as const;
    if (!existsSync(helper)) {
      try {
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
      } catch {
        return { ...noCluster };
      }
    }
    try {
      const parsed = (await runCaptureJson(
        [PY3, helper, mediaSearchDir, SEARCH_MEDIA, summary],
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
        isMossGrid?: boolean;
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
    // 11A: tai file co gioi han — timeout 60s, dung luong toi da 100 MB,
    // kiem content-type va magic bytes co ban truoc khi ghi file.
    // Nguong 100 MB la nguong rong, du cho anh/video bao chi, chi de chan
    // tai vo han; content-type octet-stream duoc chap nhan vi mot so
    // server bao khong ro dinh dang, khi do magic bytes se quyet dinh.
    // B24 (06/11/2026, lệnh CEO, lựa chọn A): đọc body theo chunk và hủy
    // ngay khi vượt 100 MB — trước đây tải hết vào RAM rồi mới kiểm;
    // timer 60s giữ suốt quá trình đọc body (trước đây clear ngay sau
    // khi headers về nên body tải chậm có thể chạy quá 60s).
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 60_000);
    let buf: Buffer;
    try {
      let res: Response;
      try {
        res = await fetch(fileUrl, { signal: controller.signal });
      } catch (e) {
        throw new Error(`Tải file thất bại: quá thời gian 60s hoặc lỗi mạng (${e instanceof Error ? e.message : String(e)})`);
      }
      if (!res.ok) throw new Error(`Tải file thất bại: HTTP ${res.status}`);
      const contentType = res.headers.get("content-type")?.split(";")[0]?.trim().toLowerCase() ?? "";
      if (contentType && contentType !== "application/octet-stream") {
        const want = mediaType === "video" ? "video/" : "image/";
        if (!contentType.startsWith(want)) throw new Error(`Tải file thất bại: content-type ${contentType} không khớp mediaType ${mediaType}`);
      }
      const declared = Number(res.headers.get("content-length"));
      if (Number.isFinite(declared) && declared > 100 * 1024 * 1024) {
        throw new Error("Tải file thất bại: file vượt 100 MB");
      }
      if (!res.body) throw new Error("Tải file thất bại: server không trả về nội dung");
      const chunks: Buffer[] = [];
      let total = 0;
      const reader = res.body.getReader();
      try {
        for (;;) {
          const { done, value } = await reader.read();
          if (done) break;
          total += value.byteLength;
          if (total > 100 * 1024 * 1024) {
            await reader.cancel();
            throw new Error("Tải file thất bại: file vượt 100 MB");
          }
          chunks.push(Buffer.from(value));
        }
      } catch (e) {
        if (e instanceof Error && e.name === "AbortError") {
          throw new Error("Tải file thất bại: quá thời gian 60s hoặc lỗi mạng (AbortError)");
        }
        throw e;
      } finally {
        reader.releaseLock();
      }
      buf = Buffer.concat(chunks, total);
    } finally {
      clearTimeout(timer);
    }
    if (mediaType !== "video") {
      // Magic bytes co ban cho anh: JPEG FF D8 FF, PNG 89 50 4E 47,
      // WEBP RIFF....WEBP. Khong decode day du o day; viec decode day
      // du thuoc ve buoc soi truc quan/render, khong phai pickMedia.
      const isJpeg = buf.length >= 3 && buf[0] === 0xff && buf[1] === 0xd8 && buf[2] === 0xff;
      const isPng = buf.length >= 4 && buf[0] === 0x89 && buf[1] === 0x50 && buf[2] === 0x4e && buf[3] === 0x47;
      const isWebp = buf.length >= 12 && buf.toString("ascii", 0, 4) === "RIFF" && buf.toString("ascii", 8, 12) === "WEBP";
      if (!isJpeg && !isPng && !isWebp) throw new Error("Tải file thất bại: file ảnh không đúng định dạng JPEG/PNG/WEBP theo magic bytes");
      // Luu y: khong bat buoc magic bytes phai khop phan mo rong suy tu URL,
      // vi URL bao chi co the sai hau to; render/preview doc noi dung file
      // (PIL/ffmpeg sniff) chu khong chi dua vao hau to, nen file van dung duoc.
    }
    writeFileSync(join(destDir, fileName), buf);
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
        // A21 (05/11/2026): đã gắn ảnh thật thì không còn là nền rêu.
        delete scene.isMossGrid;
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
        isMossGrid?: boolean;
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
    // B40 (06/11/2026, lệnh CEO, lựa chọn A): output không có "{" hoặc
    // parse lỗi thì ném lỗi có ngữ cảnh thay vì lỗi JSON thô.
    const start = out.indexOf("{");
    if (start < 0) throw new Error(`Công cụ tạo media không trả JSON: ${out.slice(-300)}`);
    let parsed: { media_paths?: string[] };
    try {
      parsed = JSON.parse(out.slice(start)) as typeof parsed;
    } catch {
      throw new Error(`Công cụ tạo media trả output không đọc được: ${out.slice(-300)}`);
    }
    const src = parsed.media_paths?.[0];
    if (!src || !existsSync(src)) throw new Error("Công cụ tạo media không trả về file");
    const mediaSource = { source: "AI từ prompt", reason: "Không tìm được file đạt yêu cầu ở Wikipedia/stock", visuallyChecked: false, prompt };
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
        // A21 (05/11/2026): đã tạo ảnh AI thì không còn là nền rêu.
        delete scene.isMossGrid;
      }
      writeJson(planPath, plan);
    });
    return { fileName };
  }

  // A22 (05/11/2026, lệnh CEO): xóa ảnh đã gắn của một cảnh — lối thoát
  // duy nhất để thay ảnh thật đã chọn. buildGenImageJobs bỏ qua cảnh đã
  // có ảnh thật nên muốn tạo lại job AI/card thì phải xóa ảnh trước. Xóa
  // file trên đĩa (chỉ trong build/media/images, theo basename) và gỡ
  // imageFile, mediaSource, isMossGrid khỏi plan, trong cùng một khóa ghi
  // plan để plan và đĩa không lệch nhau. Giữ nguyên sceneImagePrompt để
  // lần tạo job sau tạo lại ảnh AI từ prompt đó nếu người dùng muốn.
  export async function clearSceneImage({ projectId, sceneOrder }: ArgsOf<"clearSceneImage">): Promise<ResOf<"clearSceneImage">> {
    const dir = projDir(projectId);
    const planPath = join(dir, "broll-plan.json");
    type PlanShape = {
      scenes?: Array<{
        order?: number;
        imageFile?: string;
        mediaSource?: unknown;
        isMossGrid?: boolean;
      }>;
    };
    let fileName: string | null = null;
    await withPlanWriteLock(projectId, () => {
      const plan = readJson<PlanShape | null>(planPath, null);
      if (!plan) throw new Error("Project chưa có plan");
      const scene = (plan.scenes ?? []).find((s) => s.order === sceneOrder);
      if (!scene) throw new Error(`Không thấy cảnh ${sceneOrder}`);
      fileName = scene.imageFile ?? null;
      if (fileName) {
        const target = join(dir, "build/media/images", basename(fileName));
        if (existsSync(target)) rmSync(target, { force: true });
      }
      delete scene.imageFile;
      delete scene.mediaSource;
      delete scene.isMossGrid;
      writeJson(planPath, plan);
    });
    return { cleared: true, fileName };
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
    // B24 (06/11/2026, lệnh CEO, lựa chọn A): hỗ trợ tiền tố
    // __factory__/ như getMediaChunk, và kiểm kích thước TRƯỚC khi đọc
    // (statSync) thay vì đọc cả file vào RAM rồi mới kiểm.
    const full = clean.startsWith("__factory__/")
      ? join(FACTORY, clean.slice("__factory__/".length))
      : join(dir, clean);
    if (!existsSync(full)) throw new Error(`Không thấy file ${clean}`);
    const st = statSync(full);
    if (!st.isFile()) throw new Error(`Đường dẫn không phải file: ${clean}`);
    // Inline data URLs are only safe for small files: base64 inflates the
    // payload by ~4/3 and the whole thing rides in ONE action response,
    // which the daemon truncates once it grows too large (a 41.5 MB MP4
    // became a ~55 MB response and died with "response was truncated").
    // Fail fast with a clear message instead; large files must go through
    // getMediaChunk, which the client uses for video/MP4 and downloads.
    // Ngưỡng 10.000.000 byte theo quyết định CEO 05/11/2026 (mục 4C).
    if (st.size > 10_000_000) {
      throw new Error(
        "File quá lớn để tải nội tuyến trong một phản hồi — hãy dùng đường tải theo từng phần (áp dụng cho video/MP4 và nút Tải MP4).",
      );
    }
    const mime = mimeForPath(full);
    const buf = readFileSync(full);
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
