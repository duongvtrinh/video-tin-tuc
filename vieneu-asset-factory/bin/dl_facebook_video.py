#!/usr/bin/env python3
"""Tải video Facebook (reel / bài viết có video) bằng yt-dlp (CEO 10/11/2026).

Chỉ tải video/reel CÔNG KHAI, không cần đăng nhập. facebook-cli không
trả url video trực tiếp nên không dùng được cho việc này; gallery-dl
không cần (CEO 10/11/2026: mở link bài viết bằng trình duyệt thực là
tải được ảnh; video thì dùng yt-dlp).

    python3 bin/dl_facebook_video.py <url-facebook-video> <output.mp4> [--cookies <cookies.txt>]

Cờ --no-check-certificates là bắt buộc trên máy này (proxy egress dùng
chứng chỉ tự ký, đã kiểm chứng 09/11/2026 với reel 1684240226461453,
48 MB / 348 s). Video riêng tư/nhóm kín cần --cookies <file cookies.txt>
(CEO xuất file, KHÔNG commit vào repo). Ghi đè output nếu đã có.
In DL-OK kèm kích thước + thời lượng (ffprobe), lỗi thì in DL-ERROR.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _probe(path: Path):
    """Trả (width, height, duration_s) bằng ffprobe, None nếu không đọc được."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", str(path)],
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if out.returncode != 0:
        return None
    try:
        data = json.loads(out.stdout)
    except json.JSONDecodeError:
        return None
    video = next((s for s in data.get("streams", [])
                  if s.get("codec_type") == "video"), None)
    if video is None:
        return None
    try:
        duration = float(data.get("format", {}).get("duration", 0) or 0)
    except (TypeError, ValueError):
        duration = 0.0
    return (int(video.get("width", 0)), int(video.get("height", 0)), duration)


def main() -> int:
    args = sys.argv[1:]
    cookies = None
    if "--cookies" in args:
        i = args.index("--cookies")
        if i + 1 >= len(args):
            print("usage: dl_facebook_video.py <url> <output.mp4> [--cookies <cookies.txt>]",
                  file=sys.stderr)
            return 2
        cookies = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print("usage: dl_facebook_video.py <url> <output.mp4> [--cookies <cookies.txt>]",
              file=sys.stderr)
        return 2
    url, dst = args[0], Path(args[1])
    if shutil.which("yt-dlp") is None:
        print("DL-ERROR yt-dlp chưa cài (pip install -r requirements.txt)",
              file=sys.stderr)
        return 1
    if cookies is not None and not Path(cookies).is_file():
        print(f"DL-ERROR không thấy file cookies: {cookies}", file=sys.stderr)
        return 1
    dst.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["yt-dlp", "--no-check-certificates", "--no-playlist",
           "--force-overwrites", "--merge-output-format", "mp4",
           "-f", "bv+ba/b",
           "-o", str(dst)]
    if cookies is not None:
        cmd += ["--cookies", cookies]
    cmd.append(url)
    run = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if run.returncode != 0 or not dst.is_file():
        tail = (run.stderr or run.stdout or "").strip().splitlines()[-3:]
        print("DL-ERROR yt-dlp thất bại: " + " | ".join(tail), file=sys.stderr)
        return 1
    probe = _probe(dst)
    if probe is None:
        print(f"DL-ERROR file tải về không phải video đọc được: {dst}",
              file=sys.stderr)
        return 1
    w, h, dur = probe
    print(f"DL-OK {dst.name} {w}x{h} {dur:.1f}s {dst.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
