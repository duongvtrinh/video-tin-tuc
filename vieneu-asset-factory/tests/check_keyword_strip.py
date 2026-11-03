#!/usr/bin/env python3
"""Test yêu cầu cho template keyword-strip (luật CEO 02/11/2026).

Mỗi lần sửa template phải chạy test này và ĐẠT trước khi xác nhận.
check_templates.py chỉ bắt lỗi render, không bắt sai thiết kế — test này
assert trực tiếp trên ảnh render thật theo đúng yêu cầu:
  - không viền ngoài, không nền ngoài (góc trong suốt, không vàng ở mép ảnh)
  - từng ô keyword CÓ nền tối (không phải trắng 6% coi như không nền)
  - đúng 3 ô, dòng dẫn vẫn hiện

Chạy bằng asset-factory/.venv (có weasyprint + PIL).
Thoát 0 khi mọi kiểm tra đạt, 1 khi có kiểm tra rớt.
"""
import json
import subprocess
import sys
from collections import deque
from pathlib import Path

FACTORY = Path.home() / "workspace" / "asset-factory"
sys.path.insert(0, str(FACTORY / "bin"))
from PIL import Image  # noqa: E402


def is_gold(r, g, b, a):
    # Vàng nhấn: tông ấm r>g>b, chênh r-b rõ. Viền vàng 55% trên nền tối
    # hợp thành (141,112,27) nên không dùng ngưỡng r>200 như khi viền trên
    # nền trong suốt; nền tối (8,10,16) và chữ trắng đều trượt tông ấm này.
    return a > 100 and r > g > b and (r - b) > 60 and r > 100


def is_dark(r, g, b, a):
    return a >= 200 and max(r, g, b) <= 80


def is_white_text(r, g, b, a):
    return a > 150 and min(r, g, b) > 200


def gold_components(px, w, h):
    """Các cụm pixel vàng liên thông 4-hướng (mỗi ô = 1 khung viền kín)."""
    seen = [[False] * w for _ in range(h)]
    comps = []
    for y in range(h):
        for x in range(w):
            if seen[y][x]:
                continue
            seen[y][x] = True
            r, g, b, a = px[x, y]
            if not is_gold(r, g, b, a):
                continue
            q = deque([(x, y)])
            xs, ys = [x], [y]
            while q:
                cx, cy = q.popleft()
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx]:
                        seen[ny][nx] = True
                        nr, ng, nb, na = px[nx, ny]
                        if is_gold(nr, ng, nb, na):
                            q.append((nx, ny))
                            xs.append(nx)
                            ys.append(ny)
            comps.append((min(xs), min(ys), max(xs), max(ys)))
    return comps


def main():
    meta = json.loads((FACTORY / "templates" / "keyword-strip" / "meta.json").read_text())
    inputs = meta["exampleInputs"]
    out = "/tmp/keyword-strip-requirements.png"
    r = subprocess.run(
        [str(FACTORY / ".venv" / "bin" / "python"),
         str(FACTORY / "bin" / "render_template.py"),
         "keyword-strip", json.dumps(inputs), "720", "1280", out],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL render: {r.stdout} {r.stderr}")
        return 1
    im = Image.open(out).convert("RGBA")
    w, h = im.size
    px = im.load()
    fails = []

    def check(name, ok, detail=""):
        print(f"{'PASS' if ok else 'FAIL'} {name} {detail}")
        if not ok:
            fails.append(name)

    # C1: không nền ngoài — 4 góc trong suốt hoàn toàn.
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    check("C1-goc-trong-suot", all(c[3] == 0 for c in corners), str(corners))

    # C2: đúng 3 ô (3 khung viền vàng), mỗi ô đủ lớn.
    # C2: đúng 3 ô — chỉ tính cụm đủ cỡ ô; mép dưới viền bị khử răng cưa
    # tách thành mảnh 1-2px nên phải lọc mảnh vụn trước khi đếm.
    comps = gold_components(px, w, h)
    comps = [c for c in comps if c[2] - c[0] > 40 and c[3] - c[1] > 20]
    check("C2-dung-3-o", len(comps) == 3, f"o-hop-le={len(comps)} {comps}")

    # C3: từng ô CÓ nền tối — 4 góc trong của ô đều tối và đục.
    # C3b: đúng màu thống nhất — mực #080A10 alpha .8 (danh nghĩa
    # (8,10,16,204); WeasyPrint làm tròn premultiply nên cho sai số ±3).
    for i, (x0, y0, x1, y1) in enumerate(sorted(comps)):
        samples = [px[x0 + 4, y0 + 4], px[x1 - 4, y0 + 4],
                   px[x0 + 4, y1 - 4], px[x1 - 4, y1 - 4]]
        check(f"C3-o{i + 1}-nen-toi", all(is_dark(*s) for s in samples), str(samples))
        check(f"C3b-o{i + 1}-muc-chuan-alpha-8",
              all(abs(s[0] - 8) <= 3 and abs(s[1] - 10) <= 3
                  and abs(s[2] - 16) <= 3 and abs(s[3] - 204) <= 3
                  for s in samples), str(samples))

    # C4: nền tối chiếm diện tích thật, không phải vài pixel lẻ.
    dark_n = sum(1 for y in range(h) for x in range(w) if is_dark(*px[x, y]))
    check("C4-nen-toi-du-lon", dark_n > 3000, f"dark-px={dark_n}")

    # C5: không viền ngoài — không pixel vàng nào chạm mép ảnh.
    edge_gold = sum(
        1 for y in range(h) for x in range(w)
        if (x < 3 or x >= w - 3 or y < 3 or y >= h - 3) and is_gold(*px[x, y]))
    check("C5-khong-vien-ngoai", edge_gold == 0, f"edge-gold-px={edge_gold}")

    # C6: dòng dẫn vẫn hiện (chữ trắng phía trên dải ô).
    if comps:
        band_top = min(c[1] for c in comps)
        head_white = sum(1 for y in range(band_top) for x in range(w)
                         if is_white_text(*px[x, y]))
        check("C6-dong-dan-hien", head_white > 50, f"head-white-px={head_white}")

    print(f"KET-QUA: {'DAT' if not fails else 'ROT ' + ','.join(fails)} (anh {w}x{h})")
    return 0 if not fails else 1


if __name__ == "__main__":
    raise SystemExit(main())
