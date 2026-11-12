#!/usr/bin/env python3
"""Nâng meta.json của mọi template lên specVersion 2 — CỘNG THÊM, KHÔNG ĐỔI HÀNH VI RENDER.

    python3 bin/migrate_meta_v2.py --dry-run   # chỉ báo cáo sẽ đổi gì
    python3 bin/migrate_meta_v2.py             # ghi file (idempotent: chạy lại không đổi gì thêm)

Những gì script làm (mỗi mục là một thay đổi nhỏ, có lý do, có thể kiểm bằng validate_templates.py):
  1. enum: thêm `values` suy ra từ CSS/engine; khóa cũ `enum` -> `values`.
  2. input hệ thống `position`/`animation` (engine không đọc): thêm `noEffect: true`.
  3. input số (w*, pct*): thêm min/max/integer.
  4. input danh sách (items): thêm maxLength theo MỖI MỤC khi còn thiếu (giá trị khởi điểm — QA hiệu chỉnh).
  5. sfx dạng chuỗi -> object {id, offsetSec, volume}.
  6. specVersion=2, placement (thay ID hardcode trong render_draft), neutralBgEligible (thay luật chữ trong skill SX).
  7. themes: bổ sung theo ma trận thể loại (skills/broll-genre-palette).
  8. constraints: requiredWhen (compare-bars) — khái quát hóa khối hardcode trong preflight.
  9. sửa notFor trỏ template không tồn tại.
Giữ nguyên: version, description, HTML, CSS, SFX gợi ý, mọi giá trị mặc định.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TPL = HERE.parent / "templates"

ACCENT_VALUES = ["gold", "red", "cyan", "green", "pink", "purple", "orange", "white", "violet"]
POSITION_VALUES = ["top", "center", "bottom", "left", "right"]
ANIMATION_VALUES = ["none", "fade", "flash", "slide-up", "slide-left", "slide-right", "pop", "wipe"]
FLUSH_BOTTOM = {"preview-banner", "keyword-block"}
EDGE_BOTTOM = {"clip-caption"}

# Template KHÔNG được dùng nền trung tính dù không có input ảnh (CEO 13/11/2026, DEC-268):
# cutaway-standard là cảnh cắt chuyển mạch — phải có ảnh thật, không được chạy nền trơn.
NEUTRAL_BG_EXCLUDE = {"cutaway-standard"}

# Giá trị khởi điểm cho maxLength MỖI MỤC của input danh sách (chưa từng có giới hạn).
ITEM_MAXLEN = {"map-route": 24, "podium-rank": 40, "timeline-horizontal": 36, "timeline-strip": 64}

# enum theo template (suy ra từ CSS .broll-*-<giá trị> và README/preflight)
ENUM_VALUES = {
    ("bar-chart", "tone"): ["money", "volume", "decline", "mild"],
    ("compare-bars", "tone"): ["gold", "white", "decline"],
    ("compare-bars", "count"): ["2", "3", "4"],
    ("market-ticker", "dir"): ["up", "down"],
    ("verdict-stamp", "tone"): ["green", "red"],
    ("verdict-stamp", "tilt"): ["-15", "0", "15"],
}

# Ma trận theme bổ sung (nguồn: skills/broll-genre-palette §2 "Template Thường Dùng" + đánh giá whenToUse)
THEME_ADD = {
    "war": ["section-title", "thesis-marker"],
    "economy": ["tactical-banner", "section-title", "thesis-marker", "market-ticker", "trend-badge", "share-bar"],
    "history": ["thesis-marker", "section-title", "source-citation"],
    "tech": ["tactical-banner", "stat-counter", "keyword-burst", "section-title", "typewriter-reveal",
             "compare-bars", "bar-chart", "lower-third-pro", "info-note", "trend-badge", "step-flow"],
    "science": ["section-title", "stat-counter", "typewriter-reveal", "timeline-horizontal", "info-note",
                "bar-chart", "compare-bars", "step-flow", "share-bar", "map-route"],
    "crime": ["typewriter-reveal", "keyword-burst", "date-stamp", "quote-card", "timeline-strip",
              "source-citation", "strike-verdict", "verdict-stamp", "social-comment", "comment-frame",
              "thesis-marker", "info-note"],
    "sports": ["dual-stat", "compare-bars", "poll-vote", "bar-chart"],
}


def stage_values(m: dict) -> list[str] | None:
    mx = m.get("maxStage")
    if isinstance(mx, int) and mx >= 1:
        return [str(i) for i in range(1, mx + 1)]
    return None


def migrate(tid: str, m: dict, idset: set) -> list[str]:
    log: list[str] = []
    inputs = m.get("inputs") or {}
    has_img = False

    for k, d in inputs.items():
        if not isinstance(d, dict):
            continue
        base = k.rstrip("1234")
        if d.get("type") == "image":
            has_img = True
        # 1/2. enum values + noEffect
        if d.get("type") == "enum":
            if "enum" in d and "values" not in d:
                d["values"] = d.pop("enum")
                log.append(f"inputs.{k}: enum -> values")
            if "values" not in d:
                vals = None
                if base == "accent":
                    vals = ACCENT_VALUES
                elif base == "position":
                    vals = POSITION_VALUES
                elif base == "animation":
                    vals = ANIMATION_VALUES
                elif base == "stage":
                    vals = stage_values(m)
                else:
                    vals = ENUM_VALUES.get((tid, base))
                if vals:
                    d["values"] = vals
                    log.append(f"inputs.{k}: + values {vals}")
            if base == "accent" and isinstance(d.get("values"), list):
                for extra in ACCENT_VALUES:
                    if extra not in d["values"]:
                        d["values"].append(extra)
            if base in ("position", "animation") and not d.get("noEffect"):
                d["noEffect"] = True
                log.append(f"inputs.{k}: + noEffect (engine không đọc)")
        # 3. số (poll-vote: {{pct}} vừa là chữ vừa là `width:` nên BẮT BUỘC có đuôi %)
        if tid == "poll-vote" and base == "pct" and "pattern" not in d:
            d["pattern"] = r"(100|[1-9]?\d)%"
            d["patternHint"] = "số 0-100 kèm dấu %, vd 68% — dùng làm width CSS nên thiếu % thì thanh bar mất kích thước"
            log.append(f"inputs.{k}: + pattern (giá trị phải có đuôi %)")
        elif re.fullmatch(r"(w|pct)\d*", k) and d.get("type") == "string":
            for kk, vv in (("min", 0), ("max", 100), ("integer", True)):
                if kk not in d:
                    d[kk] = vv
                    log.append(f"inputs.{k}: + {kk}={vv}")
        # 4. items
        if d.get("type") == "string" and "maxItems" in d and "maxLength" not in d:
            d["maxLength"] = ITEM_MAXLEN.get(tid, 48)
            log.append(f"inputs.{k}: + maxLength={d['maxLength']} (mỗi mục, khởi điểm)")

    # 5. sfx chuỗi -> object
    if isinstance(m.get("sfx"), str):
        m["sfx"] = {"id": m["sfx"], "offsetSec": 0, "volume": 0.6}
        log.append("sfx: chuỗi -> object (volume 0.6 = mặc định của render_draft)")

    # 6. specVersion / placement / neutralBgEligible
    if m.get("specVersion") != 2:
        m["specVersion"] = 2
        log.append("specVersion=2")
    if "placement" not in m:
        if m.get("mode") == "cutaway":
            pl = "none"
        elif m.get("mode") == "fullscreen" or (m.get("position") or {}).get("default") == "full-stage":
            pl = "full-stage"
        elif tid in FLUSH_BOTTOM:
            pl = "flush-bottom"
        elif tid in EDGE_BOTTOM:
            pl = "edge-bottom"
        else:
            pl = "subtitle-bottom"
        m["placement"] = pl
        log.append(f"placement={pl}")
    if "neutralBgEligible" not in m:
        m["neutralBgEligible"] = (not has_img) and tid not in NEUTRAL_BG_EXCLUDE
        log.append(f"neutralBgEligible={m['neutralBgEligible']}")

    # 7. themes
    th = list(m.get("themes") or [])
    for theme, tids in THEME_ADD.items():
        if tid in tids and theme not in th:
            th.append(theme)
            log.append(f"themes + {theme}")
    m["themes"] = th

    # 8. constraints
    if tid == "compare-bars" and not m.get("constraints"):
        m["constraints"] = [{
            "type": "requiredWhen", "countKey": "count",
            "keysByCount": {"3": ["label3", "value3", "w3", "tone3"],
                            "4": ["label3", "value3", "w3", "tone3", "label4", "value4", "w4", "tone4"]},
        }]
        log.append("constraints: requiredWhen(count) — khái quát khối hardcode trong preflight")

    # 9. notFor ref ma
    nf = m.get("notFor") or []
    new_nf = []
    for s in nf:
        for ref in re.findall(r"\(dùng ([a-z0-9\-]+)", s):
            if ref not in idset:
                fix = {"keyword-emphasis": "keyword-burst"}.get(ref)
                if fix:
                    s = s.replace(f"dùng {ref}", f"dùng {fix}")
                    log.append(f"notFor: {ref} -> {fix}")
        new_nf.append(s)
    m["notFor"] = new_nf

    # exampleInputs4Bars -> exampleVariants (khóa meta ngoài chuẩn)
    if "exampleInputs4Bars" in m:
        m.setdefault("exampleVariants", {})["4bars"] = m.pop("exampleInputs4Bars")
        log.append("exampleInputs4Bars -> exampleVariants.4bars")

    # checklist: ví dụ chuẩn của chính meta bị preflight cũ chặn oan; ngữ nghĩa maxLength là MỖI DÒNG
    return log


def dump_like(raw: str, m: dict) -> str:
    m = dict(sorted(m.items()))
    if "\n" in raw.strip():
        return json.dumps(m, ensure_ascii=False, indent=2)
    return json.dumps(m, ensure_ascii=False, sort_keys=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    ids = sorted(p.name for p in TPL.iterdir() if p.is_dir() and not p.name.startswith("_"))
    idset = set(ids)
    total = 0
    for tid in ids:
        f = TPL / tid / "meta.json"
        raw = f.read_text(encoding="utf-8")
        m = json.loads(raw)
        log = migrate(tid, m, idset)
        if log:
            total += 1
            print(f"{tid}: {len(log)} thay đổi")
            for l in log:
                print("   -", l)
            if not a.dry_run:
                f.write_text(dump_like(raw, m), encoding="utf-8")
    print(f"\n{'(dry-run) ' if a.dry_run else ''}{total}/{len(ids)} template có thay đổi")


if __name__ == "__main__":
    main()
