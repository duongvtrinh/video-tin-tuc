#!/usr/bin/env python3
"""Kiểm tra tĩnh toàn bộ catalog template — chạy trước mỗi lần đẩy repo / thêm sửa template.

    python3 bin/validate_templates.py            # in báo cáo, exit 1 nếu có ERROR
    python3 bin/validate_templates.py --strict   # WARN cũng làm exit 1
    python3 bin/validate_templates.py --json     # xuất JSON máy đọc được
    python3 bin/validate_templates.py --no-docs  # bỏ quét tham chiếu trong tài liệu
    python3 bin/validate_templates.py --only photo-duo,stat-counter

Chỉ dùng thư viện chuẩn. Nguồn chuẩn: templates/_tokens.json + templates/_themes.json
+ docs/TEMPLATE_SPEC.md. Mã kiểm: M01..M18 (xem docs/TEMPLATE_SPEC.md §7).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
FACTORY = HERE.parent
sys.path.insert(0, str(HERE))
import meta_check  # noqa: E402

TPL = FACTORY / "templates"
REQUIRED_KEYS = ["id", "name", "version", "status", "mode", "background", "category",
                 "description", "inputs", "exampleInputs", "whenToUse", "notFor",
                 "themes", "supportedAspectRatios", "hidesSubs", "schemaVersion"]
STATUS = {"active", "draft", "retired"}
MODES = {"overlay", "fullscreen", "cutaway"}
BACKGROUNDS = {"transparent", "opaque"}
RATIOS = {"9:16", "16:9", "1:1", "4:3"}
PLACEMENTS = {"full-stage", "flush-bottom", "edge-bottom", "subtitle-bottom", "none"}
# Ngoại lệ M12 cho neutralBgEligible (DEC-268, CEO 13/11/2026): template
# mode=cutaway luôn phải có ảnh/video phù hợp với lời đọc nên
# neutralBgEligible=false là đúng luật dù không có input ảnh — M12 mặc
# định (đủ điều kiện = không có input ảnh) không áp cho các template này.
M12_NEUTRAL_BG_EXCEPTIONS = {"cutaway-standard": "DEC-268", "preview-banner": "DEC-274"}
SYSTEM_INPUTS = {"accent", "position", "animation"}  # khóa hệ thống, không xuất hiện trong HTML
INPUT_TYPES = {"string", "enum", "image"}
LEGACY_CLASS_PREFIX = {"clip-caption", "comment-frame", "source-footer-safe", "story-title"}
TEMPLATE_WORDS = ("banner", "ticker", "badge", "tally", "flash", "emphasis", "third", "card",
                  "stamp", "burst", "strip", "block", "marker", "counter", "split", "bars",
                  "chart", "title", "header", "caption", "note", "citation", "route", "rank",
                  "vote", "comment", "frame", "score", "board", "hero", "duo", "quote",
                  "reveal", "verdict", "cutaway", "checklist", "timeline", "hook", "flow",
                  "bar", "pin", "preview", "footer", "story", "clip", "photo", "stat")
HISTORY_OK = re.compile(r"không tồn tại|tên cũ|đã gỡ|gỡ khỏi|legacy|backup|không còn|bãi bỏ|lịch sử|trước đây|renamed|cũ:", re.I)
DATE_RE = re.compile(r"\b\d{2}/\d{2}/20\d{2}\b")


class Report:
    def __init__(self):
        self.items = []  # (sev, tid, code, msg)

    def add(self, sev, tid, code, msg):
        self.items.append((sev, tid, code, msg))

    def count(self, sev):
        return sum(1 for i in self.items if i[0] == sev)


def norm_hex(h: str) -> str:
    h = h.lower()
    if len(h) == 4:
        h = "#" + "".join(c * 2 for c in h[1:])
    return h


def css_colors(css: str) -> set:
    cols = {norm_hex(x) for x in re.findall(r"#[0-9a-fA-F]{3,6}\b", css)}
    for r, g, b in re.findall(r"rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", css):
        cols.add("#%02x%02x%02x" % (int(r), int(g), int(b)))
    return cols


def font_vmins(css: str) -> set:
    out = set()
    for decl in re.findall(r"(?:^|[;{\s])(font(?:-size)?)\s*:([^;}]*)", css):
        for v in re.findall(r"(\d+(?:\.\d+)?)vmin", decl[1]):
            out.add(float(v))
    return out


def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def validate(only=None, scan_docs=True):
    rep = Report()
    tokens = load_json(TPL / "_tokens.json")
    themes = load_json(TPL / "_themes.json")
    theme_ids = {t["id"] for t in themes["themes"]}
    accents = set(tokens["accents"]) | set(tokens.get("accentAliases", {}))
    sfx_ids = set(tokens["sfx"]["files"])
    heavy_kw = tokens["sfx"]["heavyKeywords"]
    heavy_cap = tokens["sfx"]["heavyVolumeCap"]
    pal = {norm_hex(tokens["accents"][k]) for k in tokens["accents"]}
    pal |= {norm_hex(c) for c in tokens["palette"]["text"]}
    pal |= {norm_hex(tokens["palette"][k]) for k in ("ink", "redDeep", "black")}
    pal |= {norm_hex(v) for v in tokens["palette"]["moss"].values()}
    pal |= {norm_hex(t["tokens"][k]) for t in themes["themes"] for k in t.get("tokens", {})}
    pal |= {"#fff", "#000"}
    scale = set(tokens["typeScaleVmin"])
    exc_colors = {k: {norm_hex(x) for x in v} for k, v in tokens["paletteExceptions"].items() if not k.startswith("_")}
    dev_colors = {k: {norm_hex(x) for x in v} for k, v in tokens["knownDeviations"]["colors"].items()}
    exc_vmin = {k: set(v) for k, v in tokens["typeScaleExceptions"].items()}
    dev_vmin = {k: set(v) for k, v in tokens["knownDeviations"]["fontVmin"].items()}
    desc_max = tokens["limits"]["descriptionSoftMaxChars"]

    ids = sorted(p.name for p in TPL.iterdir() if p.is_dir() and not p.name.startswith("_"))
    idset = set(ids)
    metas = {}
    for tid in ids:
        if only and tid not in only:
            continue
        d = TPL / tid
        try:
            m = load_json(d / "meta.json")
        except Exception as e:  # noqa: BLE001
            rep.add("ERROR", tid, "M01", f"meta.json không đọc được: {e}")
            continue
        metas[tid] = m
        for fn in ("template.html", "style.css"):
            if not (d / fn).exists():
                rep.add("ERROR", tid, "M01", f"thiếu {fn}")
        if not (d / "template.html").exists() or not (d / "style.css").exists():
            continue
        html = (d / "template.html").read_text(encoding="utf-8")
        css = (d / "style.css").read_text(encoding="utf-8")
        E = lambda c, msg: rep.add("ERROR", tid, c, msg)  # noqa: E731
        W = lambda c, msg: rep.add("WARN", tid, c, msg)  # noqa: E731

        # --- M01/M02 khóa bắt buộc + enum
        for k in REQUIRED_KEYS:
            if k not in m:
                E("M01", f"thiếu khóa bắt buộc '{k}'")
        if m.get("id") != tid:
            E("M01", f"id '{m.get('id')}' ≠ tên thư mục '{tid}'")
        if m.get("status") not in STATUS:
            E("M02", f"status '{m.get('status')}' không hợp lệ")
        if m.get("mode") not in MODES:
            E("M02", f"mode '{m.get('mode')}' không hợp lệ")
        if m.get("background") not in BACKGROUNDS:
            E("M02", f"background '{m.get('background')}' không hợp lệ")
        if not re.fullmatch(r"\d+\.\d+\.\d+", str(m.get("version", ""))):
            E("M02", f"version '{m.get('version')}' không phải semver")
        bad_r = set(m.get("supportedAspectRatios") or []) - RATIOS
        if bad_r:
            E("M02", f"supportedAspectRatios lạ: {sorted(bad_r)}")
        if not isinstance(m.get("hidesSubs"), bool):
            E("M02", "hidesSubs phải là bool")

        # --- M03 themes
        th = m.get("themes") or []
        if not th:
            E("M03", "themes rỗng")
        for x in th:
            if x not in theme_ids:
                E("M03", f"theme '{x}' không có trong _themes.json")

        # --- M04 sfx
        sfx = m.get("sfx")
        if sfx is not None:
            if not isinstance(sfx, dict):
                E("M04", f"sfx phải là object {{id, offsetSec, volume}}, đang là {type(sfx).__name__}: {sfx!r}")
            else:
                if sfx.get("id") not in sfx_ids:
                    E("M04", f"sfx.id '{sfx.get('id')}' không có trong _tokens.json (8 file chuẩn)")
                v = sfx.get("volume")
                if not isinstance(v, (int, float)) or not (0 < v <= 1):
                    E("M04", f"sfx.volume '{v}' phải trong (0,1]")
                elif any(k in str(sfx.get("id")) for k in heavy_kw) and v > heavy_cap:
                    W("M04", f"sfx nặng volume {v} > cap {heavy_cap}: render sẽ cắt thầm lặng về {heavy_cap}")
                o = sfx.get("offsetSec", 0)
                if not isinstance(o, (int, float)):
                    E("M04", f"sfx.offsetSec '{o}' phải là số")
                elif o < 0:
                    W("M04", f"sfx.offsetSec={o} âm: part đứng đầu video sẽ làm ffmpeg adelay lỗi nếu chưa có bản vá kẹp ≥0 (patches/render_draft)")

        # --- M05/M06 inputs
        inputs = m.get("inputs") or {}
        for k, d_ in inputs.items():
            if not isinstance(d_, dict):
                E("M05", f"input '{k}' phải là object")
                continue
            ty = d_.get("type")
            if ty not in INPUT_TYPES:
                E("M05", f"input '{k}' type '{ty}' không hợp lệ")
            no_effect = bool(d_.get("noEffect"))
            if ty == "string" and "maxLength" not in d_:
                E("M05", f"input chuỗi '{k}' thiếu maxLength")
            if ty == "string" and "maxItems" in d_ and "maxLength" not in d_:
                E("M05", f"input danh sách '{k}' thiếu maxLength (mỗi mục)")
            if ty == "enum":
                vals = d_.get("values")
                if not no_effect:
                    if not isinstance(vals, list) or not vals:
                        E("M05", f"enum '{k}' thiếu danh sách 'values'")
                    elif "default" in d_ and str(d_["default"]) not in [str(x) for x in vals]:
                        E("M05", f"enum '{k}' default '{d_['default']}' không thuộc values")
                if k == "accent" and isinstance(vals, list):
                    bad = [x for x in vals if x not in accents]
                    if bad:
                        E("M05", f"accent values {bad} không có trong _tokens.accents")
            if re.fullmatch(r"(w|pct)\d*", k) and "pattern" not in d_ and ("min" not in d_ or "max" not in d_):
                E("M06", f"input mang ý nghĩa số '{k}' thiếu min/max")
            if "enum" in d_ and "values" not in d_:
                E("M05", f"input '{k}' dùng khóa 'enum' cũ — chuẩn là 'values'")
        # --- M08 placeholder ↔ inputs
        ph = set(re.findall(r"\{\{(\w+)\}\}", html))
        for k in sorted(ph - set(inputs)):
            E("M08", f"HTML dùng {{{{{k}}}}} nhưng meta.inputs không khai — engine sẽ thay bằng chuỗi rỗng thầm lặng")
        for k in sorted(set(inputs) - ph):
            if k in SYSTEM_INPUTS:
                if k in ("position", "animation") and not inputs[k].get("noEffect"):
                    W("M08", f"input hệ thống '{k}' không có tác dụng trong engine hiện tại — đánh dấu noEffect:true hoặc xóa")
            else:
                W("M08", f"input '{k}' khai nhưng HTML không dùng")

        # --- M07 exampleInputs
        ex = m.get("exampleInputs") or {}
        for k, d_ in inputs.items():
            if isinstance(d_, dict) and d_.get("required") and meta_check.is_missing(ex.get(k)):
                E("M07", f"exampleInputs thiếu input bắt buộc '{k}'")
        for k, v in ex.items():
            if k not in inputs:
                E("M07", f"exampleInputs có khóa lạ '{k}'")
        for msg in meta_check.check_all_inputs(m, ex):
            E("M07", f"exampleInputs: {msg}")
        for vname, sub in (m.get("exampleVariants") or {}).items():
            if isinstance(sub, dict):
                for msg in meta_check.check_all_inputs(m, sub):
                    E("M07", f"exampleVariants.{vname}: {msg}")
        for extra in [k for k in m if k.startswith("exampleInputs") and k != "exampleInputs"]:
            W("M07", f"'{extra}' là khóa meta ngoài chuẩn — chuyển vào exampleVariants.<tên>")

        # --- M09 notFor refs
        for s in m.get("notFor") or []:
            for ref in re.findall(r"\(dùng ([a-z0-9\-]+)", s):
                if ref not in idset:
                    E("M09", f"notFor trỏ tới template '{ref}' không tồn tại")

        # --- M10 class prefix
        for cl in re.findall(r'class="([^"]+)"', html):
            for c in cl.split():
                if "{{" in c or c.startswith("broll-"):
                    continue
                (W if tid in LEGACY_CLASS_PREFIX else E)("M10", f"class '{c}' thiếu tiền tố 'broll-'")
                break

        # --- M11 CSS
        if re.search(r"@keyframes|(?<![-\w])animation\s*:", css):
            E("M11", "CSS có animation/@keyframes — render tĩnh không chạy (đã gỡ 31/10/2026)")
        if re.search(r"radial-gradient\([^)]*\d%\s+\d+%", css):
            E("M11", "radial-gradient có color-stop 2 vị trí — WeasyPrint rớt nền, viết tường minh từng mốc")
        if "Anton" not in css:
            W("M11", "không dùng font Anton")
        offc = sorted(c for c in css_colors(css) if c not in pal)
        offc_exc = exc_colors.get(tid, set())
        offc_dev = dev_colors.get(tid, set())
        for c in offc:
            if c in offc_exc:
                continue
            (W if c in offc_dev else E)("M11", f"màu {c} ngoài bảng _tokens" + (" (nợ đã biết)" if c in offc_dev else ""))
        for v in sorted(font_vmins(css)):
            if v in scale or v in exc_vmin.get(tid, set()):
                continue
            (W if v in dev_vmin.get(tid, set()) else E)("M11", f"cỡ chữ {v}vmin ngoài thang _tokens" + (" (nợ đã biết)" if v in dev_vmin.get(tid, set()) else ""))

        # --- M12 placement / neutralBgEligible (schema v2)
        if m.get("specVersion", 1) >= 2:
            pl = m.get("placement")
            if pl not in PLACEMENTS:
                E("M12", f"placement '{pl}' không hợp lệ (cần {sorted(PLACEMENTS)})")
            elif m.get("mode") == "fullscreen" and pl != "full-stage":
                E("M12", "mode fullscreen phải có placement full-stage")
            elif m.get("mode") == "cutaway" and pl != "none":
                E("M12", "mode cutaway phải có placement none")
            has_img = any(isinstance(d_, dict) and d_.get("type") == "image" for d_ in inputs.values())
            if m.get("neutralBgEligible") is None:
                E("M12", "thiếu neutralBgEligible (luật Production: đủ điều kiện = không có input ảnh)")
            elif m["neutralBgEligible"] == has_img:
                if tid in M12_NEUTRAL_BG_EXCEPTIONS:
                    rep.add("INFO", tid, "M12", f"neutralBgEligible={m['neutralBgEligible']} trái quy tắc mặc định nhưng là ngoại lệ {M12_NEUTRAL_BG_EXCEPTIONS[tid]}")
                else:
                    E("M12", f"neutralBgEligible={m['neutralBgEligible']} mâu thuẫn với input ảnh ({'có' if has_img else 'không có'})")
        else:
            W("M12", "chưa có specVersion 2 (placement/neutralBgEligible) — chạy tools/migrate_meta_v2.py")

        # --- M13 description
        dsc = m.get("description", "")
        if len(dsc) > desc_max or DATE_RE.search(dsc):
            W("M13", f"description dài {len(dsc)} ký tự/chứa ngày lịch sử — chuyển lịch sử sang 'changelog'")

        # --- M14 constraints
        for c in m.get("constraints") or []:
            for keys in (c.get("keysByCount") or {}).values():
                for k in keys:
                    if k not in inputs:
                        E("M14", f"constraint trỏ tới input '{k}' không tồn tại")
            if c.get("countKey") and c["countKey"] not in inputs:
                E("M14", f"countKey '{c['countKey']}' không tồn tại")

        # --- M15 videoSlots
        for k in (m.get("videoSlots") or {}):
            if not (isinstance(inputs.get(k), dict) and inputs[k].get("type") == "image"):
                E("M15", f"videoSlots '{k}' phải là input type image")

    # --- M16 theme coverage
    cover = defaultdict(list)
    for tid, m in metas.items():
        for x in m.get("themes") or []:
            cover[x].append(tid)
    for t in theme_ids - {"general"}:
        if not only and len(cover[t]) < 4:
            rep.add("WARN", "(catalog)", "M16", f"theme '{t}' chỉ có {len(cover[t])} template — quá mỏng để dàn một video trọn thể loại")
    if not only and len(cover["general"]) == len(ids):
        rep.add("INFO", "(catalog)", "M16", "mọi template đều gắn theme 'general' (chấp nhận: 'general' = dùng được cho mọi video; lọc thực tế dựa vào theme chuyên biệt)")

    # --- M17 tệp phụ thuộc engine
    assets_png = FACTORY / "assets" / "transparent.png"
    legacy_png = TPL / "_shared" / "transparent.png"
    if not assets_png.exists() and not legacy_png.exists():
        rep.add("INFO", "(catalog)", "M17", "transparent.png chưa có — engine bản vá tự sinh khi cần; bản gốc thì video-slot không lỗ")

    # --- M18 tham chiếu template trong tài liệu
    if scan_docs:
        roots = [FACTORY / "skills", FACTORY / "docs", FACTORY / "PIPELINE.md", FACTORY / "README.md"]
        co = FACTORY.parent / "company-os"
        if co.exists():
            roots.append(co)
        files = []
        for r in roots:
            if r.is_file():
                files.append(r)
            elif r.exists():
                files += [p for p in r.rglob("*.md")]
        for f in sorted(files):
            if "legacy" in f.name.lower() or "CHANGELOG" in f.name or "TEMPLATE_CATALOG" in f.name:
                continue
            try:
                lines = f.read_text(encoding="utf-8").splitlines()
            except Exception:  # noqa: BLE001
                continue
            for n, line in enumerate(lines, 1):
                if HISTORY_OK.search(line):
                    continue
                toks = re.findall(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`", line)
                if line.lstrip().startswith("|"):
                    # Ô bảng: tên template thường KHÔNG có backtick. Nếu hàng đã chứa ít nhất
                    # một template thật thì quét mọi token kebab-case trong hàng đó.
                    row = re.findall(r"(?<![\w`./-])([a-z][a-z0-9]*(?:-[a-z0-9]+)+)(?![\w`./-])", line)
                    if any(t in idset for t in row):
                        toks += row
                for tok in dict.fromkeys(toks):
                    if tok in idset or tok in PLACEMENTS or not any(w in tok for w in TEMPLATE_WORDS):
                        continue
                    if tok.startswith(("media-", "broll-", "custom-", "vieneu-", "app-", "template-")):
                        continue
                    if "." in tok or tok.endswith(("-md", "-json", "-py")):
                        continue
                    rel = f.relative_to(FACTORY.parent) if str(f).startswith(str(FACTORY.parent)) else f
                    rep.add("ERROR", f"{rel}:{n}", "M18", f"tham chiếu template `{tok}` không tồn tại trong catalog")
    return rep, metas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-docs", action="store_true")
    ap.add_argument("--only")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    rep, metas = validate(only, not a.no_docs)
    if a.json:
        print(json.dumps([{"sev": s, "where": t, "code": c, "msg": m} for s, t, c, m in rep.items], ensure_ascii=False, indent=1))
    else:
        by = defaultdict(list)
        for it in rep.items:
            by[it[1]].append(it)
        for where in sorted(by):
            print(f"\n{where}")
            for sev, _, code, msg in sorted(by[where], key=lambda x: (x[0] != "ERROR", x[2])):
                print(f"  {sev:5s} {code} {msg}")
        codes = defaultdict(int)
        for s, _, c, _ in rep.items:
            codes[(s, c)] += 1
        print("\n=== TỔNG KẾT ===")
        print(f"template đã kiểm: {len(metas)} | ERROR={rep.count('ERROR')} WARN={rep.count('WARN')} INFO={rep.count('INFO')}")
        print("theo mã:", ", ".join(f"{s[0]}:{c}×{n}" for (s, c), n in sorted(codes.items(), key=lambda x: (x[0][0] != 'ERROR', x[0][1]))))
    bad = rep.count("ERROR") + (rep.count("WARN") if a.strict else 0)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
