#!/usr/bin/env python3
"""Trích các khẳng định cần kiểm chứng từ kịch bản (số liệu, ngày tháng, tên riêng).

Agent dùng output này để đối chiếu với nguồn tin trước khi chạy TTS.

    python3 extract_claims.py <project_id> [--json]

In ra text; --json cho JSON.
"""
import json
import re
import sys
from pathlib import Path

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)


MONTHS = ("tháng 1|tháng 2|tháng 3|tháng 4|tháng 5|tháng 6|tháng 7|tháng 8|"
          "tháng 9|tháng 10|tháng 11|tháng 12")


def extract(text: str) -> dict:
    claims = {"numbers": [], "dates": [], "names": []}
    # số liệu: phần trăm, số + đơn vị
    for m in re.finditer(r"\d[\d.,]*\s*%", text):
        claims["numbers"].append(m.group(0))
    for m in re.finditer(
            r"\d[\d.,]*\s*(?:phần trăm|tỷ|triệu|nghìn|năm|tháng|ngày|giờ|phút|"
            r"km|người|máy bay|tên lửa|UAV|drone|quân|xe tăng|tàu)", text):
        claims["numbers"].append(m.group(0))
    # ngày tháng / năm
    for m in re.finditer(rf"(?:ngày\s+\d{{1,2}}\s+)?(?:{MONTHS})(?:\s+năm\s+\d{{4}})?"
                         r"|\b(?:năm\s+)?(19|20)\d{2}\b", text):
        claims["dates"].append(m.group(0).strip())
    # tên riêng viết hoa (2+ từ) — loại từ thường hay đứng đầu câu
    STOP = {"khi", "được", "đánh", "đổi", "đây", "đã", "đều", "đổ", "đắt", "đỏ",
            "với", "đó", "khi", "nhận", "định", "với", "ông", "bà", "anh", "chị",
            "của", "họ", "đó", "là", "vùng", "đất", "lịch", "sử", "của", "trong",
            "ngoài", "trên", "dưới", "trước", "sau", "nếu", "thì", "mà", "và",
            "hoặc", "nhưng", "vì", "do", "từ", "đến", "về", "theo", "giữa"}
    for m in re.finditer(r"\b[A-ZÀ-Ỹ][a-zà-ỹ]+(?:\s+[A-ZÀ-Ỹ][a-zà-ỹ]+){1,3}\b", text):
        words = m.group(0).split()
        # giữ lại nếu có ít nhất 1 từ KHÔNG thuộc stop-list (tên thật)
        if any(w.lower() not in STOP for w in words):
            claims["names"].append(m.group(0))
    # khử trùng, giữ thứ tự
    for k in claims:
        seen, out = set(), []
        for v in claims[k]:
            if v not in seen:
                seen.add(v)
                out.append(v)
        claims[k] = out
    return claims


def main() -> int:
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    full = "\n".join(p["voiceText"] for sc in plan["scenes"] for p in sc["parts"])
    claims = extract(full)
    if "--json" in sys.argv:
        print(json.dumps(claims, ensure_ascii=False, indent=1))
    else:
        print(f"=== KHẲNG ĐỊNH CẦN KIỂM CHỨNG ({pid}) ===")
        for label, key in (("Số liệu", "numbers"), ("Ngày tháng", "dates"),
                           ("Tên riêng (ứng viên)", "names")):
            print(f"\n[{label}] ({len(claims[key])})")
            for v in claims[key]:
                print(f"  - {v}")
        print("\nAgent đối chiếu từng mục với nguồn tin trước khi chạy TTS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
