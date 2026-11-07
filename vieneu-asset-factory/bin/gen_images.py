#!/usr/bin/env python3
"""Tạo ảnh cảnh cho Asset Factory, hai đường song song, cùng chuẩn tên file.

Usage: python3 gen_images.py jobs.json

Mỗi job là một dict, app (artifact vieneu-asset-factory, action
generateImages) xây jobs từ broll-plan.json của project:

1. Ảnh AI (đường cũ, không đổi):
   {"prompt": "...", "out": "/path.jpg", "orientation": "vertical"}
   -> media-generation CLI (4 luồng song song), ffmpeg chuyển về JPG đúng tên.

2. Nền cảnh dạng LƯỚI XANH RÊU, KHÔNG CHỮ (sửa 05/11/2026 theo lệnh CEO,
   thay thế hoàn toàn card chữ cũ):
   {"card_pid": "<pid>", "card_order": <order>, "out": "/path.jpg"}
   -> bin/render_scene_card.py <pid> <order> <out>, dùng factory venv.
   Đường này cho scene KHÔNG có sceneImagePrompt/mediaPrompt: output là
   nền xanh rêu #1C372A kẻ ô vuông, không thêm bất kỳ chữ nào. Nó KHÔNG
   phải ảnh thật hay ảnh AI, và không thay thế ảnh.
   Trước đây app chỉ xây job AI nên plan kiểu này trả jobCount 0 —
   không phải plan thiếu ảnh, mà là gen_images chưa biết đường card.
   App phải xây cả hai loại job, hoặc gọi render_scene_card trực tiếp
   cho scene không có prompt AI; gen_images ở đây chỉ là điểm vào chung.

Tính chất quan trọng cho app (timeout 30s của action):
- Job nào đã có file out hợp lệ thì BỎ QUA, trừ khi job khai
  "force": true. "Hợp lệ" nghĩa là file tồn tại, >0 byte VÀ giải mã
  được hết bằng PIL (A23, 05/11/2026): file bị cắt dở/ghi hỏng có kích
  thước nhưng không mở được thì coi như chưa có và tạo lại, không bỏ
  qua lặng lẽ. Lần chạy thứ hai sau timeout vì vậy chỉ làm tiếp phần
  chưa xong, không chạy lại toàn bộ và không phá ảnh đã tạo.
- Tên file out LUÔN lấy từ bin/filename.py (rand6), không tự đặt tên
  ngẫu nhiên — render_draft/preflight/thumbnail đều tra cứu theo tên này,
  tên sai là ra MP4 nền đen.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from filename import atomic_write_text, img_decode_error, plan_lock  # noqa: E402

try:
    from PIL import Image as _PILImage
except Exception:  # PIL chưa cài: fallback kiểm tra >0 byte, không crash batch
    _PILImage = None

_PIL_WARNED = False

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)

VENV_PY = FACTORY / ".venv" / "bin" / "python"


def _decodes(path: Path) -> bool:
    """Kiểm tra ảnh giải mã được hết hay không (A23, 05/11/2026).

    Dùng Image.open + .load() để đọc hết dữ liệu ảnh: .verify() không
    đủ vì nó chỉ kiểm tra header/cấu trúc mà không giải mã scan data,
    nên file JPEG bị cắt dở vẫn qua .verify() nhưng hỏng khi render.
    PIL mặc định không chấp nhận ảnh cắt (LOAD_TRUNCATED_IMAGES=False)
    nên .load() trên file cắt dở sẽ raise.
    PIL không có sẵn thì fallback về kiểm tra >0 byte cũ và chỉ cảnh
    báo một lần — không bao giờ crash batch vì thiếu thư viện.
    Logic giải mã dùng chung ở filename.img_decode_error (B10)."""
    global _PIL_WARNED
    if _PILImage is None:
        if not _PIL_WARNED:
            _PIL_WARNED = True
            print("IMG-WARN PIL không có sẵn — chỉ kiểm tra file >0 byte",
                  file=sys.stderr, flush=True)
        return True
    err = img_decode_error(path)
    if err is not None:
        print(f"IMG-BROKEN {path}: {err} — tạo lại", flush=True)
        return False
    return True


def _exists_ok(path: str) -> bool:
    """File out có dùng được để bỏ qua job không (A23, 05/11/2026).

    Tồn tại + >0 byte + (với jpg/png/webp — các định dạng script này
    tạo ra) giải mã được hết. File thiếu/rỗng/hỏng đều trả False để
    job chạy lại."""
    try:
        p = Path(path)
        if not p.exists() or p.stat().st_size == 0:
            return False
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            return _decodes(p)
        return True
    except Exception:
        return False


def _validate_job(job, idx: int):
    """Validate schema của 1 job, trả về thông báo lỗi hoặc None.

    Giai đoạn 5: job thiếu key phải thành lỗi per-job, không được thành
    KeyError/IndexError giết cả batch. Mọi job đều cần "out"; job card
    cần "card_pid" + "card_order"; job AI cần "prompt" (chuỗi không rỗng).
    """
    if not isinstance(job, dict):
        return f"job {idx} không phải dict"
    if not job.get("out"):
        return f"job {idx} thiếu key 'out'"
    if job.get("card_pid") is not None:
        if "card_order" not in job:
            return f"job {idx} (card, out={job['out']}) thiếu key 'card_order'"
        # R4-39 (07/11/2026, DEC-047): card_order phải đổi được thành
        # số — int() ở cuối vòng lặp sẽ crash ValueError nếu không
        # (vd "hai"), sau khi job đã chạy; chặn ở đây thì job này lỗi
        # per-job rõ ràng, các job khác vẫn chạy.
        try:
            int(job["card_order"])
        except (TypeError, ValueError):
            return (f"job {idx} (card, out={job['out']}) card_order "
                    f"{job['card_order']!r} không phải số")
        return None
    if not isinstance(job.get("prompt"), str) or not job["prompt"].strip():
        return f"job {idx} (AI, out={job['out']}) thiếu key 'prompt' (hoặc rỗng)"
    return None


def one(item):
    """Chạy 1 job. Trả về (out, skipped, error, card_flag): error None
    nghĩa là thành công/skip; error khác None nghĩa là job này lỗi nhưng
    batch vẫn tiếp tục các job khác (không raise ra ngoài). card_flag
    chỉ có ý nghĩa với job card: "grid" = render_scene_card in GRID-OK
    (nền rêu thật), "bg" = in BG-IMAGE-OK (ảnh thật làm nền qua
    cardImage), "unknown" = stdout không chứa mã nào (fail-closed),
    None = không phải job card / job skip / job lỗi."""
    idx, job = item
    err = _validate_job(job, idx)
    if err is not None:
        return (job.get("out") if isinstance(job, dict) else "?", False, err, None)
    out = job["out"]
    card_flag = None
    try:
        if not job.get("force") and _exists_ok(out):
            return out, True, None, None
        if job.get("card_pid") is not None:
            # Nền xanh rêu kẻ ô, không chữ, không qua media-generation.
            cmd = [str(VENV_PY), str(FACTORY / "bin" / "render_scene_card.py"),
                   str(job["card_pid"]), str(job["card_order"]), out]
            # R4-25 (07/11/2026, DEC-033 phương án A): capture stdout để
            # phân biệt ảnh thật làm nền (BG-IMAGE-OK) với nền rêu thật
            # (GRID-OK) — trước đây không đọc stdout nên gắn cờ cho mọi
            # job card, kể cả scene có ảnh thật qua cardImage.
            p = subprocess.run(cmd, check=True, timeout=300,
                               capture_output=True, text=True)
            if p.stdout:
                print(p.stdout.strip(), flush=True)
            if p.stderr:
                print(p.stderr.strip(), file=sys.stderr, flush=True)
            _so = p.stdout or ""
            if "BG-IMAGE-OK" in _so:
                card_flag = "bg"
            elif "GRID-OK" in _so:
                card_flag = "grid"
            else:
                # Fail-closed: stdout lạ/trống — gắn cờ + cảnh báo rõ để
                # Production/QA kiểm tra tay (cổng B7 chặn scene thiếu ảnh).
                card_flag = "unknown"
                print(f"IMG-FLAG-WARN card {job['card_pid']} order {job['card_order']}: "
                      f"stdout không chứa BG-IMAGE-OK/GRID-OK — gắn cờ isMossGrid "
                      f"fail-closed (stdout: {_so.strip()[:300]!r})",
                      file=sys.stderr, flush=True)
        else:
            cmd = ["/opt/hatch/bin/media-generation", "--media-subagent-output-type", "image"]
            if job.get("orientation"):
                # vertical = dọc 9:16, landscape = ngang 16:9, square = vuông
                cmd += ["--orientation", job["orientation"]]
            cmd += ["--conversation-json", json.dumps([{"text": job["prompt"]}], ensure_ascii=False)]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            # Giai đoạn 5: kiểm tra exit code TRƯỚC khi parse JSON —
            # trước đây parse stdout của tiến trình lỗi rồi crash cả batch.
            if p.returncode != 0:
                return out, False, (f"media-generation exit {p.returncode}: "
                                    f"{(p.stderr or p.stdout or '').strip()[-500:]}"), None
            try:
                d = json.loads(p.stdout)
            except Exception as exc:
                return out, False, f"media-generation trả stdout không phải JSON: {exc}", None
            paths = d.get("media_paths") if isinstance(d, dict) else None
            if not paths:
                return out, False, "media-generation không trả media_paths", None
            src = paths[0]
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, out],
                           check=True, timeout=120)
        if not _exists_ok(out):
            return out, False, "chạy xong nhưng file out không tồn tại, rỗng hoặc không giải mã được", None
        return out, False, None, card_flag
    except Exception as exc:
        # Giai đoạn 5: lỗi per-job — trả về để main ghi IMG-FAIL và
        # chạy tiếp job khác, không crash cả batch.
        return out, False, f"{type(exc).__name__}: {exc}", None



def _mark_moss_grid(rendered_cards: list[tuple[str, int]]) -> None:
    """A21 (05/11/2026): job card nào render xong nền rêu thật thì ghi cờ
    isMossGrid: true vào đúng scene đó trong broll-plan.json — cờ là căn cứ
    để app/QA nhận ra nền rêu, không đoán theo tên file. Chạy một lần sau
    batch; lỗi ghi plan chỉ cảnh báo ra stderr, không làm fail batch (ảnh
    đã render xong). Job AI không động vào cờ ở đây — app xóa cờ khi xây
    job AI (projects.ts buildGenImageJobs)."""
    try:
        for pid in sorted({pid for pid, _ in rendered_cards}):
            orders = {o for p, o in rendered_cards if p == pid}
            plan_path = FACTORY / "projects" / pid / "broll-plan.json"
            # R4-49 (08/11/2026, DEC-059 A): đọc–sửa–ghi cờ dưới khóa chung
            # trên đĩa — trước đây ngoài khóa, savePlan đúng lúc này là đè
            # mất cờ (khóa promise trong app Node không bao được Python).
            with plan_lock(plan_path, holder="gen_images._mark_moss_grid"):
                plan = json.loads(plan_path.read_text(encoding="utf-8"))
                changed = False
                for sc in plan.get("scenes", []):
                    if sc.get("order") in orders and not sc.get("isMossGrid"):
                        sc["isMossGrid"] = True
                        changed = True
                if changed:
                    atomic_write_text(plan_path, json.dumps(plan, ensure_ascii=False, indent=2))
                    print(f"IMG-FLAG {pid}: đánh dấu isMossGrid cho cảnh {sorted(orders)}", flush=True)
    except Exception as exc:
        print(f"IMG-FLAG-WARN không ghi được cờ isMossGrid: {exc}", file=sys.stderr, flush=True)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: gen_images.py <jobs.json>", file=sys.stderr)
        return 2
    try:
        jobs = json.load(open(sys.argv[1], encoding="utf-8"))
    except Exception as exc:
        print(f"IMG-ERROR không đọc được jobs file: {exc}", file=sys.stderr)
        return 1
    if not isinstance(jobs, list):
        print("IMG-ERROR jobs file hỏng: cấp cao phải là list", file=sys.stderr)
        return 1
    n_failed = 0
    rendered_cards: list[tuple[str, int]] = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        for n, (f, skipped, err, card_flag) in enumerate(
                ex.map(one, list(enumerate(jobs))), start=1):
            job = jobs[n - 1] if 0 < n <= len(jobs) else {}
            if err is not None:
                n_failed += 1
                print(f"IMG-FAIL {n}/{len(jobs)} {f}: {err}", flush=True)
            else:
                tag = "IMG-SKIP" if skipped else "IMG-OK"
                print(f"{tag} {n}/{len(jobs)} {f}", flush=True)
                # A21 (05/11/2026): chỉ job card nào render xong THẬT (không
                # skip) mới được ghi cờ — job bị skip vì file đã có thì cờ
                # giữ nguyên như trong plan.
                # R4-25 (07/11/2026, DEC-033 phương án A): chỉ gắn cờ khi
                # render_scene_card in GRID-OK (nền rêu thật) hoặc stdout
                # không rõ mã (fail-closed, "unknown"); BG-IMAGE-OK = ảnh
                # thật làm nền qua cardImage → KHÔNG gắn cờ.
                if (not skipped and isinstance(job, dict)
                        and job.get("card_pid") is not None
                        and card_flag in ("grid", "unknown")):
                    rendered_cards.append((str(job["card_pid"]), int(job["card_order"])))
    if rendered_cards:
        _mark_moss_grid(rendered_cards)
    # Fail-closed ở mức batch: có job lỗi -> exit 1 (để caller biết mà
    # chạy lại chỉ các job lỗi — job đã xong được skip nhờ _exists_ok),
    # nhưng các job khác vẫn đã chạy xong trong lần này.
    return 1 if n_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
