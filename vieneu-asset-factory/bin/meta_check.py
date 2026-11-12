#!/usr/bin/env python3
"""Kiểm tra giá trị input của template theo khai báo trong meta.json.

Một nguồn logic duy nhất cho:
  - bin/preflight.py        (kiểm input của từng part trong plan)
  - bin/validate_templates.py (kiểm exampleInputs của từng template)

Chỉ dùng thư viện chuẩn (venv factory không có jsonschema).

Các khóa meta.inputs.<tên> được hiểu (tất cả TÙY CHỌN, thiếu thì bỏ qua kiểm đó):
  type        "string" | "enum" | "image"
  required    bool                         (do nơi gọi kiểm — xem is_missing)
  maxLength   int   — với input có maxItems: giới hạn MỖI DÒNG; ngược lại: cả chuỗi
  maxItems    int   — số dòng/mục tối đa của input dạng danh sách (items)
  values      [str] — tập giá trị hợp lệ của enum
  min, max    số    — khoảng hợp lệ cho input mang ý nghĩa số (w1, pct1, ...)
  integer     bool  — bắt buộc số nguyên
  pattern     regex — giá trị phải khớp toàn chuỗi (vd poll-vote: "68%" vì {{pct1}} vừa là chữ vừa là width)
  patternHint str   — mô tả ngắn hiển thị khi sai pattern

meta.constraints (mảng) — ràng buộc liên-input, mỗi phần tử:
  {"type": "requiredWhen", "countKey": "count", "keysByCount": {"3": [...], "4": [...]}}
      count=N thì các khóa trong keysByCount[N] phải có giá trị
  {"type": "sum", "countKey": "count", "keysByCount": {"2": [...], ...},
   "equals": 100, "tolerance": 1}
      tổng các khóa trong keysByCount[N] phải bằng `equals` ± tolerance
"""
from __future__ import annotations

import re

_NUM_RE = re.compile(r"^-?\d+(?:[.,]\d+)?$")


def is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, (list, tuple)):
        return not any(str(x).strip() for x in value)
    return not str(value).strip()


def as_lines(value) -> list[str]:
    """Input dạng danh sách (items): list hoặc chuỗi nhiều dòng -> list dòng không rỗng."""
    if isinstance(value, (list, tuple)):
        return [str(x) for x in value if str(x).strip()]
    return [ln for ln in str(value).splitlines() if ln.strip()]


def _to_number(value):
    s = str(value).strip().replace(" ", "")
    # Hậu tố % (vd poll-vote pct1="68%" — pattern đã kiểm định dạng, đây chỉ
    # lấy phần số để kiểm min/max/integer; migrate 2b gán min/max cho pct*).
    if s.endswith("%"):
        s = s[:-1]
    if not _NUM_RE.match(s):
        return None
    return float(s.replace(",", "."))


def check_input_value(name: str, idef: dict, value) -> list[str]:
    """Trả danh sách thông báo lỗi (rỗng = hợp lệ). Giá trị rỗng không bị kiểm ở đây
    (input bắt buộc do nơi gọi kiểm bằng is_missing)."""
    errs: list[str] = []
    if not isinstance(idef, dict) or is_missing(value):
        return errs
    max_items = idef.get("maxItems")
    max_len = idef.get("maxLength")

    if isinstance(max_items, int) and not isinstance(max_items, bool):
        lines = as_lines(value)
        if len(lines) > max_items:
            errs.append(f"'{name}' có {len(lines)} mục > tối đa {max_items}")
        if isinstance(max_len, int):
            for i, ln in enumerate(lines, 1):
                if len(ln) > max_len:
                    errs.append(f"'{name}' mục {i} dài {len(ln)} > {max_len} ký tự")
    elif isinstance(max_len, int) and not isinstance(max_len, bool):
        if len(str(value)) > max_len:
            errs.append(f"'{name}' dài {len(str(value))} > {max_len} ký tự")

    vals = idef.get("values")
    if idef.get("type") == "enum" and isinstance(vals, list) and vals:
        if str(value).strip() not in [str(v) for v in vals]:
            errs.append(f"'{name}'='{value}' không thuộc {vals}")

    pat = idef.get("pattern")
    if isinstance(pat, str) and not re.fullmatch(pat, str(value).strip()):
        errs.append(f"'{name}'='{value}' sai định dạng" + (f" ({idef['patternHint']})" if idef.get("patternHint") else f" (cần khớp {pat})"))

    lo, hi = idef.get("min"), idef.get("max")
    if lo is not None or hi is not None or idef.get("integer"):
        num = _to_number(value)
        if num is None:
            errs.append(f"'{name}'='{value}' phải là số")
        else:
            if idef.get("integer") and num != int(num):
                errs.append(f"'{name}'={value} phải là số nguyên")
            if lo is not None and num < lo:
                errs.append(f"'{name}'={value} < min {lo}")
            if hi is not None and num > hi:
                errs.append(f"'{name}'={value} > max {hi}")
    return errs


def check_constraints(meta: dict, inputs: dict) -> list[str]:
    """Kiểm meta.constraints trên bộ inputs của một part / exampleInputs."""
    errs: list[str] = []
    inputs = inputs or {}
    for c in (meta.get("constraints") or []):
        if not isinstance(c, dict):
            continue
        ctype = c.get("type")
        count_key = c.get("countKey")
        default = ((meta.get("inputs") or {}).get(count_key) or {}).get("default") if count_key else None
        count = str(inputs.get(count_key, default if default is not None else "")).strip()
        keys = (c.get("keysByCount") or {}).get(count)
        if keys is None:
            continue
        if ctype == "requiredWhen":
            for k in keys:
                if is_missing(inputs.get(k)):
                    errs.append(f"{count_key}={count} nhưng thiếu input '{k}'")
        elif ctype == "sum":
            nums = [_to_number(inputs.get(k)) for k in keys]
            if any(n is None for n in nums):
                errs.append(f"{count_key}={count}: các input {keys} phải đều là số để kiểm tổng")
                continue
            total = sum(nums)
            eq, tol = c.get("equals", 100), c.get("tolerance", 0)
            if abs(total - eq) > tol:
                errs.append(f"tổng {keys} = {total:g}, phải bằng {eq} (±{tol})")
    return errs


def check_all_inputs(meta: dict, inputs: dict) -> list[str]:
    """Kiểm giá trị + ràng buộc cho toàn bộ inputs của một part."""
    errs: list[str] = []
    for name, idef in (meta.get("inputs") or {}).items():
        errs += check_input_value(name, idef, (inputs or {}).get(name))
    errs += check_constraints(meta, inputs)
    return errs
