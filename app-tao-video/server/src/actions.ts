// Actions for App Tạo Video — a UI shell over the real VieNeu Asset Factory
// repo. Project content lives in the repo filesystem and is accessed through
// privileged handlers (server/src/privileged.ts). This database only holds
// app-side state: background job records, soft-delete trash, snapshots log.

import { defineAction, z, type ActionsModule, type Ctx } from "@hatch/space-sdk";
import { desc, eq } from "drizzle-orm";
import * as schema from "./schema";
import { buildScriptPrompt } from "./script-prompt";
import { Factory } from "@space/privileged";

const projectSummarySchema = Factory.listProjects.response.shape.projects.element;
const projectDetailSchema = Factory.getProject.response;
const planSchema = Factory.savePlan.request.shape.plan;
const inputSchema = Factory.saveInput.request.shape.input;
const okSchema = Factory.saveScript.response;
const templateSchema = Factory.getCatalogs.response.shape.templates.element;
const bgmTrackSchema = Factory.getCatalogs.response.shape.bgm.element;
const mediaCandidateSchema = Factory.searchMedia.response.shape.candidates.element;

const ALL_PRIVILEGED = Object.values(Factory);

const jobSchema = z.object({
  id: z.string(),
  projectId: z.string(),
  step: z.string(),
  status: z.string(),
  startedAt: z.number(),
  finishedAt: z.number().nullable(),
  exitCode: z.number().nullable(),
  logTail: z.string(),
  note: z.string(),
});

type JobRow = typeof schema.jobs.$inferSelect;

function toJob(row: JobRow): z.infer<typeof jobSchema> {
  return {
    id: row.id,
    projectId: row.projectId,
    step: row.step,
    status: row.status,
    startedAt: row.startedAt,
    finishedAt: row.finishedAt ?? null,
    exitCode: row.exitCode ?? null,
    logTail: row.logTail,
    note: row.note,
  };
}

// Map an on-disk poll result to the stored job status. Exit code -2 is
// the runner's "cancelled by user" marker (see cancelJob): it gets its
// own status instead of being folded into "error" (the client used to
// special-case -2 in two separate components to tell them apart).
function statusFromExit(exitCode: number | null): "done" | "error" | "cancelled" {
  if (exitCode === 0) return "done";
  if (exitCode === -2) return "cancelled";
  return "error";
}

// Single reconciliation path for job rows (giai đoạn 2, dọn trùng 03/11):
// startJob, getJobStatus, listJobs and cancelJob all used to carry their
// own copy of "poll the disk, and if the process is gone, write the
// final status back". A row that is not running passes through as-is; a
// running row is checked against the on-disk status file and updated in
// the DB when the process has finished.
async function reconcileJob(
  ctx: Ctx,
  row: JobRow,
): Promise<z.infer<typeof jobSchema>> {
  if (row.status !== "running") return toJob(row);
  const poll = await ctx.executePrivileged(Factory.pollJob, {
    jobId: row.id,
    projectId: row.projectId,
    step: row.step,
  });
  if (poll.running) {
    return { ...toJob(row), logTail: poll.logTail || row.logTail };
  }
  const status = statusFromExit(poll.exitCode);
  const finishedAt = Date.now();
  const db = ctx.db<typeof schema>();
  await db
    .update(schema.jobs)
    .set({ status, exitCode: poll.exitCode, finishedAt, logTail: poll.logTail })
    .where(eq(schema.jobs.id, row.id));
  return { ...toJob(row), status, exitCode: poll.exitCode, finishedAt, logTail: poll.logTail };
}

export const Actions = {
  listProjects: defineAction({
    description: "Liệt kê các project video trong nhà máy, kèm danh sách project đã xoá trong thùng rác.",
    request: z.object({ includeTrashed: z.boolean().default(false) }),
    response: z.object({
      projects: z.array(projectSummarySchema),
      trashed: z.array(
        z.object({ projectId: z.string(), name: z.string(), deletedAt: z.number() }),
      ),
    }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const trashRows = await db.select().from(schema.trash);
      const trashedSet = new Set(trashRows.map((r) => r.projectId));
      const { projects } = await ctx.executePrivileged(Factory.listProjects, {
        includeTrashed: args.includeTrashed,
      });
      return {
        projects: projects.filter(
          (p) => args.includeTrashed || !trashedSet.has(p.id),
        ),
        trashed: trashRows.map((r) => ({
          projectId: r.projectId,
          name: r.name,
          deletedAt: r.deletedAt,
        })),
      };
    },
  }),

  getProject: defineAction({
    description: "Đọc toàn bộ chi tiết một project: thông tin đầu vào, kịch bản, plan phân cảnh, TTS, karaoke và bản preview.",
    request: z.object({ projectId: z.string().min(1) }),
    response: projectDetailSchema,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.getProject, { projectId: args.projectId });
    },
  }),

  createProject: defineAction({
    description: "Tạo project video mới với tên và chủ đề tự do, dùng mặc định khung dọc 9:16 tiếng Việt.",
    request: z.object({
      name: z.string().min(1).max(300),
      // 5.000 ký tự (giai đoạn 1, 03/11): trần 1.000 cũ chặn project
      // pipeline thật — topic của TOPIC-114 dài ~1,5k ký tự ghi chú
      // chấm điểm/nguồn nên sửa/lưu lại bị validation chặn trước khi
      // tới privileged (vốn không đặt trần này).
      topic: z.string().max(5000).default(""),
    }),
    response: z.object({ projectId: z.string() }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const res = await ctx.executePrivileged(Factory.createProject, args);
      ctx.invalidateQueries(["projects"]);
      return res;
    },
  }),

  saveInput: defineAction({
    description: "Lưu thông tin đầu vào (tên, chủ đề) của một project, có chụp snapshot trước khi ghi.",
    request: z.object({ projectId: z.string().min(1), input: inputSchema }),
    response: okSchema,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      await ctx.executePrivileged(Factory.snapshotProject, {
        projectId: args.projectId,
        kind: "before-input-save",
      });
      const res = await ctx.executePrivileged(Factory.saveInput, args);
      ctx.invalidateQueries(["projects", "project"]);
      return res;
    },
  }),

  saveScript: defineAction({
    description: "Lưu nội dung kịch bản của một project, có chụp snapshot trước khi ghi.",
    request: z.object({
      projectId: z.string().min(1),
      content: z.string().max(200_000),
      topic: z.string().max(5000).default(""),
    }),
    response: okSchema,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      await ctx.executePrivileged(Factory.snapshotProject, {
        projectId: args.projectId,
        kind: "before-script-save",
      });
      const res = await ctx.executePrivileged(Factory.saveScript, args);
      ctx.invalidateQueries(["projects", "project"]);
      return res;
    },
  }),

  generateScriptAI: defineAction({
    description: "Sinh bản nháp kịch bản tiếng Việt bằng AI từ chủ đề và các sự kiện đã kiểm chứng do người dùng cung cấp. Mục tiêu thời lượng chỉ là gợi ý độ dài gộp vào prompt, không ràng buộc kịch bản đầu ra.",
    request: z.object({
      topic: z.string().min(1).max(5000),
      verifiedFacts: z.string().min(1).max(20_000),
      angle: z.string().max(2000).default(""),
      targetSeconds: z.number().int().min(30).max(600).default(240),
    }),
    response: z.object({ draft: z.string(), wordCount: z.number() }),
    async handler(ctx, args) {
      // Luật CEO 03/11: "Mục tiêu thời lượng" chỉ là prompt phụ mang
      // tính GỢI Ý, gộp chung vào prompt chính bên dưới — hệ số
      // 4,16 từ/giây chỉ đổi giây mục tiêu thành số từ dự tính để AI
      // định hướng độ dài khi viết. KHÔNG ràng buộc đầu ra: không
      // dung sai phần trăm, không cắt/bơm chữ cho khớp, không kiểm
      // tra đạt/không đạt theo con số này ở bất kỳ khâu nào.
      const draft = await ctx.inference.complete(buildScriptPrompt(args), {
        schema: z.string(),
      });
      const wordCount = draft.trim().split(/\s+/).filter(Boolean).length;
      return { draft, wordCount };
    },
  }),

  savePlan: defineAction({
    description: "Lưu plan phân cảnh và b-roll của một project, trả về danh sách vấn đề nếu plan chưa hợp lệ.",
    request: z.object({ projectId: z.string().min(1), plan: planSchema }),
    response: z.object({ ok: z.literal(true), problems: z.array(z.string()) }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      await ctx.executePrivileged(Factory.snapshotProject, {
        projectId: args.projectId,
        kind: "before-plan-save",
      });
      // Trước đây action còn insert thêm một dòng vào bảng snapshots của
      // app (note rỗng, không đường dẫn, không UI nào đọc) — trùng với
      // chính snapshot file mà snapshotProject vừa chụp. Đã bỏ (giai
      // đoạn 3, 03/11): snapshot thật nằm trong .snapshots/ của project
      // và xem/khôi phục được qua listSnapshots/restoreSnapshot.
      const res = await ctx.executePrivileged(Factory.savePlan, args);
      ctx.invalidateQueries(["projects", "project"]);
      return res;
    },
  }),

  getCatalogs: defineAction({
    description: "Đọc danh mục template, nhạc nền và hiệu ứng âm thanh SFX hiện có trong nhà máy.",
    request: z.object({}),
    response: z.object({
      templates: z.array(templateSchema),
      bgm: z.array(bgmTrackSchema),
      sfx: z.array(
        z.object({
          id: z.string(),
          file: z.string(),
          durationSec: z.number().nullable(),
        }),
      ),
    }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx) {
      return ctx.executePrivileged(Factory.getCatalogs, {});
    },
  }),

  startJob: defineAction({
    description: "Khởi chạy một bước xử lý nền cho project: TTS, chuẩn hóa, karaoke, preflight, render, tạo ảnh hoặc xuất file.",
    request: z.object({
      projectId: z.string().min(1),
      step: z.enum([
        "tts",
        "normalize",
        "karaoke",
        "preflight",
        "render",
        "genimages",
        "export",
      ]),
      force: z.boolean().default(false),
    }),
    response: z.object({ job: jobSchema }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const existing = await db
        .select()
        .from(schema.jobs)
        .where(eq(schema.jobs.projectId, args.projectId));
      const active = existing.find(
        (j) => j.step === args.step && j.status === "running",
      );
      if (active) {
        // A stale "running" row (dead process) must not block new jobs:
        // verify liveness through the status file first.
        const reconciled = await reconcileJob(ctx, active);
        if (reconciled.status === "running") return { job: reconciled };
      }
      if (args.step === "render") {
        await ctx.executePrivileged(Factory.snapshotProject, {
          projectId: args.projectId,
          kind: "before-render",
        });
      }
      const jobId = `job_${Date.now()}_${Math.floor(Math.random() * 1_000_000)}`;
      const startedAt = Date.now();
      await db.insert(schema.jobs).values({
        id: jobId,
        projectId: args.projectId,
        step: args.step,
        status: "running",
        startedAt,
        logTail: "",
        note: "",
      });
      const { logTail } = await ctx.executePrivileged(Factory.startJob, {
        jobId,
        projectId: args.projectId,
        step: args.step,
        force: args.force,
      });
      const rows = await db
        .select()
        .from(schema.jobs)
        .where(eq(schema.jobs.id, jobId));
      const row = rows[0];
      if (!row) throw new Error("Không tạo được job");
      return { job: { ...toJob(row), logTail: logTail || row.logTail } };
    },
  }),

  getJobStatus: defineAction({
    description: "Kiểm tra trạng thái hiện tại của một job nền và đồng bộ kết quả thật vào cơ sở dữ liệu của app.",
    request: z.object({ jobId: z.string().min(1) }),
    response: z.object({ job: jobSchema }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const rows = await db
        .select()
        .from(schema.jobs)
        .where(eq(schema.jobs.id, args.jobId));
      const row = rows[0];
      if (!row) throw new Error("Không thấy job");
      const job = await reconcileJob(ctx, row);
      if (job.status !== "running" && row.status === "running") {
        ctx.invalidateQueries(["projects", "project"]);
      }
      return { job };
    },
  }),

  listJobs: defineAction({
    description: "Liệt kê các job gần nhất của một project, đã đối chiếu với trạng thái thật trên đĩa.",
    request: z.object({ projectId: z.string().min(1) }),
    response: z.object({ jobs: z.array(jobSchema) }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const rows = await db
        .select()
        .from(schema.jobs)
        .where(eq(schema.jobs.projectId, args.projectId))
        .orderBy(desc(schema.jobs.startedAt))
        .limit(20);
      // Reconcile "running" rows against the on-disk job status through
      // the shared helper. Without this the list returned the DB row
      // verbatim, so a job whose runner died unseen (host reboot, killed
      // process) stayed "running" in the list forever even after its
      // detail had already reconciled.
      const jobs: Array<z.infer<typeof jobSchema>> = [];
      for (const row of rows) {
        jobs.push(await reconcileJob(ctx, row));
      }
      return { jobs };
    },
  }),

  cancelJob: defineAction({
    description: "Hủy một job nền đang chạy của project.",
    request: z.object({ jobId: z.string().min(1) }),
    response: z.object({ job: jobSchema }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const rows = await db
        .select()
        .from(schema.jobs)
        .where(eq(schema.jobs.id, args.jobId));
      const row = rows[0];
      if (!row) throw new Error("Không thấy job");
      if (row.status !== "running") return { job: toJob(row) };
      await ctx.executePrivileged(Factory.cancelJob, {
        jobId: row.id,
        projectId: row.projectId,
        step: row.step,
      });
      // Re-read the on-disk truth after the kill through the shared
      // helper: the status file now says cancelled (-2 → status
      // "cancelled"), already finished, or (kill failed) still running.
      const job = await reconcileJob(ctx, row);
      if (job.status !== "running") ctx.invalidateQueries(["projects", "project"]);
      return { job };
    },
  }),

  suggestKeywords: defineAction({
    description: "Gợi ý cụm từ khóa tiếng Việt và tiếng Anh để tìm media cho một đoạn tóm tắt cảnh.",
    request: z.object({ summary: z.string().min(1).max(2000) }),
    response: z.object({
      clusterId: z.string().nullable(),
      viPhrases: z.array(z.string()),
      enPhrases: z.array(z.string()),
      noCluster: z.boolean(),
    }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.suggestKeywords, {
        summary: args.summary,
      });
    },
  }),

  searchMedia: defineAction({
    description: "Tìm ứng viên ảnh hoặc video ở tầng Wikimedia hoặc kho stock cho một cảnh theo từ khóa.",
    request: z.object({
      layer: z.enum(["wikimedia", "stock"]),
      summary: z.string().min(1).max(2000),
      enKeywords: z.string().max(500).default(""),
      extraKeywords: z.string().max(500).default(""),
      mediaType: z.enum(["image", "video"]),
      durationSec: z.number().min(0).max(3600).default(0),
    }),
    response: z.object({
      candidates: z.array(mediaCandidateSchema),
      queriesTried: z.array(z.string()),
      note: z.string(),
    }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.searchMedia, args);
    },
  }),

  pickMedia: defineAction({
    description: "Tải file media đã chọn về project và ghi thông tin nguồn gốc vào plan.",
    request: z.object({
      projectId: z.string().min(1),
      sceneOrder: z.number().int().positive(),
      partId: z.string().nullable(),
      fileUrl: z.string().min(1),
      mediaType: z.enum(["image", "video"]),
      source: z.string().min(1).max(200),
      pageUrl: z.string().max(2000).default(""),
      license: z.string().max(200).default(""),
      author: z.string().max(500).default(""),
      score: z.number().nullable().default(null),
      verdict: z.string().max(100).default(""),
      runnerUpScore: z.number().nullable().default(null),
    }),
    response: z.object({ fileName: z.string() }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const res = await ctx.executePrivileged(Factory.pickMedia, args);
      ctx.invalidateQueries(["project"]);
      return res;
    },
  }),

  generateAiMedia: defineAction({
    description: "Tạo ảnh hoặc video bằng AI cho một cảnh hoặc part khi tìm kiếm không có file phù hợp.",
    request: z.object({
      projectId: z.string().min(1),
      sceneOrder: z.number().int().positive(),
      partId: z.string().nullable(),
      prompt: z.string().min(1).max(4000),
      mediaType: z.enum(["image", "video"]),
    }),
    response: z.object({ fileName: z.string() }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const res = await ctx.executePrivileged(Factory.generateAiMedia, args);
      ctx.invalidateQueries(["project"]);
      return res;
    },
  }),

  renderTemplatePreview: defineAction({
    description: "Render thử một template với dữ liệu nhập cho trước và trả về ảnh PNG xem trước.",
    request: z.object({
      templateId: z.string().min(1),
      inputs: z.record(
        z.string(),
        z.union([z.string(), z.number(), z.boolean()]).nullable(),
      ),
    }),
    response: z.object({ pngBase64: z.string() }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.renderTemplatePreview, args);
    },
  }),

  getMediaDataUrl: defineAction({
    description: "Đọc một file media nhỏ của project dưới dạng data URL để hiển thị hoặc phát trong app.",
    request: z.object({
      projectId: z.string().min(1),
      relPath: z.string().min(1).max(500),
    }),
    response: z.object({ dataUrl: z.string() }),
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.getMediaUrl, args);
    },
  }),

  // Chunked transfer for large media files: the inline data-URL action
  // cannot carry a tens-of-MB file — base64 inflates it further in one
  // response and the daemon truncates it. The client requests <=2 MiB raw
  // chunks and reassembles a Blob locally (ảnh, video b-roll, BGM/SFX của
  // Preview HTML).
  getMediaChunk: defineAction({
    description: "Đọc một đoạn tối đa 2 MiB của file media lớn của project để client ghép lại thành Blob hiển thị trong app.",
    request: z.object({
      projectId: z.string().min(1),
      relPath: z.string().min(1).max(500),
      offset: z.number().int().min(0),
      length: z.number().int().min(1).max(2_097_152),
    }),
    response: Factory.getMediaChunk.response,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.getMediaChunk, args);
    },
  }),

  getPreviewData: defineAction({
    description: "Dựng dữ liệu Preview HTML của project gồm engine render, từng part, karaoke, nhạc nền và các sự kiện SFX đã cắt theo đúng luật render.",
    request: z.object({ projectId: z.string().min(1) }),
    response: Factory.getPreviewData.response,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.getPreviewData, args);
    },
  }),

  softDeleteProject: defineAction({
    description: "Xoá một project vào thùng rác của app mà không xóa file trên đĩa (khôi phục được).",
    request: z.object({ projectId: z.string().min(1), name: z.string().default("") }),
    response: okSchema,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      await db
        .insert(schema.trash)
        .values({
          projectId: args.projectId,
          name: args.name,
          deletedAt: Date.now(),
        })
        .onConflictDoUpdate({
          target: schema.trash.projectId,
          set: { deletedAt: Date.now(), name: args.name },
        });
      ctx.invalidateQueries(["projects"]);
      return { ok: true as const };
    },
  }),

  restoreProject: defineAction({
    description: "Khôi phục một project đang nằm trong thùng rác của app.",
    request: z.object({ projectId: z.string().min(1) }),
    response: okSchema,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      await db.delete(schema.trash).where(eq(schema.trash.projectId, args.projectId));
      ctx.invalidateQueries(["projects"]);
      return { ok: true as const };
    },
  }),

  deleteProjectForever: defineAction({
    description: "Xóa vĩnh viễn một project đang ở trong thùng rác, bao gồm toàn bộ file trên đĩa.",
    request: z.object({ projectId: z.string().min(1) }),
    response: okSchema,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const inTrash = await db
        .select()
        .from(schema.trash)
        .where(eq(schema.trash.projectId, args.projectId));
      if (inTrash.length === 0) {
        throw new Error("Chỉ xóa vĩnh viễn được project đang ở trong thùng rác");
      }
      await ctx.executePrivileged(Factory.deleteProjectForever, {
        projectId: args.projectId,
      });
      await db.delete(schema.trash).where(eq(schema.trash.projectId, args.projectId));
      ctx.invalidateQueries(["projects"]);
      return { ok: true as const };
    },
  }),

  listSnapshots: defineAction({
    description: "Liệt kê các snapshot đã chụp của một project (input, kịch bản, plan, TTS) mới nhất trước, để người dùng xem và khôi phục.",
    request: z.object({ projectId: z.string().min(1) }),
    response: Factory.listSnapshots.response,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      return ctx.executePrivileged(Factory.listSnapshots, args);
    },
  }),

  restoreSnapshot: defineAction({
    description: "Khôi phục input, kịch bản, plan và TTS của project từ một snapshot đã chụp; trạng thái hiện tại được chụp lại trước khi ghi đè.",
    request: z.object({
      projectId: z.string().min(1),
      snapshotId: z.string().min(1),
    }),
    response: okSchema,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const res = await ctx.executePrivileged(Factory.restoreSnapshot, args);
      ctx.invalidateQueries(["projects", "project"]);
      return res;
    },
  }),

  deleteSnapshot: defineAction({
    description: "Xóa một snapshot của project khỏi thư mục .snapshots để giải phóng đĩa.",
    request: z.object({
      projectId: z.string().min(1),
      snapshotId: z.string().min(1),
    }),
    response: okSchema,
    privileged: ALL_PRIVILEGED,
    async handler(ctx, args) {
      const res = await ctx.executePrivileged(Factory.deleteSnapshot, args);
      ctx.invalidateQueries(["project"]);
      return res;
    },
  }),

  getAutoProgress: defineAction({
    description: "Đọc tiến độ 10 bước của panel Tạo video tự động đã lưu cho một project, để mở lại app vẫn thấy đúng trạng thái.",
    request: z.object({ projectId: z.string().min(1) }),
    response: z.object({
      progress: z
        .object({
          statuses: z.record(
            z.string(),
            z.enum(["pending", "running", "done", "error", "skipped"]),
          ),
          messages: z.array(z.string()),
          needsManual: z.array(z.string()),
          updatedAt: z.number(),
        })
        .nullable(),
    }),
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const rows = await db
        .select()
        .from(schema.autoProgress)
        .where(eq(schema.autoProgress.projectId, args.projectId));
      const row = rows[0];
      if (!row) return { progress: null };
      const parse = <T,>(raw: string, fallback: T): T => {
        try {
          return JSON.parse(raw) as T;
        } catch {
          return fallback;
        }
      };
      return {
        progress: {
          statuses: parse(row.statuses, {}),
          messages: parse<string[]>(row.messages, []),
          needsManual: parse<string[]>(row.needsManual, []),
          updatedAt: row.updatedAt,
        },
      };
    },
  }),

  saveAutoProgress: defineAction({
    description: "Lưu tiến độ 10 bước của panel Tạo video tự động cho một project xuống server.",
    request: z.object({
      projectId: z.string().min(1),
      statuses: z.record(
        z.string(),
        z.enum(["pending", "running", "done", "error", "skipped"]),
      ),
      messages: z.array(z.string().max(4000)).max(60),
      needsManual: z.array(z.string().max(500)).max(100),
    }),
    response: okSchema,
    async handler(ctx, args) {
      const db = ctx.db<typeof schema>();
      const values = {
        projectId: args.projectId,
        statuses: JSON.stringify(args.statuses),
        messages: JSON.stringify(args.messages.slice(-60)),
        needsManual: JSON.stringify(args.needsManual),
        updatedAt: Date.now(),
      };
      await db
        .insert(schema.autoProgress)
        .values(values)
        .onConflictDoUpdate({
          target: schema.autoProgress.projectId,
          set: {
            statuses: values.statuses,
            messages: values.messages,
            needsManual: values.needsManual,
            updatedAt: values.updatedAt,
          },
        });
      return { ok: true as const };
    },
  }),

} satisfies ActionsModule;
