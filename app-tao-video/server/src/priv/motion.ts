// Chuỗi motion Ken Burns của render ffmpeg, nhân bản chính xác cho
// Preview HTML (CPython random.Random("motion-<pid>") port sang TS).
// Chỉ privileged.ts import file này.
import { createHash } from "node:crypto";

// ---- Motion sequence of the ffmpeg render, replicated for the preview ----
// bin/render_draft.py picks each part's Ken Burns motion from
// random.Random(f"motion-{pid}") — a SEQUENTIAL draw in render part order
// (tts scenes in order, parts of each scene in tts order) with a
// no-immediate-repeat rule — while the preview engine used to pick by
// hash(partId). The two sequences disagree (blurtest001 part 4: render
// pan_down vs preview zoom_in), so the preview showed a different image
// animation than the rendered video even though both were "a valid
// motion". getPreviewData therefore computes the render's exact sequence
// here and ships it as part.motion; the engine honors it when present.
// CPython seeding for a str seed (version 2): int.from_bytes(utf8 bytes +
// sha512(utf8 bytes)) fed to MT19937 init_by_array; choice() draws via
// _randbelow (getrandbits with rejection). This port is verified
// byte-for-byte against CPython's random for multiple project ids and
// sequence lengths (up to 60 draws) — do not "simplify" it.
const RENDER_MOTIONS = [
  "zoom_in",
  "zoom_out",
  "pan_left",
  "pan_right",
  "pan_up",
  "pan_down",
] as const;

function pySeedWords(seed: string): number[] {
  const bytes = new TextEncoder().encode(seed);
  const digest = createHash("sha512").update(bytes).digest();
  let v = 0n;
  for (const b of bytes) v = (v << 8n) | BigInt(b);
  for (const b of digest) v = (v << 8n) | BigInt(b);
  if (v === 0n) return [0];
  const words: number[] = [];
  while (v > 0n) {
    words.push(Number(v & 0xffffffffn));
    v >>= 32n;
  }
  return words;
}

class PyRandom {
  private mt: number[] = new Array<number>(624).fill(0);
  private index = 624;

  constructor(seed: string) {
    const mt = this.mt;
    const at = (i: number): number => mt[i] ?? 0;
    mt[0] = 19650218;
    for (let i = 1; i < 624; i++) {
      const prev = at(i - 1);
      mt[i] = (Math.imul(prev ^ (prev >>> 30), 1812433253) + i) >>> 0;
    }
    const key = pySeedWords(seed);
    let i = 1;
    let j = 0;
    for (let k = Math.max(624, key.length); k > 0; k--) {
      const prev = at(i - 1);
      mt[i] =
        ((at(i) ^ Math.imul(prev ^ (prev >>> 30), 1664525)) +
          (key[j] ?? 0) +
          j) >>>
        0;
      i++;
      j++;
      if (i >= 624) {
        mt[0] = at(623);
        i = 1;
      }
      if (j >= key.length) j = 0;
    }
    for (let k = 623; k > 0; k--) {
      const prev = at(i - 1);
      mt[i] = ((at(i) ^ Math.imul(prev ^ (prev >>> 30), 1566083941)) - i) >>> 0;
      i++;
      if (i >= 624) {
        mt[0] = at(623);
        i = 1;
      }
    }
    mt[0] = 0x80000000;
  }

  private genrand(): number {
    if (this.index >= 624) {
      const mt = this.mt;
      const at = (i: number): number => mt[i] ?? 0;
      for (let i = 0; i < 624; i++) {
        const y = (at(i) & 0x80000000) | (at((i + 1) % 624) & 0x7fffffff);
        const xA = (y >>> 1) ^ (y & 1 ? 0x9908b0df : 0);
        mt[i] = at((i + 397) % 624) ^ xA;
      }
      this.index = 0;
    }
    let y = this.mt[this.index] ?? 0;
    this.index++;
    y ^= y >>> 11;
    y ^= (y << 7) & 0x9d2c5680;
    y ^= (y << 15) & 0xefc60000;
    y ^= y >>> 18;
    return y >>> 0;
  }

  private randbelow(n: number): number {
    const k = n.toString(2).length;
    let r = this.genrand() >>> (32 - k);
    while (r >= n) r = this.genrand() >>> (32 - k);
    return r;
  }

  choiceIndex(len: number): number {
    return this.randbelow(len);
  }
}

// The exact motion kind render_draft.py will use for each part, keyed by
// part id. Iteration order mirrors render_draft.py's part_list: scenes in
// tts order, and inside each scene its parts in tts.parts order; every
// part consumes a draw (video b-roll parts too — render draws before it
// branches), and a draw equal to the previous part's motion is redrawn
// from the remaining five.
export function renderMotionByPartId(
  projectId: string,
  scenes: Array<{ order?: number }> | undefined,
  parts: Array<{ id: string; sceneOrder?: number }>,
): Map<string, string> {
  const ordered: Array<{ id: string; sceneOrder?: number }> = [];
  if (scenes && scenes.length > 0) {
    for (const sc of scenes) {
      for (const p of parts) {
        if (p.sceneOrder === sc.order) ordered.push(p);
      }
    }
    // Parts whose scene is missing from tts.scenes are not rendered by
    // render_draft.py either; they simply get no motion (hash fallback).
  } else {
    ordered.push(...parts);
  }
  const rng = new PyRandom(`motion-${projectId}`);
  const out = new Map<string, string>();
  let prev: string | null = null;
  ordered.forEach((p, ci) => {
    let motion =
      RENDER_MOTIONS[rng.choiceIndex(RENDER_MOTIONS.length)] ?? "zoom_in";
    if (ci > 0 && motion === prev) {
      const rest = RENDER_MOTIONS.filter((m) => m !== prev);
      motion = rest[rng.choiceIndex(rest.length)] ?? motion;
    }
    prev = motion;
    out.set(p.id, motion);
  });
  return out;
}
