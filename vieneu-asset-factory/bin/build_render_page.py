#!/usr/bin/env python3
"""Tạo trang HTML seekable để render video bằng frame capture.

ASSEMBLER MỎNG — toàn bộ logic render nằm trong lib/render-engine.js
(engine duy nhất dùng chung với preview player trong app). Script này chỉ:
  1. gom data project (parts + ảnh thật của từng part + template + karaoke)
  2. nhúng engine + data vào build/render_page.html
  3. trang đó expose window.seekTo(t) / getDuration() / seekReady()
     (đều delegate sang VieNeuRender) cho render_frames.py chụp frame.

    python3 bin/build_render_page.py <project_id>
"""
import base64
import glob
import json
import random
import subprocess
import sys
from pathlib import Path

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent


def img_b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def find_one(pattern: str):
    hits = sorted(glob.glob(pattern))
    return Path(hits[0]) if hits else None


def main() -> int:
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    build = proj / "build"

    tts = json.loads((proj / "tts.json").read_text(encoding="utf-8"))
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    karaoke = json.loads((build / "subtitles" / "karaoke.json").read_text(encoding="utf-8"))
    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    wide = inp.get("aspectRatio", "16:9") != "9:16"
    W, H = (1280, 720) if wide else (720, 1280)

    engine = (FACTORY / "lib" / "render-engine.js").read_text(encoding="utf-8")

    # map partId -> broll info
    broll_map = {}
    for sc in plan["scenes"]:
        for pt in sc["parts"]:
            broll_map[pt["id"]] = pt.get("broll") or {}

    kara_map = {k["partId"]: k for k in karaoke}

    tpl_cache = {}

    def get_tpl(tid):
        if tid not in tpl_cache:
            td = FACTORY / "templates" / tid
            tpl_cache[tid] = (
                (td / "template.html").read_text(encoding="utf-8"),
                (td / "style.css").read_text(encoding="utf-8"),
            )
        return tpl_cache[tid]

    # ảnh thật của từng part: broll image nếu có, không thì scene image
    def part_image(p):
        so, pi = p.get("sceneOrder"), p.get("partIdx")
        if so is not None and pi is not None:
            b = find_one(str(build / "media" / "broll" /
                              f"broll_seg_{so}_part_{pi}_*.jpg"))
            if b:
                return b
        if so is not None:
            s = find_one(str(build / "media" / "images" / f"seg_{so}_*.jpg"))
            if s:
                return s
        return None

    # Motion TỪNG PART đúng như render_draft.py sẽ dùng khi render MP4:
    # chuỗi random.Random(f"motion-{pid}") duyệt part theo thứ tự render
    # (scene theo tts, part của scene theo tts), tránh lặp motion liền
    # trước. Engine ưu tiên part.motion này; thiếu nó engine fallback
    # hash(partId) và khung chụp lệch hẳn motion của bản render thật
    # (lỗi preview blurtest001, user bắt 2026-11-01).
    MOTIONS = ["zoom_in", "zoom_out", "pan_left", "pan_right",
               "pan_up", "pan_down"]
    _rng = random.Random(f"motion-{pid}")
    _part_list = []
    for sc in tts["scenes"]:
        for p in tts["parts"]:
            if p["sceneOrder"] == sc["order"]:
                _part_list.append(p)
    motion_by_id = {}
    _prev_motion = None
    for _ci, _p in enumerate(_part_list):
        _m = _rng.choice(MOTIONS)
        if _ci > 0 and _m == _prev_motion:
            _m = _rng.choice([x for x in MOTIONS if x != _prev_motion])
        _prev_motion = _m
        motion_by_id[_p["id"]] = _m

    parts_data = []
    used_imgs = {}  # tên file -> data URL (resize về chiều rộng video)
    for p in tts["parts"]:
        br = broll_map.get(p["id"], {})
        tid = br.get("templateId")
        tpl_html, tpl_css = "", ""
        tpl_inputs = {}
        if tid and tid != "none":
            try:
                tpl_html, tpl_css = get_tpl(tid)
                tpl_inputs = br.get("inputs") or {}
            except Exception:
                pass
        imgf = part_image(p)
        img_url = ""
        if imgf is not None:
            if imgf.name not in used_imgs:
                try:
                    out = build / f"_thumb_{imgf.name}"
                    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(imgf),
                                    "-vf", f"scale={W}:-1", str(out)],
                                   check=True, timeout=30)
                    used_imgs[imgf.name] = "data:image/jpeg;base64," + img_b64(out)
                except Exception as e:
                    print(f"  warn: không encode được {imgf.name}: {e}")
                    used_imgs[imgf.name] = ""
            img_url = used_imgs[imgf.name]
        parts_data.append({
            "id": p["id"],
            "start": p["startSec"],
            "end": p["endSec"],
            "image": img_url,
            "motion": motion_by_id.get(p["id"]),
            "templateId": tid,
            "tplHtml": tpl_html,
            "tplCss": tpl_css,
            "tplInputs": tpl_inputs,
            "karaoke": kara_map.get(p["id"], {}),
        })

    data_json = json.dumps({"W": W, "H": H, "parts": parts_data},
                           ensure_ascii=False)

    page = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>body {{ margin: 0; background: #000; overflow: hidden; }}</style>
</head><body>
<div id="stage"></div>
<script>
const DATA = {data_json};
</script>
<script>
{engine}
</script>
<script>
// boot: engine là nguồn logic duy nhất; chỉ expose API cho render_frames.py
VieNeuRender.mount(document.getElementById('stage'), DATA);
window.seekTo = (t) => VieNeuRender.seekTo(t);
window.getDuration = () => VieNeuRender.getDuration();
window.seekReady = () => VieNeuRender.isReady();
</script>
</body></html>"""

    out = build / "render_page.html"
    out.write_text(page, encoding="utf-8")
    n_img = sum(1 for p in parts_data if p["image"])
    print(f"RENDER-PAGE-OK {out} ({len(page)//1024}KB, {len(parts_data)} parts, "
          f"{n_img} ảnh)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
