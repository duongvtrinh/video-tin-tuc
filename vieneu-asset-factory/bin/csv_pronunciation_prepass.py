#!/usr/bin/env python3
"""Lớp quét thô bằng từ điển CSV cho phát âm VieNeu-TTS (CEO 04/11/2026).

Vấn đề: lớp agent rà soát sau sea-g2p đôi khi vẫn bỏ sót những cụm hay gặp.
Lớp này quét TRƯỚC lần normalize đầu tiên: đọc file CSV chung, tìm những
term thật sự xuất hiện trong kịch bản của project, và ghi chúng vào từ điển
riêng của project (`abbr_dict.json`). Sau đó pipeline chạy đúng như cũ:
normalize_chunks lần 1 (abbr_expand đã áp entry CSV trước engine) -> agent
rà soát 6 nhóm, trong đó có soát lại cả các hit CSV -> sửa/thêm entry nếu
cần -> normalize lại -> tts_batch. Agent vẫn là cửa cuối; lớp CSV không
bypass agent.

File CSV chung (bản gốc duy nhất nằm trên GitHub, repo private
vieneu-media-company, đường dẫn `vieneu-asset-factory/data/`):
    term,reading
    MB,em bê
    "mạng xã hội X","mạng xã hội ích"
Định dạng: UTF-8, dòng đầu là header `term,reading`, các dòng sau parse
bằng module csv (dấu phẩy phân cách, chuỗi chứa dấu phẩy đặt trong ngoặc
kép). Luật kiểm tra entry kế thừa nguyên từ `abbr_expand.py`: term không
rỗng, cách đọc không rỗng, cách đọc không chứa dấu kết câu (. ! ?) hay
xuống dòng, khớp đúng chữ hoa/thường như trong kịch bản, cụm dài ưu tiên
trước, ranh giới từ hai đầu, thay một lượt duy nhất.

Đồng bộ (CHỈ có điều kiện, theo lệnh CEO 04/11/2026): script này KHÔNG gọi
GitHub và KHÔNG tự tải CSV. Bước đồng bộ do agent làm bằng GitHub
connector TRƯỚC khi chạy script này, và chỉ đồng bộ khi có phiên bản mới:
agent lấy mã SHA của file CSV trên GitHub, so với mã đã lưu trong file
phiên bản local (`pronunciation_dict.version.json`, cạnh file cache, chỉ
nằm ở máy này, không đẩy lên repo); mã trùng và cache còn nguyên thì BỎ
QUA đồng bộ, ghi log CSV-SKIP; mã khác, hoặc chạy lần đầu, hoặc cache mất
hay hỏng thì mới tải nội dung, kiểm tra hợp lệ rồi ghi đè cache kiểu
atomic và cập nhật file phiên bản. Nếu bước hỏi GitHub lỗi thì giữ cache
cũ, ghi cảnh báo và chạy tiếp (fail-open), vì lớp agent phía sau vẫn còn.
Tuyệt đối không sửa cache local bằng tay: mọi sửa CSV đều sửa trên GitHub,
lần đồng bộ sau sẽ lấy bản mới. Script này chỉ đọc cache local.

Luật merge vào `abbr_dict.json`:
- Chỉ ghi những term CSV thật sự trúng kịch bản của project này, không ghi
  cả CSV vào từ điển project.
- Entry agent đã có sẵn trong project THẮNG khi trùng term nhưng khác cách
  đọc: entry CSV đó không ghi đè, chỉ ghi vào log xung đột để agent xem ở
  bước rà soát.
- Không có hit nào và project chưa có `abbr_dict.json` thì không tạo file,
  giữ nguyên hành vi ABBR-EMPTY hiện tại. Không có hit nào nhưng project
  đã có từ điển thì không sửa từ điển.
- Giữ nguyên định dạng file `abbr_dict.json` đang có (dạng phẳng hoặc dạng
  {"version": 1, "entries": {...}}); file mới tạo dùng dạng phẳng như các
  project gần đây (ví dụ {"MB": "em bê"}).
- Script KHÔNG sửa kịch bản/plan/voiceText, chỉ ghi `abbr_dict.json` và
  file truy vết `build/csv_pronunciation_hits.json` (term, cách đọc, số
  lần trúng, các part trúng, SHA CSV, xung đột, dòng CSV bị bỏ qua). Cách
  đọc chỉ đổi speech, phụ đề vẫn hiện câu gốc như luật abbr_dict hiện hành.

Cách chạy:
    python bin/csv_pronunciation_prepass.py <project_id>
    python bin/csv_pronunciation_prepass.py <project_id> --csv <đường-dẫn-CSV-khác>
Log stdout: CSV-OK / CSV-EMPTY / CSV-WARN kèm số hit, số part, số entry
mới, số xung đột. Thoát 0 cho mọi trường hợp đã xử lý được (kể cả cache
thiếu hay CSV không trúng); thoát 2 khi sai cách dùng; thoát 1 khi plan
của project không đọc được (lỗi thật, phải dừng).
"""
import argparse
import csv
import hashlib
import json
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from abbr_expand import _SENT_END, build_pattern, load_dict  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_csv(path: Path):
    """Đọc CSV chung. Trả về (entries, skipped, rows_total).

    entries: OrderedDict term -> reading, dòng đầu tiên thắng khi trùng.
    skipped: [{row, term, reason}] cho dòng lỗi hoặc dòng trùng.
    Dòng đầu là header term,reading thì bỏ qua; nếu không có header thì
    mọi dòng đều là dữ liệu.
    """
    entries = OrderedDict()
    skipped = []
    rows_total = 0
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    for idx, row in enumerate(rows, start=1):
        if len(row) >= 2 and row[0].strip().lower() == "term" and row[1].strip().lower() == "reading":
            continue
        rows_total += 1
        if len(row) < 2:
            skipped.append({"row": idx, "term": row[0] if row else "", "reason": "thiếu cột reading"})
            continue
        term = row[0].strip()
        reading = " ".join(row[1].split())
        if not term:
            skipped.append({"row": idx, "term": "", "reason": "term rỗng"})
            continue
        if not reading:
            skipped.append({"row": idx, "term": term, "reason": "cách đọc rỗng"})
            continue
        if _SENT_END.search(reading):
            skipped.append({"row": idx, "term": term, "reason": "cách đọc chứa dấu kết câu/xuống dòng"})
            continue
        if term in entries:
            skipped.append({"row": idx, "term": term, "reason": "trùng term, giữ dòng đầu"})
            continue
        entries[term] = reading
    return entries, skipped, rows_total


def write_abbr_dict(proj: Path, existing_path, new_entries):
    """Merge entry mới vào abbr_dict.json, giữ nguyên định dạng file cũ.

    Trả về (path, total_entries) sau khi ghi. Không gọi khi không có entry
    mới và chưa có file cũ.
    """
    if existing_path is not None and existing_path.exists():
        raw = json.loads(existing_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and isinstance(raw.get("entries"), dict):
            raw["entries"].update(new_entries)
            merged = raw
            total = len(raw["entries"])
        elif isinstance(raw, dict):
            raw.update(new_entries)
            merged = raw
            total = len([k for k in merged if not k.startswith("_")])
        else:
            merged = dict(new_entries)
            total = len(merged)
        path = existing_path
    else:
        merged = dict(new_entries)
        path = proj / "abbr_dict.json"
        total = len(merged)
    path.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path, total


def main() -> int:
    parser = argparse.ArgumentParser(description="Quét CSV phát âm vào abbr_dict của project.")
    parser.add_argument("project_id")
    parser.add_argument("--csv", default=None, help="Đường dẫn file CSV cache (mặc định: factory/data/pronunciation_dict.csv)")
    parser.add_argument("--version-file", default=None, help="Đường dẫn file phiên bản local (mặc định: cạnh file CSV)")
    parser.add_argument("--hits", default=None, help="Đường dẫn file truy vết (mặc định: project/build/csv_pronunciation_hits.json)")
    args = parser.parse_args()

    pid = args.project_id
    proj = FACTORY / "projects" / pid
    plan_path = proj / "broll-plan.json"
    try:
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"CSV-ERROR {pid}: không đọc được plan {plan_path}: {exc}", file=sys.stderr)
        return 1

    csv_path = Path(args.csv) if args.csv else FACTORY / "data" / "pronunciation_dict.csv"
    version_path = Path(args.version_file) if args.version_file else csv_path.with_suffix(".version.json")
    hits_path = Path(args.hits) if args.hits else proj / "build" / "csv_pronunciation_hits.json"

    version_info = {}
    if version_path.exists():
        try:
            version_info = json.loads(version_path.read_text(encoding="utf-8"))
        except Exception:
            version_info = {}

    if not csv_path.exists():
        print(f"CSV-WARN {pid}: không có cache CSV tại {csv_path}, bỏ qua lớp quét (pipeline chạy như cũ)", file=sys.stderr)
        hits_doc = {
            "project_id": pid,
            "csv_path": str(csv_path),
            "csv_found": False,
            "hits": {},
            "conflicts": {},
            "already_present": {},
            "new_entries_added": {},
            "skipped_rows": [],
            "github_sha": version_info.get("github_sha"),
            "csv_sha256": None,
            "synced_at": version_info.get("synced_at"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        hits_path.parent.mkdir(parents=True, exist_ok=True)
        hits_path.write_text(json.dumps(hits_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"CSV-EMPTY {pid}: hits=0 parts=0 (không có cache CSV)")
        return 0

    entries, skipped, rows_total = load_csv(csv_path)
    if not entries:
        print(f"CSV-WARN {pid}: CSV tại {csv_path} không có entry hợp lệ nào", file=sys.stderr)
        pattern = None
    else:
        pattern = build_pattern(entries)

    hits = {}
    parts_hit = set()
    if pattern is not None:
        for sc in plan.get("scenes", []):
            for pt in sc.get("parts", []):
                text = pt.get("voiceText", "")
                if not text:
                    continue
                for m in pattern.finditer(text):
                    term = m.group(0)
                    slot = hits.setdefault(term, {"reading": entries[term], "count": 0, "parts": []})
                    slot["count"] += 1
                    if pt.get("id") not in slot["parts"]:
                        slot["parts"].append(pt.get("id"))
                    parts_hit.add(pt.get("id"))

    existing_entries, existing_path = load_dict(proj)
    new_entries = {}
    conflicts = {}
    already_present = {}
    for term, slot in hits.items():
        if term in existing_entries:
            if existing_entries[term] == slot["reading"]:
                already_present[term] = slot["reading"]
            else:
                conflicts[term] = {"existing": existing_entries[term], "csv": slot["reading"]}
        else:
            new_entries[term] = slot["reading"]

    abbr_path = None
    total_entries = len(existing_entries)
    if new_entries:
        abbr_path, total_entries = write_abbr_dict(proj, existing_path, new_entries)
    elif existing_path is not None:
        abbr_path = existing_path

    hits_doc = {
        "project_id": pid,
        "csv_path": str(csv_path),
        "csv_found": True,
        "csv_rows_total": rows_total,
        "csv_rows_valid": len(entries),
        "csv_sha256": sha256_file(csv_path),
        "github_sha": version_info.get("github_sha"),
        "synced_at": version_info.get("synced_at"),
        "hits": hits,
        "conflicts": conflicts,
        "already_present": already_present,
        "new_entries_added": new_entries,
        "skipped_rows": skipped,
        "abbr_dict_path": str(abbr_path) if abbr_path else None,
        "abbr_dict_total_entries": total_entries,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
    hits_path.parent.mkdir(parents=True, exist_ok=True)
    hits_path.write_text(json.dumps(hits_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if skipped or conflicts:
        for s in skipped:
            print(f"CSV-WARN {pid}: bỏ dòng CSV {s['row']} term={s['term']!r}: {s['reason']}", file=sys.stderr)
        for term, c in conflicts.items():
            print(f"CSV-WARN {pid}: xung đột term={term!r}: giữ entry project {c['existing']!r}, không ghi đè bằng CSV {c['csv']!r}", file=sys.stderr)
    if not hits:
        print(f"CSV-EMPTY {pid}: hits=0 parts=0 csv_rows_valid={len(entries)}")
    else:
        print(f"CSV-OK {pid}: hits={sum(s['count'] for s in hits.values())} terms={len(hits)} parts={len(parts_hit)} new_entries={len(new_entries)} conflicts={len(conflicts)} abbr_dict_total={total_entries} hits={ {t: s['count'] for t, s in hits.items()} }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
