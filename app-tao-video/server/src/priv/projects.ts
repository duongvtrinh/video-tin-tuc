// Tóm tắt project cho danh sách, chính sách snapshot (giữ 30 bản), ánh
// xạ bước job → lệnh factory, hàng job tạo ảnh cảnh và md5 preview có
// cache theo mtime/size. Chỉ privileged.ts import file này.
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
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
import { isAiSource } from "./plan-normalize";

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
        `Cảnh ${order} chưa có ảnh nền nào (không thấy seg_${order}_*.jpg/*.png/*.webp trong build/media/images, cũng không có b-roll) — render sẽ ra nền đen ở cảnh này`,
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

// B19 (05/11/2026, lệnh CEO, lựa chọn A): file ảnh phải dùng được thì
// mới tính là "đã có ảnh thật" — tồn tại + >0 byte + giải mã được hết
// bằng PIL (dùng chung filename.img_decode_error ở B10, qua PY3). PIL
// không có sẵn, hoặc gọi helper thất bại/timeout, thì coi như dùng được
// (fail-open như _decodes ở gen_images) để không chặn cả batch chỉ vì
// thiếu thư viện hay helper lỗi.
function imageFileUsable(path: string): boolean {
  try {
    if (statSync(path).size === 0) return false;
  } catch {
    return false;
  }
  try {
    const r = spawnSync(
      PY3,
      [
        "-c",
        "import sys; sys.path.insert(0, sys.argv[1]); from filename import img_decode_error; sys.exit(0 if img_decode_error(sys.argv[2]) is None else 1)",
        BIN,
        path,
      ],
      { timeout: 15_000 },
    );
    if (r.error || typeof r.status !== "number") return true;
    return r.status === 0;
  } catch {
    return true;
  }
}

export function buildGenImageJobs(projectId: string): { count: number; skipped: string[] } {
  const dir = projDir(projectId);
  const plan = readJson<{
    scenes?: Array<{
      order?: number;
      sceneImagePrompt?: string;
      imageFile?: string;
      sceneScriptSummary?: string;
      mediaSource?: unknown;
      isMossGrid?: boolean;
    }>;
  } | null>(join(dir, "broll-plan.json"), null);
  const jobs: Array<Record<string, unknown>> = [];
  const skipped: string[] = [];
  const imagesDir = join(dir, "build/media/images");
  let planDirty = false;
  for (const scene of plan?.scenes ?? []) {
    const order = scene.order ?? 0;
    if (!order) continue;
    const out = join(dir, `build/media/images/${scene.imageFile ?? sceneImageFileName(projectId, order)}`);
    mkdirSync(join(dir, "build/media/images"), { recursive: true });
    // A22 (05/11/2026, lệnh CEO): cảnh đã có ảnh thật được chọn thì KHÔNG
    // tạo job ảnh nữa — job AI/card ghi vào đúng đường out = file ảnh thật
    // đó, trong khi mediaSource trong plan vẫn ghi nguồn thật, video sẽ
    // chiếu ảnh AI/nền rêu mà hồ sơ nói ảnh thật. "Ảnh thật đã chọn" =
    // imageFile đã có file trên đĩa VÀ không phải ảnh AI (classification
    // "ai-tu-prompt" / source "AI từ prompt") VÀ không phải nền rêu
    // (isMossGrid). File đã có mà mediaSource thiếu hẳn vẫn bỏ qua (có thể
    // là ảnh thật mất hồ sơ — preflight A20 đã chặn cảnh đó; muốn làm lại
    // thì xóa ảnh bằng clearSceneImage rồi tạo lại job).
    // B18 (05/11/2026, lệnh CEO, lựa chọn A): project pipeline để
    // imageFile null ở mọi cảnh nên A22 gốc không bao giờ kích hoạt ở tầng
    // app — job tạo cho mọi cảnh rồi gen_images mới skip lặng ở dưới.
    // Nay kiểm tra file theo đúng tên rand6 trên đĩa (jpg → png → webp,
    // như partImagePath ở A24) ngay cả khi imageFile null: cảnh nào đã có
    // file thật thì đưa vào skipped, không tạo job. Cảnh bị skip thì
    // KHÔNG điền imageFile vào plan ở đây (việc đó thuộc getProject,
    // B5-C); plan chỉ ghi khi có thay đổi thật (planDirty).
    // B20: nhận diện AI dùng chung isAiSource (plan-normalize) — khớp
    // type/source/classification chứa prompt-AI, ai-tu-prompt, AI từ
    // prompt, chuỗi trần, và quy tắc prompt+type của pipeline cũ.
    const isAiImage = isAiSource(scene.mediaSource);
    const rand6Stem = sceneImageFileName(projectId, order).slice(0, -".jpg".length);
    const diskImage = (["jpg", "png", "webp"] as const)
      .map((ext) => join(imagesDir, `${rand6Stem}.${ext}`))
      .find((p) => existsSync(p));
    const pickedPath = scene.imageFile ? join(imagesDir, basename(scene.imageFile)) : undefined;
    const existingFile = diskImage ?? (pickedPath && existsSync(pickedPath) ? pickedPath : undefined);
    // B19: file tồn tại chưa đủ — phải dùng được (>0 byte + giải mã được,
    // imageFileUsable). File hỏng thì tạo job lại như bình thường, không kẹt.
    const hasPickedRealPhoto =
      !!existingFile &&
      imageFileUsable(existingFile) &&
      !isAiImage &&
      scene.isMossGrid !== true;
    if (hasPickedRealPhoto) {
      skipped.push(`Cảnh ${order}: đã có ảnh thật (${basename(existingFile)}) — xóa ảnh trước rồi tạo lại job`);
      continue;
    }
    if (scene.sceneImagePrompt && scene.sceneImagePrompt.trim()) {
      jobs.push({ prompt: scene.sceneImagePrompt, out, orientation: "vertical" });
      // A21 (05/11/2026): cảnh có prompt AI thì ảnh thật sự là AI — xóa cờ
      // nền rêu nếu cảnh này trước đây từng là nền rêu.
      if (scene.isMossGrid !== undefined) {
        delete scene.isMossGrid;
        planDirty = true;
      }
      if (!scene.imageFile) {
        scene.imageFile = basename(out);
        planDirty = true;
      }
      // Ảnh cảnh do job này tạo ra là ảnh AI từ đúng prompt của cảnh:
      // ghi nguồn gốc kèm prompt vào plan (nếu cảnh chưa có nguồn) để
      // thư viện media ở tab Media hiện đúng nguồn AI + prompt.
      if (!scene.mediaSource) {
        scene.mediaSource = { source: "AI từ prompt", prompt: scene.sceneImagePrompt };
        planDirty = true;
      }
    } else {
      jobs.push({ card_pid: projectId, card_order: order, out });
      // B41 (06/11/2026, lệnh CEO, lựa chọn A): KHÔNG gán isMossGrid ở
      // đây nữa — cờ chỉ có nghĩa "nền rêu đã render thật", mà job card
      // mới tạo chưa render; gen_images ghi cờ qua _mark_moss_grid sau
      // batch khi render xong thật (trước đây gán sớm nên job lỗi vẫn để
      // lại cờ "nền rêu" dù chưa có file nào). File out đã có thì job bị
      // skip, cờ giữ nguyên như trong plan.
      if (!scene.imageFile) {
        scene.imageFile = basename(out);
        planDirty = true;
      }
    }
  }
  if (plan && planDirty) writeJson(join(dir, "broll-plan.json"), plan);
  const jobsPath = join(dir, ".app-jobs/genimages-jobs.json");
  mkdirSync(join(dir, ".app-jobs"), { recursive: true });
  writeFileSync(jobsPath, JSON.stringify(jobs, null, 2), "utf8");
  return { count: jobs.length, skipped };
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
