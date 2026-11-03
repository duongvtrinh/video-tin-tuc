#!/usr/bin/env python3
"""Đóng gói project VieNeu Asset Factory thành thư mục chuẩn schema 2.0 + ZIP.

Đọc:  projects/<id>/{input.json, script.json, broll-plan.json, tts.json}
      projects/<id>/build/{audio/voice/**, media/images/*, media/broll/*}
Ghi:  projects/<id>/build/{project.json, timeline.json, subtitles/*.srt,
                            audio/sfx/*, googleFlow/config.json, README_HUONG_DAN.txt}
      projects/<id>/export/<id>.zip
      (ZIP chứa thêm <id>/abbr_dict.json nếu project có file từ điển ở gốc,
       để VieNeu Studio local đọc được)

Quy ước (khớp bản local): JSON UTF-8 ensure_ascii=False; URL media dạng
/projects/<id>/...; tên file seg_<order>_<rand6>.* / broll_seg_<order>_part_<p>_<rand6>.*
"""
import json
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import rand6  # noqa: E402  (single source of truth)

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent


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

    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    script = json.loads((proj / "script.json").read_text(encoding="utf-8"))
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    tts = json.loads((proj / "tts.json").read_text(encoding="utf-8"))
    chunk_cues_path = proj / "build" / "subtitles" / "sent_cues.json"
    chunk_cues = (json.loads(chunk_cues_path.read_text(encoding="utf-8"))
                  if chunk_cues_path.exists() else [])
    part_map = {p["id"]: p for p in tts["parts"]}
    scene_map = {s["id"]: s for s in tts["scenes"]}

    aspect = inp.get("aspectRatio", "16:9")
    voice = plan.get("voice", "Hữu Quân")
    speed = float(plan.get("speed", 1.0))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    url = lambda *a: "/projects/" + pid + "/" + "/".join(a)  # noqa: E731

    # ---- timeline.json ----
    segments = []
    srt_cues, sent_cues = [], []
    cue_n = 0
    thumb = None
    for sc in plan["scenes"]:
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
        if img_file and thumb is None:
            thumb = url("media", "images", img_file)

        vparts = []
        for pi, p in enumerate(sc["parts"], start=1):
            pt = part_map[p["id"]]
            br = p.get("broll") or {}
            broll = None
            if br:
                # tên file suy từ quy ước chung (filename.py); chỉ gắn URL khi file đã tồn tại
                br6 = rand6(pid, "broll", str(sc["order"]), str(pi))
                # B-roll có thể là video (quy tắc 27/10/2026): ưu tiên .mp4
                # nếu có, nếu không thì .jpg như trước.
                fn = f"broll_seg_{sc['order']}_part_{pi}_{br6}.jpg"
                if (build / "media" / "broll" /
                        f"broll_seg_{sc['order']}_part_{pi}_{br6}.mp4").exists():
                    fn = f"broll_seg_{sc['order']}_part_{pi}_{br6}.mp4"
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
                "pauseAfterMs": plan.get("pauseAfterMs", 180),
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
            chunked = [c for c in chunk_cues if c["partId"] == p["id"]]
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
    (build / "subtitles" / "synced_cues.srt").write_text("\n".join(srt_cues), encoding="utf-8")
    (build / "subtitles" / "sentences.srt").write_text("\n".join(sent_cues), encoding="utf-8")

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
    (build / "timeline.json").write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")

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
    (build / "project.json").write_text(
        json.dumps(project, ensure_ascii=False, indent=2), encoding="utf-8")

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
    for sc in plan["scenes"]:
        r6 = rand6(pid, "img", str(sc["order"]))
        if sc.get("sceneImagePrompt"):
            gf_items.append({
                "prompt": sc["sceneImagePrompt"], "ratio": aspect, "quality": "standard",
                "segIdx": sc["order"] - 1, "taskType": "scene", "segOrder": sc["order"],
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
                    "segIdx": sc["order"] - 1, "taskType": "broll", "segOrder": sc["order"],
                    "partIdx": pi - 1, "partOrder": pi, "partId": p["id"],
                    "targetFilename": f"broll_seg_{sc['order']}_part_{pi}_{br6}",
                    "subDir": "media/broll",
                    "mediaType": "video" if br.get("needVideo") else "image",
                    "projectId": pid,
                })
    gf_dir = build / "googleFlow"
    gf_dir.mkdir(parents=True, exist_ok=True)
    (gf_dir / "config.json").write_text(
        json.dumps({"projectId": pid, "projectName": inp.get("name", pid),
                    "items": gf_items}, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---- README ----
    plan_data = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    bgm_note = ""
    _bgm = plan_data.get("bgm") or {}
    if _bgm.get("attribution"):
        bgm_note = (f"\nNHẠC NỀN (ghi công khi đăng YouTube/Facebook):\n"
                    f"{_bgm['attribution']}\n")
    (build / "README_HUONG_DAN.txt").write_text(
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
        "6. Bấm 'Xuất Video' để render.\n",
        encoding="utf-8")

    # ---- ZIP ----
    exp_dir = proj / "export"
    exp_dir.mkdir(parents=True, exist_ok=True)
    zip_path = exp_dir / f"{pid}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(build.rglob("*")):
            if f.is_file():
                if f.name.startswith("silence_"):
                    continue  # file phụ lúc nối WAV, không đưa vào project cuối
                # zip chứa thư mục <pid>/... để user bung thẳng vào projects/
                z.write(f, Path(pid) / f.relative_to(build))
        # từ điển viết tắt (nếu có): file ở gốc project, không nằm trong
        # build/ nên phải thêm riêng; đặt cùng cấp project.json trong ZIP
        # để VieNeu Studio local đọc được sau khi bung vào projects/
        abbr = proj / "abbr_dict.json"
        if abbr.is_file():
            z.write(abbr, Path(pid) / "abbr_dict.json")
    print(f"ASSEMBLE-OK zip={zip_path} size={zip_path.stat().st_size//1024}KB "
          f"segments={len(segments)} duration={tts['totalDuration']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
