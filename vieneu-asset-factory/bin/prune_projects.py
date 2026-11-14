#!/usr/bin/env python3
"""Xoa tu dong thu muc project qua 7 ngay (quyet CEO 14/11/2026).

Quy tac (CEO 14/11/2026): thu muc project co THOI DIEM SINH (birth time
cua thu muc) qua 7 ngay thi xoa — khong tinh tu ngay sua cuoi hay ngay
xuat video, vi 2 moc do de lech (vd lan don rac vua roi ghi them file
vao moi project nen mtime moi nhat deu la hom nay).
  - Tuoi = hom nay - birth time cua thu muc project (stat %W).
    Neu he thong khong tra duoc birth time thi dung file cu nhat
    trong project lam dai dien (da kiem chung: birth == file cu nhat
    o ca 3 project mau 033001/041001/373001).
  - Xoa CA THU MUC (mp4 da xuat, kich ban, plan, media, audio) — khong
    khoi phuc duoc. Video da duyet chi con song tren Drive "Video Muse"
    (QA da upload). Khong render lai hay doi chieu duoc sau khi xoa.
  - Chay tu dong bang cron hang ngay (xem company-os/crons/daily/
    prune-projects-0300.md). Khong chay bang tay tru khi can thiet.

Cach dung:
    <factory-venv-python> bin/prune_projects.py [--days N] [--dry-run|--apply]
  Mac dinh: --days 7, --dry-run (chi bao cao, khong xoa). Them --apply
  de xoa that. Khi --apply, ghi log vao prune_log.txt (ghi them, o
  goc factory).
"""
import argparse
import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent
PROJECTS = FACTORY / "projects"
LOG = FACTORY / "prune_log.txt"


def _birth_time(d: Path) -> float:
    """Thoi diem sinh cua thu muc (giay epoch). Fallback: file cu nhat."""
    try:
        out = subprocess.run(
            ["stat", "-c", "%W", str(d)],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        b = float(out)
        if b > 0:
            return b
    except Exception:  # noqa: BLE001
        pass
    files = [f for f in d.rglob("*") if f.is_file()]
    if not files:
        return d.stat().st_mtime
    return min(f.stat().st_mtime for f in files)


def _dir_size(d: Path) -> int:
    total = 0
    for f in d.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except OSError:
                pass
    return total


def main() -> int:
    ap = argparse.ArgumentParser(description="Xoa thu muc project qua N ngay (tinh tu luc sinh).")
    ap.add_argument("--days", type=float, default=7, help="nguong tuoi (ngay), mac dinh 7")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="chi bao cao, khong xoa (mac dinh)")
    g.add_argument("--apply", action="store_true", help="xoa that cac thu muc qua han")
    args = ap.parse_args()
    apply = args.apply

    if not PROJECTS.is_dir():
        print(f"khong thay thu muc projects: {PROJECTS}", file=sys.stderr)
        return 1

    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=args.days)
    to_delete: list[tuple[str, float, int, str]] = []
    kept = 0
    for d in sorted(PROJECTS.iterdir()):
        if not d.is_dir():
            continue
        born = _birth_time(d)
        born_dt = datetime.datetime.fromtimestamp(born)
        age_days = (now - born_dt).total_seconds() / 86400
        if born_dt < cutoff:
            to_delete.append((d.name, age_days, _dir_size(d), born_dt.strftime("%Y-%m-%d %H:%M")))
        else:
            kept += 1

    total_mb = sum(sz for _, _, sz, _ in to_delete) / 1048576
    print(f"nguong: >{args.days} ngay (tinh tu thoi diem sinh thu muc)")
    print(f"{'XOA THAT' if apply else 'DRY-RUN (khong xoa)'}: {len(to_delete)} project, {total_mb:.1f} MB | giu lai {kept} project trong han")
    for name, age, sz, born in to_delete:
        print(f"  - {name}: sinh {born} ({age:.0f} ngay), {sz / 1048576:.1f} MB")
        if apply:
            shutil.rmtree(PROJECTS / name, ignore_errors=True)

    if apply:
        lines = [
            f"{now.strftime('%Y-%m-%d %H:%M')} — prune --days {args.days}: xoa {len(to_delete)} project, {total_mb:.1f} MB",
        ] + [f"  - {n} (sinh {b}, {a:.0f} ngay, {s / 1048576:.1f} MB)" for n, a, s, b in to_delete]
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"\nda ghi log xoa vao: {LOG}")

    if not to_delete:
        print("khong co project qua han — khong xoa gi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
