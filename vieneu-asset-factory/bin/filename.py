#!/usr/bin/env python3
"""Single source of truth cho quy tắc đặt tên file media.

Dùng chung cho các script factory: assemble_project.py, tts_batch.py,
render_draft.py, preflight.py, thumbnail.py. App (server/src/privileged.ts)
ĐÃ dùng hợp đồng này từ đợt C1 (01/11/2026): mọi tên media app tạo mới
và duplicateProject đều theo đúng rand6() này, nên render_draft tìm
thấy đúng file (hết clip đen/sai hình do lệch tên).
    python3 filename.py <project_id> img <order>            -> seg_1_483920.jpg
    python3 filename.py <project_id> broll <order> <partIdx> -> broll_seg_1_part_2_771122.jpg
    python3 filename.py <project_id> voice <order>           -> voice_seg_1_483920.wav
    python3 filename.py <project_id> partwav <order> <partIdx> -> parts/part_1_2_771122.wav
"""
import hashlib
import os
import sys
import tempfile
import wave
from pathlib import Path


def rand6(*parts: str) -> str:
    h = hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()
    return "".join(c for c in h if c.isdigit())[:6].ljust(6, "0")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Ghi file kiểu atomic (Giai đoạn 5, 05/11/2026): ghi file tạm cùng
    thư mục rồi os.replace sang tên thật. Crash giữa chừng chỉ để lại
    file tạm (dọn sau), không bao giờ để lại file đích bị cắt nửa chừng.
    File đích cũ còn nguyên vẹn nếu ghi thất bại."""
    path = Path(path)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".tmp-", dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    """Như atomic_write_bytes, cho nội dung text (JSON/SRT/README)."""
    atomic_write_bytes(Path(path), text.encode(encoding))


def wav_ok(path: Path) -> bool:
    """WAV có dùng được cho skip-if-exists không (Giai đoạn 5)?

    Trả về False (phải làm lại, không chấp nhận lặng lẽ) khi: file
    không đọc được header WAV, số frame = 0, samplerate = 0, hoặc kích
    thước file nhỏ hơn phần data mà header khai (file bị cắt/truncate:
    header còn nguyên nhưng data thiếu — wave.open vẫn mở được nên chỉ
    kiểm tra header là không đủ). Ước lượng dùng header WAV chuẩn 44
    byte; file có chunk phụ sẽ lớn hơn ước lượng nên không bị loại oan
    (chỉ loại khi file NHỎ hơn mức tối thiểu, tức chắc chắn thiếu data).
    """
    try:
        p = Path(path)
        if not p.is_file() or p.stat().st_size == 0:
            return False
        with wave.open(str(p), "rb") as w:
            nframes = w.getnframes()
            if nframes <= 0 or w.getframerate() <= 0:
                return False
            min_size = 44 + nframes * w.getnchannels() * w.getsampwidth()
        return p.stat().st_size >= min_size
    except Exception:
        return False


def img_decode_error(path: Path):
    """Ảnh có giải mã được hết hay không (B10, 05/11/2026).

    Trả None nếu giải mã được hết, ngược lại trả thông báo lỗi. Dùng
    chung cho preflight.py (cửa chặn) và gen_images.py (_decodes, A23):
    PIL Image.open + .load() đọc hết dữ liệu — .verify() không đủ vì
    chỉ kiểm header/cấu trúc, file JPEG cắt dở vẫn qua .verify() nhưng
    hỏng khi render. PIL không có sẵn thì trả None (không chặn chỉ vì
    thiếu thư viện; nơi gọi tự fallback kiểm >0 byte).
    """
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        with Image.open(path) as im:
            im.load()
        return None
    except Exception as exc:
        return str(exc)


def check_plan(plan, *, require_voice_text: bool = False):
    """Guard plan dùng chung (Giai đoạn 5, 05/11/2026), nhất quán giữa
    các script pipeline: plan hỏng phải báo rõ thiếu key nào và dừng,
    không crash trần KeyError/IndexError, cũng không coi plan hỏng là
    rỗng một cách lặng lẽ (plan.get("scenes", []) cũ nuốt mất lỗi).

    Kiểm tra: plan là dict; có "scenes" là list; mỗi scene có "id" và
    "order", có "parts" là list; mỗi part có "id"; và khi
    require_voice_text=True thì part phải có "voiceText" dạng str.
    B28 (06/11/2026, lệnh CEO, lựa chọn A): "parts" không được rỗng;
    "order" và scene "id" phải duy nhất trong toàn plan; khi
    require_voice_text=True thì "voiceText" phải là str không rỗng.
    Trả về danh sách scenes. Lỗi -> ValueError liệt kê mọi vấn đề tìm
    thấy (không dừng ở lỗi đầu tiên để người chạy sửa một lượt)."""
    problems = []
    if not isinstance(plan, dict):
        raise ValueError(f"plan không phải dict mà là {type(plan).__name__}")
    scenes = plan.get("scenes")
    if scenes is None:
        problems.append("thiếu key 'scenes'")
        raise ValueError("plan hỏng: " + "; ".join(problems))
    if not isinstance(scenes, list):
        raise ValueError("plan hỏng: 'scenes' không phải list")
    seen_orders, seen_ids = set(), set()
    for si, sc in enumerate(scenes):
        where = f"scenes[{si}]"
        if not isinstance(sc, dict):
            problems.append(f"{where} không phải dict")
            continue
        if "id" not in sc:
            problems.append(f"{where} thiếu key 'id'")
        elif sc["id"] in seen_ids:
            problems.append(f"{where} trùng scene id '{sc['id']}'")
        else:
            seen_ids.add(sc["id"])
        if "order" not in sc:
            problems.append(f"{where} thiếu key 'order'")
        elif sc["order"] in seen_orders:
            problems.append(f"{where} trùng order {sc['order']}")
        else:
            seen_orders.add(sc["order"])
        parts = sc.get("parts")
        if parts is None:
            problems.append(f"{where} thiếu key 'parts'")
            continue
        if not isinstance(parts, list):
            problems.append(f"{where}: 'parts' không phải list")
            continue
        if not parts:
            problems.append(f"{where}: 'parts' rỗng — scene không có part nào")
            continue
        for pi, p in enumerate(parts):
            pwhere = f"{where}.parts[{pi}]"
            if not isinstance(p, dict):
                problems.append(f"{pwhere} không phải dict")
                continue
            if "id" not in p:
                problems.append(f"{pwhere} thiếu key 'id'")
            if require_voice_text and (not isinstance(p.get("voiceText"), str)
                                      or not p.get("voiceText").strip()):
                problems.append(f"{pwhere} thiếu key 'voiceText' (hoặc không phải str, hoặc rỗng)")
    if problems:
        raise ValueError("plan hỏng: " + "; ".join(problems))
    return scenes


def main() -> int:
    pid, kind = sys.argv[1], sys.argv[2]
    if kind == "img":
        o = sys.argv[3]
        print(f"seg_{o}_{rand6(pid, 'img', o)}.jpg")
    elif kind == "broll":
        o, p = sys.argv[3], sys.argv[4]
        print(f"broll_seg_{o}_part_{p}_{rand6(pid, 'broll', o, p)}.jpg")
    elif kind == "voice":
        o = sys.argv[3]
        print(f"voice_seg_{o}_{rand6(pid, 'seg', o)}.wav")
    elif kind == "partwav":
        o, p = sys.argv[3], sys.argv[4]
        print(f"parts/part_{o}_{p}_{rand6(pid, 'part', o, p)}.wav")
    else:
        print(f"unknown kind: {kind}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
