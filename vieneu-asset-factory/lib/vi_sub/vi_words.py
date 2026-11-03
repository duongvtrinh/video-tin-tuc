"""
VieNeu Studio - Vietnamese compound-word detection
Dùng underthesea để biết hai âm tiết liền kề có thuộc cùng một từ ghép hay không
(vd. "đại | học", "phát | triển") nhằm tránh cắt phụ đề ngay giữa từ ghép.

Nếu underthesea chưa được cài, mọi hàm vẫn chạy: coi mỗi âm tiết là một từ riêng
(chỉ mất khả năng nhận diện từ ghép, các tín hiệu khác như dấu câu và VAD vẫn dùng được).
"""

from __future__ import annotations

import functools
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional, Sequence

try:
    from core.common.logger import get_logger
except Exception:
    import logging
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger("vi_words")

_tokenize: Optional[Callable[[str], list[str]]] = None
_tokenize_loaded = False


def _get_tokenizer() -> Optional[Callable[[str], list[str]]]:
    """Lazy-load underthesea.word_tokenize (chỉ thử import một lần)."""
    global _tokenize, _tokenize_loaded
    if _tokenize_loaded:
        return _tokenize
    _tokenize_loaded = True

    # 1. Thử import trực tiếp từ môi trường hiện tại
    try:
        from underthesea import word_tokenize  # type: ignore

        _tokenize = word_tokenize
        logger.info("underthesea available: compound-word aware subtitle splitting enabled.")
        return _tokenize
    except Exception:
        pass

    # 2. Cầu nối tự động (Bridge): nạp underthesea từ môi trường .venv ở thư mục gốc nếu tools/VieNeu-TTS chạy riêng
    try:
        import sys
        root_dir = Path(__file__).resolve().parents[2]
        candidate_site_packages = [
            root_dir / ".venv" / "Lib" / "site-packages",
            root_dir / ".venv" / "lib" / "python3.10" / "site-packages",
            root_dir / ".venv" / "lib" / "python3.11" / "site-packages",
            root_dir / ".venv" / "lib" / "python3.12" / "site-packages",
        ]
        for sp in candidate_site_packages:
            if sp.is_dir() and str(sp) not in sys.path:
                sys.path.append(str(sp))

        from underthesea import word_tokenize  # type: ignore

        _tokenize = word_tokenize
        logger.info("underthesea available (bridged from root .venv): compound-word aware subtitle splitting enabled.")
        return _tokenize
    except Exception as exc:
        _tokenize = None
        logger.warning("underthesea unavailable (%s); falling back to syllable-only splitting. "
                       "Cài đặt: pip install underthesea", exc)
    return _tokenize


def segmenter_name() -> str:
    """'underthesea' nếu tách từ được, ngược lại 'syllable'."""
    return "underthesea" if _get_tokenizer() is not None else "syllable"


def _compact(text: str) -> str:
    """Chuỗi chỉ gồm chữ/số (NFC, casefold): dùng để đối chiếu vị trí ký tự giữa các cách tách từ."""
    norm = unicodedata.normalize("NFC", text).casefold()
    return "".join(ch for ch in norm if ch.isalnum())



# --- Từ điển từ ghép bổ sung ---------------------------------------------------------------------------------
_LEXICON: Optional[dict[str, list[tuple[str, ...]]]] = None


def _lexicon_files() -> list[Path]:
    files = [Path(__file__).with_name("vi_compounds.txt")]
    try:
        import config

        files.append(Path(config.DATA_DIR) / "vi_compounds.txt")  # cụm riêng của người dùng (tùy chọn)
    except Exception:
        pass
    return files


def _load_lexicon() -> dict[str, list[tuple[str, ...]]]:
    """Đọc các cụm từ ghép; trả về {âm tiết đầu: [cụm dài nhất trước]}."""
    global _LEXICON
    if _LEXICON is not None:
        return _LEXICON
    index: dict[str, list[tuple[str, ...]]] = {}
    for path in _lexicon_files():
        if not path.is_file():
            continue
        try:
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                cores = tuple(c for c in (_compact(t) for t in line.split()) if c)
                if len(cores) >= 2:
                    index.setdefault(cores[0], []).append(cores)
        except OSError as exc:
            logger.warning("Cannot read compound lexicon %s: %s", path, exc)
    for phrases in index.values():
        phrases.sort(key=len, reverse=True)
    _LEXICON = index
    return index


def reload_lexicon() -> None:
    """Đọc lại file từ điển (sau khi sửa data/vi_compounds.txt)."""
    global _LEXICON
    _LEXICON = None
    _analyze_cached.cache_clear()


def _apply_lexicon(words: Sequence[str], comp_words: Sequence[str], compound: list[bool], unit_len: list[int]) -> None:
    index = _load_lexicon()
    if not index:
        return
    n = len(words)
    for i in range(n - 1):
        for phrase in index.get(comp_words[i], ()):
            m = len(phrase)
            if i + m > n:
                continue
            if any(comp_words[i + k] != phrase[k] for k in range(m)):
                continue
            # không nối qua dấu câu (vd. "máy, tính")
            if any(not words[i + k][-1].isalnum() for k in range(m - 1)):
                continue
            for k in range(m - 1):
                compound[i + k] = True
                unit_len[i + k] = 2  # từ điển: coi là từ ghép chắc chắn (phạt cắt mạnh)
            break


@dataclass(frozen=True)
class Boundaries:
    """Thông tin ranh giới giữa các âm tiết liền kề (độ dài n-1 với n âm tiết)."""

    compound: tuple[bool, ...]   # True nếu âm tiết i và i+1 thuộc cùng một từ ghép
    unit_len: tuple[int, ...]    # số âm tiết của từ chứa ranh giới đó (0 nếu không phải từ ghép)
    method: str                  # "underthesea" | "syllable"


def _plain(n: int, method: str) -> Boundaries:
    return Boundaries((False,) * max(0, n - 1), (0,) * max(0, n - 1), method)


def _lexicon_only(words: Sequence[str], comp_words: Sequence[str]) -> Boundaries:
    n = len(words)
    compound = [False] * (n - 1)
    unit_len = [0] * (n - 1)
    _apply_lexicon(words, comp_words, compound, unit_len)
    return Boundaries(tuple(compound), tuple(unit_len), "syllable")


@functools.lru_cache(maxsize=2048)
def _analyze_cached(words: tuple[str, ...]) -> Boundaries:
    n = len(words)
    if n < 2:
        return _plain(n, "syllable")
    comp_words = [_compact(w) for w in words]
    tokenize = _get_tokenizer()
    if tokenize is None:
        return _lexicon_only(words, comp_words)

    try:
        units = tokenize(" ".join(words))
    except Exception as exc:
        logger.warning("word_tokenize failed (%s); using syllable-only boundaries.", exc)
        return _lexicon_only(words, comp_words)

    unit_of_char: list[int] = []
    unit_first_word_count: dict[int, int] = {}
    for k, unit in enumerate(units):
        unit_of_char.extend([k] * len(_compact(unit)))

    # Hai cách tách phải cho cùng chuỗi ký tự thì mới đối chiếu vị trí được
    if "".join(comp_words) != "".join(_compact(u) for u in units):
        logger.debug("Tokenizer output does not align with input words; skipping underthesea compounds.")
        return _lexicon_only(words, comp_words)

    first: list[Optional[int]] = []
    last: list[Optional[int]] = []
    pos = 0
    for c in comp_words:
        if c:
            first.append(pos)
            last.append(pos + len(c) - 1)
            pos += len(c)
        else:  # từ chỉ có dấu câu
            first.append(None)
            last.append(None)

    for f in first:
        if f is not None:
            k = unit_of_char[f]
            unit_first_word_count[k] = unit_first_word_count.get(k, 0) + 1

    compound: list[bool] = []
    unit_len: list[int] = []
    for i in range(n - 1):
        if last[i] is None or first[i + 1] is None:
            compound.append(False)
            unit_len.append(0)
            continue
        ka, kb = unit_of_char[last[i]], unit_of_char[first[i + 1]]  # type: ignore[index]
        same = ka == kb
        compound.append(same)
        unit_len.append(unit_first_word_count.get(ka, 0) if same else 0)
    _apply_lexicon(words, comp_words, compound, unit_len)
    return Boundaries(tuple(compound), tuple(unit_len), "underthesea")


def analyze_compounds(words: Sequence[str]) -> Boundaries:
    """Với danh sách âm tiết (tách theo khoảng trắng, còn dấu câu), trả về ranh giới từ ghép."""
    return _analyze_cached(tuple(words))
