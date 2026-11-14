#!/usr/bin/env python3
"""Don rac trong thu muc company-os (quyet CEO 14/11/2026 — mo rong tu
co che don rac factory). Mac dinh --dry-run (chi bao cao, khong xoa).

Rac o day la file lam viec cua quy trinh San xuat (tim media, render,
chup khung hinh QA) ghi vao company-os/ song song voi thu muc project
trong factory — factory van co du project tuong ung nen day la ban lam
viec thua, khong phai ban duy nhat (da kiem chung 14/11: 38/38 thu muc
topic*-media/frames deu co project factory tuong ung).

CHI XOA 3 mau sau, khong dong vao tai lieu (spec/skill/huong dan/.md/.py/
.json, crons/, media-search/, ...):
  1. Thu muc topic*-media/ va topic*-frames/  (media lam viec theo chu de)
  2. Thu muc qa*_frames/                     (anh khung hinh QA theo chu de)
  3. File TOPIC*.mp4 o goc company-os/       (video nhap/preview da render)
Tuoi: thoi diem sinh thu muc (birth time; fallback file cu nhat) doi voi
thu muc; mtime doi voi file mp4. Qua --days (mac dinh 7) ngay thi xoa.
Video da duyet chi con tren Drive "Video Muse" + mp4 export trong
factory; anh/video lam viec trong company-os khong dung de render lai
(render dung build/media/broll/ trong factory).

CHAN XOA BAN DUY NHAT (sua lo hong 14/11/2026 — quyet CEO 16:23):
chi xoa khi factory co ban goc:
  - File TOPIC*.mp4: chi xoa khi factory export
    projects/topic<NNN>001/export/topic<NNN>001_preview.mp4 TON TAI va
    md5 TRUNG. Neu khong co factory export, hoac md5 khac (ban rieng /
    ban render moi chua ve factory) thi GIU LAI, bao cao ly do.
  - Thu muc topic*/qa*: chi xoa khi factory project topic<NNN>001
    ton tai. Neu khong co project thi GIU LAI, bao cao ly do.
Ban duy nhat (vd TOPIC271 chi co o company-os, TOPIC274 ban 313s
md5 khac factory) khong bao gio bi xoa — phai dong bo/xu ly tay truoc.

Cach dung:
    <factory-venv-python> bin/cleanup_company_os.py [--days N] [--dry-run|--apply]
Mac dinh: --days 7, --dry-run. Them --apply de xoa that; log ghi them
vao company-os/cleanup_company_os_log.txt.
"""
import argparse
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

FACTORY = Path(__file__).resolve().parent.parent
COMPANY_OS = Path.home() / "workspace" / "company-os"
LOG = COMPANY_OS / "cleanup_company_os_log.txt"
TOPIC_RE = re.compile(r"^topic\d+-(media|frames)$")
QA_RE = re.compile(r"^qa\d+_frames$")
NUM_RE = re.compile(r"^topic(\d+)-|^qa(\d+)_|^TOPIC(\d+)")


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


def _size(p: Path) -> int:
    if p.is_file():
        return p.stat().st_size
    total = 0
    for f in p.rglob("*"):
        if f.is_file():
            try:
                total += f.stat().st_size
            except OSError:
                pass
    return total


def _count(p: Path) -> int:
    if p.is_file():
        return 1
    return sum(1 for f in p.rglob("*") if f.is_file())


def _md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _topic_num(name: str) -> str | None:
    """So chu de (NNN) tu ten muc/file, vd topic274-media -> '274'."""
    m = NUM_RE.match(name)
    if not m:
        return None
    return next((g for g in m.groups() if g), None)


def _factory_export(num: str) -> Path:
    return FACTORY / "projects" / f"topic{num}001" / "export" / f"topic{num}001_preview.mp4"


def _factory_project(num: str) -> Path:
    return FACTORY / "projects" / f"topic{num}001"


def main() -> int:
    ap = argparse.ArgumentParser(description="Don rac company-os: thu muc media/QA + mp4 nhap qua N ngay (chan xoa ban duy nhat).")
    ap.add_argument("--days", type=float, default=7, help="nguong tuoi (ngay), mac dinh 7")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="chi bao cao, khong xoa (mac dinh)")
    g.add_argument("--apply", action="store_true", help="xoa that cac muc qua han")
    args = ap.parse_args()
    apply = args.apply

    if not COMPANY_OS.is_dir():
        print(f"khong thay thu muc company-os: {COMPANY_OS}", file=sys.stderr)
        return 1

    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(days=args.days)

    def age_days(ts: float) -> float:
        return (now - datetime.datetime.fromtimestamp(ts)).total_seconds() / 86400

    to_delete: list[tuple[str, str, float, int, int]] = []  # (ten, loai, tuoi, so file, byte)
    kept: list[tuple[str, str, float, int, int]] = []
    kept_unique: list[tuple[str, str, float, int, int, str]] = []  # + ly do giu
    for entry in sorted(COMPANY_OS.iterdir()):
        kind = None
        if entry.is_dir() and (TOPIC_RE.match(entry.name) or QA_RE.match(entry.name)):
            kind = "media" if TOPIC_RE.match(entry.name) else "qa-frames"
            born = _birth_time(entry)
        elif entry.is_file() and entry.name.startswith("TOPIC") and entry.suffix == ".mp4":
            kind = "mp4-nhap"
            born = entry.stat().st_mtime
        else:
            continue
        age = age_days(born)
        rec = (entry.name, kind, age, _count(entry), _size(entry))
        if born >= cutoff.timestamp():
            kept.append(rec)
            continue
        # Qua han: kiem tra chan xoa ban duy nhat truoc khi xoa.
        num = _topic_num(entry.name)
        reason = None
        if kind == "mp4-nhap":
            if num is None:
                reason = "khong doc duoc so chu de"
            else:
                fac = _factory_export(num)
                if not fac.is_file():
                    reason = "khong co factory export (ban duy nhat)"
                elif _md5(entry) != _md5(fac):
                    reason = "md5 khac factory export (ban rieng)"
        else:
            if num is None:
                reason = "khong doc duoc so chu de"
            elif not _factory_project(num).is_dir():
                reason = "khong co factory project (ban duy nhat)"
        if reason:
            kept_unique.append((*rec, reason))
        else:
            to_delete.append(rec)

    total_files = sum(r[3] for r in to_delete)
    total_mb = sum(r[4] for r in to_delete) / 1048576
    print(f"nguong: >{args.days} ngay (thu muc: thoi diem sinh; mp4: ngay sua cuoi)")
    print(f"{'XOA THAT' if apply else 'DRY-RUN (khong xoa)'}: {len(to_delete)} muc, {total_files} file, {total_mb:.1f} MB | giu lai {len(kept)} muc trong han | giu lai {len(kept_unique)} muc BAN DUY NHAT")

    by_kind: dict[str, list] = {}
    for rec in to_delete:
        by_kind.setdefault(rec[1], []).append(rec)
    for kind in ("media", "qa-frames", "mp4-nhap"):
        rows = by_kind.get(kind, [])
        if not rows:
            continue
        mb = sum(r[4] for r in rows) / 1048576
        print(f"\n[{kind}] {len(rows)} muc, {sum(r[3] for r in rows)} file, {mb:.1f} MB:")
        for name, _, age, n, sz in sorted(rows, key=lambda r: -r[4])[:12]:
            print(f"  - {name}: {age:.0f} ngay, {n} file, {sz / 1048576:.1f} MB")
        if len(rows) > 12:
            print(f"    ... va {len(rows) - 12} muc nua")
        if apply:
            for name, _, _, _, _ in rows:
                p = COMPANY_OS / name
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    p.unlink(missing_ok=True)

    if kept_unique:
        mb = sum(r[4] for r in kept_unique) / 1048576
        print(f"\n[GIU LAI — BAN DUY NHAT, KHONG XOA] {len(kept_unique)} muc, {sum(r[3] for r in kept_unique)} file, {mb:.1f} MB:")
        for name, kind, age, n, sz, reason in sorted(kept_unique, key=lambda r: -r[4]):
            print(f"  - {name} ({kind}): {age:.1f} ngay, {sz / 1048576:.1f} MB — {reason}")

    if kept:
        mb = sum(r[4] for r in kept) / 1048576
        print(f"\n[GIU LAI — TRONG HAN] {len(kept)} muc, {sum(r[3] for r in kept)} file, {mb:.1f} MB (trong {args.days} ngay):")
        for name, kind, age, n, sz in sorted(kept, key=lambda r: r[2])[:10]:
            print(f"  - {name} ({kind}): {age:.1f} ngay, {sz / 1048576:.1f} MB")

    if apply:
        lines = [
            f"{now.strftime('%Y-%m-%d %H:%M')} — cleanup_company_os --days {args.days}: xoa {len(to_delete)} muc, {total_files} file, {total_mb:.1f} MB; giu {len(kept_unique)} ban duy nhat",
        ] + [f"  - {n} ({k}, {a:.0f} ngay, {s / 1048576:.1f} MB)" for n, k, a, _, s in to_delete]
        lines += [f"  GIU (ban duy nhat): {n} ({k}) — {r}" for n, k, _, _, _, r in kept_unique]
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"\nda ghi log xoa vao: {LOG}")
    if not to_delete:
        print("khong co muc qua han — khong xoa gi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
