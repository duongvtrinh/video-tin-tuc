// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { btnCls, btnPrimary, fetchMediaBlob, fmtMinSecCore } from "../lib";
import { InfoTip } from "./InfoTip";
import { JobRunner } from "./shared";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import type { ApiResponse } from "../api";
import type { Part, ProjectDetail } from "../lib";

type PreviewData = ApiResponse<typeof api, "getPreviewData">;
type PreviewPart = PreviewData["parts"][number];

type VieNeuApi = {
  mount: (el: HTMLElement, data: unknown) => void;
  seekTo: (t: number) => void;
  // Engine motion bằng CSS keyframes: setPlaying(true) để animation ảnh
  // chạy thật trên compositor khi phát, setPlaying(false) quay lại chế độ
  // lái bằng delay âm + paused (đứng đúng khung hình). Optional vì engine
  // được nạp verbatim từ repo — bản engine cũ không có hàm này thì player
  // vẫn chạy như trước.
  setPlaying?: (playing: boolean) => void;
  getDuration: () => number;
  isReady: () => boolean;
};

function fmtClock(sec: number): string {
  const { m, sText } = fmtMinSecCore(Math.max(0, sec));
  return `${m}:${sText}`;
}

function findPreviewPartIdx(parts: PreviewPart[], t: number): number {
  for (let i = 0; i < parts.length; i++) {
    const p = parts[i];
    if (p && t >= p.start && t < p.end) return i;
  }
  return Math.max(0, parts.length - 1);
}

function HtmlPreviewPlayer({ detail, data }: { detail: ProjectDetail; data: PreviewData }) {
  const queryClient = useQueryClient();
  const parts = data.parts;
  const duration = data.durationSec;
  const idRef = useRef(detail.id);
  idRef.current = detail.id;
  const partsRef = useRef<PreviewPart[]>(parts);
  partsRef.current = parts;
  const durationRef = useRef(duration);
  durationRef.current = duration;

  const wrapRef = useRef<HTMLDivElement | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const engineRef = useRef<VieNeuApi | null>(null);
  const audioEls = useRef(new Map<string, HTMLAudioElement>());
  const stRef = useRef({ playing: false, time: 0, raf: 0, lastTs: 0, lastUi: 0, audioPart: -2 });
  const sigRef = useRef("");
  const [scale, setScale] = useState(0.45);
  const [engineOk, setEngineOk] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [time, setTime] = useState(0);
  const [dragVal, setDragVal] = useState<number | null>(null);

  // --- Audio layers beyond the voice: BGM + SFX, mixed with the exact
  // parameters of bin/render_draft.py (BGM loop volume 0.12, sidechain
  // ducking under the voice, 2s fade-out at the end; SFX at
  // part.startSec + offsetSec with the plan volume, heavy SFX already
  // capped at 0.4 server-side, and every SFX trimmed at its part's end —
  // typing SFX additionally limited server-side to the displayed
  // template text at 0.1s/char, never the whole voice part). Each layer
  // has its own mute toggle, and seeking/pausing stops and re-schedules
  // the layers at the new time so a stale SFX can never fire after a
  // seek.
  const dataRef = useRef(data);
  dataRef.current = data;
  const [voiceOn, setVoiceOn] = useState(true);
  const [bgmOn, setBgmOn] = useState(true);
  const [sfxOn, setSfxOn] = useState(true);
  const [layerMsg, setLayerMsg] = useState<string | null>(null);
  const layerOnRef = useRef({ voice: true, bgm: true, sfx: true });
  const actxRef = useRef<AudioContext | null>(null);
  const bgmBufRef = useRef<AudioBuffer | null>(null);
  const sfxBufsRef = useRef(new Map<string, AudioBuffer>());
  const bgmNodeRef = useRef<{ src: AudioBufferSourceNode; gain: GainNode } | null>(null);
  const sfxNodesRef = useRef<Array<{ src: AudioBufferSourceNode; atSec: number }>>([]);
  const layersSigRef = useRef("");

  const stopAudio = () => {
    for (const el of audioEls.current.values()) el.pause();
  };

  function ensureCtx(): AudioContext | null {
    try {
      if (!actxRef.current) {
        const AC =
          window.AudioContext ??
          (window as unknown as { webkitAudioContext?: typeof AudioContext })
            .webkitAudioContext;
        if (!AC) return null;
        actxRef.current = new AC();
      }
      return actxRef.current;
    } catch {
      return null;
    }
  }

  function stopBgm() {
    const n = bgmNodeRef.current;
    bgmNodeRef.current = null;
    if (n) {
      try { n.src.stop(); } catch { /* already stopped */ }
      try { n.src.disconnect(); n.gain.disconnect(); } catch { /* noop */ }
    }
  }

  function stopSfx() {
    for (const n of sfxNodesRef.current) {
      try { n.src.stop(); } catch { /* already stopped */ }
      try { n.src.disconnect(); } catch { /* noop */ }
    }
    sfxNodesRef.current = [];
  }

  function stopLayers() {
    stopBgm();
    stopSfx();
  }

  function bgmGainAt(t: number): number {
    // Render chain: volume=0.12, sidechaincompress ducks the music under
    // the voice mix, afade out over the last 2 seconds. The preview
    // mirrors that gain shape: ducked to ~35% while a voice part covers
    // the playhead, linear fade-out in the final 2s.
    const dur = durationRef.current;
    let g = dataRef.current.bgm?.volume ?? 0.12;
    if (dur > 2 && t > dur - 2) g *= Math.max(0, (dur - t) / 2);
    const voiceActive = partsRef.current.some((p) => t >= p.start && t < p.end);
    if (voiceActive) g *= 0.35;
    return g;
  }

  function startBgm(t: number) {
    stopBgm();
    const ctx = ensureCtx();
    const buf = bgmBufRef.current;
    if (!ctx || !buf || !layerOnRef.current.bgm) return;
    void ctx.resume().catch(() => {});
    const src = ctx.createBufferSource();
    src.buffer = buf;
    src.loop = true;
    const gain = ctx.createGain();
    gain.gain.value = bgmGainAt(t);
    src.connect(gain);
    gain.connect(ctx.destination);
    try {
      src.start(0, t % buf.duration);
    } catch {
      return;
    }
    bgmNodeRef.current = { src, gain };
  }

  function scheduleSfx(t: number) {
    stopSfx();
    const ctx = ensureCtx();
    if (!ctx || !layerOnRef.current.sfx) return;
    void ctx.resume().catch(() => {});
    const now = ctx.currentTime;
    for (const ev of dataRef.current.sfxEvents) {
      const buf = sfxBufsRef.current.get(ev.id);
      if (!buf) continue;
      // Cùng luật cắt của render_draft.py (atrim + fade-out 0,05s):
      // SFX chỉ nghe được trong cửa sổ [atSec, endSec) mà server đã tính
      // — dừng chậm nhất ở cuối part, riêng typing dừng theo độ dài text
      // HIỂN THỊ (0,1s/ký tự), không phủ hết voicepart. File ngắn hơn
      // cửa sổ thì tự hết (trừ typing: lặp cho đủ cửa sổ như aloop của
      // render); file dài hơn thì bị stop đúng endSec.
      const audibleEnd = ev.loop
        ? ev.endSec
        : Math.min(ev.endSec, ev.atSec + buf.duration);
      if (audibleEnd <= t || ev.atSec >= durationRef.current) continue;
      const when = now + Math.max(0, ev.atSec - t);
      const offset = Math.max(0, t - ev.atSec);
      const remaining = audibleEnd - Math.max(t, ev.atSec);
      if (remaining <= 0) continue;
      const src = ctx.createBufferSource();
      src.buffer = buf;
      src.loop = ev.loop;
      const gain = ctx.createGain();
      // Fade-out 0,05s ở cuối cửa sổ, khớp afade của render (tránh click
      // và để tiếng gõ/rise tắt hẳn trước mốc chuyển part).
      const fade = Math.min(0.05, remaining);
      gain.gain.setValueAtTime(ev.volume, when);
      gain.gain.setValueAtTime(ev.volume, when + Math.max(0, remaining - fade));
      gain.gain.linearRampToValueAtTime(0, when + remaining);
      src.connect(gain);
      gain.connect(ctx.destination);
      try {
        src.start(when, ev.loop ? offset % buf.duration : offset);
        src.stop(when + remaining + 0.02);
      } catch {
        continue;
      }
      sfxNodesRef.current.push({ src, atSec: ev.atSec });
    }
  }

  function startLayers(t: number) {
    startBgm(t);
    scheduleSfx(t);
  }

  // Load + decode the BGM track and the SFX files through the chunked
  // media path (getMediaChunk); the small per-part voice WAVs keep their
  // existing inline path.
  useEffect(() => {
    const sig = `${detail.id}|bgm:${data.bgm?.file ?? ""}|sfx:${[...new Set(data.sfxEvents.map((e) => e.id))].join(",")}`;
    if (layersSigRef.current === sig) return;
    layersSigRef.current = sig;
    stopLayers();
    bgmBufRef.current = null;
    sfxBufsRef.current.clear();
    setLayerMsg(null);
    if (!data.bgm && data.sfxEvents.length === 0) return;
    const ctx = ensureCtx();
    if (!ctx) {
      setLayerMsg("Trình duyệt này không hỗ trợ Web Audio — Preview chỉ phát được giọng đọc.");
      return;
    }
    let cancelled = false;
    void (async () => {
      if (data.bgm) {
        try {
          const { blob } = await fetchMediaBlob(detail.id, `__factory__/bgm/${data.bgm.file}`);
          const buf = await ctx.decodeAudioData(await blob.arrayBuffer());
          if (!cancelled) bgmBufRef.current = buf;
        } catch {
          if (!cancelled) {
            setLayerMsg("Không tải/giải mã được file nhạc nền cho Preview — bản render vẫn dùng file gốc trong repo.");
          }
        }
      }
      for (const id of new Set(data.sfxEvents.map((e) => e.id))) {
        try {
          const { blob } = await fetchMediaBlob(detail.id, `__factory__/sfx/${id}.mp3`);
          const buf = await ctx.decodeAudioData(await blob.arrayBuffer());
          if (!cancelled) sfxBufsRef.current.set(id, buf);
        } catch {
          // R4-62 (08/11/2026, DEC-070 A): file SFX thiếu khi tải — chỉ
          // là phòng thủ, vì server đã lọc file thiếu ra khỏi sfxEvents
          // và báo qua data.missingSfx. KHÔNG được hiểu là "render cuối
          // cũng bỏ qua": render chặn đúng ở A26 (preflight BÁO LỖI +
          // render dừng RENDER-ERROR), chỉ preview là bỏ qua tiếng này.
        }
      }
    })();
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, detail.id]);

  async function ensureAudioEl(idx: number): Promise<HTMLAudioElement | null> {
    const part = partsRef.current[idx];
    if (!part || !part.audioFile) return null;
    const cached = audioEls.current.get(part.id);
    if (cached) return cached;
    try {
      const rel = `build/audio/voice/${part.audioFile}`;
      const res = await queryClient.fetchQuery({
        queryKey: ["media", idRef.current, rel],
        queryFn: () => api.getMediaDataUrl({ projectId: idRef.current, relPath: rel }),
        staleTime: 300_000,
      });
      const el = new Audio();
      el.preload = "auto";
      el.src = res.dataUrl;
      audioEls.current.set(part.id, el);
      return el;
    } catch {
      return null;
    }
  }

  async function syncAudio(t: number, wantPlay: boolean) {
    const list = partsRef.current;
    if (list.length === 0) return;
    const idx = findPreviewPartIdx(list, t);
    const part = list[idx];
    if (!part) return;
    const st = stRef.current;
    if (st.audioPart !== idx) {
      st.audioPart = idx;
      for (const [pid, el] of audioEls.current) {
        if (pid !== part.id) el.pause();
      }
      void ensureAudioEl(idx + 1);
    }
    const el = await ensureAudioEl(idx);
    if (!el || stRef.current.audioPart !== idx) return;
    const target = Math.min(
      Math.max(t - part.start, 0),
      Math.max(part.end - part.start - 0.05, 0),
    );
    if (Math.abs(el.currentTime - target) > 0.3) {
      try {
        el.currentTime = target;
      } catch {
        /* audio chưa sẵn sàng — bỏ qua, khung hình vẫn chạy */
      }
    }
    if (wantPlay && layerOnRef.current.voice) {
      try {
        await el.play();
      } catch {
        /* trình duyệt chặn phát tự động — người dùng bấm Phát lại */
      }
    } else {
      el.pause();
    }
  }
  const syncAudioRef = useRef(syncAudio);
  syncAudioRef.current = syncAudio;

  function tick(ts: number) {
    const st = stRef.current;
    if (!st.playing) return;
    const dt = st.lastTs ? Math.min((ts - st.lastTs) / 1000, 0.25) : 0;
    st.lastTs = ts;
    let t = st.time + dt;
    const dur = durationRef.current;
    if (t >= dur) {
      t = dur;
      st.time = t;
      engineRef.current?.seekTo(t);
      setTime(t);
      pausePlayback();
      return;
    }
    st.time = t;
    // Khi đang phát, engine ở runningMode (setPlaying(true)): seekTo mỗi
    // khung hình chỉ còn lo phụ đề/template/crossfade — nó KHÔNG chạm vào
    // CSS animation của ảnh khi còn cùng part, motion chạy trên compositor.
    engineRef.current?.seekTo(t);
    const bn = bgmNodeRef.current;
    if (bn && actxRef.current) {
      // Ducking + fade-out follow the playhead continuously, with the
      // render sidechain's time constants (attack 200ms / release 600ms).
      const voiceActive = partsRef.current.some((p) => t >= p.start && t < p.end);
      bn.gain.gain.setTargetAtTime(
        bgmGainAt(t),
        actxRef.current.currentTime,
        voiceActive ? 0.2 : 0.6,
      );
    }
    const idx = findPreviewPartIdx(partsRef.current, t);
    if (idx !== st.audioPart) void syncAudioRef.current(t, true);
    if (ts - st.lastUi > 100) {
      st.lastUi = ts;
      setTime(t);
    }
    st.raf = requestAnimationFrame(tickRef.current);
  }
  const tickRef = useRef(tick);
  tickRef.current = tick;

  function pausePlayback() {
    const st = stRef.current;
    st.playing = false;
    setPlaying(false);
    cancelAnimationFrame(st.raf);
    // Đồng bộ engine về đúng mốc dừng rồi mới tắt runningMode:
    // setPlaying(false) lái animation bằng delay âm + paused nên ảnh
    // đứng yên đúng khung hình tại st.time.
    engineRef.current?.seekTo(st.time);
    engineRef.current?.setPlaying?.(false);
    stopAudio();
    stopLayers();
    setTime(st.time);
  }

  function startPlayback() {
    const st = stRef.current;
    if (st.playing || !engineRef.current) return;
    if (st.time >= durationRef.current - 0.05) {
      st.time = 0;
      st.audioPart = -2;
    }
    st.playing = true;
    st.lastTs = 0;
    st.lastUi = 0;
    setPlaying(true);
    // seekTo chốt đúng khung hình bắt đầu, rồi setPlaying(true) bật
    // runningMode: từ đây CSS animation của ảnh chạy thật trên
    // compositor, JS không gán transform mỗi khung hình nữa.
    engineRef.current.seekTo(st.time);
    engineRef.current.setPlaying?.(true);
    void syncAudioRef.current(st.time, true);
    startLayers(st.time);
    st.raf = requestAnimationFrame(tickRef.current);
  }

  function seekToTime(t: number) {
    const st = stRef.current;
    const clamped = Math.max(0, Math.min(t, durationRef.current));
    st.time = clamped;
    st.audioPart = -2;
    // Tua/nhảy part: chỉ seekTo như cũ — engine tự nhận biết cú nhảy
    // (đổi part hoặc bước thời gian lớn) và đồng bộ lại CSS animation về
    // đúng khung hình của mốc mới, giữ nguyên trạng thái đang phát/dừng
    // (setPlaying không đổi ở đây).
    engineRef.current?.seekTo(clamped);
    setTime(clamped);
    if (st.playing) {
      void syncAudioRef.current(clamped, true);
      // Kill every scheduled SFX/BGM node, then re-schedule from the new
      // playhead — nothing scheduled for the old position can fire late.
      stopLayers();
      startLayers(clamped);
    }
  }

  function toggleVoice() {
    const next = !voiceOn;
    setVoiceOn(next);
    layerOnRef.current.voice = next;
    if (!next) stopAudio();
    else if (stRef.current.playing) void syncAudioRef.current(stRef.current.time, true);
  }

  function toggleBgm() {
    const next = !bgmOn;
    setBgmOn(next);
    layerOnRef.current.bgm = next;
    if (!next) stopBgm();
    else if (stRef.current.playing) startBgm(stRef.current.time);
  }

  function toggleSfx() {
    const next = !sfxOn;
    setSfxOn(next);
    layerOnRef.current.sfx = next;
    if (!next) stopSfx();
    else if (stRef.current.playing) scheduleSfx(stRef.current.time);
  }

  // --- B-roll video của từng part: server chỉ trả đường dẫn file trong
  // project (part.videoFile, kèm kích thước ffprobe videoW/videoH) —
  // bytes được tải qua đường chunk getMediaChunk, tạo blob URL để mount
  // effect bên dưới gán vào part.video cho engine.
  // Thiếu bước này engine không có <video> nào để vẽ: part video chỉ
  // còn khung đen + tiếng thoại (lỗi user báo 2026-11-01). Video tải
  // lỗi thì part đó rơi về ảnh như cũ, không chặn cả preview.
  const [videoUrls, setVideoUrls] = useState<Record<string, string>>({});
  const videoUrlsRef = useRef<Record<string, string>>({});
  const videoSigRef = useRef("");
  useEffect(() => {
    const vids = data.parts.filter((p) => p.videoFile);
    const sig = `${detail.id}|${vids.map((p) => `${p.id}:${p.videoFile}`).join("|")}`;
    if (videoSigRef.current === sig) return;
    videoSigRef.current = sig;
    for (const u of Object.values(videoUrlsRef.current)) URL.revokeObjectURL(u);
    videoUrlsRef.current = {};
    setVideoUrls({});
    if (vids.length === 0) return;
    let cancelled = false;
    void (async () => {
      const out: Record<string, string> = {};
      for (const p of vids) {
        if (!p.videoFile) continue;
        try {
          const { blob } = await fetchMediaBlob(detail.id, p.videoFile);
          out[p.id] = URL.createObjectURL(blob);
        } catch {
          // tải lỗi -> part rơi về ảnh như cũ
        }
      }
      if (cancelled) {
        for (const u of Object.values(out)) URL.revokeObjectURL(u);
        return;
      }
      videoUrlsRef.current = out;
      setVideoUrls(out);
    })();
    return () => {
      cancelled = true;
    };
  }, [data, detail.id]);

  // Nạp engine thật của repo (lib/render-engine.js) và mount vào stage.
  // Dữ liệu đổi (sau khi sửa plan/kịch bản/media và đọc lại) -> chữ ký đổi
  // -> mount lại từ dữ liệu mới, không giữ bản cũ. Chữ ký CÓ tính cả dấu
  // vân tay của engineSource và motion từng part: thiếu hai thứ này,
  // preview đang mở giữ engine/motion cũ dù repo đã sửa (lỗi blurtest001
  // 2026-11-01 — engine đã đảo dấu pan + nối motion render nhưng preview
  // mở sẵn vẫn chạy bản cũ). Chữ ký cũng tính trạng thái blob URL của
  // từng part video: video tải xong (chunk) thì mount lại với
  // part.video, không để part video đứng ở khung ảnh/đen của lần mount
  // khi URL chưa có. Chữ ký còn tính dấu vân tay của tplInputs và tplCss
  // từng part (đợt C2): thiếu hai thứ này, đổi chữ template (inputs) hoặc
  // sửa style.css của template trong lúc Preview đang mở không remount,
  // người xem nhìn nhầm bản template cũ dù dữ liệu đã mới. tplHtml cũng
  // được băm nội dung thay vì chỉ độ dài, cùng một lớp lỗi.
  useEffect(() => {
    if (!stageRef.current) return;
    const hashStr = (s: string): string => {
      let h = 0;
      for (let i = 0; i < s.length; i++) {
        h = (Math.imul(h, 31) + s.charCodeAt(i)) >>> 0;
      }
      return `${s.length}.${h}`;
    };
    const sig = `${detail.id}|${data.width}x${data.height}|eng${hashStr(data.engineSource)}|${data.parts
      .map((p) => `${p.id}:${p.start}-${p.end}:${p.motion ?? ""}:${p.image.length}:${p.videoFile ? (videoUrls[p.id] ? "vid1" : "vid0") : ""}:tpl${hashStr(p.tplHtml)}.${hashStr(p.tplCss)}.${hashStr(JSON.stringify(p.tplInputs))}:${p.karaoke.lines.length}:${p.karaoke.subsHidden ? 1 : 0}`)
      .join("|")}`;
    if (sigRef.current === sig && engineRef.current) return;
    sigRef.current = sig;
    const st = stRef.current;
    st.playing = false;
    st.time = 0;
    st.audioPart = -2;
    cancelAnimationFrame(st.raf);
    // Engine sắp mount lại (mount tự reset runningMode=false); tắt
    // runningMode của bản engine cũ cho chắc để animation không chạy
    // nền trong lúc đổi dữ liệu.
    engineRef.current?.setPlaying?.(false);
    stopAudio();
    stopLayers();
    audioEls.current.clear();
    setPlaying(false);
    setTime(0);
    const script = document.createElement("script");
    script.textContent = data.engineSource;
    document.body.appendChild(script);
    script.remove();
    const V = (window as unknown as { VieNeuRender?: VieNeuApi }).VieNeuRender;
    if (!V || !stageRef.current) {
      setEngineOk(false);
      return;
    }
    engineRef.current = V;
    // Part video: thay đường dẫn file trong project bằng blob URL đã
    // tải + kích thước thật để engine dựng <video> đúng chế độ (cửa sổ
    // 3:4 cố định trên nền blur cho video ngang/vuông, đầy khung cho
    // video 9:16). Chưa tải xong thì part tạm hiện theo ảnh như cũ.
    const engineParts = data.parts.map((p) => {
      const url = p.videoFile ? videoUrls[p.id] : undefined;
      return url
        ? { ...p, video: url, videoW: p.videoW ?? undefined, videoH: p.videoH ?? undefined }
        : p;
    });
    V.mount(stageRef.current, { W: data.width, H: data.height, parts: engineParts });
    V.seekTo(0);
    setEngineOk(true);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, detail.id, videoUrls]);

  useEffect(() => {
    const els = audioEls.current;
    const st = stRef.current;
    return () => {
      st.playing = false;
      cancelAnimationFrame(st.raf);
      engineRef.current?.setPlaying?.(false);
      for (const el of els.values()) el.pause();
      stopBgm();
      stopSfx();
      for (const u of Object.values(videoUrlsRef.current)) URL.revokeObjectURL(u);
      videoUrlsRef.current = {};
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const update = () => setScale(Math.min(el.clientWidth / data.width, 0.72));
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [data.width]);

  const displayTime = dragVal ?? time;
  const activeIdx = parts.length ? findPreviewPartIdx(parts, displayTime) : -1;
  const activePart = activeIdx >= 0 ? parts[activeIdx] : undefined;
  let currentLine = "";
  let subsNote = "";
  if (activePart) {
    if (activePart.karaoke.subsHidden) {
      subsNote = "Part này có template chữ thật — phụ đề karaoke ẩn (đúng thiết kế).";
    } else {
      const lines = activePart.karaoke.lines;
      const line = lines.find((l) => displayTime >= l.start && displayTime < l.end);
      if (line) {
        currentLine = line.words.map((w) => w.text).join(" ");
      } else if (lines.length > 0) {
        subsNote = "Đang ở khoảng nghỉ giữa hai dòng phụ đề — không có dòng nào tại đúng mốc này.";
      }
    }
  }
  const planPartById = new Map<string, Part>();
  for (const sc of detail.plan?.scenes ?? []) {
    for (const p of sc.parts) planPartById.set(p.id, p);
  }

  return (
    <div className="min-w-0">
      <div ref={wrapRef} className="w-full min-w-0">
        <div
          className="relative mx-auto overflow-hidden rounded-lg bg-black"
          style={{ width: data.width * scale, height: data.height * scale }}
        >
          <div
            ref={stageRef}
            className="vieneu-stage"
            style={{ transform: `scale(${scale})`, transformOrigin: "top left" }}
          />
        </div>
      </div>
      {!engineOk && (
        <p className="mt-2 text-sm text-[var(--bad)]">
          Không nạp được engine render của repo (lib/render-engine.js — VieNeuRender).
        </p>
      )}
      {parts.some((p) => p.videoFile && !videoUrls[p.id]) && (
        <p className="mt-2 text-xs text-[var(--dim)]">
          Đang tải file video b-roll về cho Preview (tải theo từng phần) — part video hiện hình ngay khi tải xong.
        </p>
      )}
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button
          type="button"
          className={btnPrimary}
          disabled={!engineOk}
          onClick={() => (playing ? pausePlayback() : startPlayback())}
          aria-label={playing ? "Tạm dừng preview HTML" : "Phát preview HTML"}
        >
          {playing ? "⏸ Tạm dừng" : "▶ Phát"}
        </button>
        <span className="mono text-sm">
          {fmtClock(displayTime)} / {fmtClock(duration)}
        </span>
        {activePart && (
          <span className="mono text-xs text-[var(--dim)]">
            {activePart.id} · {fmtClock(activePart.start)}–{fmtClock(activePart.end)}
          </span>
        )}
      </div>
      <div className="mt-2 flex flex-wrap items-center gap-2" role="group" aria-label="Bật tắt từng lớp âm thanh của Preview">
        <button
          type="button"
          className={btnCls}
          aria-pressed={voiceOn}
          onClick={toggleVoice}
          aria-label="Bật hoặc tắt lớp giọng đọc trong Preview"
        >
          Giọng đọc: {voiceOn ? "Đang bật" : "Đã tắt"}
        </button>
        <button
          type="button"
          className={btnCls}
          aria-pressed={bgmOn}
          disabled={!data.bgm}
          onClick={toggleBgm}
          aria-label="Bật hoặc tắt lớp nhạc nền trong Preview"
        >
          Nhạc nền{data.bgm ? ` ${data.bgm.id}` : ""}: {!data.bgm ? "Chưa chọn" : bgmOn ? "Đang bật" : "Đã tắt"}
        </button>
        <button
          type="button"
          className={btnCls}
          aria-pressed={sfxOn}
          disabled={data.sfxEvents.length === 0}
          onClick={toggleSfx}
          aria-label="Bật hoặc tắt lớp hiệu ứng âm thanh SFX trong Preview"
        >
          SFX ({data.sfxEvents.length}): {data.sfxEvents.length === 0 ? "Không có" : sfxOn ? "Đang bật" : "Đã tắt"}
        </button>
        <InfoTip label="Chú thích cách mix âm thanh của Preview" text="Mix đúng tham số render cuối: nhạc nền lặp ở volume 0,12, tự hạ khi có giọng đọc, fade-out 2 giây cuối; SFX phát tại mốc part + offsetSec trong plan, dừng đúng cuối part (không lấn sang part sau), SFX nặng (thud/slam/boom) bị giới hạn 0,4; riêng tiếng gõ typing chỉ kéo dài theo text hiển thị trong template (0,1 giây/ký tự), không phủ hết phần giọng đọc." />
      </div>
      {layerMsg && (
        <p className="mt-1 text-xs" style={{ color: "var(--warn)" }}>{layerMsg}</p>
      )}
      {data.sfxEvents.length > 0 && (
        <p className="mono mt-1 text-[11px] text-[var(--dim)]">
          Mốc SFX: {data.sfxEvents.map((e) => `${e.id} @ ${fmtClock(e.atSec)}–${fmtClock(e.endSec)} (${e.durationSec.toFixed(2)}s, vol ${e.volume})`).join(" · ")}
        </p>
      )}
      {(data.missingSfx ?? []).length > 0 && (
        <p className="mt-1 text-xs" style={{ color: "var(--warn)" }}>
          Cảnh báo: thiếu file SFX {(data.missingSfx ?? []).map((m) => `${m.id} (part ${m.partId})`).join(", ")} — render sẽ DỪNG với RENDER-ERROR (A26). Khôi phục file mp3 trong thư mục sfx hoặc gỡ SFX khỏi plan trước khi render.
        </p>
      )}
      <input
        type="range"
        min={0}
        max={duration || 0}
        step={0.05}
        value={displayTime}
        className="mt-2 w-full"
        aria-label="Tua preview tới thời điểm (giây)"
        onChange={(e) => {
          const v = Number(e.target.value);
          setDragVal(v);
          engineRef.current?.seekTo(v);
        }}
        onPointerUp={() => {
          if (dragVal !== null) {
            seekToTime(dragVal);
            setDragVal(null);
          }
        }}
        onKeyUp={() => {
          if (dragVal !== null) {
            seekToTime(dragVal);
            setDragVal(null);
          }
        }}
        onBlur={() => {
          if (dragVal !== null) {
            seekToTime(dragVal);
            setDragVal(null);
          }
        }}
      />
      {currentLine && (
        <p className="mt-1 text-sm">
          Phụ đề tại {fmtClock(displayTime)}:{" "}
          <span className="font-semibold">“{currentLine}”</span>
        </p>
      )}
      {subsNote && (
        <p className="mt-1 text-xs" style={{ color: "var(--warn)" }}>
          {subsNote}
        </p>
      )}
      <div
        className="mt-3 max-h-96 min-w-0 space-y-1 overflow-auto pr-1"
        aria-label="Danh sách part — bấm để nhảy tới đúng mốc part"
      >
        {parts.map((p, i) => {
          const pp = planPartById.get(p.id);
          const active = i === activeIdx;
          return (
            <button
              key={p.id}
              type="button"
              className="flex w-full max-w-full items-start gap-2 overflow-hidden rounded-lg border px-2 py-1.5 text-left active:opacity-70"
              style={{
                borderColor: active ? "var(--accent)" : "var(--border)",
                background: active
                  ? "color-mix(in srgb, var(--accent) 14%, transparent)"
                  : "var(--surface2)",
              }}
              onClick={() => seekToTime(p.start)}
              aria-label={`Nhảy tới part ${p.id} tại ${fmtClock(p.start)}`}
              aria-current={active ? "true" : undefined}
            >
              <span className="mono text-[11px] font-bold">{p.id}</span>
              <span className="mono text-[11px] text-[var(--dim)]">{fmtClock(p.start)}</span>
              <span className="min-w-0 flex-1 truncate text-xs">{pp?.voiceText ?? ""}</span>
              {p.templateId && (
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                  style={{
                    background: "color-mix(in srgb, var(--accent) 20%, transparent)",
                    color: "var(--accent)",
                  }}
                >
                  {p.templateId}
                </span>
              )}
              {p.videoFile && (
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-semibold"
                  style={{
                    background: "color-mix(in srgb, var(--ok) 20%, transparent)",
                    color: "var(--ok)",
                  }}
                >
                  video{p.videoW && p.videoH ? ` ${p.videoW}×${p.videoH}` : ""}
                  {videoUrls[p.id] ? "" : " · đang tải…"}
                </span>
              )}
              {!p.image && !p.videoFile && (
                <span className="text-[10px] font-semibold" style={{ color: "var(--bad)" }}>
                  thiếu ảnh
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function PreviewTab({ detail }: { detail: ProjectDetail }) {
  const queryClient = useQueryClient();
  const dataQ = useQuery({
    queryKey: ["preview-data", detail.id],
    queryFn: () => api.getPreviewData({ projectId: detail.id }),
    staleTime: 0,
  });
  const overlapWarnings: string[] = [];
  const sorted = [...detail.karaokeLines].sort((a, b) => a.startSec - b.startSec);
  for (let i = 1; i < sorted.length; i++) {
    const prev = sorted[i - 1];
    const cur = sorted[i];
    if (prev && cur && cur.startSec < prev.endSec - 0.01) {
      overlapWarnings.push(`Dòng karaoke chồng mốc quanh ${cur.startSec.toFixed(2)}s: “${cur.text.slice(0, 40)}…” — chạy lại karaoke sau khi sửa gốc, không sửa tay file phụ đề.`);
    }
  }
  const reload = () => {
    queryClient.invalidateQueries({ queryKey: ["project", detail.id] });
    void dataQ.refetch();
  };
  const missingImages = (dataQ.data?.parts ?? []).filter((p) => !p.image);
  return (
    <div className="grid grid-cols-[minmax(0,1fr)] gap-4">
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 text-sm">
        <p>
          <strong>Preview HTML</strong> — xem trước đúng như bản render
          <InfoTip text={`Bản chạy xem trước khi render, dùng đúng engine render duy nhất của nhà máy (lib/render-engine.js — VieNeuRender) và đúng dữ liệu như trang render chính thức: ảnh thật từng part (b-roll nếu có, không thì ảnh cảnh), template hiện đúng cửa sổ part, karaoke highlight từng từ, phụ đề ẩn ở part có template chữ thật, motion theo part, chuyển cảnh crossfade 0,5s, khung ${dataQ.data ? `${dataQ.data.width}×${dataQ.data.height}` : "720×1280"}. Giọng WAV từng part phát đồng bộ theo mốc start/end của tts.json; kéo thanh tua hoặc bấm vào part để nhảy đúng mốc. Preview phát đủ 3 lớp âm thanh như bản render cuối với nút tắt riêng từng lớp; tua hoặc tạm dừng sẽ dừng và lên lịch lại SFX/BGM theo mốc mới. Dữ liệu được đọc lại mỗi lần mở tab này — vừa sửa plan/kịch bản/media xong thì bấm “Đọc lại dữ liệu preview” để chắc chắn đang xem bản mới.`} />
        </p>
        <button type="button" className={`${btnCls} mt-2`} onClick={reload} aria-label="Đọc lại dữ liệu preview mới nhất">
          ↻ Đọc lại dữ liệu preview
        </button>
      </div>
      {overlapWarnings.slice(0, 4).map((w) => (
        <p key={w} className="text-sm" style={{ color: "var(--bad)" }}>⚠ {w}</p>
      ))}
      {dataQ.isPending && (
        <p className="text-[var(--dim)]">Đang gom dữ liệu preview từ kho thật (ảnh từng part, template, karaoke)…</p>
      )}
      {dataQ.error && (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
          <h3 className="font-bold">Chưa dựng được Preview HTML</h3>
          <p className="mt-1 text-sm text-[var(--bad)]">{String(dataQ.error)}</p>
          <p className="mt-1 text-sm text-[var(--dim)]">
            Preview cần TTS + karaoke của bước 4 xong trước — chạy ba job dưới đây rồi bấm “Đọc lại dữ liệu preview”.
          </p>
          <div className="mt-2 grid gap-2">
            <JobRunner projectId={detail.id} step="tts" label="TTS toàn bộ" forceOption />
            <JobRunner projectId={detail.id} step="normalize" label="chuẩn hóa chunk" />
            <JobRunner projectId={detail.id} step="karaoke" label="karaoke" />
          </div>
        </section>
      )}
      {dataQ.data && (
        <section className="min-w-0 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Trình phát Preview HTML">
          <HtmlPreviewPlayer key={detail.id} detail={detail} data={dataQ.data} />
          {missingImages.length > 0 && (
            <p className="mt-2 text-sm font-semibold" style={{ color: "var(--bad)" }}>
              {missingImages.length} part chưa có ảnh ({missingImages.map((p) => p.id).join(", ")}) —
              preview và bản render sẽ hiện nền đen ở các part này. Bổ sung media ở bước 3.
            </p>
          )}
        </section>
      )}
    </div>
  );
}

// Setting giọng đọc (giọng + tốc độ đọc) nằm ở tab TTS — luật 03/11/2026:
// chuyển từ tab 2 · Phân cảnh & template sang đây vì đây là tham số của
// bước tổng hợp tiếng. Vẫn đọc/ghi đúng hai trường voice/speed trong plan,
// lưu qua cùng action savePlan như tab Phân cảnh.
