#!/usr/bin/env python3
"""Kiểm thử hồi quy cho một video đã render (đợt B4, chưa bắt buộc chạy
trong pipeline — chạy tay sau mỗi đợt sửa render/karaoke/template).

    python3 tests/regression_clip.py <project_id>

Kiểm tra, đọc từ project factory (không render lại):
1. Khung hình đúng 720x1280 khi aspectRatio là 9:16.
2. Không part nào bị nền đen: khung giữa mỗi part phải có độ sáng trung
   bình >= 8 (ngưỡng gần-đen; khung đen thật có mean ~0-2).
3. Phụ đề: part KHÔNG template nào cũng phải có karaoke lines > 0.
   Part có template thì lines = 0 là đúng thiết kế, không tính lỗi.
4. Blur-fill: part dùng ảnh ngang/vuông phải có dải mờ trên/dưới yếu hơn
   hẳn cửa sổ nét (năng lượng gradient dải / cửa sổ < 0.5 ở cả hai dải).

In từng kiểm tra dạng REG-PASS / REG-FAIL. Exit 0 khi tất cả pass,
1 khi có fail. Dùng PIL + ffmpeg/ffprobe có sẵn trong môi trường.
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bin"))
from filename import rand6  # noqa: E402

FACTORY = Path.home() / "workspace" / "asset-factory"
TMP = Path("/tmp/regression_clip")
TMP.mkdir(exist_ok=True)


def ffprobe_dims(mp4):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", str(mp4)],
                       capture_output=True, text=True, timeout=30)
    vals = [x for x in r.stdout.strip().split(",") if x.strip()]
    w, h = int(vals[0]), int(vals[1])
    return w, h


def grab(mp4, t, out):
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(mp4),
                    "-frames:v", "1", str(out), "-y"],
                   capture_output=True, timeout=60, check=True)
    from PIL import Image
    import numpy as np
    return np.asarray(Image.open(out).convert("L"), dtype=float)


def main() -> int:
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    mp4 = proj / "export" / f"{pid}_preview.mp4"
    fails = []

    def check(name, ok, detail=""):
        print(f"{'REG-PASS' if ok else 'REG-FAIL'} {name} {detail}")
        if not ok:
            fails.append(name)

    w, h = ffprobe_dims(mp4)
    expect = (720, 1280) if plan.get("aspectRatio") == "9:16" else None
    check("dims", expect is None or (w, h) == expect, f"{w}x{h}")

    karaoke = json.loads(
        (proj / "build/subtitles/karaoke.json").read_text(encoding="utf-8"))
    lines_by_id = {e.get("partId"): len(e.get("lines") or [])
                   for e in karaoke if isinstance(e, dict)}
    tpl_ids = {p["id"] for sc in plan["scenes"] for p in sc["parts"]
               if (p.get("broll") or {}).get("templateId")}
    build = proj / "build"

    for sc in plan["scenes"]:
        order = sc["order"]
        simg = next((q for ext in ("jpg", "png", "webp")
                     for q in [build / "media" / "images" /
                               f"seg_{order}_{rand6(pid, 'img', str(order))}.{ext}"]
                     if q.exists()), None)
        for pi, p in enumerate(sc["parts"], start=1):
            k = next((e for e in karaoke if isinstance(e, dict)
                      and e.get("partId") == p["id"]), None)
            if not k:
                check(f"part {p['id']} karaoke-entry", False, "thiếu entry")
                continue
            mid = (k["startSec"] + k["endSec"]) / 2
            frame = grab(mp4, mid, TMP / f"{p['id']}.jpg")
            mean = float(frame.mean())
            check(f"part {p['id']} not-black", mean >= 8,
                  f"mean={mean:.1f} t={mid:.2f}s")
            n_lines = lines_by_id.get(p["id"], 0)
            if p["id"] not in tpl_ids:
                check(f"part {p['id']} karaoke-lines", n_lines > 0,
                      f"lines={n_lines}")
            # Blur-fill: chỉ xét khi ảnh part là ngang/vuông.
            bimg = build / "media" / "broll" / (
                f"broll_seg_{order}_part_{pi}_"
                f"{rand6(pid, 'broll', str(order), str(pi))}.jpg")
            img = bimg if bimg.exists() else simg
            if img is not None:
                from PIL import Image
                iw, ih = Image.open(img).size
                if iw >= ih:  # ngang/vuông -> phải có dải mờ
                    import numpy as np
                    gy = np.abs(np.diff(frame, axis=0)).mean(axis=1)
                    top = gy[10:150].mean()
                    win = gy[200:1080].mean()
                    bot = gy[1130:1270].mean()
                    ok = win > 0 and top / win < 0.5 and bot / win < 0.5
                    check(f"part {p['id']} blur-bands", ok,
                          f"top={top:.2f} win={win:.2f} bot={bot:.2f}")
    print(f"REG-SUMMARY {pid}: {'PASS' if not fails else 'FAIL ' + str(fails)}")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
