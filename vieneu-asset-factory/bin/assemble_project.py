#!/usr/bin/env python3
"""Đóng gói project VieNeu Asset Factory thành thư mục chuẩn schema 2.0 + ZIP.

Đọc:  projects/<id>/{input.json, script.json, broll-plan.json, tts.json}
      projects/<id>/build/{audio/voice/**, media/images/*, media/broll/*}
Ghi:  projects/<id>/build/{project.json, timeline.json, subtitles/*.srt,
                            audio/sfx/*, googleFlow/config.json, README_HUONG_DAN.txt}
      projects/<id>/export/<id>.zip
      (ZIP chứa toàn bộ build/ TRỪ file silence_*, cộng thêm ở root <id>/:
       abbr_dict.json nếu project có file từ điển ở gốc (để VieNeu Studio
       local đọc được), broll-plan.json (gốc sự thật của plan, gồm
       plan.bgm), và audio/bgm/<file BGM> nếu plan chọn BGM và file tồn
       tại trong factory/bgm/ — chốt Giai đoạn 4, 05/11/2026: ZIP KHÔNG
       còn "không chứa BGM" như trước. Lưu ý: file BGM trong ZIP chỉ là
       bản kèm theo để Studio/máy khác có nhạc mà không cần factory/bgm/;
       timeline.json/project.json hiện không trỏ tới audio/bgm/ nên
       Studio muốn dùng phải tự nối theo plan.bgm trong broll-plan.json
       kèm theo — việc nối tự động đó thuộc đợt sau, không tự nhận là
       đã nối. BGM thiếu file thì CHẶN assemble (13B, 05/11/2026),
       khớp hành vi preflight và render_draft.)
      aspectRatio mặc định khi thiếu field là "9:16" (chốt Giai đoạn 4,
      khớp render_draft/karaoke/build_render_page/render_scene_card).

Quy ước (khớp bản local): JSON UTF-8 ensure_ascii=False; URL media dạng
/projects/<id>/...; tên file seg_<order>_<rand6>.* / broll_seg_<order>_part_<p>_<rand6>.*
"""
import json
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import atomic_write_text, check_plan, rand6  # noqa: E402  (single source of truth)

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)



def srt_ts(sec: float) -> str:
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: assemble_project.py <project_id>", file=sys.stderr)
        return 2
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    build = proj / "build"

    try:
        inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
        script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
        plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
        tts = json.loads((proj / "tts.json").read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ASSEMBLE-ERROR {pid}: không đọc được input/script/plan/tts: {exc}",
              file=sys.stderr)
        return 1
    try:
        scenes = check_plan(plan, require_voice_text=True)
    except ValueError as exc:
        # Giai đoạn 5: plan thiếu key báo rõ key nào, dừng trước khi ghi
        # bất kỳ output nào — không crash trần, không coi plan hỏng là rỗng.
        print(f"ASSEMBLE-ERROR {pid}: {exc}", file=sys.stderr)
        return 1
    # B26 (06/11/2026, lệnh CEO, lựa chọn A): kiểm BGM ngay đầu main —
    # trước đây chỉ kiểm trong khối ghi ZIP (sau khi đã ghi timeline.json,
    # project.json, SRT, googleFlow/config.json), nên project thiếu BGM để
    # lại output dở trên đĩa và ZIP cũ vẫn nằm đó dễ nhầm là mới. Cửa
    # chặn muộn trong khối ZIP vẫn còn làm backstop.
    _bgm = plan.get("bgm") or {}
    if _bgm.get("file"):
        _bgm_file = FACTORY / "bgm" / _bgm["file"]
        if not _bgm_file.is_file():
            print(f"ASSEMBLE-ERROR {pid}: BGM da chon {_bgm.get('file')} "
                  f"khong ton tai — dung dong goi, giong preflight",
                  file=sys.stderr)
            return 1
    if not isinstance(tts, dict) or not isinstance(tts.get("parts"), list) \
            or not isinstance(tts.get("scenes"), list):
        print(f"ASSEMBLE-ERROR {pid}: tts.json hỏng: phải có 'parts' và "
              f"'scenes' dạng list", file=sys.stderr)
        return 1
    try:
        part_map = {p["id"]: p for p in tts["parts"]}
        scene_map = {s["id"]: s for s in tts["scenes"]}
    except (KeyError, TypeError) as exc:
        print(f"ASSEMBLE-ERROR {pid}: tts.json thiếu key: {exc}", file=sys.stderr)
        return 1
    chunk_cues_path = proj / "build" / "subtitles" / "sent_cues.json"
    try:
        chunk_cues = (json.loads(chunk_cues_path.read_text(encoding="utf-8"))
                      if chunk_cues_path.exists() else [])
    except Exception:
        chunk_cues = []
    if not isinstance(chunk_cues, list):
        chunk_cues = []

    # Mặc định 9:16 khi thiếu field (chốt Giai đoạn 4).
    aspect = inp.get("aspectRatio", "9:16")
    voice = plan.get("voice", "Hữu Quân")
    speed = float(plan.get("speed", 1.0))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = lambda *a: "/projects/" + pid + "/" + "/".join(a)  # noqa: E731

    # ---- timeline.json ----
    segments = []
    srt_cues, sent_cues = [], []
    cue_n = 0
    thumb = None
    for sc in scenes:
        # Giai đoạn 5: scene/part có trong plan nhưng thiếu trong tts.json
        # là lỗi chặn, báo rõ ID — không KeyError trần giữa chừng (lúc
        # đó chưa ghi output nào nên dừng ở đây là an toàn).
        if sc["id"] not in scene_map:
            print(f"ASSEMBLE-ERROR {pid}: scene {sc['id']} có trong plan "
                  f"nhưng thiếu trong tts.json — chạy lại tts_batch trước",
                  file=sys.stderr)
            return 1
        ts = scene_map[sc["id"]]
        # Plan do pipeline ghi không có trường "text" ở cảnh (chỉ có
        # sceneScriptSummary + voiceText từng part) — text của cảnh theo
        # schema 2.0 là toàn văn lời đọc của cảnh, ghép từ các part.
        # Plan cũ có sẵn "text" thì dùng nguyên.
        scene_text = sc.get("text") or " ".join(
            (p.get("voiceText") or "").strip() for p in sc["parts"]
        ).strip()
        img_file = None
        for ext in ("jpg", "png", "webp"):
            cand = build / "media" / "images" / f"seg_{sc['order']}_{rand6(pid, 'img', str(sc['order']))}.{ext}"
            if cand.exists():
                img_file = cand.name
                break
        # R4-40 (07/11/2026, DEC-048, phương án A): bỏ qua cảnh nền rêu
        # khi chọn thumbnail — ảnh bìa không được là card nền rêu trơn;
        # nếu mọi cảnh đều rêu thì thumbnail để None (không bịa ảnh bìa).
        if img_file and thumb is None and not sc.get("isMossGrid"):
            thumb = url("media", "images", img_file)

        vparts = []
        for pi, p in enumerate(sc["parts"], start=1):
            if p["id"] not in part_map:
                print(f"ASSEMBLE-ERROR {pid}: part {p['id']} có trong plan "
                      f"nhưng thiếu trong tts.json — chạy lại tts_batch trước",
                      file=sys.stderr)
                return 1
            pt = part_map[p["id"]]
            br = p.get("broll") or {}
            broll = None
            if br:
                # tên file suy từ quy ước chung (filename.py); chỉ gắn URL khi file đã tồn tại
                br6 = rand6(pid, "broll", str(sc["order"]), str(pi))
                # B-roll có thể là video (quy tắc 27/10/2026): ưu tiên .mp4
                # nếu có, nếu không thì .jpg như trước.
                # 11A: b-roll co the la mp4/jpg/png/webp — thu theo thu tu do.
                fn = None
                for _ext in ("mp4", "jpg", "png", "webp"):
                    if (build / "media" / "broll" /
                            f"broll_seg_{sc['order']}_part_{pi}_{br6}.{_ext}").exists():
                        fn = f"broll_seg_{sc['order']}_part_{pi}_{br6}.{_ext}"
                        break
                if fn is None:
                    fn = f"broll_seg_{sc['order']}_part_{pi}_{br6}.jpg"
                has_file = (build / "media" / "broll" / fn).exists()
                broll = {
                    "url": url("media", "broll", fn) if has_file else None,
                    "filename": fn if has_file else None,
                    "mediaType": br.get("mediaType", "image"),
                    "duration": None,
                    "mode": br.get("mode", "overlay"),
                    "fit": "cover",
                    "sourceStartSec": 0,
                    "keepAudio": False,
                    "inputs": br.get("inputs", {}),
                    "templateId": br.get("templateId"),
                    "templateVersion": None,
                    "sfx": br.get("sfx"),
                    "keywords": br.get("keywords", []),
                    "agentNote": br.get("agentNote"),
                }
            vparts.append({
                "id": p["id"],
                "voiceText": p["voiceText"],
                # Per-part (chốt Giai đoạn 4): part có pauseAfterMs riêng
                # thì giữ riêng, không có thì dùng plan.pauseAfterMs
                # (mặc định 180ms). Trước đây dùng pause chung của plan
                # cho mọi part, lệch tts_batch.py (per-part) và lệch
                # duration thật trong tts.json (tts đã cộng pause riêng).
                "pauseAfterMs": p.get("pauseAfterMs",
                                      plan.get("pauseAfterMs", 180)),
                "duration": pt["duration"],
                "baseDuration": pt["duration"],
                "startSec": pt["startSec"],
                "endSec": pt["endSec"],
                "audio_file": pt["audio_file"],
                "broll": broll,
                "brollSuggestion": None,
            })
            cue_n += 1
            # synced_cues: ưu tiên mốc câu ngắn đã chuẩn hoá (chunk_cues.json);
            # không có thì lùi về mốc part như cũ
            # Giai đoạn 5: cue hỏng (thiếu key) bị bỏ qua thay vì
            # KeyError trần — cue là dữ liệu phụ, part vẫn có mốc SRT.
            chunked = [c for c in chunk_cues
                       if isinstance(c, dict) and c.get("partId") == p["id"]
                       and isinstance(c.get("start"), (int, float))
                       and isinstance(c.get("end"), (int, float))
                       and isinstance(c.get("text"), str)]
            if chunked:
                for cc in chunked:
                    cue_n += 1
                    srt_cues.append(
                        f"{cue_n}\n{srt_ts(cc['start'])} --> {srt_ts(cc['end'])}\n{cc['text']}\n")
            else:
                srt_cues.append(
                    f"{cue_n}\n{srt_ts(pt['startSec'])} --> {srt_ts(pt['endSec'])}\n{p['voiceText']}\n")

        sent_cues.append(
            f"{sc['order']}\n{srt_ts(ts['startSec'])} --> {srt_ts(ts['endSec'])}\n{scene_text}\n")

        segments.append({
            "id": sc["id"],
            "order": sc["order"],
            "text": scene_text,
            "startSec": ts["startSec"],
            "endSec": ts["endSec"],
            "duration": ts["duration"],
            "effect": sc.get("effect", "zoomIn"),
            "image": url("media", "images", img_file) if img_file else None,
            "mediaType": "image",
            "ai_prompt": sc.get("ai_prompt"),
            "keywords": sc.get("keywords", []),
            "audio_file": ts["audio_file"],
            "manualImages": ([{"previewUrl": url("media", "images", img_file),
                               "filename": img_file}] if img_file else []),
            "selectedImageIdx": 0,
            "voiceParts": vparts,
            "soundClip": None,
            "memeClip": None,
        })

    (build / "subtitles").mkdir(parents=True, exist_ok=True)
    # Giai đoạn 5: mọi output JSON/SRT/README ghi tạm rồi rename.
    atomic_write_text(build / "subtitles" / "synced_cues.srt", "\n".join(srt_cues))
    atomic_write_text(build / "subtitles" / "sentences.srt", "\n".join(sent_cues))

    timeline = {
        "version": "2.0",
        "projectId": pid,
        "totalDuration": tts["totalDuration"],
        "currentTime": 0.0,
        "isSfxMuted": False,
        "sfxVolume": 0.8,
        "bgLayers": [],
        "segments": segments,
    }
    atomic_write_text(build / "timeline.json",
                      json.dumps(timeline, ensure_ascii=False, indent=2))

    # ---- project.json ----
    project = {
        "version": "2.0",
        "id": pid,
        "name": inp.get("name", pid),
        "created_at": inp.get("created_at", now),
        "updated_at": now,
        "script": {"topic": script.get("topic", ""), "content": script.get("content", ""),
                   "sentences": script.get("sentences", [])},
        "settings": {"aspectRatio": aspect, "subFormat": "srt",
                     "voiceId": voice, "voiceSpeed": speed},
        "voiceConfig": {},
        "summary": {"totalDuration": tts["totalDuration"],
                    "segmentCount": len(segments),
                    "hasMasterVoice": True, "thumbnail": thumb},
    }
    atomic_write_text(build / "project.json",
                      json.dumps(project, ensure_ascii=False, indent=2))

    # ---- SFX kèm theo ----
    sfx_dir = build / "audio" / "sfx"
    sfx_dir.mkdir(parents=True, exist_ok=True)
    sfx_files = sorted((FACTORY / "sfx").glob("*.mp3"))
    if not sfx_files:
        print("CẢNH BÁO: sfx/ rỗng — ZIP xuất ra sẽ không có SFX "
              "(lấy 8 file từ thư mục Drive 'sfx' theo BOOTSTRAP §7)",
              file=sys.stderr)
    for f in sfx_files:
        shutil.copy2(f, sfx_dir / f.name)

    # ---- googleFlow/config.json (để extension tạo video local cho part needVideo) ----
    gf_items = []
    # B25 (06/11/2026, lệnh CEO, lựa chọn A): segIdx là chỉ số thật của
    # scene trong danh sách segments (vị trí vòng lặp), không phải
    # order - 1 — sau khi cắt scene, order khuyết (vd 1-9,11,12) nên
    # order - 1 lệch 1 từ chỗ cắt trở đi.
    for seg_idx, sc in enumerate(scenes):
        r6 = rand6(pid, "img", str(sc["order"]))
        if sc.get("sceneImagePrompt"):
            gf_items.append({
                "prompt": sc["sceneImagePrompt"], "ratio": aspect, "quality": "standard",
                "segIdx": seg_idx, "taskType": "scene", "segOrder": sc["order"],
                "partIdx": None, "partOrder": None, "partId": None,
                "targetFilename": f"seg_{sc['order']}_{r6}", "subDir": "media/images",
                "mediaType": "image", "projectId": pid,
            })
        for pi, p in enumerate(sc["parts"], start=1):
            br = p.get("broll") or {}
            if br.get("mediaPrompt"):
                br6 = rand6(pid, "broll", str(sc["order"]), str(pi))
                gf_items.append({
                    "prompt": br["mediaPrompt"], "ratio": aspect, "quality": "standard",
                    "segIdx": seg_idx, "taskType": "broll", "segOrder": sc["order"],
                    "partIdx": pi - 1, "partOrder": pi, "partId": p["id"],
                    "targetFilename": f"broll_seg_{sc['order']}_part_{pi}_{br6}",
                    "subDir": "media/broll",
                    "mediaType": "video" if br.get("needVideo") else "image",
                    "projectId": pid,
                })
    gf_dir = build / "googleFlow"
    gf_dir.mkdir(parents=True, exist_ok=True)
    atomic_write_text(gf_dir / "config.json",
                      json.dumps({"projectId": pid, "projectName": inp.get("name", pid),
                                  "items": gf_items}, ensure_ascii=False, indent=2))

    # ---- README ----
    plan_data = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    bgm_note = ""
    _bgm = plan_data.get("bgm") or {}
    if _bgm.get("attribution"):
        bgm_note = (f"\nNHẠC NỀN (ghi công khi đăng YouTube/Facebook):\n"
                    f"{_bgm['attribution']}\n")
    atomic_write_text(
        build / "README_HUONG_DAN.txt",
        "VieNeu Asset Factory — project tạo bởi agent Muse\n"
        f"Project: {pid}\n"
        f"{bgm_note}\n"
        "CÁCH DÙNG:\n"
        "1. Copy toàn bộ thư mục này vào thư mục projects/ của VieNeu Studio trên máy bạn.\n"
        "2. Mở VieNeu Studio → Video Studio → Quản lý dự án → mở project.\n"
        "3. Giọng đọc đã có sẵn (audio/voice/). Muốn đổi giọng: bấm 'Tạo giọng toàn bộ'.\n"
        "4. B-roll chữ render tự động lúc xuất video (templateId + inputs đã điền sẵn).\n"
        "5. Part nào cần video: mở googleFlow/config.json, dùng extension tạo rồi\n"
        "   copy file .mp4 vào media/broll/ đúng tên targetFilename.\n"
        "6. Bấm 'Xuất Video' để render.\n")

    # ---- ZIP ----
    # Giai đoạn 5: ghi ZIP tạm rồi rename — ZIP cũ còn nguyên nếu ghi
    # thất bại giữa chừng, không bao giờ để lại ZIP dở mang tên thật.
    exp_dir = proj / "export"
    exp_dir.mkdir(parents=True, exist_ok=True)
    zip_path = exp_dir / f"{pid}.zip"
    zip_tmp = exp_dir / f".{pid}.zip.tmp"
    _bgm_note = "bgm=none"
    try:
        with zipfile.ZipFile(zip_tmp, "w", zipfile.ZIP_DEFLATED) as z:
            for f in sorted(build.rglob("*")):
                if f.is_file():
                    if f.name.startswith("silence_"):
                        continue  # file phụ lúc nối WAV, không đưa vào project cuối
                    # B31 (06/11/2026, lệnh CEO, lựa chọn A): file tạm
                    # của build preview — _thumb_* và render_page.html
                    # (chứa base64 toàn bộ ảnh) — không đưa vào ZIP.
                    if f.name.startswith("_thumb_") or f.name == "render_page.html":
                        continue
                    # zip chứa thư mục <pid>/... để user bung thẳng vào projects/
                    z.write(f, Path(pid) / f.relative_to(build))
            # từ điển viết tắt (nếu có): file ở gốc project, không nằm trong
            # build/ nên phải thêm riêng; đặt cùng cấp project.json trong ZIP
            # để VieNeu Studio local đọc được sau khi bung vào projects/
            abbr = proj / "abbr_dict.json"
            if abbr.is_file():
                z.write(abbr, Path(pid) / "abbr_dict.json")
            # broll-plan.json (gốc sự thật của plan, gồm plan.bgm) cũng nằm
            # ngoài build/ nên thêm riêng cùng cấp, để máy nhận ZIP vẫn biết
            # BGM nào đã chọn và attribution nào phải ghi công.
            z.write(proj / "broll-plan.json", Path(pid) / "broll-plan.json")
            # BGM: file nhạc thật từ factory/bgm/ vào audio/bgm/ trong ZIP.
            # 13B (05/11/2026): plan chọn BGM mà file không tồn tại thì CHẶN
            # (tra ve 1, khong ghi ZIP), nhu preflight — khong canh bao roi
            # dong goi ZIP khong nhac lang le nua.
            _bgm = plan.get("bgm") or {}
            if _bgm.get("file"):
                _bgm_file = FACTORY / "bgm" / _bgm["file"]
                if _bgm_file.is_file():
                    z.write(_bgm_file, Path(pid) / "audio" / "bgm" / _bgm_file.name)
                    _bgm_note = f"bgm={_bgm.get('id') or _bgm_file.name}"
                else:
                    print(f"ASSEMBLE-ERROR {pid}: BGM da chon {_bgm.get('file')} "
                          f"khong ton tai — dung dong goi, giong preflight",
                          file=sys.stderr)
                    zip_tmp.unlink(missing_ok=True)
                    return 1
    except Exception as exc:
        # ZIP dở chỉ nằm ở file tạm, ZIP cũ (nếu có) còn nguyên.
        zip_tmp.unlink(missing_ok=True)
        print(f"ASSEMBLE-ERROR {pid}: ghi ZIP thất bại: {exc}", file=sys.stderr)
        return 1
    os.replace(zip_tmp, zip_path)
    print(f"ASSEMBLE-OK zip={zip_path} size={zip_path.stat().st_size//1024}KB "
          f"segments={len(segments)} duration={tts['totalDuration']}s "
          f"{_bgm_note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
