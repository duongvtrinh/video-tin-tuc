#!/usr/bin/env python3
"""Render all factory templates over ONE real background photo, placed
exactly like render_draft.py (law 31/10/2026): subtitle-margin bottom
(256px at 720x1280), clip-caption at edge bottom (38px), preview-banner /
keyword-block flush bottom, full-stage templates full-frame. No template
sits at top since the evening of 31/10/2026 (TOP_IDS is empty). Outputs composited frames,
labelled contact sheets and a manifest."""
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# Như bin/*.py: máy gốc giữ symlink cũ, bản clone resolve từ vị trí file test.
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
VENV_PY = FACTORY / ".venv/bin/python"
_BG_ENV = os.environ.get("TEMPLATE_CHECK_BG")
BG_SRC = Path(_BG_ENV) if _BG_ENV else FACTORY / "projects/topic086001/build/media/images/seg_4_105210.jpg"
OUT = Path(os.environ.get("TEMPLATE_CHECK_OUT", str(Path(__file__).resolve().parent / "output" / "template-check")))
FRAMES = OUT / "frames"
SHEETS = OUT / "sheets"
W, H = 720, 1280
MARGIN_V = 256  # 20% of 1280, same formula as karaoke.py for 9:16
EDGE = int(H * 0.03)  # 38
TOP_IDS = set()  # bãi bỏ tối 31/10/2026: không template nào ở top nữa
EDGE_IDS = {"clip-caption"}  # caption sát đáy theo thiết kế (lệnh CEO 31/10/2026); story-title đã về bottom chung
FLUSH_IDS = {"preview-banner", "keyword-block"}  # đặc thù: phủ kín ngang, sát đáy khung

FRAMES.mkdir(parents=True, exist_ok=True)
SHEETS.mkdir(parents=True, exist_ok=True)

# Background: cover-crop photo to 720x1280. BG mẫu là project cũ không có
# trong repo: nếu thiếu thì tạo nền gradient tổng hợp để test vẫn chạy được.
if BG_SRC.exists():
    bg = Image.open(BG_SRC).convert("RGB")
    bw, bh = bg.size
    scale = max(W / bw, H / bh)
    bg = bg.resize((round(bw * scale), round(bh * scale)), Image.LANCZOS)
    left, top = (bg.width - W) // 2, (bg.height - H) // 2
    bg = bg.crop((left, top, left + W, top + H))
else:
    print(f"BG mẫu {BG_SRC} không có trong repo — tạo nền gradient tổng hợp")
    grad = Image.new("RGB", (1, H))
    grad.putdata([(int(30 + 60 * y / H), int(40 + 50 * y / H), int(70 + 60 * y / H)) for y in range(H)])
    bg = grad.resize((W, H))
bg.save(OUT / "background_used.jpg", quality=90)

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
font_big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)


def placeholder(tid, msg):
    im = bg.copy()
    d = ImageDraw.Draw(im)
    d.rectangle([0, 600, W, 680], fill=(160, 0, 0))
    d.text((20, 615), f"{tid}: {msg}", fill=(255, 255, 255), font=font_big)
    return im


manifest = []
templates = sorted(p for p in (FACTORY / "templates").iterdir() if p.is_dir() and not p.name.startswith("_"))
for tdir in templates:
    tid = tdir.name
    meta = json.loads((tdir / "meta.json").read_text(encoding="utf-8"))
    ex = {k: ("" if v is None else str(v)) for k, v in (meta.get("exampleInputs") or {}).items()}
    png = OUT / f"tmp_{tid}.png"
    r = subprocess.run(
        [str(VENV_PY), "bin/render_template.py", tid, json.dumps(ex, ensure_ascii=False),
         str(W), str(H), str(png)],
        cwd=FACTORY, capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not png.exists():
        placeholder(tid, "RENDER FAIL").save(FRAMES / f"{tid}.jpg", quality=88)
        manifest.append(f"{tid} | RENDER-FAIL | {r.stderr.strip()[-200:]}")
        print(f"{tid}: RENDER-FAIL", flush=True)
        continue
    ov = Image.open(png).convert("RGBA")
    ow, oh = ov.size
    fullstage = abs(ow / oh - W / H) < 0.05 and ow >= int(W * 0.90) and oh >= int(H * 0.90)
    if fullstage:
        ov2 = ov.resize((W, H), Image.LANCZOS)
        x, y, place = 0, 0, "fullstage"
    elif tid in FLUSH_IDS:
        ov2 = ov
        x, y, place = 0, H - ov2.size[1], "flush-bottom"
    else:
        sw, sh = int(W * 0.92), int(H * 0.80)
        s = min(1.0, sw / ow, sh / oh)
        if s < 1.0:
            ov2 = ov.resize((round(ow * s), round(oh * s)), Image.LANCZOS)
        else:
            ov2 = ov
        w2, h2 = ov2.size
        x = (W - w2) // 2
        if tid in TOP_IDS:
            y, place = EDGE, "top"
        elif tid in EDGE_IDS:
            y, place = H - h2 - EDGE, "edge-bottom"
        else:
            y, place = H - h2 - MARGIN_V, "subtitle-bottom"
    frame = bg.copy()
    frame.paste(ov2, (x, y), ov2)
    frame.save(FRAMES / f"{tid}.jpg", quality=88)
    manifest.append(f"{tid} | {place} | png={ow}x{oh} | placed={ov2.size[0]}x{ov2.size[1]} @ x={x},y={y}")
    print(f"{tid}: {place} png={ow}x{oh} @ x={x},y={y}", flush=True)
    png.unlink(missing_ok=True)

# Contact sheets: 5 cols, tile 240 wide + 24px id header
ids = [p.name for p in sorted((FACTORY / "templates").iterdir()) if p.is_dir() and not p.name.startswith("_")]
tiles = []
for tid in ids:
    fr = Image.open(FRAMES / f"{tid}.jpg")
    tw = 240
    th = round(fr.height * tw / fr.width)
    tile = Image.new("RGB", (tw, th + 24), (0, 0, 0))
    tile.paste(fr.resize((tw, th), Image.LANCZOS), (0, 24))
    d = ImageDraw.Draw(tile)
    d.text((6, 3), tid, fill=(255, 200, 40), font=font)
    tiles.append(tile)
COLS = 5
PER = 15
for si in range(0, len(tiles), PER):
    batch = tiles[si:si + PER]
    rows = (len(batch) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * 240, rows * (427 + 24)), (20, 20, 20))
    for i, t in enumerate(batch):
        sheet.paste(t, ((i % COLS) * 240, (i // COLS) * (427 + 24)))
    sheet.save(SHEETS / f"sheet{si // PER + 1}.png")

with zipfile.ZipFile(OUT / "template-check-20261031-frames.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(FRAMES.glob("*.jpg")):
        z.write(f, f.name)
(OUT / "manifest.txt").write_text("\n".join(manifest) + "\n", encoding="utf-8")
print("DONE", len(ids), "templates;", "sheets:", len(list(SHEETS.glob('*.png'))))
print("\n".join(manifest))
