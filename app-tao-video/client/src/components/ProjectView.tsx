// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { btnCls, btnPrimary, firstIncompleteTab, fmtSec, pollWhenVisible } from "../lib";
import { AudioTab } from "./AudioTab";
import { FinishTab } from "./FinishTab";
import { InfoTip } from "./InfoTip";
import { MediaTab } from "./MediaTab";
import { PreviewTab } from "./PreviewTab";
import { ScenesTab } from "./ScenesTab";
import { ScriptTab } from "./ScriptTab";
import { StepStrip } from "./shared";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import type { TabKey } from "../lib";

export function ProjectView({ projectId, onBack }: { projectId: string; onBack: () => void }) {
  const [tab, setTab] = useState<TabKey>("script");
  const initialTabSetRef = useRef(false);
  const detail = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => api.getProject({ projectId }),
    refetchInterval: () => pollWhenVisible(15000),
  });
  const projects = useQuery({ queryKey: ["projects"], queryFn: () => api.listProjects({ includeTrashed: false }) });
  const catalogs = useQuery({ queryKey: ["catalogs"], queryFn: () => api.getCatalogs({}), staleTime: 600_000 });
  const summary = projects.data?.projects.find((p) => p.id === projectId);
  const d = detail.data;
  // Mở lại project thì đứng ở bước dở dang đầu tiên trong dãy tab
  // wizard (1 · Kịch bản là tab đầu tiên).
  useEffect(() => {
    if (!initialTabSetRef.current && summary && d) {
      initialTabSetRef.current = true;
      setTab(firstIncompleteTab(summary, d));
    }
  }, [summary, d]);
  const tabs: Array<{ key: TabKey; label: string }> = [
    { key: "script", label: "1 · Kịch bản" },
    { key: "scenes", label: "2 · Phân cảnh & template" },
    { key: "media", label: "3 · Media" },
    { key: "audio", label: "4 · TTS & Karaoke" },
    { key: "preview", label: "5 · Preview HTML" },
    { key: "finish", label: "6 · Render & Xuất file" },
  ];
  // Bố cục đầu trang project (luật UX 03/11, chốt cuối cùng cùng
  // ngày): hàng trên cùng là 2 cột song song trên 1 dòng — cột trái
  // nút "← Danh sách", cột phải id topic (ví dụ TOPIC-114, không in
  // cả đoạn chủ đề dài lê thê) — rồi tới tên dự án (tên mô tả video).
  // Tooltip ⓘ "Xem chi tiết project" đặt NGAY CUỐI tên dự án —
  // nằm inline trong cùng dòng chữ của tên, ngay sau từ cuối cùng,
  // không tách thành cột riêng bên cạnh tên. Mọi chi tiết còn lại
  // (đoạn chủ đề đầy đủ, mã project, số cảnh/part, thời lượng,
  // ảnh/video/SFX, karaoke, preview, giọng, BGM, lần sửa cuối)
  // không in inline nữa mà gom vào tooltip đó. StepStrip và cảnh
  // báo vẫn hiện trực tiếp vì đó là trạng thái/cảnh báo cần thấy
  // ngay, không phải chi tiết mô tả.
  const topicText = d?.input.topic || d?.scriptTopic || summary?.topic || "";
  // Id topic rút từ đúng dữ liệu đã ghi: mã "TOPIC-<số>" xuất hiện
  // trong tên project / chủ đề / chủ đề kịch bản của các project
  // pipeline (kiểm chứng: mọi project topic* đều mang mã này ở đầu
  // tên). Project không có mã topic (tạo tay, project test) thì
  // hàng id hiện chính id project — vẫn là một id ngắn gọn, không
  // phải đoạn mô tả.
  const topicId = (() => {
    for (const s of [d?.input.name, topicText, d?.scriptTopic, summary?.name, summary?.topic]) {
      const m = s?.match(/TOPIC-\d+/i);
      if (m) return m[0].toUpperCase();
    }
    const pm = projectId.match(/^topic(\d{3})/i);
    return pm ? `TOPIC-${pm[1]}` : projectId;
  })();
  const detailTip = [
    `Mã project: ${projectId}`,
    topicText && topicText !== topicId ? `Chủ đề: ${topicText}` : "",
    summary
      ? `${summary.sceneCount} cảnh · ${summary.partCount} part · ${fmtSec(summary.totalDurationSec)} · ${summary.imageCount} ảnh · ${summary.videoCount} video · ${summary.sfxCount} SFX`
      : "",
    d ? `Karaoke ${d.karaokeLineCount} dòng` : "",
    summary ? (d?.preview?.exists ? `Preview md5 ${d.preview.md5.slice(0, 10)}…` : "Chưa render") : "",
    summary?.voice ? `Giọng ${summary.voice}` : "",
    summary?.bgmId ? `BGM ${summary.bgmId}` : "",
    summary ? `Sửa ${new Date(summary.modifiedAt).toLocaleString("vi-VN")}` : "",
  ]
    .filter(Boolean)
    .join(" · ");
  return (
    <div className="mx-auto max-w-5xl px-4 pb-16 pt-4">
      <div className="flex items-center justify-between gap-3">
        <button type="button" className={`${btnCls} shrink-0`} onClick={onBack} aria-label="Quay lại danh sách project">← Danh sách</button>
        <p className="mono min-w-0 truncate text-right text-base font-bold leading-snug" aria-label={`ID topic: ${topicId}`} title={topicText || topicId}>{topicId}</p>
      </div>
      <h1 className="mt-1 min-w-0 break-words text-xl font-extrabold leading-snug [overflow-wrap:anywhere]">
        {d?.input.name ?? summary?.name ?? projectId}
        <InfoTip label="Xem chi tiết project" text={detailTip} />
      </h1>
      {summary && (
        <div className="mt-3 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3">
          <StepStrip steps={summary.steps} />
          {summary.warnings.length > 0 && (
            <ul className="mt-1 space-y-0.5">
              {summary.warnings.map((w) => (
                <li key={w} className="text-xs" style={{ color: "var(--warn)" }}>⚠ {w}</li>
              ))}
            </ul>
          )}
        </div>
      )}
      {detail.isPending && <p className="mt-4 text-[var(--dim)]">Đang đọc project từ kho thật…</p>}
      {detail.error && <p className="mt-4 text-[var(--bad)]">Không đọc được project: {String(detail.error)}</p>}
      {/* Bố cục tab wizard (luật 03/11, thay khối cố định đợt 02/11):
          Kịch bản là tab đầu tiên "1 · Kịch bản", tiếp theo là
          "2 · Phân cảnh & template" > "3 · Media" > … — mỗi bước một
          tab, chỉ tab đang chọn mới hiện nội dung. Nút Tạo video tự
          động vẫn nằm trong mục Cách B của tab Kịch bản (app tự lưu
          kịch bản khi trường nhập mất focus, tiến trình chỉ hiện sau
          khi bấm chạy). */}
      <nav className="mt-4 flex gap-1 overflow-x-auto pb-1" aria-label="Các bước làm video">
        {tabs.map((t) => (
          <button
            key={t.key}
            type="button"
            className="whitespace-nowrap rounded-lg px-3 py-2 text-sm font-semibold"
            style={{
              background: tab === t.key ? "var(--accent)" : "var(--surface2)",
              color: tab === t.key ? "var(--accent-text)" : "var(--text)",
            }}
            onClick={() => setTab(t.key)}
            aria-label={`Mở bước ${t.label}`}
            aria-current={tab === t.key ? "step" : undefined}
          >
            {t.label}
          </button>
        ))}
      </nav>
      <div className="mt-4">
        {d && tab === "script" && <ScriptTab key={d.id} detail={d} summary={summary} onNavigate={setTab} />}
        {d && tab === "scenes" && <ScenesTab key={d.id} detail={d} catalogs={catalogs.data} />}
        {d && tab === "media" && <MediaTab key={d.id} detail={d} />}
        {d && tab === "audio" && <AudioTab key={d.id} detail={d} onNavigate={setTab} />}
        {d && tab === "preview" && <PreviewTab key={d.id} detail={d} />}
        {d && tab === "finish" && <FinishTab key={d.id} detail={d} />}
      </div>
      {d && <SnapshotsPanel projectId={d.id} />}
    </div>
  );
}

// Danh sách snapshot của project (giai đoạn 2, 03/11): app tự chụp
// snapshot trước mỗi lần lưu input/kịch bản/plan và trước render, nhưng
// trước đây không có chỗ nào xem lại hay khôi phục — đĩa chỉ tăng mà
// người dùng không dùng được gì. Panel này liệt kê các bản đã chụp
// (giữ tối đa 30 bản mới nhất, phía server tự dọn bản cũ), cho khôi
// phục (trạng thái hiện tại được chụp lại trước khi ghi đè) và xóa tay.

function SnapshotsPanel({ projectId }: { projectId: string }) {
  const queryClient = useQueryClient();
  const [open, setOpen] = useState(false);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const q = useQuery({
    queryKey: ["snapshots", projectId],
    queryFn: () => api.listSnapshots({ projectId }),
    enabled: open,
  });
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["snapshots", projectId] });
    queryClient.invalidateQueries({ queryKey: ["project", projectId] });
    queryClient.invalidateQueries({ queryKey: ["projects"] });
  };
  const restore = useMutation({
    mutationFn: (snapshotId: string) => api.restoreSnapshot({ projectId, snapshotId }),
    onSuccess: () => { setConfirmId(null); invalidate(); },
  });
  const del = useMutation({
    mutationFn: (snapshotId: string) => api.deleteSnapshot({ projectId, snapshotId }),
    onSuccess: invalidate,
  });
  const items = q.data?.snapshots ?? [];
  return (
    <section className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Snapshot của project">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="font-bold">
          Snapshot đã chụp
          <InfoTip text="App tự chụp lại input, kịch bản, plan và TTS trước mỗi lần lưu và trước khi render, để có đường quay lui khi lưu nhầm. Giữ tối đa 30 bản mới nhất cho mỗi project; khôi phục một bản sẽ ghi đè các file tương ứng hiện tại (trạng thái hiện tại được chụp lại trước, nên khôi phục cũng quay lui được)." />
        </h3>
        <button type="button" className={btnCls} onClick={() => setOpen((v) => !v)} aria-expanded={open} aria-label={open ? "Đóng danh sách snapshot" : "Xem danh sách snapshot"}>
          {open ? "Đóng" : "Xem danh sách"}
        </button>
      </div>
      {open && (
        <div className="mt-3">
          {q.isPending && <p className="text-sm text-[var(--dim)]">Đang đọc danh sách snapshot…</p>}
          {q.error && <p className="text-sm text-[var(--bad)]">Không đọc được snapshot: {String(q.error)}</p>}
          {q.data && items.length === 0 && <p className="text-sm text-[var(--dim)]">Chưa có snapshot nào — app sẽ tự chụp khi bạn lưu kịch bản/plan hoặc chạy render.</p>}
          <ul className="space-y-2">
            {items.map((s) => (
              <li key={s.id} className="flex flex-wrap items-center gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface2)] px-3 py-2 text-sm">
                <span className="font-semibold">{s.kind}</span>
                <span className="text-xs text-[var(--dim)]">{new Date(s.createdAtMs).toLocaleString("vi-VN")} · {s.files.join(", ")}</span>
                <span className="flex-1" />
                {confirmId === s.id ? (
                  <>
                    <button type="button" className={btnPrimary} disabled={restore.isPending} onClick={() => restore.mutate(s.id)} aria-label={`Xác nhận khôi phục snapshot ${s.kind} lúc ${new Date(s.createdAtMs).toLocaleString("vi-VN")}`}>
                      {restore.isPending ? "Đang khôi phục…" : "Chắc chắn khôi phục"}
                    </button>
                    <button type="button" className={btnCls} onClick={() => setConfirmId(null)} aria-label="Hủy khôi phục snapshot">Hủy</button>
                  </>
                ) : (
                  <button type="button" className={btnCls} onClick={() => setConfirmId(s.id)} aria-label={`Khôi phục snapshot ${s.kind} lúc ${new Date(s.createdAtMs).toLocaleString("vi-VN")}`}>Khôi phục</button>
                )}
                <button type="button" className={btnCls} style={{ color: "var(--bad)" }} disabled={del.isPending} onClick={() => del.mutate(s.id)} aria-label={`Xóa snapshot ${s.kind} lúc ${new Date(s.createdAtMs).toLocaleString("vi-VN")}`}>Xóa</button>
              </li>
            ))}
          </ul>
          {restore.error && <p className="mt-2 text-sm text-[var(--bad)]">{String(restore.error)}</p>}
          {del.error && <p className="mt-2 text-sm text-[var(--bad)]">{String(del.error)}</p>}
        </div>
      )}
    </section>
  );
}
