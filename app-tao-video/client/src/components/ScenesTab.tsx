// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { api } from "../api";
import { MOTIONS, btnCls, btnPrimary, fmtSec, inputCls, labelCls, provText, toStringInputs } from "../lib";
import { InfoTip } from "./InfoTip";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef, useState } from "react";
import type { ApiResponse } from "../api";
import type { BgmTrack, Part, Plan, ProjectDetail } from "../lib";


function TemplatePreviewButton({ templateId, inputs, projectId }: { templateId: string; inputs: Record<string, string>; projectId: string }) {
  const [png, setPng] = useState<string | null>(null);
  const m = useMutation({
    mutationFn: () => api.renderTemplatePreview({ templateId, inputs, projectId }),
    onSuccess: (r) => setPng(r.pngBase64),
  });
  return (
    <span className="inline-block">
      <button type="button" className={btnCls} disabled={m.isPending} onClick={() => m.mutate()} aria-label={`Xem trước template ${templateId}`}>
        {m.isPending ? "Đang render…" : "Xem trước template"}
      </button>
      {m.error && <span className="ml-2 text-xs text-[var(--bad)]">{String(m.error)}</span>}
      {png && (
        <span className="mt-2 block">
          <img src={`data:image/png;base64,${png}`} alt={`Xem trước template ${templateId}`} className="max-h-72 rounded-lg border border-[var(--border)]" />
          <span className="mt-1 flex items-center gap-1 text-xs text-[var(--dim)]">
            Khung 720×1280 thật
            <InfoTip text="Kiểm tra chữ trong lề an toàn: 96px hai bên, 140px phía trên — chữ ngoài lề này dễ bị giao diện nền tảng che hoặc lọt khung khi render thật." />
          </span>
        </span>
      )}
    </span>
  );
}

type Stamp = NonNullable<NonNullable<Part["broll"]>["stamps"]>[number];

// R4-59 (08/11/2026, DEC-068 A): sửa dấu (stamp) của một part — trước
// đây stamp/reveal chỉ sửa được bằng tay trong file plan. Mỗi dấu:
// text (chữ đóng dấu; trống thì render bỏ qua), tone (màu, mặc định
// "red"), tilt (độ nghiêng, mặc định "-15"), on (slot ảnh, vd "img1"),
// at (giây xuất hiện), sfx (thud riêng — offsetSec luôn bằng at, kêu
// cùng lúc dấu hiện). Sửa xong ghi vào broll.stamps; hết dấu thì xóa key.
function StampsEditor({ idPrefix, stamps, sfxList, onStamps }: { idPrefix: string; stamps: Stamp[]; sfxList: Array<{ id: string }>; onStamps: (next: Stamp[]) => void }) {
  const set = (i: number, patch: Partial<Stamp>) => onStamps(stamps.map((s, j) => (j === i ? { ...s, ...patch } : s)));
  const setAt = (i: number, at: number) => {
    const next = stamps.map((s) => ({ ...s }));
    const st = next[i]!;
    st.at = at;
    if (st.sfx) st.sfx = { ...st.sfx, offsetSec: at };
    onStamps(next);
  };
  const setSfx = (i: number, sid: string) => {
    const next = stamps.map((s) => ({ ...s }));
    const st = next[i]!;
    if (!sid) delete st.sfx;
    else st.sfx = { id: sid, offsetSec: st.at ?? 0, volume: sid === "heavy_thud_slam" || sid === "boom_sub_impact" ? 0.35 : 0.65 };
    onStamps(next);
  };
  return (
    <div className="mt-2">
      <label className={labelCls}>Dấu (stamp) — chữ đóng dấu lên template</label>
      {stamps.map((st, i) => (
        <div key={i} className="mt-2 rounded-lg border border-[var(--border)] p-2">
          <div className="flex flex-wrap items-end gap-2">
            <div className="min-w-32 flex-1">
              <label className={labelCls} htmlFor={`stamp-${idPrefix}-text-${i}`}>Chữ dấu</label>
              <input id={`stamp-${idPrefix}-text-${i}`} className={inputCls} value={st.text ?? ""} placeholder="VD: THUA" onChange={(e) => set(i, { text: e.target.value })} />
            </div>
            <div className="w-20">
              <label className={labelCls} htmlFor={`stamp-${idPrefix}-tone-${i}`}>Màu</label>
              <input id={`stamp-${idPrefix}-tone-${i}`} className={inputCls} value={st.tone ?? "red"} placeholder="red" onChange={(e) => set(i, { tone: e.target.value })} />
            </div>
            <div className="w-16">
              <label className={labelCls} htmlFor={`stamp-${idPrefix}-tilt-${i}`}>Nghiêng</label>
              <input id={`stamp-${idPrefix}-tilt-${i}`} className={inputCls} value={String(st.tilt ?? "-15")} placeholder="-15" onChange={(e) => set(i, { tilt: e.target.value })} />
            </div>
            <div className="w-20">
              <label className={labelCls} htmlFor={`stamp-${idPrefix}-on-${i}`}>Lên slot</label>
              <input id={`stamp-${idPrefix}-on-${i}`} className={inputCls} value={st.on ?? "img1"} placeholder="img1" onChange={(e) => set(i, { on: e.target.value })} />
            </div>
            <div className="w-20">
              <label className={labelCls} htmlFor={`stamp-${idPrefix}-at-${i}`}>Giây hiện</label>
              <input id={`stamp-${idPrefix}-at-${i}`} className={inputCls} type="number" step="0.1" min="0" value={st.at ?? 0} onChange={(e) => { const v = Number(e.target.value); setAt(i, Number.isFinite(v) ? v : 0); }} />
            </div>
            <div className="w-44">
              <label className={labelCls} htmlFor={`stamp-${idPrefix}-sfx-${i}`}>SFX của dấu</label>
              <select id={`stamp-${idPrefix}-sfx-${i}`} className={inputCls} value={st.sfx?.id ?? ""} onChange={(e) => setSfx(i, e.target.value)}>
                <option value="">— Không SFX —</option>
                {sfxList.map((s) => (
                  <option key={s.id} value={s.id}>{s.id}</option>
                ))}
              </select>
            </div>
            <button type="button" className={btnCls} style={{ color: "var(--bad)" }} onClick={() => onStamps(stamps.filter((_, j) => j !== i))} aria-label={`Xóa dấu ${i + 1}`}>Xóa dấu</button>
          </div>
          {st.sfx && <p className="mt-1 text-xs text-[var(--dim)]">SFX {st.sfx.id} · volume {st.sfx.volume} · kêu ở giây {st.sfx.offsetSec}</p>}
        </div>
      ))}
      <button type="button" className={btnCls} onClick={() => onStamps([...stamps, { text: "", tone: "red", tilt: "-15", on: "img1", at: 0 }])} aria-label="Thêm dấu mới">
        + Thêm dấu
      </button>
      <p className="mt-1 text-xs text-[var(--dim)]">Dấu hiện từ giây “at” lên slot “on”; SFX thud kêu cùng lúc dấu hiện. Dấu không có chữ sẽ bị render bỏ qua.</p>
    </div>
  );
}

export function ScenesTab({ detail, catalogs }: { detail: ProjectDetail; catalogs: ApiResponse<typeof api, "getCatalogs"> | undefined }) {
  const queryClient = useQueryClient();
  const [plan, setPlan] = useState<Plan | null>(detail.plan);
  const dirty = useRef(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  useEffect(() => {
    if (!dirty.current) setPlan(detail.plan);
  }, [detail]);
  const save = useMutation({
    mutationFn: () => api.savePlan({ projectId: detail.id, plan: plan as Plan }),
    onSuccess: (r) => {
      dirty.current = false;
      setSaveMsg(r.problems.length > 0 ? `Đã lưu nhưng plan có vấn đề: ${r.problems.join("; ")}` : "Đã lưu plan (đã snapshot bản trước).");
      queryClient.invalidateQueries({ queryKey: ["project", detail.id] });
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
  if (!plan) {
    return (
      <div className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <p className="text-sm text-[var(--dim)]">Project chưa có plan. Hãy lưu kịch bản rồi bấm “Tách thành cảnh/part” ở tab Kịch bản, hoặc tạo plan rỗng:</p>
        <button
          type="button"
          className={`${btnPrimary} mt-3`}
          onClick={() => {
            dirty.current = true;
            setPlan({ pauseAfterMs: 180, speed: 1.0, voice: "Hữu Quân", scenes: [] });
          }}
          aria-label="Tạo plan rỗng"
        >
          Tạo plan rỗng
        </button>
      </div>
    );
  }
  const templates = catalogs?.templates ?? [];
  const bgmTracks: BgmTrack[] = catalogs?.bgm ?? [];
  const sfxList = catalogs?.sfx ?? [];
  const templatedCount = plan.scenes.reduce((n, s) => n + s.parts.filter((p) => p.broll?.templateId).length, 0);
  const totalParts = plan.scenes.reduce((n, s) => n + s.parts.length, 0);
  const update = (fn: (p: Plan) => Plan) => {
    dirty.current = true;
    setPlan((prev) => (prev ? fn(structuredClone(prev)) : prev));
  };
  return (
    <div className="grid gap-4">
      <section className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4">
        <div className="grid gap-3 sm:max-w-md">
          <div>
            <label className={labelCls} htmlFor="plan-bgm">Nhạc nền (BGM)</label>
            <select
              id="plan-bgm"
              className={inputCls}
              value={plan.bgm?.id ?? ""}
              onChange={(e) => {
                const t = bgmTracks.find((x) => x.id === e.target.value);
                update((p) => ({ ...p, bgm: t ? { id: t.id, file: t.file, mood: t.moods[0] ?? "" } : undefined }));
              }}
            >
              <option value="">— Chưa chọn —</option>
              {bgmTracks.map((t) => (
                <option key={t.id} value={t.id}>{t.title} · {t.moods.join("/")} · {fmtSec(t.durationSec)} · {t.license}</option>
              ))}
            </select>
          </div>
        </div>
        <p className="mt-3 text-sm text-[var(--dim)]">
          Mật độ chữ: {templatedCount}/{totalParts} part có template.
          {totalParts > 0 && templatedCount / totalParts > 0.7 && (
            <span style={{ color: "var(--warn)" }}> Gần 100% là dàn sai.</span>
          )}
          <InfoTip text="Mặc định KHÔNG gắn chữ, chỉ gắn template ở beat nhấn mạnh; part có template sẽ ẩn phụ đề karaoke. SFX: part có template tự lấy SFX gợi ý trong meta của template khi bạn chọn template; hook, móc lại (~50%) và kết luận bắt buộc có SFX." />
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className={btnPrimary} disabled={save.isPending} onClick={() => save.mutate()} aria-label="Lưu plan phân cảnh">
            {save.isPending ? "Đang lưu…" : "Lưu plan"}
          </button>
          <button
            type="button"
            className={btnCls}
            onClick={() =>
              update((p) => ({
                ...p,
                scenes: [...p.scenes, { id: `scene${p.scenes.length + 1}`, order: p.scenes.length + 1, sceneScriptSummary: "", sceneImagePrompt: "", text: "", parts: [{ id: `scene${p.scenes.length + 1}-part-1`, voiceText: "", broll: {} }] }],
              }))
            }
            aria-label="Thêm cảnh mới"
          >
            + Thêm cảnh
          </button>
          {saveMsg && <span className="text-sm" style={{ color: saveMsg.includes("vấn đề") ? "var(--warn)" : "var(--ok)" }}>{saveMsg}</span>}
          {save.error && <span className="text-sm text-[var(--bad)]">{String(save.error)}</span>}
        </div>
      </section>
      {plan.scenes.map((scene, si) => (
        <section key={scene.id} className="rounded-xl border border-[var(--border)] bg-[var(--surface)] p-4" aria-label={`Cảnh ${scene.order}`}>
          <div className="flex items-start gap-2">
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <h3 className="font-bold">Cảnh {scene.order}</h3>
                <span className="mono text-xs text-[var(--dim)]">{scene.id}</span>
              </div>
              <div className="mt-1 flex flex-wrap items-center gap-2">
                {scene.isMossGrid ? (
                  <span className="rounded-full px-2 py-0.5 text-xs font-semibold" style={{ color: "var(--warn)", background: "color-mix(in srgb, var(--warn) 12%, transparent)" }}>Nền xanh rêu — thiếu ảnh</span>
                ) : scene.imageFile ? (
                  <span className="rounded-full bg-[var(--surface2)] px-2 py-0.5 text-xs">Ảnh: <span className="mono">{scene.imageFile}</span>{scene.mediaSource ? ` · ${provText(scene.mediaSource).source}${provText(scene.mediaSource).license ? ` · ${provText(scene.mediaSource).license}` : ""}` : ""}</span>
                ) : (
                  <span className="rounded-full px-2 py-0.5 text-xs font-semibold" style={{ color: "var(--bad)", background: "color-mix(in srgb, var(--bad) 12%, transparent)" }}>Chưa có ảnh cảnh — render sẽ ra nền đen</span>
                )}
              </div>
            </div>
            <div className="shrink-0">
              <button type="button" className={btnCls} style={{ color: "var(--bad)" }} onClick={() => update((p) => ({ ...p, scenes: p.scenes.filter((_, i) => i !== si).map((x, i) => ({ ...x, order: i + 1 })) }))} aria-label={`Xóa cảnh ${scene.order}`}>Xóa cảnh</button>
            </div>
          </div>
          <div className="mt-3 grid gap-3">
            <div>
              <label className={labelCls} htmlFor={`sum-${scene.id}`}>Tóm tắt cảnh (tiếng Việt, bắt buộc)</label>
              <textarea id={`sum-${scene.id}`} className={inputCls} rows={2} value={scene.sceneScriptSummary} onChange={(e) => update((p) => { p.scenes[si]!.sceneScriptSummary = e.target.value; return p; })} placeholder="1–2 câu: diễn biến chính + ý đồ hình ảnh + chi tiết đã kiểm chứng của đúng cảnh này" />
            </div>
            <div>
              <label className={labelCls} htmlFor={`prompt-${scene.id}`}>Prompt ảnh cảnh (tiếng Việt)</label>
              <textarea id={`prompt-${scene.id}`} className={inputCls} rows={2} value={scene.sceneImagePrompt} onChange={(e) => update((p) => { p.scenes[si]!.sceneImagePrompt = e.target.value; return p; })} placeholder="Bối cảnh, đối tượng chính, hành động, vật chứng, ánh sáng, góc máy, dọc 9:16, không chữ, không watermark. Người thật thiếu tư liệu: góc rộng/bóng lưng/vật chứng, không cận mặt." />
            </div>
            <div>
              <label className={labelCls} htmlFor={`motion-${scene.id}`}>Chuyển động (motion)</label>
              <select id={`motion-${scene.id}`} className={inputCls} value={scene.motion ?? ""} onChange={(e) => update((p) => { p.scenes[si]!.motion = e.target.value || undefined; return p; })}>
                {MOTIONS.map((m) => (
                  <option key={m} value={m}>{m === "" ? "Ngẫu nhiên theo seed project (không lặp liên tiếp)" : m}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="mt-3 space-y-3">
            {scene.parts.map((part, pi) => {
              const tpl = templates.find((t) => t.id === part.broll?.templateId);
              return (
                <div key={part.id} className="rounded-lg border border-[var(--border)] bg-[var(--surface2)] p-3">
                  <div className="flex items-start gap-2">
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="mono text-xs font-bold">{part.id}</span>
                        {part.broll?.templateId ? (
                          <span className="rounded-full px-2 py-0.5 text-xs font-semibold" style={{ background: "color-mix(in srgb, var(--accent) 20%, transparent)", color: "var(--accent)" }}>
                            {part.broll.templateId} — part này ẩn phụ đề karaoke
                          </span>
                        ) : (
                          <span className="text-xs text-[var(--dim)]">Không template (mặc định đúng)</span>
                        )}
                        {part.broll?.file && <span className="mono text-xs text-[var(--dim)]">b-roll: {part.broll.file}</span>}
                      </div>
                    </div>
                    <div className="shrink-0">
                      <button type="button" className={btnCls} style={{ color: "var(--bad)" }} onClick={() => update((p) => { p.scenes[si]!.parts = p.scenes[si]!.parts.filter((_, i) => i !== pi); return p; })} aria-label={`Xóa part ${part.id}`}>Xóa part</button>
                    </div>
                  </div>
                  <label className={labelCls} htmlFor={`vt-${part.id}`}>Lời đọc của part</label>
                  <textarea id={`vt-${part.id}`} className={inputCls} rows={2} value={part.voiceText} onChange={(e) => update((p) => { p.scenes[si]!.parts[pi]!.voiceText = e.target.value; return p; })} />
                  <div className="mt-2 grid gap-2 sm:grid-cols-2">
                    <div>
                      <label className={labelCls} htmlFor={`tpl-${part.id}`}>Template ở beat nhấn mạnh</label>
                      <select
                        id={`tpl-${part.id}`}
                        className={inputCls}
                        value={part.broll?.templateId ?? ""}
                        onChange={(e) => {
                          const tid = e.target.value;
                          update((p) => {
                            const b = { ...(p.scenes[si]!.parts[pi]!.broll ?? {}) };
                            if (!tid) {
                              delete b.templateId;
                              delete b.inputs;
                            } else {
                              b.templateId = tid;
                              const t = templates.find((x) => x.id === tid);
                              b.inputs = b.inputs ?? {};
                              if (t?.sfxId && !b.sfx) b.sfx = { id: t.sfxId, offsetSec: 0, volume: t.sfxId === "heavy_thud_slam" || t.sfxId === "boom_sub_impact" ? 0.35 : 0.65 };
                            }
                            p.scenes[si]!.parts[pi]!.broll = b;
                            return p;
                          });
                        }}
                      >
                        <option value="">— Không template —</option>
                        {templates.map((t) => (
                          <option key={t.id} value={t.id}>{t.name} ({t.id})</option>
                        ))}
                      </select>
                      {tpl && (
                        <span className="mt-1 flex items-center gap-1 text-xs text-[var(--dim)]">
                          Hướng dẫn dùng template này:
                          <InfoTip text={`Dùng khi: ${tpl.whenToUse.join("; ") || "—"}. Không dùng: ${tpl.notFor.join("; ") || "—"}`} />
                        </span>
                      )}
                    </div>
                    <div>
                      <label className={labelCls} htmlFor={`sfx-${part.id}`}>Hiệu ứng âm thanh (SFX)</label>
                      <select
                        id={`sfx-${part.id}`}
                        className={inputCls}
                        value={part.broll?.sfx?.id ?? ""}
                        onChange={(e) => {
                          const sid = e.target.value;
                          update((p) => {
                            const b = { ...(p.scenes[si]!.parts[pi]!.broll ?? {}) };
                            if (!sid) delete b.sfx;
                            else b.sfx = { id: sid, offsetSec: 0, volume: sid === "heavy_thud_slam" || sid === "boom_sub_impact" ? 0.35 : 0.65 };
                            p.scenes[si]!.parts[pi]!.broll = b;
                            return p;
                          });
                        }}
                      >
                        <option value="">— Không SFX —</option>
                        {sfxList.map((s) => (
                          <option key={s.id} value={s.id}>{s.id}</option>
                        ))}
                      </select>
                      {part.broll?.sfx && <p className="mt-1 text-xs text-[var(--dim)]">Âm lượng {part.broll.sfx.volume} (SFX nặng để 0,35; render còn cap 0,4 + limiter)</p>}
                    </div>
                  </div>
                  <StampsEditor
                    idPrefix={part.id}
                    stamps={part.broll?.stamps ?? []}
                    sfxList={sfxList}
                    onStamps={(next) => update((p) => {
                      const b = { ...(p.scenes[si]!.parts[pi]!.broll ?? {}) };
                      if (next.length === 0) delete b.stamps;
                      else b.stamps = next;
                      p.scenes[si]!.parts[pi]!.broll = b;
                      return p;
                    })}
                  />
                  {tpl && (
                    <div className="mt-2 grid gap-2">
                      {tpl.inputs.map((inp) => (
                        <div key={inp.key}>
                          <label className={labelCls} htmlFor={`in-${part.id}-${inp.key}`}>
                            {inp.key}{inp.required ? " *" : ""}{inp.maxLength ? ` (tối đa ${inp.maxLength} ký tự — chữ phải là số liệu/thông tin thật của part này)` : ""}
                          </label>
                          <input
                            id={`in-${part.id}-${inp.key}`}
                            className={inputCls}
                            maxLength={inp.maxLength ?? undefined}
                            value={String(part.broll?.inputs?.[inp.key] ?? "")}
                            onChange={(e) => update((p) => {
                              const b = { ...(p.scenes[si]!.parts[pi]!.broll ?? {}) };
                              b.inputs = { ...(b.inputs ?? {}), [inp.key]: e.target.value };
                              p.scenes[si]!.parts[pi]!.broll = b;
                              return p;
                            })}
                          />
                        </div>
                      ))}
                      <div>
                        <label className={labelCls} htmlFor={`reveal-${part.id}`}>Hiện lần lượt (reveal) — stage, cách nhau bằng dấu phẩy</label>
                        <input
                          id={`reveal-${part.id}`}
                          className={inputCls}
                          value={(part.broll?.reveal ?? []).join(",")}
                          placeholder="VD: 1,2,5,6"
                          onChange={(e) => update((p) => {
                            const b = { ...(p.scenes[si]!.parts[pi]!.broll ?? {}) };
                            const stages = e.target.value.split(",").map((s) => s.trim()).filter((s) => /^\d+$/.test(s));
                            if (stages.length === 0) delete b.reveal;
                            else b.reveal = stages;
                            p.scenes[si]!.parts[pi]!.broll = b;
                            return p;
                          })}
                        />
                        <p className="mt-1 text-xs text-[var(--dim)]">Chỉ áp cho template full-stage; template không full-stage thì reveal bị bỏ qua. Để trống là không reveal.</p>
                      </div>
                      <TemplatePreviewButton templateId={tpl.id} inputs={toStringInputs(part.broll?.inputs)} projectId={detail.id} />
                    </div>
                  )}
                </div>
              );
            })}
            <button
              type="button"
              className={btnCls}
              onClick={() => update((p) => { const sc = p.scenes[si]!; sc.parts = [...sc.parts, { id: `${sc.id}-part-${sc.parts.length + 1}`, voiceText: "", broll: {} }]; return p; })}
              aria-label={`Thêm part vào cảnh ${scene.order}`}
            >
              + Thêm part vào cảnh {scene.order}
            </button>
          </div>
        </section>
      ))}
    </div>
  );
}
