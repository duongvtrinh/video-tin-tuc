#!/usr/bin/env python3
"""Lớp từ điển viết tắt cho VieNeu-TTS — ĐỘC LẬP với engine TTS.

Vấn đề: engine Vieneu chuẩn hoá bằng sea-g2p (bên trong thư mục TTS, KHÔNG
được sửa) vẫn đọc sai một số từ/cụm: tên nhóm BIGBANG thành từng chữ cái
"bê i gờ bê a nờ gờ", WORLD TOUR thành "vê kép ô rờ lờ...", chữ X trong
"mạng xã hội X" thành số "mười". Agent rà soát output chuẩn hoá
(build/norm_chunks.json), tìm những chỗ còn sót, và ghi cách đọc đúng vào
từ điển của project.

File từ điển: <project>/abbr_dict.json (nằm trong thư mục dự án):
    {"version": 1,
     "entries": {"BIGBANG": "bích beng",
                 "WORLD TOUR": "uôn tua",
                 "COSMOS": "cốt mốt",
                 "mạng xã hội X": "mạng xã hội ích"}}
Dạng phẳng (toàn bộ key cấp cao là term -> cách đọc) cũng được chấp nhận;
key bắt đầu bằng "_" được bỏ qua (dùng ghi chú).

Từ 29/10/2026, bước rà soát này là LỚP AI BẮT BUỘC cho mọi video mới
(quy tắc CEO, xem skill Sản xuất mục "Lớp AI rà soát phát âm sau sea-g2p"):
chạy normalize_chunks lần đầu, rà soát có hệ thống toàn bộ output theo
6 nhóm (token viết hoa/chữ-số lẫn, hậu tố la mã, chữ cái độc lập, tiếng
Anh còn trơ, danh từ riêng nước ngoài, thuật ngữ chuyên ngành), ghi entry
theo bảng quyết định của skill (tiếng Anh -> tag <en>, viết tắt tiếng Việt
-> cách đọc theo ngữ cảnh, viết số ra chữ, giữ số phân biệt, bỏ hậu tố bậc
theo mặc định), chạy lại normalize_chunks để kiểm chứng rồi mới chạy TTS.

Quy tắc khớp (cố tình chặt để không phá chữ thường):
- Khớp đúng chữ hoa/thường như trong kịch bản (case-sensitive): term "AI"
  sẽ KHÔNG chạm vào từ "ai" (ngôi thứ ba) trong câu.
- Cụm dài được ưu tiên trước (sắp xếp theo độ dài giảm dần), thay một lượt
  duy nhất trên text gốc nên cách đọc đã thay không bị thay lại lần nữa.
- Ranh giới từ hai đầu (?<!\\w ... (?!\\w): "X" trong "mạng xã hội X" chỉ
  khớp khi đứng độc lập, không khớp chữ X trong từ khác.
- Cách đọc KHÔNG được chứa dấu kết câu (. ! ?) hay xuống dòng (sẽ làm lệch
  chia câu của karaoke); entry vi phạm bị bỏ qua và báo trong log.

Luật chung chữ cái đứng độc lập (CEO 30/10/2026, đo thật sea-g2p):
normalizer của engine mở rộng hầu hết chữ cái thành tên chữ cái (N→nờ,
S→ét, T→tê...) nhưng để trơ 3 chữ Đ/Ă/Â: Đ/Ă thành token chết (G2P đi
xuyên, audio mất tiếng — vụ TOPIC-067: "ông N.S.Đ." nghe thành
"ông N S"), Â bị G2P đọc sang tiếng Anh ("a circumflex"). Luật này
chạy tự động cho mọi project, không cần entry từng project: chữ cái
đứng một mình (ranh giới từ hai đầu, có hoặc không có chấm đi kèm)
được đổi thành tên chữ cái — Đ→đờ, Ă→á, Â→ớ — và KHÔNG chạm chữ
trong từ (ĐÀO, ĐÔNG, ÂN). Thứ tự trong expand_text: từ điển project
trước (quyết định riêng của project thắng), luật chung sau (lấp phần
còn sót). Project mới chưa có từ điển vẫn được luật chung bảo vệ.

Ai dùng module này (đều là code factory, không chạm thư mục TTS):
- bin/normalize_chunks.py: speech_text = expand(voiceText) rồi mới gọi
  engine chuẩn hoá -> norm_chunks phản ánh đúng thứ giọng sẽ đọc.
- bin/tts_batch.py: cùng một hàm expand, cùng một từ điển, trước khi gọi
  infer() -> audio và timing karaoke dùng chung một bản speech_text.
- bin/karaoke.py: KHÔNG cần sửa — pairs (câu gốc -> câu chuẩn hoá) vẫn giữ
  câu gốc để hiển thị, align_words đã chịu được nở 1->N.

Chạy kiểm tra (chỉ in báo cáo, không ghi file):
    python bin/abbr_expand.py <project_id>
"""
import json
import re
import sys
from pathlib import Path

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
_SENT_END = re.compile(r"[.!?\n\r]")


def load_dict(proj: Path):
    """Đọc từ điển của project. Trả về (entries, path_hoặc_None).
    entries: {term: cách_đọc} đã lọc entry vi phạm quy tắc."""
    path = proj / "abbr_dict.json"
    if not path.exists():
        return {}, None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # từ điển hỏng: không chặn pipeline, chỉ bỏ qua
        print(f"ABBR-WARN dict hỏng, bỏ qua: {exc}", file=sys.stderr)
        return {}, path
    if isinstance(raw, dict) and isinstance(raw.get("entries"), dict):
        mapping = raw["entries"]
    elif isinstance(raw, dict):
        mapping = {k: v for k, v in raw.items() if not k.startswith("_")}
    else:
        mapping = {}
    entries, skipped = {}, []
    for term, spoken in mapping.items():
        if not isinstance(term, str) or not term.strip():
            skipped.append((term, "term rỗng"))
            continue
        if not isinstance(spoken, str) or not spoken.strip():
            skipped.append((term, "cách đọc rỗng"))
            continue
        if _SENT_END.search(spoken):
            skipped.append((term, "cách đọc chứa dấu kết câu/xuống dòng"))
            continue
        entries[term.strip()] = " ".join(spoken.split())
    for term, reason in skipped:
        print(f"ABBR-WARN bỏ entry {term!r}: {reason}", file=sys.stderr)
    return entries, path


def build_pattern(entries: dict):
    """Một regex duy nhất, cụm dài trước, ranh giới từ hai đầu."""
    if not entries:
        return None
    terms = sorted(entries, key=len, reverse=True)
    alt = "|".join(re.escape(t) for t in terms)
    return re.compile(r"(?<!\w)(?:" + alt + r")(?!\w)")


def expand_text(text: str, entries: dict):
    """Trả về (text_đã_mở_rộng, {term: số_lần_thay}).
    Thứ tự: từ điển project trước, luật chung Đ/Ă/Â sau. Không có
    entries -> chỉ luật chung (text gốc nếu cũng không có chữ cần sửa)."""
    hits = {}
    if entries:
        pattern = build_pattern(entries)

        def _sub(m):
            hits[m.group(0)] = hits.get(m.group(0), 0) + 1
            return entries[m.group(0)]

        text = pattern.sub(_sub, text)
    text, letter_hits = apply_letter_fix(text)
    hits.update(letter_hits)
    return text, hits


# Luật chung chữ cái đứng độc lập (xem docstring): chỉ chữ cái đứng một
# mình, ranh giới từ hai đầu (re \w đã bao gồm chữ có dấu tiếng Việt).
_LETTER_FIX = {"Đ": "đờ", "đ": "đờ", "Ă": "á", "ă": "á", "Â": "ớ", "â": "ớ"}
_LETTER_FIX_RE = re.compile(r"(?<!\w)([ĐĂÂđăâ])(?!\w)")


def apply_letter_fix(text: str):
    """Luật chung Đ/Ă/Â đứng độc lập. Trả về (text_đã_sửa, hits).
    Không có chữ cần sửa -> (text gốc, {})."""
    hits = {}

    def _sub(m):
        name = _LETTER_FIX[m.group(1)]
        key = f"{m.group(1)}→{name} (luật chung)"
        hits[key] = hits.get(key, 0) + 1
        return name

    return _LETTER_FIX_RE.sub(_sub, text), hits


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: abbr_expand.py <project_id>", file=sys.stderr)
        return 2
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    entries, path = load_dict(proj)
    if path is None:
        print(f"ABBR-EMPTY {pid}: chưa có abbr_dict.json trong thư mục dự án")
        return 0
    total_hits = {}
    n_parts = 0
    for sc in plan["scenes"]:
        for pt in sc["parts"]:
            _, hits = expand_text(pt["voiceText"], entries)
            if hits:
                n_parts += 1
                print(f"{pt['id']}: {hits}")
                for term, n in hits.items():
                    total_hits[term] = total_hits.get(term, 0) + n
    print(f"ABBR-OK entries={len(entries)} parts_applied={n_parts} "
          f"total_hits={sum(total_hits.values())} hits={total_hits}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
