#!/usr/bin/env python3
"""Don rac sau san xuat video — chi giu file dang dung.

Co che (quyet CEO 14/11/2026):
  - Noi xac dinh cho moi file:
      + Tai ve tu trinh duyet: ~/workspace/browser_downloads/<phien>/
      + Media cua project: projects/<pid>/build/media/
          images/  — anh tai ve (ung cu vien, ca loai lan duoc chon)
          broll/   — b-roll da xu ly (doan cat/crop dang dung) — KHONG XOA
          raw/     — file goc tai ve (video stock nguyen ban, anh goc)
                     truoc khi xu ly; sau khi xu ly xong thi la rac
                     tru khi plan/media-log con tham chieu toi no.
          checks/  — anh chup khung hinh de QA soi (hook/concl/rehook,
                     contact sheet) — chi la bang chung kiem tra, khong
                     dung trong video; don sau khi duyet.
      + Tam render: /tmp/draft_* — render_draft.py tu xoa o cuoi
        (shutil.rmtree, dong 1190); chi con sot khi render crash.
  - Chay SAU KHI QA duyet (DELIVERED), khong chay truoc — Production/QA
    co the can render lai. Ghi vao skill San xuat + pipeline.
  - "File dang dung" = file co ten xuat hien trong media-log.json
    (chosen.file tung part) HOAC trong broll-plan.json (bat ky ten file
    media nao duoc tham chieu). Moi file khac trong build/media/ la rac.
  - NGOAI LE AN TOAN — build/media/broll/ KHONG BAO GIO bi xoa: day la
    dau vao render theo quy uoc (doan b-roll da cat + video stock).
    Plan khong luu ten file local cua video b-roll (chi luu
    videoSource.page_url, vd Pexels) nen khong the xac minh bang ten file
    — xoa bua se pha kha nang render lai. Video stock nguyen ban to
    (chi dung vai giay) la van de rieng: can cat ngan luc tai ve
    (cai tien pipeline), khong giai quyet bang script don rac.
  - Chi xoa trong build/media/images/, build/media/raw/ va
    build/media/checks/ (anh tai ve / file goc / anh chup khung hinh
    kiem tra) va export/ (ban preview cu hon ban moi nhat).
  - KHONG BAO GIO xoa: mp4 xuat cuoi (export/), script.json,
    broll-plan.json, media-log.json, input.json, build/audio/,
    build/subtitles/, render report, toan bo build/media/broll/.

Cach dung:
    <factory-venv-python> bin/cleanup_project.py <project_id> [--dry-run|--apply]
  Mac dinh la --dry-run (chi bao cao, khong xoa). Them --apply de xoa that.
  In ra danh sach file se xoa + tong MB. Khi --apply, ghi log vao
  <pid>/cleanup_report.txt (ghi de moi lan chay).
"""
import argparse
import json
import re
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent

MEDIA_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".webm", ".gif"}
# Ten file duoc bao ve tuyet doi (khong bao gio xoa, du khong duoc tham chieu).
PROTECTED_NAMES = {
    "script.json", "broll-plan.json", "media-log.json", "input.json",
    "cleanup_report.txt",
}
# Thu muc duoc bao ve tuyet doi.
PROTECTED_DIRS = {"audio", "subtitles"}

# Tim ten file media trong mot chuoi JSON bat ky (plan, media-log).
_MEDIA_RE = re.compile(r"([A-Za-z0-9_.\-]+\.(?:jpg|jpeg|png|webp|mp4|mov|webm|gif))")


def _collect_used_names(obj, out: set):
    """Thu tat ca ten file media xuat hien trong mot doi tuong JSON."""
    if isinstance(obj, dict):
        for v in obj.values():
            _collect_used_names(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_used_names(v, out)
    elif isinstance(obj, str):
        for m in _MEDIA_RE.findall(obj):
            out.add(m)


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"  canh bao: khong doc duoc {path}: {exc}", file=sys.stderr)
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Don rac project video sau khi QA duyet.")
    ap.add_argument("project_id", help="vd topic373001")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="chi bao cao, khong xoa (mac dinh)")
    g.add_argument("--apply", action="store_true", help="xoa that cac file rac da liet ke")
    args = ap.parse_args()
    apply = args.apply

    proj = FACTORY / "projects" / args.project_id
    if not proj.is_dir():
        print(f"khong thay project: {proj}", file=sys.stderr)
        return 1

    # 1. Tap file dang dung: media-log.json (chosen) + broll-plan.json.
    used: set = set()
    media_log = proj / "media-log.json"
    plan = proj / "broll-plan.json"
    if media_log.exists():
        data = _load_json(media_log)
        if data is not None:
            _collect_used_names(data, used)
    else:
        print("  canh bao: khong co media-log.json — chi dung broll-plan.json lam chuan", file=sys.stderr)
    if plan.exists():
        data = _load_json(plan)
        if data is not None:
            _collect_used_names(data, used)
    print(f"file media dang dung (theo media-log + plan): {len(used)}")

    # 2. Quet build/media/ — CHI images/ va _raw/ (va thu muc con khac),
    # KHONG BAO GIO xoa build/media/broll/ (dau vao render theo quy uoc;
    # plan khong luu ten file local cua video b-roll nen khong xac minh duoc).
    media_dir = proj / "build" / "media"
    to_delete: list[tuple[Path, int]] = []
    if media_dir.is_dir():
        for f in sorted(media_dir.rglob("*")):
            if not f.is_file():
                continue
            if f.suffix.lower() not in MEDIA_EXTS:
                continue
            if f.name in PROTECTED_NAMES:
                continue
            # Bao ve tuyet doi: bo qua toan bo build/media/broll/.
            try:
                rel = f.relative_to(media_dir)
            except ValueError:
                continue
            if rel.parts and rel.parts[0] == "broll":
                continue
            # Chi xoa file khong nam trong tap dang dung.
            if f.name not in used:
                to_delete.append((f, f.stat().st_size))
    else:
        print("  khong co build/media/ — bo qua buoc media", file=sys.stderr)

    # 3. export/: chi giu ban preview mp4 moi nhat + render report.
    export_dir = proj / "export"
    if export_dir.is_dir():
        previews = sorted(
            (f for f in export_dir.glob("*.mp4")),
            key=lambda p: p.stat().st_mtime,
        )
        for f in previews[:-1]:  # giu ban moi nhat, xoa cac ban cu hon
            to_delete.append((f, f.stat().st_size))
        # Cac file .txt/.md/.json trong export (bao cao) duoc giu.
        for f in export_dir.iterdir():
            if f.is_file() and f.suffix.lower() in MEDIA_EXTS and f not in previews:
                to_delete.append((f, f.stat().st_size))

    total = sum(sz for _, sz in to_delete)
    print(f"\n{'XOA THAT' if apply else 'DRY-RUN (khong xoa)'}: {len(to_delete)} file, {total / 1048576:.1f} MB")
    for f, sz in to_delete:
        rel = f.relative_to(proj)
        print(f"  - {rel}  ({sz / 1048576:.2f} MB)")
        if apply:
            f.unlink(missing_ok=True)

    if apply:
        report = proj / "cleanup_report.txt"
        lines = [
            f"cleanup project {args.project_id}: xoa {len(to_delete)} file, {total / 1048576:.1f} MB",
            "",
        ] + [f"- {f.relative_to(proj)} ({sz / 1048576:.2f} MB)" for f, sz in to_delete]
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nda ghi log xoa vao: {report}")

    if not to_delete:
        print("khong co rac — project da sach.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
