// Thư viện media của tab Media: liệt kê toàn bộ file media trên đĩa của
// project và nối mỗi file với nguồn gốc ghi trong plan (khớp tường minh
// theo tên file trong plan trước, khớp quy ước tên seg_*/broll_* sau).
// Chỉ privileged.ts import file này.
import { existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

// ---- Thư viện media (tab Media) ----
// Liệt kê TOÀN BỘ file media ĐÃ CÓ trên đĩa của project (build/media/
// images + build/media/broll) rồi nối mỗi file với nguồn gốc ghi trong
// plan. Việc nối không thể chỉ dựa vào scene.imageFile / broll.file:
// project pipeline để hai trường đó null và định danh file thuần bằng
// quy ước tên seg_<order>_* và broll_seg_<order>_part_<pi>_*, nên phải
// khớp cả theo quy ước tên (và khớp tường minh khi plan có ghi file).
export type MediaLibraryItem = {
  fileName: string;
  relPath: string;
  kind: "image" | "video";
  sizeBytes: number;
  slot: "scene" | "broll" | "other";
  sceneOrder: number | null;
  partId: string | null;
  partLabel: string;
  source: string;
  urls: string[];
  license: string | null;
  author: string | null;
  title: string | null;
  isAi: boolean;
  aiPrompt: string | null;
  note: string | null;
};

function provAsRecord(v: unknown): Record<string, unknown> {
  if (typeof v === "string") {
    return /^https?:\/\//i.test(v.trim()) ? { page_url: v } : { source: v };
  }
  if (v && typeof v === "object" && !Array.isArray(v)) {
    return v as Record<string, unknown>;
  }
  return {};
}

function provStr(rec: Record<string, unknown>, ...keys: string[]): string | null {
  for (const k of keys) {
    const v = rec[k];
    if (typeof v === "string" && v.trim()) return v.trim();
    if (typeof v === "number" || typeof v === "boolean") return String(v);
  }
  return null;
}

function urlsFromText(text: string | null): string[] {
  if (!text) return [];
  const hits = text.match(/https?:\/\/[^\s"'<>)\]]+/g) ?? [];
  return hits.map((u) => u.replace(/[.,;]+$/, ""));
}

// "AI" phải đứng thành từ riêng — khớp lỏng lẻo sẽ bắt nhầm chữ "ai"
// trong từ tiếng Việt (Hải, bài, tải…) ở tên nguồn báo.
const AI_SOURCE_RE = /(^|[\s([{\/—–-])AI($|[\s)\]}\/—–\-:,.])/;

export function buildMediaLibrary(dir: string, plan: unknown): MediaLibraryItem[] {
  const planRec = (plan ?? {}) as {
    scenes?: Array<Record<string, unknown>>;
  };
  const scenes = Array.isArray(planRec.scenes) ? planRec.scenes : [];
  type SceneInfo = {
    order: number | null;
    imageFile: string | null;
    mediaSource: Record<string, unknown>;
    sceneImagePrompt: string;
    parts: Array<{
      id: string;
      brollFile: string | null;
      broll: Record<string, unknown>;
      mediaSource: Record<string, unknown>;
      videoSource: Record<string, unknown>;
    }>;
  };
  const sceneInfos: SceneInfo[] = scenes.map((s) => {
    const partsRaw = Array.isArray(s["parts"]) ? (s["parts"] as Array<Record<string, unknown>>) : [];
    return {
      order: typeof s["order"] === "number" ? s["order"] : null,
      imageFile: typeof s["imageFile"] === "string" && s["imageFile"] ? (s["imageFile"] as string) : null,
      mediaSource: provAsRecord(s["mediaSource"]),
      sceneImagePrompt: typeof s["sceneImagePrompt"] === "string" ? (s["sceneImagePrompt"] as string) : "",
      parts: partsRaw.map((p) => {
        const broll = (p["broll"] ?? {}) as Record<string, unknown>;
        return {
          id: String(p["id"] ?? ""),
          brollFile: typeof broll["file"] === "string" && broll["file"] ? (broll["file"] as string) : null,
          broll,
          mediaSource: provAsRecord(broll["mediaSource"]),
          videoSource: provAsRecord(broll["videoSource"]),
        };
      }),
    };
  });

  const items: MediaLibraryItem[] = [];
  const scan = (sub: "images" | "broll") => {
    const mediaDir = join(dir, "build/media", sub);
    if (!existsSync(mediaDir)) return;
    const names = readdirSync(mediaDir)
      .filter((f) => /\.(jpe?g|png|webp|mp4|webm)$/i.test(f))
      .sort();
    for (const fileName of names) {
      const kind: "image" | "video" = /\.mp4$|\.webm$/i.test(fileName) ? "video" : "image";
      let sizeBytes = 0;
      try {
        sizeBytes = statSync(join(mediaDir, fileName)).size;
      } catch {
        sizeBytes = 0;
      }
      // Khớp file → cảnh/part: tường minh trong plan trước, quy ước
      // tên file sau.
      let slot: MediaLibraryItem["slot"] = "other";
      let sceneInfo: SceneInfo | null = null;
      let partInfo: SceneInfo["parts"][number] | null = null;
      let partIdx: number | null = null;
      for (const si of sceneInfos) {
        if (sub === "images" && si.imageFile === fileName) {
          slot = "scene";
          sceneInfo = si;
          break;
        }
        const pi = si.parts.findIndex((p) => p.brollFile === fileName);
        if (sub === "broll" && pi >= 0) {
          slot = "broll";
          sceneInfo = si;
          partInfo = si.parts[pi] ?? null;
          partIdx = pi + 1;
          break;
        }
      }
      if (!sceneInfo && sub === "images") {
        const m = /^seg_(\d+)_/.exec(fileName);
        if (m) {
          const order = parseInt(m[1] ?? "", 10);
          const si = sceneInfos.find((x) => x.order === order);
          if (si) {
            slot = "scene";
            sceneInfo = si;
          }
        }
      }
      if (!sceneInfo && sub === "broll") {
        const m = /^broll_seg_(\d+)_part_(\d+)_/.exec(fileName);
        if (m) {
          const order = parseInt(m[1] ?? "", 10);
          const pi = parseInt(m[2] ?? "", 10);
          const si = sceneInfos.find((x) => x.order === order);
          if (si) {
            slot = "broll";
            sceneInfo = si;
            partInfo = si.parts[pi - 1] ?? null;
            partIdx = pi;
          }
        }
      }
      // Nguồn gốc: ảnh lấy mediaSource, video ưu tiên videoSource khi
      // có (pipeline ghi nguồn video riêng ở đó), URL gom từ cả hai.
      const recs: Array<Record<string, unknown>> =
        slot === "broll" && partInfo
          ? kind === "video" && Object.keys(partInfo.videoSource).length > 0
            ? [partInfo.videoSource, partInfo.mediaSource]
            : [partInfo.mediaSource, partInfo.videoSource]
          : slot === "scene" && sceneInfo
            ? [sceneInfo.mediaSource]
            : [];
      const primary = recs[0] ?? {};
      const source =
        provStr(primary, "source", "type") ??
        (recs[1] ? provStr(recs[1], "source", "type") : null) ??
        "Chưa ghi nguồn trong plan";
      const urlFields = [
        "pageUrl",
        "page_url",
        "article_url",
        "original_url",
        "image_url",
        "reference_image_url",
        "referenceImageUrl",
        "referencePageUrl",
        "videoPageUrl",
        "videoFileUrl",
      ];
      const urlSet = new Set<string>();
      for (const rec of recs) {
        for (const f of urlFields) {
          const u = provStr(rec, f);
          if (u && /^https?:\/\//i.test(u)) urlSet.add(u);
        }
        // Có pipeline ghi luôn URL vào trường title của videoSource.
        const t = provStr(rec, "title");
        if (t && /^https?:\/\//i.test(t)) urlSet.add(t);
        for (const u of urlsFromText(provStr(rec, "source"))) urlSet.add(u);
      }
      const sourceTypeText = `${source} ${provStr(primary, "type") ?? ""}`;
      const provPrompt =
        provStr(primary, "prompt", "aiPrompt") ??
        (recs[1] ? provStr(recs[1], "prompt", "aiPrompt") : null);
      const isAi =
        AI_SOURCE_RE.test(sourceTypeText) ||
        provStr(primary, "type") === "prompt-AI" ||
        (provPrompt !== null && /prompt/i.test(provStr(primary, "type") ?? ""));
      const planPrompt =
        slot === "scene" && sceneInfo
          ? sceneInfo.sceneImagePrompt || null
          : slot === "broll" && partInfo
            ? provStr(partInfo.broll, "prompt")
            : null;
      const titleRaw = provStr(primary, "title");
      items.push({
        fileName,
        relPath: `build/media/${sub}/${fileName}`,
        kind,
        sizeBytes,
        slot,
        sceneOrder: sceneInfo?.order ?? null,
        partId: partInfo?.id || null,
        partLabel:
          slot === "scene"
            ? `Ảnh nền cảnh ${sceneInfo?.order ?? "?"}`
            : slot === "broll"
              ? `B-roll cảnh ${sceneInfo?.order ?? "?"} · part ${partIdx ?? "?"}${partInfo?.id ? ` (${partInfo.id})` : ""}`
              : "File trong thư mục media — chưa gắn cảnh/part trong plan",
        source,
        // Không cắt bớt URL nguồn (trước cắt tối đa 4 — giai đoạn 4,
        // 03/11): URL là bằng chứng nguồn gốc, mất URL là mất khả năng
        // kiểm chứng; danh sách đã dedupe sẵn nên độ dài có giới hạn tự
        // nhiên theo số trường provenance của plan.
        urls: [...urlSet],
        license:
          provStr(primary, "license", "videoLicense") ??
          (recs[1] ? provStr(recs[1], "license", "videoLicense") : null),
        author: provStr(primary, "author"),
        title: titleRaw && !/^https?:\/\//i.test(titleRaw) ? titleRaw : null,
        isAi,
        aiPrompt: isAi ? (provPrompt ?? planPrompt) : null,
        note:
          provStr(primary, "note", "reason") ??
          (recs[1] ? provStr(recs[1], "note", "reason") : null),
      });
    }
  };
  scan("images");
  scan("broll");
  const slotRank = { scene: 0, broll: 1, other: 2 } as const;
  items.sort(
    (a, b) =>
      slotRank[a.slot] - slotRank[b.slot] ||
      (a.sceneOrder ?? 9999) - (b.sceneOrder ?? 9999) ||
      a.fileName.localeCompare(b.fileName),
  );
  return items;
}
