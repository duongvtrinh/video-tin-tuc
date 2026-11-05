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

Lưu ý chunk (Giai đoạn 4, 05/11/2026): file này KHÔNG tự chunk text —
toàn bộ voiceText của part được đưa nguyên cho engine infer() và engine
tự chunk bên trong; giới hạn 140 ký tự chỉ xuất hiện ở
bin/normalize_chunks.py (MAX_CHARS, để gương theo infer()) và timing
karaoke không phụ thuộc biên chunk đó (xem ghi chú ở normalize_chunks.py).
Pause: per-part — part có pauseAfterMs riêng thì dùng riêng, không có thì
dùng plan.pauseAfterMs (mặc định 180ms); assemble_project.py phải giữ
đúng per-part này trong timeline (đã sửa Giai đoạn 4, trước đó assemble
dùng pause chung của plan cho mọi part).
"""
import atexit
import json
import os
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import atomic_write_text, check_plan, rand6, wav_ok  # noqa: E402  (single source of truth)
from abbr_expand import expand_text, load_dict  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)

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
    try:
        plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: không đọc được plan: {exc}", file=sys.stderr)
        return 1
    try:
        scenes = check_plan(plan, require_voice_text=True)
    except ValueError as exc:
        # Giai đoạn 5: plan thiếu key báo rõ key nào, dừng có thông báo
        # — không crash trần KeyError, không coi plan hỏng là rỗng.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    # Sửa 29/10/2026 (code-fix, audit D-L2): kết quả TTS được khóa theo
    # partId (by_id), nên ID trùng lặng lẽ ghi đè — lỗi topic004 (mọi
    # scene dùng chung audio part cuối, tổng sai 42.7s thay vì 37.29s).
    # Chặn NGAY TRƯỚC KHI tổng hợp: báo rõ ID nào trùng, dừng lại, không
    # ghi đè, không viết tts.json dở. Part ID phải duy nhất toàn project.
    _seen, _dups = set(), []
    for _sc in scenes:
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
    # B32 (06/11/2026, lệnh CEO, lựa chọn A): kiểm voice/speed/pause
    # NGAY sau khi đọc plan, TRƯỚC khi nạp model — trước đây giá trị
    # vô lý chỉ lộ ở worker sau khi đã nạp model (timeout 3600s) hoặc
    # ra audio/timing sai. Ngưỡng speed 0.5–2.0 khớp server TTS
    # (vieneu-tts/server.py SpeakRequest); 11 giọng preset theo
    # vieneu-tts/README.md và file preset của engine
    # (vieneu/assets/voices_v3_nano.json).
    _VOICES = ("Adam", "Ái Hân", "Mỹ Duyên", "Đức Trí", "Hữu Quân",
               "Xuân Tiên", "Mai Anh", "Trúc Ly", "Anh Khôi",
               "Minh Quân", "Mạnh Dũng")
    _problems = []
    _voice0 = plan.get("voice", "Hữu Quân")
    if not isinstance(_voice0, str) or _voice0 not in _VOICES:
        _problems.append(f"voice '{_voice0}' không thuộc 11 giọng preset "
                         f"({', '.join(_VOICES)})")
    try:
        _speed0 = float(plan.get("speed", 1.0))
    except (TypeError, ValueError):
        _problems.append(f"speed '{plan.get('speed')}' không phải số")
        _speed0 = None
    if _speed0 is not None and not 0.5 <= _speed0 <= 2.0:
        _problems.append(f"speed {_speed0} ngoài khoảng 0.5–2.0")

    def _pause_ok(val):
        if isinstance(val, bool):
            return False
        try:
            v = int(val)
        except (TypeError, ValueError):
            return False
        return 0 <= v <= 10000
    _pause0 = plan.get("pauseAfterMs", 180)
    if not _pause_ok(_pause0):
        _problems.append(f"pauseAfterMs của plan '{_pause0}' phải là số nguyên 0–10000ms")
    for _sc in scenes:
        for _p in _sc["parts"]:
            if _p.get("voice") is not None and _p["voice"] not in _VOICES:
                _problems.append(f"voice của part {_p['id']} '{_p['voice']}' không thuộc 11 giọng preset")
            if "pauseAfterMs" in _p and not _pause_ok(_p["pauseAfterMs"]):
                _problems.append(f"pauseAfterMs của part {_p['id']} '{_p['pauseAfterMs']}' phải là số nguyên 0–10000ms")
    if _problems:
        print("ERROR: " + "; ".join(_problems) +
              " — sửa plan rồi chạy lại tts_batch", file=sys.stderr)
        return 1
    voice = _voice0
    speed = _speed0
    pause_ms = int(_pause0)
    try:
        entries, dict_path = load_dict(proj)
    except ValueError as exc:
        # Từ điển hỏng là CHẶN (xem abbr_expand.load_dict): dừng trước
        # khi tổng hợp, không chạy tiếp với từ điển rỗng ra audio sai.
        print(f"ERROR: {exc} — sửa abbr_dict.json rồi chạy lại",
              file=sys.stderr)
        return 1
    dict_mtime = dict_path.stat().st_mtime if dict_path else 0.0

    # Nạp model 1 lần trong tiến trình con duy nhất: truyền toàn bộ parts qua stdin
    parts_in = []
    for sc in scenes:
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
import json, os, sys, wave
sys.path.insert(0, {str(TTS_DIR)!r})
from vieneu import Vieneu

def _wav_ok(dst):
    # Bản inline của filename.wav_ok (tiến trình con không có bin/ trên
    # sys.path): WAV hỏng/dở -> False, phải tổng hợp lại.
    try:
        if not os.path.isfile(dst) or os.path.getsize(dst) == 0:
            return False
        w = wave.open(dst, 'rb')
        n = w.getnframes()
        ok = (n > 0 and w.getframerate() > 0
              and os.path.getsize(dst) >= 44 + n * w.getnchannels() * w.getsampwidth())
        w.close()
        return ok
    except Exception:
        return False

tts = Vieneu(mode='v3nano')
req = json.load(sys.stdin)
out = []
failures = []
for it in req['items']:
    dst = {str(parts_dir)!r} + '/' + it['filename']
    try:
        if os.path.exists(dst) and not it['force'] and _wav_ok(dst):
            pass
        else:
            # Giai đoạn 5: WAV cũ hỏng/dở (header lỗi, 0 frame, bị cắt)
            # không được chấp nhận lặng lẽ — tổng hợp lại thay vì skip.
            audio = tts.infer(it['text'], voice=it.get('voice') or {voice!r}, speed={speed})
            tts.save(audio, dst)
        if not _wav_ok(dst):
            raise RuntimeError('file WAV sau tổng hợp không hợp lệ (rỗng/cắt)')
        w = wave.open(dst, 'rb')
        dur = w.getnframes() / w.getframerate()
        w.close()
        out.append({{'partId': it['partId'], 'filename': it['filename'], 'duration': round(dur, 2)}})
        print('TTS-OK', it['filename'], round(dur, 2), flush=True)
    except Exception as exc:
        # Giai đoạn 5: lỗi per-part — ghi lỗi, TIẾP TỤC các part khác,
        # không giết cả batch. Tiến trình cha thấy failures sẽ dừng
        # trước khi nối segment và KHÔNG ghi tts.json dở; chạy lại
        # tts_batch sẽ chỉ tổng hợp lại các part lỗi (các WAV hợp lệ
        # đã có được skip nhờ _wav_ok), đó chính là cơ chế retry
        # per-part mà không cần refactor kiến trúc nạp model 1 lần.
        failures.append({{'partId': it['partId'], 'filename': it['filename'], 'error': str(exc)}})
        print('TTS-FAIL', it['filename'], str(exc), flush=True)
_tmp = {str(proj / 'tts-parts-tmp.json')!r} + '.tmp'
json.dump({{'parts': out, 'failures': failures}}, open(_tmp, 'w'))
os.replace(_tmp, {str(proj / 'tts-parts-tmp.json')!r})
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
    results_doc = json.loads((proj / "tts-parts-tmp.json").read_text(encoding="utf-8"))
    (proj / "tts-parts-tmp.json").unlink(missing_ok=True)
    # Giai đoạn 5, fail-closed: có part lỗi -> dừng TRƯỚC khi nối segment,
    # KHÔNG ghi tts.json dở. Các part thành công đã nằm trên đĩa dưới
    # dạng WAV hợp lệ; chạy lại tts_batch sẽ skip chúng và chỉ làm lại
    # các part lỗi (retry per-part qua lần chạy lại, không cần nạp lại
    # model cho part đã xong).
    failures = results_doc.get("failures", [])
    part_results = results_doc.get("parts", [])
    if failures:
        for _f in failures:
            print(f"TTS-FAIL part={_f.get('partId')} file={_f.get('filename')}: "
                  f"{_f.get('error')}", file=sys.stderr)
        print(f"ERROR: {len(failures)}/{len(parts_in)} part TTS lỗi — "
              f"tts.json KHÔNG được ghi; sửa nguyên nhân rồi chạy lại "
              f"tts_batch (chỉ các part lỗi được tổng hợp lại)",
              file=sys.stderr)
        return 1
    _missing = {p["partId"] for p in parts_in} - {p["partId"] for p in part_results}
    if _missing:
        print(f"ERROR: worker TTS không trả kết quả cho part: "
              f"{', '.join(sorted(_missing))} — tts.json KHÔNG được ghi",
              file=sys.stderr)
        return 1
    by_id = {p["partId"]: p for p in part_results}

    # File silence cho pauseAfterMs: global + per-part override (luat luan diem
    # CEO 30/10: part tieu de co pauseAfterMs dai hon, vd 2000ms)
    pause_values = {pause_ms} | {int(pp.get("pauseAfterMs", pause_ms))
                                for sc in scenes for pp in sc["parts"]}
    silence_files = {}
    for pv in pause_values:
        silence_files[pv] = build_voice / f"silence_{pv}ms.wav"
        # Giai đoạn 5: silence cũ bị cắt cũng làm lại (wav_ok), và ghi
        # qua file tạm rồi rename để không còn silence dở trên đĩa.
        if not wav_ok(silence_files[pv]):
            n = int(SR * pv / 1000)
            _tmp_sil = silence_files[pv].with_suffix(".wav.tmp")
            with wave.open(str(_tmp_sil), "wb") as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(SR)
                w.writeframes(b"\x00\x00" * n)
            os.replace(_tmp_sil, silence_files[pv])

    # Nối các part (+ silence) thành WAV từng segment (ffmpeg concat) + tính timing
    tts = {"parts": [], "scenes": []}
    cursor = 0.0
    # B32 (06/11/2026, lệnh CEO, lựa chọn A): concat.txt dời vào thư
    # mục tạm — trước đây nằm ở gốc project và sót lại nếu ffmpeg nối
    # lỗi (đường thành công đã unlink). atexit dọn cả khi return sớm.
    _concat_dir = tempfile.mkdtemp(prefix="tts_concat_")
    atexit.register(shutil.rmtree, _concat_dir, True)
    for si, sc in enumerate(scenes):
        seg_r6 = rand6(pid, "seg", str(sc["order"]))
        seg_wav = build_voice / f"voice_seg_{sc['order']}_{seg_r6}.wav"
        concat_list = Path(_concat_dir) / "concat.txt"
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
                is_video_last = is_last_in_scene and si == len(scenes) - 1
                if (not is_last_in_scene) or ("pauseAfterMs" in p and not is_video_last):
                    f.write(f"file '{silence_files[int(p.get('pauseAfterMs', pause_ms))]}'\n")
        # cùng sr/codec nên nối trực tiếp bằng copy
        # Giai đoạn 5: ffmpeg lỗi -> báo rõ, dừng, không crash trần
        # CalledProcessError và không ghi tts.json dở ở cuối.
        _ff = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                              "-i", str(concat_list), "-c", "copy", str(seg_wav)],
                             timeout=300)
        if _ff.returncode != 0:
            print(f"ERROR: ffmpeg nối segment scene {sc['order']} thất bại "
                  f"(exit {_ff.returncode}) — tts.json KHÔNG được ghi",
                  file=sys.stderr)
            return 1
        seg_dur = wav_duration(seg_wav)
        # cong pauseAfterMs vao duration cua tung part (tru part cuoi video;
        # part cuoi scene co pause dat ro cung duoc cong — khop silence da chen)
        off = 0.0
        for pi, p in enumerate(sc["parts"], start=1):
            pr = by_id[p["id"]]
            is_last_in_scene = pi == len(sc["parts"])
            is_video_last = is_last_in_scene and si == len(scenes) - 1
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
    # Giai đoạn 5: ghi tạm rồi rename — tts.json chỉ xuất hiện khi đã
    # đầy đủ, không bao giờ ở trạng thái dở do crash giữa chừng.
    atomic_write_text(proj / "tts.json", json.dumps(tts, ensure_ascii=False, indent=2))
    print(f"TTS-DONE scenes={len(tts['scenes'])} parts={len(tts['parts'])} total={tts['totalDuration']}s")
    if dict_path is not None:
        print(f"ABBR-OK dict=abbr_dict.json entries={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
