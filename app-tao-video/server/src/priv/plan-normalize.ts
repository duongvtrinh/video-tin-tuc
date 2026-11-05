// Chuẩn hóa provenance/template-inputs của plan trước khi trả về client
// hoặc ghi xuống đĩa: pipeline bên ngoài đã ghi mediaSource dưới nhiều
// hình dạng qua thời gian, tầng này ép mọi bản ghi về hình dạng schema
// chịu được mà không mất khóa lạ. Hàm isAiSource ở đây được dùng chung
// bởi handlers-projects, projects (buildGenImageJobs) và media-library
// (B20, 05/11/2026).

// "AI" phải đứng thành từ riêng — khớp lỏng lẻo sẽ bắt nhầm chữ "ai"
// trong từ tiếng Việt (Hải, bài, tải…) ở tên nguồn báo. (Chuyển từ
// media-library sang đây ở B20 để cả 3 nơi dùng chung một quy tắc.)
const AI_SOURCE_RE = /(^|[\s([{\/—–-])AI($|[\s)\]}\/—–\-:,.])/;

function isAiText(text: string): boolean {
  const t = text.toLowerCase();
  return (
    t.includes("prompt-ai") ||
    t.includes("ai-tu-prompt") ||
    t.includes("ai từ prompt") ||
    AI_SOURCE_RE.test(text)
  );
}

// B20 (05/11/2026, lệnh CEO, lựa chọn A): một hàm nhận diện "ảnh AI" dùng
// chung cho buildGenImageJobs (projects.ts), plan-normalize và
// media-library — trước đây 3 nơi nhận diện khác nhau (projects.ts chỉ
// khớp đúng 2 chuỗi "ai-tu-prompt"/"AI từ prompt", media-library khớp cả
// type "prompt-AI", plan-normalize suy source từ type). Nhận
// type/source/classification chứa "prompt-AI", "ai-tu-prompt" hoặc "AI từ
// prompt" (không phân biệt hoa/thường); chấp nhận mediaSource dạng chuỗi
// trần. Một bản ghi có trường prompt/aiPrompt mà type chứa "prompt" cũng
// là ảnh AI (pipeline cũ ghi {type: "prompt-...", prompt: ...}).
export function isAiSource(value: unknown): boolean {
  if (typeof value === "string") return isAiText(value);
  if (value && typeof value === "object") {
    const rec = value as Record<string, unknown>;
    for (const k of ["type", "source", "classification"]) {
      const v = rec[k];
      if (typeof v === "string" && isAiText(v)) return true;
    }
    const typeStr = typeof rec["type"] === "string" ? rec["type"] : "";
    const hasPrompt =
      typeof rec["prompt"] === "string" || typeof rec["aiPrompt"] === "string";
    if (hasPrompt && /prompt/i.test(typeStr)) return true;
    return false;
  }
  return false;
}

// The Production pipeline has written mediaSource in several shapes over
// time; the newest ones record {type, prompt, note} or {type, aiPrompt,
// file, visualCheck} with no `source` at all, which used to make the
// closed response schema reject the whole project. The UI renders
// mediaSource.source, and the plan law requires every mediaSource to
// carry one, so when `source` is missing/null we derive it from `type`,
// falling back to a prompt marker or an explicit "not recorded" label.
// getProject applies this only to the returned copy — it never writes
// the plan file; savePlan applies it before writing so plans saved
// through the app always carry a source string. B41 (06/11/2026, lệnh
// CEO, lựa chọn A): "Chưa ghi nguồn" chỉ là nhãn hiển thị cho bản trả
// về — savePlan gọi với inventSource: false để KHÔNG ghi chuỗi bịa này
// xuống đĩa (ghi bịa thì kiểm tra thiếu source ở savePlan không còn
// cảnh báo nữa); plan trên đĩa giữ nguyên thiếu source cho tới khi
// Production ghi nguồn thật.
function normalizeProvenance(value: unknown, inventSource = true): unknown {
  // The pipeline has also written provenance as a BARE STRING (topic053001
  // records broll.videoSource as just a Pexels page URL). Wrap it into the
  // object shape instead of letting response validation reject the whole
  // project: a URL becomes page_url, any other string becomes the source.
  if (typeof value === "string") {
    value = /^https?:\/\//i.test(value.trim())
      ? { page_url: value }
      : { source: value };
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) return value;
  const rec = value as Record<string, unknown>;
  // Coerce EVERY field to a schema-safe shape, not just the known string
  // fields: the pipeline's provenance shapes keep drifting, and one
  // number/boolean/object sitting in a string-declared field used to fail
  // the entire getProject response. score/runnerUpScore/visuallyChecked
  // already accept number/boolean unions and duration_sec is numeric, so
  // those are only coerced when they arrive as the wrong kind entirely.
  for (const k of Object.keys(rec)) {
    const v = rec[k];
    if (v === null || v === undefined || typeof v === "string") continue;
    if (k === "duration_sec") {
      const n = typeof v === "number" ? v : Number(v);
      if (Number.isFinite(n)) rec[k] = n;
      else delete rec[k];
      continue;
    }
    if (
      (k === "score" || k === "runnerUpScore" || k === "visuallyChecked") &&
      (typeof v === "number" || typeof v === "boolean")
    ) {
      continue;
    }
    rec[k] = typeof v === "object" ? JSON.stringify(v) : String(v);
  }
  const asStr = (v: unknown): string | null =>
    typeof v === "string" && v.trim()
      ? v
      : typeof v === "number" || typeof v === "boolean"
        ? String(v)
        : null;
  let source = asStr(rec["source"]);
  // B20: bản ghi AI thì nguồn chuẩn hóa về "AI từ prompt" để 3 nơi nhận
  // diện cùng một chuỗi; chỉ bản ghi không phải AI mới giữ nguyên type.
  if (!source && isAiSource(rec)) source = "AI từ prompt";
  if (!source) source = asStr(rec["type"]);
  if (!source) {
    // B41: chỉ bịa "Chưa ghi nguồn" cho bản trả về (inventSource); bản
    // ghi xuống đĩa thì để trống source để cảnh báo thiếu nguồn còn chạy.
    if (typeof rec["aiPrompt"] === "string" || typeof rec["prompt"] === "string") {
      source = "AI từ prompt";
    } else if (inventSource) {
      source = "Chưa ghi nguồn";
    }
  }
  if (source) rec["source"] = source;
  else delete rec["source"];
  for (const k of ["license", "pageUrl", "page_url", "title", "author"]) {
    const s = asStr(rec[k]);
    if (rec[k] != null && s != null) rec[k] = s;
  }
  return rec;
}

// Template inputs reach the template engine as text, but the pipeline
// writes some as raw JSON numbers/booleans (bar-chart w1..w4 = 100/52/62/0
// in drone001). Coerce every value to its string form — null means "no
// value" and drops the key, objects (never valid input) are JSON-encoded
// so the shape stays a flat string record instead of crashing validation.
function normalizeTemplateInputs(value: unknown): unknown {
  if (!value || typeof value !== "object" || Array.isArray(value)) return value;
  const out: Record<string, string> = {};
  for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
    if (v === null || v === undefined) continue;
    out[k] =
      typeof v === "string"
        ? v
        : typeof v === "object"
          ? JSON.stringify(v)
          : String(v);
  }
  return out;
}

export function normalizePlanProvenance<T>(plan: T, opts?: { inventSource?: boolean }): T {
  if (!plan || typeof plan !== "object") return plan;
  const inventSource = opts?.inventSource ?? true;
  const scenes = (plan as { scenes?: unknown }).scenes;
  if (!Array.isArray(scenes)) return plan;
  for (const scene of scenes) {
    if (!scene || typeof scene !== "object") continue;
    const s = scene as Record<string, unknown>;
    // The pipeline writes explicit null for "no value" on optional fields
    // (e.g. imageFile: null on every scene of topic037001); optional in the
    // schema means the key may be absent, so drop nulls to be safe even
    // where a field is not declared nullable.
    for (const k of ["imageFile", "cardImage", "motion", "text", "sceneScriptSummary", "sceneImagePrompt"]) {
      if (s[k] === null) delete s[k];
    }
    if ("mediaSource" in s) s["mediaSource"] = normalizeProvenance(s["mediaSource"], inventSource);
    const parts = s["parts"];
    if (!Array.isArray(parts)) continue;
    for (const part of parts) {
      if (!part || typeof part !== "object") continue;
      const partRec = part as Record<string, unknown>;
      if (partRec["broll"] === null) delete partRec["broll"];
      const broll = partRec["broll"];
      if (!broll || typeof broll !== "object" || Array.isArray(broll)) continue;
      const b = broll as Record<string, unknown>;
      for (const k of ["templateId", "file", "scriptSummary", "prompt", "videoNote", "keepAudio", "mediaType", "sourceStartSec", "inputs", "sfx"]) {
        if (b[k] === null) delete b[k];
      }
      if ("inputs" in b) b["inputs"] = normalizeTemplateInputs(b["inputs"]);
      if ("mediaSource" in b) b["mediaSource"] = normalizeProvenance(b["mediaSource"], inventSource);
      if ("videoSource" in b) b["videoSource"] = normalizeProvenance(b["videoSource"], inventSource);
    }
  }
  return plan;
}
