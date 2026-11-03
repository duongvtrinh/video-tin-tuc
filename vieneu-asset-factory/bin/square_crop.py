#!/usr/bin/env python3
"""Cắt ảnh ngang/vuông thành vuông LẤY GIỮA khung (CEO 2026-11-01).

Ảnh ngang tìm trên internet không còn cắt mù về 9:16: cắt thành vuông
lấy giữa khung. LƯU Ý: pipeline hiện chưa có model saliency nên đây là
cắt giữa, KHÔNG phải focus chủ thể thật — docstring cũ ghi "focus chủ
thể" là sai, đã sửa đợt D5 (01/11/2026). Ảnh vuông render thành composite
blur-fill 3:4 (xem blurfill_image_vf trong render_draft.py).

    python3 square_crop.py <input> <output.jpg>

Ghi đè output, luôn lưu JPEG quality 92.
"""
import sys
from pathlib import Path

from PIL import Image


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: square_crop.py <input> <output.jpg>", file=sys.stderr)
        return 2
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    with Image.open(src) as im:
        im = im.convert("RGB")
        w, h = im.size
        s = min(w, h)
        x, y = (w - s) // 2, (h - s) // 2
        im.crop((x, y, x + s, y + s)).save(dst, "JPEG", quality=92)
    print(f"SQUARE-OK {src.name} {w}x{h} -> {s}x{s} {dst.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
