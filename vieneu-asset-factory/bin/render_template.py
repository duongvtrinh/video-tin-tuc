#!/usr/bin/env python3
"""Render b-roll text template (HTML/CSS của VieNeu) thành ảnh để composite lên video.

Dùng WeasyPrint rasterize template đã điền inputs -> PDF -> PNG -> crop nội dung.
Chạy bằng asset-factory/.venv (có weasyprint).
"""
import html as htmlmod
import json
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
ACCENT = "#FBBF24"
# Bảng màu chuẩn (PALETTE.md 31/10/2026) cho accent của template.
ACCENT_HEX = {
    "gold": "#FBBF24",
    "red": "#EF4444",
    "cyan": "#22D3EE",
    "green": "#22C55E",
    "pink": "#F472B6",
    "purple": "#A78BFA",
    "orange": "#FB923C",
}


def resolve_accent(template_id: str, inputs: dict) -> str:
    """Màu nhấn (--broll-accent) của template, đợt D4 (CEO quyết giữ
    accent, 01/11/2026): ưu tiên inputs['accent'] nếu plan/host truyền
    tên màu, rồi accent.default trong meta.json của template, cuối cùng
    vàng #FBBF24. Trước D4, mọi đường đều gán cứng vàng nên accent
    trong meta (vd breaking-banner đỏ) không bao giờ có tác dụng."""
    name = (inputs or {}).get("accent")
    if isinstance(name, str) and name in ACCENT_HEX:
        return ACCENT_HEX[name]
    try:
        meta = json.loads(
            (FACTORY / "templates" / template_id / "meta.json").read_text(
                encoding="utf-8"))
        default = (meta.get("accent") or {}).get("default")
        if isinstance(default, str) and default in ACCENT_HEX:
            return ACCENT_HEX[default]
    except Exception:
        pass
    return ACCENT


def fill_placeholders(tpl: str, inputs: dict) -> str:
    # QA Chợ nổi 26/10/2026: đường render tĩnh trước đây chèn nguyên chuỗi
    # items vào <ul> mà không tạo <li>, nên chữ checklist rơi về màu đen
    # mặc định của trình duyệt trên banner tối, chìm hẳn, và xuống dòng bị
    # gộp thành một dòng. Phải chuyển items thành <li class="broll-item">
    # để CSS checklist (.broll-item màu trắng) áp dụng cho đường render.
    def rep(m):
        key = m.group(1)
        v = inputs.get(key, "")
        if key == "items":
            if isinstance(v, list):
                lines = [str(x) for x in v if str(x).strip()]
            else:
                lines = [ln for ln in str(v).splitlines() if ln.strip()]
            return "".join(
                f'<li class="broll-item">{htmlmod.escape(ln)}</li>'
                for ln in lines)
        ev = htmlmod.escape(str(v))
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", ev)
    return re.sub(r"\{\{(\w+)\}\}", rep, tpl)


def _render_on_bg(template_id: str, body: str, css: str, W: int, H: int,
                  bg: str, accent: str) -> "Image.Image | None":
    """Render template lên nền màu bg, trả về PIL RGB."""
    # class orientation cho template: đường render tĩnh (WeasyPrint) không
    # đánh giá @media orientation nên template cần class tường minh
    # (vd versus-split 9:16 xếp dọc thay vì ngang).
    orient = "portrait" if H > W else "landscape"
    page = f"""<html><head><meta charset="utf-8"><style>
@page {{ size: {W}px {H}px; margin: 0; }}
:root {{--broll-accent:{accent}; }}
{css}
body {{ margin:0; width:{W}px; height:{H}px; display:flex;
        align-items:center; justify-content:center; background:{bg}; }}
</style></head><body class="{orient}">{body}</body></html>"""
    try:
        from weasyprint import HTML
        with tempfile.TemporaryDirectory() as tmp:
            pdf = str(Path(tmp) / "t.pdf")
            png = str(Path(tmp) / "t")
            HTML(string=page).write_pdf(pdf)
            # WeasyPrint ghi 1 CSS px = 1pt (72/96). pdftoppm -r 72 cho ra
            # ảnh 0.75x kích thước CSS -> overlay trong video nhỏ hơn
            # preview ~28% (đo thực tế: card stat video cũ 640px, PNG cũ
            # chỉ 499px). -r 96 khôi phục 1 CSS px = 1 PNG px để overlay
            # khớp kích thước preview (fit 92%/80% chỉ co khi vượt khung).
            r = subprocess.run(
                ["pdftoppm", "-png", "-r", "96", "-singlefile", pdf, png],
                capture_output=True, timeout=120)
            if r.returncode != 0:
                return None
            return Image.open(png + ".png").convert("RGB")
    except Exception:
        return None


def render_template(template_id: str, inputs: dict, W: int = 1280,
                    H: int = 720) -> Image.Image | None:
    """Trả về PIL RGBA của template (alpha thật, tách bằng matting 2 nền)."""
    import numpy as np
    tdir = FACTORY / "templates" / template_id
    html_path = tdir / "template.html"
    css_path = tdir / "style.css"
    if not html_path.exists():
        return None
    body = fill_placeholders(html_path.read_text(encoding="utf-8"), inputs or {})
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    # bỏ bóng đổ: khó tách alpha ở vùng shadow mềm. LƯU Ý: pattern cũ
    # [^;]+ ăn qua dấu } khi shadow là khai báo cuối rule (không có ;)
    # và phá hỏng rule kế tiếp (unit stat-counter, text date-stamp,
    # badge versus-split bị nuốt vào rule trước) -> phải dừng ở }
    # (không ăn }) và ; cuối là tùy chọn.
    css = re.sub(r"box-shadow\s*:[^;}]+;?", "", css)
    css = re.sub(r"text-shadow\s*:[^;}]+;?", "", css)
    # Render tĩnh (WeasyPrint) không chạy animation CSS: các template có
    # animation vào (vd checklist .broll-item opacity:0 -> 1 theo delay)
    # sẽ bị kẹt ở trạng thái đầu và chữ biến mất. Ép trạng thái cuối cho
    # đường tĩnh để chữ luôn hiện trắng, đúng như frame hold của đường
    # animation Chrome. Đây là phần thứ hai của lỗi checklist QA Chợ nổi.
    css += ("\n.broll-item{opacity:1 !important;transform:none !important;"
            "animation:none !important}\n")
    img_w = _render_on_bg(template_id, body, css, W, H, "#FFFFFF",
                          resolve_accent(template_id, inputs or {}))
    img_b = _render_on_bg(template_id, body, css, W, H, "#000000",
                          resolve_accent(template_id, inputs or {}))
    if img_w is None or img_b is None:
        return None
    w = np.asarray(img_w).astype(float)
    b = np.asarray(img_b).astype(float)
    # Cw = F*a + 255*(1-a); Cb = F*a  ->  a = 1 - mean(Cw-Cb)/255
    alpha = np.clip(1.0 - (w - b).mean(axis=2) / 255.0, 0, 1)
    a_safe = np.maximum(alpha, 1e-6)[..., None]
    fg = np.clip(b / a_safe, 0, 255)
    rgba = np.dstack([fg, alpha * 255]).astype(np.uint8)
    # crop theo alpha
    ys, xs = (alpha > 0.02).nonzero()
    if len(xs) == 0:
        return None
    pad = 6
    x0, x1 = max(0, xs.min() - pad), min(rgba.shape[1], xs.max() + pad)
    y0, y1 = max(0, ys.min() - pad), min(rgba.shape[0], ys.max() + pad)
    return Image.fromarray(rgba[y0:y1, x0:x1], "RGBA")


def composite_center(base: Image.Image, overlay: Image.Image) -> Image.Image:
    """Dán overlay vào giữa base (giữ tỉ lệ, không vượt quá 92% khung)."""
    bw, bh = base.size
    ow, oh = overlay.size
    scale = min(1.0, (bw * 0.92) / ow, (bh * 0.80) / oh)
    if scale < 1.0:
        overlay = overlay.resize((int(ow * scale), int(oh * scale)),
                                 Image.LANCZOS)
        ow, oh = overlay.size
    out = base.copy()
    out.paste(overlay, ((bw - ow) // 2, (bh - oh) // 2), overlay)
    return out


if __name__ == "__main__":
    import json as _json
    import sys as _sys
    _tid, _inputs_json, _W, _H, _out = _sys.argv[1:6]
    _inputs = _json.loads(_inputs_json)
    _im = render_template(_tid, _inputs, int(_W), int(_H))
    if _im is None:
        print("RENDER-FAIL", file=_sys.stderr)
        raise _sys.exit(1)
    _im.save(_out)
    print(f"RENDER-OK {_out}")
