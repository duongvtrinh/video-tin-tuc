#!/usr/bin/env python3
"""Chuẩn hoá text ĐÚNG NHƯ Vieneu-TTS đọc (tái sử dụng normalize_to_chunks_v3_with_gaps
của engine, max_chars=140 như infer()) để phụ đề dùng đúng chữ mà giọng đọc phát ra.

Sau lớp sea-g2p của engine, agent rà soát norm_chunks để tìm viết tắt còn sót
(vd BIGBANG đọc thành từng chữ cái) và ghi cách đọc đúng vào <project>/abbr_dict.json.
File này áp từ điển TRƯỚC khi gọi engine (xem bin/abbr_expand.py):
speech_text = expand(voiceText); norm = engine.normalize(speech_text). Nhờ vậy
audio (tts_batch, cùng một từ điển) và timing karaoke dùng chung một bản
speech_text, còn câu hiển thị trong pairs vẫn là câu gốc.

Ví dụ: "năm 1991" -> "năm một nghìn chín trăm chín mươi mốt",
        "GDP" -> "<en>g d p</en>" (đọc từng chữ cái).

Chạy bằng TTS venv (máy gốc: vieneu-tts-api, bản clone: vieneu-tts —
    xem _tts_dir() trong tts_batch.py và BOOTSTRAP §3):
    <thư-mục-TTS>/.venv/bin/python bin/normalize_chunks.py <project_id>

Ghi: build/norm_chunks.json  {partId: {"chunks": [...], "gaps": [...]}}

CHUNK 140 KÝ TỰ — LỰA CHỌN ĐÃ CHỐT (Giai đoạn 4, 05/11/2026):
MAX_CHARS = 140 là giá trị duy nhất trong pipeline này, dùng để "gương"
theo infer() của engine Vieneu v3 Nano như tài liệu của engine mô tả lúc
viết code; mã nguồn engine KHÔNG nằm trong repo này (vieneu-tts local
chỉ có server/CLI, không có infer()) nên không kiểm chứng được tại đây
rằng engine hiện tại vẫn chunk đúng 140 — nếu engine đổi giới hạn, chỉ
sửa MAX_CHARS ở file này, không sửa rải rác. Quan trọng: timing karaoke
KHÔNG dùng biên chunk này — karaoke.py align từng chữ gốc -> span chữ
chuẩn hoá (pairs) rồi gắn mốc bằng VAD trên WAV thật, nên engine tự
chunk khác biên KHÔNG làm lệch timing karaoke; thứ sẽ lệch khi giới hạn
đổi chỉ là danh sách chunks trong norm_chunks.json (không còn gương
đúng các chunk synthesis). Đừng vì vậy mà "sửa" karaoke theo biên chunk.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from abbr_expand import expand_text, load_dict  # noqa: E402
from filename import atomic_write_text, check_plan  # noqa: E402  (Giai đoạn 5)

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)

MAX_CHARS = 140  # khớp infer() của Vieneu v3 Nano


def sentence_pairs_expanded(orig_text: str, speech_text: str):
    """Tách câu GỐC để hiển thị và chuẩn hoá bản SPEECH (voiceText đã mở
    rộng qua abbr_dict) để làm timing. Hai bản có cùng số câu (cách đọc
    không chứa dấu kết câu, đã chặn ở load_dict); nếu lệch thì ghép cả đoạn
    (câu gốc giữ nguyên để hiển thị, norm vẫn là bản speech)."""
    import re
    from vieneu_utils.phonemize_text import _normalized_sentences_by_para
    from vieneu_utils.core_utils import split_into_sentences

    orig_paras = [p for p in re.split(r"\n+", orig_text) if p.strip()]
    norm_paras = _normalized_sentences_by_para(speech_text)
    pairs = []
    for pi, para in enumerate(orig_paras):
        orig_sents = split_into_sentences(para)
        norm_sents = norm_paras[pi] if pi < len(norm_paras) else []
        if len(orig_sents) == len(norm_sents) and orig_sents:
            pairs.extend(zip(orig_sents, norm_sents))
        else:
            pairs.append((para, " ".join(norm_sents)))
    return pairs


def main() -> int:
    from vieneu_utils.phonemize_text import normalize_to_chunks_v3_with_gaps

    if len(sys.argv) < 2:
        print("usage: normalize_chunks.py <project_id>", file=sys.stderr)
        return 2
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    try:
        plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"NORM-ERROR {pid}: không đọc được plan: {exc}", file=sys.stderr)
        return 1
    try:
        scenes = check_plan(plan, require_voice_text=True)
    except ValueError as exc:
        print(f"NORM-ERROR {pid}: {exc}", file=sys.stderr)
        return 1
    try:
        entries, dict_path = load_dict(proj)
    except ValueError as exc:
        # Từ điển hỏng là CHẶN (xem abbr_expand.load_dict): dừng trước
        # khi ghi norm_chunks sai, không chạy tiếp với từ điển rỗng.
        print(f"NORM-ERROR {pid}: {exc} — sửa abbr_dict.json rồi chạy lại",
              file=sys.stderr)
        return 1
    out = {}
    n_applied = 0
    for sc in scenes:
        for pt in sc["parts"]:
            speech, hits = expand_text(pt["voiceText"], entries)
            chunks, gaps = normalize_to_chunks_v3_with_gaps(speech,
                                                            max_chars=MAX_CHARS)
            pairs = sentence_pairs_expanded(pt["voiceText"], speech)
            if hits:
                n_applied += 1
            out[pt["id"]] = {"chunks": chunks, "gaps": gaps,
                             "pairs": [list(p) for p in pairs],
                             "speech_text": speech,
                             "abbr_applied": bool(hits),
                             "abbr_hits": hits}

    build = proj / "build"
    build.mkdir(parents=True, exist_ok=True)
    # Giai đoạn 5: ghi tạm rồi rename, không ghi đè trực tiếp — crash
    # giữa chừng không để lại norm_chunks.json bị cắt nửa chừng.
    atomic_write_text(build / "norm_chunks.json",
                      json.dumps(out, ensure_ascii=False, indent=1))
    n_chunks = sum(len(v["chunks"]) for v in out.values())
    print(f"NORM-OK parts={len(out)} chunks={n_chunks} max_chars={MAX_CHARS}")
    if dict_path is not None:
        print(f"ABBR-OK dict=abbr_dict.json entries={len(entries)} parts_applied={n_applied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
