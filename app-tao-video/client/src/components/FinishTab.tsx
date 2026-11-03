// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { btnCls, btnPrimary, fetchMediaBlob, fmtBytes, fmtSec, renderBlockers } from "../lib";
import { InfoTip } from "./InfoTip";
import { JobRunner, JobsList } from "./shared";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import type { ProjectDetail } from "../lib";

function RenderedVideoPlayer({ projectId, version }: { projectId: string; version?: string }) {
  const relPath = `export/${projectId}_preview.mp4`;
  const [url, setUrl] = useState<string | null>(null);
  const [progress, setProgress] = useState<{ loaded: number; total: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [retryKey, setRetryKey] = useState(0);
  useEffect(() => {
    let cancelled = false;
    let objectUrl: string | null = null;
    setUrl(null);
    setError(null);
    setProgress(null);
    fetchMediaBlob(projectId, relPath, (loaded, total) => {
      if (!cancelled) setProgress({ loaded, total });
    })
      .then(({ blob }) => {
        if (cancelled) return;
        objectUrl = URL.createObjectURL(blob);
        setUrl(objectUrl);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(String(e));
      });
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
    // version (md5) changes after a re-render, so the player reloads the new file.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, relPath, version, retryKey]);
  if (error) {
    return (
      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface2)] p-4 text-center">
        <p className="text-sm text-[var(--bad)]">Không mở được video: {error}</p>
        <button
          type="button"
          className={`${btnCls} mt-3`}
          onClick={() => setRetryKey((v) => v + 1)}
          aria-label="Thử mở lại video"
        >
          Thử mở lại video
        </button>
      </div>
    );
  }
  if (!url) {
    return (
      <div className="flex aspect-[9/16] max-h-[72vh] w-full items-center justify-center rounded-xl bg-black/40 p-4 text-center sm:mx-auto sm:max-w-[360px]">
        <p className="text-sm text-[var(--dim)]">
          Đang mở video…
          {progress && progress.total > 0
            ? ` ${fmtBytes(progress.loaded)} / ${fmtBytes(progress.total)} (${Math.min(100, Math.round((progress.loaded / progress.total) * 100))}%)`
            : ""}
        </p>
      </div>
    );
  }
  return (
    <div className="flex justify-center">
      <video
        src={url}
        controls
        playsInline
        preload="auto"
        aria-label="Video đã render — xem ngay"
        className="max-h-[72vh] w-full max-w-[420px] rounded-xl bg-black object-contain"
      />
    </div>
  );
}

function CreateVideoRunner({ projectId, mode = "create", blockers = [] }: { projectId: string; mode?: "create" | "recreate"; blockers?: string[] }) {
  const queryClient = useQueryClient();
  const [jobId, setJobId] = useState<string | null>(null);
  const start = useMutation({
    mutationFn: () => api.startJob({ projectId, step: "render", force: false }),
    onSuccess: (r) => {
      setJobId(r.job.id);
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
    },
  });
  const status = useQuery({
    queryKey: ["jobstatus", jobId],
    queryFn: () => api.getJobStatus({ jobId: jobId as string }),
    enabled: jobId !== null,
    refetchInterval: (query) => (query.state.data?.job.status === "running" ? 4000 : false),
  });
  const job = status.data?.job;
  const cancel = useMutation({
    mutationFn: () => api.cancelJob({ jobId: jobId as string }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobstatus", jobId] });
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
    },
  });
  useEffect(() => {
    if (job && job.status !== "running") {
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
    }
  }, [job?.status, projectId, queryClient, job]);
  const isRunning = job?.status === "running" || start.isPending;
  const blocked = blockers.length > 0 && mode === "create";
  const idleLabel = mode === "recreate" ? "Tạo lại video" : "Tạo Video";
  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
      {blocked && (
        <div className="mb-3 rounded-lg bg-[color-mix(in_srgb,var(--bad)_10%,transparent)] p-3" role="alert" aria-label="Chưa đủ điều kiện tạo video">
          <p className="text-sm font-bold" style={{ color: "var(--bad)" }}>Chưa tạo video được — còn thiếu:</p>
          <ul className="mt-1 list-disc space-y-0.5 pl-5 text-sm">
            {blockers.map((b) => (<li key={b}>{b}</li>))}
          </ul>
          <p className="mt-1 text-xs text-[var(--dim)]">Bổ sung các mục trên ở các tab trước, hoặc dùng nút “Tạo video tự động” trong mục Cách B của tab 1 · Kịch bản để app tự chạy xuyên suốt các bước còn thiếu.</p>
        </div>
      )}
      <div className="flex flex-wrap items-center justify-center gap-2 sm:justify-start">
        <button
          type="button"
          className={`${btnPrimary} px-6 py-3 text-base`}
          disabled={isRunning || blocked}
          onClick={() => start.mutate()}
          aria-label={mode === "recreate" ? "Tạo lại video" : "Tạo Video"}
        >
          {isRunning ? "Đang tạo video…" : blocked ? "Chưa đủ điều kiện tạo video" : idleLabel}
        </button>
        {job && (
          <span
            className="text-xs font-semibold"
            style={{ color: job.status === "done" ? "var(--ok)" : job.status === "error" ? "var(--bad)" : "var(--warn)" }}
          >
            {job.status === "done"
              ? "Tạo video xong — video sẽ hiện ở trên để xem ngay"
              : job.status === "error"
                ? job.exitCode === -2
                  ? "Đã hủy tạo video"
                  : `Tạo video lỗi (mã ${job.exitCode ?? "?"}) — bấm Tạo Video để thử lại`
                : "Đang tạo video ở nền — cứ để đó, xong video sẽ tự hiện để xem"}
          </span>
        )}
        {job?.status === "running" && (
          <button
            type="button"
            className={btnCls}
            disabled={cancel.isPending}
            onClick={() => cancel.mutate()}
            aria-label="Hủy tạo video đang chạy"
          >
            Hủy job
          </button>
        )}
        {cancel.error && <span className="text-xs text-[var(--bad)]">{String(cancel.error)}</span>}
        {start.error && <span className="text-xs text-[var(--bad)]">{String(start.error)}</span>}
      </div>
      {job?.logTail && (
        <pre className="mono mt-2 max-h-40 overflow-auto whitespace-pre-wrap rounded bg-black/30 p-2 text-[11px] text-[var(--dim)]">
          {job.logTail.slice(-3000)}
        </pre>
      )}
    </div>
  );
}

function FilePathNote({ label, path }: { label: string; path: string }) {
  return (
    <div className="mt-2 rounded-lg border border-[var(--border)] bg-[var(--surface2)] p-3">
      <p className="text-xs font-semibold text-[var(--dim)]">{label}</p>
      <p className="mono mt-1 select-all break-all text-xs leading-relaxed text-[var(--text)] [overflow-wrap:anywhere]">
        {path}
      </p>
    </div>
  );
}

export function FinishTab({ detail }: { detail: ProjectDetail }) {
  const mp4Path = `~/workspace/vieneu-asset-factory/projects/${detail.id}/export/${detail.id}_preview.mp4`;
  const zipPath = `~/workspace/vieneu-asset-factory/projects/${detail.id}/export/${detail.id}.zip`;
  const [showRerender, setShowRerender] = useState(false);
  const hasVideo = detail.preview?.exists === true;
  return (
    <div className="grid gap-4">
      {detail.warnings.length > 0 && (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
          <h3 className="font-bold">Lưu ý kỹ thuật</h3>
          <ul className="mt-2 space-y-0.5">
            {detail.warnings.map((w) => (
              <li key={w} className="text-sm" style={{ color: "var(--warn)" }}>⚠ {w}</li>
            ))}
          </ul>
        </section>
      )}
      {hasVideo && detail.preview ? (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Video đã sẵn sàng để xem">
          <div className="flex flex-wrap items-baseline gap-2">
            <h3 className="font-bold">Video đã sẵn sàng</h3>
            <span className="mono text-xs text-[var(--dim)]">
              {fmtSec(detail.preview.durationSec)} · {detail.preview.width ?? "?"}×{detail.preview.height ?? "?"} · {fmtBytes(detail.preview.sizeBytes)} · {new Date(detail.preview.modifiedAt).toLocaleString("vi-VN")}
            </span>
          </div>
          <p className="mono mt-1 text-xs text-[var(--dim)]">md5 {detail.preview.md5}</p>
          <FilePathNote
            label="Đường dẫn file video trên máy chủ — mở đúng đường dẫn này để xem hoặc tải file khi cần:"
            path={mp4Path}
          />
          <div className="mt-3">
            <RenderedVideoPlayer projectId={detail.id} version={detail.preview.md5} />
          </div>
          <div className="mt-3 flex flex-wrap items-center gap-2">
            {!showRerender ? (
              <button
                type="button"
                className={btnCls}
                onClick={() => setShowRerender(true)}
                aria-label="Tạo lại video mới"
              >
                Tạo lại video mới
              </button>
            ) : (
              <span className="text-xs text-[var(--dim)]">Tạo lại sẽ ghi đè bản hiện tại (bản cũ được snapshot trước khi ghi đè).</span>
            )}
          </div>
          {showRerender && (
            <div className="mt-2">
              <CreateVideoRunner projectId={detail.id} mode="recreate" />
              <InfoTip label="Chú thích thời gian tạo lại video" text="Tạo video chạy nền ~9–10 phút cho video ~267 giây. Không tạo 2 video cùng lúc cho một project." />
            </div>
          )}
        </section>
      ) : (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Chưa có video — tạo video">
          <h3 className="font-bold">Chưa có video</h3>
          <p className="mt-1 text-sm text-[var(--dim)]">Project này chưa render. Bấm Tạo Video để bắt đầu — video tạo xong sẽ tự mở sẵn ở đây để xem ngay.</p>
          <FilePathNote
            label="Sau khi tạo xong, file video sẽ nằm tại đường dẫn này trên máy chủ:"
            path={mp4Path}
          />
          <div className="mt-3">
            <CreateVideoRunner projectId={detail.id} mode="create" blockers={renderBlockers(detail)} />
          </div>
          <InfoTip label="Chú thích thời gian tạo video" text="Tạo video chạy nền ~9–10 phút cho video ~267 giây (sau khi đã kiểm tra ở Preview HTML). Không tạo 2 video cùng lúc cho một project." />
        </section>
      )}
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">Xuất file</h3>
        <div className="mt-2"><JobRunner projectId={detail.id} step="export" label="xuất ZIP (assemble + schema 2.0)" /></div>
        <FilePathNote
          label={
            detail.exportZipExists
              ? "Đường dẫn file ZIP đóng gói project trên máy chủ — mở đúng đường dẫn này để xem hoặc tải file khi cần:"
              : "Chưa xuất ZIP. Sau khi bấm xuất ở trên, file ZIP đóng gói project sẽ nằm tại đường dẫn này trên máy chủ:"
          }
          path={zipPath}
        />
        {!hasVideo && (
          <p className="mt-3 text-xs text-[var(--dim)]">Chưa có MP4 — tạo video ở mục trên trước.</p>
        )}
      </section>
      <JobsList projectId={detail.id} />
    </div>
  );
}
