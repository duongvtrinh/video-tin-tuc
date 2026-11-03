// Tóm tắt project cho danh sách, chính sách snapshot (giữ 30 bản), ánh
// xạ bước job → lệnh factory, hàng job tạo ảnh cảnh và md5 preview có
// cache theo mtime/size. Chỉ privileged.ts import file này.
import { createHash } from "node:crypto";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  readFileSync,
  readdirSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { basename, join } from "node:path";
import {
  BIN,
  PY3,
  TTS_PY,
  VENV_PY,
  projDir,
  readJson,
  sceneImageFileName,
  writeJson,
} from "./core";

type RawPlan = {
  voice?: string;
  bgm?: { id?: string; file?: string };
  scenes?: Array<{
    order?: number;
    imageFile?: string;
    parts?: Array<{ broll?: { templateId?: string; file?: string; mediaType?: string; sfx?: unknown } }>;
  }>;
};

export function summarize(id: string) {
  const dir = projDir(id);
  const input = readJson<Record<string, unknown>>(join(dir, "input.json"), {});
  const scriptFile = readJson<{ content?: string }>(join(dir, "script.json"), { content: "" });
  const plan = readJson<RawPlan | null>(join(dir, "broll-plan.json"), null);
  const tts = readJson<{ parts?: Array<{ duration?: number }> } | null>(join(dir, "tts.json"), null);
  const scenes = plan?.scenes ?? [];
  const partCount = scenes.reduce((n, s) => n + (s.parts?.length ?? 0), 0);
  const sfxCount = scenes.reduce(
    (n, s) => n + (s.parts ?? []).filter((p) => p.broll?.sfx).length,
    0,
  );
  const imagesDir = join(dir, "build/media/images");
  const brollDir = join(dir, "build/media/broll");
  const imageCount = existsSync(imagesDir)
    ? readdirSync(imagesDir).filter((f) => /\.(jpe?g|png|webp)$/i.test(f)).length
    : 0;
  const videoCount = existsSync(brollDir)
    ? readdirSync(brollDir).filter((f) => /\.mp4$/i.test(f)).length
    : 0;
  const warnings: string[] = [];
  for (const s of scenes) {
    if (s.imageFile && !existsSync(join(imagesDir, s.imageFile))) {
      warnings.push(`Cảnh ${s.order ?? "?"} thiếu file ảnh ${s.imageFile} (render sẽ ra nền đen)`);
    }
  }
  // Pipeline projects leave scene.imageFile null and address images purely
  // by the seg_<order>_* file convention, so the check above never fires
  // for them — a scene with NO image file at all (and no b-roll media for
  // that scene) renders as a solid black clip in render_draft.py, silently.
  // Warn from the actual files on disk so the black render is visible in
  // the project list and the Render tab BEFORE the user exports it.
  const imageFiles = existsSync(imagesDir) ? readdirSync(imagesDir) : [];
  const brollFiles = existsSync(brollDir) ? readdirSync(brollDir) : [];
  for (const s of scenes) {
    if (s.imageFile) continue; // covered by the explicit check above
    const order = s.order;
    if (order === undefined) continue;
    const hasSceneImage = imageFiles.some(
      (f) => f.startsWith(`seg_${order}_`) && /\.(jpe?g|png|webp)$/i.test(f),
    );
    if (hasSceneImage) continue;
    const hasBrollMedia = brollFiles.some((f) =>
      f.startsWith(`broll_seg_${order}_`),
    );
    if (!hasBrollMedia) {
      warnings.push(
        `Cảnh ${order} chưa có ảnh nền nào (không thấy seg_${order}_*.jpg trong build/media/images, cũng không có b-roll) — render sẽ ra nền đen ở cảnh này`,
      );
    }
  }
  const totalDuration =
    tts?.parts && tts.parts.length > 0
      ? tts.parts.reduce((n, p) => n + (p.duration ?? 0), 0)
      : null;
  const isTest = input["isTestClip"] === true || /^(test|mediasrc)/i.test(id);
  if (plan && sfxCount === 0 && partCount > 0) {
    warnings.push("Chưa có SFX nào trong plan — cân nhắc gắn SFX ở hook, điểm móc lại và kết luận");
  }
  const previewPath = join(dir, `export/${id}_preview.mp4`);
  return {
    id,
    name: String(input["name"] ?? id),
    topic: String(input["topic"] ?? ""),
    createdAt: String(input["created_at"] ?? ""),
    modifiedAt: statSync(dir).mtimeMs,
    sceneCount: scenes.length,
    partCount,
    totalDurationSec: totalDuration,
    voice: String(plan?.voice ?? ""),
    bgmId: String(plan?.bgm?.id ?? ""),
    imageCount,
    videoCount,
    sfxCount,
    isTestClip: isTest,
    steps: {
      // Bước kịch bản chỉ xong khi script.json có NỘI DUNG thật —
      // createProject ghi sẵn file này với content "" nên tính theo
      // file tồn tại sẽ báo "đã có kịch bản" cho project mới tinh —
      // client dựa vào cờ này để chọn tab mở đầu và cổng nút Tạo video
      // tự động, cả hai đều sai theo (mở nhầm tab Phân cảnh, nút tự
      // động sáng khi chưa có kịch bản). Ngoại lệ: project pipeline để
      // script.json trống nhưng đã có plan có cảnh suy ra từ kịch bản
      // thì bước kịch bản vẫn coi như xong. Tương tự, plan file tồn
      // tại nhưng 0 cảnh (sau reset theo kịch bản) chưa phải xong
      // bước phân cảnh.
      script:
        (typeof scriptFile.content === "string" &&
          scriptFile.content.trim().length > 0) ||
        scenes.length > 0,
      plan: plan !== null && scenes.length > 0,
      tts: tts !== null,
      karaoke: existsSync(join(dir, "build/subtitles/karaoke.json")),
      preview: existsSync(previewPath),
      exported: existsSync(join(dir, "export"))
        ? readdirSync(join(dir, "export")).some((name) => name.endsWith(".zip"))
        : false,
    },
    warnings,
    loadError: null,
  };
}

export function jobFiles(projectId: string, jobId: string) {
  const dir = join(projDir(projectId), ".app-jobs");
  mkdirSync(dir, { recursive: true });
  return {
    status: join(dir, `${jobId}.json`),
    log: join(dir, `${jobId}.log`),
  };
}

export function stepCommand(projectId: string, step: string, force: boolean): string[] {
  switch (step) {
    case "tts":
      return [TTS_PY, join(BIN, "tts_batch.py"), projectId, ...(force ? ["--force"] : [])];
    case "normalize":
      // normalize_chunks.py import vieneu_utils của engine TTS — phải chạy
      // bằng TTS venv (đúng docstring của script); python3 hệ thống không có
      // module này nên chết ở import với exit 1 trước khi đọc plan.
      return [TTS_PY, join(BIN, "normalize_chunks.py"), projectId];
    case "karaoke":
      return [PY3, join(BIN, "karaoke.py"), projectId];
    case "preflight":
      return [PY3, join(BIN, "preflight.py"), projectId, "--json"];
    case "render":
      return [PY3, join(BIN, "render_draft.py"), projectId];
    case "genimages":
      return [VENV_PY, join(BIN, "gen_images.py"), join(projDir(projectId), ".app-jobs/genimages-jobs.json")];
    case "export":
      return [PY3, join(BIN, "assemble_project.py"), projectId];
    default:
      throw new Error(`Bước job không hợp lệ: ${step}`);
  }
}

export function buildGenImageJobs(projectId: string): number {
  const dir = projDir(projectId);
  const plan = readJson<{
    scenes?: Array<{
      order?: number;
      sceneImagePrompt?: string;
      imageFile?: string;
      sceneScriptSummary?: string;
      mediaSource?: unknown;
    }>;
  } | null>(join(dir, "broll-plan.json"), null);
  const jobs: Array<Record<string, unknown>> = [];
  for (const scene of plan?.scenes ?? []) {
    const order = scene.order ?? 0;
    if (!order) continue;
    const out = join(dir, `build/media/images/${scene.imageFile ?? sceneImageFileName(projectId, order)}`);
    mkdirSync(join(dir, "build/media/images"), { recursive: true });
    if (scene.sceneImagePrompt && scene.sceneImagePrompt.trim()) {
      jobs.push({ prompt: scene.sceneImagePrompt, out, orientation: "vertical" });
      if (!scene.imageFile) {
        scene.imageFile = basename(out);
      }
      // Ảnh cảnh do job này tạo ra là ảnh AI từ đúng prompt của cảnh:
      // ghi nguồn gốc kèm prompt vào plan (nếu cảnh chưa có nguồn) để
      // thư viện media ở tab Media hiện đúng nguồn AI + prompt.
      if (!scene.mediaSource) {
        scene.mediaSource = { source: "AI từ prompt", prompt: scene.sceneImagePrompt };
      }
    } else {
      jobs.push({ card_pid: projectId, card_order: order, out });
      if (!scene.imageFile) scene.imageFile = basename(out);
    }
  }
  if (plan) writeJson(join(dir, "broll-plan.json"), plan);
  const jobsPath = join(dir, ".app-jobs/genimages-jobs.json");
  mkdirSync(join(dir, ".app-jobs"), { recursive: true });
  writeFileSync(jobsPath, JSON.stringify(jobs, null, 2), "utf8");
  return jobs.length;
}

// Preview-MP4 md5 cache (giai đoạn 2, 03/11): getProject used to read
// the whole preview file (tens of MB) and hash it on EVERY call, while
// the client polls getProject every 15s — pure repeated cost. The hash
// is now cached per file path and only recomputed when the file's
// mtime or size changes; ffprobe still runs per call because it reads
// metadata only, not the whole file.
const previewMd5Cache = new Map<string, { mtimeMs: number; size: number; md5: string }>();

export function previewMd5(path: string): { md5: string; sizeBytes: number } {
  const st = statSync(path);
  const hit = previewMd5Cache.get(path);
  if (hit && hit.mtimeMs === st.mtimeMs && hit.size === st.size) {
    return { md5: hit.md5, sizeBytes: st.size };
  }
  const bytes = readFileSync(path);
  const md5 = createHash("md5").update(bytes).digest("hex");
  previewMd5Cache.set(path, { mtimeMs: st.mtimeMs, size: st.size, md5 });
  return { md5, sizeBytes: bytes.length };
}

// Chụp snapshot input/script/plan/tts của project vào .snapshots/ và
// áp chính sách giữ 30 bản mới nhất (giai đoạn 2, 03/11 — trước đây
// snapshot chỉ tăng không giảm, không có đường khôi phục).
const SNAPSHOT_KEEP = 30;

export function takeSnapshot(projectId: string, kind: string): void {
  const dir = projDir(projectId);
  const stamp = new Date().toISOString().replace(/[:.]/g, "-");
  const snapDir = join(dir, `.snapshots/${stamp}_${kind}`);
  mkdirSync(snapDir, { recursive: true });
  for (const f of ["input.json", "script.json", "broll-plan.json", "tts.json"]) {
    const p = join(dir, f);
    if (existsSync(p)) copyFileSync(p, join(snapDir, f));
  }
  const preview = join(dir, `export/${projectId}_preview.mp4`);
  if (existsSync(preview)) {
    writeFileSync(join(snapDir, "preview.md5"), createHash("md5").update(readFileSync(preview)).digest("hex"));
  }
  const snapsRoot = join(dir, ".snapshots");
  const names = readdirSync(snapsRoot, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort()
    .reverse();
  for (const old of names.slice(SNAPSHOT_KEEP)) {
    rmSync(join(snapsRoot, old), { recursive: true, force: true });
  }
}
