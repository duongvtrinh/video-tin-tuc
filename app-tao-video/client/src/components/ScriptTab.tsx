// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { btnCls, btnPrimary, countWords, fmtSec, inputCls, labelCls, splitScriptToScenes } from "../lib";
import { AutoPanel } from "./AutoPanel";
import { InfoTip } from "./InfoTip";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import type { ProjectDetail, ProjectSummary, Scene, TabKey } from "../lib";

export function ScriptTab({ detail, summary, onNavigate }: { detail: ProjectDetail; summary?: ProjectSummary; onNavigate?: (tab: TabKey) => void }) {
  const queryClient = useQueryClient();
  const [content, setContent] = useState(detail.scriptContent);
  const [topic, setTopic] = useState(detail.scriptTopic || detail.input.topic);
  const [facts, setFacts] = useState("");
  const [angle, setAngle] = useState("");
  const [targetSeconds, setTargetSeconds] = useState(240);
  const [aiMsg, setAiMsg] = useState<string | null>(null);
  const [splitMsg, setSplitMsg] = useState<string | null>(null);
  const dirty = useRef(false);
  useEffect(() => {
    if (!dirty.current) {
      setContent(detail.scriptContent);
      setTopic(detail.scriptTopic || detail.input.topic);
    }
  }, [detail]);
  // Không còn nút "Lưu kịch bản": kịch bản TỰ LƯU khi trường nhập MẤT
  // FOCUS (luật CEO 03/11, thay cơ chế debounce ~0,9s khi gõ) — đang gõ
  // trong ô Chủ đề / ô Toàn văn thì không lưu liên tục; bấm ra ngoài ô
  // mới ghi xuống kho đúng một lần, nên đóng/mở lại app vẫn còn nguyên
  // bản đang soạn mà không cần bấm lưu tay. Hai đường còn lại (Tách
  // cảnh/part và Tạo video tự động) vốn đã tự lưu trước khi chạy, nên
  // nút lưu tay là thừa. Khác luật cũ ở điểm quan trọng: kịch bản bị
  // XÓA TRẮNG rồi mất focus cũng được lưu (lưu bản trống xuống kho) —
  // bản trống làm nội dung phân cảnh lệch kịch bản hiện tại, AutoPanel
  // sẽ tự reset các phân cảnh đã chia và đưa nút chạy về trạng thái
  // "▶ Tạo video tự động" theo luật reset theo kịch bản.
  const [autoSaveState, setAutoSaveState] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const lastSavedRef = useRef<{ content: string; topic: string }>({
    content: detail.scriptContent,
    topic: detail.scriptTopic || detail.input.topic,
  });
  const latestRef = useRef({ content, topic });
  latestRef.current = { content, topic };
  const savingRef = useRef(false);
  const saveScriptOnBlur = () => {
    if (!dirty.current || savingRef.current) return;
    const { content: c, topic: t } = latestRef.current;
    if (lastSavedRef.current.content === c && lastSavedRef.current.topic === t) {
      dirty.current = false;
      return;
    }
    savingRef.current = true;
    setAutoSaveState("saving");
    api
      .saveScript({ projectId: detail.id, content: c, topic: t })
      .then(() => {
        lastSavedRef.current = { content: c, topic: t };
        savingRef.current = false;
        if (latestRef.current.content === c && latestRef.current.topic === t) {
          dirty.current = false;
          setAutoSaveState("saved");
        } else {
          // Người dùng sửa tiếp trong lúc đang lưu: lưu luôn bản mới
          // nhất thay vì bắt họ phải mất focus thêm lần nữa.
          saveScriptOnBlur();
        }
        queryClient.invalidateQueries({ queryKey: ["project", detail.id] });
        queryClient.invalidateQueries({ queryKey: ["projects"] });
      })
      .catch(() => {
        savingRef.current = false;
        setAutoSaveState("error");
      });
  };
  const gen = useMutation({
    mutationFn: () =>
      api.generateScriptAI({
        topic: topic || detail.input.name,
        verifiedFacts: facts,
        angle,
        targetSeconds,
      }),
    onSuccess: (r) => {
      dirty.current = true;
      setContent(r.draft);
      setAiMsg(`AI đã viết nháp ${r.wordCount} từ (ước tính ~${fmtSec(r.wordCount / 4.16)}). Mục tiêu thời lượng chỉ là gợi ý cho AI lúc viết nên bản nháp lệch mục tiêu là bình thường, không cần ép khớp. Đây là bản nháp từ đúng dữ kiện bạn đưa — đọc kỹ và sửa trực tiếp trong ô Toàn văn bên dưới; app tự lưu khi bạn bấm ra ngoài ô Toàn văn, không cần nút lưu.`);
    },
  });
  const splitToPlan = useMutation({
    mutationFn: async () => {
      await api.saveScript({ projectId: detail.id, content, topic });
      const scenes: Scene[] = splitScriptToScenes(content);
      return api.savePlan({
        projectId: detail.id,
        plan: {
          pauseAfterMs: detail.plan?.pauseAfterMs ?? 180,
          speed: detail.plan?.speed ?? 1.0,
          voice: detail.plan?.voice ?? "Hữu Quân",
          bgm: detail.plan?.bgm,
          scenes,
        },
      });
    },
    onSuccess: (r) => {
      dirty.current = false;
      setSplitMsg(
        r.problems.length > 0
          ? `Đã tách cảnh nhưng plan có vấn đề: ${r.problems.join("; ")}`
          : "Đã tách kịch bản thành cảnh/part và lưu plan — tự chuyển sang bước Phân cảnh để bổ sung tóm tắt + prompt từng cảnh rồi dàn template.",
      );
      queryClient.invalidateQueries({ queryKey: ["project", detail.id] });
      if (r.problems.length === 0) onNavigate?.("scenes");
    },
  });
  const words = countWords(content);
  return (
    <div className="grid gap-4">
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">
          Cách A — Viết bằng AI từ sự kiện đã kiểm chứng
          <InfoTip text="AI chỉ viết từ dữ kiện bạn dán vào đây — không tự bịa số, tên, ngày. Dán càng đúng nguồn, kịch bản càng đáng tin." />
        </h3>
        <div className="mt-3 grid gap-3">
          <div>
            <label className={labelCls} htmlFor="ai-facts">Sự kiện đã kiểm chứng + nguồn</label>
            <textarea id="ai-facts" className={inputCls} rows={5} value={facts} onChange={(e) => setFacts(e.target.value)} placeholder="Mỗi dòng một sự kiện kèm nguồn, ví dụ: Tuyến dài 54 km (báo X, ngày…)…" />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className={labelCls} htmlFor="ai-angle">Góc làm</label>
              <input id="ai-angle" className={inputCls} value={angle} onChange={(e) => setAngle(e.target.value)} placeholder="Ví dụ: từ đề xuất trên giấy ra công trường thật" />
            </div>
            <div>
              <div className="flex items-center gap-1">
                <label className={labelCls} htmlFor="ai-target">Mục tiêu thời lượng (chỉ là gợi ý)</label>
                <InfoTip text="Mục này chỉ là một prompt phụ mang tính gợi ý, được gộp chung vào prompt chính khi nhờ AI viết kịch bản: app đổi giây mục tiêu thành số từ dự tính (~4,16 từ/giây) để AI định hướng độ dài lúc viết. Nó KHÔNG ràng buộc kịch bản đầu ra — bản nháp dài hơn hay ngắn hơn mục tiêu đều được nhận nguyên trạng, không bị cắt, bơm chữ hay chấm đạt/không đạt theo con số này." />
              </div>
              <select id="ai-target" className={inputCls} value={targetSeconds} onChange={(e) => setTargetSeconds(Number(e.target.value))}>
                <option value={180}>180 giây (gợi ý ~750 từ)</option>
                <option value={210}>210 giây (gợi ý ~875 từ)</option>
                <option value={240}>240 giây (gợi ý ~1000 từ)</option>
                <option value={270}>270 giây (gợi ý ~1120 từ)</option>
                <option value={300}>300 giây (gợi ý ~1250 từ)</option>
              </select>
            </div>
          </div>
          <div>
            <button type="button" className={btnPrimary} disabled={!facts.trim() || gen.isPending} onClick={() => gen.mutate()} aria-label="Viết kịch bản bằng AI">
              {gen.isPending ? "AI đang viết…" : "Viết kịch bản bằng AI"}
            </button>
            {gen.error && <span className="ml-2 text-sm text-[var(--bad)]">{String(gen.error)}</span>}
          </div>
          {aiMsg && <p className="text-sm" style={{ color: "var(--ok)" }}>{aiMsg}</p>}
        </div>
      </section>
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">Cách B — Kịch bản (AI nháp hoặc nhập thủ công)</h3>
        <div className="mt-3 grid gap-3">
          <div>
            <label className={labelCls} htmlFor="script-topic">Chủ đề của kịch bản</label>
            <input id="script-topic" className={inputCls} value={topic} onChange={(e) => { dirty.current = true; setAutoSaveState("idle"); setTopic(e.target.value); }} onBlur={saveScriptOnBlur} />
          </div>
          <div>
            <label className={labelCls} htmlFor="script-content">Toàn văn kịch bản</label>
            <textarea
              id="script-content"
              className={`${inputCls} leading-relaxed`}
              rows={14}
              value={content}
              onChange={(e) => { dirty.current = true; setAutoSaveState("idle"); setContent(e.target.value); }}
              onBlur={saveScriptOnBlur}
              placeholder="Dán kịch bản thủ công vào đây, hoặc dùng bản AI nháp ở trên…"
            />
          </div>
          <p className="mono text-xs text-[var(--dim)]">
            {words} từ · ước tính {fmtSec(words / 4.16)} (giọng VieNeu ~4,16 từ/giây — thời lượng THẬT chỉ có sau TTS)
            {words > 0 && words / 4.16 < 180 && (
              <span style={{ color: "var(--warn)" }}> · dưới 180s: cần mở rộng bằng góc đã kiểm chứng, không độn/lặp/giảm tốc độ</span>
            )}
          </p>
          {autoSaveState !== "idle" && (
            <div className="flex items-center" aria-live="polite">
              {autoSaveState === "saving" && <span className="text-xs text-[var(--dim)]">Đang tự lưu kịch bản…</span>}
              {autoSaveState === "saved" && <span className="text-xs" style={{ color: "var(--ok)" }}>Đã tự lưu kịch bản</span>}
              {autoSaveState === "error" && <span className="text-xs text-[var(--bad)]">Tự lưu kịch bản lỗi — bấm vào ô nhập rồi bấm ra ngoài để app lưu lại.</span>}
            </div>
          )}
          <div className="flex flex-wrap items-center gap-2">
            <button type="button" className={btnCls} disabled={!content.trim() || splitToPlan.isPending} onClick={() => splitToPlan.mutate()} aria-label="Tách kịch bản thành cảnh và part">
              Tách thành cảnh/part → sang Phân cảnh
            </button>
          </div>
          {splitMsg && <p className="text-sm" style={{ color: "var(--ok)" }}>{splitMsg}</p>}
          {splitToPlan.error && <p className="text-sm text-[var(--bad)]">{String(splitToPlan.error)}</p>}
        </div>
        {/* Tạo video tự động nằm NGAY trong Cách B (không còn là panel
            riêng tách khỏi khối Kịch bản như trước): nút chạy ở đây, và
            tiến trình các bước chỉ hiện ra sau khi bấm chạy. Kịch bản
            đang soạn trong ô trên mà chưa kịp tự lưu cũng được panel tự
            lưu trước khi chạy. */}
        <AutoPanel
          detail={detail}
          summary={summary}
          onNavigate={onNavigate ?? (() => {})}
          unsavedScript={() => content}
          unsavedTopic={() => topic}
        />
      </section>
    </div>
  );
}

// Plan template inputs are text for the template engine, but pipeline
// projects can carry raw numbers/booleans (bar-chart w1..w4 = 100/52/62/0).
// The server normalizes them to strings on read; this coercion keeps the
// form controls and the template preview correct even if a numeric value
// ever slips through.
// Provenance (mediaSource) is an object in the app, but the plan schema
// also accepts the pipeline's bare-string form (getProject normalizes it
// to an object; this helper keeps rendering correct for either shape).
