"""
VieNeu Studio - Smart subtitle phrase splitter
==============================================
Chia một phụ đề (cue) dài thành các cụm ngắn ~N từ một cách hợp lý, và căn thời gian theo giọng đọc thật.

Ý tưởng (thay cho cách cắt cứng "mỗi N từ" trước đây):
  1. Tách từ ghép bằng underthesea -> không cắt giữa "đại | học", "phát | triển"...
  2. Chấm điểm từng vị trí có thể cắt (dấu câu, liên từ, từ chức năng, từ ghép) rồi chọn cách chia có
     tổng điểm tốt nhất bằng quy hoạch động, bám sát độ dài mục tiêu.
  3. Nếu có kết quả VAD của track giọng đọc: các quãng nghỉ THẬT trong giọng nói được gán vào ranh giới
     từ (theo tỉ lệ độ dài âm tiết), được thưởng điểm khi cắt và dùng làm mốc thời gian chính xác.
  4. Không có VAD: thời gian chia theo trọng số âm tiết + khoảng nghỉ ở dấu câu (tốt hơn chia theo số từ).

Module này thuần logic (không đọc file audio) nên test được dễ dàng. Xem core/subtitles/voice_track.py
để lấy các quãng "có tiếng" từ track giọng đọc.
"""

from __future__ import annotations

import bisect
import re
import unicodedata
from typing import Any, Optional, Sequence

from vi_words import Boundaries, analyze_compounds, segmenter_name

Interval = tuple[float, float]

# --- Từ chức năng tiếng Việt (chữ thường, không dấu câu) -------------------------------------------------------
# Không nên ngắt NGAY SAU những từ này (chúng cần từ phía sau để trọn nghĩa).
NO_BREAK_AFTER = frozenset({
    "của", "và", "với", "cùng", "để", "cho", "những", "các", "một", "mỗi", "mọi", "từng", "rất", "đã", "sẽ",
    "đang", "vừa", "không", "chưa", "cũng", "vẫn", "còn", "là", "mà", "bị", "được", "trong", "ngoài", "trên",
    "dưới", "từ", "đến", "tại", "về", "như", "bằng", "theo", "do", "bởi", "vì", "nếu", "khi", "lúc", "nhưng",
    "hoặc", "thì", "cả", "chỉ", "đều", "phải", "nhằm", "tuy", "song", "rồi",
    # Giới từ chỉ vị trí / hướng và loại từ chỉ đơn vị thiết yếu
    "ở", "vào", "qua", "lên", "xuống", "sang", "ra", "chiếc", "con", "cái", "viên", "bức", "tấm", "cây",
})
# Ngắt TRƯỚC những từ này thì tự nhiên (mở đầu một vế/cụm mới).
BREAK_BEFORE = frozenset({
    "và", "nhưng", "tuy", "song", "mà", "thì", "vì", "bởi", "nếu", "khi", "để", "rồi", "hoặc", "còn", "nhằm",
    "nên", "do",
})

_STRONG_PUNCT = frozenset(".!?…")
_MEDIUM_PUNCT = frozenset(";:—–")
_TAIL_STRIP = re.compile(r"[\"'”’»)\]}]+$")
_NUM_RE = re.compile(r"^[\$€£¥₫]?\d+([.,/]\d+)*[%]?$")
_UNITS = frozenset({
    "usd", "vnd", "vnđ", "đồng", "đô", "dollar", "euro", "tỷ", "triệu", "nghìn", "ngàn",
    "km", "m", "cm", "mm", "kg", "g", "tấn", "tạ", "yến", "lít", "ml", "ha", "m2", "m3",
    "giờ", "phút", "giây", "ngày", "tháng", "năm", "tuổi", "người", "chiếc", "cái", "con",
    "lần", "bước", "phần", "điểm", "độ",
})

# Trọng số "thời gian đọc" tương đối của khoảng nghỉ sau dấu câu (đơn vị ~ một âm tiết trung bình)
_PAUSE_WEIGHT = {".": 1.8, "!": 1.8, "?": 1.8, "…": 1.8, ";": 1.2, ":": 1.0, ",": 0.9, "—": 0.9, "–": 0.9}

CHUNK_COST = 1.0          # phạt nhẹ mỗi cụm để không cắt vụn
LENGTH_WEIGHT = 4.0       # trọng số độ lệch so với độ dài mục tiêu (hạ từ 6.0 để ưu tiên ngữ nghĩa câu)
OUT_OF_RANGE_COST = 30.0  # phạt cụm quá ngắn/quá dài


def _core(word: str) -> str:
    norm = unicodedata.normalize("NFC", word).casefold()
    return "".join(ch for ch in norm if ch.isalnum())


def _tail_punct(word: str) -> str:
    w = _TAIL_STRIP.sub("", word)
    return w[-1] if w and not w[-1].isalnum() else ""


def _is_number(word: str) -> bool:
    clean = word.strip("""\"'“”’()[].!?,;:-""")
    return bool(_NUM_RE.match(clean))


def _word_weight(core: str) -> float:
    if not core:
        return 0.3
    return min(1.6, max(0.8, 0.6 + 0.12 * len(core)))


def length_bounds(target: int) -> tuple[int, int]:
    """(độ dài tối thiểu, tối đa) cho phép của một cụm, tính bằng số từ."""
    target = max(1, int(target))
    return max(2, round(target * 0.6)), target + max(2, round(target * 0.5))


# --- Chấm điểm vị trí cắt ------------------------------------------------------------------------------------
def _boundary_costs(words: Sequence[str], bounds: Boundaries, measured_gap: Sequence[float]):
    """Trả về (cost, linear_cost); chỉ số b = ranh giới ngay TRƯỚC từ b (1..n-1). Càng thấp càng nên cắt."""
    n = len(words)
    cores = [_core(w) for w in words]
    cost = [0.0] * (n + 1)
    linear = [0.0] * (n + 1)
    for b in range(1, n):
        c = 0.0
        # 1. Từ ghép tiếng Việt (phạt cấm cắt mạnh giữa từ ghép)
        if bounds.compound[b - 1]:
            c += 12.0 if bounds.unit_len[b - 1] <= 2 else 7.0

        # 2. Không cắt rời Số + Đơn vị tính (5.000 USD, 40.000 tỷ, 100 km, v.v.)
        prev_is_num = _is_number(words[b - 1])
        cur_is_unit = cores[b] in _UNITS or _is_number(words[b])
        if prev_is_num and cur_is_unit:
            c += 14.0
        elif cores[b - 1] in ("tỷ", "triệu", "nghìn", "ngàn") and cores[b] in ("usd", "vnd", "vnđ", "đồng", "đô", "dollar", "euro"):
            c += 14.0

        # 3. Dấu câu & Từ chức năng
        tail = _tail_punct(words[b - 1])
        if tail in _STRONG_PUNCT:
            c -= 8.0
        elif tail in _MEDIUM_PUNCT:
            c -= 6.0
        elif tail == ",":
            c -= 4.5
        elif cores[b - 1] in NO_BREAK_AFTER:
            c += 6.0
        if cores[b] in BREAK_BEFORE:
            c -= 2.5
        linear[b] = c
        cost[b] = c - min(measured_gap[b], 0.5) * 20.0  # quãng nghỉ 0.5s ~ -10 điểm
    return cost, linear


def _length_cost(length: int, target: int, mn: int, mx: int) -> float:
    c = ((length - target) / max(1, target)) ** 2 * LENGTH_WEIGHT
    if length > mx:
        c += OUT_OF_RANGE_COST * (length - mx)
    if length < mn:
        c += OUT_OF_RANGE_COST * (mn - length)
    return c


def _partition(n: int, cost: Sequence[float], target: int) -> list[int]:
    """Quy hoạch động: trả về danh sách chỉ số bắt đầu của các cụm (luôn gồm 0)."""
    mn, mx = length_bounds(target)
    inf = float("inf")
    best = [inf] * (n + 1)
    prev = [0] * (n + 1)
    best[0] = 0.0
    for j in range(1, n + 1):
        for i in range(max(0, j - mx - 4), j):
            if best[i] == inf:
                continue
            c = best[i] + _length_cost(j - i, target, mn, mx) + CHUNK_COST
            if j < n:
                c += cost[j]
            if c < best[j]:
                best[j] = c
                prev[j] = i
    starts: list[int] = []
    j = n
    while j > 0:
        starts.append(prev[j])
        j = prev[j]
    starts.reverse()
    return starts


# --- Thời gian từng từ ---------------------------------------------------------------------------------------
def _text_timing(weights: Sequence[float], pauses: Sequence[float], start: float, end: float):
    n = len(weights)
    total = sum(weights) + sum(pauses[: n - 1])
    scale = (end - start) / total if total > 0 else 0.0
    starts: list[float] = []
    ends: list[float] = []
    t = start
    for i in range(n):
        starts.append(t)
        t += weights[i] * scale
        ends.append(t)
        if i < n - 1:
            t += pauses[i] * scale
    return starts, ends, [0.0] * (n + 1)


def _clip_runs(speech: Sequence[Interval], lo: float, hi: float, min_gap: float, min_run: float = 0.03) -> list[Interval]:
    """Cắt các quãng có tiếng vào cửa sổ [lo, hi], gộp các quãng nghỉ ngắn hơn min_gap."""
    runs: list[list[float]] = []
    for s, e in speech:
        s2, e2 = max(s, lo), min(e, hi)
        if e2 - s2 <= 0:
            continue
        if runs and s2 - runs[-1][1] < min_gap:
            runs[-1][1] = max(runs[-1][1], e2)
        else:
            runs.append([s2, e2])
    return [(a, b) for a, b in runs if b - a >= min_run]


def _vad_timing(weights: Sequence[float], runs: list[Interval], bcost_linear: Sequence[float]):
    """Gán từ vào các quãng có tiếng: quãng nghỉ thứ j -> ranh giới từ có tỉ lệ độ dài gần nhất."""
    n = len(weights)
    runs = list(runs)
    while len(runs) > n:  # nhiều quãng nghỉ hơn số từ: gộp các quãng nghỉ ngắn nhất
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        i = min(range(len(gaps)), key=gaps.__getitem__)
        runs[i:i + 2] = [(runs[i][0], runs[i + 1][1])]
    k = len(runs)

    cw = [0.0]
    for w in weights:
        cw.append(cw[-1] + w)
    total_w = cw[-1]
    mean_w = total_w / n
    total_r = sum(e - s for s, e in runs)

    cuts: list[int] = []  # ranh giới (chỉ số từ đầu tiên của quãng kế tiếp)
    acc = 0.0
    prev_b = 0
    for j in range(k - 1):
        acc += runs[j][1] - runs[j][0]
        target = total_w * acc / total_r
        lower = prev_b + 1
        upper = n - 1 - (k - 2 - j)  # chừa ít nhất 1 từ cho mỗi quãng còn lại
        nearest = min(range(lower, upper + 1), key=lambda b: abs(cw[b] - target))
        best_b, best_score = nearest, float("inf")
        for b in range(max(lower, nearest - 2), min(upper, nearest + 2) + 1):
            score = abs(cw[b] - target) / mean_w + 0.35 * bcost_linear[b]
            if score < best_score:
                best_b, best_score = b, score
        cuts.append(best_b)
        prev_b = best_b

    starts = [0.0] * n
    ends = [0.0] * n
    measured = [0.0] * (n + 1)
    edges = [0] + cuts + [n]
    for j in range(k):
        a, b = edges[j], edges[j + 1]
        rs, re_ = runs[j]
        span_w = cw[b] - cw[a]
        for i in range(a, b):
            starts[i] = rs + (cw[i] - cw[a]) / span_w * (re_ - rs)
            ends[i] = rs + (cw[i + 1] - cw[a]) / span_w * (re_ - rs)
        if j < k - 1:
            measured[b] = runs[j + 1][0] - runs[j][1]
    return starts, ends, measured, (runs[0][0], runs[-1][1])


# --- API chính -----------------------------------------------------------------------------------------------
def _r(x: float) -> float:
    return round(float(x), 3)


def split_cue(
    text: str,
    start: float,
    end: float,
    target_words: int,
    runs: Optional[Sequence[Interval]] = None,
    *,
    window: Optional[Interval] = None,
    retime: bool = True,
    min_gap: float = 0.06,
) -> list[dict[str, Any]]:
    """
    Chia một cue thành các cụm ngắn.

    text          : nội dung phụ đề (các từ cách nhau bởi khoảng trắng)
    start, end    : thời gian cue hiện tại (giây, trên timeline)
    target_words  : số từ mong muốn mỗi cụm
    runs          : các quãng CÓ TIẾNG (giây, timeline) từ VAD; None -> chỉ dùng văn bản
    window        : cửa sổ được phép lấy tiếng (mặc định [start, end])
    retime        : True -> thời gian cụm bám theo tiếng thật; False -> giữ nguyên [start, end] của cue gốc

    Trả về danh sách dict: text, start, end, source ("vad"|"text"), words[{text,start,end}],
    tokens[{text,duration,startOffset,endOffset}] (dùng trực tiếp cho karaoke).
    """
    words = text.split()
    n = len(words)
    if n == 0 or end <= start:
        return [{"text": text, "start": _r(start), "end": _r(end), "source": "text", "words": [], "tokens": []}]

    target = max(1, int(target_words or 1))
    cores = [_core(w) for w in words]
    weights = [_word_weight(c) for c in cores]
    pauses = [_PAUSE_WEIGHT.get(_tail_punct(w), 0.0) for w in words]
    bounds = analyze_compounds(words)

    # 1) Thời gian từng từ
    lo, hi = window if window else (start, end)
    source = "text"
    timing = None
    if runs:
        clipped = _clip_runs(runs, lo, hi, min_gap)
        speech_total = sum(e - s for s, e in clipped)
        if clipped and speech_total >= max(0.12, 0.04 * n):
            zero_gap = [0.0] * (n + 1)
            _, linear = _boundary_costs(words, bounds, zero_gap)
            w_starts, w_ends, measured, span = _vad_timing(weights, clipped, linear)
            timing = (w_starts, w_ends, measured, span)
            source = "vad"
    if timing is None:
        w_starts, w_ends, measured = _text_timing(weights, pauses, start, end)
        span = (start, end)
    else:
        w_starts, w_ends, measured, span = timing

    # 2) Chọn điểm cắt
    if n <= target:
        chunk_starts = [0]
    else:
        cost, _ = _boundary_costs(words, bounds, measured)
        chunk_starts = _partition(n, cost, target)
    edges = chunk_starts + [n]

    # 3) Mốc thời gian cắt giữa các cụm
    cut_end: dict[int, float] = {}
    cut_start: dict[int, float] = {}
    for b in edges[1:-1]:
        gs, ge = w_ends[b - 1], w_starts[b]
        gap = ge - gs
        if gap <= 0.02:
            mid = (gs + ge) / 2
            cut_end[b] = cut_start[b] = mid
        else:
            mid = (gs + ge) / 2
            cut_end[b] = min(gs + 0.12, mid)
            cut_start[b] = max(ge - 0.06, mid)

    if source == "vad" and retime:
        first_start = max(lo, span[0] - 0.04)
        last_end = min(hi, span[1] + 0.10)
    else:
        first_start, last_end = start, end
    if last_end <= first_start:
        first_start, last_end = start, end

    out: list[dict[str, Any]] = []
    for idx in range(len(edges) - 1):
        a, b = edges[idx], edges[idx + 1]
        c_start = first_start if idx == 0 else cut_start[a]
        c_end = last_end if idx == len(edges) - 2 else cut_end[b]
        if c_end - c_start < 0.05:  # bảo vệ: cụm quá ngắn
            c_end = c_start + 0.05

        tokens = []
        word_items = []
        for i in range(a, b):
            w_s = c_start if i == a else max(c_start, w_starts[i])
            nxt = c_end if i == b - 1 else max(w_s, w_starts[i + 1])
            dur = max(0.02, nxt - w_s)
            tokens.append({
                "text": ("" if i == a else " ") + words[i],
                "duration": _r(dur),
                "startOffset": _r(w_s - c_start),
                "endOffset": _r(w_s - c_start + dur),
            })
            word_items.append({"text": words[i], "start": _r(w_starts[i]), "end": _r(w_ends[i])})
        out.append({
            "text": " ".join(words[a:b]),
            "start": _r(c_start),
            "end": _r(c_end),
            "source": source,
            "words": word_items,
            "tokens": tokens,
        })
    return out


# NOTE (code-fix 29/10/2026): hàm split_cues() cũ đã xóa — grep toàn repo
# + company-os chứng minh không caller nào dùng nó (karaoke.py chỉ dùng
# split_cue() số ít). Bản sao trước khi xóa nằm ở
# company-os/code-fix-20261029/backup/vieneu-asset-factory/lib/vi_sub/phrase_splitter.py.
