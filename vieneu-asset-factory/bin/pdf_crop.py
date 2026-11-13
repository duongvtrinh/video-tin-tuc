#!/usr/bin/env python3
"""Anh bang chung tu PDF bai bao (v1 thi diem, quyet CEO 13/11/2026).

DUONG CHINH (tu 13/11/2026, sau lenh CEO loai chup anh man hinh khoi
logic — chup anh chi cho ti le 16:9, la phuong an toi): render NGUYEN
TRANG PDF thanh anh bang `--whole-page`, khong cat.
  pdf_crop.py bai-bao.pdf --page 1 --whole-page --out evidence.png

Luat ti le trang (lenh CEO 13/11/2026, sua cung ngay — 3 truong hop):
  (1) trang co ti le rong/cao trong khoang 3:4 (0,75) den 4:3 (1,33)
  — trang Letter/A4 thuong nam trong khoang nay: dung NGUYEN TRANG
  (`--whole-page`), khong cat, KHONG can canh bao loi gi.
  (2) trang DAI HON 3:4 (rong/cao < 0,75): GIU LAI, cat anh 3:4
  (`--full-page` — cua so tren cung, day chieu rong, vi tua de/sapo
  o dau trang).
  (3) trang RONG HON 4:3 (rong/cao > 1,33): LOAI NGUON NAY, tim nguon
  bao khac (tool thoat 1, in ro ly do).

Che do cat 3:4 (`--full-page` / `--box`): dung cho trang DAI HON 3:4
(giu lai, cat anh 3:4) — `--full-page` lay cua so tren cung (day chieu
rong); `--box` cho cua so tuy chon (vd anh cua bai o giua trang).

Quy tac cat (chi ap cho che do cat, khong ap cho --whole-page):
  - Chi cat anh CUA BAI (hero/anh than bai) hoac tieu de + sapo.
  - TUYET DOI KHONG cat muc tin lien quan / sidebar.
  - Vung cat phai co ti le 3:4 (sai so 1%). Neu box dua vao khong dung
    3:4, tool tu mo rong canh ngan (can giua, khong vuot trang) va bao
    canh bao — khong cat lech ti le.

In ra stdout: kich thuoc trang, ti le trang, box cat (neu co), kich
thuoc output — builder chep pdfPage vao media-log.
Thoat 0 khi xong, 1 khi loi (PDF thieu, trang ngoai pham vi, box sai,
trang ngoai khoang ti le, thieu pdftoppm/PIL).
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

RATIO = 3 / 4  # rong / cao cua cua so hien thi (chi dung cho che do cat)
BAND_LO = 3 / 4   # 0,75 — trang hep nhat chap nhan (3:4 doc)
BAND_HI = 4 / 3   # 1,33 — trang rong nhat chap nhan (4:3 ngang)
BAND_TOL = 0.01   # dung sai ti le


def parse_args():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", help="duong dan file PDF bai bao")
    p.add_argument("--page", type=int, required=True,
                   help="so trang PDF (1-based, trang co tieu de/anh cua bai)")
    p.add_argument("--out", required=True, help="duong dan PNG output")
    p.add_argument("--box", default=None,
                   help="vung cat, phan so cua trang: x0,y0,x1,y1 (0..1, "
                        "goc trai-tren la 0,0). Khong dung 3:4 thi tool tu mo rong.")
    p.add_argument("--full-page", action="store_true",
                   help="cat trang ve 3:4 — trang DAI HON 3:4 thi lay cua so TREN CUNG (day chieu rong, tua de/sapo o dau trang); trang rong hon 3:4 thi lay cua so GIUA (day chieu cao)")
    p.add_argument("--whole-page", action="store_true",
                   help="DUONG CHINH anh bang chung (trang trong khoang 3:4-4:3): render NGUYEN trang thanh anh, khong cat. Trang dai hon 3:4 thi thoat 1 (bao cat 3:4); trang rong hon 4:3 thi thoat 1 (bao loai nguon).")
    p.add_argument("--dpi", type=int, default=200,
                   help="DPI render trang (mac dinh 200; chu vector nen sac o moi DPI)")
    p.add_argument("--size", default="720x960",
                   help="kich thuoc PNG output, dang WxH (mac dinh 720x960)")
    return p.parse_args()


def page_count(pdf: Path) -> int:
    r = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"LOI: khong doc duoc PDF {pdf} (pdfinfo loi): {r.stderr.strip()}")
    for line in r.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    sys.exit(f"LOI: khong lay duoc so trang cua {pdf}")


def page_size_pts(pdf: Path, page: int):
    # pdfinfo -f N -l N in dang "Page    1 size:  612 x 792 pts (letter)".
    import re
    r = subprocess.run(["pdfinfo", "-f", str(page), "-l", str(page), str(pdf)],
                       capture_output=True, text=True)
    m = re.search(r"Page\s+\d+\s+size:\s+([\d.]+)\s+x\s+([\d.]+)\s+pts", r.stdout)
    if m:
        return float(m.group(1)), float(m.group(2))
    sys.exit(f"LOI: khong lay duoc kich thuoc trang {page} cua {pdf}")


def enforce_34(x0, y0, x1, y1):
    """Ep box ve ti le 3:4 bang cach mo rong canh ngan (can giua, kep trong [0,1]).
    Tra (box_moi, da_dieu_chinh: bool)."""
    w, h = x1 - x0, y1 - y0
    if w <= 0 or h <= 0:
        sys.exit("LOI: box cat co canh <= 0")
    cur = w / h
    if abs(cur - RATIO) / RATIO <= 0.01:
        return (x0, y0, x1, y1), False
    if cur > RATIO:
        # qua rong -> mo rong chieu cao
        need_h = w / RATIO
        extra = need_h - h
        y0 = max(0.0, y0 - extra / 2)
        y1 = min(1.0, y1 + extra / 2)
        if y1 - y0 < need_h - 1e-9:  # cham tran tren/duoi -> thu hep chieu rong
            y0, y1 = 0.0, 1.0
            w = RATIO
            cx = (x0 + x1) / 2
            x0, x1 = cx - w / 2, cx + w / 2
    else:
        # qua cao -> mo rong chieu rong
        need_w = h * RATIO
        extra = need_w - w
        x0 = max(0.0, x0 - extra / 2)
        x1 = min(1.0, x1 + extra / 2)
        if x1 - x0 < need_w - 1e-9:
            x0, x1 = 0.0, 1.0
            h = 1.0 / RATIO
            cy = (y0 + y1) / 2
            y0, y1 = cy - h / 2, cy + h / 2
    return (x0, y0, x1, y1), True


def main():
    a = parse_args()
    pdf = Path(a.pdf)
    if not pdf.is_file():
        sys.exit(f"LOI: khong thay file PDF {pdf}")
    if a.page < 1:
        sys.exit("LOI: --page phai >= 1")
    n = page_count(pdf)
    if a.page > n:
        sys.exit(f"LOI: PDF chi co {n} trang, --page {a.page} vuot pham vi")
    _modes = sum([bool(a.box), bool(a.full_page), bool(a.whole_page)])
    if _modes != 1:
        sys.exit("LOI: chi dung dung 1 trong --box, --full-page, --whole-page")

    pw, ph = page_size_pts(pdf, a.page)
    if a.whole_page:
        # Duong chinh anh bang chung: nguyen trang, khong cat.
        # Chi dung trang trong khoang 3:4-4:3. Trang dai hon 3:4 thi GIU
        # LAI, cat 3:4 (bao dung --full-page); trang rong hon 4:3 (qua
        # ngan) thi LOAI NGUON (lenh CEO 13/11: chi bo trang qua ngan).
        _ratio = pw / ph
        if _ratio < BAND_LO - BAND_TOL:
            sys.exit(f"LOI: trang {a.page} ti le rong/cao {_ratio:.3f} dai hon 3:4 — "
                     f"giu lai, cat anh 3:4 bang --full-page (khong dung --whole-page)")
        if _ratio > BAND_HI + BAND_TOL:
            sys.exit(f"LOI: trang {a.page} ti le rong/cao {_ratio:.3f} rong hon 4:3 "
                     f"(trang qua ngan) — loai nguon nay, tim nguon bao khac")
        with tempfile.TemporaryDirectory(prefix="pdf_crop_") as td:
            prefix = str(Path(td) / "p")
            r = subprocess.run(["pdftoppm", "-png", "-r", str(a.dpi),
                                "-f", str(a.page), "-l", str(a.page),
                                str(pdf), prefix],
                               capture_output=True, text=True)
            if r.returncode != 0:
                sys.exit(f"LOI: pdftoppm loi: {r.stderr.strip()}")
            rendered = sorted(Path(td).glob("*.png"))
            if not rendered:
                sys.exit("LOI: pdftoppm khong tao duoc anh trang")
            from PIL import Image
            im = Image.open(rendered[0]).convert("RGB")
            out = Path(a.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            im.save(out, "PNG")
            W, H = im.size
        print(f"PDF: {pdf} ({n} trang, trang {a.page} {pw:.0f}x{ph:.0f} pt, ti le {_ratio:.3f} trong khoang 3:4-4:3)")
        print(f"output: {out} {W}x{H} (nguyen trang, khong cat)")
        return 0
    if a.full_page:
        # Cat trang ve 3:4 (cua so 3:4 lon nhat): trang DAI HON 3:4
        # (rong/cao < 0,75) thi lay cua so TREN CUNG, day chieu rong
        # (tua de/sapo o dau trang); trang rong hon 3:4 thi lay cua so
        # GIUA, day chieu cao. Trang dung 3:4 thi lay toan trang.
        if pw / ph < RATIO - BAND_TOL:
            ch = (pw / RATIO) / ph  # chieu cao box (phan so cua trang)
            box = (0.0, 0.0, 1.0, ch)
        else:
            cw = ph * RATIO / pw  # chieu rong box (phan so cua trang)
            cw = min(cw, 1.0)
            x0 = (1 - cw) / 2
            box = (x0, 0.0, x0 + cw, 1.0)
        adjusted = False
    else:
        try:
            box = tuple(float(v) for v in a.box.split(","))
        except ValueError:
            sys.exit("LOI: --box phai co dang x0,y0,x1,y1 (so thap phan)")
        if len(box) != 4 or not all(0.0 <= v <= 1.0 for v in box):
            sys.exit("LOI: --box phai co 4 so trong [0,1]")
        box, adjusted = enforce_34(*box)
    if adjusted:
        print("CANH BAO: box dua vao khong dung 3:4 — da tu mo rong canh ngan "
              "ve dung ti le (can giua).", file=sys.stderr)
    x0, y0, x1, y1 = box
    try:
        ow, oh = (int(v) for v in a.size.lower().split("x"))
    except ValueError:
        sys.exit("LOI: --size phai co dang WxH, vd 720x960")
    if abs(ow / oh - RATIO) / RATIO > 0.01:
        sys.exit(f"LOI: --size {a.size} khong dung ti le 3:4 (cua so engine la 3:4)")

    with tempfile.TemporaryDirectory(prefix="pdf_crop_") as td:
        prefix = str(Path(td) / "p")
        r = subprocess.run(["pdftoppm", "-png", "-r", str(a.dpi),
                            "-f", str(a.page), "-l", str(a.page),
                            str(pdf), prefix],
                           capture_output=True, text=True)
        if r.returncode != 0:
            sys.exit(f"LOI: pdftoppm loi: {r.stderr.strip()}")
        rendered = sorted(Path(td).glob("*.png"))
        if not rendered:
            sys.exit("LOI: pdftoppm khong tao duoc anh trang")
        from PIL import Image
        im = Image.open(rendered[0]).convert("RGB")
        W, H = im.size
        px = (round(x0 * W), round(y0 * H), round(x1 * W), round(y1 * H))
        crop = im.crop(px)
        crop = crop.resize((ow, oh), Image.LANCZOS)
        out = Path(a.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        crop.save(out, "PNG")

    print(f"PDF: {pdf} ({n} trang, trang {a.page} {pw:.0f}x{ph:.0f} pt)")
    print(f"box cat: x0={x0:.3f} y0={y0:.3f} x1={x1:.3f} y1={y1:.3f} "
          f"(diem: {x0*pw:.0f},{y0*ph:.0f} - {x1*pw:.0f},{y1*ph:.0f})")
    print(f"output: {out} {ow}x{oh} (ti le 3:4)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
