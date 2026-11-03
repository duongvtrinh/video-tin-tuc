#!/usr/bin/env python3
"""Render ảnh cảnh dạng CARD CHỮ (không phải ảnh AI) cho 1 scene.

    <factory-venv-python> bin/render_scene_card.py <project_id> <order> <out_jpg>

Bối cảnh: các video thật (topic004, hormuz002) dùng ảnh cảnh là card chữ
(kicker + headline + dòng nguồn), không có sceneImagePrompt/mediaPrompt.
App gọi script này trong generateImages cho mọi scene không có prompt AI
và chưa có ảnh seg_<order>_<rand6>.jpg.

Quy tắc cứng (từ QA TOPIC-004 + Hormuz, 26/10/2026):
- Khung theo render_draft.py: 9:16 -> 720x1280, còn lại -> 1280x720.
- Lề an toàn: trái/phải 96px, trên 140px (ở khung 720x1280, scale theo khung).
- Motion Ken Burns tối đa zoom 1.05 cắt tối đa ~34px ngang nên chữ trong
  lề an toàn không bao giờ bị cắt.
- Dòng nguồn dùng template `source-footer-safe` làm mặc định: ngắt tối đa
  3 dòng ngắn, mỗi dòng <= 528px ở khung 720 (max-width của template),
  lề phải luôn >= 96px.

Scene có thể khai trong broll-plan.json:
  headline, kicker, source (dòng nguồn), sourceLabel, cardBg (màu nền),
  cardTemplateId + cardInputs (template overlay thay cho headline vẽ tay).
Plan có thể khai: source, cardBg dùng chung.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
import render_template as rt  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
ACCENT = (251, 191, 36)  # #FBBF24
INK = (245, 245, 240)
DEFAULT_BG = "#20242c"


def font_path(bold: bool) -> str:
    """Font có dấu tiếng Việt: ưu tiên Noto Sans (fc-match :lang=vi)."""
    try:
        q = ":lang=vi:weight=bold" if bold else ":lang=vi"
        out = subprocess.run(["fc-match", q, "file"], capture_output=True,
                             text=True, timeout=10).stdout
        p = out.split(":file=")[-1].strip()
        if p and Path(p).exists():
            return p
    except Exception:
        pass
    cands = [
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in cands:
        if Path(c).exists():
            return c
    return cands[-1]


def wrap(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> list[str]:
    lines: list[str] = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            continue
        cur = words[0]
        for w in words[1:]:
            trial = f"{cur} {w}"
            if draw.textlength(trial, font=font) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def main() -> int:
    pid, order_s, out_path = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    order = int(order_s)
    proj = FACTORY / "projects" / pid
    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    scene = next((s for s in plan.get("scenes", []) if s.get("order") == order), None)
    if scene is None:
        print(f"không thấy scene order={order}", file=sys.stderr)
        return 1

    W, H = (720, 1280) if inp.get("aspectRatio", "9:16") == "9:16" else (1280, 720)
    sx, sy = W / 720, H / 1280
    mx = round(96 * sx)          # lề trái/phải
    top = round(140 * sy)        # lề trên
    max_text_w = W - 2 * mx

    bg = scene.get("cardBg") or plan.get("cardBg") or DEFAULT_BG
    img = Image.new("RGB", (W, H), hex_rgb(bg))
    # QA Chợ nổi 26/10/2026, lỗi 3: card kết luận nền tối che mất ảnh sông,
    # ấn tượng cuối là nền tối. Từ nay scene card được phép khai cardImage
    # (tên file trong build/media/images hoặc đường dẫn tuyệt đối): dùng
    # ảnh đó làm nền thay cho màu tối, chỉ phủ một lớp tối 35% để chữ vẫn
    # đọc được mà ảnh sông vẫn hiện rõ. Mặc định vẫn là nền tối khi không
    # khai cardImage.
    _card_img = scene.get("cardImage") or scene.get("bgImage")
    if _card_img:
        _p = Path(str(_card_img))
        if not _p.is_absolute():
            _cand = proj / "build" / "media" / "images" / _p.name
            _p = _cand if _cand.exists() else _p
        if _p.exists():
            _bg_im = Image.open(_p).convert("RGB")
            # center-crop về đúng tỉ lệ khung, không bóp méo
            _sw, _sh = _bg_im.size
            _scale = max(W / _sw, H / _sh)
            _nw, _nh = round(_sw * _scale), round(_sh * _scale)
            _bg_im = _bg_im.resize((_nw, _nh), Image.LANCZOS)
            _x, _y = (_nw - W) // 2, (_nh - H) // 2
            img = _bg_im.crop((_x, _y, _x + W, _y + H))
            _ov = Image.new("RGBA", (W, H), (0, 0, 0, 90))
            img = Image.alpha_composite(img.convert("RGBA"), _ov).convert("RGB")
    draw = ImageDraw.Draw(img)

    # thanh accent trên cùng (như card Hormuz đã duyệt)
    draw.rectangle([0, 0, W, round(14 * sy)], fill=ACCENT)

    tpl_id = scene.get("cardTemplateId")
    if tpl_id:
        overlay = rt.render_template(tpl_id, scene.get("cardInputs") or {}, W, H)
        if overlay is None:
            print(f"render template {tpl_id} thất bại", file=sys.stderr)
            return 1
        img = rt.composite_center(img.convert("RGB"), overlay)
        draw = ImageDraw.Draw(img)
    else:
        y = top
        kicker = str(scene.get("kicker") or "").strip()
        if kicker:
            f_kick = ImageFont.truetype(font_path(True), round(30 * sx))
            draw.text((mx, y), kicker.upper(), font=f_kick, fill=ACCENT)
            y += round(58 * sy)
        headline = str(scene.get("headline") or scene.get("title") or "").strip()
        if not headline:
            text = str(scene.get("text") or "").strip()
            if not text:
                parts = scene.get("parts") or []
                text = " ".join(str(p.get("voiceText", "")) for p in parts).strip()
            # lấy câu đầu làm headline
            headline = text.split(". ")[0].strip()
            if len(headline) > 110:
                headline = headline[:107].rstrip() + "…"
        if headline:
            f_head = ImageFont.truetype(font_path(True), round(56 * sx))
            for line in wrap(draw, headline, f_head, max_text_w):
                draw.text((mx, y), line, font=f_head, fill=INK)
                y += round(70 * sy)

    # dòng nguồn: template source-footer-safe làm mặc định
    source = str(scene.get("source") or plan.get("source") or "").strip()
    if source:
        label = str(scene.get("sourceLabel") or "Nguồn")
        # đo trước số dòng ở cỡ chữ của template (22px, max-width 528px@720)
        f_meas = ImageFont.truetype(font_path(False), round(22 * sx))
        n_lines = len(wrap(draw, source, f_meas, round(528 * sx)))
        if n_lines > 3:
            print(f"FOOTER-WARN scene {order}: nguồn cần {n_lines} dòng (>3) "
                  f"ở 528px — rút ngắn nguồn hoặc tách scene")
        overlay = rt.render_template(
            "source-footer-safe", {"label": label, "text": source}, W, H)
        if overlay is None:
            print("render source-footer-safe thất bại", file=sys.stderr)
            return 1
        oy = H - overlay.height - round(0.03 * H)
        img.paste(overlay, (mx, oy), overlay)
        print(f"FOOTER-OK scene {order}: {n_lines} dòng, lề phải >= "
              f"{W - mx - overlay.width}px")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=90)
    print(f"CARD-OK {out_path} {W}x{H}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
