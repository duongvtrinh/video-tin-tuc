#!/usr/bin/env python3
"""script_lint.py — kiểm tra cơ học kịch bản TRƯỚC KHI chạy TTS.

Mục đích: biến bước "đọc to rồi sửa" trong skill media-video-production thành
một cửa kiểm tra chạy được. Công cụ này KHÔNG chấm hay/dở. Nó chỉ bắt:
  - mẫu câu cấm theo luật CEO 29/10, 30/10, 31/10 (đối chiếu SCRIPT_DOCTRINE.md);
  - dấu hiệu "văn viết, không phải văn nói" (nhịp đều, câu quá dài, từ hành chính);
  - số liệu trong kịch bản không có trong dữ kiện đã kiểm chứng (--facts).

KHÔNG kiểm ký hiệu, ký tự định dạng hay cách đọc số/viết tắt: phần đó do bộ chuẩn hoá của VieNeu-TTS
(`normalize_chunks.py`, `abbr_dict.json`) lo; lint chỉ nhìn vào chất lượng viết và số liệu.

Quy ước đếm: "tiếng" = token tách theo khoảng trắng (cùng cách đếm với hệ số
4,16 tiếng/giây của TTS trong skill). Ước tính thời lượng chỉ là THÔNG TIN, không
bao giờ đạt/không đạt (luật CEO 03/11).

Dùng:
  python3 bin/script_lint.py script.txt [--facts facts.txt] [--strict] [--json]

Mã thoát: 0 = không có LỖI; 1 = có LỖI (hoặc có CẢNH BÁO khi --strict); 2 = lỗi đầu vào.
Chỉ dùng thư viện chuẩn.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import unicodedata

TIENG_PER_SEC = 4.16  # hệ số đo thật của VieNeu TTS (skill media-video-production)

# ---------------------------------------------------------------- mẫu cấm
# Mỗi mục: (mã, mức, regex trên văn bản đã hạ chữ thường, thông điệp)
# Mức: "LỖI" chặn TTS; "CẢNH BÁO" cần người/AI cân nhắc.
# Cấm theo LỚP chức năng, không chỉ theo cụm: gặp biến thể cùng chức năng vẫn phải sửa.
BAN_RULES = [
    ("C1", "LỖI", r"câu hỏi (đặt ra|đầu tiên|lớn|quan trọng|then chốt) là|vậy (thì )?điều gì|điều gì (đã )?khiến|phải chăng|(?:^|[,.!?]\s*)liệu\b|bạn có (từng )?biết|bạn có tò mò",
     "câu hỏi tu từ rỗng làm hook/cầu nối. Thay bằng sự kiện hoặc con số cụ thể."),
    ("C2", "LỖI", r"không chỉ\b.{0,80}\bmà còn|không (phải|đơn thuần|chỉ đơn thuần)\b.{0,60}\bmà (là|còn)|chẳng những|không chỉ là",
     "cấu trúc đối lập sáo 'không chỉ… mà còn / không phải… mà là'. Nói thẳng điều đúng."),
    ("C3", "LỖI", r"(^|[.!?]\s+)(trong thời đại|khi nhắc đến|từ trước đến nay|từ xưa đến nay|xưa nay)\b",
     "mở đầu khái quát. Mở bằng cảnh/sự kiện cụ thể."),
    ("C4", "LỖI", r"câu chuyện (chưa|không) dừng lại ở đó|điều bất ngờ|diễn biến (tiếp theo|kế tiếp) sẽ|điều đáng nói là|đáng chú ý hơn|thú vị hơn nữa|điều đáng chú ý là|đáng chú ý là|bạn sẽ không tin|và rồi,? (điều|chuyện)",
     "cầu nối kiểu trailer, không mang thông tin. Đưa thẳng thông tin kế tiếp."),
    ("C5", "LỖI", r"bài học rút ra|qua đó (có thể )?thấy|cho (chúng ta|ta|người xem) thấy|có thể thấy (rằng)?|điều này cho thấy|suy cho cùng|tóm lại|nhìn chung|nói cách khác",
     "câu tổng kết/kết luận đạo lý. Kết bằng diễn biến hoặc bước tiếp theo cụ thể."),
    ("C6", "CẢNH BÁO", r"một mặt\b.{0,200}\bmặt khác|vừa\b.{0,40}\bvừa\b",
     "liệt kê cân bằng kiểu bài luận. Chọn một ý và kể."),
    ("C7", "CẢNH BÁO", r"đáng kinh ngạc|không thể tin được|gây chấn động|chấn động|thật đau lòng|gây sốc|khó tin|choáng váng|kinh hoàng|vô cùng|cực kỳ|cực kì|đặc biệt (quan trọng|nghiêm trọng)",
     "tính từ cảm xúc thay cho bằng chứng. Thay bằng thứ nhìn thấy/đếm được (trừ khi là lời nhân vật)."),
    ("C8", "CẢNH BÁO", r"đóng vai trò|góp phần|mang (lại|đến)|tạo nên|đánh dấu|khẳng định vị thế|bước (ngoặt|tiến|đột phá)|bức tranh (toàn cảnh|chung)|toàn cảnh|toàn diện|hành trình|tầm nhìn|làn sóng|dấu mốc|không thể phủ nhận|có thể nói|hứa hẹn|thu hút sự quan tâm|dư luận|kỷ nguyên|diện mạo mới|biểu tượng của|chìa khóa (của|để)|lợi ích thiết thực",
     "từ 'nâng tầm' đặc trưng văn AI/văn báo cáo. Thay bằng sự việc cụ thể."),
    ("C9", "LỖI", r"^\s*(xin chào|chào (mừng|các bạn)|hôm nay (chúng ta|mình|chúng tôi)|các bạn (thân mến|ơi)|kính chào|hãy cùng|cùng (nhau )?tìm hiểu)|(hãy|đừng quên) (like|đăng ký|theo dõi|chia sẻ)",
     "mở đầu chào hỏi/giới thiệu kênh hoặc kêu gọi hành động. Vào thẳng sự kiện."),
]

SUPERLATIVES = re.compile(
    r"(lớn|cao|thấp|nhiều|ít|nhanh|chậm|dài|sớm|muộn|tốt|mạnh|yếu|bùng nổ|đắt|rẻ|nặng|sâu|rộng|hẹp|tệ|lạ) nhất|duy nhất|chưa từng có|kỷ lục|từ trước đến nay|lần đầu tiên"
)
CONNECTORS_START = re.compile(r"^(tuy nhiên|bên cạnh đó|ngoài ra|đồng thời|hơn nữa|hơn thế nữa|ngoài ra,|do đó|vì vậy|chính vì vậy|trước hết|cuối cùng)\b")
WRITTEN_REGISTER = re.compile(r"\b(tiến hành|thực hiện|nhằm|triển khai|diễn ra|sở hữu|nhằm mục đích|đã được|sẽ được|đang được|cho biết thêm|được cho là|việc)\b")
FUTURE_CLAIM = re.compile(r"\b(sẽ|giúp giảm|sẽ giúp|nhằm giảm|kỳ vọng|hứa hẹn)\b")
SOURCE_MARK = re.compile(r"\b(theo|dự kiến|kế hoạch|quy hoạch|đề xuất|cho biết|nói|công bố|ông|bà|cáo trạng|chủ đầu tư|ước tính|dự báo)\b")
ABSTRACT_CLOSER = re.compile(r"^(đó (mới )?là|đây (mới |chính )?là|và đó chính là|chính là)\b")
QUOTE_SPAN = re.compile(r"“[^”]*”|\"[^\"]*\"|«[^»]*»")
HEADING_NUM = re.compile(r"^\s*\d+\.\s+")
DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b")
NUM_RE = re.compile(r"\d[\d.,]*\d|\d")


# Luật CEO 12/11/2026: câu MỞ ĐẦU được là câu hỏi dẫn dắt/đặt vấn đề của chính câu chuyện.
# Các từ hỏi này chỉ được miễn ở câu đầu tiên của bài; công thức "câu hỏi đặt ra là…", "bạn có biết…" vẫn cấm ở mọi nơi.
OPENER_Q_OK = re.compile(r"điều gì (đã )?khiến|phải chăng|(?:^|[,.!?]\s*)liệu\b")
# K3: câu mở đầu tuyệt đối không dẫn số liệu hoặc ngày tháng.
OPENER_NUM = re.compile(
    r"\d|%|phần trăm"
    r"|\b(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mươi|vài|mấy|hàng)\s+(trăm|nghìn|ngàn|triệu|tỷ|tỉ|chục)\b"
    r"|\b(ngày|tháng|quý)\s+(mùng|mồng|giêng|chạp)\b")
# K4 (cảnh báo): số bằng chữ đi với đơn vị thời gian/đếm cụ thể, vẫn là số liệu trá hình.
OPENER_NUM_SOFT = re.compile(r"\b(hai|ba|bốn|sáu|bảy|tám|chín|mười)\s+(ngày|tuần|tháng|giờ|phút|giây|người|tuổi|lần|năm|chiếc|căn|xe)\b")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def is_heading(line: str) -> bool:
    """Tiêu đề luận điểm: IN HOA toàn bộ (có thể có số thứ tự đầu dòng), ngắn."""
    core = HEADING_NUM.sub("", line.strip())
    letters = [c for c in core if c.isalpha()]
    if len(letters) < 3:
        return False
    return core == core.upper() and len(core.split()) <= 16


_ABBR = {"tp.", "ts.", "ths.", "pgs.", "gs.", "bs.", "đh.", "q.", "p.", "tt.", "ông.", "st."}


def split_sentences(par: str) -> list[str]:
    parts = re.split(r"(?<=[.!?…])\s+(?=[A-ZÀ-ỸĐ“\"«0-9])", par.strip())
    out: list[str] = []
    for p in parts:
        if out:
            last = out[-1].split()[-1].lower() if out[-1].split() else ""
            if last in _ABBR or re.fullmatch(r"[A-ZĐ]\.", out[-1].split()[-1] if out[-1].split() else ""):
                out[-1] = out[-1] + " " + p
                continue
        out.append(p)
    return [s for s in out if s.strip()]


def norm_number(tok: str) -> str:
    tok = tok.strip(".,")
    # 4.000 / 1.250.000 -> 4000 / 1250000 (dấu chấm ngăn nghìn)
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", tok):
        tok = tok.replace(".", "")
    return tok


def numbers_in(text: str) -> set[str]:
    nums = set(DATE_RE.findall(text))
    stripped = DATE_RE.sub(" ", text)
    for m in NUM_RE.findall(stripped):
        n = norm_number(m)
        if n:
            nums.add(n)
    return nums


class Finding:
    def __init__(self, level: str, code: str, line: int, msg: str, snippet: str = ""):
        self.level, self.code, self.line, self.msg, self.snippet = level, code, line, msg, snippet

    def as_dict(self):
        return {"level": self.level, "code": self.code, "line": self.line, "msg": self.msg, "snippet": self.snippet}


def lint(text: str, facts: str | None = None) -> tuple[list[Finding], dict]:
    text = nfc(text)
    findings: list[Finding] = []
    lines = text.split("\n")

    # -------- dựng danh sách câu, gắn số dòng; bỏ tiêu đề khỏi thống kê câu
    sentences: list[tuple[int, str, bool]] = []  # (số dòng, câu, đầu đoạn?)
    headings: list[tuple[int, str]] = []
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s:
            continue
        if is_heading(s):
            headings.append((i, s))
            continue
        for j, sent in enumerate(split_sentences(s)):
            sentences.append((i, sent, j == 0))

    def tieng(s: str) -> int:
        return len(s.split())

    for i, h in headings:
        if re.search(r"#\s*\d|luận điểm (một|hai|ba|bốn|\d)", h.lower()):
            findings.append(Finding("LỖI", "H1", i, "tiêu đề luận điểm dạng '#1' / 'luận điểm 2' bị cấm (luật 30/10). Dùng '1. TIÊU ĐỀ.' hoặc IN HOA.", h))
        if len(h.split()) > 10:
            findings.append(Finding("CẢNH BÁO", "H2", i, "tiêu đề luận điểm dài hơn 10 tiếng; nên là một mệnh đề cụ thể ngắn.", h))

    # -------- mẫu cấm (bỏ phần trong ngoặc kép: lời nhân vật được miễn)
    for idx, (i, sent, _first) in enumerate(sentences):
        low = QUOTE_SPAN.sub(" ", sent.lower())
        low_ban = OPENER_Q_OK.sub(" ", low) if idx == 0 else low  # luật 12/11/2026: câu mở đầu được là câu hỏi riêng của câu chuyện
        for code, level, pat, msg in BAN_RULES:
            m = re.search(pat, low_ban if code == "C1" else low)
            if m:
                findings.append(Finding(level, code, i, msg, sent[:90]))
        if SUPERLATIVES.search(low):
            findings.append(Finding("CẢNH BÁO", "S1", i, "khẳng định tuyệt đối/xếp hạng: chỉ giữ khi dữ kiện có bảng xếp hạng hoặc chuỗi số chứng minh (skill, bước 4).", sent[:90]))
        if CONNECTORS_START.search(low):
            findings.append(Finding("CẢNH BÁO", "N1", i, "từ nối văn viết đầu câu. Thường cắt được; nếu cần thì dùng 'Nhưng', 'Còn', 'Nên'.", sent[:90]))
        if FUTURE_CLAIM.search(low) and not SOURCE_MARK.search(low):
            findings.append(Finding("CẢNH BÁO", "N2", i, "khẳng định về tương lai/lợi ích chưa ghi nguồn ngay trong câu (luật 31/10: 'theo chủ đầu tư', 'dự kiến').", sent[:90]))
        if _first and ABSTRACT_CLOSER.search(low) and tieng(sent) <= 9:
            findings.append(Finding("CẢNH BÁO", "N3", i, "câu chốt cách ngôn kiểu 'Đó là… / Đây chính là…'. Thay bằng chi tiết cụ thể.", sent[:90]))

    # -------- câu hỏi: tối đa 1 trong cả bài (ngoài lời trích); câu cuối không được là câu hỏi
    q_lines = [(i, s) for i, s, _ in sentences if "?" in QUOTE_SPAN.sub(" ", s)]
    if len(q_lines) > 1:
        for i, s in q_lines[1:]:
            findings.append(Finding("LỖI", "Q1", i, f"có {len(q_lines)} câu hỏi; luật chỉ cho tối đa 1 câu hỏi thật trong cả bài.", s[:90]))
    if sentences and "?" in sentences[-1][1]:
        findings.append(Finding("LỖI", "Q2", sentences[-1][0], "kịch bản kết bằng câu hỏi. Luật 31/10 cấm câu hỏi mở cho khán giả ở cuối.", sentences[-1][1][:90]))

    # -------- thống kê nhịp câu
    lens = [tieng(s) for _, s, _ in sentences]
    stats: dict = {"sentences": len(lens), "tieng": sum(lens), "est_seconds_info_only": round(sum(lens) / TIENG_PER_SEC, 1)}
    if len(lens) >= 8:
        mean = statistics.mean(lens)
        sd = statistics.pstdev(lens)
        cv = sd / mean if mean else 0
        short_ratio = sum(1 for n in lens if n <= 7) / len(lens)
        long_ratio = sum(1 for n in lens if n >= 25) / len(lens)
        stats.update({"mean_tieng": round(mean, 1), "cv": round(cv, 2), "short_ratio": round(short_ratio, 2), "long_ratio": round(long_ratio, 2)})
        if cv < 0.45:
            findings.append(Finding("CẢNH BÁO", "R1", 0, f"nhịp câu đều (độ lệch/trung bình = {cv:.2f}, người kể thật thường ≥ 0.45). Xen câu rất ngắn (2-7 tiếng) với câu 14-24 tiếng."))
        if short_ratio < 0.12:
            findings.append(Finding("CẢNH BÁO", "R2", 0, f"chỉ {short_ratio:.0%} câu ≤ 7 tiếng; cần câu ngắn để nhấn (mục tiêu ≥ 12%)."))
        if mean > 20:
            findings.append(Finding("CẢNH BÁO", "R3", 0, f"câu trung bình {mean:.1f} tiếng, quá dài cho tai nghe (mục tiêu 10-17)."))
    run = 1
    for k in range(1, len(lens)):
        if abs(lens[k] - lens[k - 1]) <= 3 and lens[k] >= 10:
            run += 1
            if run == 3:
                findings.append(Finding("CẢNH BÁO", "R4", sentences[k][0], "3 câu liền nhau dài gần bằng nhau: nhịp đều như máy.", sentences[k][1][:70]))
        else:
            run = 1
    for (i, s, _), n in zip(sentences, lens):
        if n > 40:
            findings.append(Finding("LỖI", "R5", i, f"câu {n} tiếng, TTS hết hơi và người nghe mất ý. Tách làm 2-3 câu.", s[:90]))
        elif n > 30:
            findings.append(Finding("CẢNH BÁO", "R6", i, f"câu {n} tiếng; nên ≤ 28.", s[:90]))

    # -------- lặp cấu trúc đầu câu
    openers = [" ".join(s.lower().split()[:2]) for _, s, _ in sentences]
    for k in range(2, len(openers)):
        if openers[k] == openers[k - 1] == openers[k - 2]:
            findings.append(Finding("CẢNH BÁO", "R7", sentences[k][0], f"3 câu liền mở bằng '{openers[k]}'. Đổi chủ ngữ hoặc gộp câu.", sentences[k][1][:70]))
    n_theo = sum(1 for _, s, _ in sentences if s.lower().startswith("theo "))
    if sentences and n_theo / len(sentences) > 0.2:
        findings.append(Finding("CẢNH BÁO", "R8", 0, f"{n_theo}/{len(sentences)} câu mở bằng 'Theo…'. Nêu nguồn một lần rồi xen 'ông nói', 'cáo trạng ghi' (luật trích nguồn)."))

    # -------- mật độ văn viết
    allow = text.lower()
    words = max(1, sum(lens))
    reg = len(WRITTEN_REGISTER.findall(allow)) / words * 100
    stats["written_register_per100"] = round(reg, 1)
    if reg > 2.0:
        findings.append(Finding("CẢNH BÁO", "W1", 0, f"{reg:.1f} từ văn viết/100 tiếng (tiến hành, thực hiện, nhằm, việc, đã được…). Viết lại bằng động từ chủ động, khẩu ngữ."))

    # -------- hook: câu đầu tiên
    if sentences:
        first = sentences[0][1]
        n_first = tieng(first)
        if n_first > 22:
            findings.append(Finding("CẢNH BÁO", "K1", sentences[0][0], f"câu mở đầu dài {n_first} tiếng; hook nên ≤ 18 tiếng.", first[:90]))
        m3 = OPENER_NUM.search(first.lower())
        if m3:
            findings.append(Finding("LỖI", "K3", sentences[0][0], f"câu mở đầu có số liệu/ngày tháng ('{m3.group(0).strip()}'). Luật 12/11/2026: câu đầu tuyệt đối không dẫn số liệu hay ngày tháng; dời xuống câu thứ 2.", first[:90]))
        elif OPENER_NUM_SOFT.search(first.lower()):
            findings.append(Finding("CẢNH BÁO", "K4", sentences[0][0], "câu mở đầu có số bằng chữ đi với đơn vị (vd 'ba ngày', 'hai người'): vẫn là số liệu trá hình. Cân nhắc bỏ hoặc dời xuống câu thứ 2.", first[:90]))

    # -------- lặp cụm dài (dấu hiệu bơm chữ)
    toks = re.findall(r"\w+", allow)
    grams: dict[str, int] = {}
    for k in range(len(toks) - 4):
        g = " ".join(toks[k:k + 5])
        grams[g] = grams.get(g, 0) + 1
    for g, c in grams.items():
        if c >= 3:
            findings.append(Finding("CẢNH BÁO", "D1", 0, f"cụm '{g}' lặp {c} lần: dấu hiệu độn chữ hoặc lặp ý.", g))

    # -------- đối chiếu số với dữ kiện đã kiểm chứng
    if facts is not None:
        fnums = numbers_in(nfc(facts))
        seen_v1: set[str] = set()
        for i, raw in enumerate(lines, 1):
            s = raw.strip()
            if not s:
                continue
            if is_heading(s):
                s = HEADING_NUM.sub("", s)
            for n in sorted(numbers_in(s)):
                if n in fnums or n in seen_v1:
                    continue
                seen_v1.add(n)
                big = ("/" in n) or ("," in n) or (n.isdigit() and int(n) > 31)
                findings.append(Finding(
                    "LỖI" if big else "CẢNH BÁO", "V1", i,
                    f"số/ngày '{n}' không có trong dữ kiện đã kiểm chứng. " + ("Không được bịa số liệu." if big else "Nếu là phép tính suy ra từ dữ kiện (vd 14-10=4) thì ghi chú phép tính; nếu không thì bỏ."),
                    s[:90]))

    findings.sort(key=lambda f: (f.line, f.code))
    return findings, stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra cơ học kịch bản trước khi chạy TTS.")
    ap.add_argument("script", help="file kịch bản (.txt/.md), lời đọc thuần")
    ap.add_argument("--facts", help="file dữ kiện đã kiểm chứng; bật đối chiếu số/ngày")
    ap.add_argument("--strict", action="store_true", help="coi CẢNH BÁO như LỖI")
    ap.add_argument("--json", action="store_true", help="in kết quả dạng JSON")
    a = ap.parse_args(argv)
    try:
        text = open(a.script, encoding="utf-8").read()
        facts = open(a.facts, encoding="utf-8").read() if a.facts else None
    except OSError as e:
        print(f"Không đọc được file: {e}", file=sys.stderr)
        return 2
    findings, stats = lint(text, facts)
    errors = [f for f in findings if f.level == "LỖI"]
    warns = [f for f in findings if f.level == "CẢNH BÁO"]
    if a.json:
        print(json.dumps({"stats": stats, "errors": [f.as_dict() for f in errors], "warnings": [f.as_dict() for f in warns]}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            where = f"dòng {f.line}" if f.line else "toàn bài"
            snip = f"\n      > {f.snippet}" if f.snippet else ""
            print(f"[{f.level}] {f.code} · {where}: {f.msg}{snip}")
        print("-" * 60)
        print(f"{len(errors)} LỖI, {len(warns)} CẢNH BÁO · {stats['sentences']} câu, {stats['tieng']} tiếng "
              f"(ước tính ~{stats['est_seconds_info_only']}s, chỉ để tham khảo)")
        if "cv" in stats:
            print(f"nhịp: trung bình {stats['mean_tieng']} tiếng/câu, độ lệch/TB {stats['cv']}, câu ngắn {stats['short_ratio']:.0%}, câu dài {stats['long_ratio']:.0%}")
        print("KẾT QUẢ:", "CHẶN, sửa lỗi rồi chạy lại trước khi TTS" if (errors or (a.strict and warns)) else "ĐẠT cửa cơ học (vẫn phải rà tai và đối chiếu nguồn)")
    return 1 if (errors or (a.strict and warns)) else 0


if __name__ == "__main__":
    sys.exit(main())
