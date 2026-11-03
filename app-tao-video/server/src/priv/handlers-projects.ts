// Handlers project: liệt kê/đọc/tạo/lưu/xóa project, snapshot và catalog template/BGM/SFX.
// Chỉ privileged.ts import file này; kiểu tham số/kết quả lấy thẳng từ
// contract tương ứng (ArgsOf/ResOf) để handler không lệch contract.
import type { Factory } from "@space/privileged";
import type { z } from "@hatch/space-sdk";

type ArgsOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["request"]>;
type ResOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["response"]>;

import { copyFileSync, existsSync, mkdirSync, readdirSync, rmSync, statSync } from "node:fs";
import { basename, join } from "node:path";
import { FACTORY, PROJECTS, ffprobe, findFirstGlob, projDir, randomSuffix, readJson, writeJson } from "./core";
import { normalizePlanProvenance } from "./plan-normalize";
import { buildMediaLibrary } from "./media-library";
import { previewMd5, summarize, takeSnapshot } from "./projects";

export async function listProjects(): Promise<ResOf<"listProjects">> {
    const ids = readdirSync(PROJECTS, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name)
      .sort();
    // A broken project folder (corrupt JSON, unreadable files) used to
    // vanish from the list silently — the user could not tell it existed
    // or that anything was wrong. It now stays in the list as an error
    // row carrying the failure message (giai đoạn 2, 03/11).
    const projects = ids.map((id) => {
      try {
        return summarize(id);
      } catch (e) {
        let modifiedAt = 0;
        try {
          modifiedAt = statSync(projDir(id)).mtimeMs;
        } catch { /* folder itself unreadable — keep 0 */ }
        return {
          id,
          name: id,
          topic: "",
          createdAt: "",
          modifiedAt,
          sceneCount: 0,
          partCount: 0,
          totalDurationSec: null,
          voice: "",
          bgmId: "",
          imageCount: 0,
          videoCount: 0,
          sfxCount: 0,
          isTestClip: false,
          steps: { script: false, plan: false, tts: false, karaoke: false, preview: false, exported: false },
          warnings: [],
          loadError: `Không đọc được project: ${e instanceof Error ? e.message : String(e)}`,
        };
      }
    });
    projects.sort((a, b) => b.modifiedAt - a.modifiedAt);
    return { projects };
  }

export async function getProject({ projectId }: ArgsOf<"getProject">): Promise<ResOf<"getProject">> {
    const dir = projDir(projectId);
    if (!existsSync(dir)) throw new Error(`Không thấy project ${projectId}`);
    const inputRaw = readJson<Record<string, unknown>>(join(dir, "input.json"), {});
    const script = readJson<{ topic?: string; content?: string }>(join(dir, "script.json"), {
      topic: "",
      content: "",
    });
    const planRaw = readJson<unknown>(join(dir, "broll-plan.json"), null);
    // Pipeline projects leave scene.imageFile null and address the scene
    // image purely by the seg_<order>_* file convention. Fill it in the
    // RETURNED copy only (the plan file on disk is not rewritten) so the
    // UI shows the real scene image instead of falsely claiming "chưa có
    // ảnh cảnh — render sẽ ra nền đen" for scenes whose image is sitting
    // in build/media/images — that false black warning is part of why a
    // good render was reported as a black video.
    if (planRaw && typeof planRaw === "object") {
      const scenes = (planRaw as { scenes?: unknown }).scenes;
      if (Array.isArray(scenes)) {
        const imagesDir = join(dir, "build/media/images");
        for (const sc of scenes) {
          if (!sc || typeof sc !== "object") continue;
          const s = sc as Record<string, unknown>;
          if (typeof s["imageFile"] === "string" && s["imageFile"]) continue;
          const order = s["order"];
          if (typeof order !== "number") continue;
          const hit =
            findFirstGlob(imagesDir, `seg_${order}_`, ".jpg") ??
            findFirstGlob(imagesDir, `seg_${order}_`, ".png") ??
            findFirstGlob(imagesDir, `seg_${order}_`, ".webp");
          if (hit) s["imageFile"] = basename(hit);
        }
      }
    }
    const tts = readJson<{
      parts?: Array<{
        id: string;
        sceneOrder: number;
        partIdx: number;
        audio_file: string;
        duration: number;
        startSec: number;
        endSec: number;
      }>;
    } | null>(join(dir, "tts.json"), null);
    const ttsParts = (tts?.parts ?? []).map((p) => ({
      id: p.id,
      sceneOrder: p.sceneOrder,
      partIdx: p.partIdx,
      audioFile: p.audio_file,
      duration: p.duration,
      startSec: p.startSec,
      endSec: p.endSec,
    }));
    const partScene = new Map(ttsParts.map((p) => [p.id, p.sceneOrder]));
    type KaraokePart = {
      partId?: string;
      subsHidden?: boolean;
      lines?: Array<{ text: string; start: number; end: number }>;
    };
    const karaokeRaw = readJson<KaraokePart[]>(join(dir, "build/subtitles/karaoke.json"), []);
    const karaokeLines = (Array.isArray(karaokeRaw) ? karaokeRaw : []).flatMap((kp) =>
      (kp.lines ?? []).map((l) => ({
        startSec: l.start,
        endSec: l.end,
        text: l.text,
        sceneOrder: kp.partId ? (partScene.get(kp.partId) ?? null) : null,
        partId: kp.partId ?? null,
        hidden: kp.subsHidden === true,
      })),
    );
    const hiddenCount = (Array.isArray(karaokeRaw) ? karaokeRaw : []).filter(
      (kp) => kp.subsHidden,
    ).length;
    void hiddenCount;
    const previewPath = join(dir, `export/${projectId}_preview.mp4`);
    let preview = null;
    if (existsSync(previewPath)) {
      const { md5, sizeBytes } = previewMd5(previewPath);
      const probe = ffprobe(previewPath);
      preview = {
        exists: true,
        md5,
        sizeBytes,
        durationSec: probe.duration,
        width: probe.width,
        height: probe.height,
        modifiedAt: statSync(previewPath).mtimeMs,
      };
    }
    const summary = summarize(projectId);
    const normalizedPlan = normalizePlanProvenance(planRaw);
    const mediaLibrary = buildMediaLibrary(dir, normalizedPlan);
    return {
      id: projectId,
      input: {
        name: String(inputRaw["name"] ?? projectId),
        mode: String(inputRaw["mode"] ?? "idea"),
        aspectRatio: String(inputRaw["aspectRatio"] ?? "9:16"),
        lang: String(inputRaw["lang"] ?? "vi"),
        density: String(inputRaw["density"] ?? "normal"),
        created_at: String(inputRaw["created_at"] ?? ""),
        topic: String(inputRaw["topic"] ?? ""),
        sourceType: String(inputRaw["sourceType"] ?? ""),
        isTestClip: inputRaw["isTestClip"] === true,
      },
      scriptContent: script.content ?? "",
      scriptTopic: script.topic ?? "",
      plan: normalizedPlan as never,
      ttsParts,
      totalDurationSec:
        ttsParts.length > 0 ? ttsParts.reduce((n, p) => n + p.duration, 0) : null,
      karaokeLines,
      karaokeLineCount: karaokeLines.length,
      preview,
      exportZipExists: summary.steps.exported,
      warnings: summary.warnings,
      mediaLibrary,
    };
  }

export async function createProject({ name, topic }: ArgsOf<"createProject">): Promise<ResOf<"createProject">> {
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, "0");
    const stamp = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
    const projectId = `project_${stamp}_${randomSuffix()}`;
    const dir = projDir(projectId);
    mkdirSync(join(dir, "build/media/images"), { recursive: true });
    mkdirSync(join(dir, "build/media/broll"), { recursive: true });
    mkdirSync(join(dir, "build/audio/voice/parts"), { recursive: true });
    mkdirSync(join(dir, "export"), { recursive: true });
    writeJson(join(dir, "input.json"), {
      name,
      mode: "idea",
      aspectRatio: "9:16",
      lang: "vi",
      density: "normal",
      created_at: `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`,
      topic,
      sourceType: "",
      isTestClip: false,
    });
    writeJson(join(dir, "script.json"), { topic, content: "" });
    return { projectId };
  }

export async function saveScript({ projectId, content, topic }: ArgsOf<"saveScript">): Promise<ResOf<"saveScript">> {
    writeJson(join(projDir(projectId), "script.json"), { topic, content });
    return { ok: true as const };
  }

export async function saveInput({ projectId, input }: ArgsOf<"saveInput">): Promise<ResOf<"saveInput">> {
    writeJson(join(projDir(projectId), "input.json"), input);
    return { ok: true as const };
  }

export async function savePlan({ projectId, plan }: ArgsOf<"savePlan">): Promise<ResOf<"savePlan">> {
    normalizePlanProvenance(plan);
    const problems: string[] = [];
    const ids = new Set<string>();
    const templateIds = new Set(
      readdirSync(join(FACTORY, "templates"), { withFileTypes: true })
        .filter((e) => e.isDirectory())
        .map((e) => e.name),
    );
    const sfxIds = new Set(
      readdirSync(join(FACTORY, "sfx"))
        .filter((f) => f.endsWith(".mp3"))
        .map((f) => f.replace(/\.mp3$/, "")),
    );
    // Giai đoạn 1 (03/11): kiểm tra bổ sung dạng CẢNH BÁO — plan vẫn lưu
    // bình thường (tương thích ngược với plan cũ do pipeline ghi), các
    // vấn đề dưới đây chỉ được trả về trong problems để UI hiện rõ thay
    // vì để plan hỏng lặng lẽ tới render/preview mới vỡ:
    // - mediaSource ở cảnh/part đã có file nhưng thiếu source chuỗi
    //   khác rỗng (luật nguồn bắt buộc 29/10);
    // - input template bắt buộc còn trống hoặc vượt maxLength của meta;
    // - SFX nặng (heavy_thud_slam / boom_sub_impact) để volume > 0,35;
    // - file media plan trỏ tới không tồn tại trên đĩa.
    const HEAVY_SFX = new Set(["heavy_thud_slam", "boom_sub_impact"]);
    const templateMetaCache = new Map<string, Record<string, Record<string, unknown>>>();
    const templateInputsOf = (tid: string): Record<string, Record<string, unknown>> => {
      const hit = templateMetaCache.get(tid);
      if (hit) return hit;
      const meta = readJson<Record<string, unknown>>(join(FACTORY, "templates", tid, "meta.json"), {});
      const inputs = (meta["inputs"] ?? {}) as Record<string, Record<string, unknown>>;
      templateMetaCache.set(tid, inputs);
      return inputs;
    };
    const sourceOf = (ms: unknown): string => {
      if (typeof ms === "string") return ms.trim();
      if (ms && typeof ms === "object") {
        const s = (ms as Record<string, unknown>)["source"];
        return typeof s === "string" ? s.trim() : "";
      }
      return "";
    };
    const imagesDir = join(projDir(projectId), "build/media/images");
    const brollDir = join(projDir(projectId), "build/media/broll");
    for (const scene of plan.scenes) {
      if (scene.imageFile) {
        if (!existsSync(join(imagesDir, scene.imageFile))) {
          problems.push(`Cảnh báo: cảnh ${scene.order} trỏ ảnh ${scene.imageFile} nhưng file không có trên đĩa`);
        }
        if (!sourceOf(scene.mediaSource)) {
          problems.push(`Cảnh báo: cảnh ${scene.order} đã có ảnh nhưng mediaSource thiếu trường source (luật nguồn 29/10)`);
        }
      }
      for (const part of scene.parts) {
        if (ids.has(part.id)) problems.push(`Part id trùng: ${part.id}`);
        ids.add(part.id);
        const tid = part.broll?.templateId;
        if (tid && !templateIds.has(tid)) problems.push(`Template không tồn tại: ${tid} (part ${part.id})`);
        if (tid && templateIds.has(tid)) {
          const metaInputs = templateInputsOf(tid);
          const given = (part.broll?.inputs ?? {}) as Record<string, unknown>;
          for (const [key, spec] of Object.entries(metaInputs)) {
            const raw = given[key];
            const val = raw === null || raw === undefined ? "" : String(raw);
            if (spec["required"] === true && !val.trim()) {
              problems.push(`Cảnh báo: part ${part.id} dùng template ${tid} nhưng thiếu input bắt buộc "${key}"`);
            }
            const max = spec["maxLength"];
            if (typeof max === "number" && val.length > max) {
              problems.push(`Cảnh báo: part ${part.id} input "${key}" của template ${tid} dài ${val.length} ký tự, vượt tối đa ${max}`);
            }
          }
        }
        const sfxId = part.broll?.sfx?.id;
        if (sfxId && !sfxIds.has(sfxId)) problems.push(`SFX không tồn tại: ${sfxId} (part ${part.id})`);
        const sfxVol = part.broll?.sfx?.volume;
        if (sfxId && HEAVY_SFX.has(sfxId) && typeof sfxVol === "number" && sfxVol > 0.35) {
          problems.push(`Cảnh báo: part ${part.id} gắn SFX nặng ${sfxId} ở volume ${sfxVol}, vượt trần 0,35`);
        }
        const bfile = part.broll?.file;
        if (bfile) {
          const inImages = existsSync(join(imagesDir, bfile));
          const inBroll = existsSync(join(brollDir, bfile));
          if (!inImages && !inBroll) {
            problems.push(`Cảnh báo: part ${part.id} trỏ file b-roll ${bfile} nhưng file không có trên đĩa`);
          }
          if (!sourceOf(part.broll?.mediaSource) && !sourceOf(part.broll?.videoSource)) {
            problems.push(`Cảnh báo: part ${part.id} đã có file b-roll nhưng mediaSource thiếu trường source (luật nguồn 29/10)`);
          }
        }
      }
      scene.text = scene.parts.map((p) => p.voiceText).join(" ");
    }
    writeJson(join(projDir(projectId), "broll-plan.json"), plan);
    return { ok: true as const, problems };
  }

export async function deleteProjectForever({ projectId }: ArgsOf<"deleteProjectForever">): Promise<ResOf<"deleteProjectForever">> {
    rmSync(projDir(projectId), { recursive: true, force: true });
    return { ok: true as const };
  }

export async function snapshotProject({ projectId, kind }: ArgsOf<"snapshotProject">): Promise<ResOf<"snapshotProject">> {
    takeSnapshot(projectId, kind);
    return { ok: true as const };
  }

export async function listSnapshots({ projectId }: ArgsOf<"listSnapshots">): Promise<ResOf<"listSnapshots">> {
    const snapsRoot = join(projDir(projectId), ".snapshots");
    if (!existsSync(snapsRoot)) return { snapshots: [] };
    const snapshots = readdirSync(snapsRoot, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => {
        const full = join(snapsRoot, e.name);
        const us = e.name.indexOf("_");
        return {
          id: e.name,
          kind: us >= 0 ? e.name.slice(us + 1) : e.name,
          createdAtMs: statSync(full).mtimeMs,
          files: readdirSync(full).sort(),
        };
      })
      .sort((a, b) => b.createdAtMs - a.createdAtMs);
    return { snapshots };
  }

export async function restoreSnapshot({ projectId, snapshotId }: ArgsOf<"restoreSnapshot">): Promise<ResOf<"restoreSnapshot">> {
    if (snapshotId.includes("/") || snapshotId.includes("..")) {
      throw new Error("Mã snapshot không hợp lệ");
    }
    const dir = projDir(projectId);
    const snapDir = join(dir, ".snapshots", snapshotId);
    if (!existsSync(snapDir)) throw new Error(`Không thấy snapshot ${snapshotId}`);
    // Chụp trạng thái hiện tại trước khi ghi đè, để lần khôi phục này
    // tự nó cũng quay lui được.
    takeSnapshot(projectId, "before-restore");
    for (const f of ["input.json", "script.json", "broll-plan.json", "tts.json"]) {
      const src = join(snapDir, f);
      if (existsSync(src)) copyFileSync(src, join(dir, f));
    }
    return { ok: true as const };
  }

export async function deleteSnapshot({ projectId, snapshotId }: ArgsOf<"deleteSnapshot">): Promise<ResOf<"deleteSnapshot">> {
    if (snapshotId.includes("/") || snapshotId.includes("..")) {
      throw new Error("Mã snapshot không hợp lệ");
    }
    rmSync(join(projDir(projectId), ".snapshots", snapshotId), {
      recursive: true,
      force: true,
    });
    return { ok: true as const };
  }

export async function getCatalogs(): Promise<ResOf<"getCatalogs">> {
    const templatesDir = join(FACTORY, "templates");
    const templates = readdirSync(templatesDir, { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => {
        const meta = readJson<Record<string, unknown>>(join(templatesDir, e.name, "meta.json"), {});
        const inputsRaw = (meta["inputs"] ?? {}) as Record<string, Record<string, unknown>>;
        const sfxRaw = (meta["sfx"] ?? null) as { id?: string; volume?: number } | null;
        return {
          id: String(meta["id"] ?? e.name),
          name: String(meta["name"] ?? e.name),
          version: String(meta["version"] ?? ""),
          category: String(meta["category"] ?? ""),
          description: String(meta["description"] ?? ""),
          whenToUse: (meta["whenToUse"] as string[] | undefined) ?? [],
          notFor: (meta["notFor"] as string[] | undefined) ?? [],
          hidesSubs: meta["hidesSubs"] !== false && meta["mode"] === "overlay",
          inputs: Object.entries(inputsRaw).map(([key, v]) => ({
            key,
            type: String(v["type"] ?? "string"),
            required: v["required"] === true,
            maxLength: typeof v["maxLength"] === "number" ? v["maxLength"] : null,
            defaultValue: v["default"] !== undefined ? String(v["default"]) : "",
          })),
          sfxId: sfxRaw?.id ?? null,
          sfxVolume: typeof sfxRaw?.volume === "number" ? sfxRaw.volume : null,
        };
      })
      .sort((a, b) => a.id.localeCompare(b.id));
    const bgmRaw = readJson<Array<Record<string, unknown>>>(join(FACTORY, "bgm/bgm_catalog.json"), []);
    const bgm = bgmRaw.map((t) => ({
      id: String(t["id"] ?? ""),
      title: String(t["title"] ?? ""),
      artist: String(t["artist"] ?? ""),
      moods: (t["moods"] as string[] | undefined) ?? [],
      durationSec: typeof t["duration_sec"] === "number" ? t["duration_sec"] : 0,
      license: String(t["license"] ?? ""),
      attribution: String(t["attribution"] ?? ""),
      file: String(t["file"] ?? ""),
    }));
    const sfx = readdirSync(join(FACTORY, "sfx"))
      .filter((f) => f.endsWith(".mp3"))
      .map((f) => ({ id: f.replace(/\.mp3$/, ""), file: f, durationSec: null }));
    return { templates, bgm, sfx };
  }
