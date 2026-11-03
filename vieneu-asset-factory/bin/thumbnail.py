#!/usr/bin/env python3
"""Tạo thumbnail YouTube (1280x720) tự động cho project.

Chọn 2-3 khoảnh khắc đắt (part có template chữ hoặc giữa scene),
lấy ảnh nền + phủ tiêu đề -> 3 mẫu khác nhau.

    python3 thumbnail.py <project_id> ["Tiêu đề tùy chọn"]

Ghi: projects/<id>/export/<id>_thumb_1.jpg (2, 3)
"""
import json
import subprocess
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import rand6  # noqa: E402

from PIL import Image, ImageDraw, ImageFont

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
W, H = 1280, 720
GOLD = (251, 191, 36)


def font(size, bold=True):
    for name in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                 if bold else
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def base_image(proj, pid, order, pi):
    b = (proj / "build" / "media" / "broll" /
         f"broll_seg_{order}_part_{pi}_{rand6(pid, 'broll', str(order), str(pi))}.jpg")
    if b.exists():
        return Image.open(b).convert("RGB")
    s = (proj / "build" / "media" / "images" /
         f"seg_{order}_{rand6(pid, 'img', str(order))}.jpg")
    if s.exists():
        return Image.open(s).convert("RGB")
    return None


def cover(im, w=W, h=H):
    """Scale-to-cover + crop giữa, tối nhẹ 2 viền để chữ nổi."""
    r = max(w / im.width, h / im.height)
    im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    im = im.crop((x, y, x + w, y + h))
    # gradient tối dưới + trên
    overlay = Image.new("L", (1, h), 0)
    for yy in range(h):
        v = 0
        if yy > h * 0.55:
            v = int(140 * (yy - h * 0.55) / (h * 0.45))
        elif yy < h * 0.25:
            v = int(90 * (1 - yy / (h * 0.25)))
        overlay.putpixel((0, yy), v)
    overlay = overlay.resize((w, h))
    black = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(black, im, overlay)


def draw_text_stroke(d, xy, text, fnt, fill, stroke=3):
    d.text(xy, text, font=fnt, fill=fill, stroke_width=stroke,
           stroke_fill=(0, 0, 0))


def thumb1(base, title):
    """Mẫu 1: chữ to dưới-trái + gạch vàng."""
    im = cover(base.copy())
    d = ImageDraw.Draw(im)
    d.rectangle([60, H - 300, 76, H - 120], fill=GOLD)
    fnt = font(72)
    lines = textwrap.wrap(title, width=16)[:2]
    y = H - 300
    for ln in lines:
        draw_text_stroke(d, (110, y), ln, fnt, (255, 255, 255))
        y += 92
    return im


def thumb2(base, title):
    """Mẫu 2: dải đen trên + chữ vàng giữa."""
    im = cover(base.copy())
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, W, 210], fill=(0, 0, 0, 255))
    fnt = font(64)
    lines = textwrap.wrap(title, width=22)[:2]
    y = 40
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=fnt)
        tw = bb[2] - bb[0]
        draw_text_stroke(d, ((W - tw) // 2, y), ln, fnt, GOLD)
        y += 80
    return im


def thumb3(base, title, quote):
    """Mẫu 3: kiểu quote-card — trích dẫn nổi bật."""
    im = cover(base.copy())
    d = ImageDraw.Draw(im)
    # card mờ giữa
    card = Image.new("RGB", (W - 240, 300), (12, 14, 20))
    im.paste(card, (120, (H - 300) // 2))
    d = ImageDraw.Draw(im)
    d.rectangle([120, (H - 300) // 2, 136, (H + 300) // 2], fill=GOLD)
    fnt = font(54)
    lines = textwrap.wrap(quote or title, width=26)[:3]
    y = (H - 300) // 2 + 40
    for ln in lines:
        draw_text_stroke(d, (180, y), ln, fnt, (255, 255, 255), stroke=2)
        y += 72
    return im


def main() -> int:
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    tts = json.loads((proj / "tts.json").read_text(encoding="utf-8"))
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    title = sys.argv[2] if len(sys.argv) > 2 else inp.get("topic", "Video")
    # rút gọn tiêu đề cho thumbnail
    title = title.replace("Kịch bản ", "").strip()
    if len(title) > 60:
        title = title[:57] + "..."

    # chọn 3 part đắt: ưu tiên part có template chữ, rải đều video
    tpl_parts = []
    for sc in plan["scenes"]:
        for p in sc["parts"]:
            br = p.get("broll") or {}
            if br.get("templateId"):
                tpl_parts.append((sc["order"], sc["parts"].index(p) + 1, p))
    picks = []
    if tpl_parts:
        idxs = [0, len(tpl_parts) // 2, len(tpl_parts) - 1]
        for ii in dict.fromkeys(idxs):
            picks.append(tpl_parts[ii])
    else:
        mid = len(tts["parts"]) // 2
        for p in [tts["parts"][0], tts["parts"][mid], tts["parts"][-1]]:
            picks.append((p["sceneOrder"], p["partIdx"], p))
    # quote cho mẫu 3
    quote = ""
    for sc in plan["scenes"]:
        for p in sc["parts"]:
            br = p.get("broll") or {}
            if br.get("templateId") == "quote-card":
                quote = (br.get("inputs") or {}).get("text", "")
                break

    makers = [(thumb1, (title,)), (thumb2, (title,)), (thumb3, (title, quote))]
    out_dir = proj / "export"
    out_dir.mkdir(parents=True, exist_ok=True)
    made = 0
    for i, (order, pi, _) in enumerate(picks[:3]):
        base = base_image(proj, pid, order, pi)
        if base is None:
            continue
        fn, args = makers[i]
        im = fn(base, *args)
        out = out_dir / f"{pid}_thumb_{i + 1}.jpg"
        im.save(out, quality=90)
        print(f"THUMB-OK {out}")
        made += 1
    if not made:
        print("không có ảnh nền để làm thumbnail", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
