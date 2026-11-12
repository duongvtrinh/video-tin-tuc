"""Kiểm chứng 3 template mới bước 2 (trend-badge, share-bar, step-flow) — CEO duyệt 13/11/2026.
Chạy: .venv/bin/python tests/test_new_templates_step2.py
Render qua đường thật (bin/render_template.py, WeasyPrint 70.0 + Anton), assert trên ảnh
render thật theo skill template_render_assertion (không chỉ render không lỗi, không chỉ
soi mắt). Kèm kiểm meta_check: exampleInputs phải PASS, share-bar tổng != 100 phải FAIL.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
FACTORY = HERE.parent
sys.path.insert(0, str(FACTORY / "bin"))
import meta_check as mc  # noqa: E402
import render_template as rt  # noqa: E402

VENV_PY = str(FACTORY / ".venv" / "bin" / "python")
OUT = Path("/tmp/newtpl_assert")

MOSS = np.array([28, 55, 42], dtype=float)
GREEN = np.array([34, 197, 94], dtype=float)   # #22c55e
GOLD = np.array([251, 191, 36], dtype=float)   # #fbbf24
WHITE = np.array([255, 255, 255], dtype=float)
CYAN = np.array([34, 211, 238], dtype=float)   # #22d3ee
PINK = np.array([244, 114, 182], dtype=float)  # #f472b6


def _close(rgb, target, tol=18):
    return np.abs(rgb.astype(float) - target).max(axis=2) <= tol


def _count(rgb, target, tol=18):
    return int(_close(rgb, target, tol).sum())


def render(tid):
    meta = json.loads((FACTORY / "templates" / tid / "meta.json").read_text(encoding="utf-8"))
    inputs = meta["exampleInputs"]
    out = OUT / f"{tid}.png"
    OUT.mkdir(parents=True, exist_ok=True)
    r = subprocess.run([VENV_PY, str(FACTORY / "bin" / "render_template.py"), tid,
                        json.dumps(inputs, ensure_ascii=False), "720", "1280", str(out)],
                       capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"{tid}: render FAIL: {r.stderr[-500:]}"
    assert out.exists(), f"{tid}: không có file PNG"
    return Image.open(out).convert("RGBA"), meta, inputs


def rgb_of(img):
    a = np.asarray(img).astype(float)
    alpha = a[..., 3:4] / 255.0
    return (a[..., :3] * alpha + 0 * (1 - alpha)).astype(np.uint8)


def test_trend_badge():
    img, meta, inputs = render("trend-badge")
    rgb = rgb_of(img)
    assert img.size[0] > 300 and img.size[1] > 100, f"trend-badge: kích thước lạ {img.size}"
    assert _count(rgb, MOSS) > 5000, "trend-badge: thiếu nền rêu #1C372A"
    assert _count(rgb, GREEN) > 300, "trend-badge: thiếu màu xanh lá #22c55e (dir=up: viền + giá trị + mũi tên)"
    assert _count(rgb, WHITE) > 300, "trend-badge: thiếu chữ trắng (label/sub)"
    assert _count(rgb, GOLD) == 0, "trend-badge: dir=up không được có màu vàng (vàng là dir=flat)"
    print("PASS trend-badge: rêu + xanh lá (up) + chữ trắng, không vàng")


def test_share_bar():
    img, meta, inputs = render("share-bar")
    rgb = rgb_of(img)
    assert img.size[0] > 300 and img.size[1] > 200, f"share-bar: kích thước lạ {img.size}"
    assert _count(rgb, MOSS) > 5000, "share-bar: thiếu nền rêu"
    assert _count(rgb, GOLD) > 500, "share-bar: thiếu đoạn vàng (seg1 48%)"
    assert _count(rgb, WHITE) > 500, "share-bar: thiếu đoạn trắng (seg2 32%)"
    assert _count(rgb, CYAN) > 200, "share-bar: thiếu đoạn cyan (seg3 20%)"
    assert _count(rgb, PINK) == 0, "share-bar: count=3 mà còn đoạn hồng (seg4 phải ẩn)"
    # meta_check: exampleInputs tổng 100 phải PASS
    errs = mc.check_all_inputs(meta, inputs)
    assert not errs, f"share-bar: exampleInputs FAIL meta_check: {errs}"
    # meta_check: tổng 110 phải FAIL (ràng buộc sum=100)
    bad = dict(inputs, pct3="30")
    errs_bad = mc.check_all_inputs(meta, bad)
    assert errs_bad, "share-bar: tổng 110 mà meta_check không chặn (mất ràng buộc sum=100)"
    print("PASS share-bar: 3 đoạn vàng/trắng/cyan, không hồng; meta_check PASS tổng 100, FAIL tổng 110")


def test_step_flow():
    img, meta, inputs = render("step-flow")
    rgb = rgb_of(img)
    assert img.size[0] > 300 and img.size[1] > 200, f"step-flow: kích thước lạ {img.size}"
    assert _count(rgb, MOSS) > 5000, "step-flow: thiếu nền rêu"
    assert _count(rgb, GOLD) > 500, "step-flow: thiếu vòng số vàng"
    assert _count(rgb, WHITE) > 500, "step-flow: thiếu chữ trắng (tiêu đề/bước)"
    # đếm vòng số vàng ở cột trái (x < 25% rộng): phải đúng 3 (count=3, step4 ẩn).
    # Bỏ qua viền trên cùng (border-top accent vàng, ~12px đầu) để khỏi đếm nhầm thành vòng số.
    gold = _close(rgb, GOLD)
    left = gold[14:, : img.size[0] // 4]
    rows = np.where(left.any(axis=1))[0]
    assert len(rows) > 0, "step-flow: không tìm thấy vòng số vàng ở cột trái"
    groups, start = 0, rows[0]
    prev = rows[0]
    for y in rows[1:]:
        if y - prev > 6:
            groups += 1
            start = y
        prev = y
    groups += 1
    assert groups == 3, f"step-flow: đếm được {groups} vòng số vàng, kỳ vọng 3 (count=3)"
    errs = mc.check_all_inputs(meta, inputs)
    assert not errs, f"step-flow: exampleInputs FAIL meta_check: {errs}"
    print("PASS step-flow: 3 vòng số vàng + chữ trắng; meta_check PASS")


if __name__ == "__main__":
    test_trend_badge()
    test_share_bar()
    test_step_flow()
    print("ALL PASS: 3 template mới bước 2 (trend-badge, share-bar, step-flow)")
