#!/usr/bin/env python3
"""Batch TTS cho VieNeu Asset Factory.

Đọc projects/<id>/broll-plan.json (voice parts do agent chia), synthesize mỗi part
1 file WAV (nạp model 1 lần duy nhất), đo duration thật, ghi tts.json.
Trước khi đọc, mỗi voiceText được mở rộng qua từ điển viết tắt
projects/<id>/abbr_dict.json nếu có (xem bin/abbr_expand.py, cùng từ điển với
normalize_chunks.py); part nào có từ điển mới hơn file WAV sẽ đọc lại kể cả
không có --force.

Chạy bằng venv TTS (resolve theo _tts_dir() dưới đây — biến VIENEU_TTS_DIR,
    rồi vieneu-tts, rồi vieneu-tts-api):
    <thư-mục-TTS>/.venv/bin/python tts_batch.py <project_id> [--force]

Output:
    projects/<id>/build/audio/voice/parts/part_<order>_<partIdx>_<rand6>.wav
    projects/<id>/build/audio/voice/voice_seg_<order>_<rand6>.wav   (nối các part)
    projects/<id>/tts.json
"""
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import rand6  # noqa: E402  (single source of truth)
from abbr_expand import expand_text, load_dict  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
def _tts_dir() -> Path:
    """Thư mục TTS: ưu tiên biến môi trường, rồi layout repo (vieneu-tts),
    rồi tên cũ trên máy gốc (vieneu-tts-api). Máy gốc không đổi hành vi
    vì vieneu-tts chưa tồn tại ở đó nên rơi về vieneu-tts-api."""
    env = os.environ.get("VIENEU_TTS_DIR")
    if env:
        return Path(env)
    for cand in (FACTORY.parent / "vieneu-tts",
                 FACTORY.parent / "vieneu-tts-api",
                 Path.home() / "workspace" / "vieneu-tts",
                 Path.home() / "workspace" / "vieneu-tts-api"):
        if cand.exists():
            return cand
    return FACTORY.parent / "vieneu-tts"


TTS_DIR = _tts_dir()
VENV_PY = TTS_DIR / ".venv" / "bin" / "python"
SR = 24000  # v3nano


def wav_duration(path: Path) -> float:
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: tts_batch.py <project_id> [--force]", file=sys.stderr)
        return 2
    pid = sys.argv[1]
    force = "--force" in sys.argv

    proj = FACTORY / "projects" / pid
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    # Sửa 29/10/2026 (code-fix, audit D-L2): kết quả TTS được khóa theo
    # partId (by_id), nên ID trùng lặng lẽ ghi đè — lỗi topic004 (mọi
    # scene dùng chung audio part cuối, tổng sai 42.7s thay vì 37.29s).
    # Chặn NGAY TRƯỚC KHI tổng hợp: báo rõ ID nào trùng, dừng lại, không
    # ghi đè, không viết tts.json dở. Part ID phải duy nhất toàn project.
    _seen, _dups = set(), []
    for _sc in plan["scenes"]:
        for _p in _sc["parts"]:
            if _p["id"] in _seen and _p["id"] not in _dups:
                _dups.append(_p["id"])
            _seen.add(_p["id"])
    if _dups:
        print(f"ERROR: partId trùng trong plan, TTS dừng lại, không ghi đè: "
              f"{', '.join(_dups)} — đổi ID cho duy nhất toàn project "
              f"(vd part-1..part-N theo từng scene, không lặp 'part1' ở "
              f"mọi scene) rồi chạy lại", file=sys.stderr)
        return 2
    voice = plan.get("voice", "Hữu Quân")
    speed = float(plan.get("speed", 1.0))
    pause_ms = int(plan.get("pauseAfterMs", 180))
    entries, dict_path = load_dict(proj)
    dict_mtime = dict_path.stat().st_mtime if dict_path else 0.0

    # Nạp model 1 lần trong tiến trình con duy nhất: truyền toàn bộ parts qua stdin
    parts_in = []
    for sc in plan["scenes"]:
        for pi, p in enumerate(sc["parts"], start=1):
            r6 = rand6(pid, "part", str(sc["order"]), str(pi))
            fname = f"part_{sc['order']}_{pi}_{r6}.wav"
            speech, _hits = expand_text(p["voiceText"], entries)
            wav_path = proj / "build" / "audio" / "voice" / "parts" / fname
            force_part = force or (dict_path is not None and wav_path.exists()
                                   and dict_mtime > wav_path.stat().st_mtime)
            parts_in.append({
                "sceneOrder": sc["order"], "partIdx": pi, "partId": p["id"],
                "text": speech, "filename": fname, "force": force_part,
                "pauseMs": int(p.get("pauseAfterMs", pause_ms)),
                # multi-voice: part có thể ghi đè voice (vd quote đọc giọng khác)
                "voice": p.get("voice") or voice,
            })

    build_voice = proj / "build" / "audio" / "voice"
    parts_dir = build_voice / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)

    worker = f"""
import json, sys, wave
sys.path.insert(0, {str(TTS_DIR)!r})
from vieneu import Vieneu
tts = Vieneu(mode='v3nano')
req = json.load(sys.stdin)
out = []
for it in req['items']:
    dst = {str(parts_dir)!r} + '/' + it['filename']
    import os
    if os.path.exists(dst) and not it['force']:
        pass
    else:
        audio = tts.infer(it['text'], voice=it.get('voice') or {voice!r}, speed={speed})
        tts.save(audio, dst)
    w = wave.open(dst, 'rb')
    dur = w.getnframes() / w.getframerate()
    w.close()
    out.append({{'partId': it['partId'], 'filename': it['filename'], 'duration': round(dur, 2)}})
    print('TTS-OK', it['filename'], round(dur, 2), flush=True)
json.dump(out, open({str(proj / 'tts-parts-tmp.json')!r}, 'w'))
"""
    payload = json.dumps({"items": parts_in}, ensure_ascii=False)
    import os
    env = dict(os.environ, HF_HUB_OFFLINE="1")  # dùng model cache, không gọi HF Hub
    r = subprocess.run([str(VENV_PY), "-c", worker], input=payload,
                       capture_output=True, text=True, timeout=3600, env=env)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:])
        return 1
    part_results = json.loads((proj / "tts-parts-tmp.json").read_text(encoding="utf-8"))
    (proj / "tts-parts-tmp.json").unlink(missing_ok=True)
    by_id = {p["partId"]: p for p in part_results}

    # File silence cho pauseAfterMs: global + per-part override (luat luan diem
    # CEO 30/10: part tieu de co pauseAfterMs dai hon, vd 2000ms)
    pause_values = {pause_ms} | {int(pp.get("pauseAfterMs", pause_ms))
                                for sc in plan["scenes"] for pp in sc["parts"]}
    silence_files = {}
    for pv in pause_values:
        silence_files[pv] = build_voice / f"silence_{pv}ms.wav"
        if not silence_files[pv].exists():
            n = int(SR * pv / 1000)
            with wave.open(str(silence_files[pv]), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(SR)
                w.writeframes(b"\x00\x00" * n)

    # Nối các part (+ silence) thành WAV từng segment (ffmpeg concat) + tính timing
    tts = {"parts": [], "scenes": []}
    cursor = 0.0
    for si, sc in enumerate(plan["scenes"]):
        seg_r6 = rand6(pid, "seg", str(sc["order"]))
        seg_wav = build_voice / f"voice_seg_{sc['order']}_{seg_r6}.wav"
        concat_list = proj / "concat.txt"
        with open(concat_list, "w", encoding="utf-8") as f:
            for pi, p in enumerate(sc["parts"], start=1):
                pr = by_id[p["id"]]
                f.write(f"file '{parts_dir / pr['filename']}'\n")
                # 03/11/2026 (lenh CEO, luat nghi nhan): pauseAfterMs dat ro
                # trong plan o part cuoi scene cung phai thanh tieng — truoc
                # day dieu kien pi < len(...) bo silence cuoi scene nen khoang
                # lang 1000ms truoc part chia doan (luon la part dau scene sau)
                # khong bao gio nghe thay. Chi part cuoi cung cua video van
                # khong co silence cuoi (thua, khong nghe).
                is_last_in_scene = pi == len(sc["parts"])
                is_video_last = is_last_in_scene and si == len(plan["scenes"]) - 1
                if (not is_last_in_scene) or ("pauseAfterMs" in p and not is_video_last):
                    f.write(f"file '{silence_files[int(p.get('pauseAfterMs', pause_ms))]}'\n")
        # cùng sr/codec nên nối trực tiếp bằng copy
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                        "-i", str(concat_list), "-c", "copy", str(seg_wav)],
                       check=True, timeout=300)
        seg_dur = wav_duration(seg_wav)
        # cong pauseAfterMs vao duration cua tung part (tru part cuoi video;
        # part cuoi scene co pause dat ro cung duoc cong — khop silence da chen)
        off = 0.0
        for pi, p in enumerate(sc["parts"], start=1):
            pr = by_id[p["id"]]
            is_last_in_scene = pi == len(sc["parts"])
            is_video_last = is_last_in_scene and si == len(plan["scenes"]) - 1
            add_pause = (not is_last_in_scene) or ("pauseAfterMs" in p and not is_video_last)
            d = pr["duration"] + (int(p.get("pauseAfterMs", pause_ms)) / 1000.0 if add_pause else 0.0)
            tts["parts"].append({
                "id": p["id"], "sceneOrder": sc["order"], "partIdx": pi,
                "audio_file": f"parts/{pr['filename']}",
                "voice": p.get("voice") or voice,
                "duration": round(d, 2),
                "startSec": round(cursor + off, 2),
                "endSec": round(cursor + off + d, 2),
            })
            off += d
        # duration segment = tổng (kể cả pause); endSec tuyệt đối
        total = round(off, 2)
        if abs(seg_dur - total) > 0.15:
            print(f"WARN seg {sc['order']}: wav={seg_dur:.2f}s != sum={total:.2f}s",
                  file=sys.stderr)
        tts["scenes"].append({
            "id": sc["id"], "order": sc["order"],
            "audio_file": seg_wav.name,
            "duration": total,
            "startSec": round(cursor, 2),
            "endSec": round(cursor + total, 2),
        })
        cursor += total
        concat_list.unlink(missing_ok=True)

    tts["totalDuration"] = round(cursor, 2)
    (proj / "tts.json").write_text(json.dumps(tts, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"TTS-DONE scenes={len(tts['scenes'])} parts={len(tts['parts'])} total={tts['totalDuration']}s")
    if dict_path is not None:
        print(f"ABBR-OK dict=abbr_dict.json entries={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
