// Handler Preview HTML: dựng dữ liệu preview đúng như render thật (ảnh/video từng part, motion, karaoke, BGM và sự kiện SFX đã cắt theo luật render).
// Chỉ privileged.ts import file này; kiểu tham số/kết quả lấy thẳng từ
// contract tương ứng (ArgsOf/ResOf) để handler không lệch contract.
import type { Factory } from "@space/privileged";
import type { z } from "@hatch/space-sdk";

type ArgsOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["request"]>;
type ResOf<K extends keyof typeof Factory> = z.infer<(typeof Factory)[K]["response"]>;

import { existsSync, readFileSync, statSync } from "node:fs";
import { basename, join } from "node:path";
import { FACTORY, ffprobe, findFirstGlob, projDir, readJson, run } from "./core";
import { renderMotionByPartId } from "./motion";

export async function getPreviewData({ projectId }: ArgsOf<"getPreviewData">): Promise<ResOf<"getPreviewData">> {
    const dir = projDir(projectId);
    if (!existsSync(dir)) throw new Error(`Không thấy project ${projectId}`);
    const build = join(dir, "build");
    const tts = readJson<{
      scenes?: Array<{ order?: number }>;
      parts?: Array<{
        id: string;
        sceneOrder?: number;
        partIdx?: number;
        audio_file?: string;
        startSec: number;
        endSec: number;
      }>;
    } | null>(join(dir, "tts.json"), null);
    if (!tts?.parts || tts.parts.length === 0) {
      throw new Error(
        "Project chưa có tts.json — hãy chạy TTS (và Chuẩn hóa chunk + Karaoke) trước khi xem Preview HTML, vì mốc thời gian của preview lấy từ tts.json.",
      );
    }
    const plan = readJson<{
      bgm?: { id?: string; file?: string };
      scenes?: Array<{
        parts?: Array<{
          id: string;
          broll?: {
            templateId?: string;
            inputs?: Record<string, unknown>;
            sfx?: { id: string; offsetSec?: number; volume?: number };
          };
        }>;
      }>;
    } | null>(join(dir, "broll-plan.json"), null);
    type KaraokePartFull = {
      partId?: string;
      subsHidden?: boolean;
      lines?: Array<{
        start: number;
        end: number;
        words?: Array<{ text: string; start: number; end: number }>;
      }>;
    };
    const karaokeRaw = readJson<KaraokePartFull[]>(
      join(build, "subtitles/karaoke.json"),
      [],
    );
    const inputRaw = readJson<Record<string, unknown>>(join(dir, "input.json"), {});
    const wide = String(inputRaw["aspectRatio"] ?? "9:16") !== "9:16";
    const W = wide ? 1280 : 720;
    const H = wide ? 720 : 1280;

    const engineSource = readFileSync(join(FACTORY, "lib/render-engine.js"), "utf8");

    const brollMap = new Map<
      string,
      {
        templateId?: string;
        inputs?: Record<string, unknown>;
        sfx?: { id: string; offsetSec?: number; volume?: number };
      }
    >();
    for (const sc of plan?.scenes ?? []) {
      for (const pt of sc.parts ?? []) brollMap.set(pt.id, pt.broll ?? {});
    }
    const karaMap = new Map<string, KaraokePartFull>();
    for (const k of Array.isArray(karaokeRaw) ? karaokeRaw : []) {
      if (k.partId) karaMap.set(k.partId, k);
    }
    const tplCache = new Map<string, [string, string]>();
    const getTpl = (tid: string): [string, string] => {
      const hit = tplCache.get(tid);
      if (hit) return hit;
      const td = join(FACTORY, "templates", tid);
      const readOrEmpty = (f: string) => {
        try {
          return readFileSync(join(td, f), "utf8");
        } catch {
          return "";
        }
      };
      const pair: [string, string] = [readOrEmpty("template.html"), readOrEmpty("style.css")];
      tplCache.set(tid, pair);
      return pair;
    };

    // Real image of a part: b-roll jpg if present, else the scene image —
    // identical lookup to build_render_page.py part_image().
    const partImagePath = (sceneOrder?: number, partIdx?: number): string | null => {
      if (sceneOrder !== undefined && partIdx !== undefined) {
        const b = findFirstGlob(
          join(build, "media/broll"),
          `broll_seg_${sceneOrder}_part_${partIdx}_`,
          ".jpg",
        );
        if (b) return b;
      }
      if (sceneOrder !== undefined) {
        return findFirstGlob(join(build, "media/images"), `seg_${sceneOrder}_`, ".jpg");
      }
      return null;
    };

    // B-roll video of a part, mirroring render_draft.py base_video():
    // the conventional mp4 in build/media/broll, accepted only when
    // ffprobe reports real video dimensions (the repo helper's ffprobe
    // returns width/height only for a stream that has them) — otherwise
    // the part falls back to the image path above, exactly like the
    // render refuses to let a broken video file break the clip.
    const videoProbeCache = new Map<
      string,
      { rel: string; w: number; h: number } | null
    >();
    const partVideo = (
      sceneOrder?: number,
      partIdx?: number,
    ): { rel: string; w: number; h: number } | null => {
      if (sceneOrder === undefined || partIdx === undefined) return null;
      const v = findFirstGlob(
        join(build, "media/broll"),
        `broll_seg_${sceneOrder}_part_${partIdx}_`,
        ".mp4",
      );
      if (!v) return null;
      const hit = videoProbeCache.get(v);
      if (hit !== undefined) return hit;
      const probe = ffprobe(v);
      const ok =
        probe.width !== null && probe.height !== null
          ? {
              rel: `build/media/broll/${basename(v)}`,
              w: probe.width,
              h: probe.height,
            }
          : null;
      videoProbeCache.set(v, ok);
      return ok;
    };

    const imgCache = new Map<string, string>();
    const encodeImage = async (imgPath: string): Promise<string> => {
      const name = basename(imgPath);
      const cached = imgCache.get(name);
      if (cached !== undefined) return cached;
      let dataUrl = "";
      try {
        const thumb = join(build, `_thumb_${name}`);
        const stale =
          !existsSync(thumb) || statSync(imgPath).mtimeMs > statSync(thumb).mtimeMs;
        if (stale) {
          const { code } = await run(
            ["ffmpeg", "-v", "error", "-y", "-i", imgPath, "-vf", `scale=${W}:-1`, thumb],
            { timeoutMs: 30_000 },
          );
          if (code !== 0) throw new Error(`ffmpeg scale failed (${code})`);
        }
        dataUrl = `data:image/jpeg;base64,${readFileSync(thumb).toString("base64")}`;
      } catch {
        dataUrl = "";
      }
      imgCache.set(name, dataUrl);
      return dataUrl;
    };

    const motionByPart = renderMotionByPartId(projectId, tts.scenes, tts.parts);
    const parts = [];
    for (const p of tts.parts) {
      const br = brollMap.get(p.id) ?? {};
      const tid =
        br.templateId && br.templateId !== "none" ? br.templateId : null;
      let tplHtml = "";
      let tplCss = "";
      const tplInputs: Record<string, string> = {};
      if (tid) {
        [tplHtml, tplCss] = getTpl(tid);
        for (const [k, v] of Object.entries(br.inputs ?? {})) {
          tplInputs[k] = v === null || v === undefined ? "" : String(v);
        }
      }
      const imgPath = partImagePath(p.sceneOrder, p.partIdx);
      const image = imgPath ? await encodeImage(imgPath) : "";
      const vid = partVideo(p.sceneOrder, p.partIdx);
      const kp = karaMap.get(p.id);
      parts.push({
        id: p.id,
        start: p.startSec,
        end: p.endSec,
        image,
        videoFile: vid?.rel ?? null,
        videoW: vid?.w ?? null,
        videoH: vid?.h ?? null,
        motion: motionByPart.get(p.id) ?? null,
        templateId: tid,
        tplHtml,
        tplCss,
        tplInputs,
        audioFile: p.audio_file ?? "",
        karaoke: {
          lines: (kp?.lines ?? []).map((l) => ({
            start: l.start,
            end: l.end,
            words: (l.words ?? []).map((w) => ({
              text: String(w.text),
              start: w.start,
              end: w.end,
            })),
          })),
          subsHidden: kp?.subsHidden === true,
        },
      });
    }
    const last = parts[parts.length - 1];
    // SFX events with the EXACT timing/volume/duration rules of
    // render_draft.py (the final render), so the preview sounds like the
    // render instead of playing each SFX file end-to-end:
    // - fire at part.startSec + offsetSec, plan volume, heavy SFX
    //   (thud/slam/boom in the id) capped at 0.4 in the mix layer;
    // - TRIM at the part's end (CEO rule 31/10/2026): duration is capped
    //   at part.endSec - start, and an SFX that would start at/after the
    //   part's end is dropped entirely — it never bleeds into the next
    //   part, even though the raw file (typing_fast 6.37s, riser 3.0s)
    //   is longer than many parts;
    // - typing SFX (id contains "typing", e.g. the typewriter-reveal
    //   template's typing_fast): the typing time follows the DISPLAYED
    //   template text (broll inputs.text), NOT the voice part — the
    //   voice text is far longer than the short line the template shows.
    //   duration = min(part remainder, text length × 0.1s) at 10
    //   chars/sec including spaces, and the file loops when shorter
    //   than that window (render: aloop + atrim; player: loop + stop).
    const sfxEvents: Array<{
      id: string;
      file: string;
      partId: string;
      atSec: number;
      volume: number;
      durationSec: number;
      endSec: number;
      loop: boolean;
    }> = [];
    for (const p of tts.parts) {
      const br = brollMap.get(p.id);
      const sfx = br?.sfx;
      if (!sfx?.id) continue;
      let vol = typeof sfx.volume === "number" ? sfx.volume : 0.6;
      if (/(thud|slam|boom)/.test(sfx.id)) vol = Math.min(vol, 0.4);
      const atSec =
        p.startSec + (typeof sfx.offsetSec === "number" ? sfx.offsetSec : 0);
      let durationSec = p.endSec - atSec;
      if (durationSec <= 0) continue; // starts after the part ends — render drops it too
      const isTyping = sfx.id.includes("typing");
      if (isTyping) {
        const txtRaw = br?.inputs?.["text"];
        const txt =
          txtRaw === null || txtRaw === undefined ? "" : String(txtRaw);
        if (txt) durationSec = Math.min(durationSec, txt.length * 0.1);
      }
      if (durationSec <= 0) continue;
      sfxEvents.push({
        id: sfx.id,
        file: `${sfx.id}.mp3`,
        partId: p.id,
        atSec,
        volume: vol,
        durationSec,
        endSec: atSec + durationSec,
        loop: isTyping,
      });
    }
    sfxEvents.sort((a, b) => a.atSec - b.atSec);
    // BGM exactly as render_draft.py mixes it: the plan's chosen track,
    // looped over the whole video at volume 0.12 (ducking + 2s fade-out
    // are applied by the player, mirroring the sidechain/afade filters).
    const bgm =
      plan?.bgm?.file
        ? { id: String(plan.bgm.id ?? ""), file: String(plan.bgm.file), volume: 0.12 }
        : null;
    return {
      engineSource,
      width: W,
      height: H,
      durationSec: last ? last.end : 0,
      parts,
      bgm,
      sfxEvents,
    };
  }
