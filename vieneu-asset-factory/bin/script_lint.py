#!/usr/bin/env python3
"""script_lint.py — kiểm tra cơ học kịch bản TRƯỚC KHI chạy TTS.

Mục đích: biến bước "đọc to rồi sửa" trong skill media-video-production thành
một cửa kiểm tra chạy được. Công cụ này KHÔNG chấm hay/dở. Nó chỉ bắt:
  - mẫu câu cấm theo luật CEO 29/10, 30/10, 31/10 (đối chiếu SCRIPT_DOCTRINE.md);
  - xưng hô sai luật (§1: cấm "tôi"/"các bạn"/"quý vị", "mình" tối đa 3, "bạn" tối đa 2);
  - thiếu đoạn preview sau hook (§3.2, chỉ kiểm có/không có đoạn) và câu chốt cuối > 12 tiếng (§3.6);
  - dấu hiệu "văn viết, không phải văn nói" (nhịp đều, câu quá dài, từ hành chính);
  - số liệu trong kịch bản không có trong dữ kiện đã kiểm chứng (--facts).

KHÔNG kiểm (cần tai người / QA): chất lượng lời hứa trong preview (có phải lời hứa thật
hay chỉ là mục lục), nhịp treo/trả vòng mở §3.3 (chỉ bắt cụm trailer rỗng qua C4),
xưng hô trong lời trích nguyên văn (được miễn, như dạng mở đầu 8).
Ngưỡng tự thêm đã gỡ theo I13 (13/11/2026): R1 (cv < 0,45), R3 (câu trung bình > 20),
W1 (từ văn viết > 2,0/100 tiếng), N1 "trước hết/cuối cùng" — các con số này không có
trong doctrine nên lint không cảnh báo theo chúng nữa. W1 đã quay lại dạng mới theo
Phụ lục B (cảnh báo từng từ + gợi ý từ thay, xem nhóm 1 bên dưới).

NGUYÊN TẮC: mọi kiểm tra bám một mục của `skills/SCRIPT_DOCTRINE.md` (số mục ghi
trong thông báo; §4 của doctrine này đánh số 1–13, không phải 4.1–4.13). Mục nào
doctrine viết "Cấm" -> LỖI; mục viết "tối đa", "≤", "nên" -> CẢNH BÁO. Kiểm tra theo
heuristic thì thông báo nói rõ. LINT KHÔNG PHẢI XÁC NHẬN "KỊCH BẢN ĐẠT DOCTRINE" —
nó chỉ bắt được cái đo được bằng chuỗi/đếm; danh sách việc nó KHÔNG kiểm (xem
NOT_CHECKED) luôn được in ở cuối kết quả.
Nhóm 1 học từ bản tham khảo script_lint v0.02ii (chi nhánh khác, 13/11/2026; CEO duyệt
áp ngay 12:38): sửa N3 về cuối đoạn, N1 chỉ đầu đoạn, H2 (is_heading ≤ 30 từ),
H3/H4, T1, đếm xưng hô loại trừ, miễn lời trích sau "nói:", in NOT_CHECKED.

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

# Việc lint KHÔNG kiểm được: người viết/QA phải tự rà. In kèm mọi kết quả để "không lỗi" không bị hiểu là "đạt".
NOT_CHECKED = [
    "câu mở đầu có thuộc 1 trong 13 dạng và có phải của RIÊNG câu chuyện không (§3.1); điều câu đầu hứa có được trả trong bài không",
    "preview có là lời hứa có mẩu tò mò thật không (§3.2) — lint chỉ kiểm có đoạn preview (P1) và cấm cụm loan báo trong đoạn preview (P2)",
    "vòng mở: có treo/trả đều khoảng 20-25 giây, treo rồi có trả không (§3.3); móc lại quanh 50% có thật không (§3.5)",
    "tiêu đề luận điểm có là mệnh đề cụ thể (số hoặc động từ) không (§3.4) — lint chỉ bắt nhãn chủ đề quen (H3) và tiêu đề quá dài (H2)",
    "kết có soi lại vấn đề mở đầu bằng diễn biến cụ thể không; câu chốt có phải chi tiết cụ thể, không phải khẩu hiệu (§3.6)",
    "cấm theo CHỨC NĂNG (§5): biến thể mới không có trong danh sách regex vẫn lọt; bộ ba trừu tượng; dữ kiện nào đáng bỏ",
    "số có đúng NGHĨA không (V1 chỉ so chuỗi số với file dữ kiện); trích nguồn có đúng; chọn/cắt dữ kiện (§2)",
    "ba bài kiểm tra rà tai (§8): thay chủ đề, xoá thử, che số",
]

# ---------------------------------------------------------------- mẫu cấm
# Mỗi mục: (mã, mức, regex trên văn bản đã hạ chữ thường, thông điệp)
# Mức: "LỖI" chặn TTS; "CẢNH BÁO" cần người/AI cân nhắc.
# Cấm theo LỚP chức năng, không chỉ theo cụm: gặp biến thể cùng chức năng vẫn phải sửa.
BAN_RULES = [
    ("C1", "LỖI", r"câu hỏi (đặt ra|đầu tiên|lớn|quan trọng|then chốt) là|vậy (thì )?điều gì|điều gì (đã )?khiến|phải chăng|(?:^|[,.!?]\s*)liệu\b|bạn có (từng )?biết|bạn có tò mò",
     "câu hỏi tu từ rỗng làm hook/cầu nối. Thay bằng sự kiện hoặc con số cụ thể."),
    ("C2", "LỖI", r"không chỉ\b.{0,80}\bmà còn|không (phải|đơn thuần|chỉ đơn thuần)\b.{0,60}\bmà (là|còn)|chẳng những",
     "cấu trúc đối lập sáo 'không chỉ… mà còn / không phải… mà là'. Nói thẳng điều đúng."),
    ("C3", "LỖI", r"(^|[.!?]\s+)(trong thời đại|khi nhắc đến|từ trước đến nay|từ xưa đến nay|xưa nay)\b",
     "mở đầu khái quát. Mở bằng cảnh/sự kiện cụ thể."),
    ("C4", "LỖI", r"câu chuyện (chưa|không) dừng lại ở đó|điều bất ngờ|diễn biến (tiếp theo|kế tiếp) sẽ|điều đáng nói là|đáng chú ý hơn|thú vị hơn nữa|điều đáng chú ý là|đáng chú ý là|bạn sẽ không tin|và rồi,? (điều|chuyện)",
     "cầu nối kiểu trailer, không mang thông tin. Đưa thẳng thông tin kế tiếp."),
    ("C5", "LỖI", r"bài học rút ra|qua đó (có thể )?thấy|cho (chúng ta|ta|người xem) thấy|có thể thấy (rằng)?|điều này cho thấy|suy cho cùng|tóm lại|nhìn chung|nói cách khác",
     "câu tổng kết/kết luận đạo lý. Kết bằng diễn biến hoặc bước tiếp theo cụ thể."),
    ("C6", "CẢNH BÁO", r"một mặt\b.{0,200}\bmặt khác|vừa\b.{0,40}\bvừa\b",
     "liệt kê cân bằng kiểu bài luận. Chọn một ý và kể."),
    # C7: "gây sốc" đứng sau "tuyên bố " là nhãn dạng mở đầu 1 của doctrine ("Tuyên bố gây sốc") nên được miễn (I13).
    ("C7", "CẢNH BÁO", r"đáng kinh ngạc|không thể tin được|gây chấn động|chấn động|thật đau lòng|(?<!tuyên bố )gây sốc|khó tin|choáng váng|kinh hoàng|vô cùng|cực kỳ|cực kì|đặc biệt (quan trọng|nghiêm trọng)",
     "tính từ cảm xúc thay cho bằng chứng. Thay bằng thứ nhìn thấy/đếm được (trừ khi là lời nhân vật)."),
    ("C8", "CẢNH BÁO", r"đóng vai trò|góp phần|mang (lại|đến)|tạo nên|đánh dấu|khẳng định vị thế|bước (ngoặt|tiến|đột phá)|bức tranh (toàn cảnh|chung)|toàn cảnh|toàn diện|tầm nhìn|làn sóng|dấu mốc|không thể phủ nhận|có thể nói|hứa hẹn|thu hút sự quan tâm|dư luận|kỷ nguyên|diện mạo mới|biểu tượng của|chìa khóa (của|để)|lợi ích thiết thực",
     "từ 'nâng tầm' đặc trưng văn AI/văn báo cáo. Thay bằng sự việc cụ thể."),
    ("C9", "LỖI", r"^\s*(xin chào|chào (mừng|các bạn)|hôm nay (chúng ta|mình|chúng tôi)|các bạn (thân mến|ơi)|kính chào|hãy cùng|cùng (nhau )?tìm hiểu)|(hãy|đừng quên) (like|đăng ký|theo dõi|chia sẻ)",
     "mở đầu chào hỏi/giới thiệu kênh hoặc kêu gọi hành động. Vào thẳng sự kiện."),
    ("T1", "LỖI", r"\b(nhé|nhỉ|nha|nhá|đấy)\W*$",
     "§1: tiểu từ khẩu ngữ (nhé, nhỉ, đấy, nha) cuối câu bị cấm, trừ khi brief kênh khai báo khác."),
]

SUPERLATIVES = re.compile(
    r"(lớn|cao|thấp|nhiều|ít|nhanh|chậm|dài|sớm|muộn|tốt|mạnh|yếu|bùng nổ|đắt|rẻ|nặng|sâu|rộng|hẹp|tệ|lạ) nhất|duy nhất|chưa từng có|kỷ lục|từ trước đến nay|lần đầu tiên"
)
CONNECTORS_START = re.compile(r"^(tuy nhiên|bên cạnh đó|ngoài ra|đồng thời|hơn nữa)\b")  # §4 mục 10: cấm ĐẦU ĐOẠN
# Phụ lục B (văn viết -> văn nói): chỉ cảnh báo, gom theo từ, kèm từ thay
WRITTEN_TERMS = {
    "tiến hành": "làm", "thực hiện": "làm", "nhằm mục đích": "để", "nhằm": "để", "sở hữu": "có",
    "diễn ra": "xảy ra/có", "hiện nay": "giờ", "hiện tại": "giờ", "do đó": "nên", "vì vậy": "nên",
}
FUTURE_CLAIM = re.compile(r"\b(sẽ|giúp giảm|sẽ giúp|nhằm giảm|kỳ vọng|hứa hẹn)\b")
SOURCE_MARK = re.compile(r"\b(theo|dự kiến|kế hoạch|quy hoạch|đề xuất|cho biết|nói|công bố|ông|bà|cáo trạng|chủ đầu tư|ước tính|dự báo)\b")
ABSTRACT_CLOSER = re.compile(r"^(đó (mới )?là|đây (mới |chính )?là|và đó chính là|chính là)\b")
QUOTE_SPAN = re.compile(r"“[^”]*”|\"[^\"]*\"|«[^»]*»")
SPEECH_TAIL = re.compile(r"\b(nói|kể|hỏi|viết|đáp|khai|thốt lên|cho biết|trả lời)\s*:\s*.*$")
NUMWORD = r"(?:một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười)"
HEADING_BAD_NUM = re.compile(r"#\s*(\d|" + NUMWORD + r"\b)|luận điểm (\d|" + NUMWORD + r"\b)")
LABEL_HEADINGS = {"TỔNG QUAN", "TÁC ĐỘNG", "KẾT LUẬN"}  # §3.4 ví dụ cấm
LABEL_LIKE = {"BỐI CẢNH", "GIỚI THIỆU", "NGUYÊN NHÂN", "HẬU QUẢ", "DIỄN BIẾN", "NHẬN ĐỊNH", "ĐÁNH GIÁ", "MỞ ĐẦU"}
MINH = re.compile(r"(?<!một )(?<!tự )(?<!riêng )\bmình\b")
BAN_RE = re.compile(r"(?<!các )\bbạn\b(?!\s+bè)")
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
    r"|\b(ngày|tháng|quý)\s+(mùng|mồng|giêng|chạp)\b"
    r"|\b(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mười một|mười hai)\s+tháng\s+(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mười một|mười hai)\b"
    r"|\btháng\s+(một|hai|ba|bốn|năm|sáu|bảy|tám|chín|mười|mười một|mười hai)\b")
# K4 (cảnh báo): số bằng chữ đi với đơn vị thời gian/đếm cụ thể, vẫn là số liệu trá hình.
OPENER_NUM_SOFT = re.compile(r"\b(mười một|hai mươi|một|hai|ba|bốn|sáu|bảy|tám|chín|mười)\s+(ngày|tuần|tháng|giờ|phút|giây|người|tuổi|lần|năm|chiếc|căn|xe)\b")


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)


def spoken(s: str) -> str:
    """Hạ chữ thường và bỏ lời trích (ngoặc kép, hoặc phần sau 'nói:', 'kể:'…): lời nhân vật được miễn."""
    return QUOTE_SPAN.sub(" ", SPEECH_TAIL.sub(" ", s.lower()))


def is_heading(line: str) -> bool:
    """Tiêu đề luận điểm: IN HOA toàn bộ (có thể có số thứ tự đầu dòng)."""
    core = HEADING_NUM.sub("", line.strip())
    letters = [c for c in core if c.isalpha()]
    if len(letters) < 3:
        return False
    return core == core.upper() and len(core.split()) <= 30


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

    # -------- tiêu đề luận điểm (§3.4, luật 30/10)
    for i, h in headings:
        core = HEADING_NUM.sub("", h.strip())
        bare = core.rstrip(". ").strip()
        if HEADING_BAD_NUM.search(h.lower()):
            findings.append(Finding("LỖI", "H1", i, "§3.4/luật 30/10: tiêu đề luận điểm dạng '#1' / 'luận điểm 2' / 'luận điểm năm' bị cấm. Dùng '1. TIÊU ĐỀ.' hoặc IN HOA.", h))
        if tieng(bare) > 8:
            findings.append(Finding("CẢNH BÁO", "H2", i, f"§3.4: tiêu đề {tieng(bare)} tiếng; doctrine yêu cầu ≤ 8 tiếng.", h))
        if bare in LABEL_HEADINGS or any(bare.startswith(lbl + " ") for lbl in LABEL_HEADINGS):
            findings.append(Finding("LỖI", "H3", i, "§3.4: tiêu đề là nhãn chủ đề (TỔNG QUAN/TÁC ĐỘNG/KẾT LUẬN) bị cấm; phải là mệnh đề cụ thể có số hoặc động từ.", h))
        elif bare in LABEL_LIKE or (tieng(bare) <= 2 and not re.search(r"\d", bare)):
            findings.append(Finding("CẢNH BÁO", "H3", i, "§3.4 (heuristic): tiêu đề ngắn, không số — có vẻ là nhãn chủ đề; cần mệnh đề cụ thể có số hoặc động từ.", h))
        if not h.rstrip().endswith("."):
            findings.append(Finding("CẢNH BÁO", "H4", i, "§3.4: tiêu đề là dòng riêng '1. IN HOA.' hoặc IN HOA kết thúc bằng dấu chấm.", h))

    # câu cuối đoạn (đoạn = một dòng)
    last_in_par = [k + 1 >= len(sentences) or sentences[k + 1][0] != sentences[k][0] for k in range(len(sentences))]

    # -------- mẫu cấm (bỏ lời trích: lời nhân vật được miễn)
    for idx, (i, sent, first_in_par) in enumerate(sentences):
        low = spoken(sent)
        low_c1 = OPENER_Q_OK.sub(" ", low) if idx == 0 else low  # luật 12/11/2026: câu mở đầu được là câu hỏi riêng của câu chuyện
        for code, level, pat, msg in BAN_RULES:
            if re.search(pat, low_c1 if code == "C1" else low):
                findings.append(Finding(level, code, i, msg, sent[:90]))
        # C6 (13/11/2026, DEC-273): dạng hai câu "Một mặt… / Mặt khác…" —
        # regex trong BAN_RULES chỉ bắt khi hai vế cùng một câu, nên kiểm
        # thêm câu kế tiếp: câu này có "một mặt" mà câu sau mở bằng
        # "mặt khác" thì báo ở câu sau. Chỉ CẢNH BÁO — hai phía của một
        # tranh cãi thật khác với liệt kê cân bằng kiểu bài luận, QA phán xét.
        if idx + 1 < len(sentences) and re.search(r"\bmột mặt\b", low):
            _nx_i, _nx_s, _ = sentences[idx + 1]
            if re.match(r"\s*mặt khác\b", spoken(_nx_s)):
                findings.append(Finding("CẢNH BÁO", "C6", _nx_i, "liệt kê cân bằng kiểu bài luận. Chọn một ý và kể.", _nx_s[:90]))
        if SUPERLATIVES.search(low):
            findings.append(Finding("CẢNH BÁO", "S1", i, "khẳng định tuyệt đối/xếp hạng: chỉ giữ khi dữ kiện có bảng xếp hạng hoặc chuỗi số chứng minh (skill, bước 4).", sent[:90]))
        if first_in_par and CONNECTORS_START.search(low):
            findings.append(Finding("LỖI", "N1", i, "§4 mục 10: cấm đầu đoạn 'Tuy nhiên / Bên cạnh đó / Ngoài ra / Đồng thời / Hơn nữa'. Dùng 'Nhưng', 'Còn', 'Nên' hoặc bỏ.", sent[:90]))
        if FUTURE_CLAIM.search(low) and not SOURCE_MARK.search(low):
            findings.append(Finding("CẢNH BÁO", "N2", i, "§4 mục 12: khẳng định tương lai/lợi ích chưa ghi nguồn ngay trong câu ('theo chủ đầu tư', 'dự kiến').", sent[:90]))
        if last_in_par[idx] and ABSTRACT_CLOSER.search(low) and tieng(sent) <= 9:
            findings.append(Finding("CẢNH BÁO", "N3", i, "§5 N3: câu chốt cách ngôn cuối đoạn kiểu 'Đó là… / Đây chính là…'. Thay bằng chi tiết cụ thể.", sent[:90]))

    # -------- xưng hô (§1 doctrine; I13 13/11/2026) — lời trích nguyên văn được miễn
    # "tôi" / "các bạn" / "quý vị" / "hôm nay chúng ta": doctrine cấm tuyệt đối -> LỖI.
    # "mình" tối đa 3 lần, "bạn" tối đa 2 lần cả bài -> quá thì CẢNH BÁO.
    # "bạn" đếm riêng, không tính "các bạn" (đã cấm riêng ở X2) và "bạn bè";
    # "mình" không tính "một mình"/"tự mình"/"riêng mình" (nhóm 1, 13/11/2026).
    _X_BANNED = [
        (r"\btôi\b", "X1", "xưng 'tôi'. Doctrine §1: không xưng 'tôi' — kể như người đã đọc hồ sơ, không xưng danh."),
        (r"\bcác bạn\b", "X2", "xưng 'các bạn'. Doctrine §1: cấm 'các bạn' — kể cho một người bạn, không gọi đám đông."),
        (r"\bquý vị\b", "X2", "xưng 'quý vị'. Doctrine §1: cấm 'quý vị' — giọng báo cáo, không phải giọng kể."),
        (r"\bhôm nay chúng ta\b", "X2", "'hôm nay chúng ta'. Doctrine §1: cấm — mở đầu kiểu giới thiệu chương trình."),
    ]
    _plain = [(i, s) for i, s, _ in sentences]
    for i, s in _plain:
        low = spoken(s)
        for pat, code, msg in _X_BANNED:
            if re.search(pat, low):
                findings.append(Finding("LỖI", code, i, msg, s.strip()[:90]))
    _body_low = " ".join(spoken(s) for _, s in _plain)
    n_minh = len(MINH.findall(_body_low))
    if n_minh > 3:
        findings.append(Finding("CẢNH BÁO", "X3", 0, f"'mình' xuất hiện {n_minh} lần; doctrine §1 cho tối đa 3 lần cả bài, chỉ dùng ở chỗ dẫn đường ('Mình đi qua ba chuyện…')."))
    n_ban = len(BAN_RE.findall(_body_low))
    if n_ban > 2:
        findings.append(Finding("CẢNH BÁO", "X4", 0, f"'bạn' xuất hiện {n_ban} lần; doctrine §1 cho tối đa 2 lần cả bài (không tính 'các bạn' đã cấm riêng ở X2)."))

    # -------- từ văn viết (Phụ lục B; nhóm 1, 13/11/2026): gom theo từ, chỉ cảnh báo,
    # kèm từ thay. Thay cho W1 mật độ đã gỡ ở I13 (ngưỡng không có trong doctrine).
    # "nhằm" không tính lần đã đếm trong "nhằm mục đích" để khỏi đếm trùng.
    for term, spoken_form in WRITTEN_TERMS.items():
        pat = re.compile(r"\bnhằm\b(?!\s+mục đích)") if term == "nhằm" else re.compile(r"\b" + term + r"\b")
        n = len(pat.findall(_body_low))
        if n:
            first_line = next((i for i, s, _ in sentences if pat.search(spoken(s))), 0)
            findings.append(Finding("CẢNH BÁO", "W1", first_line, f"Phụ lục B: '{term}' xuất hiện {n} lần; văn nói: '{spoken_form}'."))

    # -------- câu hỏi: tối đa 1 trong cả bài (ngoài lời trích); câu cuối không được là câu hỏi
    q_lines = [(i, s) for i, s, _ in sentences if "?" in spoken(s)]
    if len(q_lines) > 1:
        for i, s in q_lines[1:]:
            findings.append(Finding("LỖI", "Q1", i, f"có {len(q_lines)} câu hỏi; luật chỉ cho tối đa 1 câu hỏi thật trong cả bài.", s[:90]))
    if sentences and "?" in sentences[-1][1]:
        findings.append(Finding("LỖI", "Q2", sentences[-1][0], "kịch bản kết bằng câu hỏi. Luật 31/10 cấm câu hỏi mở cho khán giả ở cuối.", sentences[-1][1][:90]))

    # -------- câu chốt cuối (§3.6 doctrine; I13 13/11/2026): chi tiết cụ thể cuối
    # cùng, ≤ 12 tiếng, đặt sau nhịp nghỉ. Chỉ kiểm độ dài câu cuối; nội dung
    # có phải "chi tiết cụ thể" hay không cần tai người. Câu cuối là câu hỏi thì
    # thôi (Q2 đã bắt) để khỏi gắn cờ trùng.
    if sentences:
        n_last = tieng(sentences[-1][1])
        if n_last > 12 and "?" not in sentences[-1][1]:
            findings.append(Finding("CẢNH BÁO", "F1", sentences[-1][0],
                f"câu cuối dài {n_last} tiếng; câu chốt nên ≤ 12 tiếng (doctrine §3.6) — "
                "một chi tiết cụ thể cuối cùng, đặt sau nhịp nghỉ.", sentences[-1][1][:90]))

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
        # I13 (13/11/2026): R1 (cv < 0,45) và R3 (trung bình > 20) đã gỡ — hai ngưỡng
        # này không có trong doctrine; chỉ giữ lại trong stats để tham khảo.
        if short_ratio < 0.12:
            findings.append(Finding("CẢNH BÁO", "R2", 0, f"chỉ {short_ratio:.0%} câu ≤ 7 tiếng; cần câu ngắn để nhấn (mục tiêu ≥ 12%)."))
        # I13 (13/11/2026): R3 (trung bình > 20) đã gỡ — ngưỡng không có trong doctrine.
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
        elif n > 28:
            findings.append(Finding("CẢNH BÁO", "R6", i, f"câu {n} tiếng; nên ≤ 28.", s[:90]))

    # -------- lặp cấu trúc đầu câu
    openers = [" ".join(s.lower().split()[:2]) for _, s, _ in sentences]
    for k in range(2, len(openers)):
        if openers[k] == openers[k - 1] == openers[k - 2]:
            findings.append(Finding("CẢNH BÁO", "R7", sentences[k][0], f"3 câu liền mở bằng '{openers[k]}'. Đổi chủ ngữ hoặc gộp câu.", sentences[k][1][:70]))
    n_theo = sum(1 for _, s, _ in sentences if s.lower().startswith("theo "))
    if sentences and n_theo / len(sentences) > 0.2:
        findings.append(Finding("CẢNH BÁO", "R8", 0, f"{n_theo}/{len(sentences)} câu mở bằng 'Theo…'. Nêu nguồn một lần rồi xen 'ông nói', 'cáo trạng ghi' (luật trích nguồn)."))

    # -------- mật độ văn viết: chỉ còn biến allow cho D1 dùng bên dưới.
    # Thống kê mật độ (written_register_per100) đã bỏ theo nhóm 1 — W1 giờ là
    # cảnh báo từng từ theo Phụ lục B (xem khối xưng hô ở trên).
    allow = text.lower()

    # -------- preview (§3.2 doctrine; I13 13/11/2026) — chỉ kiểm có/không có đoạn,
    # không kiểm chất lượng lời hứa (cần tai người). Đoạn preview là các câu nằm
    # giữa câu hook (câu đầu tiên) và tiêu đề luận điểm đầu tiên.
    if sentences and headings:
        first_head_line = headings[0][0]
        preview_sents = [(i, s) for i, s, _ in sentences[1:] if i < first_head_line]
        if not preview_sents:
            findings.append(Finding("CẢNH BÁO", "P1", sentences[0][0],
                "không thấy đoạn preview sau hook: hook đi thẳng vào tiêu đề luận điểm đầu tiên. "
                "Luật 31/10: sau hook phải có 1–2 câu giới thiệu sơ bộ toàn bộ câu chuyện trước khi đi sâu."))
        else:
            _PREVIEW_TOC = re.compile(r"(video|bài viết|bài|clip) này sẽ|chúng ta sẽ cùng|chúng ta sẽ đi|sau đây chúng ta")
            for i, s in preview_sents:
                if _PREVIEW_TOC.search(QUOTE_SPAN.sub(" ", s).lower()):
                    findings.append(Finding("CẢNH BÁO", "P2", i,
                        "preview viết kiểu mục lục ('video này sẽ…', 'chúng ta sẽ cùng…'). "
                        "Doctrine §3.2: preview là lời hứa dẫn đường, không phải mục lục.", s[:90]))

    # -------- hook: câu đầu tiên
    if sentences:
        first = sentences[0][1]
        n_first = tieng(first)
        if n_first > 18:
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


def verdict(errors, warns, strict: bool) -> str:
    if errors or (strict and warns):
        return "CHẶN: sửa lỗi rồi chạy lại trước khi TTS"
    if warns:
        return f"KHÔNG CÓ LỖI, còn {len(warns)} CẢNH BÁO: đọc từng cái. Đây KHÔNG phải xác nhận kịch bản đạt doctrine."
    return "KHÔNG CÓ LỖI/CẢNH BÁO cơ học. Đây KHÔNG phải xác nhận kịch bản đạt doctrine: còn các mục lint không kiểm được (bên dưới)."


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
    v = verdict(errors, warns, a.strict)
    if a.json:
        print(json.dumps({"stats": stats, "errors": [f.as_dict() for f in errors], "warnings": [f.as_dict() for f in warns],
                          "verdict": v, "not_checked": NOT_CHECKED}, ensure_ascii=False, indent=2))
    else:
        for f in findings:
            where = f"dòng {f.line}" if f.line else "toàn bài"
            snip = f"\n      > {f.snippet}" if f.snippet else ""
            print(f"[{f.level}] {f.code} · {where}: {f.msg}{snip}")
        print("-" * 60)
        print(f"{len(errors)} LỖI, {len(warns)} CẢNH BÁO · {stats['sentences']} câu, {stats['tieng']} tiếng "
              f"(ước tính ~{stats['est_seconds_info_only']}s, chỉ để tham khảo)")
        if "cv" in stats:
            print(f"nhịp (chỉ để biết, không có ngưỡng): trung bình {stats['mean_tieng']} tiếng/câu, độ lệch/TB {stats['cv']}, câu ngắn {stats['short_ratio']:.0%}, câu dài {stats['long_ratio']:.0%}")
        print("KẾT QUẢ:", v)
        print("LINT KHÔNG KIỂM (người viết/QA tự rà):")
        for n in NOT_CHECKED:
            print("  -", n)
    return 1 if (errors or (a.strict and warns)) else 0


if __name__ == "__main__":
    sys.exit(main())
