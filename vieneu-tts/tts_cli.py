#!/usr/bin/env python3
"""Gọi VieNeu-TTS trực tiếp từ dòng lệnh (Muse dùng để đọc theo yêu cầu trong chat).

Ví dụ:
    .venv/bin/python tts_cli.py --text "Xin chào" --voice "Minh Quân" --out out.wav
    .venv/bin/python tts_cli.py --text "..." --voice "Mỹ Duyên" --speed 1.2 --out out.wav
    .venv/bin/python tts_cli.py --voices   # liệt kê giọng
"""
import argparse
import sys
import time

MODE_DEFAULT = "v3nano"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="", help="Văn bản cần đọc")
    ap.add_argument("--voice", default="Hữu Quân", help="Tên/id giọng")
    ap.add_argument("--speed", type=float, default=1.0, help="Tốc độ 0.5-2.0")
    ap.add_argument("--out", default="speech.wav", help="File wav đầu ra")
    ap.add_argument("--voices", action="store_true", help="Chỉ liệt kê giọng rồi thoát")
    ap.add_argument("--mode", default=MODE_DEFAULT, help="v3nano | turbo (mọi giá trị khác v3nano đều chạy turbo)")
    args = ap.parse_args()

    from vieneu import Vieneu

    t0 = time.time()
    tts = Vieneu(mode=args.mode) if args.mode == "v3nano" else Vieneu()
    voices = tts.list_preset_voices()
    if args.voices:
        for label, vid in voices:
            print(f"{vid}  —  {label}")
        return 0

    text = args.text.strip()
    if not text:
        print("Thiếu --text", file=sys.stderr)
        return 2
    if len(text) > 5000:
        print("Text quá dài (tối đa 5000 ký tự)", file=sys.stderr)
        return 2

    ids = [vid for _, vid in voices]
    voice = args.voice if args.voice in ids else "Hữu Quân" if "Hữu Quân" in ids else ids[0]
    audio = tts.infer(text, voice=voice, speed=args.speed)
    tts.save(audio, args.out)
    sr = 24000 if args.mode == "v3nano" else 48000
    print(f"OK voice={voice} seconds={len(audio)/sr:.2f} file={args.out} wall={time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
