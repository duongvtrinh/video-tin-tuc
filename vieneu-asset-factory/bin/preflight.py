#!/usr/bin/env python3
"""Checklist trước khi xuất project: báo lỗi/thiếu sót cần sửa.

    python3 preflight.py <project_id> [--json]

Kiểm tra: audio từng part, ảnh scene/b-roll, karaoke, template inputs,
BGM đã chọn, đồng bộ thời lượng, file export.
Exit 0 nếu không có lỗi nghiêm trọng, 1 nếu có.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import rand6  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent


def main() -> int:
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    errors, warnings = [], []

    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
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

    # BGM
    bgm = plan.get("bgm")
    if not bgm:
        warnings.append("Chưa chọn nhạc nền (BGM)")
    else:
        bf = FACTORY / "bgm" / bgm.get("file", "")
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
