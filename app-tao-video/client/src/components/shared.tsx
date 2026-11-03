// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { JOB_LABELS, STEP_DEFS, btnCls, btnPrimary, fetchMediaBlob, fmtBytes, jobStatusColor, jobStatusLabel, pollWhenVisible } from "../lib";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import type { Job, ProjectSummary } from "../lib";

export function StepStrip({ steps }: { steps: ProjectSummary["steps"] }) {
  return (
    <div className="flex max-w-full flex-wrap items-center gap-1" aria-label="Trạng thái các bước">
      {STEP_DEFS.map((s, i) => (
        <span key={s.key} className="flex items-center gap-1">
          <span
            className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-semibold"
            style={{
              background: steps[s.key] ? "color-mix(in srgb, var(--ok) 18%, transparent)" : "var(--surface2)",
              color: steps[s.key] ? "var(--ok)" : "var(--dim)",
            }}
          >
            <span aria-hidden>{steps[s.key] ? "●" : "○"}</span> {s.label}
          </span>
          {i < STEP_DEFS.length - 1 && <span className="text-[var(--dim)]">→</span>}
        </span>
      ))}
    </div>
  );
}

export function MediaFile({
  projectId,
  relPath,
  kind,
  label,
}: {
  projectId: string;
  relPath: string;
  kind: "image" | "video" | "audio";
  label: string;
}) {
  // All kinds load through the chunked Blob path (getMediaChunk), which
  // reports real progress while the chunks arrive.
  const [url, setUrl] = useState<string | null>(null);
  const [progress, setProgress] = useState<{ loaded: number; total: number } | null>(null);
  const [error, setError] = useState<string | null>(null);
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
  }, [projectId, relPath, kind]);
  if (error) {
    return <p className="text-xs text-[var(--bad)]">Không tải được {label}: {error}</p>;
  }
  if (!url) {
    return (
      <p className="text-xs text-[var(--dim)]">
        Đang tải {label}…
        {progress && progress.total > 0
          ? ` ${fmtBytes(progress.loaded)} / ${fmtBytes(progress.total)} (${Math.min(100, Math.round((progress.loaded / progress.total) * 100))}%)`
          : ""}
      </p>
    );
  }
  if (kind === "image") {
    return <img src={url} alt={label} className="max-h-64 w-full rounded-lg object-contain bg-black/30" />;
  }
  if (kind === "video") {
    return (
      <video src={url} controls muted loop playsInline aria-label={label} className="max-h-64 w-full rounded-lg bg-black/30" />
    );
  }
  return <audio src={url} controls aria-label={label} className="w-full" />;
}

export function JobRunner({
  projectId,
  step,
  label,
  forceOption,
  disabled,
  disabledReason,
  onDone,
}: {
  projectId: string;
  step: string;
  label: string;
  forceOption?: boolean;
  disabled?: boolean;
  disabledReason?: string;
  onDone?: () => void;
}) {
  const queryClient = useQueryClient();
  const [force, setForce] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const start = useMutation({
    mutationFn: () =>
      api.startJob({
        projectId,
        step: step as "tts",
        force,
      }),
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
  const doneFiredRef = useRef(false);
  useEffect(() => {
    if (job && job.status !== "running") {
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      if (job.status === "done" && onDone && !doneFiredRef.current) {
        doneFiredRef.current = true;
        onDone();
      }
    }
    if (job?.status === "running") doneFiredRef.current = false;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [job?.status, projectId, queryClient, job]);
  return (
    <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          className={btnPrimary}
          disabled={disabled || start.isPending || job?.status === "running"}
          onClick={() => start.mutate()}
          aria-label={`Chạy ${label}`}
        >
          {job?.status === "running" ? `Đang chạy ${label}…` : `Chạy ${label}`}
        </button>
        {disabled && disabledReason && (
          <span className="text-xs font-semibold" style={{ color: "var(--bad)" }}>{disabledReason}</span>
        )}
        {forceOption && (
          <label className="flex items-center gap-1 text-xs text-[var(--dim)]">
            <input type="checkbox" checked={force} onChange={(e) => setForce(e.target.checked)} aria-label={`Làm lại từ đầu ${label}`} />
            Làm lại từ đầu (force)
          </label>
        )}
        {job && (
          <span className="text-xs font-semibold" style={{ color: jobStatusColor(job) }}>
            {jobStatusLabel(job, "sentence")}
          </span>
        )}
        {job?.status === "running" && (
          <button
            type="button"
            className={btnCls}
            disabled={cancel.isPending}
            onClick={() => cancel.mutate()}
            aria-label={`Hủy ${label} đang chạy`}
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

export function JobsList({ projectId }: { projectId: string }) {
  const queryClient = useQueryClient();
  const q = useQuery({
    queryKey: ["jobs", projectId],
    queryFn: () => api.listJobs({ projectId }),
    refetchInterval: () => pollWhenVisible(8000),
  });
  const cancel = useMutation({
    mutationFn: (jobId: string) => api.cancelJob({ jobId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs", projectId] });
      queryClient.invalidateQueries({ queryKey: ["project", projectId] });
    },
  });
  if (!q.data || q.data.jobs.length === 0) return null;
  return (
    <div className="mt-3 space-y-1">
      <h4 className="text-xs font-semibold uppercase tracking-wide text-[var(--dim)]">Job gần đây</h4>
      {q.data.jobs.slice(0, 8).map((j: Job) => (
        <div key={j.id} className="flex flex-wrap items-center gap-2 text-xs">
          <span className="mono text-[var(--dim)]">{new Date(j.startedAt).toLocaleTimeString("vi-VN")}</span>
          <span className="font-semibold">{JOB_LABELS[j.step] ?? j.step}</span>
          <span style={{ color: jobStatusColor(j) }}>{jobStatusLabel(j, "short")}</span>
          {j.status === "running" && (
            <button
              type="button"
              className="rounded border border-[var(--border)] px-1.5 py-0.5 font-semibold active:opacity-70"
              disabled={cancel.isPending}
              onClick={() => cancel.mutate(j.id)}
              aria-label={`Hủy job ${JOB_LABELS[j.step] ?? j.step} đang chạy`}
            >
              Hủy job
            </button>
          )}
          {j.note && <span className="text-[var(--dim)]">{j.note}</span>}
        </div>
      ))}
      {cancel.error && <p className="text-xs text-[var(--bad)]">{String(cancel.error)}</p>}
    </div>
  );
}
