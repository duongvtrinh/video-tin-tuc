// Privileged host handlers: the only code in this artifact allowed to touch
// the local filesystem and spawn processes. Everything here operates on the
// real VieNeu Asset Factory repo (~/workspace/asset-factory, a symlink to
// vieneu-asset-factory) — the repo is the source of truth; this app is a UI
// shell over its projects/ folder, bin/ scripts, templates/, bgm/ and sfx/.

import { definePrivilegedContracts, definePrivilegedHandlers, z } from "@hatch/space-sdk";

// ---- Schema plan/input: MỘT định nghĩa duy nhất (hợp nhất 03/11) ----
// Generator contract trích NGUYÊN VĂN đối số của definePrivilegedContracts
// vào server/.generated/privileged.contract.ts — file sinh ra chỉ import
// { definePrivilegedContracts, z } từ SDK, nên đối số không thể tham chiếu
// const khai báo ngoài lời gọi. Vì vậy các schema dùng chung (mediaSource,
// broll, part, scene, plan, input, ok) được khai báo MỘT LẦN bên trong
// IIFE tự chứa dưới đây rồi dùng lại cho mọi contract (getProject,
// saveInput, savePlan trước đây mỗi nơi chép một bản inline riêng, cộng
// thêm một bản const ở đầu file — 3 bản sao dễ lệch nhau). Đã kiểm chứng:
// JSON-schema sinh từ contract mới giống hệt bản 3-bản-sao cũ và hành vi
// parse (default, looseObject giữ khóa lạ) không đổi.
export const Factory = definePrivilegedContracts((() => {
// Provenance records in broll-plan.json are written by the external
// Production pipeline, whose media logic has changed shape repeatedly
// (search-script {source,...}, AI-prompt {type,prompt,note} with NO source,
// {type,aiPrompt,file,visualCheck}, news-direct {article_url,original_url,...}).
// A closed schema here made getProject fail with 500 on every plan whose
// mediaSource did not match the one expected shape, and stripped every
// unknown provenance key when a plan was saved back through the app.
// These schemas are therefore deliberately OPEN (looseObject: unknown keys
// pass through untouched) and every known field is optional/nullable;
// getProject additionally normalizes a display `source` from `type` when
// the pipeline left it out. Never tighten this back to a closed shape.
const mediaSourceSchema = z.looseObject({
  source: z.string().nullable().optional(),
      type: z.string().nullable().optional(),
      pageUrl: z.string().nullable().optional(),
      page_url: z.string().nullable().optional(),
      title: z.string().nullable().optional(),
      note: z.string().nullable().optional(),
      license: z.string().nullable().optional(),
      author: z.string().nullable().optional(),
      score: z.union([z.number(), z.string()]).nullable().optional(),
      reason: z.string().nullable().optional(),
      detail: z.string().nullable().optional(),
      verdict: z.string().nullable().optional(),
      runnerUpScore: z.union([z.number(), z.string()]).nullable().optional(),
      visuallyChecked: z.union([z.boolean(), z.string()]).nullable().optional(),
      prompt: z.string().nullable().optional(),
      aiPrompt: z.string().nullable().optional(),
      visualCheck: z.string().nullable().optional(),
      newLogicVisualCheck: z.string().nullable().optional(),
      file: z.string().nullable().optional(),
      image_url: z.string().nullable().optional(),
      article_url: z.string().nullable().optional(),
      original_url: z.string().nullable().optional(),
      reference_image_url: z.string().nullable().optional(),
      referenceImageUrl: z.string().nullable().optional(),
      referencePageUrl: z.string().nullable().optional(),
      referenceNote: z.string().nullable().optional(),
      searchNote: z.string().nullable().optional(),
      copyright_note: z.string().nullable().optional(),
      crop_note: z.string().nullable().optional(),
      edit: z.string().nullable().optional(),
      intrinsic_text_note: z.string().nullable().optional(),
      refinement2_note: z.string().nullable().optional(),
      brollVideoNote: z.string().nullable().optional(),
      brollFile: z.string().nullable().optional(),
      videoFileUrl: z.string().nullable().optional(),
      videoLicense: z.string().nullable().optional(),
      videoNote: z.string().nullable().optional(),
      videoPageUrl: z.string().nullable().optional(),
});
const videoSourceSchema = z.looseObject({
  source: z.string().nullable().optional(),
      page_url: z.string().nullable().optional(),
      pageUrl: z.string().nullable().optional(),
      title: z.string().nullable().optional(),
      note: z.string().nullable().optional(),
      license: z.string().nullable().optional(),
      video: z.string().nullable().optional(),
      verdict: z.string().nullable().optional(),
      frames: z.string().nullable().optional(),
      desc: z.string().nullable().optional(),
      score: z.union([z.number(), z.string()]).nullable().optional(),
      duration_sec: z.number().nullable().optional(),
      visuallyChecked: z.union([z.boolean(), z.string()]).nullable().optional(),
});
const sfxSchema = z.looseObject({
  id: z.string(),
  offsetSec: z.number().default(0),
  volume: z.number().default(0.6),
});
// Template inputs are TEXT for the template engine (every template meta
// declares its inputs as strings/enums), but the external Production
// pipeline writes some of them as raw JSON numbers/booleans — bar-chart
// column heights w1..w4 were written as 100/52/62/0 in drone001 and
// topic058001, which made getProject fail 500 because this record only
// accepted strings. The schema therefore accepts any scalar, and
// normalizePlanProvenance coerces every value to its string form before
// the plan is returned or saved, so the client and the template engine
// only ever see strings. Never narrow this back to z.string() alone.
const templateInputsSchema = z.record(
  z.string(),
  z.union([z.string(), z.number(), z.boolean()]).nullable(),
);
const brollSchema = z.looseObject({
  templateId: z.string().nullable().optional(),
  inputs: templateInputsSchema.nullable().optional(),
  mediaType: z.enum(["image", "video"]).nullable().optional(),
  keepAudio: z.boolean().nullable().optional(),
  file: z.string().nullable().optional(),
  scriptSummary: z.string().nullable().optional(),
  prompt: z.string().nullable().optional(),
  mediaSource: z.union([z.string(), mediaSourceSchema]).nullable().optional(),
  videoSource: z.union([z.string(), videoSourceSchema]).nullable().optional(),
  videoNote: z.string().nullable().optional(),
  sfx: sfxSchema.optional(),
  sourceStartSec: z.number().nullable().optional(),
});
const partSchema = z.looseObject({
  id: z.string(),
  voiceText: z.string(),
  broll: brollSchema.optional(),
});
const sceneSchema = z.looseObject({
  id: z.string(),
  order: z.number(),
  sceneScriptSummary: z.string().default(""),
  sceneImagePrompt: z.string().default(""),
  imageFile: z.string().nullable().optional(),
  cardImage: z.string().nullable().optional(),
  text: z.string().default(""),
  motion: z.string().nullable().optional(),
  mediaSource: z.union([z.string(), mediaSourceSchema]).nullable().optional(),
  parts: z.array(partSchema).default([]),
});
const planSchema = z.looseObject({
  pauseAfterMs: z.number().default(180),
  speed: z.number().default(1.0),
  voice: z.string().default("Hữu Quân"),
  bgm: z
    .looseObject({
      id: z.string().optional(),
      file: z.string().nullable().optional(),
      mood: z.string().optional(),
      volume: z.number().optional(),
    })
    .nullable()
    .optional(),
  scenes: z.array(sceneSchema).default([]),
});
const inputSchema = z.looseObject({
  name: z.string(),
  mode: z.string().default("idea"),
  aspectRatio: z.string().default("9:16"),
  lang: z.string().default("vi"),
  density: z.string().default("normal"),
  created_at: z.string().default(""),
  topic: z.string().default(""),
  sourceType: z.string().default(""),
  isTestClip: z.boolean().default(false),
});
const okSchema = z.object({ ok: z.literal(true) });
  return {
  listProjects: {
    request: z.object({ includeTrashed: z.boolean().default(false) }),
    response: z.object({
      projects: z.array(
        z.object({
          id: z.string(),
          name: z.string(),
          topic: z.string(),
          createdAt: z.string(),
          modifiedAt: z.number(),
          sceneCount: z.number(),
          partCount: z.number(),
          totalDurationSec: z.number().nullable(),
          voice: z.string(),
          bgmId: z.string(),
          imageCount: z.number(),
          videoCount: z.number(),
          sfxCount: z.number(),
          isTestClip: z.boolean(),
          steps: z.object({
            script: z.boolean(),
            plan: z.boolean(),
            tts: z.boolean(),
            karaoke: z.boolean(),
            preview: z.boolean(),
            exported: z.boolean(),
          }),
          warnings: z.array(z.string()),
          // null khi đọc bình thường; project có thư mục hỏng (JSON lỗi,
          // thiếu file) vẫn xuất hiện trong danh sách với thông điệp này
          // thay vì bị lặng lẽ lọc bỏ như trước (giai đoạn 2, 03/11).
          loadError: z.string().nullable(),
        }),
      ),
    }),
    capabilities: ["filesystem:read"],
    timeoutMs: 60_000,
  },
  getProject: {
    request: z.object({ projectId: z.string().min(1) }),
    response: z.object({
      id: z.string(),
      input: inputSchema,
      scriptContent: z.string(),
      scriptTopic: z.string(),
      plan: planSchema.nullable(),
      ttsParts: z.array(
        z.object({
          id: z.string(),
          sceneOrder: z.number(),
          partIdx: z.number(),
          audioFile: z.string(),
          duration: z.number(),
          startSec: z.number(),
          endSec: z.number(),
        }),
      ),
      totalDurationSec: z.number().nullable(),
      karaokeLines: z.array(
        z.object({
          startSec: z.number(),
          endSec: z.number(),
          text: z.string(),
          sceneOrder: z.number().nullable(),
          partId: z.string().nullable(),
          hidden: z.boolean(),
        }),
      ),
      karaokeLineCount: z.number(),
      preview: z
        .object({
          exists: z.boolean(),
          md5: z.string(),
          sizeBytes: z.number(),
          durationSec: z.number().nullable(),
          width: z.number().nullable(),
          height: z.number().nullable(),
          modifiedAt: z.number(),
        })
        .nullable(),
      exportZipExists: z.boolean(),
      warnings: z.array(z.string()),
      mediaLibrary: z.array(
        z.object({
          fileName: z.string(),
          relPath: z.string(),
          kind: z.enum(["image", "video"]),
          sizeBytes: z.number(),
          slot: z.enum(["scene", "broll", "other"]),
          sceneOrder: z.number().nullable(),
          partId: z.string().nullable(),
          partLabel: z.string(),
          source: z.string(),
          urls: z.array(z.string()),
          license: z.string().nullable(),
          author: z.string().nullable(),
          title: z.string().nullable(),
          isAi: z.boolean(),
          aiPrompt: z.string().nullable(),
          note: z.string().nullable(),
        }),
      ),
    }),
    capabilities: ["filesystem:read"],
    timeoutMs: 60_000,
  },
  createProject: {
    request: z.object({
      name: z.string().min(1),
      topic: z.string().default(""),
    }),
    response: z.object({ projectId: z.string() }),
    capabilities: ["filesystem:write"],
    timeoutMs: 30_000,
  },
  saveScript: {
    request: z.object({
      projectId: z.string().min(1),
      content: z.string(),
      topic: z.string().default(""),
    }),
    response: okSchema,
    capabilities: ["filesystem:write"],
    timeoutMs: 30_000,
  },
  saveInput: {
    request: z.object({ projectId: z.string().min(1), input: inputSchema }),
    response: okSchema,
    capabilities: ["filesystem:write"],
    timeoutMs: 30_000,
  },
  savePlan: {
    request: z.object({ projectId: z.string().min(1), plan: planSchema }),
    response: z.object({ ok: z.literal(true), problems: z.array(z.string()) }),
    capabilities: ["filesystem:write"],
    timeoutMs: 30_000,
  },
  deleteProjectForever: {
    request: z.object({ projectId: z.string().min(1) }),
    response: okSchema,
    capabilities: ["filesystem:write"],
    timeoutMs: 120_000,
  },
  snapshotProject: {
    request: z.object({ projectId: z.string().min(1), kind: z.string().min(1) }),
    response: okSchema,
    capabilities: ["filesystem:write"],
    timeoutMs: 120_000,
  },
  listSnapshots: {
    request: z.object({ projectId: z.string().min(1) }),
    response: z.object({
      snapshots: z.array(
        z.object({
          id: z.string(),
          kind: z.string(),
          createdAtMs: z.number(),
          files: z.array(z.string()),
        }),
      ),
    }),
    capabilities: ["filesystem:read"],
    timeoutMs: 60_000,
  },
  restoreSnapshot: {
    request: z.object({ projectId: z.string().min(1), snapshotId: z.string().min(1) }),
    response: okSchema,
    capabilities: ["filesystem:write"],
    timeoutMs: 120_000,
  },
  deleteSnapshot: {
    request: z.object({ projectId: z.string().min(1), snapshotId: z.string().min(1) }),
    response: okSchema,
    capabilities: ["filesystem:write"],
    timeoutMs: 60_000,
  },
  getCatalogs: {
    request: z.object({}),
    response: z.object({
      templates: z.array(
        z.object({
          id: z.string(),
          name: z.string(),
          version: z.string(),
          category: z.string(),
          description: z.string(),
          whenToUse: z.array(z.string()),
          notFor: z.array(z.string()),
          hidesSubs: z.boolean(),
          inputs: z.array(
            z.object({
              key: z.string(),
              type: z.string(),
              required: z.boolean(),
              maxLength: z.number().nullable(),
              defaultValue: z.string(),
            }),
          ),
          sfxId: z.string().nullable(),
          sfxVolume: z.number().nullable(),
        }),
      ),
      bgm: z.array(
        z.object({
          id: z.string(),
          title: z.string(),
          artist: z.string(),
          moods: z.array(z.string()),
          durationSec: z.number(),
          license: z.string(),
          attribution: z.string(),
          file: z.string(),
        }),
      ),
      sfx: z.array(
        z.object({
          id: z.string(),
          file: z.string(),
          durationSec: z.number().nullable(),
        }),
      ),
    }),
    capabilities: ["filesystem:read"],
    timeoutMs: 60_000,
  },
  startJob: {
    request: z.object({
      jobId: z.string().min(1),
      projectId: z.string().min(1),
      step: z.enum(["tts", "normalize", "karaoke", "preflight", "render", "genimages", "export"]),
      force: z.boolean().default(false),
    }),
    response: z.object({ logTail: z.string() }),
    capabilities: ["process:spawn", "filesystem:write"],
    timeoutMs: 30_000,
  },
  pollJob: {
    request: z.object({
      jobId: z.string().min(1),
      projectId: z.string().min(1),
      step: z.string().min(1),
    }),
    response: z.object({
      running: z.boolean(),
      exitCode: z.number().nullable(),
      logTail: z.string(),
    }),
    capabilities: ["filesystem:read"],
    timeoutMs: 30_000,
  },
  cancelJob: {
    request: z.object({
      jobId: z.string().min(1),
      projectId: z.string().min(1),
      step: z.string().min(1),
    }),
    response: z.object({ cancelled: z.boolean() }),
    capabilities: ["process:spawn", "filesystem:write"],
    timeoutMs: 30_000,
  },
  searchMedia: {
    request: z.object({
      layer: z.enum(["wikimedia", "stock"]),
      summary: z.string().min(1),
      enKeywords: z.string().default(""),
      extraKeywords: z.string().default(""),
      mediaType: z.enum(["image", "video"]),
      durationSec: z.number().default(0),
    }),
    response: z.object({
      candidates: z.array(
        z.object({
          title: z.string(),
          pageUrl: z.string(),
          fileUrl: z.string(),
          thumbUrl: z.string(),
          mime: z.string(),
          width: z.number().nullable(),
          height: z.number().nullable(),
          durationSec: z.number().nullable(),
          license: z.string(),
          author: z.string(),
          score: z.number().nullable(),
          verdict: z.string(),
          source: z.string(),
        }),
      ),
      queriesTried: z.array(z.string()),
      note: z.string(),
    }),
    capabilities: ["process:spawn", "network"],
    timeoutMs: 180_000,
  },
  suggestKeywords: {
    request: z.object({ summary: z.string().min(1) }),
    response: z.object({
      clusterId: z.string().nullable(),
      viPhrases: z.array(z.string()),
      enPhrases: z.array(z.string()),
      noCluster: z.boolean(),
    }),
    capabilities: ["process:spawn"],
    timeoutMs: 60_000,
  },
  pickMedia: {
    request: z.object({
      projectId: z.string().min(1),
      sceneOrder: z.number().int().positive(),
      partId: z.string().nullable(),
      fileUrl: z.string().min(1),
      mediaType: z.enum(["image", "video"]),
      source: z.string().min(1),
      pageUrl: z.string().default(""),
      license: z.string().default(""),
      author: z.string().default(""),
      score: z.number().nullable(),
      verdict: z.string().default(""),
      runnerUpScore: z.number().nullable().default(null),
    }),
    response: z.object({ fileName: z.string() }),
    capabilities: ["network", "filesystem:write"],
    timeoutMs: 180_000,
  },
  generateAiMedia: {
    request: z.object({
      projectId: z.string().min(1),
      sceneOrder: z.number().int().positive(),
      partId: z.string().nullable(),
      prompt: z.string().min(1),
      mediaType: z.enum(["image", "video"]),
    }),
    response: z.object({ fileName: z.string() }),
    capabilities: ["process:spawn", "filesystem:write"],
    timeoutMs: 600_000,
  },
  renderTemplatePreview: {
    request: z.object({
      templateId: z.string().min(1),
      inputs: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()]).nullable()),
    }),
    response: z.object({ pngBase64: z.string() }),
    capabilities: ["process:spawn"],
    timeoutMs: 120_000,
  },
  getMediaUrl: {
    request: z.object({ projectId: z.string().min(1), relPath: z.string().min(1) }),
    response: z.object({ dataUrl: z.string() }),
    capabilities: ["filesystem:read"],
    timeoutMs: 60_000,
  },
  getMediaChunk: {
    // Chunked media transfer for large files (e.g. a 41.5 MB rendered
    // MP4): the inline data-URL path base64-inflates the whole file into
    // one action response (~55 MB for that MP4) and the daemon truncates
    // it ("web artifact daemon response was truncated"). The client pulls
    // the file in <=2 MiB raw chunks and reassembles a Blob locally.
    request: z.object({
      projectId: z.string().min(1),
      relPath: z.string().min(1),
      offset: z.number().int().min(0),
      length: z.number().int().min(1).max(2_097_152),
    }),
    response: z.object({
      base64: z.string(),
      offset: z.number(),
      chunkBytes: z.number(),
      totalSize: z.number(),
      eof: z.boolean(),
      mime: z.string(),
    }),
    capabilities: ["filesystem:read"],
    timeoutMs: 60_000,
  },
  getPreviewData: {
    // HTML preview data, assembled exactly like bin/build_render_page.py:
    // per part — real image (b-roll jpg if any, else scene image, resized
    // to frame width), templateId + template.html/style.css + inputs,
    // karaoke lines/words + subsHidden, start/end from tts.json, and the
    // part's render motion (render_draft.py's sequential
    // random.Random("motion-<pid>") sequence, replicated in
    // renderMotionByPartId) — plus the verbatim source of
    // lib/render-engine.js (the repo's only render engine) so the client
    // player runs the engine itself, not a rewrite.
    request: z.object({ projectId: z.string().min(1) }),
    response: z.object({
      engineSource: z.string(),
      width: z.number(),
      height: z.number(),
      durationSec: z.number(),
      parts: z.array(
        z.object({
          id: z.string(),
          start: z.number(),
          end: z.number(),
          image: z.string(),
          // B-roll VIDEO of the part, detected exactly like
          // render_draft.py's base_video(): the
          // build/media/broll/broll_seg_<order>_part_<idx>_*.mp4 file,
          // kept only when ffprobe sees a real video stream (a broken
          // file falls back to the image path, like the render).
          // videoFile is the project-relative path — the client streams
          // the bytes through getMediaChunk and hands the engine a blob
          // URL as part.video (the engine draws a real <video>: in a
          // portrait frame a landscape/square video sits inside the
          // FIXED 3:4 window over the blurred background, height matched
          // to the window, sides cropped; a 9:16 video fills the frame).
          // videoW/videoH are the ffprobe dimensions the engine uses to
          // pick that mode before the file's metadata loads. Before
          // these fields existed the preview data carried no video at
          // all, so a video part rendered as a black frame with only
          // the voice audible (user report 2026-11-01).
          videoFile: z.string().nullable(),
          videoW: z.number().nullable(),
          videoH: z.number().nullable(),
          // The exact Ken Burns motion bin/render_draft.py will use for
          // this part (its sequential random.Random("motion-<pid>")
          // sequence, replicated server-side), or null when the part is
          // outside the render's part order. The engine honors it when
          // present and only falls back to its hash pick when null —
          // before this field existed the preview animated images with a
          // different motion than the rendered video.
          motion: z.string().nullable(),
          templateId: z.string().nullable(),
          tplHtml: z.string(),
          tplCss: z.string(),
          tplInputs: z.record(z.string(), z.string()),
          audioFile: z.string(),
          karaoke: z.object({
            lines: z.array(
              z.object({
                start: z.number(),
                end: z.number(),
                words: z.array(
                  z.object({ text: z.string(), start: z.number(), end: z.number() }),
                ),
              }),
            ),
            subsHidden: z.boolean(),
          }),
        }),
      ),
      // Audio layers of the final render (bin/render_draft.py), exposed so
      // the HTML preview plays the SAME mix: BGM loops at volume 0.12 with
      // sidechain ducking + 2s fade-out at the end; each SFX event fires at
      // part.startSec + offsetSec with the plan volume, heavy SFX
      // (thud/slam/boom) capped at 0.4 in the mix layer. Every SFX is
      // TRIMMED at its part's end (durationSec/endSec, CEO rule
      // 31/10/2026 — an SFX never bleeds into the next part), and a typing
      // SFX (id contains "typing", the typewriter-reveal template) plays
      // only for the DISPLAYED template text: durationSec =
      // min(part remainder, inputs.text length × 0.1s), loop=true when
      // the file is shorter than that window. The preview player must
      // honor durationSec/endSec/loop exactly like the render's
      // atrim/aloop chain — playing the raw file end-to-end was the bug
      // that made preview SFX cover the whole voice part.
      bgm: z
        .object({ id: z.string(), file: z.string(), volume: z.number() })
        .nullable(),
      sfxEvents: z.array(
        z.object({
          id: z.string(),
          file: z.string(),
          partId: z.string(),
          atSec: z.number(),
          volume: z.number(),
          durationSec: z.number(),
          endSec: z.number(),
          loop: z.boolean(),
        }),
      ),
    }),
    capabilities: ["filesystem:read", "process:spawn"],
    timeoutMs: 180_000,
  },
  };
})());

// Tầng handler đã tách module (giai đoạn 3 đợt riêng, 03/11): file này
// chỉ còn contracts (định nghĩa schema hợp nhất ở trên) và điểm lắp
// handlers. Toàn bộ logic nằm ở server/src/priv/: core (đường dẫn nhà
// máy, hợp đồng tên file, khóa ghi plan, chạy lệnh), motion (chuỗi Ken
// Burns của render), plan-normalize (chuẩn hóa provenance), media-
// library (thư viện tab Media), projects (tóm tắt/snapshot/job) và 4
// nhóm handlers-*. Các module đó CHỈ được tầng privileged import,
// tuyệt đối không import từ actions.ts.
import { listProjects, getProject, createProject, saveScript, saveInput, savePlan, deleteProjectForever, snapshotProject, listSnapshots, restoreSnapshot, deleteSnapshot, getCatalogs } from "./priv/handlers-projects";
import { startJob, pollJob, cancelJob } from "./priv/handlers-jobs";
import { searchMedia, suggestKeywords, pickMedia, generateAiMedia, renderTemplatePreview, getMediaUrl, getMediaChunk } from "./priv/handlers-media";
import { getPreviewData } from "./priv/handlers-preview";

export const privilegedHandlers = definePrivilegedHandlers(Factory, {
  listProjects,
  getProject,
  createProject,
  saveScript,
  saveInput,
  savePlan,
  deleteProjectForever,
  snapshotProject,
  listSnapshots,
  restoreSnapshot,
  deleteSnapshot,
  getCatalogs,
  startJob,
  pollJob,
  cancelJob,
  searchMedia,
  suggestKeywords,
  pickMedia,
  generateAiMedia,
  renderTemplatePreview,
  getMediaUrl,
  getMediaChunk,
  getPreviewData,
});
