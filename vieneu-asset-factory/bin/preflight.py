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
  scene chưa có ảnh (render sẽ ra clip nền đen); template không tồn
  tại / meta.json hỏng / inputs không phải dict; thiếu input bắt buộc
  của template; BGM đã chọn nhưng file không tồn tại; SFX đã chọn
  nhưng file không tồn tại (A26, 05/11/2026); tổng thời lượng
  audio = 0; scene thiếu nguồn media (mediaSource.source trống/thiếu)
  hoặc thiếu nhật ký tìm ảnh (media-log.json không có, hoặc scene
  không có mục nhật ký, hoặc keywordsTried trống/thiếu) — cửa chặn
  ảnh thật, lệnh CEO 05/11/2026 (lựa chọn A20). Scene chỉ có nền
  xanh rêu kẻ ô (không có mediaSource) cũng chặn ở đây, vì nền xanh
  rêu không tính là ảnh. Miễn cửa provenance cho project test kỹ
  thuật (pid bắt đầu bằng "test", vd test001 fixture).
- CẢNH BÁO (exit 0): b-roll video khai nhưng thiếu file mp4 (render
  rơi về ảnh scene); karaoke thiếu hoặc lệch số part / lines=0 diện
  rộng ở part không template / có part fallback timing (WAV hỏng/mất
  hoặc thiếu entry norm_chunks); chưa chọn BGM; video dưới 120s hoặc trên
  180s (Production tự quyết độ dài); 0 SFX hoặc thiếu beat SFX
  hook/móc lại/kết luận; input template vượt maxLength; template gợi ý
  SFX nhưng plan chưa có broll.sfx.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import check_plan, img_decode_error, rand6  # noqa: E402

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
    build = proj / "build"
    n_parts = 0
    n_sfx = 0
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
            errors.append(f"Scene {order} chưa có ảnh — render sẽ ra "
                          f"clip nền đen cho scene này, phải tạo ảnh "
                          f"trước (generateImages: job AI hoặc card)")
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
            if (br.get("sfx") or {}).get("id"):
                n_sfx += 1
                # A26 (05/11/2026, lệnh CEO): SFX khai trong plan nhưng
                # file mp3 không tồn tại thì LỖI như BGM thiếu — trước
                # đây render chỉ log sfx-thieu-bo-qua rồi render tiếp
                # không tiếng đó.
                _sf = FACTORY / "sfx" / f"{br['sfx']['id']}.mp3"
                if not _sf.exists():
                    errors.append(
                        f"Part {p['id']}: SFX '{br['sfx']['id']}' không tồn tại "
                        f"({_sf.name} trong thư mục sfx) — render sẽ thiếu tiếng này")
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
                                ml = idef.get("maxLength")
                                if ml and len(str(v)) > ml:
                                    warnings.append(
                                        f"Part {p['id']}: '{name}' dài "
                                        f"{len(str(v))}>{ml} ký tự")
                    # Sửa 29/10/2026 (code-fix, audit D-L6): render chỉ đọc
                    # SFX từ plan, không bao giờ đọc meta template. Nếu
                    # template gợi ý SFX mà plan chưa copy thì SFX đó mất
                    # lặng lẽ — cảnh báo để Production copy vào plan theo
                    # luật SFX, KHÔNG tự copy lặng lẽ.
                    meta_sfx = meta.get("sfx")
                    meta_sfx_id = (meta_sfx.get("id") if isinstance(meta_sfx, dict)
                                   else meta_sfx if isinstance(meta_sfx, str) else None)
                    if meta_sfx_id and not (br.get("sfx") or {}).get("id"):
                        warnings.append(
                            f"Part {p['id']}: template {br['templateId']} gợi ý "
                            f"SFX '{meta_sfx_id}' nhưng plan chưa có broll.sfx "
                            f"— copy vào plan trước khi render (render chỉ đọc "
                            f"SFX từ plan, không đọc meta template)")

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
                _sfx_by_id[_p["id"]] = ((_p.get("broll") or {}).get("sfx")
                                        or {}).get("id")
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
