#!/usr/bin/env python3
"""Tạo ảnh cảnh cho Asset Factory, hai đường song song, cùng chuẩn tên file.

Usage: python3 gen_images.py jobs.json

Mỗi job là một dict, app (artifact vieneu-asset-factory, action
generateImages) xây jobs từ broll-plan.json của project:

1. Ảnh AI (đường cũ, không đổi):
   {"prompt": "...", "out": "/path.jpg", "orientation": "vertical"}
   -> media-generation CLI (4 luồng song song), ffmpeg chuyển về JPG đúng tên.

2. Ảnh cảnh dạng CARD CHỮ (mới, audit repo-vs-app 27/10/2026):
   {"card_pid": "<pid>", "card_order": <order>, "out": "/path.jpg"}
   -> bin/render_scene_card.py <pid> <order> <out>, dùng factory venv.
   Đường này là bắt buộc cho các project thật như topic004, hormuz002,
   vì ảnh cảnh của chúng là card chữ (kicker + headline + dòng nguồn
   source-footer-safe), KHÔNG có sceneImagePrompt/mediaPrompt.
   Trước đây app chỉ xây job AI nên plan kiểu này trả jobCount 0 —
   không phải plan thiếu ảnh, mà là gen_images chưa biết đường card.
   App phải xây cả hai loại job, hoặc gọi render_scene_card trực tiếp
   cho scene không có prompt AI; gen_images ở đây chỉ là điểm vào chung.

Tính chất quan trọng cho app (timeout 30s của action):
- Job nào đã có file out hợp lệ (>0 byte) thì BỎ QUA, trừ khi job khai
  "force": true. Lần chạy thứ hai sau timeout vì vậy chỉ làm tiếp phần
  chưa xong, không chạy lại toàn bộ và không phá ảnh đã tạo.
- Tên file out LUÔN lấy từ bin/filename.py (rand6), không tự đặt tên
  ngẫu nhiên — render_draft/preflight/thumbnail đều tra cứu theo tên này,
  tên sai là ra MP4 nền đen.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
VENV_PY = FACTORY / ".venv" / "bin" / "python"


def _exists_ok(path: str) -> bool:
    try:
        p = Path(path)
        return p.exists() and p.stat().st_size > 0
    except Exception:
        return False


def one(job):
    out = job["out"]
    if not job.get("force") and _exists_ok(out):
        return out, True
    if job.get("card_pid") is not None:
        # Ảnh card chữ, không qua media-generation.
        cmd = [str(VENV_PY), str(FACTORY / "bin" / "render_scene_card.py"),
               str(job["card_pid"]), str(job["card_order"]), out]
        subprocess.run(cmd, check=True, timeout=300)
        return out, False
    cmd = ["/opt/hatch/bin/media-generation", "--media-subagent-output-type", "image"]
    if job.get("orientation"):
        # vertical = dọc 9:16, landscape = ngang 16:9, square = vuông
        cmd += ["--orientation", job["orientation"]]
    cmd += ["--conversation-json", json.dumps([{"text": job["prompt"]}], ensure_ascii=False)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    d = json.loads(p.stdout)
    src = d["media_paths"][0]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, out],
                   check=True, timeout=120)
    return out, False


def main() -> int:
    jobs = json.load(open(sys.argv[1], encoding="utf-8"))
    n = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for f, skipped in ex.map(one, jobs):
            n += 1
            tag = "IMG-SKIP" if skipped else "IMG-OK"
            print(f"{tag} {n}/{len(jobs)} {f}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
