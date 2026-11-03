// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { btnCls, btnPrimary, fmtSec, inputCls, labelCls } from "../lib";
import { InfoTip } from "./InfoTip";
import { StepStrip } from "./shared";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import type { ProjectSummary } from "../lib";

function CreateProjectPanel({ onCreated }: { onCreated: (id: string) => void }) {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [topic, setTopic] = useState("");
  const create = useMutation({
    mutationFn: () =>
      api.createProject({ name: name.trim(), topic: topic.trim() }),
    onSuccess: (r) => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      onCreated(r.projectId);
    },
  });
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Tạo project mới">
      <h2 className="text-lg font-bold">
        Tạo project mới
        <InfoTip text="Chỉ cần tên và chủ đề. Tạo xong, app mở project ở tab 1 · Kịch bản — viết/sinh kịch bản xong mới tới nút Tạo video tự động trong mục Cách B của tab đó để chạy xuyên suốt tới video + ZIP, hoặc đi tiếp lần lượt qua các tab 2 · Phân cảnh, 3 · Media… để làm tay từng bước. Các thông số còn lại đã đặt mặc định sẵn: khung dọc 9:16 (720×1280, 30fps), tiếng Việt, giọng Hữu Quân, tốc độ đọc 1,0." />
      </h2>
      <div className="mt-3 grid gap-3">
        <div>
          <label className={labelCls} htmlFor="np-name">Tên project</label>
          <input id="np-name" className={inputCls} value={name} onChange={(e) => setName(e.target.value)} placeholder="Ví dụ: Đường sắt cao tốc Bắc Nam — cập nhật mới" />
        </div>
        <div>
          <label className={labelCls} htmlFor="np-topic">Chủ đề / mô tả tự do</label>
          <input id="np-topic" className={inputCls} value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Mô tả ngắn chủ đề của video" />
        </div>
        <div className="flex flex-wrap gap-2">
          <button type="button" className={btnPrimary} disabled={!name.trim() || create.isPending} onClick={() => create.mutate()} aria-label="Tạo project và mở bước Kịch bản">
            Tạo project → bắt đầu ở Kịch bản
          </button>
        </div>
        {create.error && <p className="text-sm text-[var(--bad)]">Tạo thất bại: {String(create.error)}</p>}
      </div>
    </section>
  );
}

export function ProjectList({ onOpen }: { onOpen: (id: string) => void }) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [showTrash, setShowTrash] = useState(false);
  const [confirmForever, setConfirmForever] = useState<string | null>(null);
  const q = useQuery({
    queryKey: ["projects"],
    queryFn: () => api.listProjects({ includeTrashed: false }),
  });
  const softDelete = useMutation({
    mutationFn: (p: ProjectSummary) => api.softDeleteProject({ projectId: p.id, name: p.name }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });
  const restore = useMutation({
    mutationFn: (id: string) => api.restoreProject({ projectId: id }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] }),
  });
  const forever = useMutation({
    mutationFn: (id: string) => api.deleteProjectForever({ projectId: id }),
    onSuccess: () => {
      setConfirmForever(null);
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  const filtered = (q.data?.projects ?? []).filter((p) => {
    const hay = `${p.name} ${p.id} ${p.topic}`.toLowerCase();
    return hay.includes(search.toLowerCase());
  });
  return (
    <div className="mx-auto max-w-5xl px-4 pb-16 pt-4">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="text-2xl font-extrabold">Dự án video</h1>
        <span className="mono rounded-full bg-[var(--surface2)] px-2 py-0.5 text-xs text-[var(--dim)]">
          {q.data ? `${q.data.projects.length} project trong kho thật` : "…"}
        </span>
        <div className="ml-auto flex gap-2">
          <button type="button" className={btnCls} onClick={() => setShowTrash((v) => !v)} aria-label="Mở thùng rác">
            Thùng rác ({q.data?.trashed.length ?? 0})
          </button>
          <button type="button" className={btnPrimary} onClick={() => setShowCreate((v) => !v)} aria-label="Tạo project mới">
            + Project mới
          </button>
        </div>
      </div>
      <div className="mt-3">
        <label className={labelCls} htmlFor="search-projects">Tìm theo tên, id, chủ đề</label>
        <input id="search-projects" className={inputCls} value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Tìm project…" />
      </div>
      {showCreate && (
        <div className="mt-4">
          <CreateProjectPanel onCreated={(id) => onOpen(id)} />
        </div>
      )}
      {showTrash && (
        <section className="mt-4 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Thùng rác">
          <h2 className="font-bold">Thùng rác — đã xoá, khôi phục được</h2>
          {(q.data?.trashed ?? []).length === 0 && <p className="mt-2 text-sm text-[var(--dim)]">Chưa có project nào bị xoá.</p>}
          {(q.data?.trashed ?? []).map((t) => (
            <div key={t.projectId} className="mt-2 flex flex-wrap items-center gap-2 border-t border-[var(--border)] pt-2">
              <span className="font-semibold">{t.name || t.projectId}</span>
              <span className="mono text-xs text-[var(--dim)]">{t.projectId} · xóa {new Date(t.deletedAt).toLocaleString("vi-VN")}</span>
              <span className="ml-auto flex gap-2">
                <button type="button" className={btnCls} onClick={() => restore.mutate(t.projectId)} aria-label={`Khôi phục ${t.name || t.projectId}`}>Khôi phục</button>
                {confirmForever === t.projectId ? (
                  <button type="button" className={btnCls} style={{ color: "var(--bad)" }} onClick={() => forever.mutate(t.projectId)} aria-label={`Xác nhận xóa vĩnh viễn ${t.name || t.projectId}`}>
                    Xác nhận xóa hẳn (mất cả preview và build)
                  </button>
                ) : (
                  <button type="button" className={btnCls} style={{ color: "var(--bad)" }} onClick={() => setConfirmForever(t.projectId)} aria-label={`Xóa vĩnh viễn ${t.name || t.projectId}`}>Xóa vĩnh viễn…</button>
                )}
              </span>
            </div>
          ))}
        </section>
      )}
      {q.isPending && <p className="mt-6 text-[var(--dim)]">Đang đọc kho project thật…</p>}
      {q.error && <p className="mt-6 text-[var(--bad)]">Không đọc được kho project: {String(q.error)}</p>}
      <div className="mt-4 grid gap-3">
        {filtered.map((p) => p.loadError ? (
          // Project có thư mục hỏng: hiện thành dòng lỗi rõ ràng thay vì
          // biến mất khỏi danh sách như trước (giai đoạn 2, 03/11). Vẫn
          // cho xoá vào thùng rác để dọn, nhưng không mở được.
          <article key={p.id} className="min-w-0 overflow-hidden rounded-xl border p-4" style={{ borderColor: "var(--bad)", background: "var(--surface)" }}>
            <h3 className="mono break-words text-base font-bold leading-snug [overflow-wrap:anywhere]">{p.id}</h3>
            <p className="mt-1 break-words text-sm" style={{ color: "var(--bad)" }}>{p.loadError}</p>
            <p className="mt-1 text-xs text-[var(--dim)]">Thư mục project vẫn nằm trong kho của nhà máy — kiểm tra file JSON trong thư mục đó, hoặc xoá project này nếu không còn cần.</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <button type="button" className={btnCls} style={{ color: "var(--bad)" }} onClick={() => softDelete.mutate(p)} aria-label={`Xoá project hỏng ${p.id}`}>Xoá</button>
            </div>
          </article>
        ) : (
          <article key={p.id} className="min-w-0 overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
            <div className="min-w-0">
              <h3 className="break-words text-base font-bold leading-snug [overflow-wrap:anywhere]">{p.name}</h3>
              <p className="mono mt-0.5 flex flex-wrap items-baseline gap-x-2 text-xs text-[var(--dim)]">
                <span>{p.id}</span>
                <span className="text-sm font-bold text-[var(--text)]">{fmtSec(p.totalDurationSec)}</span>
              </p>
            </div>
            <div className="mt-2">
              <StepStrip steps={p.steps} />
            </div>
            <p className="mono mt-2 break-words text-xs text-[var(--dim)] [overflow-wrap:anywhere]">
              {p.sceneCount} cảnh · {p.partCount} part · {p.imageCount} ảnh · {p.videoCount} video · {p.sfxCount} SFX
              {p.voice ? ` · giọng ${p.voice}` : ""}{p.bgmId ? ` · BGM ${p.bgmId}` : ""}
              {" · "}sửa {new Date(p.modifiedAt).toLocaleString("vi-VN")}
            </p>
            {p.warnings.length > 0 && (
              <ul className="mt-2 space-y-0.5">
                {p.warnings.slice(0, 3).map((w) => (
                  <li key={w} className="break-words text-xs" style={{ color: "var(--warn)" }}>⚠ {w}</li>
                ))}
              </ul>
            )}
            <div className="mt-3 flex flex-wrap gap-2">
              <button type="button" className={btnPrimary} onClick={() => onOpen(p.id)} aria-label={`Mở project ${p.name}`}>Mở project</button>
              <button type="button" className={btnCls} style={{ color: "var(--bad)" }} onClick={() => softDelete.mutate(p)} aria-label={`Xoá project ${p.name}`}>Xoá</button>
            </div>
          </article>
        ))}
        {q.data && filtered.length === 0 && (
          <p className="text-[var(--dim)]">Không có project nào khớp từ tìm. Kho project nằm ở thư mục projects/ của nhà máy — nếu trống thật, hãy tạo project mới.</p>
        )}
      </div>
    </div>
  );
}
