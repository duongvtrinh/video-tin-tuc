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
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from abbr_expand import expand_text, load_dict  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
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

    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))

    entries, dict_path = load_dict(proj)
    out = {}
    n_applied = 0
    for sc in plan["scenes"]:
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
    (build / "norm_chunks.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    n_chunks = sum(len(v["chunks"]) for v in out.values())
    print(f"NORM-OK parts={len(out)} chunks={n_chunks} max_chars={MAX_CHARS}")
    if dict_path is not None:
        print(f"ABBR-OK dict=abbr_dict.json entries={len(entries)} parts_applied={n_applied}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
