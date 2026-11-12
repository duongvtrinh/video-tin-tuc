#!/usr/bin/env python3
"""Sinh docs/TEMPLATE_CATALOG.md từ templates/*/meta.json (+ _themes.json).

    python3 bin/gen_catalog.py            # ghi docs/TEMPLATE_CATALOG.md
    python3 bin/gen_catalog.py --check    # exit 1 nếu file đang commit đã LỖI THỜI so với meta (dùng trong CI)

Skill/tài liệu CHỈ được trỏ tới file này khi cần danh sách template, KHÔNG tự chép tên template
vào văn bản (đã từng lệch: 7 tên không tồn tại trong broll-director/TEXT_DENSITY_RULES).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent
TPL = FACTORY / "templates"
OUT = FACTORY / "docs" / "TEMPLATE_CATALOG.md"


def build() -> str:
    themes = json.loads((TPL / "_themes.json").read_text(encoding="utf-8"))["themes"]
    metas = {}
    for d in sorted(p for p in TPL.iterdir() if p.is_dir() and not p.name.startswith("_")):
        metas[d.name] = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    active = {k: v for k, v in metas.items() if v.get("status") == "active"}
    L = []
    L.append("# TEMPLATE_CATALOG (TỰ SINH — KHÔNG SỬA TAY)\n")
    L.append("> Sinh bởi `bin/gen_catalog.py` từ `templates/*/meta.json`. Sửa meta rồi chạy lại; "
             "`gen_catalog.py --check` báo lỗi thời. Đây là NGUỒN DUY NHẤT cho 'template nào tồn tại, "
             "dùng khi nào' — skill và doctrine trỏ về đây, không tự liệt kê tên.\n")
    L.append(f"**{len(active)} template active** · {len(themes)} theme · chuẩn schema `specVersion 2` "
             "(xem `docs/TEMPLATE_SPEC.md`).\n")

    L.append("## 1. Theo chủ đề (theme)\n")
    L.append("Chọn theme theo thể loại video (`broll-genre-palette`), rồi chọn template trong hàng đó. "
             "'general' = dùng được cho mọi video nên không liệt kê lại ở đây.\n")
    L.append("| Theme | Thể loại (genre) | Accent mặc định | Template (id) |")
    L.append("|---|---|---|---|")
    for t in themes:
        if t["id"] == "general":
            continue
        ids = [k for k, m in active.items() if t["id"] in (m.get("themes") or [])]
        L.append(f"| `{t['id']}` {t['name']} | {t.get('genre') or '—'} | {t.get('defaultAccent')} | "
                 + ", ".join(f"`{i}`" for i in ids) + " |")
    L.append("")

    L.append("## 2. Theo vai trò (category) và vị trí\n")
    L.append("`placement`: `subtitle-bottom` (mặc định, trên vùng phụ đề) · `flush-bottom` (sát đáy) · "
             "`edge-bottom` (sát mép) · `full-stage` (phủ khung hình) · `none` (cutaway, không lớp chữ).\n")
    L.append("| Category | Template | placement | nền | SFX gợi ý (id vol) |")
    L.append("|---|---|---|---|---|")
    bycat: dict[str, list] = {}
    for k, m in active.items():
        bycat.setdefault(m.get("category", "?"), []).append(k)
    for cat in sorted(bycat):
        for k in bycat[cat]:
            m = active[k]
            sfx = m.get("sfx")
            s = f"{sfx['id']} {sfx.get('volume')}" if isinstance(sfx, dict) else "—"
            L.append(f"| {cat} | `{k}` v{m['version']} | {m.get('placement', '?')} | {m.get('background')} | {s} |")
    L.append("")

    L.append("## 3. Chi tiết từng template\n")
    for k, m in active.items():
        L.append(f"### `{k}` — {m.get('name')}  (v{m['version']}, {m.get('mode')}, {m.get('category')})")
        inp = []
        for n, d in (m.get("inputs") or {}).items():
            if d.get("noEffect"):
                continue
            flag = "*" if d.get("required") else ""
            ex = ""
            if d.get("type") == "enum" and d.get("values"):
                ex = "∈{" + "|".join(map(str, d["values"][:6])) + ("…" if len(d["values"]) > 6 else "") + "}"
            elif d.get("maxItems"):
                ex = f"≤{d['maxItems']} mục×{d.get('maxLength', '?')}"
            elif d.get("maxLength"):
                ex = f"≤{d['maxLength']}"
            if d.get("pattern"):
                ex += " (có %)"
            inp.append(f"`{n}`{flag} {ex}".strip())
        L.append("- **Input** (* bắt buộc): " + "; ".join(inp))
        L.append("- **Dùng khi**: " + " · ".join(m.get("whenToUse") or []))
        L.append("- **KHÔNG dùng khi**: " + " · ".join(m.get("notFor") or []))
        if m.get("constraints"):
            L.append("- **Ràng buộc**: " + "; ".join(
                (f"tổng = {c['equals']}" if c["type"] == "sum" else f"bắt buộc thêm theo {c['countKey']}")
                for c in m["constraints"]))
        L.append(f"- Ảnh nội dung: {'CÓ (không dùng nền trung tính)' if not m.get('neutralBgEligible') else 'không → đủ điều kiện nền trung tính'}")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    text = build()
    if a.check:
        cur = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if cur != text:
            print("TEMPLATE_CATALOG.md LỖI THỜI — chạy: python3 bin/gen_catalog.py", file=sys.stderr)
            sys.exit(1)
        print("TEMPLATE_CATALOG.md khớp meta.json")
        return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    print(f"ghi {OUT} ({len(text)} ký tự)")


if __name__ == "__main__":
    main()
