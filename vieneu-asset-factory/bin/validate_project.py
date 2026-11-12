#!/usr/bin/env python3
"""Validator gói Studio export (project.json + timeline.json + subtitles/*.srt
+ googleFlow), KHÔNG phải preflight cho project factory.

Project factory (broll-plan.json + tts.json + karaoke.json) dùng
bin/preflight.py. Dùng script này cho project factory sẽ FAIL sai
("thiếu project.json") vì factory không sinh project.json — đó là sai
công cụ, không phải project hỏng (đợt D7, 01/11/2026).

PHẠM VI: chỉ hợp lệ SAU assemble (assemble_project.py đã sinh
project.json/timeline.json/subtitles/*.srt/googleFlow/config.json).
Chạy trước assemble là sai công cụ, không phải project hỏng.

Chạy: python3 validate_project.py <project_id> [--zip]
  mặc định kiểm tra thư mục projects/<id>/build ; --zip kiểm tra file export/<id>.zip
Trả về exit 0 nếu không có lỗi; in toàn bộ lỗi (không dừng sớm ở cổng
nào) và in riêng cảnh báo (không tính vào exit code).

ĐỊNH NGHĨA CHẶN / CẢNH BÁO — CHỐT Giai đoạn 4, 05/11/2026, NHẤT QUÁN
với preflight.py (cả hai: exit 1 khi và chỉ khi có lỗi chặn; cảnh báo
không tính vào exit code):
- CHẶN (exit 1): thiếu project.json / timeline.json / subtitles
  (*.srt); project.json thiếu key, id không khớp thư mục, created_at
  sai định dạng, script thiếu key; timeline version != 2.0, projectId
  không khớp, không có segments, segment thiếu key, chứa key sẽ bị
  strip, URL media không tương đối hoặc file không tồn tại, startSec
  không khớp tiling, endSec không khớp tổng parts, voiceText nối lại
  không khớp text (lossless fail), order không tăng dần duy nhất;
  templateId lạ, thiếu input bắt buộc, input vượt maxLength, sfx id lạ,
  tên file b-roll sai pattern; SRT không parse được cue, cue start >=
  end hoặc không đơn điệu tăng; googleFlow item thiếu key; ZIP thiếu
  file hoặc không chứa thư mục <pid>/ ở root.
- CẢNH BÁO (exit 0): duy nhất hiện tại là JSON chứa escape \\uXXXX
  (JSON vẫn hợp lệ, chỉ khuyên viết ensure_ascii=False cho dễ đọc).
  Mọi lỗi khác trong danh sách chặn đều là lỗi, không có mức "cảnh báo
  nhưng vẫn FAIL" — khác với preflight ở chỗ validate không có cảnh báo
  về nội dung (độ dài, SFX, BGM): những thứ đó preflight đã kiểm tra
  trước render, validate chỉ kiểm tra tương thích schema 2.0.
"""
import json
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import meta_check  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)

ERRORS = []
WARNINGS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def norm(s):
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"\s+", " ", s).strip(" .,;!?\"'")


def check_raw_no_escape(path: Path):
    raw = path.read_bytes()
    try:
        raw.decode("utf-8")
    except UnicodeDecodeError:
        err(f"{path.name}: không phải UTF-8 hợp lệ")
    # Đợt D7: escape \uXXXX là JSON hợp lệ (json.dumps mặc định dùng
    # ensure_ascii=True) nên chỉ cảnh báo, không còn là lỗi. Trước đây
    # FAIL cả file JSON hợp lệ chỉ vì encode ASCII.
    if b"\\u" in raw:
        warn(f"{path.name}: chứa escape \\uXXXX (JSON vẫn hợp lệ, nên "
             f"viết ensure_ascii=False cho dễ đọc)")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: validate_project.py <project_id> [--zip]", file=sys.stderr)
        return 2
    pid = sys.argv[1]
    use_zip = "--zip" in sys.argv
    proj = FACTORY / "projects" / pid

    tmp = None
    if use_zip:
        zpath = proj / "export" / f"{pid}.zip"
        if not zpath.exists():
            print(f"FAIL: thiếu {zpath}")
            return 1
        tmp = proj / "_validate_tmp"
        if tmp.exists():
            import shutil
            shutil.rmtree(tmp)
        with zipfile.ZipFile(zpath) as z:
            z.extractall(tmp)
        root = tmp / pid
    else:
        root = proj / "build"

    try:
        if use_zip and not root.exists():
            print(f"FAIL: zip không chứa thư mục {pid}/ ở root")
            return 1

        # ---- project.json ----
        # Đợt D7: không dừng sớm — thiếu project.json thì vẫn kiểm tiếp
        # timeline/subtitles/googleFlow để in toàn bộ lỗi một lần.
        pj_path = root / "project.json"
        if not pj_path.exists():
            err("thiếu project.json")
        else:
            check_raw_no_escape(pj_path)
            pj = json.loads(pj_path.read_text(encoding="utf-8"))
            for k in ("version", "id", "name", "created_at", "updated_at", "script", "settings", "summary"):
                if k not in pj:
                    err(f"project.json thiếu key: {k}")
            if pj.get("id") != pid:
                err(f"project.json id={pj.get('id')} != tên thư mục {pid}")
            if not re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", str(pj.get("created_at", ""))):
                err("project.json created_at sai định dạng YYYY-MM-DD HH:MM:SS")
            sc = pj.get("script", {})
            for k in ("topic", "content", "sentences"):
                if k not in sc:
                    err(f"project.json script thiếu key: {k}")

        # ---- timeline.json ----
        tl = None
        tl_path = root / "timeline.json"
        if not tl_path.exists():
            err("thiếu timeline.json")
        else:
            check_raw_no_escape(tl_path)
            tl = json.loads(tl_path.read_text(encoding="utf-8"))
            if tl.get("version") != "2.0":
                err("timeline.json version != 2.0")
            if tl.get("projectId") != pid:
                err("timeline.json projectId không khớp")
            segs = tl.get("segments", [])
            if not segs:
                err("timeline.json không có segments")

        # catalog template để validate broll
        catalog = {}
        for mf in (FACTORY / "templates").glob("*/meta.json"):
            m = json.loads(mf.read_text(encoding="utf-8"))
            if m.get("status", "active") == "active":
                catalog[m["id"]] = m
        sfx_ids = {p.stem for p in (FACTORY / "sfx").glob("*.mp3")}

        STRIP_KEYS = {"subCues", "rawSubCues", "karaokeTokens", "rawText", "imagePreviewUrl",
                      "imageFilename", "suggestedPrompt", "audioUrl", "note", "title"}
        if tl is None:
            segs = []
        orders = []
        for s in segs:
            for k in ("id", "order", "text", "startSec", "endSec", "duration", "voiceParts"):
                if k not in s:
                    err(f"segment {s.get('order')}: thiếu key {k}")
            orders.append(s.get("order"))
            bad = STRIP_KEYS & set(s.keys())
            if bad:
                err(f"segment {s.get('order')}: chứa key sẽ bị strip {bad}")
            # URL media tồn tại?
            for key in ("image",):
                u = s.get(key)
                if u:
                    if not u.startswith(f"/projects/{pid}/"):
                        err(f"segment {s['order']}: URL không tương đối: {u}")
                    elif not (root / u.split(f"/projects/{pid}/", 1)[1]).exists():
                        err(f"segment {s['order']}: file không tồn tại: {u}")
            # tiling voice parts
            t = s.get("startSec", 0)
            for p in s.get("voiceParts", []):
                if abs(p.get("startSec", -1) - t) > 0.05:
                    err(f"part {p.get('id')}: startSec không khớp tiling")
                t = p.get("endSec", t)
                # lossless
                br = p.get("broll") or {}
                tid = br.get("templateId")
                if tid and tid not in catalog:
                    err(f"part {p.get('id')}: templateId lạ: {tid}")
                if tid:
                    meta = catalog[tid]
                    inputs = br.get("inputs", {})
                    for ik, idef in meta.get("inputs", {}).items():
                        if idef.get("required") and not inputs.get(ik):
                            err(f"part {p.get('id')}: thiếu input bắt buộc '{ik}' của {tid}")
                        for _m in meta_check.check_input_value(ik, idef, inputs.get(ik)):
                            err(f"part {p.get('id')}: {_m}")
                    sfx = br.get("sfx")
                    if sfx and sfx.get("id") not in sfx_ids:
                        err(f"part {p.get('id')}: sfx id lạ: {sfx.get('id')}")
                fn = (br.get("filename") or "")
                if fn and not re.match(r"^broll_seg_\d+_part_\d+_\d{6}\.(jpg|png|webp|mp4)$", fn):
                    err(f"part {p.get('id')}: tên file b-roll sai pattern: {fn}")
            joined = norm(" ".join(p.get("voiceText", "") for p in s.get("voiceParts", [])))
            if s.get("voiceParts") and joined != norm(s.get("text", "")):
                err(f"segment {s['order']}: voiceText nối lại không khớp text (lossless fail)")
            if abs(s.get("endSec", 0) - t) > 0.1:
                err(f"segment {s['order']}: endSec không khớp tổng parts")
        # B25 (06/11/2026, lệnh CEO, lựa chọn A): order chỉ cần tăng dần và
        # duy nhất — sau khi cắt scene, order có thể khuyết (vd 1-9,11,12,
        # tiền lệ TOPIC-040); render đã chấp nhận từ trước nên validate không
        # bắt liên tục 1..N nữa.
        if orders != sorted(orders) or len(set(orders)) != len(orders):
            err(f"segment order không tăng dần duy nhất: {orders}")

        # ---- subtitles ----
        for name in ("synced_cues.srt", "sentences.srt"):
            sp = root / "subtitles" / name
            if not sp.exists():
                err(f"thiếu subtitles/{name}")
                continue
            txt = sp.read_text(encoding="utf-8-sig")
            cues = re.findall(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", txt)
            if not cues:
                err(f"{name}: không parse được cue nào")
            prev = 0.0
            for a, b in cues:
                def to_s(x):
                    h, m, rest = x.split(":")
                    s, ms = rest.split(",")
                    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
                if to_s(a) >= to_s(b):
                    err(f"{name}: cue có start >= end")
                if to_s(a) < prev - 0.01:
                    err(f"{name}: cue không đơn điệu tăng")
                prev = to_s(a)

        # ---- googleFlow ----
        gf = root / "googleFlow" / "config.json"
        if gf.exists():
            g = json.loads(gf.read_text(encoding="utf-8"))
            for it in g.get("items", []):
                for k in ("prompt", "segIdx", "taskType", "targetFilename", "subDir", "projectId"):
                    if k not in it:
                        err(f"googleFlow item thiếu key {k}")

        return finish()
    finally:
        # B44 (06/11/2026, lệnh CEO, lựa chọn A): dọn thư mục tạm sau khi
        # xong — kể cả khi return sớm hay lỗi; trước đây _validate_tmp ở
        # lại trong project sau mỗi lần validate --zip.
        if tmp is not None and tmp.exists():
            import shutil
            shutil.rmtree(tmp)


def finish() -> int:
    if WARNINGS:
        print(f"(cảnh báo, không tính vào exit code: {len(WARNINGS)}):")
        for w in WARNINGS:
            print(" -", w)
    if ERRORS:
        print(f"FAIL ({len(ERRORS)} lỗi):")
        for e in ERRORS:
            print(" -", e)
        return 1
    print("VALIDATE-OK: project tương thích với VieNeu Studio local")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
