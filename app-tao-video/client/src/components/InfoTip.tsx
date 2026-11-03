// File tách từ App.tsx (giai đoạn 3 đợt riêng, 03/11) — hành vi không đổi,
// chỉ di chuyển nguyên văn sang module riêng để dễ đọc/bảo trì.
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

// Chú thích dài không để inline nữa (luật UX 02/11): gọn giao diện bằng
// nút ⓘ — hover/focus thấy qua title, bấm (điện thoại) thì mở bong bóng
// tooltip, bấm lại hoặc rời focus thì đóng.
// Luật tooltip 03/11: bong bóng phải nằm trọn trong màn hình, không vượt
// khỏi phạm vi màn hình (vượt là bị che, không thấy nội dung). Bong bóng
// cũ dùng absolute theo nút nên bị khung cha (overflow) cắt và tràn mép
// khi nút ở gần biên. Nay render qua portal ra body với position:fixed,
// đo vị trí nút rồi kẹp trong viewport: điện thoại full chiều rộng
// (trừ lề 8px hai bên), máy tính tối đa 700px; chiều dọc ưu tiên dưới
// nút, thiếu chỗ thì lật lên trên, cao tối đa bằng khoảng trống còn lại
// và cuộn trong bong bóng nếu chú thích dài hơn.
export function InfoTip({ text, label = "Xem chú thích" }: { text: string; label?: string }) {
  const [open, setOpen] = useState(false);
  const btnRef = useRef<HTMLButtonElement | null>(null);
  const [box, setBox] = useState<{
    left: number;
    width: number;
    top: number | null;
    bottom: number | null;
    maxH: number;
  } | null>(null);

  const place = () => {
    const btn = btnRef.current;
    if (!btn) return;
    const r = btn.getBoundingClientRect();
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const margin = 8;
    const gap = 6;
    const width = vw < 640 ? vw - margin * 2 : Math.min(700, vw - margin * 2);
    const center = r.left + r.width / 2;
    const left = Math.min(Math.max(center - width / 2, margin), vw - margin - width);
    const spaceBelow = vh - r.bottom - gap - margin;
    const spaceAbove = r.top - gap - margin;
    if (spaceBelow >= 140 || spaceBelow >= spaceAbove) {
      setBox({ left, width, top: r.bottom + gap, bottom: null, maxH: Math.max(spaceBelow, 80) });
    } else {
      setBox({ left, width, top: null, bottom: vh - r.top + gap, maxH: Math.max(spaceAbove, 80) });
    }
  };

  // Vị trí fixed tính theo viewport nên khi cuộn/resize lúc bong bóng
  // đang mở thì đóng lại, tránh bong bóng trôi lệch khỏi nút.
  useEffect(() => {
    if (!open) return;
    const close = () => setOpen(false);
    window.addEventListener("scroll", close, true);
    window.addEventListener("resize", close);
    return () => {
      window.removeEventListener("scroll", close, true);
      window.removeEventListener("resize", close);
    };
  }, [open ]);

  return (
    <span className="inline-flex align-middle">
      <button
        ref={btnRef}
        type="button"
        className="ml-1 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface2)] text-[11px] font-bold text-[var(--dim)] active:opacity-70"
        aria-label={label}
        aria-expanded={open}
        title={text}
        onClick={() => {
          if (!open) place();
          setOpen((v) => !v);
        }}
        onBlur={() => setOpen(false)}
      >
        i
      </button>
      {open &&
        box &&
        createPortal(
          <span
            role="tooltip"
            style={{
              left: box.left,
              width: box.width,
              top: box.top ?? undefined,
              bottom: box.bottom ?? undefined,
              maxHeight: box.maxH,
            }}
            className="fixed z-[100] block overflow-y-auto rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 text-left text-xs font-normal normal-case leading-relaxed tracking-normal text-[var(--text)] shadow-xl"
          >
            {text}
          </span>,
          document.body,
        )}
    </span>
  );
}
