// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { JOB_LABELS, STEP_DEFS, btnCls, btnPrimary, normalizeScriptText, scriptMatchesPlan, sleep, splitScriptToScenes } from "../lib";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import type { ApiResponse } from "../api";
import type { Part, Plan, ProjectDetail, ProjectSummary, TabKey } from "../lib";

const AUTO_STEPS: Array<{ key: string; label: string }> = [
  { key: "split", label: "Tách cảnh/part" },
  { key: "templates", label: "Gắn template/SFX ở beat nhấn" },
  { key: "media", label: "Media cho mục còn thiếu" },
  { key: "tts", label: "TTS" },
  { key: "normalize", label: "Chuẩn hóa chunk" },
  { key: "karaoke", label: "Karaoke" },
  { key: "preflight", label: "Preflight" },
  { key: "preview", label: "Kiểm tra Preview (chặn nền đen)" },
  { key: "render", label: "Render video" },
  { key: "export", label: "Xuất ZIP" },
];
type AutoStatus = "pending" | "running" | "done" | "error" | "skipped";
type Catalogs = ApiResponse<typeof api, "getCatalogs">;

// Tìm con số nổi bật duy nhất trong lời đọc của một part để gắn thẻ số
// liệu / khối từ khóa. Chỉ nhận khi part có đúng MỘT con số (đúng luật
// "không nhiều hơn một con số trong cùng câu" của stat-counter) và con
// số đó hoặc có đơn vị đi kèm, hoặc có dấu phân cách thập phân — năm
// đứng một mình không tính là số liệu nhấn.
function findStatPhrase(voiceText: string): { value: string; unit: string; phrase: string } | null {
  const matches = [...voiceText.matchAll(/(\d[\d.,]*)\s*(km\/h|%|km|kg|tấn|tỷ|triệu|nghìn|đồng|mét|m|lít|ha|°C)?/gi)];
  if (matches.length !== 1) return null;
  const m = matches[0];
  if (!m) return null;
  const value = m[1] ?? "";
  const unit = (m[2] ?? "").trim();
  if (!value || value.length > 10) return null;
  if (!unit && !/[.,]/.test(value)) return null;
  const phrase = unit ? `${value} ${unit}` : value;
  if (phrase.length > 30) return null;
  return { value, unit, phrase };
}

export function AutoPanel({ detail, summary, onNavigate, unsavedScript, unsavedTopic }: { detail: ProjectDetail; summary?: ProjectSummary; onNavigate: (tab: TabKey) => void; unsavedScript?: () => string; unsavedTopic?: () => string }) {
  const queryClient = useQueryClient();
  const projectId = detail.id;
  const [statuses, setStatuses] = useState<Record<string, AutoStatus>>({});
  const [running, setRunning] = useState(false);
  // Tiến trình CHỈ hiện sau khi bấm Tạo video tự động trong phiên này —
  // trước đó Cách B chỉ trưng nút chạy (làm mờ khi chưa có kịch bản),
  // không dàn sẵn thanh tiến độ + chip 10 bước, kể cả khi đã có tiến độ
  // lưu trên server từ lần chạy trước (bản lưu vẫn dùng để chạy tiếp).
  const [started, setStarted] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [needsManual, setNeedsManual] = useState<string[]>([]);
  const cancelledRef = useRef(false);
  const currentJobRef = useRef<string | null>(null);
  const setSt = (key: string, st: AutoStatus) => setStatuses((prev) => ({ ...prev, [key]: st }));
  const doneCount = AUTO_STEPS.filter((s) => statuses[s.key] === "done" || statuses[s.key] === "skipped").length;
  const pct = Math.round((doneCount / AUTO_STEPS.length) * 100);
  const alreadyDone = !!detail.preview?.exists && detail.exportZipExists;
  // Project đã đủ 6 bước (có video + ZIP) thì panel không trưng nút
  // chạy tự động nữa — muốn chạy lại ghi đè phải qua nút riêng có xác
  // nhận, tránh bấm nhầm như trước.
  const complete = summary ? STEP_DEFS.every((s) => summary.steps[s.key]) : alreadyDone;
  const [confirmRerun, setConfirmRerun] = useState(false);
  const [rerunArmed, setRerunArmed] = useState(false);
  // Sinh kịch bản AI đã có riêng ở Cách A phía trên nên panel tự động
  // KHÔNG nhập lại form kịch bản (sự kiện/góc/thời lượng) nữa: nó tái
  // sử dụng kịch bản đã có của project (đã lưu, hoặc bản đang soạn trong
  // ô Toàn văn của Cách B) và bắt đầu thẳng từ bước tách cảnh/part.
  const hasScript = detail.scriptContent.trim().length > 0;
  // Ô Toàn văn của Cách B là nguồn sự thật cho trạng thái nút trong
  // phiên đang mở: ô có chữ thì nút sáng (kể cả bản đang soạn chưa kịp
  // tự lưu, runPipeline sẽ tự lưu trước khi chạy); ô trống — chưa từng
  // có kịch bản HOẶC người dùng vừa xóa trắng ô từ một kịch bản đang
  // có — thì nút về ngay trạng thái ẩn (làm mờ + khóa bấm). Không OR
  // với bản đã lưu trên đĩa như trước: bản lưu còn đó khiến xóa trắng
  // ô vẫn bị tính là “còn kịch bản” và nút không mờ lại.
  const draftScriptText = unsavedScript ? unsavedScript() : null;
  const effectiveHasScript = draftScriptText !== null ? draftScriptText.trim().length > 0 : hasScript;
  // Luật reset theo kịch bản (CEO 03/11): đã có phân cảnh nhưng nội
  // dung phân cảnh khác kịch bản hiện tại = kịch bản đã đổi sau khi
  // tách. Khi đó phân cảnh cũ phải reset và tiến độ đã lưu KHÔNG được
  // dùng lại — nút chạy không được hiện "Tiếp tục từ bước còn thiếu",
  // chỉ khi kịch bản giữ nguyên (giống phân cảnh) mới tiếp tục được.
  const planStale = !!detail.plan && detail.plan.scenes.length > 0 && !scriptMatchesPlan(detail);
  // Điểm 3: tiến độ các bước lưu xuống server (bảng auto_progress) —
  // khôi phục khi mở lại panel và ghi lại mỗi khi trạng thái đổi, thay
  // vì chỉ sống trong bộ nhớ trang như trước.
  const savedProgress = useQuery({
    queryKey: ["autoprogress", projectId],
    queryFn: () => api.getAutoProgress({ projectId }),
    staleTime: 60_000,
  });
  const interactedRef = useRef(false);
  const hydratedRef = useRef(false);
  useEffect(() => {
    if (hydratedRef.current || interactedRef.current || !savedProgress.data) return;
    // Phân cảnh đã lệch kịch bản: tiến độ đã lưu thuộc về kịch bản cũ —
    // không khôi phục để nút "Tiếp tục từ bước còn thiếu" sống lại;
    // effect reset bên dưới sẽ xóa cả bản lưu lẫn phân cảnh cũ.
    if (planStale) return;
    hydratedRef.current = true;
    const p = savedProgress.data.progress;
    if (p && Object.keys(p.statuses).length > 0) {
      // Bước nào đang "running" trong bản lưu nghĩa là lần chạy trước bị
      // ngắt giữa chừng (đóng app) — hạ về pending để bấm Tiếp tục chạy lại.
      setStatuses(Object.fromEntries(Object.entries(p.statuses).map(([k, v]) => [k, v === "running" ? "pending" : v])) as Record<string, AutoStatus>);
      setMessages(p.messages);
      setNeedsManual(p.needsManual);
      // Bản lưu chỉ khôi phục trạng thái để bấm Tiếp tục chạy đúng bước
      // còn thiếu — KHÔNG hiện tiến trình khi vừa mở project. Thanh tiến
      // độ + chip bước + thông báo chỉ hiện sau khi bấm nút trong phiên
      // này (started), cho giao diện gọn.
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [savedProgress.data]);
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    if (!hydratedRef.current) return;
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      void api.saveAutoProgress({ projectId, statuses, messages: messages.slice(-60), needsManual }).catch(() => { /* lưu tiến độ lỗi thì lần đổi sau thử lại */ });
    }, 600);
    return () => { if (saveTimerRef.current) clearTimeout(saveTimerRef.current); };
  }, [statuses, messages, needsManual, projectId]);

  // Reset khi kịch bản đã đổi khác nội dung phân cảnh (CEO 03/11): xóa
  // các phân cảnh đã chia (giữ nguyên thông số đọc plan; action savePlan
  // chụp snapshot trước khi ghi nên khôi phục được) và xóa tiến độ tự
  // động đã lưu + trạng thái trong phiên, để nút chạy về "▶ Tạo video
  // tự động" thay vì "Tiếp tục từ bước còn thiếu". Mỗi nội dung kịch
  // bản chỉ reset một lần (khóa theo chính nội dung đã chuẩn hóa);
  // đang chạy thì không reset giữa chừng — runPipeline tự tách lại ở
  // bước tách cảnh nếu gặp plan lệch.
  const staleResetKeyRef = useRef<string | null>(null);
  useEffect(() => {
    if (!planStale || running) return;
    const key = normalizeScriptText(detail.scriptContent);
    if (staleResetKeyRef.current === key) return;
    staleResetKeyRef.current = key;
    interactedRef.current = true;
    hydratedRef.current = true;
    setStatuses({});
    setNeedsManual([]);
    setMessages(["Kịch bản đã thay đổi so với nội dung ở phân cảnh — đã reset các phân cảnh đã chia và tiến độ tự động cũ. Bấm Tạo video tự động để tách lại từ kịch bản hiện tại."]);
    if (!detail.plan) return;
    void (async () => {
      try {
        // Đọc lại bản mới nhất trước khi ghi: nếu trong lúc chờ mà
        // người dùng vừa bấm Tách tay (plan mới đã khớp kịch bản) thì
        // không reset nữa — tránh xóa nhầm phân cảnh vừa tách xong.
        const fresh = await api.getProject({ projectId });
        if (fresh.plan && fresh.plan.scenes.length > 0 && !scriptMatchesPlan(fresh)) {
          await api.savePlan({ projectId, plan: { pauseAfterMs: fresh.plan.pauseAfterMs, speed: fresh.plan.speed, voice: fresh.plan.voice, bgm: fresh.plan.bgm, scenes: [] } });
        }
        await api.saveAutoProgress({ projectId, statuses: {}, messages: [], needsManual: [] });
      } catch { /* reset lỗi thì runPipeline vẫn tự tách lại khi chạy */ }
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [planStale, running, detail.scriptContent, detail.plan, projectId]);

  async function runJobStep(step: "tts" | "normalize" | "karaoke" | "preflight" | "render" | "genimages" | "export"): Promise<void> {
    const r = await api.startJob({ projectId, step, force: false });
    currentJobRef.current = r.job.id;
    for (;;) {
      if (cancelledRef.current) throw new Error("__cancelled__");
      const s = await api.getJobStatus({ jobId: r.job.id });
      if (s.job.status === "done") { currentJobRef.current = null; return; }
      if (s.job.status === "error") { currentJobRef.current = null; throw new Error(`${JOB_LABELS[step] ?? step} lỗi (mã ${s.job.exitCode ?? "?"}). ${s.job.logTail ? s.job.logTail.slice(-500) : ""}`); }
      await sleep(3000);
    }
  }

  // Giai đoạn 1 của bước media (luật hàng chờ AI, CEO 03/11): hàm này
  // CHỈ xác định media bằng tìm kiếm (Wikimedia rồi stock) — tìm được
  // file đạt thì gắn ngay và trả true; cả hai lớp đều không có thì trả
  // false và caller đưa mục đó vào HÀNG CHỜ tạo AI, rồi đi xác định
  // tiếp cảnh/part sau, KHÔNG tạo AI ngay tại chỗ như trước.
  async function searchMediaForTarget(args: { sceneOrder: number; partId: string | null; summary: string; prompt: string; label: string; mediaType: "image" | "video" }): Promise<boolean> {
    // Ngưỡng điểm tối thiểu cho ứng viên tự động (giai đoạn 1, 03/11):
    // thang điểm của công cụ tìm là 0–100 và chính nó chỉ coi ứng viên
    // là "xem xét được" (CONSIDER_TOP) từ 50 điểm — trước đây app lấy
    // luôn ứng viên điểm cao nhất kể cả 5–10 điểm, gắn nhầm media kém
    // liên quan mà không nói lý do. Dưới ngưỡng thì loại kèm lý do rõ.
    const MIN_AUTO_SCORE = 50;
    let enKeywords = "";
    try {
      const sug = await api.suggestKeywords({ summary: args.summary });
      if (!sug.noCluster) enKeywords = sug.enPhrases.join(", ");
    } catch { /* gợi ý lỗi thì vẫn thử tìm trực tiếp */ }
    const layers: Array<"wikimedia" | "stock"> = ["wikimedia", "stock"];
    const reasons: string[] = [];
    for (const layer of layers) {
      if (cancelledRef.current) throw new Error("__cancelled__");
      const layerName = layer === "wikimedia" ? "Wikipedia/Wikimedia" : "stock";
      if (layer === "stock" && !enKeywords.trim()) {
        reasons.push("stock: bỏ qua vì không suy ra được từ khóa tiếng Anh từ tóm tắt");
        continue;
      }
      try {
        const res = await api.searchMedia({ layer, summary: args.summary, enKeywords, extraKeywords: "", mediaType: args.mediaType, durationSec: 0 });
        const sorted = [...res.candidates].sort((a, b) => (b.score ?? -1) - (a.score ?? -1));
        const best = sorted[0];
        if (best && (best.score ?? -1) >= MIN_AUTO_SCORE) {
          const others = sorted.slice(1).map((x) => x.score).filter((x): x is number => x !== null);
          await api.pickMedia({ projectId, sceneOrder: args.sceneOrder, partId: args.partId, fileUrl: best.fileUrl, mediaType: args.mediaType, source: best.source, pageUrl: best.pageUrl, license: best.license, author: best.author, score: best.score, verdict: best.verdict, runnerUpScore: others.length ? Math.max(...others) : null });
          setMessages((m) => [...m, `Đã tự tìm được media cho ${args.label} ở lớp ${layerName}: ${best.title} (điểm ${best.score})`]);
          return true;
        }
        reasons.push(
          best
            ? `${layerName}: ứng viên tốt nhất chỉ đạt ${best.score ?? "?"} điểm, dưới ngưỡng ${MIN_AUTO_SCORE} nên loại`
            : `${layerName}: không có ứng viên nào${res.note ? ` — ${res.note}` : ""}`,
        );
      } catch (e) {
        // Không nuốt lỗi lặng lẽ như trước: ghi rõ lớp nào lỗi vì sao để
        // người dùng biết đường xử lý tay thay vì chỉ thấy "không đạt".
        reasons.push(`${layerName}: lỗi khi tìm — ${String(e).slice(0, 200)}`);
      }
    }
    setMessages((m) => [...m, `${args.label}: tìm kiếm không có file đạt. ${reasons.join("; ")}.`]);
    return false;
  }

  // R4-62 (08/11/2026, DEC-070 A): AutoPanel cũng phải hỏi trước khi
  // ghi đè như thao tác tay (B23) — plan có thể ghi trống nhưng đĩa
  // vẫn còn file thật (lệch plan/đĩa, xem R4-25/R4-26). Hỏi 1 lần cho
  // mỗi mục sắp ghi đè, ngay lúc chọn mục (chạy tuần tự) chứ không hỏi
  // trong hàng chờ AI chạy song song; user từ chối thì trả false để
  // caller bỏ qua mục đó và đưa vào danh sách cần xử lý tay.
  const confirmOverwriteTarget = (
    lib: Array<{ slot: string; sceneOrder: number | null; partId: string | null }>,
    sceneOrder: number,
    partId: string | null,
    label: string,
  ): boolean => {
    const onDisk = lib.some((i) =>
      partId === null
        ? i.slot === "scene" && i.sceneOrder === sceneOrder
        : i.slot === "broll" && i.partId === partId,
    );
    if (!onDisk) return true;
    return window.confirm(
      `${label} đã có file trên đĩa (plan ghi trống — lệch plan/đĩa). Tạo video tự động sẽ ghi đè file đó. Tiếp tục?`,
    );
  };

  // Giai đoạn 2: tạo media bằng AI cho MỘT mục trong hàng chờ. Việc
  // chậm nằm cả ở phía server (công cụ tạo media); ghi plan đã được
  // server khóa theo project nên nhiều luồng gọi đồng thời vẫn an toàn.
  async function generateAiForTarget(args: { sceneOrder: number; partId: string | null; summary: string; prompt: string; label: string; mediaType: "image" | "video" }): Promise<boolean> {
    const aiPrompt = args.prompt.trim() || args.summary;
    if (!aiPrompt) return false;
    try {
      const r = await api.generateAiMedia({ projectId, sceneOrder: args.sceneOrder, partId: args.partId, prompt: aiPrompt, mediaType: args.mediaType });
      setMessages((m) => [...m, `Đã tạo media bằng AI cho ${args.label}: ${r.fileName}.`]);
      return true;
    } catch (e) {
      setMessages((m) => [...m, `Tạo AI cho ${args.label} thất bại: ${String(e).slice(0, 200)} — mục này cần xử lý tay.`]);
    }
    return false;
  }

  // Điểm 2: bước gắn template/SFX của luồng tự động. Đầu ra được làm rõ
  // bằng luật cứng, mọi chữ/số trên thẻ đều trích nguyên từ lời đọc của
  // chính part đó (không bịa): beat preview (part đầu của cảnh 2) gắn
  // preview-banner với nguyên câu preview; part có đúng một con số nổi
  // bật gắn stat-counter (tối đa 3) hoặc keyword-block; part đã có
  // template/SFX (dàn tay) thì giữ nguyên. SFX lấy đúng SFX gợi ý trong
  // meta của template; beat cấu trúc hook / móc lại ~50% / kết luận còn
  // thiếu SFX thì gắn whoosh_fast. Tổng SFX sau khi gắn không vượt
  // khung 7 của video 180–300s. Trả về các ghi chú để panel báo lại.
  async function attachTemplatesAndSfx(plan: Plan): Promise<string[]> {
    const notes: string[] = [];
    let catalogs: Catalogs;
    try {
      catalogs = await api.getCatalogs({});
    } catch {
      return ["Không đọc được danh mục template/SFX nên bỏ qua bước gắn tự động — dàn tay ở bước 2 · Phân cảnh & template nếu cần beat nhấn."];
    }
    const templates = catalogs.templates;
    const sfxIds = new Set(catalogs.sfx.map((s) => s.id));
    const next: Plan = structuredClone(plan);
    const flat: Part[] = [];
    for (const s of next.scenes) for (const p of s.parts) flat.push(p);
    if (flat.length === 0) return ["Plan chưa có part nào để gắn template/SFX."];
    const existingSfx = flat.filter((p) => p.broll?.sfx).length;
    let sfxBudget = Math.max(0, 7 - existingSfx);
    const attached: string[] = [];
    const setTemplate = (part: Part, templateId: string, inputs: Record<string, string>): boolean => {
      const tpl = templates.find((t) => t.id === templateId);
      if (!tpl || part.broll?.templateId) return false;
      const b = { ...(part.broll ?? {}) };
      b.templateId = templateId;
      b.inputs = inputs;
      if (tpl.sfxId && sfxIds.has(tpl.sfxId) && !b.sfx && sfxBudget > 0) {
        b.sfx = { id: tpl.sfxId, offsetSec: 0, volume: tpl.sfxVolume ?? (tpl.sfxId === "heavy_thud_slam" || tpl.sfxId === "boom_sub_impact" ? 0.35 : 0.65) };
        sfxBudget -= 1;
      }
      part.broll = b;
      attached.push(`${templateId} → ${part.id}`);
      return true;
    };
    // Beat preview: part đầu tiên của cảnh thứ hai (sau hook), đúng vị
    // trí luật cấu trúc 3 nhịp mở đầu đặt beat giới thiệu sơ bộ.
    const scene2 = next.scenes.length >= 2 ? next.scenes[1] : undefined;
    const previewPart = scene2?.parts[0];
    if (previewPart && !previewPart.broll?.templateId) {
      const full = previewPart.voiceText.trim();
      const firstSentence = full.split(/(?<=[.!?…])\s+/)[0] ?? full;
      const text = full.length <= 160 ? full : firstSentence.length <= 160 ? firstSentence : "";
      if (text) setTemplate(previewPart, "preview-banner", { text });
      else notes.push(`Beat preview (${previewPart.id}) có câu dài quá 160 ký tự nên không gắn preview-banner — rút ngắn tay ở bước 2 nếu muốn banner preview.`);
    }
    // Thẻ số liệu cho part có đúng một con số nổi bật (tối đa 3 thẻ).
    let statCount = 0;
    for (const part of flat) {
      if (statCount >= 3 || sfxBudget <= 0) break;
      if (part.broll?.templateId || part === previewPart) continue;
      const stat = findStatPhrase(part.voiceText);
      if (stat) {
        if (setTemplate(part, "stat-counter", { value: stat.value, unit: stat.unit })) statCount += 1;
      }
    }
    // Khối từ khóa cho các part còn lại có cụm số (template này không có
    // SFX gợi ý nên không ăn vào khung SFX), giữ mật độ template ≤ 50%.
    let templated = flat.filter((p) => p.broll?.templateId).length;
    for (const part of flat) {
      if (templated / flat.length > 0.5) break;
      if (part.broll?.templateId || part === previewPart) continue;
      const stat = findStatPhrase(part.voiceText);
      if (stat && setTemplate(part, "keyword-block", { keyword: stat.phrase.toUpperCase() })) templated += 1;
    }
    // SFX cho beat cấu trúc còn thiếu: hook (part đầu), móc lại (part
    // ~50%), kết luận (part cuối).
    const beatIdx = [...new Set([0, Math.floor(flat.length / 2), flat.length - 1])];
    const uncovered: string[] = [];
    for (const idx of beatIdx) {
      const part = flat[idx];
      if (!part || part.broll?.sfx) continue;
      if (sfxIds.has("whoosh_fast") && sfxBudget > 0) {
        part.broll = { ...(part.broll ?? {}), sfx: { id: "whoosh_fast", offsetSec: 0, volume: 0.6 } };
        sfxBudget -= 1;
        attached.push(`SFX whoosh_fast → ${part.id} (beat cấu trúc)`);
      } else uncovered.push(part.id);
    }
    const changed = JSON.stringify(next) !== JSON.stringify(plan);
    if (changed) {
      const res = await api.savePlan({ projectId, plan: next });
      if (res.problems.length > 0) notes.push(`Plan sau khi gắn template/SFX có vấn đề: ${res.problems.join("; ")} — kiểm tra ở bước 2.`);
    }
    const totalSfx = flat.filter((p) => p.broll?.sfx).length;
    if (attached.length > 0) notes.push(`Template/SFX tự động đã gắn: ${attached.join("; ")}. Tổng SFX trong plan: ${totalSfx} (khung 3–7 cho video 180–300s). Chữ/số trên thẻ trích nguyên từ lời đọc của part; part đã dàn tay được giữ nguyên — kiểm tra/sửa ở bước 2 · Phân cảnh & template.`);
    else notes.push("Template/SFX: không gắn thêm gì — plan đã có sẵn template/SFX hoặc không trích được beat số liệu rõ ràng từ kịch bản. Đầu ra tự động vì vậy dùng ảnh/b-roll thường ở các beat chưa có template; cần thẻ nhấn thì gắn tay ở bước 2.");
    if (uncovered.length > 0) notes.push(`Beat cấu trúc chưa có SFX (đã chạm khung 7 SFX hoặc thiếu file whoosh_fast): ${uncovered.join(", ")} — gắn tay ở bước 2 nếu cần.`);
    return notes;
  }

  async function runPipeline() {
    if (running) return;
    interactedRef.current = true;
    cancelledRef.current = false;
    setStarted(true);
    setRunning(true);
    setMessages([]);
    setNeedsManual([]);
    try {
      // 1) Kịch bản: KHÔNG sinh ở đây — sinh kịch bản AI đã có ở Cách A
      // phía trên. Panel chỉ tái sử dụng kịch bản đã có: ô Toàn văn của
      // Cách B đang giữ bản KHÁC bản đã lưu (vừa sửa mà sự kiện lưu khi
      // mất focus chưa kịp ghi xong, hoặc bản AI nháp chưa từng được
      // focus) thì lưu đúng bản đang soạn rồi chạy tiếp, để pipeline
      // luôn chạy trên kịch bản người dùng đang thấy; chưa có kịch bản
      // nào thì dừng và chỉ rõ chỗ làm kịch bản, không nhập lại form
      // sự kiện ở đây.
      let cur = await api.getProject({ projectId });
      const draftRaw = unsavedScript ? unsavedScript() : null;
      if (draftRaw !== null && draftRaw !== cur.scriptContent) {
        await api.saveScript({ projectId, content: draftRaw, topic: unsavedTopic?.() || cur.scriptTopic || cur.input.topic });
        setMessages((m) => [...m, "Đã lưu kịch bản đang soạn ở Cách B phía trên rồi chạy tiếp."]);
        cur = await api.getProject({ projectId });
      }
      if (!cur.scriptContent.trim()) {
        setMessages((m) => [...m, "Chưa có kịch bản nên chưa chạy tự động được. Làm kịch bản trước ngay phía trên: sinh bằng AI ở mục Cách A — Viết bằng AI từ sự kiện đã kiểm chứng, hoặc viết/dán vào ô Toàn văn của Cách B (app tự lưu khi bấm ra ngoài ô) — xong quay lại bấm Tạo video tự động, app dùng luôn kịch bản đó."]);
        return;
      }
      // 2) Tách cảnh/part — chỉ dùng lại phân cảnh đã chia khi nội
      // dung của chúng còn khớp kịch bản hiện tại; kịch bản đã đổi thì
      // reset và tách lại từ đầu (luật CEO 03/11), không "bỏ qua" như
      // trước nữa.
      const planStaleNow = !!cur.plan && cur.plan.scenes.length > 0 && !scriptMatchesPlan(cur);
      if (!cur.plan || cur.plan.scenes.length === 0 || planStaleNow) {
        setSt("split", "running");
        if (planStaleNow) {
          setMessages((m) => [...m, "Kịch bản đã thay đổi so với nội dung ở phân cảnh — đã reset các phân cảnh đã chia và tách lại từ kịch bản hiện tại."]);
          // Tiến độ cũ thuộc về kịch bản cũ: xóa trạng thái các bước
          // sau bước tách để lần chạy này đi từ đầu, không "tiếp tục".
          setStatuses((prev) => Object.fromEntries(Object.entries(prev).filter(([k]) => k === "split")));
          setNeedsManual([]);
        }
        const scenes = splitScriptToScenes(cur.scriptContent);
        const res = await api.savePlan({ projectId, plan: { pauseAfterMs: cur.plan?.pauseAfterMs ?? 180, speed: cur.plan?.speed ?? 1.0, voice: cur.plan?.voice ?? "Hữu Quân", bgm: cur.plan?.bgm, scenes } });
        if (res.problems.length > 0) setMessages((m) => [...m, `Plan sau khi tách có vấn đề: ${res.problems.join("; ")} — kiểm tra ở chế độ sửa tay nâng cao.`]);
        setMessages((m) => [...m, "Đã tách cảnh/part; tóm tắt cảnh, prompt ảnh và tóm tắt b-roll của từng part được điền sẵn bản nháp từ chính nội dung kịch bản — kiểm tra/sửa ở bước 2 nếu cần."]);
        setSt("split", "done");
      } else setSt("split", "skipped");
      // 2b) Gắn template/SFX ở beat nhấn (điểm 2 — đầu ra làm rõ bằng
      // luật cứng, báo lại đúng những gì đã gắn trong thông báo bước).
      setSt("templates", "running");
      cur = await api.getProject({ projectId });
      if (cur.plan && cur.plan.scenes.length > 0) {
        const notes = await attachTemplatesAndSfx(cur.plan);
        notes.forEach((n) => setMessages((m) => [...m, n]));
        setSt("templates", "done");
      } else setSt("templates", "skipped");
      // 3) Media hai giai đoạn (luật hàng chờ AI, CEO 03/11):
      // Giai đoạn 1 — xác định media cho TỪNG cảnh/part bằng tìm kiếm;
      // mục nào xác định cần tạo bằng AI thì đưa vào hàng chờ rồi đi
      // tiếp cảnh/part sau, không dừng lại tạo ngay. Giai đoạn 2 — sau
      // khi xác định xong toàn bộ, tạo AI hàng loạt cho hàng chờ, chạy
      // tối đa 4 luồng cùng lúc.
      setSt("media", "running");
      cur = await api.getProject({ projectId });
      const failures: string[] = [];
      const skippedParts: string[] = [];
      type MediaNeed = { sceneOrder: number; partId: string | null; summary: string; prompt: string; label: string; failLabel: string; mediaType: "image" | "video" };
      const aiQueue: MediaNeed[] = [];
      for (const scene of cur.plan?.scenes ?? []) {
        if (cancelledRef.current) throw new Error("__cancelled__");
        // A21 (05/11/2026): cảnh nền rêu vẫn tính là thiếu ảnh thật nên
        // luồng tự động cũng tìm media thật cho nó.
        if (!scene.imageFile || scene.isMossGrid) {
          const summary = scene.sceneScriptSummary || scene.text || "";
          if (!summary && !scene.sceneImagePrompt) { failures.push(`Cảnh ${scene.order} (chưa có tóm tắt/prompt để tìm media)`); continue; }
          const need: MediaNeed = { sceneOrder: scene.order, partId: null, summary: summary || scene.sceneImagePrompt, prompt: scene.sceneImagePrompt, label: `cảnh ${scene.order}`, failLabel: `Cảnh ${scene.order}`, mediaType: "image" };
          // R4-62 (08/11/2026, DEC-070 A): hỏi trước khi ghi đè nếu đĩa
          // còn file (plan ghi trống) — từ chối thì bỏ qua mục này.
          if (!confirmOverwriteTarget(cur.mediaLibrary ?? [], scene.order, null, `Cảnh ${scene.order}`)) {
            failures.push(`Cảnh ${scene.order} (đã có file trên đĩa, user không đồng ý ghi đè)`);
            setMessages((m) => [...m, `Cảnh ${scene.order}: đã có file trên đĩa nhưng plan ghi trống — đã hỏi và user không đồng ý ghi đè, bỏ qua mục này, xử lý tay ở tab Media.`]);
          } else {
            const found = await searchMediaForTarget(need);
            if (!found) {
              aiQueue.push(need);
              setMessages((m) => [...m, `${need.failLabel}: tìm kiếm không có file đạt — đưa vào hàng chờ tạo bằng AI, tiếp tục xác định cảnh/part tiếp theo.`]);
            }
          }
        }
        for (const part of scene.parts) {
          if (cancelledRef.current) throw new Error("__cancelled__");
          const want = part.broll?.prompt || part.broll?.scriptSummary;
          if (want && !part.broll?.file) {
            // Dạng media lấy từ chính plan của part (giai đoạn 1,
            // 03/11): trước đây hard-code "image" nên pipeline tự động
            // không bao giờ tìm/tạo được b-roll VIDEO dù plan ghi rõ
            // mediaType video và tab Media tay có chọn video.
            const need: MediaNeed = { sceneOrder: scene.order, partId: part.id, summary: part.broll?.scriptSummary || part.voiceText, prompt: part.broll?.prompt ?? "", label: `b-roll ${part.id}`, failLabel: `B-roll ${part.id}`, mediaType: part.broll?.mediaType === "video" ? "video" : "image" };
            // R4-62 (08/11/2026, DEC-070 A): hỏi trước khi ghi đè nếu
            // đĩa còn file (plan ghi trống) — từ chối thì bỏ qua mục này.
            if (!confirmOverwriteTarget(cur.mediaLibrary ?? [], scene.order, part.id, `B-roll ${part.id}`)) {
              failures.push(`B-roll ${part.id} (đã có file trên đĩa, user không đồng ý ghi đè)`);
              setMessages((m) => [...m, `B-roll ${part.id}: đã có file trên đĩa nhưng plan ghi trống — đã hỏi và user không đồng ý ghi đè, bỏ qua mục này, xử lý tay ở tab Media.`]);
            } else {
              const found = await searchMediaForTarget(need);
              if (!found) {
                aiQueue.push(need);
                setMessages((m) => [...m, `${need.failLabel}: tìm kiếm không có file đạt — đưa vào hàng chờ tạo bằng AI, tiếp tục xác định cảnh/part tiếp theo.`]);
              }
            }
          } else if (!want && !part.broll?.file) {
            // Không bỏ qua lặng lẽ như trước: ghi lại để báo rõ ở dưới —
            // part này sẽ dùng ảnh của cảnh, không có b-roll riêng.
            skippedParts.push(part.id);
          }
        }
      }
      // Giai đoạn 2: xả hàng chờ tạo AI — tối đa 4 luồng cùng lúc, mỗi
      // luồng lấy mục kế tiếp trong hàng chờ cho tới khi hết; mục nào
      // tạo lỗi thì ghi vào danh sách cần xử lý tay, không chặn các
      // mục còn lại.
      if (aiQueue.length > 0) {
        if (cancelledRef.current) throw new Error("__cancelled__");
        setMessages((m) => [...m, `Đã xác định xong media cho mọi cảnh/part — bắt đầu tạo bằng AI cho ${aiQueue.length} mục trong hàng chờ, chạy tối đa 4 luồng cùng lúc.`]);
        let cursor = 0;
        let doneAi = 0;
        const worker = async (): Promise<void> => {
          for (;;) {
            if (cancelledRef.current) return;
            const idx = cursor;
            cursor += 1;
            const need = aiQueue[idx];
            if (!need) return;
            const ok = await generateAiForTarget(need);
            doneAi += 1;
            if (!ok) failures.push(need.failLabel);
            setMessages((m) => [...m, `Hàng chờ tạo AI: đã xử lý ${doneAi}/${aiQueue.length} mục.`]);
          }
        };
        await Promise.all(Array.from({ length: Math.min(4, aiQueue.length) }, () => worker()));
        if (cancelledRef.current) throw new Error("__cancelled__");
        const failedAi = aiQueue.filter((n) => failures.includes(n.failLabel)).length;
        setMessages((m) => [...m, failedAi > 0
          ? `Tạo AI hàng loạt xong: ${aiQueue.length - failedAi}/${aiQueue.length} mục thành công, ${failedAi} mục tạo lỗi (liệt kê ở danh sách cần xử lý tay bên dưới).`
          : `Tạo AI hàng loạt xong: cả ${aiQueue.length} mục trong hàng chờ đều đã có media.`]);
      }
      if (skippedParts.length > 0) {
        setMessages((m) => [...m, `Không tìm b-roll riêng cho ${skippedParts.length} part vì chưa có prompt/tóm tắt b-roll (${skippedParts.join(", ")}) — các part này dùng ảnh của cảnh. Muốn có b-roll riêng: điền prompt/tóm tắt ở bước 2 · Phân cảnh rồi chạy lại, app chỉ tìm cho các part còn thiếu.`]);
      }
      // Dự phòng: job tạo ảnh cảnh của nhà máy cho cảnh vẫn thiếu (card chữ/prompt AI)
      cur = await api.getProject({ projectId });
      if ((cur.plan?.scenes ?? []).some((s) => !s.imageFile)) {
        try { await runJobStep("genimages"); } catch { /* lỗi được phản ánh ở lần kiểm tra dưới đây */ }
        cur = await api.getProject({ projectId });
      }
      const stillMissing = (cur.plan?.scenes ?? []).filter((s) => !s.imageFile).map((s) => `Cảnh ${s.order}`);
      const allFailures = [...new Set([...failures, ...stillMissing])];
      if (allFailures.length > 0) {
        setSt("media", "error");
        setNeedsManual(allFailures);
        setMessages((m) => [...m, `Dừng ở bước Media: ${allFailures.join(", ")} không có ứng viên đạt ở cả Wikimedia, stock lẫn AI. Xử lý tay các mục này ở bước 3 · Media rồi bấm Tiếp tục — app sẽ chạy tiếp từ đúng bước này, không làm lại từ đầu.`]);
        onNavigate("media");
        return;
      }
      setSt("media", "done");
      // 4) TTS -> chuẩn hóa -> karaoke -> preflight
      const audioSteps: Array<["tts" | "normalize" | "karaoke" | "preflight", TabKey]> = [["tts", "audio"], ["normalize", "audio"], ["karaoke", "audio"], ["preflight", "audio"]];
      for (const [step] of audioSteps) {
        if (cancelledRef.current) throw new Error("__cancelled__");
        setSt(step, "running");
        try { await runJobStep(step); setSt(step, "done"); }
        catch (e) {
          if (String(e).includes("__cancelled__")) throw e;
          setSt(step, "error");
          setMessages((m) => [...m, `Dừng ở bước ${JOB_LABELS[step] ?? step}: ${String(e)}`]);
          onNavigate("audio");
          return;
        }
      }
      // 5) Kiểm tra Preview — chặn nền đen
      setSt("preview", "running");
      const previewData = await api.getPreviewData({ projectId });
      const missingParts = previewData.parts.filter((p) => !p.image && !p.videoFile);
      if (missingParts.length > 0) {
        setSt("preview", "error");
        setMessages((m) => [...m, `Chặn render: ${missingParts.length} part chưa có ảnh (${missingParts.map((p) => p.id).join(", ")}) — render lúc này sẽ ra nền đen ở các part đó. Bổ sung media ở bước 3 rồi bấm Tiếp tục.`]);
        onNavigate("preview");
        return;
      }
      setSt("preview", "done");
      // 6) Render + xuất ZIP
      setSt("render", "running");
      try { await runJobStep("render"); setSt("render", "done"); }
      catch (e) {
        if (String(e).includes("__cancelled__")) throw e;
        setSt("render", "error");
        setMessages((m) => [...m, `Render lỗi: ${String(e)}`]);
        onNavigate("finish");
        return;
      }
      setSt("export", "running");
      try { await runJobStep("export"); setSt("export", "done"); }
      catch (e) {
        if (String(e).includes("__cancelled__")) throw e;
        setSt("export", "error");
        setMessages((m) => [...m, `Xuất ZIP lỗi: ${String(e)} — video đã render xong, xuất lại ở bước 6.`]);
        onNavigate("finish");
        return;
      }
      setMessages((m) => [...m, "Hoàn tất: video đã render và ZIP đã xuất. Xem video ở bước 6 · Render & Xuất file."]);
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      onNavigate("finish");
    } catch (e) {
      if (String(e).includes("__cancelled__")) {
        setMessages((m) => [...m, "Đã hủy chạy tự động. Các bước đã xong vẫn được giữ — bấm Tiếp tục để chạy tiếp từ bước còn thiếu."]);
        setStatuses((prev) => Object.fromEntries(Object.entries(prev).map(([k, v]) => [k, v === "running" ? "pending" : v])));
      } else {
        setMessages((m) => [...m, `Chạy tự động dừng do lỗi: ${String(e)}`]);
      }
    } finally {
      setRunning(false);
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    }
  }

  async function cancelPipeline() {
    cancelledRef.current = true;
    const jobId = currentJobRef.current;
    if (jobId) {
      try { await api.cancelJob({ jobId }); } catch { /* job có thể đã xong */ }
    }
  }

  // Gọn giao diện: tiến trình (thanh %, chip 10 bước, thông báo) chỉ
  // hiện khi người dùng đã bấm nút trong phiên này hoặc đang chạy —
  // không hiện vì có bản lưu cũ, có thông báo cũ hay có bước đã xong.
  const showProgress = started || running;

  return (
    <div id="auto-panel" className="mt-4" aria-label="Tạo video tự động">
      {complete && !running && (
        <div className="mb-2">
          <span className="rounded-full bg-[var(--surface2)] px-2 py-0.5 text-xs font-semibold" style={{ color: "var(--ok)" }}>Đã đủ 6 bước — có video + ZIP</span>
        </div>
      )}
      {showProgress && (
      <>
      <div className="mt-3 h-3 w-full overflow-hidden rounded-full bg-[var(--surface2)]" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100} aria-label="Tiến độ tạo video tự động">
        <div className="h-full transition-all" style={{ width: `${pct}%`, background: "var(--accent)" }} />
      </div>
      <p className="mono mt-1 text-xs text-[var(--dim)]">{doneCount}/{AUTO_STEPS.length} bước · {pct}%</p>
      <ol className="mt-2 flex flex-wrap gap-1.5">
        {AUTO_STEPS.map((s) => {
          const st = statuses[s.key] ?? "pending";
          return (
            <li key={s.key} className="rounded-full px-2 py-0.5 text-[11px] font-semibold" style={{ background: st === "done" ? "color-mix(in srgb, var(--ok) 18%, transparent)" : st === "error" ? "color-mix(in srgb, var(--bad) 15%, transparent)" : st === "running" ? "color-mix(in srgb, var(--warn) 20%, transparent)" : "var(--surface2)", color: st === "done" ? "var(--ok)" : st === "error" ? "var(--bad)" : st === "running" ? "var(--warn)" : "var(--dim)" }}>
              {st === "done" ? "●" : st === "error" ? "✕" : st === "running" ? "…" : "○"} {s.label}{st === "skipped" ? " (đã có sẵn)" : ""}
            </li>
          );
        })}
      </ol>
      </>
      )}
      {complete && !rerunArmed && !running ? (
        <div className="mt-3">
          {!confirmRerun ? (
            <button type="button" className={btnCls} style={{ color: "var(--warn)", borderColor: "var(--warn)" }} onClick={() => setConfirmRerun(true)} aria-label="Chạy lại từ đầu, ghi đè video và ZIP hiện tại">
              Chạy lại từ đầu (ghi đè video + ZIP)…
            </button>
          ) : (
            <div className="mt-2 flex flex-wrap items-center gap-2 rounded-lg border p-3" style={{ borderColor: "var(--warn)", background: "color-mix(in srgb, var(--warn) 8%, transparent)" }}>
              <span className="text-sm font-semibold">Chạy lại sẽ render video mới và xuất ZIP mới, ghi đè bản hiện tại (factory chụp snapshot trước khi render). Chắc chắn?</span>
              <button type="button" className={btnPrimary} onClick={() => { setConfirmRerun(false); setRerunArmed(true); void runPipeline(); }} aria-label="Xác nhận chạy lại từ đầu, ghi đè video và ZIP hiện tại">Xác nhận chạy lại</button>
              <button type="button" className={btnCls} onClick={() => setConfirmRerun(false)} aria-label="Thôi, giữ bản video và ZIP hiện tại">Thôi, giữ bản hiện tại</button>
            </div>
          )}
        </div>
      ) : (
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            type="button"
            className={btnCls}
            disabled={running || !effectiveHasScript}
            aria-disabled={!effectiveHasScript}
            title={!effectiveHasScript ? "Chưa có kịch bản — sinh bằng AI ở Cách A hoặc viết/dán ở ô Toàn văn phía trên trước" : undefined}
            onClick={() => void runPipeline()}
            aria-label={!effectiveHasScript ? "Tạo video tự động — chưa có kịch bản nên chưa bấm được" : "Tạo video tự động — chạy xuyên suốt các bước còn thiếu"}
          >
            {running ? "Đang chạy tự động…" : !planStale && (doneCount > 0 || needsManual.length > 0) ? "Tiếp tục từ bước còn thiếu" : "▶ Tạo video tự động"}
          </button>
          {running && (
            <button type="button" className={btnCls} onClick={() => void cancelPipeline()} aria-label="Hủy chạy tự động">Hủy</button>
          )}
          {showProgress && needsManual.length > 0 && (
            <button type="button" className={btnCls} onClick={() => onNavigate("media")} aria-label="Mở bước Media để xử lý tay các mục còn thiếu">Xử lý tay ở bước Media →</button>
          )}
        </div>
      )}
      {showProgress && messages.length > 0 && (
        <ul className="mt-3 space-y-1">
          {messages.map((m, i) => (<li key={`${i}-${m.slice(0, 30)}`} className="break-words text-sm">{m}</li>))}
        </ul>
      )}
    </div>
  );
}
