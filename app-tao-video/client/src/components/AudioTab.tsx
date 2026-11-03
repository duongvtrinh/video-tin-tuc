// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { btnCls, btnPrimary, fmtSec, inputCls, labelCls } from "../lib";
import { InfoTip } from "./InfoTip";
import { JobRunner, JobsList, MediaFile } from "./shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import type { Plan, ProjectDetail, TabKey } from "../lib";

function VoiceSettings({ detail }: { detail: ProjectDetail }) {
  const queryClient = useQueryClient();
  const [voice, setVoice] = useState(detail.plan?.voice ?? "Hữu Quân");
  const [speed, setSpeed] = useState(detail.plan?.speed ?? 1.0);
  const dirty = useRef(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  useEffect(() => {
    if (!dirty.current) {
      setVoice(detail.plan?.voice ?? "Hữu Quân");
      setSpeed(detail.plan?.speed ?? 1.0);
    }
  }, [detail]);
  const save = useMutation({
    mutationFn: () =>
      api.savePlan({
        projectId: detail.id,
        plan: { ...(detail.plan as Plan), voice, speed },
      }),
    onSuccess: (r) => {
      dirty.current = false;
      setSaveMsg(r.problems.length > 0 ? `Đã lưu nhưng plan có vấn đề: ${r.problems.join("; ")}` : "Đã lưu cài đặt giọng đọc (đã snapshot bản trước).");
      queryClient.invalidateQueries({ queryKey: ["project", detail.id] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  if (!detail.plan) {
    return (
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">Giọng đọc</h3>
        <p className="mt-2 text-sm text-[var(--dim)]">Chưa có plan — hoàn thành tab 1 · Kịch bản và tab 2 · Phân cảnh trước, cài đặt giọng đọc sẽ hiện ở đây.</p>
      </section>
    );
  }
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
      <h3 className="font-bold">
        Giọng đọc
        <InfoTip text="Giọng và tốc độ đọc mà bước TTS bên dưới sử dụng. Đổi xong bấm Lưu cài đặt giọng đọc, rồi chạy lại TTS — nếu part đã có WAV thì bật ép chạy lại để đọc lại bằng giọng/tốc độ mới." />
      </h3>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <div>
          <label className={labelCls} htmlFor="plan-voice">Giọng đọc</label>
          <input
            id="plan-voice"
            className={inputCls}
            value={voice}
            onChange={(e) => {
              dirty.current = true;
              setVoice(e.target.value);
            }}
            list="voice-list"
          />
          <datalist id="voice-list"><option value="Hữu Quân" /></datalist>
        </div>
        <div>
          <label className={labelCls} htmlFor="plan-speed">Tốc độ đọc (không giảm dưới 1,0 để kéo dài)</label>
          <input
            id="plan-speed"
            className={inputCls}
            type="number"
            step="0.05"
            min="0.8"
            max="1.5"
            value={speed}
            onChange={(e) => {
              dirty.current = true;
              setSpeed(Number(e.target.value) || 1);
            }}
          />
        </div>
      </div>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        <button type="button" className={btnPrimary} disabled={save.isPending} onClick={() => save.mutate()} aria-label="Lưu cài đặt giọng đọc">
          {save.isPending ? "Đang lưu…" : "Lưu cài đặt giọng đọc"}
        </button>
        {saveMsg && <span className="text-sm" style={{ color: saveMsg.includes("vấn đề") ? "var(--warn)" : "var(--ok)" }}>{saveMsg}</span>}
        {save.error && <span className="text-sm text-[var(--bad)]">{String(save.error)}</span>}
      </div>
    </section>
  );
}

export function AudioTab({ detail, onNavigate }: { detail: ProjectDetail; onNavigate?: (tab: TabKey) => void }) {
  const [showListen, setShowListen] = useState(false);
  return (
    <div className="grid gap-4">
      <VoiceSettings detail={detail} />
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">
          TTS — đọc lời bằng VieNeu
          <InfoTip text="Bước này phải xong trước Preview HTML: Preview không tự tạo mốc thời gian, nó phát hình theo đúng start/end của tts.json và highlight phụ đề theo đúng karaoke.json. TTS chạy nền; part đã có WAV sẽ được bỏ qua, chỉ đọc lại part đổi kịch bản/từ điển. Tổng thời lượng thật lấy từ tts.json sau khi chạy xong." />
        </h3>
        <div className="mt-2"><JobRunner projectId={detail.id} step="tts" label="TTS toàn bộ" forceOption /></div>
        {detail.ttsParts.length > 0 && (
          <>
            <p className="mono mt-2 text-xs text-[var(--dim)]">
              {detail.ttsParts.length} part · tổng {fmtSec(detail.totalDurationSec)} · móc lại nên rơi quanh {fmtSec((detail.totalDurationSec ?? 0) / 2)} (50%)
            </p>
            <button type="button" className={`${btnCls} mt-2`} onClick={() => setShowListen((v) => !v)} aria-label="Nghe thử giọng đọc từng part">
              {showListen ? "Ẩn nghe thử" : "Nghe thử giọng đọc từng part"}
            </button>
            {showListen && (
              <div className="mt-2 grid gap-2">
                {detail.ttsParts.map((p) => (
                  <div key={p.id} className="flex flex-wrap items-center gap-2">
                    <span className="mono w-40 text-xs">{p.id} · {fmtSec(p.startSec)}–{fmtSec(p.endSec)}</span>
                    <span className="min-w-52 flex-1">
                      <MediaFile projectId={detail.id} relPath={`build/audio/voice/${p.audioFile}`} kind="audio" label={`Giọng đọc ${p.id}`} />
                    </span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </section>
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">
          Phụ đề karaoke + Preflight
          <InfoTip text="Chuẩn hóa chunk trước, rồi karaoke. Nếu karaoke cảnh báo từ dài >2s hoặc dòng trùng mốc: sửa gốc ở khâu căn chữ, không sửa tay file phụ đề. Xong bước này mới sang Preview HTML để xem phụ đề chạy cùng giọng đọc. Preflight đọc cảnh báo trước khi render, đừng bỏ qua." />
        </h3>
        <div className="mt-2 grid gap-2">
          <JobRunner projectId={detail.id} step="normalize" label="chuẩn hóa chunk" />
          <JobRunner projectId={detail.id} step="karaoke" label="karaoke" onDone={() => { if (detail.ttsParts.length > 0) onNavigate?.("preview"); }} />
          <JobRunner projectId={detail.id} step="preflight" label="preflight" onDone={() => onNavigate?.("preview")} />
        </div>
        {detail.karaokeLineCount > 0 && (
          <p className="mono mt-2 text-xs text-[var(--dim)]">Karaoke hiện có: {detail.karaokeLineCount} dòng — cảnh báo trùng mốc (nếu có) hiện ở tab Preview HTML.</p>
        )}
      </section>
      <JobsList projectId={detail.id} />
    </div>
  );
}
