// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "./api";
import type { ApiResponse } from "./api";


export type ProjectSummary = ApiResponse<typeof api, "listProjects">["projects"][number];
export type ProjectDetail = ApiResponse<typeof api, "getProject">;
export type Plan = NonNullable<ProjectDetail["plan"]>;
export type Scene = Plan["scenes"][number];
export type Part = Scene["parts"][number];
export type BgmTrack = ApiResponse<typeof api, "getCatalogs">["bgm"][number];
export type Candidate = ApiResponse<typeof api, "searchMedia">["candidates"][number];
export type Job = ApiResponse<typeof api, "listJobs">["jobs"][number];

export const STEP_DEFS: Array<{ key: keyof ProjectSummary["steps"]; label: string }> = [
  { key: "script", label: "Kịch bản" },
  { key: "plan", label: "Plan" },
  { key: "tts", label: "TTS" },
  { key: "karaoke", label: "Karaoke" },
  { key: "preview", label: "Preview" },
  { key: "exported", label: "ZIP" },
];

export const JOB_LABELS: Record<string, string> = {
  tts: "TTS",
  normalize: "Chuẩn hóa chunk",
  karaoke: "Karaoke",
  preflight: "Preflight",
  render: "Render",
  genimages: "Tạo ảnh cảnh",
  export: "Xuất ZIP",
};

export const MOTIONS = ["", "zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down"];

// Nhãn + màu trạng thái job DÙNG CHUNG cho JobRunner và JobsList (giai
// đoạn 3, 03/11 — trước đây mỗi nơi tự viết một bản và cả hai cùng
// special-case exitCode -2). Job bị hủy nay có status "cancelled" riêng
// từ server; exitCode -2 chỉ còn là dữ liệu cũ trong DB trước bản sửa.
export function jobStatusLabel(job: Job, style: "sentence" | "short"): string {
  if (job.status === "done") return style === "sentence" ? "Xong" : "xong";
  if (job.status === "cancelled" || job.exitCode === -2) {
    return style === "sentence" ? "Đã hủy job" : "đã hủy";
  }
  if (job.status === "error") {
    return style === "sentence" ? `Lỗi (mã ${job.exitCode ?? "?"})` : `lỗi mã ${job.exitCode ?? "?"}`;
  }
  return style === "sentence"
    ? "Đang chạy nền — cứ để đó, mở lại app vẫn thấy tiến độ"
    : "đang chạy";
}

export function jobStatusColor(job: Job): string {
  if (job.status === "done") return "var(--ok)";
  if (job.status === "error") return "var(--bad)";
  return "var(--warn)";
}

// Poll chỉ chạy khi tab đang hiện (giai đoạn 2, 03/11): trước đây danh
// sách job poll 8s và chi tiết project poll 15s vô điều kiện, kể cả khi
// người dùng đã chuyển tab/app khác — tốn pin và tải server vô ích.
export function pollWhenVisible(ms: number): number | false {
  return typeof document !== "undefined" && document.hidden ? false : ms;
}

// Lõi định dạng phút:giây dùng chung cho fmtSec và fmtClock (giai đoạn
// 3, 03/11 — hai hàm trước đây chép gần như nguyên xi phần tính toán).
export function fmtMinSecCore(sec: number): { m: number; sText: string } {
  const m = Math.floor(sec / 60);
  const s = sec - m * 60;
  return { m, sText: s.toFixed(1).padStart(4, "0") };
}

export function fmtSec(sec: number | null | undefined): string {
  if (sec === null || sec === undefined || Number.isNaN(sec)) return "—";
  const { m, sText } = fmtMinSecCore(sec);
  return m > 0 ? `${m}:${sText}` : `${sec.toFixed(1)}s`;
}

export function fmtBytes(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)} MB`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)} KB`;
  return `${n} B`;
}

export function countWords(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

export type TabKey = "script" | "scenes" | "media" | "audio" | "preview" | "finish";

// Tách kịch bản thành cảnh/part — cùng luật với nút tách tay ở tab Kịch
// bản (đoạn văn -> cảnh, gộp câu tới ~45 từ -> part), dùng chung cho cả
// chế độ tự động để hai đường không lệch nhau.
export function splitScriptToScenes(content: string): Scene[] {
  const paragraphs = content.split(/\n\s*\n/).map((s) => s.trim()).filter(Boolean);
  const blocks = paragraphs.length > 1 ? paragraphs : content.split(/(?<=[.!?…])\s+/).reduce<string[]>((acc, sentence) => {
    const last = acc[acc.length - 1];
    if (last && countWords(last) < 45) acc[acc.length - 1] = `${last} ${sentence}`;
    else acc.push(sentence);
    return acc;
  }, []);
  return blocks.map((block, i) => {
    const sentences = block.split(/(?<=[.!?…])\s+/).filter(Boolean);
    const parts: Part[] = [];
    let buf = "";
    const flush = () => {
      if (buf.trim()) {
        const voiceText = buf.trim();
        // Tóm tắt b-roll của part điền sẵn từ chính lời đọc của part:
        // hàng đợi media của chế độ tự động dùng nó để tìm media thay vì
        // bỏ qua lặng lẽ part không có prompt như trước. Người dùng vẫn
        // sửa được ở bước 2/3.
        parts.push({ id: `scene${i + 1}-part-${parts.length + 1}`, voiceText, broll: { scriptSummary: voiceText } });
        buf = "";
      }
    };
    for (const s of sentences) {
      if (countWords(`${buf} ${s}`) > 45 && buf) flush();
      buf = `${buf} ${s}`.trim();
    }
    flush();
    if (parts.length === 0) parts.push({ id: `scene${i + 1}-part-1`, voiceText: block, broll: { scriptSummary: block } });
    // Tóm tắt + prompt cảnh điền sẵn bản nháp từ chính nội dung cảnh
    // (câu đầu của cảnh) thay vì để trống: media queue có ngay dữ kiện
    // để tìm ảnh, người dùng kiểm tra/sửa lại ở bước 2 trước khi tin.
    const firstSentence = (sentences[0] ?? block).trim();
    const summaryDraft = firstSentence.length > 220 ? `${firstSentence.slice(0, 217).trimEnd()}…` : firstSentence;
    return {
      id: `scene${i + 1}`,
      order: i + 1,
      sceneScriptSummary: summaryDraft,
      sceneImagePrompt: `Ảnh minh họa dọc 9:16, không chữ, không watermark: ${summaryDraft}`,
      text: block,
      parts,
    } as Scene;
  });
}

// Luật reset theo kịch bản (CEO 03/11): phân cảnh chỉ còn giá trị khi
// nội dung của chúng KHỚP kịch bản hiện tại. Nội dung "ở phân cảnh" là
// toàn bộ lời đọc của các part theo đúng thứ tự cảnh/part — khi tách
// cảnh, các part được cắt nguyên từ kịch bản nên ghép lại (chuẩn hóa
// khoảng trắng) phải bằng đúng kịch bản; lệch nhau nghĩa là kịch bản
// đã đổi sau khi tách (hoặc phân cảnh đã bị sửa khác kịch bản).
export function normalizeScriptText(t: string): string {
  return t.replace(/\s+/g, " ").trim();
}
export function planVoiceText(plan: Plan): string {
  return plan.scenes
    .flatMap((s) => s.parts.map((p) => p.voiceText))
    .join(" ");
}
// true = chưa có phân cảnh nào để so (không có gì phải reset);
// false = đã có phân cảnh nhưng nội dung khác kịch bản hiện tại.
export function scriptMatchesPlan(detail: ProjectDetail): boolean {
  if (!detail.plan || detail.plan.scenes.length === 0) return true;
  return normalizeScriptText(planVoiceText(detail.plan)) === normalizeScriptText(detail.scriptContent);
}

// Lý do cụ thể chặn render — nút Tạo Video không còn bấm được khi chưa
// đủ điều kiện rồi mới ra nền đen/lỗi khó hiểu.
export function renderBlockers(detail: ProjectDetail): string[] {
  const blockers: string[] = [];
  const scenes = detail.plan?.scenes ?? [];
  if (!detail.scriptContent.trim()) blockers.push("Chưa có kịch bản — viết/lưu kịch bản ở bước 1 trước");
  if (scenes.length === 0) blockers.push("Chưa có phân cảnh — tách kịch bản thành cảnh/part ở bước 1 hoặc 2 trước");
  // A21 (05/11/2026): cảnh nền rêu vẫn tính là thiếu ảnh thật.
  const missingScenes = scenes.filter((s) => !s.imageFile || s.isMossGrid);
  if (scenes.length > 0 && missingScenes.length > 0) {
    blockers.push(`Còn ${missingScenes.length} cảnh chưa có ảnh thật (${missingScenes.map((s) => `cảnh ${s.order}`).join(", ")}) — cảnh không có file ảnh sẽ ra nền đen khi render; cảnh nền xanh rêu vẫn tính là thiếu ảnh ở tầng hồ sơ/QA, bổ sung ở bước 3 · Media hoặc chạy Tạo video tự động`);
  }
  if (detail.ttsParts.length === 0) blockers.push("Chưa có TTS — chạy TTS ở bước 4 trước");
  if (detail.karaokeLineCount === 0) blockers.push("Chưa có karaoke — chạy chuẩn hóa + karaoke ở bước 4 trước");
  return blockers;
}

export function firstIncompleteTab(summary: ProjectSummary | undefined, detail: ProjectDetail | undefined): TabKey {
  if (!summary) return "script";
  // Đối chiếu NỘI DUNG thật, không chỉ cờ steps của summary: kịch bản
  // trống (project mới nào cũng có sẵn file script.json rỗng) nghĩa là
  // công việc tiếp theo vẫn là nhập kịch bản ở tab 1; plan có file
  // nhưng 0 cảnh (sau reset theo kịch bản) thì công việc tiếp theo vẫn
  // là tách phân cảnh ở tab 2. Thiếu hai chốt này, tab mở đầu nhảy
  // xuống Phân cảnh/TTS trông như active ngẫu nhiên.
  const hasScript = detail
    ? detail.scriptContent.trim().length > 0 ||
      (detail.plan?.scenes.length ?? 0) > 0
    : summary.steps.script;
  if (!hasScript) return "script";
  const sceneCount = detail?.plan?.scenes.length;
  if (!summary.steps.plan || sceneCount === 0) return "scenes";
  if (detail && (detail.plan?.scenes ?? []).some((s) => !s.imageFile || s.isMossGrid)) return "media";
  if (!summary.steps.tts || !summary.steps.karaoke) return "audio";
  if (!summary.steps.preview) return "preview";
  if (!summary.steps.exported) return "finish";
  return "finish";
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// Large media (a rendered MP4 can be tens of MB) cannot ride in one action
// response as a base64 data URL — the daemon truncates it. Fetch the file
// in 2 MiB raw chunks via getMediaChunk and reassemble a Blob locally.
const MEDIA_CHUNK_BYTES = 2 * 1024 * 1024;

function base64ToArrayBuffer(b64: string): ArrayBuffer {
  const bin = atob(b64);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  return bytes.buffer as ArrayBuffer;
}

export async function fetchMediaBlob(
  projectId: string,
  relPath: string,
  onProgress?: (loaded: number, total: number) => void,
): Promise<{ blob: Blob; mime: string; totalSize: number }> {
  const parts: ArrayBuffer[] = [];
  let offset = 0;
  let total = -1;
  let mime = "application/octet-stream";
  while (total === -1 || offset < total) {
    const res = await api.getMediaChunk({
      projectId,
      relPath,
      offset,
      length: MEDIA_CHUNK_BYTES,
    });
    mime = res.mime;
    total = res.totalSize;
    if (res.chunkBytes > 0) parts.push(base64ToArrayBuffer(res.base64));
    offset += res.chunkBytes;
    onProgress?.(offset, total);
    if (res.eof || res.chunkBytes === 0) break;
  }
  return { blob: new Blob(parts, { type: mime }), mime, totalSize: Math.max(total, 0) };
}

export const inputCls =
  "w-full rounded-lg border border-[var(--border)] bg-[var(--surface2)] px-3 py-2 text-sm text-[var(--text)] outline-none focus:border-[var(--accent)]";
export const labelCls = "block text-xs font-semibold uppercase tracking-wide text-[var(--dim)] mb-1";
export const btnCls =
  "rounded-lg border border-[var(--border)] bg-[var(--surface2)] px-3 py-2 text-sm font-semibold text-[var(--text)] active:opacity-70 disabled:opacity-40";
export const btnPrimary =
  "rounded-lg bg-[var(--accent)] px-4 py-2 text-sm font-bold text-[var(--accent-text)] active:opacity-80 disabled:opacity-40";

// Đọc nguồn gốc (mediaSource) về dạng text hiển thị — dùng chung cho
// tab Phân cảnh và tab Media (chuyển từ ScenesTab sang lib khi tách
// file, nguyên văn không đổi).
export function provText(
  ms: string | { source?: string | null; license?: string | null } | null | undefined,
): { source: string; license: string } {
  if (!ms) return { source: "", license: "" };
  if (typeof ms === "string") return { source: ms, license: "" };
  return { source: ms.source ?? "", license: ms.license ?? "" };
}

export function toStringInputs(
  inputs: Record<string, string | number | boolean | null> | null | undefined,
): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(inputs ?? {})) {
    out[k] = v === null || v === undefined ? "" : String(v);
  }
  return out;
}
