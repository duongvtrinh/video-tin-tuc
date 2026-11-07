// Core dùng chung của tầng privileged: đường dẫn nhà máy VieNeu Asset
// Factory, hợp đồng tên file, tiện ích đọc/ghi JSON, khóa ghi plan theo
// project và các wrapper chạy lệnh ngoài (spawn/ffprobe). Chỉ
// privileged.ts (và các module priv/ khác) import file này — actions.ts
// không được chạm vào.
import { execFileSync, spawn } from "node:child_process";
import { createHash, randomInt, randomUUID } from "node:crypto";
import { lookup } from "node:dns/promises";
import {
  existsSync,
  readFileSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { isIP } from "node:net";
import { basename, dirname, join } from "node:path";

export const HOME = homedir();
// Resolve thư mục nhà máy theo thứ tự ưu tiên, theo mẫu resolveTtsPy
// trong cùng file (quyết CEO 05/11/2026, mục A25 — ghi vào repo sau khi
// rebuild §6 đã kiểm chứng app đọc đúng factory trên máy thật):
//   1. Biến môi trường VIENEU_FACTORY_DIR (nếu đặt)
//   2. ~/workspace/vieneu-media-company/vieneu-asset-factory nếu tồn tại (layout repo)
//   3. ~/workspace/vieneu-asset-factory nếu tồn tại (layout cũ)
//   4. ~/workspace/asset-factory nếu tồn tại (layout cũ nhất)
//   5. Mặc định ~/workspace/vieneu-media-company/vieneu-asset-factory (layout repo)
function resolveFactory(): string {
  const envDir = process.env.VIENEU_FACTORY_DIR?.trim();
  // B41 (06/11/2026, lệnh CEO, lựa chọn A): env trỏ sai thì bỏ qua, rơi
  // xuống ứng viên tiếp theo — trước đây trả thẳng đường chết.
  if (envDir && existsSync(envDir)) return envDir;
  for (const cand of [
    "vieneu-media-company/vieneu-asset-factory",
    "vieneu-asset-factory",
    "asset-factory",
  ]) {
    const p = join(HOME, "workspace", cand);
    if (existsSync(p)) return p;
  }
  return join(HOME, "workspace/vieneu-media-company/vieneu-asset-factory");
}
export const FACTORY = resolveFactory();
export const PROJECTS = join(FACTORY, "projects");
export const BIN = join(FACTORY, "bin");
export const VENV_PY = join(FACTORY, ".venv/bin/python");
// Resolve đường dẫn Python của venv TTS theo thứ tự ưu tiên để app chạy
// được cả trên máy hiện tại (TTS ở ~/workspace/vieneu-tts-api) lẫn trên
// bản clone mới của monorepo (TTS ở vieneu-tts):
//   1. Biến môi trường VIENEU_TTS_DIR (nếu đặt): $VIENEU_TTS_DIR/.venv/bin/python
//   2. ~/workspace/vieneu-tts/.venv/bin/python nếu tồn tại (layout repo)
//   3. ~/workspace/vieneu-tts-api/.venv/bin/python nếu tồn tại (máy hiện tại)
//   4. Mặc định ~/workspace/vieneu-tts/.venv/bin/python (layout repo)
function resolveTtsPy(): string {
  const envDir = process.env.VIENEU_TTS_DIR?.trim();
  // B41: như resolveFactory — env sai thì bỏ qua thay vì trả đường chết.
  if (envDir && existsSync(join(envDir, ".venv/bin/python"))) return join(envDir, ".venv/bin/python");
  const repoPath = join(HOME, "workspace/vieneu-tts/.venv/bin/python");
  if (existsSync(repoPath)) return repoPath;
  const legacyPath = join(HOME, "workspace/vieneu-tts-api/.venv/bin/python");
  if (existsSync(legacyPath)) return legacyPath;
  return repoPath;
}
export const TTS_PY = resolveTtsPy();
// SEARCH_MEDIA: file thật nằm trong monorepo (quyết CEO 05/11/2026,
// mục A25) — đường cũ ~/workspace/company-os/... không tồn tại.
function resolveSearchMedia(): string {
  const repoPath = join(HOME, "workspace/vieneu-media-company/company-os/media-search/search_media.py");
  if (existsSync(repoPath)) return repoPath;
  // B41 (06/11/2026, lệnh CEO, lựa chọn A): đường cũ
  // ~/workspace/company-os/... không tồn tại — ném lỗi rõ thay vì trả
  // đường chết rồi vỡ ở chỗ gọi.
  throw new Error(`Không tìm thấy search_media.py (đã thử ${repoPath}) — kiểm tra lại vị trí repo`);
}
export const SEARCH_MEDIA = resolveSearchMedia();
export const PY3 = "python3";

// Filename contract of the factory (bin/filename.py — the single source
// of truth, replicated here character-for-character): rand6 is the first
// 6 decimal digits found in the md5 hex digest of the parts joined with
// "|", right-padded with "0" (Python str.ljust) when fewer than 6 digits
// occur. Media files the app creates MUST carry these deterministic
// names: bin/render_draft.py looks media up by exactly this contract
// (seg_<order>_<rand6(pid,'img',order)>.jpg,
// broll_seg_<order>_part_<pi>_<rand6(pid,'broll',order,pi)>.*), so the
// old random suffix made app-created media invisible to the render —
// black clips and wrong images. Voice/part WAV names follow the same
// contract (voice seed is 'seg', part-wav seed is 'part') but are minted
// by bin/tts_batch.py itself, never by the app.
export function rand6(...parts: Array<string | number>): string {
  const hex = createHash("md5")
    .update(parts.map(String).join("|"), "utf8")
    .digest("hex");
  return hex.replace(/[^0-9]/g, "").slice(0, 6).padEnd(6, "0");
}

export function sceneImageFileName(projectId: string, order: number | string): string {
  return `seg_${order}_${rand6(projectId, "img", order)}.jpg`;
}

export function brollFileName(
  projectId: string,
  order: number | string,
  partIdx: number | string,
  ext: string,
): string {
  return `broll_seg_${order}_part_${partIdx}_${rand6(projectId, "broll", order, partIdx)}.${ext}`;
}

// Random suffix for NON-media names only (project ids, temp files):
// nothing looks those up through the filename contract, so they stay
// random and unique. Never use this for a media file name.
export function randomSuffix(): string {
  return String(randomInt(0, 1_000_000)).padStart(6, "0");
}

export function safeId(id: string): string {
  // Chặn id rỗng, "." , ".." và mọi id chỉ gồm dấu chấm (vá audit 05/11/2026):
  // id "." thỏa regex cũ và không chứa "..", nên projDir(".") chính là
  // thư mục projects/ gốc — xóa project đó sẽ xóa cả thư mục gốc.
  // R4-53 (08/11/2026, DEC-063 A): siết thêm — chặn id bắt đầu/kết thúc
  // bằng "." hoặc "-" ("-" lọt regex cũ, dùng làm tham số dòng lệnh sẽ bị
  // hiểu là cờ; ".hidden"/"foo." tạo thư mục ẩn/khó thấy; ".app-jobs"/
  // ".snapshots" trùng tên thư mục hệ thống của project) và id dài quá
  // 128 ký tự (giới hạn tên file là 255 byte; mkdirSync id dài hơn vỡ
  // bằng ENAMETOOLONG thô thay vì "ID không hợp lệ").
  if (
    !id ||
    id.length > 128 ||
    /^[.-]/.test(id) ||
    /[.-]$/.test(id) ||
    /^\.+$/.test(id) ||
    !/^[A-Za-z0-9._-]+$/.test(id) ||
    id.includes("..")
  ) {
    throw new Error(`ID project không hợp lệ: ${id}`);
  }
  return id;
}

export function projDir(id: string): string {
  return join(PROJECTS, safeId(id));
}

export function mimeForPath(full: string): string {
  const ext = (full.split(".").pop() ?? "").toLowerCase();
  return ext === "mp4"
    ? "video/mp4"
    : ext === "webm"
      ? "video/webm"
      : ext === "wav"
        ? "audio/wav"
        : ext === "mp3"
          ? "audio/mpeg"
          : ext === "png"
            ? "image/png"
            : ext === "webp"
              ? "image/webp"
              : "image/jpeg";
}

// R4-58 (08/11/2026, DEC-067 A): chặn fetch tới địa chỉ nội bộ (SSRF)
// — pickMedia fetch URL do người dùng nhập; trước đây không kiểm tra
// URL trỏ đâu. Chỉ cho http/https và hostname phải phân giải ra IP
// công khai; IP nội bộ/loopback/link-local thì từ chối. Không dùng
// allowlist domain — Production paste URL ảnh báo từ nhiều báo khác
// nhau, allowlist sẽ chặn nhầm nguồn hợp lệ. Fail-closed: hostname
// không phân giải được thì từ chối (fetch cũng sẽ fail).
export async function assertPublicUrl(raw: string): Promise<void> {
  let u: URL;
  try {
    u = new URL(raw);
  } catch {
    throw new Error(`URL không hợp lệ: ${raw}`);
  }
  if (u.protocol !== "http:" && u.protocol !== "https:") {
    throw new Error(`Chỉ tải được qua http/https, không tải được URL ${u.protocol}//...`);
  }
  const host = u.hostname.toLowerCase().replace(/^\[|\]$/g, "");
  if (host === "localhost" || host.endsWith(".localhost")) {
    throw new Error(`Từ chối tải từ URL nội bộ: ${raw}`);
  }
  // Hostname đã là IP literal thì kiểm trực tiếp, không cần DNS.
  if (isIP(host)) {
    if (isPrivateAddress(host)) {
      throw new Error(`Từ chối tải từ URL nội bộ (${host} là địa chỉ nội bộ)`);
    }
    return;
  }
  let addrs: Array<{ address: string }>;
  try {
    addrs = await lookup(host, { all: true });
  } catch {
    throw new Error(`Không phân giải được hostname ${host} — kiểm tra lại URL`);
  }
  for (const { address } of addrs) {
    if (isPrivateAddress(address)) {
      throw new Error(`Từ chối tải từ URL nội bộ (${host} phân giải ra ${address})`);
    }
  }
}

function isPrivateAddress(ip: string): boolean {
  const v = isIP(ip);
  if (v === 4) {
    const [a = -1, b = -1] = ip.split(".").map(Number); // sync-back từ artifact (rebuild 9): destructure có default để qua noUncheckedIndexedAccess — hành vi không đổi (IP hợp lệ luôn đủ 4 phần; -1 không khớp dải nào).
    if (a === 10) return true; // 10.0.0.0/8
    if (a === 172 && b >= 16 && b <= 31) return true; // 172.16.0.0/12
    if (a === 192 && b === 168) return true; // 192.168.0.0/16
    if (a === 127) return true; // 127.0.0.0/8 loopback
    if (a === 169 && b === 254) return true; // 169.254.0.0/16 link-local
    if (a === 0) return true; // 0.0.0.0/8
    return false;
  }
  if (v === 6) {
    const low = ip.toLowerCase();
    // IPv4-mapped IPv6 (::ffff:127.0.0.1 hoặc dạng hex ::ffff:7f00:1)
    // — kiểm phần IPv4 nhúng trong đó.
    if (low.startsWith("::ffff:")) {
      const rest = low.slice("::ffff:".length);
      if (rest.includes(".")) return isPrivateAddress(rest);
      const hex = rest.split(":").filter(Boolean).join("").padStart(8, "0");
      const bytes = [0, 2, 4, 6].map((i) => parseInt(hex.slice(i, i + 2), 16));
      return isPrivateAddress(bytes.join("."));
    }
    if (low === "::1" || low === "::") return true; // loopback / unspecified
    if (low.startsWith("fe8") || low.startsWith("fe9") || low.startsWith("fea") || low.startsWith("feb")) return true; // fe80::/10 link-local
    if (low.startsWith("fc") || low.startsWith("fd")) return true; // fc00::/7 unique-local
    return false;
  }
  return true; // không nhận dạng được thì chặn (fail-closed)
}

export function readJson<T>(path: string, fallback: T): T {
  try {
    if (!existsSync(path)) return fallback;
    return JSON.parse(readFileSync(path, "utf8")) as T;
  } catch {
    return fallback;
  }
}

export function writeJson(path: string, value: unknown): void {
  // R4-49 (08/11/2026, DEC-059 A): ghi atomic (file tạm cùng thư mục rồi
  // rename) — crash giữa chừng không để lại file đích bị cắt nửa chừng;
  // giống atomic_write_text bên Python (Giai đoạn 5). Người đọc
  // (assemble/preflight/render) không bao giờ thấy file đang ghi dở.
  const tmp = join(dirname(path), `.${basename(path)}.tmp-${process.pid}-${randomInt(1_000_000)}`);
  try {
    writeFileSync(tmp, JSON.stringify(value, null, 2), "utf8");
    renameSync(tmp, path);
  } catch (err) {
    try {
      rmSync(tmp, { force: true });
    } catch {
      // dọn file tạm thất bại — để lại file tạm, không che lỗi gốc
    }
    throw err;
  }
}

// R4-49 (08/11/2026, lệnh CEO, DEC-059 phương án A): khóa ghi plan CHUNG
// trên đĩa (file lock) để khóa cả tiến trình Python ngoài (gen_images,
// select_bgm) — withPlanWriteLock chỉ là hàng đợi promise trong một tiến
// trình Node, không bao được script Python. Giao thức dùng chung với
// bin/filename.py (Python), phải giữ đồng nhất cả hai bên:
//   - file khóa: <projectDir>/broll-plan.json.lock (cạnh file plan);
//   - tạo bằng cờ "wx" (O_EXCL — tạo mới nguyên tử, chỉ một tiến trình thắng);
//   - nội dung JSON {pid, token, holder, at} (token để lúc giải phóng chỉ
//     xóa đúng khóa của mình);
//   - khóa cũ hơn 30s thì bị phá (tiến trình giữ khóa chết giữa chừng);
//   - chờ tối đa 30s rồi lỗi rõ thay vì ghi không khóa (fail-closed).
// Ghi plan bình thường xong trong <1s nên 30s là biên an toàn lớn.
const PLAN_LOCK_STALE_MS = 30_000;
const PLAN_LOCK_TIMEOUT_MS = 30_000;
const PLAN_LOCK_POLL_MS = 50;

function planLockPath(projectId: string): string {
  return join(projDir(projectId), "broll-plan.json.lock");
}

async function acquirePlanFileLock(
  projectId: string,
  holder: string,
): Promise<{ lockPath: string; token: string }> {
  const lockPath = planLockPath(projectId);
  const token = randomUUID();
  const deadline = Date.now() + PLAN_LOCK_TIMEOUT_MS;
  for (;;) {
    try {
      writeFileSync(
        lockPath,
        JSON.stringify({ pid: process.pid, token, holder, at: Date.now() }),
        { flag: "wx", encoding: "utf8" },
      );
      return { lockPath, token };
    } catch (err) {
      if ((err as { code?: unknown })?.code !== "EEXIST") throw err;
      // Khóa đã có — cũ thì phá (chủ khóa chết giữa chừng), còn mới thì chờ.
      let mtime = 0;
      try {
        mtime = statSync(lockPath).mtimeMs;
      } catch {
        continue; // khóa biến mất giữa hai lần kiểm — thử lại ngay
      }
      if (Date.now() - mtime > PLAN_LOCK_STALE_MS) {
        try {
          rmSync(lockPath, { force: true });
        } catch {
          // đua với một waiter khác cũng đang phá khóa cũ — thử lại
        }
        continue;
      }
      if (Date.now() > deadline) {
        throw new Error(
          `Không lấy được khóa ghi plan của ${projectId} sau ${PLAN_LOCK_TIMEOUT_MS / 1000}s — có tiến trình khác đang ghi plan (khóa: ${lockPath})`,
        );
      }
      await new Promise((r) => setTimeout(r, PLAN_LOCK_POLL_MS));
    }
  }
}

function releasePlanFileLock(lockPath: string, token: string): void {
  try {
    const cur = JSON.parse(readFileSync(lockPath, "utf8")) as { token?: string };
    if (cur.token === token) rmSync(lockPath, { force: true });
  } catch {
    // Khóa đã bị phá (stale) hoặc không đọc được — không còn gì để giải phóng.
  }
}

export async function withPlanFileLock<T>(
  projectId: string,
  holder: string,
  fn: () => T,
): Promise<T> {
  const { lockPath, token } = await acquirePlanFileLock(projectId, holder);
  try {
    return await fn();
  } finally {
    releasePlanFileLock(lockPath, token);
  }
}

// Khóa ghi plan theo project (hàng đợi promise nối tiếp trong tiến
// trình): pickMedia / generateAiMedia đọc–sửa–ghi broll-plan.json, mà
// luồng tự động nay tạo media AI cho nhiều cảnh/part SONG SONG (4 luồng)
// cho cùng một project. Nếu hai lần gọi cùng đọc một bản plan rồi ghi
// đè cả file, lần ghi sau sẽ xóa mất cập nhật của lần ghi trước. Vì vậy
// chỉ đoạn "đọc lại plan → sửa → ghi" được tuần tự hóa theo project;
// phần việc chậm (tải file, gọi công cụ tạo AI) vẫn chạy song song
// ngoài khóa. Tên file media tất định theo (project, cảnh, part) nên
// các luồng song song không ghi trùng file của nhau.
const planWriteTails = new Map<string, Promise<void>>();
export async function withPlanWriteLock<T>(projectId: string, fn: () => T): Promise<T> {
  const prev = planWriteTails.get(projectId) ?? Promise.resolve();
  let release!: () => void;
  const gate = new Promise<void>((res) => {
    release = res;
  });
  planWriteTails.set(
    projectId,
    prev.then(() => gate),
  );
  await prev;
  try {
    // R4-49: kiêm luôn file lock trên đĩa — mọi chỗ ghi plan qua
    // withPlanWriteLock (pickMedia/generateAiMedia/clearSceneImage/
    // getProject-fill/buildGenImageJobs/savePlan) tự động khóa cả tiến
    // trình Python (gen_images/select_bgm).
    return await withPlanFileLock(projectId, "app", fn);
  } finally {
    release();
  }
}

export function run(
  cmd: string[],
  opts: { cwd?: string; timeoutMs?: number; env?: Record<string, string> } = {},
): Promise<{ code: number; out: string }> {
  return new Promise((resolve) => {
    const [bin, ...rest] = cmd as [string, ...string[]];
    const child = spawn(bin, rest, {
      cwd: opts.cwd ?? FACTORY,
      env: { ...process.env, ...(opts.env ?? {}) },
    });
    let out = "";
    const timer = setTimeout(() => child.kill("SIGKILL"), opts.timeoutMs ?? 120_000);
    child.stdout.on("data", (d: Buffer) => {
      out += d.toString();
      if (out.length > 2_000_000) out = out.slice(-2_000_000);
    });
    child.stderr.on("data", (d: Buffer) => {
      out += d.toString();
    });
    child.on("error", (e) => {
      clearTimeout(timer);
      resolve({ code: -1, out: `${out}\n${String(e)}` });
    });
    child.on("close", (code) => {
      clearTimeout(timer);
      resolve({ code: code ?? -1, out });
    });
  });
}

export function runCaptureJson(cmd: string[], timeoutMs: number): Promise<unknown> {
  return run(cmd, { timeoutMs }).then(({ out }) => {
    const start = out.indexOf("{");
    if (start < 0) throw new Error(`Không đọc được kết quả lệnh: ${out.slice(-400)}`);
    try {
      return JSON.parse(out.slice(start)) as unknown;
    } catch {
      // R4-50 (08/11/2026, DEC-060 A): bọc JSON.parse — trước đây output
      // có "{" nhưng JSON hỏng thì ném SyntaxError thô, caller nào không
      // bọc try sẽ crash; nay báo rõ lệnh nào + đoạn output cuối.
      throw new Error(
        `Lệnh ${cmd.slice(0, 2).join(" ")} trả về JSON không đọc được: ${out.slice(-400)}`,
      );
    }
  });
}

export function ffprobe(path: string): { duration: number | null; width: number | null; height: number | null } {
  try {
    const raw = execFileSync(
      "ffprobe",
      ["-v", "error", "-show_entries", "format=duration:stream=width,height", "-of", "json", path],
      { timeout: 30_000 },
    ).toString();
    const parsed = JSON.parse(raw) as {
      format?: { duration?: string };
      streams?: Array<{ width?: number; height?: number }>;
    };
    const video = (parsed.streams ?? []).find((s) => s.width);
    return {
      duration: parsed.format?.duration ? Number(parsed.format.duration) : null,
      width: video?.width ?? null,
      height: video?.height ?? null,
    };
  } catch {
    return { duration: null, width: null, height: null };
  }
}
