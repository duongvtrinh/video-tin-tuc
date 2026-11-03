// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { btnCls, btnPrimary, fmtBytes, inputCls, labelCls, provText } from "../lib";
import { InfoTip } from "./InfoTip";
import { JobRunner, MediaFile } from "./shared";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import type { Candidate, Part, ProjectDetail } from "../lib";

type LibItem = ProjectDetail["mediaLibrary"][number];
type LibCat = "ai" | "stock" | "wiki" | "web" | "unknown";

// Phân loại nguồn để lọc/badge trong thư viện. Một file có thể mang
// NHIỀU nguồn cùng lúc (ví dụ ảnh stock được AI xử lý lại): hàm này trả
// về MỌI nhóm khớp để badge hiện đủ cả hai, thay vì luật cũ "AI thắng
// hết" làm mất nhãn Stock/Wikipedia của file hỗn hợp (giai đoạn 4,
// 03/11). Thứ tự ưu tiên hiển thị: AI, stock, wiki, web; không khớp gì
// thì "unknown".
function libCategories(it: LibItem): LibCat[] {
  const s = `${it.source} ${it.urls.join(" ")}`.toLowerCase();
  const cats: LibCat[] = [];
  if (it.isAi) cats.push("ai");
  if (/stock|pexels|pixabay/.test(s)) cats.push("stock");
  if (/wikipedia|wikimedia|commons\.wikimedia/.test(s)) cats.push("wiki");
  if (cats.length === 0) {
    if (it.source === "Chưa ghi nguồn trong plan") cats.push("unknown");
    else cats.push("web");
  } else if (!cats.includes("ai") && it.source !== "Chưa ghi nguồn trong plan" && !cats.includes("stock") && !cats.includes("wiki")) {
    cats.push("web");
  }
  return cats;
}



const LIB_CAT_LABELS: Record<LibCat, string> = {
  ai: "AI",
  stock: "Stock",
  wiki: "Wikipedia/Wikimedia",
  web: "Internet · báo · Facebook",
  unknown: "Chưa rõ nguồn",
};

function LibCard({ detail, item }: { detail: ProjectDetail; item: LibItem }) {
  const [showVideo, setShowVideo] = useState(false);
  const cats = libCategories(item);
  return (
    <article className="min-w-0 rounded-lg border border-[var(--border)] bg-[var(--surface2)] p-3">
      {item.kind === "image" ? (
        <MediaFile projectId={detail.id} relPath={item.relPath} kind="image" label={`${item.partLabel}: ${item.fileName}`} />
      ) : showVideo ? (
        <MediaFile projectId={detail.id} relPath={item.relPath} kind="video" label={`${item.partLabel}: ${item.fileName}`} />
      ) : (
        <button
          type="button"
          className="flex h-32 w-full items-center justify-center rounded-lg bg-black/30 text-sm font-semibold text-[var(--text)] active:opacity-70"
          onClick={() => setShowVideo(true)}
          aria-label={`Tải và xem video ${item.fileName}`}
        >
          ▶ Xem video ({fmtBytes(item.sizeBytes)})
        </button>
      )}
      <div className="mt-2 flex flex-wrap items-center gap-1">
        <span className="rounded-full bg-[var(--surface)] px-2 py-0.5 text-[11px] font-semibold">{item.kind === "video" ? "Video" : "Ảnh"}</span>
        {cats.map((cat) => (
          <span
            key={cat}
            className="rounded-full px-2 py-0.5 text-[11px] font-semibold"
            style={{
              background: cat === "ai" ? "color-mix(in srgb, var(--accent) 22%, transparent)" : "var(--surface)",
              color: cat === "ai" ? "var(--accent)" : "var(--text)",
            }}
          >
            {LIB_CAT_LABELS[cat]}
          </span>
        ))}
        <span className="text-[11px] text-[var(--dim)]">{item.partLabel}</span>
      </div>
      <p className="mono mt-1 break-words text-[11px] text-[var(--dim)] [overflow-wrap:anywhere]">
        {item.fileName} · {fmtBytes(item.sizeBytes)}
      </p>
      <p className="mt-1 break-words text-xs">
        <span className="font-semibold">Nguồn:</span> {item.source}
      </p>
      {item.title && <p className="mt-0.5 line-clamp-2 break-words text-xs text-[var(--dim)]">{item.title}</p>}
      {item.urls.length > 0 && (
        <ul className="mt-1 space-y-0.5">
          {item.urls.map((u) => (
            <li key={u}>
              <a
                href={u}
                target="_blank"
                rel="noreferrer"
                className="break-all text-xs text-[var(--accent)] underline [overflow-wrap:anywhere]"
                aria-label={`Mở URL nguồn ${u}`}
              >
                {u}
              </a>
            </li>
          ))}
        </ul>
      )}
      {(item.license || item.author) && (
        <p className="mt-0.5 break-words text-[11px] text-[var(--dim)]">
          {item.license ? `Giấy phép: ${item.license}` : ""}
          {item.license && item.author ? " · " : ""}
          {item.author ? `Tác giả: ${item.author.replace(/<[^>]+>/g, "")}` : ""}
        </p>
      )}
      {item.isAi && item.aiPrompt && (
        <details className="mt-1">
          <summary className="cursor-pointer text-xs font-semibold text-[var(--accent)]">Prompt AI đã tạo file này</summary>
          <p className="mt-1 whitespace-pre-wrap break-words rounded bg-black/20 p-2 text-xs leading-relaxed">{item.aiPrompt}</p>
        </details>
      )}
      {item.isAi && !item.aiPrompt && (
        <p className="mt-1 text-[11px] text-[var(--dim)]">Ảnh AI nhưng plan chưa ghi lại prompt đã tạo.</p>
      )}
      {item.note && (
        <p className="mt-1 line-clamp-3 break-words text-[11px] text-[var(--dim)]" title={item.note}>
          {item.note}
        </p>
      )}
    </article>
  );
}

function MediaLibrary({ detail }: { detail: ProjectDetail }) {
  const items = detail.mediaLibrary ?? [];
  const [filter, setFilter] = useState<string>("all");
  const counts = {
    image: items.filter((i) => i.kind === "image").length,
    video: items.filter((i) => i.kind === "video").length,
    ai: items.filter((i) => libCategories(i).includes("ai")).length,
    stock: items.filter((i) => libCategories(i).includes("stock")).length,
    wiki: items.filter((i) => libCategories(i).includes("wiki")).length,
    web: items.filter((i) => libCategories(i).includes("web")).length,
    unknown: items.filter((i) => libCategories(i).includes("unknown")).length,
  };
  const visible = items.filter((i) => {
    if (filter === "all") return true;
    if (filter === "image" || filter === "video") return i.kind === filter;
    return libCategories(i).includes(filter as LibCat);
  });
  const chips: Array<{ key: string; label: string }> = [
    { key: "all", label: `Tất cả (${items.length})` },
    { key: "image", label: `Ảnh (${counts.image})` },
    { key: "video", label: `Video (${counts.video})` },
    { key: "ai", label: `AI (${counts.ai})` },
    { key: "stock", label: `Stock (${counts.stock})` },
    { key: "wiki", label: `Wikipedia/Wikimedia (${counts.wiki})` },
    { key: "web", label: `Internet · báo · Facebook (${counts.web})` },
    { key: "unknown", label: `Chưa rõ nguồn (${counts.unknown})` },
  ];
  return (
    <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Thư viện media của project">
      <h3 className="font-bold">
        Thư viện media — toàn bộ file đã có trong project ({items.length})
        <InfoTip text="Mọi ảnh/video đang nằm trong project: ảnh nền từng cảnh và b-roll từng part, gồm file tải từ internet/báo/bài đăng/Facebook, stock (Pixabay/Pexels), Wikipedia/Wikimedia và file tạo bằng AI. Mỗi mục hiện nguồn lấy và URL gốc ghi trong plan; file AI hiện thêm prompt đã tạo ra nó (bấm để mở). File pipeline định danh bằng quy ước tên seg_<cảnh> / broll_seg_<cảnh>_part_<n> nên vẫn nối đúng nguồn dù plan không ghi tên file." />
      </h3>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-[var(--dim)]">
          Project chưa có file media nào trên đĩa. Tìm media ở các mục bên dưới, tạo bằng AI, hoặc chạy Tạo video tự động — file về tới project sẽ tự hiện ở thư viện này kèm nguồn gốc.
        </p>
      ) : (
        <>
          <div className="mt-3 flex flex-wrap gap-1" role="group" aria-label="Lọc thư viện media">
            {chips.map((c) => (
              <button
                key={c.key}
                type="button"
                className="rounded-full border border-[var(--border)] px-2.5 py-1 text-xs font-semibold active:opacity-70"
                style={
                  filter === c.key
                    ? { background: "var(--accent)", color: "var(--accent-text)", borderColor: "var(--accent)" }
                    : { background: "var(--surface2)", color: "var(--text)" }
                }
                aria-pressed={filter === c.key}
                aria-label={`Lọc thư viện: ${c.label}`}
                onClick={() => setFilter(c.key)}
              >
                {c.label}
              </button>
            ))}
          </div>
          {visible.length === 0 && <p className="mt-3 text-sm text-[var(--dim)]">Không có file nào thuộc nhóm lọc này.</p>}
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {visible.map((it) => (
              <LibCard key={it.relPath} detail={detail} item={it} />
            ))}
          </div>
        </>
      )}
    </section>
  );
}

export function MediaTab({ detail }: { detail: ProjectDetail }) {
  const queryClient = useQueryClient();
  const plan = detail.plan;
  const scenes = plan?.scenes ?? [];
  const [sceneOrder, setSceneOrder] = useState<number>(scenes[0]?.order ?? 1);
  const [target, setTarget] = useState<"scene" | string>("scene");
  const [mediaType, setMediaType] = useState<"image" | "video">("image");
  const [extraKeywords, setExtraKeywords] = useState("");
  const [enKeywords, setEnKeywords] = useState("");
  const [results, setResults] = useState<{ layer: string; candidates: Candidate[]; note: string; queries: string[] } | null>(null);
  const [aiPrompt, setAiPrompt] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const scene = scenes.find((s) => s.order === sceneOrder) ?? scenes[0];
  const part: Part | undefined = target !== "scene" ? scene?.parts.find((p) => p.id === target) : undefined;
  const ttsPart = part ? detail.ttsParts.find((t) => t.id === part.id) : undefined;
  const summary = part ? (part.broll?.scriptSummary ?? part.voiceText) : (scene?.sceneScriptSummary ?? "");
  useEffect(() => {
    setAiPrompt(part ? (part.broll?.prompt ?? "") : (scene?.sceneImagePrompt ?? ""));
  }, [scene?.id, part?.id, scene, part]);
  const suggest = useMutation({
    mutationFn: () => api.suggestKeywords({ summary }),
    onSuccess: (r) => {
      if (r.noCluster) {
        setMsg("NO_CLUSTER: tóm tắt chưa khớp cụm khái niệm nào trong bảng cụm linh hoạt. Hãy thêm từ khóa bổ sung (tên riêng/dự án/địa điểm) hoặc viết tóm tắt rõ khái niệm hình ảnh hơn rồi tìm lại — đừng kết luận 'không có file' khi chưa thử hết cụm.");
      } else {
        setEnKeywords(r.enPhrases.join(", "));
        setMsg(`Cụm khái niệm: ${r.clusterId ?? ""}. Cụm Việt sẽ thử: ${r.viPhrases.join(" · ")}. Cụm Anh cho stock: ${r.enPhrases.join(", ")} (đã điền sẵn ô stock, sửa được). Script thử HẾT các cụm, không dừng ở cụm đầu.`);
      }
    },
  });
  const search = useMutation({
    mutationFn: (layer: "wikimedia" | "stock") =>
      api.searchMedia({
        layer,
        summary,
        enKeywords,
        extraKeywords,
        mediaType,
        durationSec: ttsPart?.duration ?? 0,
      }),
    onSuccess: (r, layer) => setResults({ layer, candidates: r.candidates, note: r.note, queries: r.queriesTried }),
  });
  const pick = useMutation({
    mutationFn: (c: Candidate) => {
      // Runner-up = highest score among the OTHER candidates of this same
      // search, recorded in the plan as provenance (source/score/license)
      // for the automated pipeline. Picking from this grid also records
      // the visual check.
      const others = (results?.candidates ?? [])
        .filter((x) => x.fileUrl !== c.fileUrl && x.score !== null)
        .map((x) => x.score as number);
      return api.pickMedia({
        projectId: detail.id,
        sceneOrder: scene?.order ?? 1,
        partId: part?.id ?? null,
        fileUrl: c.fileUrl,
        mediaType,
        source: c.source,
        pageUrl: c.pageUrl,
        license: c.license,
        author: c.author,
        score: c.score,
        verdict: c.verdict,
        runnerUpScore: others.length ? Math.max(...others) : null,
      });
    },
    onSuccess: (r) => {
      setMsg(`Đã tải file ${r.fileName} vào project và ghi nguồn + giấy phép vào plan. File này là minh họa theo khái niệm, không phải tư liệu thật của sự kiện cụ thể.`);
      queryClient.invalidateQueries({ queryKey: ["project", detail.id] });
    },
  });
  const genAi = useMutation({
    mutationFn: () =>
      api.generateAiMedia({
        projectId: detail.id,
        sceneOrder: scene?.order ?? 1,
        partId: part?.id ?? null,
        prompt: aiPrompt,
        mediaType,
      }),
    onSuccess: (r) => {
      setMsg(`Đã tạo bằng AI: ${r.fileName}. Xem lại ngay đối chiếu tóm tắt — lệch ý đồ thì sửa prompt và tạo lại riêng file này.`);
      queryClient.invalidateQueries({ queryKey: ["project", detail.id] });
    },
  });
  if (!plan || scenes.length === 0) {
    // Chưa có phân cảnh thì chưa gắn media mới được, nhưng thư viện
    // file đã có trên đĩa vẫn phải liệt kê được.
    return (
      <div className="grid gap-4">
        <MediaLibrary detail={detail} />
        <p className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4 text-sm text-[var(--dim)]">Chưa có plan/phân cảnh — hoàn thành tab Kịch bản và Phân cảnh trước để tìm/gắn media mới cho từng cảnh, part.</p>
      </div>
    );
  }
  const sceneLibItem = scene?.imageFile
    ? (detail.mediaLibrary ?? []).find((i) => i.relPath === `build/media/images/${scene.imageFile}`)
    : undefined;
  const partLibItem = part?.broll?.file
    ? (detail.mediaLibrary ?? []).find((i) => i.relPath === `build/media/broll/${part.broll?.file}`)
    : undefined;
  return (
    <div className="grid gap-4">
      <MediaLibrary detail={detail} />
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <div className="grid gap-3 sm:grid-cols-3">
          <div>
            <label className={labelCls} htmlFor="media-scene">Cảnh</label>
            <select id="media-scene" className={inputCls} value={scene?.order} onChange={(e) => { setSceneOrder(Number(e.target.value)); setTarget("scene"); setResults(null); }}>
              {scenes.map((s) => (
                <option key={s.id} value={s.order}>Cảnh {s.order} — {(s.sceneScriptSummary || s.text).slice(0, 60)}…</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls} htmlFor="media-target">Gắn media vào</label>
            <select id="media-target" className={inputCls} value={target} onChange={(e) => { setTarget(e.target.value); setResults(null); }}>
              <option value="scene">Ảnh nền của cảnh</option>
              {(scene?.parts ?? []).map((p) => (
                <option key={p.id} value={p.id}>B-roll của {p.id}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls} htmlFor="media-type">Loại media</label>
            <select id="media-type" className={inputCls} value={mediaType} onChange={(e) => setMediaType(e.target.value as "image" | "video")}>
              <option value="image">Ảnh</option>
              <option value="video">Video (ưu tiên hook/cảnh quan trọng)</option>
            </select>
          </div>
        </div>
        <p className="mt-3 text-sm text-[var(--dim)]">
          Thứ tự tìm: <strong>1) Wikipedia/Wikimedia</strong> → <strong>2) Stock</strong> → <strong>3) AI</strong>
          <InfoTip text="Thứ tự bắt buộc, không đảo ngược: chỉ sang lớp sau khi lớp trước không có file đúng sau khi soi trực quan. Video được chấm theo độ gần với thời lượng voice của part đích." />
          {ttsPart && <> · voice part này: <span className="mono">{ttsPart.duration.toFixed(1)}s</span></>}
        </p>
        {scene?.imageFile && target === "scene" && (
          <div className="mt-3 max-w-xs">
            <MediaFile projectId={detail.id} relPath={`build/media/images/${scene.imageFile}`} kind="image" label={`Ảnh cảnh ${scene.order}: ${scene.imageFile}`} />
            <p className="mono mt-1 text-xs text-[var(--dim)]">{scene.imageFile}{scene.mediaSource ? ` · ${provText(scene.mediaSource).source} · ${provText(scene.mediaSource).license}` : ""}</p>
            {sceneLibItem && sceneLibItem.urls.length > 0 && (
              <p className="mt-0.5 break-all text-xs [overflow-wrap:anywhere]">
                {sceneLibItem.urls.map((u) => (
                  <a key={u} href={u} target="_blank" rel="noreferrer" className="mr-2 text-[var(--accent)] underline" aria-label={`Mở URL nguồn của ảnh cảnh ${scene.order}`}>{u}</a>
                ))}
              </p>
            )}
            {sceneLibItem?.isAi && sceneLibItem.aiPrompt && (
              <details className="mt-1">
                <summary className="cursor-pointer text-xs font-semibold text-[var(--accent)]">Prompt AI đã tạo ảnh này</summary>
                <p className="mt-1 whitespace-pre-wrap break-words rounded bg-black/20 p-2 text-xs leading-relaxed">{sceneLibItem.aiPrompt}</p>
              </details>
            )}
          </div>
        )}
        {part?.broll?.file && (
          <div className="mt-3 max-w-xs">
            <MediaFile projectId={detail.id} relPath={`build/media/broll/${part.broll.file}`} kind={part.broll.file.endsWith(".mp4") ? "video" : "image"} label={`B-roll ${part.id}: ${part.broll.file}`} />
            <p className="mono mt-1 text-xs text-[var(--dim)]">{part.broll.file}{part.broll.mediaSource ? ` · ${provText(part.broll.mediaSource).source}` : ""}</p>
            {partLibItem && partLibItem.urls.length > 0 && (
              <p className="mt-0.5 break-all text-xs [overflow-wrap:anywhere]">
                {partLibItem.urls.map((u) => (
                  <a key={u} href={u} target="_blank" rel="noreferrer" className="mr-2 text-[var(--accent)] underline" aria-label={`Mở URL nguồn của b-roll ${part.id}`}>{u}</a>
                ))}
              </p>
            )}
            {partLibItem?.isAi && partLibItem.aiPrompt && (
              <details className="mt-1">
                <summary className="cursor-pointer text-xs font-semibold text-[var(--accent)]">Prompt AI đã tạo file này</summary>
                <p className="mt-1 whitespace-pre-wrap break-words rounded bg-black/20 p-2 text-xs leading-relaxed">{partLibItem.aiPrompt}</p>
              </details>
            )}
          </div>
        )}
        <div className="mt-3 grid gap-3">
          <div>
            <label className={labelCls} htmlFor="media-extra">Từ khóa bổ sung (tên riêng, dự án, địa điểm — thử trước cụm chung)</label>
            <input id="media-extra" className={inputCls} value={extraKeywords} onChange={(e) => setExtraKeywords(e.target.value)} placeholder="Ví dụ: VinSpeed, Velaro Novo" />
          </div>
          <div>
            <label className={labelCls} htmlFor="media-en">Từ khóa Anh cho stock (mỗi cụm cách nhau dấu phẩy, chạy riêng từng cụm)</label>
            <input id="media-en" className={inputCls} value={enKeywords} onChange={(e) => setEnKeywords(e.target.value)} placeholder="Ví dụ: courtroom, scales of justice" />
          </div>
          <div className="flex flex-wrap gap-2">
            <button type="button" className={btnCls} disabled={!summary || suggest.isPending} onClick={() => suggest.mutate()} aria-label="Gợi ý từ khóa theo cụm linh hoạt">Gợi ý từ khóa</button>
            <button type="button" className={btnPrimary} disabled={!summary || search.isPending} onClick={() => search.mutate("wikimedia")} aria-label="Tìm trên Wikipedia và Wikimedia Commons">1 · Tìm Wikipedia/Wikimedia</button>
            <button type="button" className={btnPrimary} disabled={search.isPending || !enKeywords.trim()} onClick={() => search.mutate("stock")} aria-label="Tìm trên stock Pixabay và Pexels">2 · Tìm stock Pixabay/Pexels</button>
          </div>
          {msg && <p className="text-sm" style={{ color: "var(--ok)" }}>{msg}</p>}
          {suggest.error && <p className="text-sm text-[var(--bad)]">{String(suggest.error)}</p>}
          {search.error && <p className="text-sm text-[var(--bad)]">Tìm kiếm lỗi: {String(search.error)}</p>}
        </div>
      </section>
      {results && (
        <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label="Kết quả tìm media">
          <h3 className="font-bold">
            Ứng viên — lớp {results.layer === "wikimedia" ? "Wikipedia/Wikimedia" : "Stock"}
            <InfoTip text="Soi trực quan bắt buộc trước khi dùng: ảnh xem khung toàn cảnh, video xem có chuyển động thật và không chen chữ với template. Đầu bảng lệch ý đồ thì loại, lấy ứng viên tiếp theo cùng lớp; hết lớp mới sang lớp sau." />
          </h3>
          <p className="mt-1 text-xs text-[var(--dim)]">Đã thử: {results.queries.join(" · ") || "—"}</p>
          {results.note && <p className="mt-1 text-sm" style={{ color: "var(--warn)" }}>{results.note}</p>}
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {results.candidates.map((c, i) => (
              <article key={`${c.fileUrl}-${i}`} className="rounded-lg border border-[var(--border)] bg-[var(--surface2)] p-2">
                {c.mime.startsWith("video") || mediaType === "video" ? (
                  <video src={c.fileUrl} controls muted playsInline preload="metadata" aria-label={`Ứng viên ${c.title}`} className="h-40 w-full rounded bg-black/40 object-contain" />
                ) : (
                  <img src={c.thumbUrl || c.fileUrl} alt={c.title} loading="lazy" className="h-40 w-full rounded bg-black/40 object-contain" />
                )}
                <p className="mt-2 line-clamp-2 text-xs font-semibold">{c.title}</p>
                <p className="mono text-[11px] text-[var(--dim)]">
                  {c.score !== null ? `điểm ${c.score.toFixed(1)} · ${c.verdict}` : c.verdict}
                  {c.width && c.height ? ` · ${c.width}×${c.height}` : ""}
                  {c.durationSec !== null ? ` · ${c.durationSec.toFixed(1)}s` : ""}
                  {` · ${c.license || "chưa rõ giấy phép"}`}
                </p>
                <p className="text-[11px] text-[var(--dim)]">{c.author}</p>
                <div className="mt-2 flex gap-2">
                  <button type="button" className={btnPrimary} disabled={pick.isPending} onClick={() => pick.mutate(c)} aria-label={`Dùng file ${c.title}`}>Dùng file này</button>
                  {c.pageUrl && (
                    <a className={`${btnCls} inline-flex items-center`} href={c.pageUrl} target="_blank" rel="noreferrer" aria-label={`Mở trang file ${c.title}`}>Trang file ↗</a>
                  )}
                </div>
              </article>
            ))}
          </div>
          {results.candidates.length === 0 && <p className="mt-2 text-sm text-[var(--dim)]">Không có ứng viên ở lớp này. Thử thêm từ khóa bổ sung, hoặc chuyển lớp tiếp theo / tạo bằng AI ở dưới.</p>}
          {pick.error && <p className="mt-2 text-sm text-[var(--bad)]">Tải file thất bại: {String(pick.error)}</p>}
        </section>
      )}
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">
          3 · Tạo bằng AI — chỉ khi không tìm được file đúng
          <InfoTip text="Prompt bằng tiếng Việt, được lưu trong plan. Video b-roll: dọc 9:16, tắt tiếng, không chữ chen template. Nếu tạo video cho hook/cảnh quan trọng mà thất bại, app sẽ báo lỗi — khi đó dùng ảnh + Ken Burns thay thế." />
        </h3>
        <label className={labelCls} htmlFor="ai-prompt">Prompt (tiếng Việt)</label>
        <textarea id="ai-prompt" className={inputCls} rows={3} value={aiPrompt} onChange={(e) => setAiPrompt(e.target.value)} placeholder="Bối cảnh, chủ thể, hành động/chuyển động, ánh sáng, góc máy, dọc 9:16, không chữ, không watermark…" />
        <button type="button" className={`${btnPrimary} mt-2`} disabled={!aiPrompt.trim() || genAi.isPending} onClick={() => genAi.mutate()} aria-label="Tạo media bằng AI">
          {genAi.isPending ? "Đang tạo (có thể vài phút)…" : `Tạo ${mediaType === "video" ? "video" : "ảnh"} bằng AI`}
        </button>
        {genAi.error && <p className="mt-2 text-sm text-[var(--bad)]">Tạo AI thất bại: {String(genAi.error)}</p>}
      </section>
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <h3 className="font-bold">
          Tạo ảnh cảnh hàng loạt theo plan
          <InfoTip text="Cảnh có prompt AI thì tạo ảnh AI; cảnh không có prompt thì dựng card chữ bằng render_scene_card (đó không phải “thiếu ảnh”). Job chạy nền, file đã có sẽ được bỏ qua." />
        </h3>
        <div className="mt-2">
          <JobRunner projectId={detail.id} step="genimages" label="tạo ảnh cảnh" />
        </div>
      </section>
    </div>
  );
}
