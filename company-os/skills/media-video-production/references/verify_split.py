#!/usr/bin/env python3
"""Chứng minh việc tách SKILL.md KHÔNG mất chữ nào.

    python3 verify_split.py <SKILL.md-cũ-trước-khi-tách> [thư-mục-references]

Dựng lại tệp cũ = dòng tiêu đề đầu + (các khối trong references/*.md sắp theo số dòng nguồn) +
khối 'Available connectors' lấy từ lõi SKILL.md mới, rồi so BYTE-với-BYTE với tệp cũ.
"""
import re, sys
from pathlib import Path

old = Path(sys.argv[1]).read_text(encoding="utf-8")
refs = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent
core = (refs.parent / "SKILL.md").read_text(encoding="utf-8")
lines = old.split("\n")
blocks = {}
for f in sorted(refs.glob("*.md")):
    cur = None
    for ln in f.read_text(encoding="utf-8").split("\n"):
        m = re.fullmatch(r"<!-- nguồn: SKILL\.md cũ dòng (\d+)-(\d+) -->", ln)
        if m:
            cur = int(m.group(1)); blocks[cur] = (int(m.group(2)), [])
        elif cur is not None:
            blocks[cur][1].append(ln)
# khối connectors nằm nguyên văn trong lõi, sau dấu mốc
m = re.search(r"<!-- nguồn: SKILL\.md cũ dòng (\d+)-(\d+) \(giữ trong lõi\) -->\n(.*)\Z", core, re.S)
assert m, "lõi thiếu khối Available connectors có dấu mốc"
blocks[int(m.group(1))] = (int(m.group(2)), m.group(3).split("\n"))
out = [lines[0]]
pos = 2
for start in sorted(blocks):
    assert start == pos, f"hổng/chồng lấn: khối tiếp theo bắt đầu {start}, mong đợi {pos}"
    end, body = blocks[start]
    assert len(body) == end - start + 1, f"khối {start}-{end} có {len(body)} dòng, mong {end-start+1}"
    out.extend(body); pos = end + 1
assert pos == len(lines) + 1, f"thiếu phần cuối: dừng ở {pos}, tệp cũ có {len(lines)} dòng"
rebuilt = "\n".join(out)
print("dựng lại:", len(rebuilt.encode()), "byte | tệp cũ:", len(old.encode()), "byte")
if rebuilt == old:
    print("KẾT QUẢ: GIỐNG HỆT TỪNG BYTE — không mất chữ nào."); sys.exit(0)
print("KẾT QUẢ: KHÁC — kiểm tra lại"); sys.exit(1)
