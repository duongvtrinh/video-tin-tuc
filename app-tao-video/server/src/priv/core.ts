// Core dùng chung của tầng privileged: đường dẫn nhà máy VieNeu Asset
// Factory, hợp đồng tên file, tiện ích đọc/ghi JSON, khóa ghi plan theo
// project và các wrapper chạy lệnh ngoài (spawn/ffprobe). Chỉ
// privileged.ts (và các module priv/ khác) import file này — actions.ts
// không được chạm vào.
import { execFileSync, spawn } from "node:child_process";
import { createHash, randomInt } from "node:crypto";
import {
  existsSync,
  readFileSync,
  readdirSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

export const HOME = homedir();
export const FACTORY = existsSync(join(HOME, "workspace/asset-factory"))
  ? join(HOME, "workspace/asset-factory")
  : join(HOME, "workspace/vieneu-asset-factory");
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
  if (envDir) return join(envDir, ".venv/bin/python");
  const repoPath = join(HOME, "workspace/vieneu-tts/.venv/bin/python");
  if (existsSync(repoPath)) return repoPath;
  const legacyPath = join(HOME, "workspace/vieneu-tts-api/.venv/bin/python");
  if (existsSync(legacyPath)) return legacyPath;
  return repoPath;
}
export const TTS_PY = resolveTtsPy();
export const SEARCH_MEDIA = join(HOME, "workspace/company-os/media-search/search_media.py");
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
  if (!/^[A-Za-z0-9._-]+$/.test(id) || id.includes("..")) {
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

export function readJson<T>(path: string, fallback: T): T {
  try {
    if (!existsSync(path)) return fallback;
    return JSON.parse(readFileSync(path, "utf8")) as T;
  } catch {
    return fallback;
  }
}

export function writeJson(path: string, value: unknown): void {
  writeFileSync(path, JSON.stringify(value, null, 2), "utf8");
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
    return fn();
  } finally {
    release();
  }
}

// First file (sorted) in dir whose name starts with prefix and ends with
// suffix — the TS equivalent of build_render_page.py's find_one(glob).
export function findFirstGlob(dir: string, prefix: string, suffix: string): string | null {
  try {
    const hits = readdirSync(dir)
      .filter((f) => f.startsWith(prefix) && f.endsWith(suffix))
      .sort();
    const first = hits[0];
    return first ? join(dir, first) : null;
  } catch {
    return null;
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
    return JSON.parse(out.slice(start)) as unknown;
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
