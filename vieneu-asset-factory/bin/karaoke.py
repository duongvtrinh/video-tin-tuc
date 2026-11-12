#!/usr/bin/env python3
"""Karaoke cho VieNeu Asset Factory.

Với mỗi voice part: VAD năng lượng trên WAV thật -> split_cue (target 5 từ,
không cắt từ ghép, chấm điểm vị trí cắt) -> karaoke.json + karaoke.ass (\\k
từng chữ rời, không lướt).

- Font phụ đề: 40 * (min(W,H)/480), khớp preview (60px ở cả 16:9 và 9:16; tăng nhẹ từ 54px theo lệnh CEO 1/11/2026 vì phụ đề render nhỏ hơn cảm nhận ở preview).
- HẰNG SỐ ĐÃ CHỐT (Giai đoạn 4, 05/11/2026 — xem PIPELINE.md mục
  "Hằng số pipeline đã chốt"): aspectRatio mặc định khi thiếu field là
  "9:16" (trước đây file này mặc định 16:9, mâu thuẫn render_scene_card.py).
  MarginV = 20% chiều cao khi dọc, 7% khi ngang — khớp preview
  (lib/render-engine.js) và bước kiểm tra lại của render_draft.py.
- Màu vàng #FBBF24 trong ASS phải viết &H0024BFFB& (thứ tự BBGGRR), không viết trực tiếp hex RGB (sẽ ra màu xanh).
- Part nào có b-roll template chữ thật (templateId + inputs có chữ) thì
  ẩn phụ đề (subsHidden=true, lines=[]) để tránh trùng/chen chữ với template.
  Phụ đề chỉ hiện khi part chỉ có ảnh nền.
  (Từ 31/10/2026, lệnh CEO: không còn ngoại lệ hidesSubs: false nữa —
  story-title và clip-caption đã về hidesSubs: true nên cũng ẩn phụ đề
  như mọi template; code vẫn giữ nhánh ngoại lệ cho template nào khai
  hidesSubs: false trong tương lai.)

    <venv>/bin/python bin/karaoke.py <project_id> [--target 5]

Ghi: build/subtitles/karaoke.json, build/subtitles/karaoke.ass
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "lib" / "vi_sub"))
from phrase_splitter import split_cue  # noqa: E402
from filename import check_plan  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)



def decode_mono_16k(path: Path) -> np.ndarray:
    p = subprocess.run(
        ["ffmpeg", "-v", "error", "-nostdin", "-i", str(path),
         "-ac", "1", "-ar", "16000", "-f", "f32le", "pipe:1"],
        capture_output=True, check=True)
    return np.frombuffer(p.stdout, dtype=np.float32)


def vad_intervals(wav: np.ndarray, sr: int = 16000, frame_ms: int = 10,
                  min_silence_ms: int = 120, min_speech_ms: int = 80) -> list:
    """VAD năng lượng đơn giản (giọng TTS sạch, không nhạc nền)."""
    if len(wav) == 0:
        return []
    fl = sr * frame_ms // 1000
    n = len(wav) // fl
    if n == 0:
        return [(0.0, len(wav) / sr)]
    frames = wav[:n * fl].reshape(n, fl)
    energy = np.sqrt((frames ** 2).mean(axis=1) + 1e-12)
    thr = max(energy.max() * 0.12, 1e-4)
    speech = energy > thr
    # tìm các đoạn tiếng, rồi gộp khoảng nghỉ ngắn hơn min_silence_ms
    runs, i = [], 0
    while i < n:
        if speech[i]:
            j = i
            while j < n and speech[j]:
                j += 1
            runs.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for s, e in runs:
        if merged and (s - merged[-1][1]) * frame_ms < min_silence_ms:
            merged[-1][1] = e
        else:
            merged.append([s, e])
    return [(s * frame_ms / 1000.0, e * frame_ms / 1000.0) for s, e in merged
            if (e - s) * frame_ms >= min_speech_ms]


def strip_tags(text: str) -> str:
    """Bỏ tag kiểu <en>...</en> của normalizer, giữ lại chữ bên trong."""
    import re
    return re.sub(r"\s+", " ", re.sub(r"</?[a-zA-Z][^>]*>", " ", text)).strip()


def _nkey(w: str) -> str:
    import re
    import unicodedata
    t = strip_tags(w)
    t = unicodedata.normalize("NFC", t).casefold()
    return "".join(ch for ch in t if ch.isalnum())


def _count_number_words(n: int) -> int:
    """Số từ khi đọc một số nguyên theo tiếng Việt (đếm, không đọc ra
    chữ): 5 -> 1 ("năm"), 10 -> 1 ("mười"), 25 -> 3 ("hai mươi lăm"),
    213 -> 4 ("hai trăm mười ba"), 361 -> 5 ("ba trăm sáu mươi mốt").
    Chỉ dùng để ước lượng số từ chuẩn hoá của một token, không dùng để
    phát âm thật."""
    if n < 0:
        n = -n
    if n < 10:
        return 1
    if n < 20:
        return 1 if n == 10 else 2
    if n < 100:
        tens, unit = divmod(n, 10)
        return 2 + (0 if unit == 0 else 1)
    if n < 1000:
        hundreds, rem = divmod(n, 100)
        if rem == 0:
            return 2
        if rem < 10:
            return 4  # "ba trăm lẻ năm"
        return 2 + _count_number_words(rem)
    # >= 1000: chia nhóm 3 chữ số, mỗi nhóm khác 0 cộng 1 từ chỉ đơn vị
    # (nghìn/triệu/tỷ); nhóm 0 không cộng.
    total, scale = 0, 0
    while n:
        group = n % 1000
        if group:
            total += _count_number_words(group) + (1 if scale else 0)
        n //= 1000
        scale += 1
    return max(1, total)


def _estimate_norm_words(token: str) -> int:
    """Ước lượng số từ chuẩn hoá mà một token gốc nở ra, để chia một
    span chuẩn hoá chung cho nhiều token gốc (xem align_words).
    - Số thập phân thuần ("25.361"): đọc như số hàng nghìn
      ("hai mươi lăm nghìn ba trăm sáu mươi mốt" = 9 từ).
    - Mã chữ + số: chữ cái viết hoa đọc từng chữ ("RON" -> 3);
      số sau một chữ cái đơn đọc như số ("E10" -> "e mười" = 2);
      số sau một acronym (nhóm chữ dài hơn 1) đọc từng chữ số
      ("RON92" -> "rờ ô nờ chín hai" = 5).
    - Từ tiếng Việt thường (chữ thường, có dấu): 1 từ.
    - Từ chỉ dấu câu: 0 (đã xử lý riêng ở align_words)."""
    import re
    t = strip_tags(token).strip().strip("\"'“”’()[]{}.,!?;:")
    if not t:
        return 0
    if re.fullmatch(r"\d+([.,]\d+)*", t):
        groups = re.split(r"[.,]", t)
        total = 0
        for gi, g in enumerate(groups):
            v = int(g) if g else 0
            if v == 0 and len(groups) > 1:
                continue  # nhóm 000 trong "30.000" không đọc thêm
            total += _count_number_words(v)
            if gi:
                total += 1  # "nghìn" nối nhóm hàng nghìn
        return max(1, total)
    total = 0
    for sub in t.split("-"):
        if not sub:
            continue
        # tách sub thành các cụm chữ / cụm số xen kẽ
        runs = re.findall(r"[^\d]+|\d+", sub)
        prev_letter_len = 0
        for run in runs:
            if run.isdigit():
                if prev_letter_len > 1:
                    total += len(run)  # đọc từng chữ số sau acronym
                else:
                    total += _count_number_words(int(run))
                prev_letter_len = 0
            else:
                letters = "".join(ch for ch in run if ch.isalpha())
                if letters and all("A" <= ch <= "Z" for ch in letters):
                    total += len(letters)  # acronym đọc từng chữ cái
                    prev_letter_len = len(letters)
                else:
                    total += 1  # từ tiếng Việt thường
                    prev_letter_len = 0
    return max(1, total)


def align_words(orig_words: list, norm_words: list) -> list:
    """Align chữ GỐC -> span chữ CHUẨN HOÁ (bao cả trường hợp 1:N như
    "1991" -> "một nghìn chín trăm chín mươi mốt").
    Trả về [(orig_idx, j_start, j_end)] với j theo norm_words.
    SỬA 28/10/2026 (lỗi Vinspeed scene4, giây 59-60): từ gốc chỉ gồm dấu câu
    (vd "-" trong "Hà Nội - Quảng Ninh") có _nkey == "" và KHÔNG có từ
    chuẩn hoá riêng (dấu gạch biến thành dấu phẩy dính vào từ trước là
    "nội,"). Trước sửa, từ này rơi vào nhánh mismatch, và vòng tìm tham
    lam bắt đầu từ j+1 nên bỏ qua từ "Quảng" đúng ngay tại j, nhảy tới
    từ "Quảng" cuối câu, khiến "-" dài 7,12 giây và mọi từ sau đó cùng
    nhận mốc cuối 60,077-60,25, tạo 6 dòng phụ đề chồng nhau trong 0,17
    giây. Từ nay: từ chỉ dấu câu KHÔNG ăn mốc thời gian, trả về mốc
    đặc biệt (-1, -1); hàm gọi sẽ gán cho nó thời lượng 0 tại cuối từ
    trước đó, để nó vẫn hiện trong dòng chữ nhưng không kéo dài dòng
    sang từ tiếp theo (trước đó, chia sẻ mốc của từ kế tiếp đã làm dòng
    "đoạn Nha Trang -" chồng 0,18 giây lên dòng "Vinh trong bảy năm").
    Từ chỉ dấu câu không làm j tiến lên, để từ gốc kế tiếp vẫn khớp
    đúng từ chuẩn hoá hiện tại."""
    n, m = len(orig_words), len(norm_words)
    res, i, j = [], 0, 0
    while i < n and j < m:
        ok, oj = _nkey(orig_words[i]), _nkey(norm_words[j])
        if ok == "":
            # Từ chỉ dấu câu: mốc đặc biệt, không tiến j.
            res.append((i, -1, -1))
            i += 1
            continue
        if ok == oj:
            res.append((i, j, j))
            i += 1
            j += 1
        else:
            # orig[i] bị nở ra: tìm orig[k] khớp norm[t] gần nhất phía sau
            # SỬA 31/10/2026 (lỗi TOPIC-072 scene4-part-2, danh sách 6 mã
            # trái phiếu): cửa sổ cũ 30 từ chuẩn hoá quá hẹp cho danh
            # sách mã — từ đồng bộ tiếp theo ("và" trước mã cuối) nằm
            # cách ~60 từ chuẩn hoá, nên 5 mã đầu rơi vào fallback 1-1
            # (mỗi mã chỉ 0,15-0,19 giây) và mã cuối ôm toàn bộ span
            # còn lại (13,79 giây cho một mã chỉ đọc ~3,5 giây).
            # Từ nay cửa sổ là 100 từ chuẩn hoá: đủ cho danh sách mã
            # dài, vẫn lấy khớp (k, t) gần nhất nên không đổi hành vi
            # với câu thường (kiểm chứng hồi quy: karaoke lại 071 cho
            # karaoke.json giống hệt). Mã dài vẫn WARN >2 giây nhưng
            # đó là đúng lớp miễn trừ "token mang phần nở của chính
            # nó" (tiền lệ A321-200 1,775 giây, 4.031,40 2,36 giây).
            found = None
            for k in range(i + 1, min(n, i + 6)):
                kk = _nkey(orig_words[k])
                if not kk:
                    continue
                for t in range(j + 1, min(m, j + 100)):
                    if _nkey(norm_words[t]) == kk:
                        found = (k, t)
                        break
                if found:
                    break
            if found:
                k, t = found
                # SỬA 29/10/2026 (lỗi TOPIC-037 scene3-part-1, giây
                # 51,67-60,24): trước sửa, nhánh này chỉ gán span
                # (j, t-1) cho orig[i] rồi nhảy thẳng tới (k, t), làm
                # RƠI các token gốc ở giữa (vd "E5 RON92" nở chung
                # thành "e năm rờ ô nờ chín hai", "E10 RON95-III
                # 25.213" nở chung thành 18 từ) — word_times ngắn
                # hơn orig_words, nên mọi từ sau đó bị gán nhầm mốc
                # của từ trước nó ("chỉ" ăn 2,11s của "25.361",
                # "xăng" ăn 3,80s của "E10/RON95-III/25.213").
                # Từ nay: chia span (j, t-1) cho TẤT CẢ token gốc
                # i..k-1 theo ước lượng số từ chuẩn hoá của từng
                # token (_estimate_norm_words), giữ đúng 1-1 giữa
                # word_times và orig_words. Trường hợp chỉ có một
                # token (k == i+1) thì kết quả không đổi so với cũ.
                span_len = t - j
                counts = [_estimate_norm_words(orig_words[oi])
                          for oi in range(i, k)]
                total_c = sum(counts) or len(counts)
                bounds = [j]
                for idx in range(len(counts) - 1):
                    target = j + round(span_len * sum(counts[:idx + 1])
                                       / total_c)
                    lo = bounds[-1] + (1 if counts[idx] > 0 else 0)
                    hi = t - sum(1 for c in counts[idx + 1:] if c > 0)
                    end = min(max(target, lo), hi) if hi >= lo else hi
                    bounds.append(end)
                bounds.append(t)
                for s_idx, oi in enumerate(range(i, k)):
                    j1 = bounds[s_idx]
                    j2 = bounds[s_idx + 1] - 1
                    if j2 < j1:  # span rỗng (hiếm): gán 1 từ để không lệch
                        j2 = min(j1, m - 1)
                    res.append((oi, j1, j2))
                i, j = k, t
            else:  # không sync được: gán 1-1 để không kẹt
                # SỬA 30/10/2026 (lỗi TOPIC-051, phát hiện khi karaoke
                # lần đầu: 7 part kết thúc bằng token số — 60%,
                # 46,53%, 49,3%, 2027, 2045, 2027-2030, 2026-2030 —
                # đều hụt timing đuôi part 0,88-3,23 giây): nhánh
                # mismatch cần một từ gốc tiếp theo để giới hạn span
                # nở; token số đứng CUỐI câu không có từ tiếp theo
                # nên rơi vào fallback 1-1, chỉ nhận 0,14-0,17 giây
                # trong khi phần nở dài 1,5-3,2 giây (vd
                # "2027-2030." lúc đầu chỉ 0,14 giây, giọng đọc phần
                # nở thêm ~2,8 giây không có phụ đề). Từ nay: khi
                # không còn từ gốc không-phải-dấu-câu nào sau i thì
                # token này chính là token cuối câu, gán toàn bộ span
                # chuẩn hoá còn lại (j..m-1) cho nó thay vì fallback
                # 1-1 — cùng tinh thần bản sửa 29/10/2026 (chia span
                # cho mọi token thay vì bỏ token giữa). Production
                # đã xử lý TOPIC-051 bằng cách viết lại câu (không
                # để số đứng cuối câu) trước khi có bản sửa này;
                # video 051 không cần render lại chỉ vì bản sửa này.
                if not [oi for oi in range(i + 1, n)
                        if _nkey(orig_words[oi])] and j < m:
                    res.append((i, j, m - 1))
                    i, j = n, m
                else:
                    res.append((i, j, j))
                    i += 1
                    j += 1
    while i < n:  # chữ gốc thừa: gán vào cuối
        res.append((i, max(0, m - 1), max(0, m - 1)))
        i += 1
    return res


def ass_time(s: float) -> str:
    s = max(0.0, s)
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h}:{m:02d}:{sec:05.2f}"


def main() -> int:
    pid = sys.argv[1]
    target = 5
    if "--target" in sys.argv:
        target = int(sys.argv[sys.argv.index("--target") + 1])
    proj = FACTORY / "projects" / pid
    tts = json.loads((proj / "tts.json").read_text(encoding="utf-8"))
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    # B28 (06/11/2026, lệnh CEO, lựa chọn A): guard cấu trúc plan —
    # trước đây part thiếu voiceText crash trần KeyError ở vòng
    # plan_text[pt["id"]] = pt["voiceText"] bên dưới.
    try:
        check_plan(plan, require_voice_text=True)
    except ValueError as exc:
        print(f"{exc}", file=sys.stderr)
        return 1
    plan_text = {}
    hide_subs = set()  # part có template chữ thật -> ẩn phụ đề (tránh trùng/chen chữ)
    for sc in plan["scenes"]:
        for pt in sc["parts"]:
            plan_text[pt["id"]] = pt["voiceText"]
            br = pt.get("broll") or {}
            tid = br.get("templateId")
            if tid and tid != "none":
                inputs = br.get("inputs") or {}
                if any(isinstance(v, str) and v.strip() for v in inputs.values()):
                    # 13/11/2026: mọi template đều hidesSubs=true (42/42) — ngoại lệ
                    # clip-caption/story-title đã bỏ 31/10/2026; nhánh kiểm
                    # hidesSubs is False là code chết, gỡ.
                    hide_subs.add(pt["id"])
    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    # Mặc định 9:16 khi thiếu field (chốt Giai đoạn 4).
    wide = inp.get("aspectRatio", "9:16") != "9:16"
    W, H = (1280, 720) if wide else (720, 1280)
    # font theo chiều NHỎ (độ rộng dòng), khớp preview: 60px ở cả 16:9 và 9:16
    font_size = max(16, int(round(40 * (min(W, H) / 480.0))))
    # bottom: 20% chiều cao khi 9:16, giữ 7% khi 16:9 (khớp preview)
    margin_v = int(H * (0.20 if not wide else 0.07))

    norm_path = proj / "build" / "norm_chunks.json"
    if not norm_path.exists():
        print("chưa có norm_chunks.json — chạy bin/normalize_chunks.py trước",
              file=sys.stderr)
        return 2
    norm_chunks = json.loads(norm_path.read_text(encoding="utf-8"))

    karaoke = []
    sent_cues = []  # mốc câu gốc (hiển thị đúng kịch bản) cho synced_cues.srt
    for p in tts["parts"]:
        wav_path = proj / "build" / "audio" / "voice" / p["audio_file"]
        runs = []
        # B29 (06/11/2026, lệnh CEO, lựa chọn A): WAV mất/hỏng hoặc VAD
        # lỗi thì timing rơi về chia đều — trước đây lặng lẽ, phụ đề
        # lệch giọng mà không ai biết. In KARAOKE-WARN rõ ràng và ghi
        # dấu "fallback" vào karaoke.json để preflight cảnh báo được.
        fallback = None
        if not wav_path.exists():
            fallback = "wav-missing"
            print(f"KARAOKE-WARN {p['id']}: không thấy file WAV {wav_path.name} — timing chia đều, phụ đề có thể lệch giọng đọc")
        else:
            try:
                raw = vad_intervals(decode_mono_16k(wav_path))
                # VAD theo file (gốc 0) -> đổi sang giờ tuyệt đối trên timeline
                runs = [(s + p["startSec"], e + p["startSec"]) for s, e in raw]
            except Exception as exc:
                fallback = "vad-error"
                print(f"KARAOKE-WARN {p['id']}: giải mã/VAD lỗi ({exc}) — timing chia đều, phụ đề có thể lệch giọng đọc")
        entry = norm_chunks.get(p["id"], {})
        if not entry.get("pairs"):
            if fallback is None:
                fallback = "norm-missing"
            print(f"KARAOKE-WARN {p['id']}: thiếu entry trong norm_chunks.json — dùng câu gốc, timing có thể lệch")
        pairs = entry.get("pairs") or [[plan_text.get(p["id"], ""),
                                        plan_text.get(p["id"], "")]]

        # câu gốc + câu chuẩn hoá (bỏ tag) của part này
        orig_sents = [o for o, _ in pairs]
        norm_sents = [strip_tags(n) for _, n in pairs]
        norm_offsets, flat_norm = [], []
        for ns in norm_sents:
            norm_offsets.append(len(flat_norm))
            flat_norm.extend(ns.split())

        # 1. timing từng chữ CHUẨN HOÁ (đúng giọng đọc) trên cả part
        timed_norm = []
        if flat_norm:
            cues = split_cue(" ".join(flat_norm), p["startSec"], p["endSec"],
                             target_words=10 ** 9, runs=runs or None)
            for c in cues:
                timed_norm.extend(c.get("words", []))

        # 2. align từng câu: chữ GỐC -> span thời gian chữ chuẩn hoá
        orig_words, word_times = [], []
        for si, osent in enumerate(orig_sents):
            ow = osent.split()
            nw = norm_sents[si].split()
            base = norm_offsets[si]
            nw_timed = timed_norm[base:base + len(nw)] if timed_norm else []
            start_wi = len(orig_words)
            for oi, j1, j2 in align_words(ow, nw):
                if j1 == -1:
                    # Từ chỉ dấu câu: thời lượng 0 tại cuối từ trước đó,
                    # không kéo dài dòng sang từ tiếp theo.
                    _prev_end = word_times[-1][1] if word_times else p["startSec"]
                    word_times.append((_prev_end, _prev_end))
                elif nw_timed and 0 <= j1 <= j2 < len(nw_timed):
                    w0, w1 = nw_timed[j1], nw_timed[j2]
                    word_times.append((w0["start"], w1["end"]))
                else:  # fallback: chia đều trong part
                    frac0, frac1 = oi / max(1, len(ow)), (oi + 1) / max(1, len(ow))
                    word_times.append((
                        p["startSec"] + (p["endSec"] - p["startSec"]) * frac0,
                        p["startSec"] + (p["endSec"] - p["startSec"]) * frac1))
            if ow and len(word_times) > start_wi and p["id"] not in hide_subs:
                sent_cues.append({"partId": p["id"], "text": osent,
                                  "start": round(word_times[start_wi][0], 3),
                                  "end": round(word_times[-1][1], 3)})
            orig_words.extend(ow)

        # 3. chia dòng karaoke trên CHỮ GỐC (không cắt từ ghép), nhịp đã align
        lines = []
        if orig_words:
            groups = split_cue(" ".join(orig_words), p["startSec"], p["endSec"],
                               target_words=target, runs=None)
            wi = 0
            for g in groups:
                gw = g["text"].split()
                ws = []
                for k in range(len(gw)):
                    if wi + k < len(word_times):
                        st, en = word_times[wi + k]
                        ws.append({"text": gw[k], "start": round(st, 3),
                                   "end": round(en, 3)})
                wi += len(gw)
                if ws:
                    lines.append({"text": g["text"],
                                  "start": ws[0]["start"], "end": ws[-1]["end"],
                                  "words": ws})
        _entry = {"partId": p["id"], "startSec": p["startSec"],
                  "endSec": p["endSec"],
                  "voiceText": plan_text.get(p["id"], ""),
                  "lines": [] if p["id"] in hide_subs else lines,
                  "subsHidden": p["id"] in hide_subs}
        if fallback is not None:
            _entry["fallback"] = fallback
        karaoke.append(_entry)

    # Cảnh báo căn phụ đề, thêm 28/10/2026 sau lỗi Vinspeed scene4:
    # từ dài hơn 2 giây hoặc nhiều dòng cùng start/end trong một part
    # là dấu hiệu align vỡ (trước sửa: "-" dài 7,12 giây, 6 dòng cùng
    # mốc 60,077-60,25). Cảnh báo in ra rõ ràng, không để lỗi qua mặt
    # như vụ 0 SFX trước đó; người chạy phải xem lại trước khi render.
    for _part in karaoke:
        _seen = {}
        for _ln in _part["lines"]:
            _key = (_ln["start"], _ln["end"])
            if _key in _seen:
                print(f"KARAOKE-WARN {_part['partId']}: dòng trùng mốc "
                      f"{_key}: '{_seen[_key]}' và '{_ln['text']}'")
            _seen[_key] = _ln["text"]
            for _w in _ln["words"]:
                if _w["end"] - _w["start"] > 2.0:
                    print(f"KARAOKE-WARN {_part['partId']}: từ dài "
                          f"{_w['end'] - _w['start']:.2f}s: {_w}")

    sub_dir = proj / "build" / "subtitles"
    sub_dir.mkdir(parents=True, exist_ok=True)
    (sub_dir / "karaoke.json").write_text(
        json.dumps(karaoke, ensure_ascii=False, indent=1), encoding="utf-8")
    (sub_dir / "sent_cues.json").write_text(
        json.dumps(sent_cues, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- karaoke.ass (\\k từng chữ rời, vàng #FBBF24) ---
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Anton,{font_size},&H0024BFFB&,&H00FFFFFF&,&H80000000&,&H80000000&,1,0,0,0,100,100,0,0,1,2,1,2,20,20,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    # #FBBF24 -> ASS &HAABBGGRR& = &H0024BFFB& (BBGGRR, xem ghi chú đầu file)
    events = []
    for part in karaoke:
        for ln in part["lines"]:
            toks = []
            for i, w in enumerate(ln["words"]):
                dur = max(0.01, w["end"] - w["start"])
                centis = max(1, round(dur * 100))
                toks.append(f"{{\\k{centis}}}{(' ' if i else '')}{w['text']}")
            text = "".join(toks) if toks else ln["text"]
            events.append(
                f"Dialogue: 0,{ass_time(ln['start'])},{ass_time(ln['end'])},"
                f"Karaoke,,0,0,0,,{text}")
    (sub_dir / "karaoke.ass").write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    n_words = sum(len(ln["words"]) for part in karaoke for ln in part["lines"])
    n_lines = sum(len(part["lines"]) for part in karaoke)
    print(f"KARAOKE-OK parts={len(karaoke)} lines={n_lines} words={n_words} target={target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
