#!/usr/bin/env python3
"""Checklist trước khi xuất project: báo lỗi/thiếu sót cần sửa.

    python3 preflight.py <project_id> [--json]

Kiểm tra: audio từng part, ảnh scene/b-roll, karaoke, template inputs,
BGM đã chọn, đồng bộ thời lượng, file export.

PHẠM VI: chỉ dùng cho project FACTORY (broll-plan.json + tts.json +
karaoke.json), chạy TRƯỚC render/assemble. Project đã assemble
(project.json + timeline.json) thì dùng bin/validate_project.py, KHÔNG
dùng preflight — và ngược lại, validate KHÔNG dùng cho project factory
(chưa assemble sẽ FAIL sai "thiếu project.json").

ĐỊNH NGHĨA CHẶN / CẢNH BÁO — CHỐT Giai đoạn 4, 05/11/2026, NHẤT QUÁN
với validate_project.py (cả hai: exit 1 khi và chỉ khi có lỗi chặn;
cảnh báo không tính vào exit code):
- CHẶN (exit 1): thiếu tts.json; part ID trùng (plan hoặc tts.json);
  part chưa có audio TTS / file audio không tồn tại / duration = 0;
  scene còn part chưa có ảnh/video riêng mà thiếu ảnh cảnh chung (luật CEO
  12/11/2026: cảnh mà mọi part đã có ảnh/video thì KHÔNG cần ảnh cảnh chung);
  ảnh cảnh chung hoặc part s1p1 (part đầu video) là nền trung tính
  (12/11/2026); template không tồn
  tại / meta.json hỏng / inputs không phải dict; thiếu input bắt buộc
  của template; input template vượt maxLength (R4-41/DEC-049 — trước
  đây chỉ cảnh báo); BGM đã chọn nhưng file không tồn tại; SFX đã chọn
  nhưng file không tồn tại (A26, 05/11/2026); tổng thời lượng
  audio = 0; scene (có ảnh cảnh chung) thiếu nguồn media (mediaSource.source
  trống/thiếu) hoặc thiếu nhật ký tìm ảnh (media-log.json không có, hoặc scene
  không có mục nhật ký, hoặc keywordsTried trống/thiếu) — cửa chặn
  ảnh thật, lệnh CEO 05/11/2026 (lựa chọn A20). Scene chỉ có nền
  xanh rêu kẻ ô (không có mediaSource) cũng chặn ở đây, vì nền xanh
  rêu không tính là ảnh. Miễn cửa provenance cho project test kỹ
  thuật (pid bắt đầu bằng "test", vd test001 fixture). 2 part liền kề
  chung 1 file visual — luật kề nhau, lệnh CEO 09/11/2026 (DEC-242,
  Khối 4 Cách 1): chặn trước render; ngoại lệ 2 part ở 2 scene khác
  nhau cùng dùng 1 file nền trung tính (nhận biết theo file thật —
  trùng md5 với file trong thư viện neutral-bg/, hoặc qua media-log
  danh sách parts, classification "trung-tinh"; A1 10/11/2026); mỗi
  scene tối đa 1 part dùng nền trung tính (DEC-244). Mỗi file visual
  nội dung chỉ xuất hiện
  tối đa 2 lần trong toàn video (đếm theo nội dung dhash, Hamming ≤ 10,
  không đếm theo tên file hay md5; trừ ảnh/video trung tính; fill-in tính
  vào trần; bookend tính là 2 lần) — trần xuất hiện, lệnh CEO 09/11/2026
  (DEC-272), chuyển sang dhash theo quyết CEO 13/11/2026 (L8):
  chặn trước render. Ảnh bằng chứng từ PDF bài báo (v1 thí điểm
  13/11/2026, quyết CEO): tối đa 1 part/video; log của part đó
  (classification "chup-man-hinh") phải đủ URL bài + tên báo + ngày
  đăng + trang PDF đã lấy; tỉ lệ ảnh bằng chứng theo 3 trường hợp
  (13/11/2026): trong khoảng 3:4–4:3 thì nguyên trang; dài hơn 3:4
  thì giữ lại, cắt ảnh 3:4; rộng hơn 4:3 (trang quá ngắn) thì loại
  nguồn, tìm nguồn báo khác — chặn trước render. Trần AI ≤ thật theo scene (DEC-244): mỗi scene
  số file AI không được vượt số file thật (đếm theo file khác nhau,
  md5; nền trung tính, ảnh giải thích và ảnh bằng chứng từ PDF bài
  báo (chup-man-hinh) tính vào vế thật; crop chi tiết và fill-in không
  cộng vào vế thật) — C1 rà soát lần 9, quyết CEO 10/11/2026
  (phương án C1-A): chặn trước render. (Ghi chú đối soát 09/11/2026: miễn trừ qua biên scene là phòng thủ — tên file b-roll của mỗi part là duy nhất theo (order, partIdx) nên 2 part khác scene không bao giờ resolve về cùng 1 file; việc dùng lại file nền qua các scene thực chất là copy cùng file nguồn vào 2 tên b-roll khác nhau nên preflight thấy 2 file khác nhau, không vi phạm.) Miễn cho project test như cửa A20.
  R4-57 (08/11/2026, DEC-066 A', port từ validate_project.py — chỉ
  hợp lệ SAU assemble nên không gọi nó trước render): thứ tự scene
  không tăng dần; part startSec không nối tiếp part trước (tiling,
  lệch >0.05s; part đầu phải bắt đầu ở 0s); endSec của scene không
  khớp part cuối (lệch >0.1s); voiceText trong plan nối lại không khớp
  nội dung script.json (lossless fail — sửa plan hoặc script cho khớp;
  thiếu script.json thì bỏ qua kiểm này).
- CẢNH BÁO (exit 0): b-roll video khai nhưng thiếu file mp4 (render
  rơi về ảnh scene); karaoke thiếu hoặc lệch số part / lines=0 diện
  rộng ở part không template / có part fallback timing (WAV hỏng/mất
  hoặc thiếu entry norm_chunks); chưa chọn BGM; video dưới 120s hoặc trên
  180s (Production tự quyết độ dài); 0 SFX hoặc thiếu beat SFX
  hook/móc lại/kết luận; template gợi ý
  SFX nhưng plan chưa có broll.sfx; media-log thiếu danh sách `parts`
  (chỉ cảnh báo khi thư viện neutral-bg/ cũng không đọc được — nếu
  đọc được thì nhận biết nền theo file thật, không cần nhãn); partId cũ
  trong danh sách `parts` của media-log; part khai prompt AI nhưng
  không có file ảnh b-roll; file b-roll video tồn tại nhưng ffprobe
  không thấy video stream.
"""
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import check_plan, img_decode_error, rand6  # noqa: E402
import meta_check  # noqa: E402  (kiểm giá trị input theo meta: maxItems/enum/số/pattern/constraints)


def _norm(s: str) -> str:
    # Chuẩn hóa text để so sánh lossless — khớp validate_project.py
    # norm(): NFC + gộp khoảng trắng + cắt dấu câu ở hai đầu.
    s = unicodedata.normalize("NFC", s)
    return re.sub(r"\s+", " ", s).strip(" .,;!?\"'")

try:
    import PIL.Image  # noqa: F401
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)



def _normalize_stamps(br: dict) -> list:
    """Danh sách dấu của một part (cơ chế danh sách dấu, 06/11/2026):
    broll.stamps = [ {...}, ... ]; broll.stamp đơn cũ -> 1 phần tử."""
    stamps = (br or {}).get("stamps")
    if isinstance(stamps, list):
        return [s for s in stamps if isinstance(s, dict)]
    stamp = (br or {}).get("stamp")
    if isinstance(stamp, dict):
        return [stamp]
    return []


def _part_sfx_ids(br: dict) -> list:
    """ID các SFX của một part: sfx của part + sfx riêng từng dấu."""
    ids = []
    _ps = (br or {}).get("sfx") or {}
    if isinstance(_ps, dict) and _ps.get("id"):
        ids.append(_ps["id"])
    for _st in _normalize_stamps(br):
        _ss = _st.get("sfx") or {}
        if isinstance(_ss, dict) and _ss.get("id"):
            ids.append(_ss["id"])
    return ids


# Stage đầu tiên mỗi ô ảnh hiện trong reveal (theo ngữ nghĩa stage của
# từng template; mặc định 1): photo-duo img2 hiện từ stage 5, photo-duo-h
# img2 từ stage 2. Dùng để kiểm at >= giờ ảnh hiện.
_STAMP_APPEAR_STAGE = {
    ("photo-duo", "img2"): 5,
    ("photo-duo-h", "img2"): 2,
}


def _is_valid_video_broll(path) -> bool:
    """Mp4 b-roll có dùng được không — mirror render_draft.py base_video
    (F1, 09/11/2026, quyết định CEO): file phải tồn tại VÀ ffprobe thấy
    video stream. mediaType KHÔNG phải điều kiện — mediaType chỉ là gợi
    ý để AI tạo ảnh hay video; nếu ảnh/video lấy từ nguồn thực
    (internet/mạng xã hội/stock) thì bỏ qua điều kiện mediaType, resolve
    theo file thật trên đĩa. File hỏng (ffprobe không thấy stream) thì
    render rơi về ảnh (B1) nên preflight cũng rơi về ảnh."""
    if not path.exists():
        return False
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=codec_type",
             "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=30)
        return r.returncode == 0 and "video" in r.stdout
    except Exception:
        return False


def _part_own_file(build, pid, order, pi) -> bool:
    """Part có ảnh/video riêng = có file b-roll riêng của part (mp4 hợp lệ
    hoặc jpg/png/webp). Luật CEO 12/11/2026 (ảnh/video cho cảnh chung)."""
    r6 = rand6(pid, "broll", str(order), str(pi))
    d = build / "media" / "broll"
    mp4 = d / f"broll_seg_{order}_part_{pi}_{r6}.mp4"
    if mp4.exists() and _is_valid_video_broll(mp4):
        return True
    return any((d / f"broll_seg_{order}_part_{pi}_{r6}.{ext}").exists()
               for ext in ("jpg", "png", "webp"))


def _scene_needs_scene_image(build, pid, sc) -> bool:
    """Luật CEO 12/11/2026: cảnh mà MỌI part đều có ảnh/video riêng (kể cả
    cảnh chỉ có 1 part đã có ảnh/video) thì KHÔNG cần ảnh/video cho cảnh
    chung — nó bị part che hoàn toàn. Cảnh còn ít nhất 1 part chưa có
    ảnh/video riêng thì cần ảnh cảnh chung (part đó rơi về ảnh cảnh)."""
    order = sc["order"]
    return not all(_part_own_file(build, pid, order, pi)
                   for pi, _p in enumerate(sc["parts"], start=1))


def main() -> int:
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    errors, warnings = [], []

    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    # B28 (06/11/2026, lệnh CEO, lựa chọn A): guard cấu trúc plan ngay
    # đầu — trước đây plan hỏng (thiếu key, trùng order/id, parts rỗng,
    # voiceText rỗng) crash trần KeyError ở các lần đọc plan["scenes"]/
    # parts trực tiếp bên dưới. Plan hỏng cấu trúc thì dừng ngay, in
    # đúng định dạng báo cáo của preflight (kể cả --json).
    try:
        check_plan(plan, require_voice_text=True)
    except ValueError as exc:
        errors.append(str(exc))
        if "--json" in sys.argv:
            print(json.dumps({"pid": pid, "parts": 0, "duration_sec": 0,
                              "errors": errors, "warnings": warnings,
                              "ok": False}, ensure_ascii=False, indent=1))
        else:
            print(f"=== PREFLIGHT {pid} ===")
            for e in errors:
                print(f"  [LỖI] {e}")
            print("KẾT QUẢ: CHƯA ĐẠT ✗")
        return 1
    tts_path = proj / "tts.json"
    if not tts_path.exists():
        errors.append("CHƯA CHẠY TTS (tts.json không có)")
        tts = {"parts": [], "scenes": []}
    else:
        tts = json.loads(tts_path.read_text(encoding="utf-8"))

    # Part ID trùng: tts_by_id key theo id nên part sau ghi đè part trước
    # lặng lẽ (lỗi topic004). Chặn ngay tại preflight, cùng với tts_batch.
    _seen_ids = set()
    for _p in tts["parts"]:
        if _p["id"] in _seen_ids:
            errors.append(f"Part ID TRÙNG trong tts.json: {_p['id']} — "
                          f"đổi ID cho duy nhất toàn project rồi chạy lại TTS")
        _seen_ids.add(_p["id"])
    _plan_ids = set()
    for _sc in plan["scenes"]:
        for _p in _sc["parts"]:
            if _p["id"] in _plan_ids:
                errors.append(f"Part ID TRÙNG trong plan: {_p['id']} — "
                              f"đổi ID cho duy nhất toàn project rồi chạy lại TTS")
            _plan_ids.add(_p["id"])

    tts_by_id = {p["id"]: p for p in tts["parts"]}

    # R4-57 (08/11/2026, DEC-066 A'): thứ tự scene phải tăng dần —
    # port từ validate_project.py (B25: chỉ cần tăng dần + duy nhất;
    # trùng order đã bị check_plan chặn ở trên nên ở đây chỉ kiểm tăng
    # dần). Render ghép scene theo order nên order lộn xộn là video lộn
    # xộn; order khuyết (vd 1-9,11,12 sau khi cắt scene) vẫn đúng.
    _orders = [sc.get("order") for sc in plan["scenes"]]
    if (all(isinstance(o, int) and not isinstance(o, bool) for o in _orders)
            and _orders != sorted(_orders)):
        errors.append(f"Thứ tự scene không tăng dần: {_orders} — sửa "
                      f"order trong plan cho tăng dần (khuyết được, "
                      f"lộn xộn thì không)")
    build = proj / "build"
    n_parts = 0
    n_sfx = 0
    total_parts = sum(len(sc.get("parts", [])) for sc in plan["scenes"])
    # B10: PIL không có sẵn thì cửa kiểm giải mã ảnh không chạy — cảnh
    # báo một lần để Production biết preflight chỉ kiểm ảnh tồn tại.
    if not _PIL_OK:
        warnings.append("PIL (Pillow) không có sẵn — preflight chỉ kiểm "
                        "ảnh tồn tại, không kiểm giải mã (cài Pillow để "
                        "bật cửa B10)")
    for sc in plan["scenes"]:
        order = sc["order"]
        # Ảnh scene: chấp nhận cả jpg/png/webp như render_draft (base_image).
        simg = next((q for ext in ("jpg", "png", "webp")
                     for q in [build / "media" / "images" /
                               f"seg_{order}_{rand6(pid, 'img', str(order))}.{ext}"]
                     if q.exists()), None)
        if simg is None:
            # Sửa 29/10/2026 (code-fix): thiếu ảnh từng là warning exit 0
            # trong khi render_draft ra clip nền đen lặng lẽ cho scene đó
            # (QA 26/10/2026). Đã kiểm chứng không xung đột: preflight chạy
            # SAU bước tạo ảnh trong cả skill Production và app (tab
                    # karaoke+preflight đứng sau bước ảnh, trước render), và mọi
            # project video đã bàn giao đều đủ ảnh; chỉ còn test001 (fixture
            # test không ảnh, không phải video bàn giao) và project app mồ
            # côi 20261028165436_213948 (ảnh lệch quy ước tên factory nên
            # render cũng không tìm thấy) là preflight sẽ báo lỗi — đúng
            # hành vi mong muốn, không phải false positive.
            # Luật CEO 12/11/2026: chỉ chặn khi cảnh còn part chưa có
            # ảnh/video riêng (part đó rơi về ảnh cảnh chung). Cảnh mà mọi
            # part đã có ảnh/video riêng không cần ảnh cảnh chung.
            if _scene_needs_scene_image(build, pid, sc):
                errors.append(f"Scene {order} còn part chưa có ảnh/video "
                              f"riêng nhưng thiếu ảnh cảnh chung — luật "
                              f"12/11/2026: cảnh có part không-ảnh thì lấy "
                              f"1 ảnh/video của part đại diện làm ảnh cảnh "
                              f"chung; cảnh không part nào có ảnh/video thì "
                              f"phải tìm ảnh thật cho cảnh chung (không nền "
                              f"đen, không nền trung tính); cảnh mà mọi part "
                              f"đã có ảnh/video thì không cần")
        elif _PIL_OK:
            # B10 (05/11/2026, lệnh CEO, lựa chọn A): ảnh tồn tại chưa
            # đủ — phải giải mã được hết (PIL .load()). File cắt dở
            # (header còn, nửa dưới hỏng) từng qua cửa này rồi mới fail
            # ở render giữa chừng. PIL không có sẵn thì bỏ qua kiểm này
            # (cảnh báo một lần ở đầu hàm main) thay vì chặn oan.
            _derr = img_decode_error(simg)
            if _derr is not None:
                errors.append(f"Scene {order} ảnh hỏng/không giải mã được "
                              f"({simg.name}: {_derr}) — tạo lại ảnh trước "
                              f"khi render")
        for pi, p in enumerate(sc["parts"], start=1):
            n_parts += 1
            tp = tts_by_id.get(p["id"])
            if not tp:
                errors.append(f"Part {p['id']} chưa có audio TTS")
                continue
            aw = build / "audio" / "voice" / tp["audio_file"]
            if not aw.exists():
                errors.append(f"Part {p['id']}: file audio không tồn tại")
            elif tp.get("duration", 0) <= 0:
                errors.append(f"Part {p['id']}: duration = 0")
            br = p.get("broll") or {}
            # 06/11/2026 (danh sách dấu): SFX của part + SFX riêng từng
            # dấu đều phải tồn tại file (mở rộng cửa A26 cho SFX của dấu).
            _sfx_ids = _part_sfx_ids(br)
            if _sfx_ids:
                n_sfx += 1
                for _sid in _sfx_ids:
                    # A26 (05/11/2026, lệnh CEO): SFX khai trong plan nhưng
                    # file mp3 không tồn tại thì LỖI như BGM thiếu — trước
                    # đây render chỉ log sfx-thieu-bo-qua rồi render tiếp
                    # không tiếng đó.
                    _sf = FACTORY / "sfx" / f"{_sid}.mp3"
                    if not _sf.exists():
                        errors.append(
                            f"Part {p['id']}: SFX '{_sid}' không tồn tại "
                            f"({_sf.name} trong thư mục sfx) — render sẽ thiếu tiếng này")
            # F11 (bước 2, 13/11/2026): SFX volume ngoài (0,1] là lỗi; SFX nặng
            # (thud/slam/boom) > 0.4 bị mixer cắt thầm lặng về 0.4 -> cảnh báo.
            _sfx_pf = br.get("sfx")
            if isinstance(_sfx_pf, dict):
                _vol = _sfx_pf.get("volume", 0.6)
                if not isinstance(_vol, (int, float)) or not (0 < _vol <= 1):
                    errors.append(f"Part {p['id']}: sfx.volume '{_vol}' phải trong (0,1]")
                elif any(k in str(_sfx_pf.get("id")) for k in ("thud", "slam", "boom")) and _vol > 0.4:
                    warnings.append(f"Part {p['id']}: sfx nặng {_sfx_pf.get('id')} volume {_vol} > 0.4 — mixer sẽ cắt về 0.4")
            # Sửa đợt B 01/11/2026 (chỉ warning): part khai b-roll video
            # nhưng không có file mp4 thì render rơi về ảnh scene lặng lẽ
            # (base_video trả None). Cảnh báo để Production biết trước,
            # không thành lỗi vì fallback ảnh vẫn ra video xem được.
            if br.get("mediaType") == "video":
                bv = build / "media" / "broll" / (
                    f"broll_seg_{order}_part_{pi}_"
                    f"{rand6(pid, 'broll', str(order), str(pi))}.mp4")
                if not bv.exists():
                    warnings.append(
                        f"Part {p['id']}: khai b-roll video nhưng không có "
                        f"file {bv.name} — render sẽ rơi về ảnh scene")
            # F3 (09/11/2026, quyết định CEO): part khai prompt AI (cần
            # ảnh riêng) nhưng không có file ảnh b-roll (và không có mp4)
            # thì render rơi về ảnh scene lặng lẽ — cảnh báo để Production
            # biết trước (đối xứng với cảnh báo thiếu mp4 ở trên). Part
            # template dùng ảnh scene làm nền thì không có prompt nên
            # không cảnh báo oan.
            _prompt = br.get("prompt")
            if isinstance(_prompt, str) and _prompt.strip():
                _bi2 = next((q for ext in ("jpg", "png", "webp")
                             for q in [build / "media" / "broll" /
                                       f"broll_seg_{order}_part_{pi}_"
                                       f"{rand6(pid, 'broll', str(order), str(pi))}.{ext}"]
                             if q.exists()), None)
                _bv2 = build / "media" / "broll" / (
                    f"broll_seg_{order}_part_{pi}_"
                    f"{rand6(pid, 'broll', str(order), str(pi))}.mp4")
                if _bi2 is None and not _bv2.exists():
                    warnings.append(
                        f"Part {p['id']}: khai prompt AI nhưng không có file "
                        f"ảnh b-roll — render sẽ rơi về ảnh scene")
            # B10 (05/11/2026, lệnh CEO, lựa chọn A): ảnh b-roll nếu có
            # mà giải mã không được thì LỖI — render sẽ fail giữa chừng
            # hoặc ra clip lỗi. Không có file thì không sao, render rơi
            # về ảnh scene như cũ.
            if _PIL_OK:
                _bimg = next((q for ext in ("jpg", "png", "webp")
                              for q in [build / "media" / "broll" /
                                        f"broll_seg_{order}_part_{pi}_"
                                        f"{rand6(pid, 'broll', str(order), str(pi))}.{ext}"]
                              if q.exists()), None)
                if _bimg is not None:
                    _berr = img_decode_error(_bimg)
                    if _berr is not None:
                        errors.append(f"Part {p['id']}: ảnh b-roll hỏng/không "
                                      f"giải mã được ({_bimg.name}: {_berr}) — "
                                      f"tạo lại ảnh b-roll")
            meta = None
            if br.get("templateId"):
                tdir = FACTORY / "templates" / br["templateId"]
                if not (tdir / "template.html").exists():
                    errors.append(f"Part {p['id']}: template "
                                  f"{br['templateId']} không tồn tại")
                # Sửa 29/10/2026 (code-fix, audit D-L1): meta khai inputs
                # dạng DICT {"value": {...}}, code cũ duyệt như list nên
                # vòng lặp chỉ ra string key, inp.get gây AttributeError và
                # except-pass nuốt trọn — kể cả meta hỏng. Chuẩn đúng là
                # .items() như validate_project.py. Chỉ bắt lỗi đọc file/
                # JSON; lỗi sai dạng inputs phải thành lỗi, không nuốt.
                try:
                    meta = json.loads((tdir / "meta.json").read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    errors.append(f"Part {p['id']}: template "
                                  f"{br['templateId']} meta.json hỏng/không "
                                  f"đọc được ({exc})")
                    meta = None
                if meta is not None:
                    inputs_def = meta.get("inputs", {})
                    if not isinstance(inputs_def, dict):
                        errors.append(f"Part {p['id']}: template "
                                      f"{br['templateId']} khai inputs không "
                                      f"phải dict — sửa meta.json theo schema "
                                      f"hiện hành")
                    else:
                        for name, idef in inputs_def.items():
                            if not isinstance(idef, dict):
                                continue
                            if idef.get("required"):
                                v = (br.get("inputs") or {}).get(name, "")
                                if not str(v).strip():
                                    errors.append(
                                        f"Part {p['id']}: thiếu input bắt buộc "
                                        f"'{name}' của {br['templateId']}")
                            # 11/11/2026: dùng meta_check — maxLength của input danh sách
                            # (items) tính MỖI DÒNG (trước đây tính cả khối nên ví dụ chuẩn của
                            # checklist bị chặn oan), thêm maxItems, enum values, min/max, pattern.
                            for _msg in meta_check.check_input_value(
                                    name, idef, (br.get("inputs") or {}).get(name, "")):
                                errors.append(
                                    f"Part {p['id']}: {_msg} ({br['templateId']})")
                            # 06/11/2026 (photo-duo): input ảnh (meta
                            # type=image) phải trỏ tới file thật trong
                            # project — thiếu file thì template render ra
                            # khung trống lặng lẽ.
                            if idef.get("type") == "image":
                                v = (br.get("inputs") or {}).get(name, "")
                                if str(v).strip() and not str(v).startswith("file://"):
                                    _ip = Path(str(v))
                                    if not _ip.is_absolute():
                                        _ip = proj / _ip
                                    if not _ip.exists():
                                        errors.append(
                                            f"Part {p['id']}: ảnh input '{name}' "
                                            f"của {br['templateId']} không có file "
                                            f"{_ip.name}")
                    # 06/11/2026 (compare-bars 1.1.0, tên cũ duel-bars):
                    # count 2-4 bars; thiếu count -> mặc định 2 bars (plan
                    # cũ vẫn đúng). count>=3 mà thiếu input của bar đó thì
                    # render ra hàng trống (w thiếu -> width:% vô hiệu, fill
                    # dài 100%; tone thiếu -> chữ đen chìm) nên chặn ở đây.
                    if br.get("templateId") == "compare-bars":
                        _cnt = str((br.get("inputs") or {}).get("count", "2")).strip()
                        if _cnt not in ("2", "3", "4"):
                            errors.append(
                                f"Part {p['id']}: compare-bars count '{_cnt}' "
                                f"phải là 2|3|4")
                        else:
                            _need = []
                            if _cnt in ("3", "4"):
                                _need += ["label3", "value3", "w3", "tone3"]
                            if _cnt == "4":
                                _need += ["label4", "value4", "w4", "tone4"]
                            for _n in _need:
                                _v = (br.get("inputs") or {}).get(_n, "")
                                if not str(_v).strip():
                                    errors.append(
                                        f"Part {p['id']}: compare-bars "
                                        f"count={_cnt} mà thiếu input '{_n}'")
                                else:
                                    _ml = ((inputs_def.get(_n) or {}).get("maxLength")
                                           if isinstance(inputs_def, dict) else None)
                                    # R4-41 (07/11/2026, DEC-049): vượt
                                    # maxLength thì FAIL như input thường.
                                    if _ml and len(str(_v)) > _ml:
                                        errors.append(
                                            f"Part {p['id']}: '{_n}' dài "
                                            f"{len(str(_v))}>{_ml} ký tự")
                    # 13/11/2026 (F2): ràng buộc meta (requiredWhen/sum) — vd share-bar tổng pct = 100.
                    for _msg in meta_check.check_constraints(meta, br.get("inputs") or {}):
                        errors.append(f"Part {p['id']}: {_msg} ({br['templateId']})")
                    # Sửa 29/10/2026 (code-fix, audit D-L6): render chỉ đọc
                    # SFX từ plan, không bao giờ đọc meta template. Nếu
                    # template gợi ý SFX mà plan chưa copy thì SFX đó mất
                    # lặng lẽ — cảnh báo để Production copy vào plan theo
                    # luật SFX, KHÔNG tự copy lặng lẽ.
                    meta_sfx = meta.get("sfx")
                    meta_sfx_id = (meta_sfx.get("id") if isinstance(meta_sfx, dict)
                                   else meta_sfx if isinstance(meta_sfx, str) else None)
                    if meta_sfx_id and meta_sfx_id not in _part_sfx_ids(br):
                        warnings.append(
                            f"Part {p['id']}: template {br['templateId']} gợi ý "
                            f"SFX '{meta_sfx_id}' nhưng plan chưa có broll.sfx "
                            f"— copy vào plan trước khi render (render chỉ đọc "
                            f"SFX từ plan, không đọc meta template)")
            # 06/11/2026 (reveal lần lượt, CEO): broll.reveal =
            # [stage...] — các lớp của template hiện lần lượt (cắt
            # cứng, chia đều thời lượng part). Chỉ áp cho template
            # full-stage; template không full-stage thì reveal bị bỏ
            # qua lặng lẽ ở render — cảnh báo trước.
            _rv = br.get("reveal")
            # Chỉ kiểm khi part có template (reveal không có template
            # thì render bỏ qua; meta ở đây là của part này vì đã qua
            # khối templateId phía trên).
            if _rv is not None and br.get("templateId"):
                if (not isinstance(_rv, list) or len(_rv) < 2
                        or not all(isinstance(_s, str)
                                   and _s.strip().isdigit()
                                   for _s in _rv)):
                    errors.append(f"Part {p['id']}: broll.reveal phải là "
                                  f"danh sách >=2 stage dạng chuỗi số, "
                                  f"vd [\"1\",\"2\",\"3\",\"4\"]")
                elif meta is not None and (
                        meta.get("mode") != "fullscreen"
                        or (meta.get("position") or {}).get("default") != "full-stage"):
                    warnings.append(f"Part {p['id']}: reveal chỉ áp cho "
                                    f"template full-stage — {br['templateId']} "
                                    f"không full-stage nên reveal sẽ bị bỏ qua")
                # R4-34 (07/11/2026, DEC-042): reveal không vượt maxStage
                # của template (meta.json) — stage không tồn tại thì
                # render rơi về đường tĩnh lặng lẽ (render_draft: stage
                # render lỗi -> _reveal_ok=False).
                if (isinstance(_rv, list) and len(_rv) >= 2
                        and all(isinstance(_s, str)
                                and _s.strip().isdigit() for _s in _rv)
                        and meta is not None
                        and isinstance(meta.get("maxStage"), int)
                        and not isinstance(meta.get("maxStage"), bool)):
                    _mx = int(meta["maxStage"])
                    _over = sorted({int(_s) for _s in _rv if int(_s) > _mx})
                    if _over:
                        errors.append(f"Part {p['id']}: broll.reveal có "
                                      f"stage {_over} vượt maxStage {_mx} "
                                      f"của {br['templateId']}")
                # R4-34 (07/11/2026, DEC-042): video-slot phải hiện trong
                # reveal — ô ảnh chỉ hiện từ stage S (vd photo-duo img2
                # từ stage 5) mà reveal chỉ tới stage < S thì video ghép
                # vào slot chưa có ảnh (trống/sai vị trí). Chỉ kiểm khi
                # reveal có hiệu lực (template full-stage); dùng cùng
                # bảng _STAMP_APPEAR_STAGE như kiểm stamp.
                if (_rv is not None and br.get("templateId")
                        and meta is not None
                        and meta.get("mode") == "fullscreen"
                        and (meta.get("position") or {}).get("default") == "full-stage"
                        and isinstance(_rv, list) and len(_rv) >= 2
                        and all(isinstance(_s, str)
                                and _s.strip().isdigit() for _s in _rv)):
                    _rv_max = max(int(_s) for _s in _rv)
                    _vslots = meta.get("videoSlots") or {}
                    for _vk, _vv in (br.get("inputs") or {}).items():
                        if (_vk in _vslots and str(_vv).strip()
                                and Path(str(_vv)).suffix.lower()
                                in (".mp4", ".mov", ".webm", ".mkv")):
                            _ap = _STAMP_APPEAR_STAGE.get(
                                (br["templateId"], _vk), 1)
                            if _ap > _rv_max:
                                errors.append(
                                    f"Part {p['id']}: video-slot '{_vk}' "
                                    f"chỉ hiện từ stage {_ap} của "
                                    f"{br['templateId']} nhưng reveal chỉ "
                                    f"tới stage {_rv_max} — video ghép vào "
                                    f"slot chưa có ảnh")
            # Lớp dấu — danh sách dấu (06/11/2026, khôi phục sau lệnh xoá
            # cùng ngày + mở rộng): broll.stamps = [{text, tone, tilt,
            # on, at, sfx}, ...]; broll.stamp đơn cũ -> 1 phần tử.
            # Dấu đóng vào TÂM Ô ẢNH (stamp.on), hiện từ t=at, SFX thud
            # khớp at. Kiểm từng dấu như kiểm một dấu đơn.
            _stamps = _normalize_stamps(br)
            if _stamps and not br.get("templateId"):
                errors.append(f"Part {p['id']}: có dấu nhưng không có "
                              f"templateId — part ảnh thường không template "
                              f"thì dùng verdict-stamp làm templateId trực tiếp")
            if _stamps and br.get("templateId"):
                if len(_stamps) > 3:
                    errors.append(f"Part {p['id']}: tối đa 3 dấu/part, "
                                  f"đang có {len(_stamps)}")
                _part_dur = tp.get("duration", 0) or 0
                _is_last = (n_parts == total_parts)
                # cdur như render_draft (XFADE_D 0.5s, trừ part cuối).
                _cdur = _part_dur + (0 if _is_last else 0.5)
                _img_ins = None
                if meta is not None:
                    _img_ins = sorted(
                        n for n, d in (meta.get("inputs") or {}).items()
                        if isinstance(d, dict) and d.get("type") == "image")
                _seen_on = set()
                for _sti, _st in enumerate(_stamps):
                    _pfx = f"Part {p['id']} dấu {_sti + 1}"
                    _text = str(_st.get("text") or "").strip()
                    if not _text:
                        errors.append(f"{_pfx}: thiếu text")
                    elif len(_text) > 14:
                        errors.append(f"{_pfx}: text '{_text}' dài "
                                      f"{len(_text)}>14 ký tự")
                    _tone = _st.get("tone", "red")
                    if _tone not in ("green", "red"):
                        errors.append(f"{_pfx}: tone '{_tone}' phải là "
                                      f"green|red")
                    _tilt = str(_st.get("tilt", "-15"))
                    if _tilt not in ("-15", "0", "15"):
                        errors.append(f"{_pfx}: tilt '{_tilt}' phải là "
                                      f"-15|0|15")
                    _on = str(_st.get("on") or "").strip()
                    if _on and _img_ins is not None and _on not in _img_ins:
                        errors.append(f"{_pfx}: on '{_on}' không phải "
                                      f"input ảnh của {br['templateId']}")
                    if _on:
                        if _on in _seen_on:
                            warnings.append(f"{_pfx}: 2 dấu trên cùng ô "
                                            f"'{_on}' sẽ chồng nhau")
                        _seen_on.add(_on)
                    _at = _st.get("at")
                    if (not isinstance(_at, (int, float))
                            or isinstance(_at, bool)):
                        errors.append(f"{_pfx}: thiếu at (giây trong part) "
                                      f"— dấu bắt buộc có at > 0")
                        _at = None
                    elif _at <= 0:
                        errors.append(f"{_pfx}: at={_at} phải > 0 — dấu "
                                      f"hiện từ t=at, không hiện suốt part")
                    elif _part_dur and _at >= _part_dur:
                        errors.append(f"{_pfx}: at={_at} >= thời lượng "
                                      f"part {_part_dur}s")
                    if _at is not None and _at > 0:
                        # Giờ ảnh hiện: không reveal -> 0; có reveal ->
                        # stage đầu tiên ảnh hiện, tính theo cdur + reveal
                        # (photo-duo img2 hiện từ stage 5, photo-duo-h
                        # img2 từ stage 2, còn lại từ stage 1).
                        _appear = 0.0
                        _rv_ok = (isinstance(_rv, list) and len(_rv) >= 2
                                  and all(isinstance(_s, str)
                                          and _s.strip().isdigit()
                                          for _s in _rv))
                        if _rv_ok:
                            _stage = _STAMP_APPEAR_STAGE.get(
                                (br["templateId"], _on), 1)
                            _idx = None
                            for _i, _sv in enumerate(_rv):
                                if int(_sv) >= _stage:
                                    _idx = _i
                                    break
                            if _idx is None:
                                _on_name = _on or (
                                    _img_ins[0] if _img_ins else "?")
                                errors.append(
                                    f"{_pfx}: ảnh '{_on_name}' không hiện "
                                    f"trong reveal nên dấu không có chỗ đóng")
                            else:
                                _appear = _idx * _cdur / len(_rv)
                        if _at < _appear:
                            errors.append(
                                f"{_pfx}: stamp at {_at}s < giờ ảnh "
                                f"'{_on}' hiện {_appear:.2f}s — dấu phải "
                                f"hiện SAU ảnh")
                    # SFX của dấu: mỗi dấu mang thud riêng; dấu đơn không
                    # có sfx riêng thì dùng sfx của part (luật cũ).
                    _ssfx = _st.get("sfx")
                    if not isinstance(_ssfx, dict):
                        _ssfx = None
                    if _ssfx is None and len(_stamps) > 1:
                        errors.append(f"{_pfx}: dấu trong danh sách thiếu "
                                      f"sfx riêng — part-level sfx không thể "
                                      f"khớp nhiều mốc at")
                    elif _ssfx is not None:
                        if _ssfx.get("id") != "heavy_thud_slam":
                            warnings.append(f"{_pfx}: SFX của dấu phải là "
                                            f"heavy_thud_slam, đang là "
                                            f"'{_ssfx.get('id')}'")
                        # R4-42 (07/11/2026, DEC-050, phương án A): lệch
                        # >0.15s thì FAIL (trước đây chỉ warn) — thud
                        # phải đánh đúng lúc dấu đóng, không lệch nhịp.
                        elif _at is not None and abs(
                                float(_ssfx.get("offsetSec", 0)) - _at) > 0.15:
                            errors.append(f"{_pfx}: SFX offsetSec "
                                            f"{_ssfx.get('offsetSec')} lệch at "
                                            f"{_at} quá 0.15s — thud phải đánh "
                                            f"đúng lúc dấu đóng")
                    elif len(_stamps) == 1:
                        _psfx = br.get("sfx") or {}
                        if _psfx.get("id") != "heavy_thud_slam":
                            warnings.append(f"{_pfx}: SFX của part phải là "
                                            f"heavy_thud_slam (thud của dấu), "
                                            f"đang là '{_psfx.get('id')}'")
                        # R4-42 (07/11/2026, DEC-050, phương án A): lệch
                        # >0.15s thì FAIL (trước đây chỉ warn).
                        elif _at is not None and abs(
                                float(_psfx.get("offsetSec", 0)) - _at) > 0.15:
                            errors.append(f"{_pfx}: SFX offsetSec "
                                            f"{_psfx.get('offsetSec')} lệch at "
                                            f"{_at} quá 0.15s")

    # R4-57 (08/11/2026, DEC-066 A'): tiling + endSec + lossless —
    # port từ validate_project.py (chỉ hợp lệ SAU assemble nên không
    # gọi nó trước render — sai công cụ, đợt D7). Ngưỡng khớp
    # validate: tiling lệch >0.05s, endSec lệch >0.1s.
    # (a) tiling: các part nối nhau không hở/không chồng — render ghép
    # part theo startSec/endSec nên hở là đoạn câm/đen, chồng là cắt
    # âm. Chuỗi nối xuyên scene (scene sau bắt đầu đúng lúc scene
    # trước kết thúc). Part chưa có audio TTS thì bỏ qua ở đây (đã báo
    # ở vòng trên) để không báo trùng.
    _prev_end = None
    _first = True
    for sc in plan["scenes"]:
        _sc_last_end = None
        for p in sc.get("parts", []):
            tp = tts_by_id.get(p["id"])
            if tp is None:
                continue
            _s = tp.get("startSec")
            _e = tp.get("endSec")
            if not isinstance(_s, (int, float)) or not isinstance(_e, (int, float)):
                continue
            if _first:
                if abs(_s) > 0.05:
                    errors.append(f"Part {p['id']}: startSec {_s}s — part "
                                  f"đầu phải bắt đầu ở 0s (lệch {abs(_s):.2f}s)")
                _first = False
            elif _prev_end is not None and abs(_s - _prev_end) > 0.05:
                errors.append(f"Part {p['id']}: startSec {_s}s không khớp "
                              f"tiling — part trước kết thúc ở {_prev_end}s "
                              f"(lệch {abs(_s - _prev_end):.2f}s, cho phép 0.05s)")
            _prev_end = _e
            _sc_last_end = _e
        # (d) endSec của scene khớp part cuối (khớp validate:213).
        if _sc_last_end is not None:
            _tts_sc = next((s for s in tts.get("scenes", [])
                            if s.get("order") == sc.get("order")), None)
            if _tts_sc is not None:
                _sc_end = _tts_sc.get("endSec")
                if isinstance(_sc_end, (int, float)) and abs(_sc_end - _sc_last_end) > 0.1:
                    errors.append(f"Scene {sc.get('order')}: endSec "
                                  f"{_sc_end}s không khớp tổng parts (part "
                                  f"cuối kết thúc ở {_sc_last_end}s, lệch "
                                  f"{abs(_sc_end - _sc_last_end):.2f}s, cho "
                                  f"phép 0.1s)")
    # (b) voiceText lossless: lời thoại trong plan nối lại phải khớp nội
    # dung kịch bản (khớp validate_project.py:211) — plan và script lệch
    # nhau nghĩa là sửa một nơi mà quên nơi kia, audio (theo script)
    # sẽ lệch với plan (QA đọc plan để đối chiếu). Thiếu script.json
    # thì bỏ qua (không chặn oan — 2 project test không có script).
    _script_path = proj / "script.json"
    if _script_path.exists():
        try:
            _script = json.loads(_script_path.read_text(encoding="utf-8"))
            _ref = _norm(str(_script.get("content", "")))
            _joined = _norm(" ".join(str(p.get("voiceText", ""))
                                     for sc in plan["scenes"]
                                     for p in sc.get("parts", [])))
            if _ref and _joined and _ref != _joined:
                errors.append("voiceText trong plan nối lại không khớp nội "
                              "dung script.json (lossless fail) — sửa plan "
                              "hoặc script cho khớp rồi chạy lại preflight")
        except (OSError, json.JSONDecodeError):
            pass

    # Cửa chặn ảnh thật — provenance (lệnh CEO 05/11/2026, lựa chọn A20):
    # mỗi scene phải có mediaSource.source là chuỗi không rỗng VÀ có
    # mục nhật ký tìm ảnh trong media-log.json với keywordsTried không
    # rỗng. Cảnh AI từ prompt vẫn cần keywordsTried (bằng chứng đã thử
    # tìm ảnh thật trước). Scene chỉ có nền xanh rêu kẻ ô không có
    # mediaSource nên chặn ở đây, khớp luật hồ sơ/QA (nền xanh rêu
    # không tính là ảnh). B7 (lệnh CEO 05/11/2026, lựa chọn A): chặn
    # thêm scene có isMossGrid=true dù đã có mediaSource + log — cờ
    # A21 có nghĩa là cảnh đang là nền rêu, nguồn/log cũ còn lại từ
    # lần thử trước không tính. Cờ tự xóa khi gắn ảnh thật/AI (A21)
    # nên cảnh đã sửa không bị chặn oan. Miễn cho project test kỹ
    # thuật (pid bắt đầu bằng "test", vd test001 fixture) — các kiểm
    # tra khác vẫn chạy bình thường với project test.
    # R3-34 (09/11/2026, rà soát lần 3): A20 là cửa tối thiểu — chỉ kiểm
    # có nguồn + có từ khóa; `candidates`/`chosen` trong log do QA kiểm
    # bằng tay, A20 không chặn khi log thiếu ứng viên/visual được chọn.
    if not pid.startswith("test"):
        _log_path = proj / "media-log.json"
        _log_scenes = {}
        if not _log_path.exists():
            errors.append("Thiếu nhật ký tìm ảnh (media-log.json không có) "
                          "— xuất nhật ký tìm ảnh từng cảnh trước khi "
                          "render (xem LOGIC.md mục \"Bài học bắt buộc "
                          "TOPIC-219\")")
        else:
            try:
                _log = json.loads(_log_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"media-log.json hỏng/không đọc được ({exc}) "
                              f"— xuất lại nhật ký tìm ảnh trước khi render")
                _log = None
            if _log is not None:
                _entries = _log.get("scenes")
                if not isinstance(_entries, list):
                    errors.append("media-log.json không có danh sách scenes "
                                  "— xuất lại nhật ký tìm ảnh trước khi "
                                  "render")
                else:
                    for _e in _entries:
                        if isinstance(_e, dict) and _e.get("sceneId"):
                            _log_scenes[_e["sceneId"]] = _e
        for sc in plan["scenes"]:
            order = sc["order"]
            # Luật CEO 12/11/2026: cảnh mọi part đã có ảnh/video riêng và
            # không có ảnh cảnh chung thật (không file, hoặc chỉ là nền rêu
            # giữ chỗ) thì không cần nguồn/nhật ký cấp cảnh — hồ sơ nằm ở
            # dòng `parts` của media-log. Cảnh đã có ảnh cảnh chung thật
            # vẫn phải đủ nguồn + nhật ký như cũ.
            _has_simg0 = any(
                (build / "media" / "images" /
                 f"seg_{order}_{rand6(pid, 'img', str(order))}.{_x}").exists()
                for _x in ("jpg", "png", "webp"))
            if (not _scene_needs_scene_image(build, pid, sc)
                    and (not _has_simg0 or sc.get("isMossGrid"))):
                continue
            if sc.get("isMossGrid"):
                errors.append(f"Scene {order} là nền xanh rêu kẻ ô vuông "
                              f"(isMossGrid=true) — chưa có ảnh thật/AI: nền "
                              f"rêu không tính là ảnh. Gắn ảnh thật hoặc ảnh "
                              f"AI cho cảnh (cờ tự xóa khi gắn ảnh) rồi chạy "
                              f"lại preflight")
            _ms = sc.get("mediaSource")
            _src = (_ms.get("source") if isinstance(_ms, dict) else None)
            if not (isinstance(_src, str) and _src.strip()):
                errors.append(f"Scene {order} thiếu nguồn media "
                              f"(mediaSource.source trống/thiếu) — ghi rõ "
                              f"nguồn ảnh/video của cảnh vào plan trước khi "
                              f"render")
            _entry = _log_scenes.get(sc.get("id"))
            if _entry is None:
                errors.append(f"Scene {order} thiếu nhật ký tìm ảnh "
                              f"(không có mục sceneId={sc.get('id')} trong "
                              f"media-log.json) — xuất nhật ký tìm ảnh "
                              f"(từ khóa đã thử, ứng viên, phân loại) trước "
                              f"khi render")
            elif not [k for k in (_entry.get("keywordsTried") or [])
                     if isinstance(k, str) and k.strip()]:
                errors.append(f"Scene {order} thiếu nhật ký tìm ảnh "
                              f"(keywordsTried trống) — ghi các từ khóa "
                              f"tiếng Việt đã thử tìm ảnh thật trước khi "
                              f"render")

    # Luật kề nhau (lệnh CEO 09/11/2026, DEC-242, Khối 4 — Cách 1, Q3;
    # đính chính DEC-244): 2 part liền kề (theo thứ tự phát toàn video,
    # kể cả qua biên scene) không được chung 1 file visual — dùng đúng
    # logic resolve của render (video b-roll > ảnh b-roll part > ảnh
    # scene). Vi phạm thì CHẶN render (exit 1) như cửa A20. Miễn cho
    # project test (pid "test*") như A20. Ngoại lệ: file nền được dùng
    # lại ở scene khác — 2 part ở 2 scene khác nhau cùng dùng 1 file nền
    # thì được chung file; trong cùng 1 scene thì không miễn (mỗi scene
    # tối đa 1 part dùng nền trung tính, thường là part đầu — kiểm riêng
    # ở dưới). Part nền trung tính nhận biết qua media-log.json danh
    # sách `parts` (classification "trung-tinh" hoặc ghi chú "nền trung
    # tính"). A1 (10/11/2026, quyết CEO): part nền còn nhận biết theo
    # file thật — b-roll riêng của part mà trùng md5 với file trong thư
    # viện neutral-bg/ thì cũng là part nền, không phụ thuộc nhãn trong
    # media-log (xem bước mở rộng _neutral_parts sau khi resolve
    # visual). Nhãn trong media-log vẫn được giữ làm đường nhận biết
    # thứ hai. Thiếu cả danh sách parts lẫn thư viện thì không có ngoại
    # lệ (kiểm chặt).
    if not pid.startswith("test"):
        _neutral_parts = set()
        _parts_list = None
        try:
            _mlog = json.loads((proj / "media-log.json").read_text(encoding="utf-8"))
            _parts_list = _mlog.get("parts")
            for _e in (_parts_list or []):
                if not isinstance(_e, dict) or not _e.get("partId"):
                    continue
                _txts = []
                for _k in ("classification", "note", "ghi_chu"):
                    _v = _e.get(_k)
                    if isinstance(_v, str):
                        _txts.append(_v)
                _ch = _e.get("chosen")
                if isinstance(_ch, dict):
                    for _k in ("classification", "note", "ghi_chu"):
                        _v = _ch.get(_k)
                        if isinstance(_v, str):
                            _txts.append(_v)
                _joined = " ".join(_txts)
                if "trung-tinh" in _joined or "nền trung tính" in _joined:
                    _neutral_parts.add(_e["partId"])
        except (OSError, json.JSONDecodeError):
            pass
        # A1 (10/11/2026, quyết CEO — sửa chặn oan nền trung tính): tập
        # md5 của mọi file trong thư viện neutral-bg/ (FACTORY/
        # neutral-bg/image + video). Dùng để nhận biết part nền theo
        # file thật ở bước mở rộng _neutral_parts dưới đây — không phụ
        # thuộc nhãn trong media-log. Thư viện thiếu/không đọc được thì
        # tập rỗng — chỉ còn nhận biết bằng nhãn như trước, preflight
        # không crash.
        _neutral_lib_md5s = set()
        try:
            for _nd in (FACTORY / "neutral-bg" / "image",
                        FACTORY / "neutral-bg" / "video"):
                if not _nd.is_dir():
                    continue
                for _nf in _nd.iterdir():
                    if not _nf.is_file():
                        continue
                    _h = hashlib.md5()
                    with open(_nf, "rb") as _f:
                        for _c in iter(lambda: _f.read(1 << 20), b""):
                            _h.update(_c)
                    _neutral_lib_md5s.add(_h.hexdigest())
        except OSError:
            _neutral_lib_md5s = set()
        # DEC-244 (đối soát 09/11/2026): không có danh sách `parts` thì
        # không kiểm được luật mỗi scene tối đa 1 nền trung tính — chỉ
        # cảnh báo (không chặn) để QA kiểm bằng tay; chỉ cảnh báo khi
        # plan có part dùng b-roll riêng (có nhật ký theo part mới kiểm
        # được).
        # R3-32 (09/11/2026, rà soát lần 3): chỉ cảnh báo khi có part thực
        # sự có visual riêng — có `prompt` (AI), hoặc `mediaType`, hoặc có
        # file b-roll trên đĩa (kể cả file nền trung tính đã copy vào
        # build/media/broll/). Part chỉ có template (không prompt, không
        # mediaType, không file b-roll) dùng ảnh scene làm nền nên không
        # cần dòng log riêng — không cảnh báo (tránh nhiễu).
        def _part_has_own_visual(_sc, _p, _pi):
            _br = (_p or {}).get("broll") or {}
            if not isinstance(_br, dict):
                return False
            if isinstance(_br.get("prompt"), str) and _br["prompt"].strip():
                return True
            if _br.get("mediaType"):
                return True
            _order = _sc.get("order")
            _r6 = rand6(pid, "broll", str(_order), str(_pi))
            if (build / "media" / "broll" /
                    f"broll_seg_{_order}_part_{_pi}_{_r6}.mp4").exists():
                return True
            return any((build / "media" / "broll" /
                        f"broll_seg_{_order}_part_{_pi}_{_r6}.{ext}").exists()
                       for ext in ("jpg", "png", "webp"))
        _has_part_broll = any(
            _part_has_own_visual(_sc, _p, _pi)
            for _sc in plan["scenes"]
            for _pi, _p in enumerate(_sc["parts"], start=1)
        )
        if _has_part_broll and not _parts_list and not _neutral_lib_md5s:
            warnings.append("media-log.json không có danh sách `parts` (hoặc danh sách trống) mà plan có part dùng b-roll riêng, và thư viện neutral-bg/ cũng không đọc được — preflight không kiểm được luật mỗi scene tối đa 1 nền trung tính (DEC-244); QA kiểm bằng tay. Ghi dòng part vào media-log (classification 'trung-tinh' cho part dùng nền) rồi chạy lại preflight")
        # F2 (09/11/2026, quyết định CEO): media-log `parts` có partId
        # không có trong plan (dòng cũ sau khi đổi số part) thì preflight
        # nhận sai part nền — chỉ cảnh báo (không chặn) để Production
        # cập nhật lại partId trong media-log rồi chạy lại preflight.
        if isinstance(_parts_list, list):
            _plan_ids = {_p.get("id") for _sc in plan["scenes"]
                         for _p in _sc["parts"] if isinstance(_p, dict)}
            # R3-33 (09/11/2026, rà soát lần 3): chỉ cảnh báo partId cũ khi
            # dòng đó được đánh dấu nền (classification/ghi chú chứa
            # "trung-tinh" hoặc "nền trung tính") — chỉ dòng nền cũ mới ảnh
            # hưởng nhận biết part nền; dòng nội dung cũ không ảnh hưởng
            # đếm nền nên không cảnh báo (tránh nhiễu).
            def _is_neutral_entry(_e):
                _txts = []
                for _k in ("classification", "note", "ghi_chu"):
                    _v = _e.get(_k)
                    if isinstance(_v, str):
                        _txts.append(_v)
                _ch = _e.get("chosen")
                if isinstance(_ch, dict):
                    for _k in ("classification", "note", "ghi_chu"):
                        _v = _ch.get(_k)
                        if isinstance(_v, str):
                            _txts.append(_v)
                _joined = " ".join(_txts)
                return "trung-tinh" in _joined or "nền trung tính" in _joined
            _stale = sorted({_e.get("partId") for _e in _parts_list
                             if isinstance(_e, dict) and _e.get("partId")
                             and _e.get("partId") not in _plan_ids
                             and _is_neutral_entry(_e)})
            if _stale:
                warnings.append(
                    "media-log.json danh sách `parts` có partId của dòng nền "
                    f"không có trong plan ({', '.join(_stale)}) — dòng nền cũ "
                    "sau khi đổi số part? Cập nhật lại partId trong "
                    "media-log rồi chạy lại preflight (preflight nhận biết "
                    "part nền theo partId)")
        # A1 (10/11/2026): hàm md5 dùng chung cho cả bước mở rộng
        # _neutral_parts (dưới đây) và khối trần DEC-272 (cuối khối).
        _md5_cache = {}

        def _file_md5(_p):
            _k = str(_p)
            if _k not in _md5_cache:
                _h = hashlib.md5()
                with open(_p, "rb") as _f:
                    for _c in iter(lambda: _f.read(1 << 20), b""):
                        _h.update(_c)
                _md5_cache[_k] = _h.hexdigest()
            return _md5_cache[_k]

        _resolved = []  # (partId, Path|None, order) theo thứ tự phát toàn video
        for _sc in plan["scenes"]:
            _order = _sc["order"]
            _simg = next((q for ext in ("jpg", "png", "webp")
                          for q in [build / "media" / "images" /
                                    f"seg_{_order}_{rand6(pid, 'img', str(_order))}.{ext}"]
                          if q.exists()), None)
            for _pi, _p in enumerate(_sc["parts"], start=1):
                _br = _p.get("broll") or {}
                _vis = None
                # F1 (09/11/2026, quyết định CEO): mediaType chỉ là gợi ý
                # để AI tạo ảnh hay video; nếu ảnh/video lấy từ nguồn thực
                # (internet/mạng xã hội/stock) thì bỏ qua điều kiện
                # mediaType — resolve theo file thật trên đĩa, đúng như
                # render (base_video). Không kiểm mediaType ở đây nữa.
                _bv = build / "media" / "broll" / (
                    f"broll_seg_{_order}_part_{_pi}_"
                    f"{rand6(pid, 'broll', str(_order), str(_pi))}.mp4")
                if _bv.exists():
                    if _is_valid_video_broll(_bv):
                        _vis = _bv
                    else:
                        # Mp4 tồn tại nhưng ffprobe không thấy video stream
                        # — render rơi về ảnh (B1), preflight cũng vậy.
                        warnings.append(
                            f"Part {_p['id']}: file b-roll video {_bv.name} "
                            f"tồn tại nhưng ffprobe không thấy video stream "
                            f"— render sẽ rơi về ảnh scene")
                if _vis is None:
                    _bi = next((q for ext in ("jpg", "png", "webp")
                                for q in [build / "media" / "broll" /
                                          f"broll_seg_{_order}_part_{_pi}_"
                                          f"{rand6(pid, 'broll', str(_order), str(_pi))}.{ext}"]
                                if q.exists()), None)
                    _vis = _bi if _bi is not None else _simg
                _resolved.append((_p["id"], _vis, _order))
        # A1 (10/11/2026, quyết CEO): mở rộng _neutral_parts theo file
        # thật — part nào resolve về b-roll riêng mà file đó trùng md5
        # với file trong thư viện neutral-bg thì là part nền, dù
        # media-log quên ghi nhãn 'trung-tinh'. Chỉ xét b-roll riêng
        # của part (tên broll_seg_…), không xét ảnh scene — ảnh scene
        # là visual của scene, không phải nền của part (tránh nhận sai
        # cả scene là nền khi ảnh scene trùng file thư viện).
        for _pid4, _v4, _o4 in _resolved:
            if _v4 is None or _pid4 in _neutral_parts:
                continue
            if not _v4.name.startswith("broll_seg_"):
                continue
            try:
                if _file_md5(_v4) in _neutral_lib_md5s:
                    _neutral_parts.add(_pid4)
            except OSError:
                continue
        # Luật CEO 12/11/2026: (a) part s1p1 (part đầu tiên của scene đầu
        # tiên) KHÔNG BAO GIỜ dùng ảnh/video trung tính — phải là ảnh/video
        # thật đúng chủ đề (báo chí, mạng xã hội, Google ảnh); (b) ảnh/video
        # cảnh chung KHÔNG BAO GIỜ là ảnh/video trung tính (trùng md5 với
        # file thư viện neutral-bg/, hoặc nhật ký cảnh ghi 'trung-tinh').
        try:
            _first_pid = plan["scenes"][0]["parts"][0]["id"]
        except (IndexError, KeyError, TypeError):
            _first_pid = None
        if _first_pid and _first_pid in _neutral_parts:
            errors.append(f"Part {_first_pid} (part đầu tiên của video) dùng "
                          f"ảnh/video trung tính — luật 12/11/2026 cấm: part "
                          f"đầu phải là ảnh/video thật đúng chủ đề (báo chí, "
                          f"mạng xã hội, Google ảnh), không lấy từ thư viện "
                          f"neutral-bg/")

        def _n9(_e):
            # L9 (13/11/2026, rà soát; thu hẹp 13/11/2026 theo quyết CEO,
            # L9 phương án A): chỉ quét ĐỆ QUY trong mục `chosen` của log
            # scene (ứng viên ĐƯỢC CHỌN) — KHÔNG quét `candidates` đã loại
            # (ứng viên bị loại mang nhãn trung tính không được gắn cờ cả
            # scene; hồ sơ loại giữ nguyên làm bằng chứng) — và
            # mediaSource.source trong plan. Nhận cả chuỗi trần.
            def _scan(_o):
                if isinstance(_o, str):
                    return "trung-tinh" in _o or "nền trung tính" in _o
                if isinstance(_o, dict):
                    return any(_scan(_v) for _v in _o.values())
                if isinstance(_o, (list, tuple)):
                    return any(_scan(_v) for _v in _o)
                return False
            return _scan(_e)

        _neu_by_order = {}
        for _sc9 in plan["scenes"]:
            _o9 = _sc9["order"]
            # L9: ảnh cảnh chung dạng video (mp4) cũng phải kiểm md5 với
            # thư viện neutral-bg/, không chỉ jpg/png/webp.
            _simg9 = next((q for ext in ("jpg", "png", "webp", "mp4")
                           for q in [build / "media" / "images" /
                                     f"seg_{_o9}_{rand6(pid, 'img', str(_o9))}.{ext}"]
                           if q.exists()), None)
            _neu9 = _n9((_log_scenes.get(_sc9.get("id")) or {}).get("chosen"))
            if not _neu9:
                # L9: nhãn trung tính có thể nằm ở mediaSource.source trong plan.
                # mediaSource ở project cũ có thể là chuỗi thẳng (vd "VFF") —
                # chuỗi thì chính nó là tên nguồn, không gọi .get (tránh crash
                # AttributeError như trên topic274001/251001/250001).
                _ms9 = _sc9.get("mediaSource")
                _neu9 = _n9(_ms9.get("source") if isinstance(_ms9, dict) else _ms9)
            if _simg9 is not None and not _neu9 and _neutral_lib_md5s:
                try:
                    _neu9 = _file_md5(_simg9) in _neutral_lib_md5s
                except OSError:
                    _neu9 = False
            _neu_by_order[_o9] = _neu9
            if _neu9:
                errors.append(f"Scene {_o9}: ảnh/video cảnh chung là nền "
                              f"trung tính — luật 12/11/2026 cấm: ảnh cảnh "
                              f"chung phải là ảnh thật đúng chủ đề (báo "
                              f"chí, mạng xã hội, Google ảnh), không phải "
                              f"nền thư viện neutral-bg/")
        # L10 (13/11/2026, rà soát): s1p1 không có b-roll riêng thì
        # resolve về ảnh scene — khi ảnh scene 1 là nền trung tính (kết
        # quả _neu9 của scene 1 ở trên) thì s1p1 cũng là nền trung tính.
        if _first_pid and _first_pid not in _neutral_parts:
            _first_vis = next((_v for _pid5, _v, _o5 in _resolved
                               if _pid5 == _first_pid), None)
            _first_is_scene_img = (
                _first_vis is not None
                and not _first_vis.name.startswith("broll_seg_"))
            _first_order = plan["scenes"][0]["order"]
            if _first_is_scene_img and _neu_by_order.get(_first_order):
                _neutral_parts.add(_first_pid)
                errors.append(f"Part {_first_pid} (part đầu tiên của video) dùng "
                              f"ảnh/video trung tính — luật 12/11/2026 cấm: part "
                              f"đầu phải là ảnh/video thật đúng chủ đề (báo chí, "
                              f"mạng xã hội, Google ảnh), không lấy từ thư viện "
                              f"neutral-bg/")
        # N9(c) (13/11/2026, rà soát — DEC-268; mở rộng DEC-274): part dùng template có
        # neutralBgEligible=false nhưng visual là nền trung tính thì chặn.
        # Đọc neutralBgEligible từ meta.json của template (preflight trước
        # đây không đọc trường này — grep = 0 tham chiếu).
        # DEC + lý do riêng cho từng template bị loại trừ khỏi diện nền:
        _NEUTRAL_EXCL = {
            "cutaway-standard": ("DEC-268", "luôn phải có ảnh/video phù hợp với lời đọc"),
            "preview-banner": ("DEC-274", "bắt buộc ảnh/video thật từ internet/báo chí/mạng xã hội/Google ảnh"),
        }
        _tpl_meta_cache: dict = {}

        def _tpl_allows_neutral(_tid):
            if _tid in _tpl_meta_cache:
                return _tpl_meta_cache[_tid]
            _ok = True
            try:
                _m = json.loads((FACTORY / "templates" / _tid / "meta.json").read_text(encoding="utf-8"))
                _ok = _m.get("neutralBgEligible", True) is not False
            except (OSError, json.JSONDecodeError):
                _ok = True  # không đọc được meta thì không chặn oan; validator M01/M12 lo phần đó
            _tpl_meta_cache[_tid] = _ok
            return _ok

        for _scn in plan["scenes"]:
            for _pn in _scn["parts"]:
                _tidn = ((_pn.get("broll") or {}).get("templateId"))
                if (_pn.get("id") in _neutral_parts and _tidn
                        and not _tpl_allows_neutral(_tidn)):
                    _dec, _why = _NEUTRAL_EXCL.get(_tidn, ("DEC-268", "luôn phải có ảnh/video phù hợp với lời đọc"))
                    errors.append(f"Part {_pn['id']} dùng template {_tidn} "
                                  f"(neutralBgEligible=false theo {_dec}: {_why}) nhưng "
                                  f"visual là nền trung tính — thay visual nội "
                                  f"dung phù hợp rồi chạy lại preflight")
        for (_id1, _v1, _o1), (_id2, _v2, _o2) in zip(_resolved, _resolved[1:]):
            if _v1 is None or _v2 is None or _v1 != _v2:
                continue
            # Ngoại lệ: file nền được dùng lại ở scene khác — 2 part ở 2
            # scene khác nhau cùng dùng 1 file nền thì được chung file.
            # Trong cùng 1 scene thì không miễn (mỗi scene tối đa 1 part
            # dùng nền trung tính — kiểm riêng ở dưới).
            # (Ghi chú đối soát 09/11/2026: miễn trừ này là phòng thủ —
            # tên file b-roll duy nhất theo part nên 2 part khác scene
            # không bao giờ chung file; dùng lại file nền qua scene =
            # copy vào 2 tên khác nhau nên không vi phạm.)
            if _o1 != _o2 and _id1 in _neutral_parts and _id2 in _neutral_parts:
                continue
            errors.append(f"Luật kề nhau (DEC-242): part {_id1} và part "
                          f"{_id2} dùng chung 1 file {_v1.name} — 2 part "
                          f"liền kề không được chung 1 file visual. Đổi "
                          f"visual cho 1 trong 2 part (visual khác trong "
                          f"pool, AI trong trần, hoặc crop chi tiết hạn "
                          f"chế) rồi chạy lại preflight")

        # Mỗi scene tối đa 1 part dùng nền trung tính (quy tắc CEO
        # 09/11/2026, DEC-244): nền thường nằm ở part đầu của scene hoặc
        # không có; 2 part trở lên trong cùng 1 scene cùng dùng nền là
        # vi phạm dù file có khác nhau.
        _neutral_by_scene = {}
        for _pid2, _v, _o in _resolved:
            if _pid2 in _neutral_parts:
                _neutral_by_scene.setdefault(_o, []).append(_pid2)
        for _o, _pids in sorted(_neutral_by_scene.items()):
            if len(_pids) > 1:
                errors.append(f"Scene {_o} có {len(_pids)} part dùng nền "
                              f"trung tính ({', '.join(_pids)}) — mỗi scene "
                              f"tối đa 1 part dùng nền trung tính (thường "
                              f"là part đầu của scene) hoặc không có (quy "
                              f"tắc CEO 09/11/2026, DEC-244). Đổi visual "
                              f"cho các part còn lại (visual nội dung trong "
                              f"pool) rồi chạy lại preflight")

        # Ảnh bằng chứng từ PDF bài báo (v1 thí điểm 13/11/2026, quyết
        # CEO — ke-hoach-chup-man-hinh-bao-20261113.md §14; sửa 13/11
        # theo lệnh CEO: LOẠI chụp ảnh màn hình khỏi logic (chỉ cho
        # 16:9, phương án tồi) — chỉ còn đường PDF; ảnh bằng chứng là
        # NGUYÊN TRANG PDF render thành ảnh (bin/pdf_crop.py
        # --whole-page), KHÔNG cắt 3:4 nữa): tối đa 1 part trong toàn
        # video; dòng log của part đó (classification "chup-man-hinh",
        # ở entry hoặc chosen) phải đủ 4 trường: link (URL bài báo),
        # source (tên báo), articleDate (ngày đăng bài), pdfPage (số
        # trang PDF đã lấy). Tỉ lệ ảnh bằng chứng theo 3 trường hợp
        # (lệnh CEO 13/11/2026, sửa cùng ngày): trong khoảng 3:4–4:3
        # thì nguyên trang; dài hơn 3:4 thì giữ lại, cắt ảnh 3:4; rộng
        # hơn 4:3 (trang quá ngắn) thì loại nguồn, tìm nguồn báo khác
        # — chỉ bỏ trang quá ngắn. Ảnh bằng chứng tính là ảnh thật
        # (vế thật của trần AI ≤ thật — xem _c1_classify_entry) và tính
        # 1 lần vào trần DEC-272 như mọi visual nội dung.
        _ev_parts = []
        for _e in (_parts_list or []):
            if not isinstance(_e, dict) or not _e.get("partId"):
                continue
            _ech = _e.get("chosen") if isinstance(_e.get("chosen"), dict) else {}
            _ecls = _ech.get("classification") or _e.get("classification")
            if _ecls != "chup-man-hinh":
                continue
            _ev_parts.append(_e["partId"])
            _missing = []
            _link = _ech.get("link")
            if not (isinstance(_link, str) and _link.strip().startswith("http")):
                _missing.append("link (URL bài báo, bắt đầu bằng http)")
            if not (isinstance(_ech.get("source"), str) and _ech["source"].strip()):
                _missing.append("source (tên báo)")
            if not (isinstance(_ech.get("articleDate"), str) and _ech["articleDate"].strip()):
                _missing.append("articleDate (ngày đăng bài)")
            if not (isinstance(_ech.get("pdfPage"), int) and _ech["pdfPage"] >= 1):
                _missing.append("pdfPage (số trang PDF đã lấy, >= 1)")
            if _missing:
                errors.append(f"Part {_e['partId']} dùng ảnh bằng chứng từ "
                              f"PDF bài báo (classification 'chup-man-hinh') "
                              f"nhưng media-log thiếu: {', '.join(_missing)} — "
                              f"bổ sung đủ 4 trường rồi chạy lại preflight")
        if len(_ev_parts) > 1:
            errors.append(f"Video có {len(_ev_parts)} part dùng ảnh bằng chứng "
                          f"({', '.join(_ev_parts)}) — luật 13/11/2026: tối đa "
                          f"1 ảnh bằng chứng/video, cho đúng 1 part luận chứng. "
                          f"Bỏ ảnh bằng chứng ở các part còn lại rồi chạy lại "
                          f"preflight")
        # Tỉ lệ ảnh bằng chứng (lệnh CEO 13/11/2026, sửa cùng ngày — 3
        # trường hợp): trang trong khoảng 3:4–4:3 thì dùng nguyên trang,
        # KHÔNG cảnh báo gì; trang DAI HON 3:4 (tỉ lệ < 0,75) thì GIỮ
        # LẠI, cắt ảnh 3:4 — file bằng chứng chưa cắt (cả trang dài) thì
        # CHẶN, báo cắt lại; trang RONG HON 4:3 (tỉ lệ > 1,33, trang quá
        # ngắn) thì CHẶN, loại nguồn, tìm nguồn báo khác. Chỉ bỏ trang
        # quá ngắn.
        for _pid6, _v6, _o6 in _resolved:
            if _pid6 in _ev_parts and _v6 is not None and _v6.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                try:
                    from PIL import Image
                    with Image.open(_v6) as _im6:
                        _w6, _h6 = _im6.size
                    _r6 = _w6 / _h6
                    if _r6 < 0.75 - 0.01:
                        errors.append(f"Part {_pid6} dùng ảnh bằng chứng {_v6.name} "
                                      f"({_w6}x{_h6}, tỉ lệ rộng/cao {_r6:.2f} dài hơn 3:4) — "
                                      f"giữ lại trang này, cắt ảnh 3:4 bằng "
                                      f"bin/pdf_crop.py --full-page rồi chạy lại preflight")
                    elif _r6 > 4 / 3 + 0.01:
                        errors.append(f"Part {_pid6} dùng ảnh bằng chứng {_v6.name} "
                                      f"({_w6}x{_h6}, tỉ lệ rộng/cao {_r6:.2f} rộng hơn 4:3, "
                                      f"trang quá ngắn) — loại nguồn này, tìm nguồn "
                                      f"báo khác rồi chạy lại preflight")
                except Exception:
                    pass

        # Trần xuất hiện tối đa 2 lần/video (quy tắc CEO 09/11/2026,
        # DEC-272): mỗi file visual nội dung chỉ xuất hiện tối đa 2 lần
        # trong toàn video. Đếm theo NỘI DUNG (dhash, Hamming ≤ 10 —
        # chuyển từ md5 theo quyết CEO 13/11/2026, L8), không đếm theo
        # tên file hay md5 — cùng 1 ảnh qua 2 nguồn khác nhau (vd VFF
        # vs Dân trí), re-encode hay crop nhẹ thì md5 khác nhau nhưng
        # dhash gần nhau nên vẫn tính là 1 nội dung (người xem thấy cùng
        # 1 hình; tiền lệ TOPIC-345). Video mp4 giữ đếm theo md5 (không
        # hash frame). Trừ part nền trung tính (nền được miễn — dùng lại
        # qua các scene không giới hạn). Fill-in tính vào trần như visual
        # nội dung. Bookend (mở và đóng bằng cùng 1 file) tính là 2 lần
        # — được phép, không vi phạm nếu file đó không xuất hiện thêm lần
        # nào nữa. Vi phạm thì CHẶN render (exit 1) như luật kề nhau.
        _dhash_cache = {}

        def _file_dhash(_p):
            # Trả (kind, key): ("dhash", ImageHash) nếu hash được,
            # ("md5", hex) nếu PIL không đọc được ảnh (rơi về md5 để
            # preflight vẫn báo lỗi ở các cửa khác thay vì crash).
            _k = str(_p)
            if _k not in _dhash_cache:
                try:
                    import imagehash
                    from PIL import Image
                    _im = Image.open(_p)
                    # Giải mã ở cỡ nhỏ (draft) trước khi hash — đỡ RAM
                    # (đo 13/11/2026: 21 ảnh đỉnh 67MB, vừa 100MB).
                    _im.draft("RGB", (720, 1280))
                    _dhash_cache[_k] = ("dhash", imagehash.dhash(_im))
                except Exception:
                    _dhash_cache[_k] = ("md5", _file_md5(_p))
            return _dhash_cache[_k]

        _appear = []  # [(kind, key, [(partId, Path)])] theo thứ tự part
        for _pid3, _v3, _o3 in _resolved:
            if _v3 is None or _pid3 in _neutral_parts:
                continue
            if _v3.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                _kind3, _key3 = _file_dhash(_v3)
            else:  # mp4/video: giữ đếm theo md5
                _kind3, _key3 = "md5", _file_md5(_v3)
            if _kind3 == "dhash":
                _grp = next((_g for _g in _appear
                             if _g[0] == "dhash" and (_key3 - _g[1]) <= 10),
                            None)
            else:
                _grp = next((_g for _g in _appear
                             if _g[0] == "md5" and _g[1] == _key3), None)
            if _grp is None:
                _appear.append([_kind3, _key3, [(_pid3, _v3)]])
            else:
                _grp[2].append((_pid3, _v3))
        for _kind, _key, _items in _appear:
            if len(_items) > 2:
                _names = ", ".join(_pid for _pid, _ in _items)
                errors.append(f"Trần xuất hiện tối đa 2 lần/video (DEC-272): "
                              f"nội dung của file {_items[0][1].name} xuất hiện "
                              f"{len(_items)} lần ở các part {_names} — mỗi "
                              f"file visual nội dung chỉ được xuất hiện tối "
                              f"đa 2 lần trong 1 video (trừ ảnh/video trung "
                              f"tính). Thay visual cho một số part (visual "
                              f"khác trong pool, AI trong trần, hoặc crop "
                              f"chi tiết hạn chế) rồi chạy lại preflight")

        # Trần AI ≤ thật theo scene (quy tắc CEO 09/11/2026, DEC-244;
        # C1 rà soát lần 9, quyết CEO 10/11/2026, phương án C1-A): mỗi
        # scene số file AI không được vượt số file thật. Đếm theo file
        # khác nhau (md5), tính riêng theo từng vai trò như QA đếm tay
        # (skill QA): vế thật = file thật nguyên khung + nền trung tính
        # (kể cả ảnh giải thích Vector/Infographic/Concept Art — file
        # thật tìm trên web, quyết CEO 10/11/2026, A2); crop chi tiết
        # KHÔNG cộng vào vế thật (DEC-242); fill-in KHÔNG cộng vào vế
        # thật (F5). Phân loại theo media-log danh sách `parts`
        # (classification "ai"/"ai-tu-prompt" hoặc promptRecord = AI;
        # "trung-tinh" = nền; "chup-man-hinh" = ảnh bằng chứng từ
        # PDF bài báo, tính thật (v1 13/11/2026); ghi chú có "crop chi
        # tiết" = crop; ghi chú có "fill-in" = fill-in; còn lại = thật); part không
        # có dòng parts thì lấy phân loại ảnh scene từ media-log danh
        # sách `scenes` (chosen.classification), và b-roll riêng không
        # có dòng parts thì lấy theo broll.prompt trong plan (có prompt
        # = AI, không prompt = thật). Thiếu phân loại cho 1 part/scene
        # thì mặc định thật (tránh chặn oan) và QA kiểm lại bằng tay.
        def _c1_classify_entry(_e):
            if not isinstance(_e, dict):
                return None
            _txts = []
            for _k in ("classification", "note", "ghi_chu"):
                _v = _e.get(_k)
                if isinstance(_v, str):
                    _txts.append(_v)
            _ch = _e.get("chosen")
            if isinstance(_ch, dict):
                for _k in ("classification", "note", "ghi_chu"):
                    _v = _ch.get(_k)
                    if isinstance(_v, str):
                        _txts.append(_v)
            _cls = _e.get("classification")
            if isinstance(_ch, dict) and _ch.get("classification"):
                _cls = _ch.get("classification")
            if _cls in ("ai", "ai-tu-prompt") or _e.get("promptRecord") or (
                    isinstance(_ch, dict) and _ch.get("promptRecord")):
                return "ai"
            # Ảnh bằng chứng từ PDF bài báo (v1 13/11/2026, quyết CEO):
            # là ảnh thật — tính vào vế thật của trần AI ≤ thật (như nền
            # trung tính và ảnh giải thích). Ghi rõ nhánh này thay vì dựa
            # vào fallback `if _cls: return "real"` ở dưới.
            if _cls == "chup-man-hinh":
                return "real"
            _joined = " ".join(_txts)
            if "trung-tinh" in _joined or "nền trung tính" in _joined:
                return "neutral"
            _low = _joined.lower()
            if "crop chi tiết" in _low or "detail crop" in _low:
                return "crop"
            if "fill-in" in _low or "fill in" in _low:
                return "fillin"
            if _cls:
                return "real"
            return None

        _c1_mlog = None
        try:
            _c1_mlog = _mlog
        except NameError:
            _c1_mlog = None
        _part_cls = {}
        for _e in (_parts_list or []):
            if isinstance(_e, dict) and _e.get("partId"):
                _part_cls[_e["partId"]] = _c1_classify_entry(_e)
        _scene_cls = {}
        if isinstance(_c1_mlog, dict):
            for _s in (_c1_mlog.get("scenes") or []):
                if not isinstance(_s, dict):
                    continue
                _sid = _s.get("sceneId") or ""
                try:
                    _so = int(str(_sid).rsplit("-", 1)[1])
                except (ValueError, IndexError):
                    continue
                _sch = _s.get("chosen") or {}
                _sc = _sch.get("classification") if isinstance(_sch, dict) else None
                _scene_cls[_so] = "ai" if _sc in ("ai", "ai-tu-prompt") else "real"
        _prompt_by_id = {}
        for _sc2 in plan["scenes"]:
            for _p2 in _sc2["parts"]:
                _br2 = (_p2 or {}).get("broll") or {}
                _prompt_by_id[_p2["id"]] = bool(
                    isinstance(_br2.get("prompt"), str) and _br2["prompt"].strip())
        _ai_by_scene = {}
        _real_by_scene = {}
        for _pid5, _v5, _o5 in _resolved:
            if _v5 is None:
                continue
            _c5 = _part_cls.get(_pid5)
            if _c5 is None:
                if _v5.name.startswith("broll_seg_"):
                    _c5 = "ai" if _prompt_by_id.get(_pid5) else "real"
                else:
                    _c5 = _scene_cls.get(_o5, "real")
            if _c5 == "ai":
                _ai_by_scene.setdefault(_o5, set()).add(_file_md5(_v5))
            elif _c5 in ("real", "neutral"):
                _real_by_scene.setdefault(_o5, set()).add(_file_md5(_v5))
            # crop / fill-in: không cộng vào vế nào
        for _o6 in sorted(set(list(_ai_by_scene) + list(_real_by_scene))):
            _na = len(_ai_by_scene.get(_o6, set()))
            _nr = len(_real_by_scene.get(_o6, set()))
            if _na > _nr:
                errors.append(f"Trần AI ≤ thật theo scene (DEC-244): Scene {_o6} có {_na} file AI nhưng chỉ {_nr} file thật — mỗi scene số file AI không được vượt số file thật (ảnh giải thích Vector/Infographic/Concept Art, nền trung tính và ảnh bằng chứng từ PDF bài báo tính vào vế thật; crop chi tiết và fill-in không cộng vào vế thật). Thay 1 file AI bằng visual thật trong pool (ảnh thật, ảnh giải thích, hoặc nền trung tính nếu scene chưa dùng nền) rồi chạy lại preflight")

    # karaoke
    kj = build / "subtitles" / "karaoke.json"
    if not kj.exists():
        warnings.append("Chưa có karaoke (phụ đề sẽ là SRT thường)")
    else:
        k = json.loads(kj.read_text(encoding="utf-8"))
        if len(k) != n_parts:
            warnings.append(f"karaoke có {len(k)} parts, plan có {n_parts}")
        # Sửa đợt B 01/11/2026 (chỉ warning): part có template thì lines=0
        # là đúng thiết kế (phụ đề ẩn). Part KHÔNG template mà lines=0 là
        # dấu hiệu dàn dựng/phụ đề lỗi — cảnh báo khi xảy ra trên diện
        # rộng (>= 2 part, hoặc toàn bộ part không template đều 0).
        _tpl_ids = {p["id"] for sc in plan["scenes"] for p in sc["parts"]
                    if (p.get("broll") or {}).get("templateId")}
        _zero, _nontpl = [], 0
        for _e in (k if isinstance(k, list) else []):
            _pid = _e.get("partId")
            if _pid in _tpl_ids:
                continue
            _nontpl += 1
            if not _e.get("lines"):
                _zero.append(_pid)
        if _zero and (len(_zero) >= 2 or len(_zero) == _nontpl):
            warnings.append(
                f"karaoke lines=0 ở {len(_zero)}/{_nontpl} part không "
                f"template ({', '.join(_zero[:5])}) — kiểm tra dàn dựng "
                f"và phụ đề trước khi render")
        # B29 (06/11/2026, lệnh CEO, lựa chọn A): karaoke ghi dấu
        # "fallback" vào từng part khi WAV mất/hỏng hoặc thiếu entry
        # norm_chunks — timing chia đều, phụ đề có thể lệch giọng.
        _fb = [(_e.get("partId"), _e.get("fallback"))
               for _e in (k if isinstance(k, list) else [])
               if isinstance(_e, dict) and _e.get("fallback")]
        if _fb:
            _fb_txt = ", ".join(f"{_pid} ({_why})" for _pid, _why in _fb[:5])
            _more = f" và {len(_fb) - 5} part khác" if len(_fb) > 5 else ""
            warnings.append(
                f"karaoke fallback timing ở {len(_fb)} part ({_fb_txt}{_more}) — phụ đề chia đều thời gian, có thể lệch giọng đọc; kiểm tra lại WAV/norm_chunks rồi chạy lại karaoke")

    # BGM
    bgm = plan.get("bgm")
    if not bgm:
        warnings.append("Chưa chọn nhạc nền (BGM)")
    elif not isinstance(bgm, dict):
        # R3-31 (09/11/2026, rà soát lần 3): bgm không phải dict (vd chuỗi
        # "track.mp3" do sửa tay plan) — trước đây bgm.get("file") crash
        # AttributeError; nay báo lỗi rõ thay vì crash.
        errors.append("BGM trong plan không phải dict (vd chuỗi tên file do sửa tay) — ghi BGM dạng dict {file: ...} hoặc bỏ chọn BGM")
    else:
        # B27 (06/11/2026, lệnh CEO, lựa chọn A): bgm có mà file rỗng/
        # thiếu thì CHẶN — trước đây FACTORY/"bgm"/"" chính là thư mục
        # bgm/ nên .exists() luôn True, preflight lọt, render/assemble
        # lại guard bằng if bgm.get("file") nên bỏ qua lặng lẽ.
        _bf = bgm.get("file")
        if not (isinstance(_bf, str) and _bf.strip()):
            errors.append("BGM đã chọn nhưng thiếu tên file (bgm.file trống/thiếu) — ghi rõ file BGM trong plan hoặc bỏ chọn BGM")
        else:
            bf = FACTORY / "bgm" / _bf
            if not bf.exists():
                errors.append(f"BGM không tồn tại: {bgm.get('file')}")

    # đồng bộ thời lượng audio tổng
    total = sum(p.get("duration", 0) for p in tts["parts"])
    if tts["parts"] and total <= 0:
        errors.append("Tổng thời lượng audio = 0")
    # Thời lượng (sửa đợt A 01/11/2026 theo lệnh CEO tối 29/10/2026):
    # Production TỰ QUYẾT độ dài, đề xuất 2–3 phút, video dài hơn vẫn chấp
    # nhận khi nội dung đã kiểm chứng — không còn mức chặn thời lượng cũ và
    # không cần xin ngoại lệ. Chỉ cảnh báo để người chạy kiểm tra lại
    # chiều sâu kịch bản, không thành lỗi.
    if tts["parts"] and 0 < total < 120:
        warnings.append(f"Video chỉ {total:.1f}s, dưới đề xuất 2–3 phút "
                        f"(lệnh CEO 29/10/2026: Production tự quyết độ dài, "
                        f"không cần xin ngoại lệ) — kiểm tra kịch bản đã "
                        f"đủ chiều sâu, không độn cho đủ phút")
    if tts["parts"] and total > 180:
        warnings.append(f"Video dài {total:.1f}s, trên đề xuất 2–3 phút — "
                        f"theo lệnh CEO 29/10/2026 Production tự quyết, "
                        f"không cần xin ngoại lệ; chỉ cần nội dung đã kiểm "
                        f"chứng và ghi thời lượng thật vào bàn giao")
    # Cảnh báo zero-SFX (sửa đợt A 01/11/2026 theo luật SFX-meta 31/10/2026):
    # SFX theo đúng meta từng part có template + đủ 3 beat hook/móc lại/
    # kết luận; khung 3–7 cũ không còn là mức chặn. Chỉ cảnh báo tại
    # preflight để không chặn clip test kỹ thuật.
    if n_parts > 0 and n_sfx == 0:
        warnings.append("Video có 0 SFX trong plan — luật SFX hiện hành: "
                        "SFX theo đúng meta từng part có template + đủ 3 "
                        "beat hook/móc lại/kết luận; bổ sung trước khi "
                        "render (QA sẽ trả lại video 0 SFX)")
    # Sửa đợt B 01/11/2026 (chỉ warning): kiểm tra SFX ở đúng 3 beat.
    # Hook = part đầu, kết luận = part cuối (vị trí tuyệt đối). Móc lại
    # là beat ở giữa video theo thiết kế kịch bản, không có marker tuyệt
    # đối trong plan, nên chỉ kiểm tra nới: có ít nhất một part có SFX mà
    # điểm giữa của nó rơi vào khoảng 30–70% tổng thời lượng. Thiếu beat
    # nào thì cảnh báo beat đó, không thành lỗi.
    if tts["parts"] and plan["scenes"]:
        _sfx_by_id = {}
        for _sc in plan["scenes"]:
            for _p in _sc["parts"]:
                _ids = _part_sfx_ids(_p.get("broll") or {})
                _sfx_by_id[_p["id"]] = _ids[0] if _ids else None
        _ordered = [p["id"] for sc in plan["scenes"] for p in sc["parts"]]
        if not _sfx_by_id.get(_ordered[0]):
            warnings.append(f"Beat hook (part {_ordered[0]}) chưa có SFX "
                            f"trong plan — luật SFX yêu cầu đủ 3 beat "
                            f"hook/móc lại/kết luận")
        if not _sfx_by_id.get(_ordered[-1]):
            warnings.append(f"Beat kết luận (part {_ordered[-1]}) chưa có "
                            f"SFX trong plan — luật SFX yêu cầu đủ 3 beat "
                            f"hook/móc lại/kết luận")
        _has_mid = False
        for _tp in tts["parts"]:
            if not _sfx_by_id.get(_tp["id"]):
                continue
            _mid = (_tp.get("startSec", 0) + _tp.get("endSec", 0)) / 2
            if 0.3 * total <= _mid <= 0.7 * total:
                _has_mid = True
                break
        if not _has_mid:
            warnings.append("Không có part nào có SFX ở khoảng giữa video "
                            "(điểm giữa part trong 30–70% tổng thời lượng) "
                            "— luật SFX yêu cầu beat móc lại (~50%) có SFX")

    report = {"pid": pid, "parts": n_parts,
              "duration_sec": round(total, 1),
              "errors": errors, "warnings": warnings,
              "ok": not errors}
    if "--json" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=1))
    else:
        print(f"=== PREFLIGHT {pid} ===")
        print(f"parts={n_parts} duration={total:.1f}s")
        for e in errors:
            print(f"  [LỖI] {e}")
        for w in warnings:
            print(f"  [chú ý] {w}")
        print("KẾT QUẢ:", "ĐẠT ✓" if not errors else "CHƯA ĐẠT ✗")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
