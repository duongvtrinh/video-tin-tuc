#!/usr/bin/env python3
"""Render video nháp (preview) cho VieNeu Asset Factory.

Mỗi voice part = 1 clip: hiện ảnh b-roll nếu có, không thì ảnh scene.
Nối các clip + giọng đọc (WAV thật) + burn phụ đề -> MP4 xem trước.

HẰNG SỐ ĐÃ CHỐT (Giai đoạn 4, 05/11/2026 — xem PIPELINE.md mục
"Hằng số pipeline đã chốt"): aspectRatio mặc định khi thiếu field là
"9:16" (video dọc); khung 9:16 -> 720x1280, còn lại -> 1280x720. Phụ đề
MarginV = 20% chiều cao khi dọc, 7% khi ngang (cùng công thức
karaoke.py và lib/render-engine.js); font phụ đề duy nhất Anton; motion
zoom tối đa 1.05, chuyển cảnh fade 0.5s.

    python3 render_draft.py <project_id>

Ghi: projects/<id>/export/<id>_preview.mp4
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import check_plan, rand6  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)



def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd[:4])}...\n{r.stderr[-1500:]}")
    return r


import random as _random  # noqa: E402

# motion ngẫu nhiên cho từng clip (seed theo project để tái lập được)
MOTIONS = ["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down"]
# chuyển cảnh giữa các part: LUÔN fade (dissolve) 0.5s để khớp quy tắc
# preview voicepart + 500ms (lớp sau phủ đè bằng fade-in, không wipe/slide
# hay fade qua đen/trắng gây chớp nền). Motion từng clip vẫn ngẫu nhiên.
XFADE_D = 0.5  # giây mỗi chuyển cảnh
# BIÊN ĐỘ ZOOM ĐỘNG (CEO 10/11/2026, thay biên độ cố định 1,05x): tốc độ
# zoom mục tiêu 0,8%/giây — part dài tự to biên độ lên để tốc độ chuyển
# động tương đương nhau giữa các part, part ngắn giữ sàn 1,05x. Trần
# 1,12x là lề an toàn (cắt 137px dọc, lề 140px). Không đo MAD, không
# có mức — đây là mặc định cho mọi part.
MOTION_RATE = 0.008  # 0,8%/giây
MOTION_MIN_EXTRA = 0.05  # sàn: biên độ tối thiểu 5% (1,05x)
MOTION_MAX_ZOOM = 1.12  # trần: zoom tối đa 1,12x (lề an toàn)


def motion_vf(kind: str, W: int, H: int, frames: int) -> str:
    # SAFE-AREA MOTION (QA TOPIC-004, 2026-10-26): zoom/pan cũ 1.12 cắt tới
    # 10,7% ở một mép (77px ngang / 137px dọc ở 720x1280), vượt lề chữ
    # 48px trái / 90px trên nên cắt headline cảnh 2, 3, 5. Zoom sàn 1,05x
    # chỉ cắt tối đa 4,8% ở một mép (34px ngang / 61px dọc), nhỏ hơn
    # lề an toàn mới của ảnh cảnh (96px trái, 140px trên), nên chữ không
    # bao giờ chạm mép dù motion pan đi hết hành trình.
    # SMOOTH MOTION (CEO 2026-10-27, sửa lag/giật): công thức zoom cũ dùng
    # biến tăng dần (zoom+0.0005/khung) bị reset ở mỗi khung đầu vào khi
    # d=1 với ảnh lặp, nên cảnh zoom gần như đứng yên (đo 6s: khung đầu
    # so với khung cuối khác 0,03). Công thức mới dùng vị trí tuyệt đối
    # on/frames cho mọi kiểu motion, tốc độ đều TUYẾN TÍNH s=t (CEO 2026-11-10,
    # bỏ easing smoothstep): smoothstep có đạo hàm 0 ở đầu/cuối part, mà zoompan
    # cắt theo pixel nguyên nên cửa sổ đứng yên ~10 khung đầu của lia và ~20 khung
    # đầu của zoom blurfill rồi mới nhảy 1 pixel — nhìn giật. Tuyến tính thì cửa sổ
    # dịch ngay từ khung đầu; xfade 0,5s đã làm mềm chuyển cảnh nên không cần easing.
    # TMIX (CEO 2026-11-10): trộn 3 khung liên tiếp sau zoompan để làm phẳng nhịp
    # MAD (bò 5 khung rồi nhảy) do bước thu nhỏ 3x gây ra; áp ở tầng clip nên phụ
    # đề gắn sau vẫn nét.
    # Ảnh nguồn phóng 4x thay vì 2x để bước cắt zoompan nhỏ hơn khi thu về khung
    # đích, giảm giật từng bậc.
    # BIÊN ĐỘ ĐỘNG (CEO 2026-11-10): biên độ = max(5%, 0,8% × thời lượng
    # part), trần 1,12x. Part 4s → 1,05x; 8s → 1,064x; 11,3s → 1,09x;
    # 15s → 1,12x. Lia tự to theo zoom (tầm lia = 1 - 1/zoom).
    dur = frames / 30.0
    extra = min(max(MOTION_MIN_EXTRA, MOTION_RATE * dur), MOTION_MAX_ZOOM - 1.0)
    zmax = 1.0 + extra
    z = f"{zmax:.4f}"
    e = f"{extra:.4f}"
    t = f"(on/{frames})"
    s = t  # tuyến tính (CEO 2026-11-10): tốc độ đều, không còn đứng yên đầu part
    base = (f"scale={W * 4}:{H * 4}:force_original_aspect_ratio=increase,"
            f"crop={W * 4}:{H * 4}")
    if kind == "zoom_in":
        zp = (f"zoompan=z='1+{e}*{s}':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=30")
    elif kind == "zoom_out":
        zp = (f"zoompan=z='{z}-{e}*{s}':"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=30")
    elif kind == "pan_right":
        zp = (f"zoompan=z='{z}':x='(iw-iw/zoom)*{s}':"
              f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=30")
    elif kind == "pan_left":
        zp = (f"zoompan=z='{z}':x='(iw-iw/zoom)*(1-{s})':"
              f"y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps=30")
    elif kind == "pan_down":
        zp = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='(ih-ih/zoom)*{s}':d=1:s={W}x{H}:fps=30")
    else:  # pan_up
        zp = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='(ih-ih/zoom)*(1-{s})':d=1:s={W}x{H}:fps=30")
    return f"{base},{zp},tmix=frames=3,setsar=1,format=yuv420p"


def esc_filter_path(p: str) -> str:
    return p.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def _normalize_stamps(br: dict) -> list:
    """Danh sách dấu của một part (cơ chế danh sách dấu, 06/11/2026 —
    khôi phục tính năng dấu đã xoá cùng ngày rồi mở rộng):
    broll.stamps = [ {text, tone, tilt, on, at, sfx}, ... ];
    broll.stamp dạng đơn cũ -> danh sách 1 phần tử (tương thích ngược).
    Trả về list (có thể rỗng)."""
    stamps = (br or {}).get("stamps")
    if isinstance(stamps, list):
        return [s for s in stamps if isinstance(s, dict)]
    stamp = (br or {}).get("stamp")
    if isinstance(stamp, dict):
        return [stamp]
    return []


# BLUR-FILL 3:4 (CEO 2026-11-01): ảnh/video ngang hoặc vuông không còn
# bị cắt mù về 9:16. Ảnh ngang cắt vuông (focus chủ thể — pipeline hiện
# chưa có model saliency nên vuông lấy giữa khung, cùng cách crop giữa
# của đường cũ) rồi hiển thị trong cửa sổ 3:4 (720x960 ở khung 720x1280,
# cách đều 160px trên/dưới); 2 dải thừa trên/dưới là chính ảnh đó phóng
# đầy khung + blur. Cửa sổ 3:4 cho animation nhiều không gian hơn đường
# 9:16 cũ (pan ngang trượt 180px trong ảnh vuông thay vì chỉ 34px zoom).
# Ảnh 9:16 giữ nguyên đường cũ (full, không blur). Video ngang không
# cần cắt file trước: render tự đóng khung 3:4 + nền blur từ chính video.
def _media_dims(path, is_video):
    try:
        if is_video:
            r = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0",
                 "-show_entries", "stream=width,height",
                 "-of", "csv=p=0", str(path)],
                capture_output=True, text=True, timeout=30)
            w, h = (int(x) for x in r.stdout.strip().split(",")[:2])
            return (w, h)
        from PIL import Image as _Im
        with _Im.open(path) as im:
            return im.size
    except Exception:
        return None


def _linear_on(frames: int) -> str:
    # Tuyến tính (CEO 2026-11-10, thay smoothstep): tốc độ đều, cửa sổ dịch
    # ngay từ khung đầu, không còn đứng yên ~20 khung đầu của zoom blurfill.
    return f"(on/{frames})"


def _linear_n(frames: int) -> str:
    # crop không có biến 'on' của zoompan — dùng 'n' (số khung vào crop)
    # Tuyến tính (CEO 2026-11-10, thay smoothstep): xem _linear_on.
    return f"(n/{frames})"


def blurfill_image_vf(motion: str, W: int, H: int, frames: int) -> str:
    WH = W * 4 // 3
    y0 = (H - WH) // 2
    s = _linear_on(frames)
    sn = _linear_n(frames)
    # Biên độ động như motion_vf (CEO 2026-11-10): sàn 1,05x, 0,8%/giây,
    # trần 1,12x. Lia ngang đã trượt tối đa 360px nên không tăng thêm.
    dur = frames / 30.0
    extra = min(max(MOTION_MIN_EXTRA, MOTION_RATE * dur), MOTION_MAX_ZOOM - 1.0)
    zmax = 1.0 + extra
    z = f"{zmax:.4f}"
    e = f"{extra:.4f}"
    # zoompan trên ảnh vuông 2880x2880 rồi crop cửa sổ 3:4 (2160x2880)
    # (CEO 2026-11-10: tăng từ 720 lên 2880 cho zoom/lia dọc để pan+zoom
    # mượt hơn — chuỗi đứng yên dài nhất từ 5 khung xuống 1 khung; lia
    # ngang giữ 1440 vì đã mượt):
    # zoom: cửa sổ cố định giữa; pan ngang: cửa sổ trượt trong ảnh
    # vuông; pan dọc: zoompan dịch y, cửa sổ giữ nguyên chiều cao.
    if motion == "zoom_in":
        zp = (f"zoompan=z='1+{e}*{s}':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d=1:s=2880x2880:fps=30")
        win = "crop=2160:2880:x=360:y=0"
    elif motion == "zoom_out":
        zp = (f"zoompan=z='{z}-{e}*{s}':"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=2880x2880:fps=30")
        win = "crop=2160:2880:x=360:y=0"
    elif motion == "pan_right":
        # TANG DO MIN (CEO 06/11/2026, giu crop): pan ngang truoc day dung
        # crop 540:720 o tang 720 voi x='2*trunc(90*sn)' — buoc nhay
        # 2,67px tren man hinh, 6 frame dau x=0 tuyet doi (lag). Nay tang
        # tang zoompan len 1440x1440, cua so 1080:1440, x='2*round(180*sn)'
        # — buoc nhay chi 1,33px tren man hinh, frame dau nhuc nhich tu
        # frame 3, round giu vi tri sat quy dao muot hon trunc. Giu x chan
        # (2*) cho yuv420p; x toi da 360, cua so 1080+360=1440 vua khit.
        zp = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d=1:s=1440x1440:fps=30")
        win = f"crop=1080:1440:x='2*round(180*{sn})':y=0"
    elif motion == "pan_left":
        # Nhu pan_right, chieu nguoc (xem ghi chu tren).
        zp = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='ih/2-(ih/zoom/2)':d=1:s=1440x1440:fps=30")
        win = f"crop=1080:1440:x='2*round(180*(1-{sn}))':y=0"
    elif motion == "pan_down":
        zp = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='(ih-ih/zoom)*{s}':d=1:s=2880x2880:fps=30")
        win = "crop=2160:2880:x=360:y=0"
    else:  # pan_up
        zp = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
              f"y='(ih-ih/zoom)*(1-{s})':d=1:s=2880x2880:fps=30")
        win = "crop=2160:2880:x=360:y=0"
    bg = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},gblur=sigma=25,fps=30")
    # TMIX (CEO 2026-11-10): trộn 3 khung liên tiếp sau scale để làm phẳng nhịp
    # MAD; chỉ áp cho fg (ảnh chuyển động), nền blur tĩnh không cần.
    fg = (f"scale=2880:2880:force_original_aspect_ratio=increase,"
          f"crop=2880:2880,{zp},{win},scale={W}:{WH},tmix=frames=3,fps=30,setsar=1")
    return (f"split[a][b];[a]{bg}[bg];[b]{fg}[fg];"
            f"[bg][fg]overlay=x=0:y={y0}")


def blurfill_video_vf(W: int, H: int) -> str:
    WH = W * 4 // 3
    y0 = (H - WH) // 2
    bg = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},gblur=sigma=25,fps=30")
    fg = (f"scale={W}:{WH}:force_original_aspect_ratio=increase,"
          f"crop={W}:{WH},fps=30")
    return (f"split[a][b];[a]{bg}[bg];[b]{fg}[fg];"
            f"[bg][fg]overlay=x=0:y={y0}")


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: render_draft.py <project_id>", file=sys.stderr)
        return 2
    pid = sys.argv[1]
    proj = FACTORY / "projects" / pid
    build = proj / "build"

    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    tts = json.loads((proj / "tts.json").read_text(encoding="utf-8"))
    # Mặc định 9:16 khi thiếu field (chốt Giai đoạn 4; trước đây mặc
    # định 16:9 ở file này trong khi render_scene_card.py mặc định 9:16).
    wide = inp.get("aspectRatio", "9:16") != "9:16"
    W, H = (1280, 720) if wide else (720, 1280)

    # Phụ đề burn ở bước mux lấy từ build/subtitles/karaoke.ass, Style
    # Fontname = Anton (font DUY NHẤT cho phụ đề + template, CEO chốt
    # 30/10/2026; karaoke.py ghi Anton, guard ở bước mux chạy lại karaoke
    # nếu .ass cũ còn font khác). Đoạn dò font DejaVu/Noto cũ ở đây là mã
    # chết (biến không nơi nào dùng) nên đã gỡ.

    tmp = Path(tempfile.mkdtemp(prefix="draft_"))
    # B1 (đợt sửa an toàn 01/11/2026): chỉ THU THẬP các fallback lặng vào
    # danh sách này, không đổi bất kỳ lệnh ffmpeg hay thứ tự xử lý nào.
    # Báo cáo được in + ghi file ở cuối hàm, sau DRAFT-OK.
    render_report = []
    try:
        # 1. từng clip (Ken Burns + overlay chữ B-roll template sau motion)
        _VENV_PY = str(FACTORY / ".venv" / "bin" / "python")
        plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
        # B28 (06/11/2026, lệnh CEO, lựa chọn A): guard cấu trúc plan —
        # trước đây plan hỏng crash trần KeyError ở vòng tpl_by_part và
        # các lần đọc plan["scenes"] bên dưới.
        try:
            check_plan(plan, require_voice_text=True)
        except ValueError as exc:
            print(f"RENDER-ERROR {pid}: {exc}", file=sys.stderr)
            return 1
        tpl_by_part = {}
        for sc in plan["scenes"]:
            for pt in sc["parts"]:
                br = pt.get("broll") or {}
                if br.get("templateId"):
                    tpl_by_part[pt["id"]] = (br["templateId"],
                                             br.get("inputs") or {},
                                             br.get("reveal"),
                                             _normalize_stamps(br))
        # B26 (06/11/2026, lệnh CEO, lựa chọn A): kiểm BGM/SFX ngay đầu
        # main — trước đây BGM chỉ được kiểm ở cuối (sau khi render xong
        # hết clip) và SFX ở giữa (trước ffmpeg trộn cuối), nên project
        # thiếu file tốn hết thời gian render rồi mới dừng. Cửa chặn muộn
        # ở cuối vẫn còn làm backstop (đề phòng file bị xóa giữa chừng).
        _bgm0 = plan.get("bgm") or {}
        if _bgm0.get("file"):
            _bgm_file0 = FACTORY / "bgm" / _bgm0["file"]
            if not _bgm_file0.exists():
                print(f"RENDER-ERROR {pid}: BGM da chon {_bgm_file0} khong ton tai — dung render, giong preflight",
                      file=sys.stderr)
                return 1
        for _sc in plan["scenes"]:
            for _pt in _sc.get("parts", []):
                _sfx0 = (_pt.get("broll") or {}).get("sfx")
                if _sfx0:
                    _f0 = FACTORY / "sfx" / f"{_sfx0['id']}.mp3"
                    if not _f0.exists():
                        print(f"RENDER-ERROR {pid}: SFX da chon {_f0} khong ton tai — dung render, giong preflight",
                              file=sys.stderr)
                        return 1

        def render_tpl_png(tid, inputs, W, H, out):
            r = subprocess.run(
                [_VENV_PY, str(FACTORY / "bin" / "render_template.py"),
                 tid, json.dumps(inputs, ensure_ascii=False),
                 str(W), str(H), str(out), str(proj)],
                capture_output=True, text=True, timeout=180)
            return r.returncode == 0 and Path(out).exists()

        def _gold_frame_rects(png_path):
            # Ô trong (x, y, w, h) các khung ảnh viền vàng trong PNG template
            # đã render, theo thứ tự trên-trước-trái-trước (khớp thứ tự input
            # ảnh đã sắp xếp: img < img1 < img2). Dùng để đặt video vào đúng
            # ô ảnh (06/11/2026, CEO: ảnh/video thay nhau trong cửa sổ ảnh).
            # Bố cục flex dịch chuyển theo nội dung nên phải đo trên PNG thật,
            # không dùng tọa độ cứng trong meta (meta chỉ là fallback).
            # Ô trong = khung ngoài trừ viền 4px mỗi bên.
            try:
                import numpy as _np
                from PIL import Image as _PILImage
                _a = _np.asarray(
                    _PILImage.open(png_path).convert("RGB")).astype(int)
            except Exception:
                return []
            _gold = ((_a[:, :, 0] > 230) & (_a[:, :, 1] >= 160)
                     & (_a[:, :, 1] <= 215) & (_a[:, :, 2] < 90))
            _g = _np.concatenate(
                [_np.zeros((_gold.shape[0], 1), dtype=bool), _gold,
                 _np.zeros((_gold.shape[0], 1), dtype=bool)], axis=1)
            _d = _np.diff(_g.astype(_np.int8), axis=1)
            _bands = []
            for _y in range(_gold.shape[0]):
                _s = _np.where(_d[_y] == 1)[0]
                _e = _np.where(_d[_y] == -1)[0]
                for _s0, _e0 in zip(_s, _e):
                    if _e0 - _s0 < 150:
                        continue
                    _placed = False
                    for _i, _b in enumerate(_bands):
                        _ov = min(_b[3], int(_e0)) - max(_b[2], int(_s0))
                        _w = min(_b[3] - _b[2], int(_e0) - int(_s0))
                        if _y - _b[1] <= 3 and _ov > 0.5 * _w:
                            _bands[_i] = (_b[0], _y, min(_b[2], int(_s0)),
                                         max(_b[3], int(_e0)))
                            _placed = True
                            break
                    if not _placed:
                        _bands.append((_y, _y, int(_s0), int(_e0)))
            _used = set()
            _rects = []
            for _i, _b in enumerate(_bands):
                if _i in _used:
                    continue
                for _j in range(_i + 1, len(_bands)):
                    if _j in _used:
                        continue
                    _ov = min(_b[3], _bands[_j][3]) - max(_b[2], _bands[_j][2])
                    _w = min(_b[3] - _b[2], _bands[_j][3] - _bands[_j][2])
                    if _ov > 0.5 * _w and _bands[_j][0] - _b[1] > 50:
                        _ox = min(_b[2], _bands[_j][2])
                        _ow = max(_b[3], _bands[_j][3]) - _ox
                        _oy = _b[0]
                        _oh = _bands[_j][1] - _b[0] + 1
                        _rects.append({"x": int(_ox + 4), "y": int(_oy + 4),
                                       "w": int(_ow - 8), "h": int(_oh - 8)})
                        _used.add(_i)
                        _used.add(_j)
                        break
            _rects.sort(key=lambda r: (r["y"], r["x"]))
            return _rects

        def _gold_frame_centers(png_path):
            # Tâm (cx, cy) các khung ảnh viền vàng trong PNG template đã
            # render, thứ tự trên-trước-trái-trước (khớp thứ tự input ảnh
            # đã sắp xếp: img < img1 < img2). Dùng để đóng dấu vào TÂM Ô
            # ẢNH (06/11/2026, CEO: dấu đóng vào lớp ảnh/video, không
            # phải giữa template). Tâm ô trong = tâm khung ngoài (viền
            # đối xứng) nên suy thẳng từ _gold_frame_rects, cùng logic
            # band; template không đo được khung thì trả về [] và dấu
            # rơi về giữa khung.
            return [(round(r["x"] + r["w"] / 2, 1),
                     round(r["y"] + r["h"] / 2, 1))
                    for r in _gold_frame_rects(png_path)]



        def base_image(order, pi):
            simg = build / "media" / "images" / f"seg_{order}_{rand6(pid, 'img', str(order))}.jpg"
            if not simg.exists():
                simg = next((q for ext in ("png", "webp")
                             for q in [build / "media" / "images" /
                                       f"seg_{order}_{rand6(pid, 'img', str(order))}.{ext}"]
                             if q.exists()), None)
            # 11A: b-roll anh co the la jpg/png/webp — thu theo thu tu do,
            # dong bo voi preview (build_render_page.py, handlers-preview.ts).
            bimg = next((build / "media" / "broll" /
                         f"broll_seg_{order}_part_{pi}_{rand6(pid, 'broll', str(order), str(pi))}.{ext}"
                         for ext in ("jpg", "png", "webp")
                         if (build / "media" / "broll" /
                             f"broll_seg_{order}_part_{pi}_{rand6(pid, 'broll', str(order), str(pi))}.{ext}").exists()),
                        None)
            return bimg if bimg is not None else simg

        def base_video(order, pi, part_id):
            # B-roll VIDEO (quy tắc 27/10/2026): b-roll không chỉ là ảnh.
            # File video b-roll nằm đúng quy ước tên của validate_project
            # (broll_seg_<order>_part_<pi>_<rand6>.mp4) trong media/broll/.
            # Chỉ dùng khi ffprobe thấy được video stream, nếu không thì
            # rơi về ảnh cảnh như cũ, không để một file video hỏng làm
            # hỏng cả lần render.
            v = build / "media" / "broll" / \
                f"broll_seg_{order}_part_{pi}_{rand6(pid, 'broll', str(order), str(pi))}.mp4"
            if not v.exists():
                return None
            try:
                r = subprocess.run(
                    ["ffprobe", "-v", "error", "-select_streams", "v:0",
                     "-show_entries", "stream=codec_type",
                     "-of", "csv=p=0", str(v)],
                    capture_output=True, text=True, timeout=30)
                if r.returncode == 0 and "video" in r.stdout:
                    return v
            except Exception:
                pass
            # B1: file video có nhưng ffprobe không thấy stream -> rơi về
            # ảnh, trước đây lặng. Chỉ ghi báo cáo, không đổi hành vi.
            render_report.append(
                f"video-hong-roi-ve-anh part={part_id} file={v}")
            return None

        clip_files = []
        clip_durs = []  # duration render (kéo dài +XFADE_D để xfade overlap)
        rng = _random.Random(f"motion-{pid}")
        part_list = []
        prev_motion = None
        for si, sc in enumerate(tts["scenes"]):
            order = sc["order"]
            for p in [x for x in tts["parts"] if x["sceneOrder"] == order]:
                part_list.append((si, order, p))
        # A26 (05/11/2026, lệnh CEO): part nào không có ảnh nào (không
        # video b-roll, không ảnh b-roll, không ảnh cảnh) thì CHẶN
        # trước khi chạy ffmpeg — như khối BGM thiếu (13B): không render
        # clip nền đen, không DRAFT-OK. Ảnh nền rêu vẫn tính là ảnh ở
        # đây; cửa chặn nền rêu nằm ở preflight (A20), không phải render.
        for _si, _order, _p in part_list:
            _pi = _p["partIdx"]
            _vpath = build / "media" / "broll" / \
                f"broll_seg_{_order}_part_{_pi}_{rand6(pid, 'broll', str(_order), str(_pi))}.mp4"
            if not _vpath.exists() and base_image(_order, _pi) is None:
                print(f"RENDER-ERROR {pid}: anh-thieu-nen-den part={_p['id']} scene={_order} — "
                      f"khong co anh canh seg_{_order}_{rand6(pid, 'img', str(_order))}.jpg/png/webp "
                      f"hay b-roll broll_seg_{_order}_part_{_pi}_{rand6(pid, 'broll', str(_order), str(_pi))}.jpg/png/webp — "
                      f"dung render, giong preflight", file=sys.stderr)
                return 1
        for ci, (si, order, p) in enumerate(part_list):
            pi = p["partIdx"]
            _vid = base_video(order, pi, p["id"])
            img = _vid if _vid is not None else base_image(order, pi)
            is_video_broll = _vid is not None
            static_png = None
            # MỌI template đều overlay SAU zoompan (chữ cố định, chỉ ảnh
            # nền chuyển động như preview); tĩnh overlay 1 ảnh suốt part,
            # lỗi -> không chữ (không bake). Đường animation Chrome đã
            # NGHỈ HƯU đợt D6 (CEO quyết 01/11/2026): từ đợt strip
            # animation 31/10 không template nào còn @keyframes nên nhánh
            # động vốn đã chết — nay xóa hẳn, chỉ còn đường tĩnh.
            if img and p["id"] in tpl_by_part:
                tid, inputs, _reveal, _stamps = tpl_by_part[p["id"]]
                ov_path = tmp / f"tpl_{si}_{pi}.png"
                if render_tpl_png(tid, inputs, W, H, ov_path):
                    static_png = ov_path
                # B1: template được yêu cầu nhưng đường tĩnh lỗi
                # -> clip không chữ, trước đây lặng.
                if not static_png:
                    render_report.append(
                        f"template-loi-khong-chu part={p['id']} file={tid}")
            clip = tmp / f"clip_{si}_{pi}.mp4"
            # motion ngẫu nhiên, tránh lặp lại ngay motion trước đó
            motion = rng.choice(MOTIONS)
            if ci > 0 and motion == prev_motion:
                motion = rng.choice([m for m in MOTIONS if m != prev_motion])
            prev_motion = motion
            # clip kéo dài thêm XFADE_D (trừ clip cuối) để chuyển cảnh overlap
            cdur = p["duration"] + (XFADE_D if ci < len(part_list) - 1 else 0)
            frames = max(1, int(round(cdur * 30)))
            # Blur-fill 3:4 (CEO 2026-11-01): khung dọc + media ngang/vuông
            # thì đi đường composite thay vì cắt mù về 9:16. Ảnh/video 9:16
            # và ảnh dọc khác tỉ lệ giữ nguyên đường cũ.
            _blurfill = False
            if img and H > W:
                _dims = _media_dims(img, is_video_broll)
                if _dims and _dims[0] >= _dims[1]:
                    _blurfill = True
                elif _dims is None:
                    # B1: không đo được kích thước media nên không vào
                    # được đường blur-fill, rơi về đường cũ — trước đây
                    # lặng. (Khi dims đo được thì ảnh dọc đi đường cũ
                    # theo thiết kế và không ghi sự kiện.)
                    render_report.append(
                        f"media-loi-roi-ve-cat-9-16-cu part={p['id']} file={img}")
            if is_video_broll:
                # Video b-roll: không dùng Ken Burns trên ảnh tĩnh nữa.
                # Cắt/lấp đầy khung, 30fps, lặp lại nếu video ngắn hơn
                # part, cắt ngắn nếu video dài hơn part. Tiếng của video
                # b-roll luôn bị tắt (-an ở mọi nhánh dưới) vì giọng đọc
                # và BGM/SFX là track âm thanh riêng của video.
                if _blurfill:
                    vf = blurfill_video_vf(W, H)
                else:
                    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
                          f"crop={W}:{H},fps=30")
                base_args = ["-stream_loop", "-1", "-t", str(cdur),
                             "-i", str(img)]
            else:
                if _blurfill:
                    vf = blurfill_image_vf(motion, W, H, frames)
                else:
                    vf = motion_vf(motion, W, H, frames)
                base_args = ["-loop", "1", "-framerate", "30", "-t",
                             str(cdur), "-i", str(img)]
            if img and static_png:
                # template tĩnh: overlay sau zoompan, suốt part. Card thường
                # scale vừa khung 92%W/80%H; template full-stage (PNG đúng
                # kích thước khung, tỉ lệ khớp khung) phải phủ kín khung
                # thay vì co lại thành hình lơ lửng (khác preview).
                from PIL import Image as _Im
                _ow, _oh = _Im.open(static_png).size
                _is_fullstage = (abs(_ow / _oh - W / H) < 0.05
                        and _ow >= int(W * 0.90) and _oh >= int(H * 0.90))
                # Reveal lần lượt (06/11/2026, CEO: các lớp ảnh/video, dấu,
                # chữ, icon hiện lần lượt tạo hiệu ứng chuyển động):
                # broll.reveal = [stage...] (vd ["1","2","3","4"]) — mỗi
                # stage hiện một khoảng bằng nhau trong part (cắt cứng,
                # như reel Texas). Chỉ áp cho template full-stage (PNG
                # đúng kích thước khung nên tọa độ khớp); stage nào render
                # lỗi thì rơi về đường tĩnh 1 stage (không dừng video).
                # static_png được đổi thành PNG của stage CUỐI (đủ lớp)
                # để kiểm video-slot / đo khung vàng cho dấu được đúng.
                _stage_pngs = []
                _reveal_ok = False
                if (_is_fullstage and isinstance(_reveal, list)
                        and len(_reveal) >= 2
                        and all(isinstance(_s, str) and _s.strip().isdigit()
                                for _s in _reveal)):
                    _ok = True
                    for _i, _sv in enumerate(_reveal):
                        _rin = dict(inputs or {})
                        _rin["stage"] = str(_sv).strip()
                        _rpath = tmp / f"tpl_{si}_{pi}_r{_i}.png"
                        if not render_tpl_png(tid, _rin, W, H, _rpath):
                            render_report.append(
                                f"reveal-loi-roi-ve-tinh part={p['id']} stage={_sv}")
                            _ok = False
                            break
                        _stage_pngs.append(_rpath)
                    _reveal_ok = _ok
                    if _reveal_ok:
                        static_png = _stage_pngs[-1]
                        _ow, _oh = _Im.open(static_png).size
                        _is_fullstage = (abs(_ow / _oh - W / H) < 0.05
                                and _ow >= int(W * 0.90)
                                and _oh >= int(H * 0.90))
                _tpl_n = len(_stage_pngs) if _reveal_ok else 1
                _tpl_base = 1 + _tpl_n
                if _reveal_ok:
                    # Chuỗi stage: scale từng PNG stage về khung rồi
                    # overlay lần lượt; stage 0 luôn hiện, stage i>0
                    # hiện từ t = i*cdur/N (cắt cứng, chia đều part).
                    _ovf = "".join(
                        f"[{i + 1}:v]scale={W}:{H}[st{i}];"
                        for i in range(_tpl_n))
                    _ovf += "[v0][st0]overlay=x='(W-w)/2':y='0'[v1];"
                    for _i in range(1, _tpl_n):
                        _ti = _i * cdur / _tpl_n
                        _ovf += (f"[v{_i}][st{_i}]overlay=x='(W-w)/2':y='0':"
                                 f"enable='gte(t,{_ti:.3f})'[v{_i + 1}];")
                elif _is_fullstage:
                    _ovf = f"[1:v]scale={W}:{H}[ov];"
                elif tid in ("preview-banner", "keyword-block"):
                    # 2 template đặc thù (CEO 31/10/2026): khối nền phủ
                    # kín chiều ngang, sát đáy khung — PNG đã đủ rộng
                    # bằng khung nên chỉ giữ nguyên chiều rộng, không co
                    # 92% như thẻ thường (co lại sẽ hở lề 2 bên).
                    _ovf = f"[1:v]scale={W}:-2[ov];"
                else:
                    sw, sh = int(W * 0.92), int(H * 0.80)
                    _ovf = (f"[1:v]scale={sw}:{sh}:"
                            f"force_original_aspect_ratio=decrease[ov];")
                # Luật CEO 31/10/2026 (sửa tối cùng ngày: bãi bỏ ngoại lệ
                # top — breaking-banner, section-header, story-title cũng
                # về bottom; chỉ thesis-marker và versus-split giữ thiết
                # kế đặc thù full-stage): vùng chữ template về bottom,
                # đúng khoảng cách phụ đề (margin_v = 20% chiều cao khi
                # dọc, 7% khi ngang — cùng công thức karaoke.py).
                # Template full-stage phủ kín khung nên y=0 (trước đây vị
                # trí top/bottom làm lệch khung full-stage). Từ 31/10/2026
                # (lệnh CEO) không còn template nào hiện phụ đề nữa
                # (story-title và clip-caption đã về hidesSubs: true);
                # clip-caption giữ thiết kế caption sát đáy 3% theo lệnh
                # riêng, còn story-title về bottom chung như mọi template.
                if _reveal_ok:
                    _ox, _oy = "(W-w)/2", "0"
                elif _is_fullstage:
                    _ox, _oy = "(W-w)/2", "0"
                elif tid in ("preview-banner", "keyword-block"):
                    # Khối nền đặc thù: sát đáy khung và 2 bên, không
                    # nâng lên khoảng cách phụ đề như thẻ thường.
                    _ox, _oy = "0", "H-h"
                elif tid == "clip-caption":
                    # Caption sát đáy theo thiết kế (lệnh CEO 31/10/2026);
                    # phụ đề đã ẩn ở part này nên không sợ chồng.
                    _ox, _oy = "(W-w)/2", "H-h-(H*0.03)"
                else:
                    _margin_v = int(H * (0.20 if H > W else 0.07))
                    _shows_subs = False
                    try:
                        _meta = json.loads((FACTORY / "templates" / tid / "meta.json").read_text(encoding="utf-8"))
                        _shows_subs = _meta.get("hidesSubs") is False
                    except Exception:
                        pass
                    if _shows_subs:
                        _ox, _oy = "(W-w)/2", "H-h-(H*0.03)"
                    else:
                        _ox, _oy = "(W-w)/2", f"H-h-{_margin_v}"
                # Video-slot (06/11/2026, photo-duo): input ảnh của slot
                # khai trong meta "videoSlots" mà trỏ tới file video thì
                # video thay đúng chỗ ảnh trong khung. Thứ tự composite:
                # nền -> ảnh template -> video trong ô slot (video đè lên
                # đúng ô trong của khung, viền vàng + chữ nằm ngoài ô nên
                # vẫn hiện). Chỉ áp cho template full-stage (PNG đúng
                # kích thước khung nên tọa độ slot khớp). Kiểm tra 2 điều
                # trên PNG template: viền ô phải là vàng (khung hiện, không
                # bị stage ẩn) và ô trong phải đồng đều (không có ảnh thật
                # — ảnh đã được thay bằng placeholder trong suốt nên ô chỉ
                # còn nền navy); thiếu một trong hai thì bỏ qua slot, không
                # vẽ video đè lên ảnh thật. Video tắt tiếng (lệnh đã có
                # -an), ngắn hơn part thì lặp, dài hơn thì cắt, như video
                # b-roll.
                _slot_args = []
                _slot_chains = []
                _slot_cur = f"v{_tpl_n}" if _reveal_ok else "v1"
                if _is_fullstage:
                    try:
                        _meta = json.loads((FACTORY / "templates" / tid / "meta.json").read_text(encoding="utf-8"))
                    except Exception:
                        _meta = {}
                    _slots = _meta.get("videoSlots") or {}
                    if _slots:
                        from PIL import ImageStat as _ImageStat
                        _tpl_im = _Im.open(static_png).convert("RGB")
                        # Thứ tự ô ảnh (map input -> khung đo được) + khung
                        # đo trực tiếp từ PNG template (stage cuối, đủ lớp).
                        _img_ins = sorted(
                            n for n, d in (_meta.get("inputs") or {}).items()
                            if isinstance(d, dict) and d.get("type") == "image")
                        _frame_rects = _gold_frame_rects(static_png)
                        # Ảnh từng stage (reveal) để đo viền vàng của ô
                        # slot theo từng stage; đường tĩnh chỉ có 1 ảnh.
                        _stage_ims = [_tpl_im]
                        if _reveal_ok:
                            _stage_ims = [_Im.open(_rp).convert("RGB")
                                          for _rp in _stage_pngs]

                        def _gold_frac(_im, _box):
                            _bx0, _by0 = max(0, _box[0]), max(0, _box[1])
                            _bx1, _by1 = min(_ow, _box[2]), min(_oh, _box[3])
                            if _bx1 <= _bx0 or _by1 <= _by0:
                                return 0.0, 0
                            _px = list(_im.crop((_bx0, _by0, _bx1, _by1)).getdata())
                            _g = sum(1 for _p in _px
                                     if _p[0] > 230 and 160 <= _p[1] <= 215 and _p[2] < 90)
                            return _g / max(1, len(_px)), len(_px)

                        def _ring_gold_frac(_im, _x, _y, _w, _h):
                            _rg = 0
                            _rn = 0
                            for _rb in ((_x - 4, _y - 4, _x + _w + 4, _y),
                                        (_x - 4, _y + _h, _x + _w + 4, _y + _h + 4),
                                        (_x - 4, _y, _x, _y + _h),
                                        (_x + _w, _y, _x + _w + 4, _y + _h)):
                                _f, _n = _gold_frac(_im, _rb)
                                _rg += _f * _n
                                _rn += _n
                            return _rg / max(1, _rn)

                        for _skey, _rect in _slots.items():
                            _val = (inputs or {}).get(_skey, "")
                            if not str(_val).strip():
                                continue
                            if Path(str(_val)).suffix.lower() not in (
                                    ".mp4", ".mov", ".webm", ".mkv"):
                                continue
                            _vp = str(_val)
                            if _vp.startswith("file://"):
                                _vp = _vp[7:]
                            _vpath = Path(_vp)
                            if not _vpath.is_absolute():
                                _vpath = proj / _vpath
                            if not _vpath.exists():
                                render_report.append(
                                    f"video-slot-thieu-bo-qua part={p['id']} file={_vpath.name}")
                                continue
                            # Ô slot: ưu tiên đo trực tiếp từ khung viền
                            # vàng trên PNG (bố cục flex dịch theo nội dung);
                            # không đo được thì dùng tọa độ meta làm fallback.
                            _x = _y = _w = _h = None
                            _measured = False
                            if _skey in _img_ins:
                                _fi = _img_ins.index(_skey)
                                if _fi < len(_frame_rects):
                                    _r = _frame_rects[_fi]
                                    _x, _y, _w, _h = _r["x"], _r["y"], _r["w"], _r["h"]
                                    _measured = True
                            if not _measured:
                                _x, _y = int(_rect["x"]), int(_rect["y"])
                                _w, _h = int(_rect["w"]), int(_rect["h"])
                            if _x < 0 or _y < 0 or _x + _w > _ow or _y + _h > _oh:
                                render_report.append(
                                    f"video-slot-ngoai-khung-bo-qua part={p['id']} slot={_skey}")
                                continue
                            # Ô đo được thì viền vàng đã chắc chắn (đo từ
                            # khung vàng), chỉ còn kiểm ô trong đồng đều;
                            # fallback meta thì kiểm cả viền + ô trong.
                            if _measured:
                                _ring_gold = 1.0
                            else:
                                _ring_gold = _ring_gold_frac(_tpl_im, _x, _y, _w, _h)
                            # Reveal: video trong slot chỉ hiện từ stage
                            # đầu tiên mà viền vàng của ô đã hiện; đường
                            # tĩnh thì video hiện suốt part (_slot_at=None).
                            _slot_at = None
                            if _reveal_ok:
                                for _si, _sim in enumerate(_stage_ims):
                                    if _ring_gold_frac(_sim, _x, _y, _w, _h) >= 0.5:
                                        _slot_at = _si * cdur / _tpl_n
                                        break
                                if _slot_at is None:
                                    render_report.append(
                                        f"video-slot-khung-an-bo-qua part={p['id']} slot={_skey}")
                                    continue
                            _in_std = max(_ImageStat.Stat(
                                _tpl_im.crop((_x, _y, _x + _w, _y + _h))).stddev)
                            if _ring_gold < 0.5 or _in_std > 20:
                                render_report.append(
                                    f"video-slot-khong-trong-bo-qua part={p['id']} slot={_skey} "
                                    f"vien-vang={_ring_gold:.2f} trong-std={_in_std:.0f}")
                                continue
                            _n = len(_slot_args) // 5
                            _slot_args += ["-stream_loop", "-1", "-t", str(cdur),
                                         "-i", str(_vpath)]
                            _slot_chains.append(
                                f"[{_tpl_base + _n}:v]scale={_w}:{_h}:force_original_aspect_ratio=increase,"
                                f"crop={_w}:{_h},fps=30,format=yuva420p[slot{_n}];")
                            _en = ""
                            if _slot_at is not None and _slot_at > 0:
                                _en = f":enable='gte(t,{_slot_at:.3f})'"
                            _slot_chains.append(
                                f"[{_slot_cur}][slot{_n}]overlay=x={_x}:y={_y}{_en}[{_slot_cur}s{_n}];")
                            _slot_cur = f"{_slot_cur}s{_n}"
                # Lớp dấu (06/11/2026 — khôi phục sau lệnh xoá cùng ngày,
                # mở rộng thành danh sách dấu): mỗi dấu render riêng qua
                # template verdict-stamp (xoay CSS transform theo tilt) rồi composite
                # SAU ảnh template và SAU cả video-slot (lên trên cùng),
                # tại TÂM Ô ẢNH của riêng nó (đo từ khung viền vàng trên
                # PNG template; không đo được thì rơi về giữa khung),
                # hiện từ t=at (overlay enable). Mỗi dấu mang SFX thud
                # riêng (thu ở bước mix bên dưới).
                _stamp_args = []
                _stamp_chains = []
                _stamp_cur = _slot_cur
                if _stamps:
                    try:
                        _smeta = json.loads((FACTORY / "templates" / tid / "meta.json").read_text(encoding="utf-8"))
                    except Exception:
                        _smeta = {}
                    _s_img_ins = sorted(
                        n for n, d in (_smeta.get("inputs") or {}).items()
                        if isinstance(d, dict) and d.get("type") == "image")
                    _s_centers = (_gold_frame_centers(static_png)
                                  if _is_fullstage else [])
                    _n_slots = len(_slot_args) // 6
                    _sn = 0
                    for _st in _stamps:
                        _stext = str(_st.get("text") or "").strip()
                        if not _stext:
                            render_report.append(
                                f"stamp-thieu-text-bo-qua part={p['id']}")
                            continue
                        _spng = tmp / f"stamp_{si}_{pi}_{_sn}.png"
                        if not render_tpl_png(
                                "verdict-stamp",
                                {"text": _stext,
                                 "tone": str(_st.get("tone") or "red"),
                                 "tilt": str(_st.get("tilt") or "-15")},
                                W, H, _spng):
                            render_report.append(
                                f"stamp-loi-bo-qua part={p['id']} text={_stext}")
                            continue
                        _son = str(_st.get("on") or "").strip()
                        _cx = _cy = None
                        if _son and _son in _s_img_ins:
                            _fi = _s_img_ins.index(_son)
                            if _fi < len(_s_centers):
                                _cx, _cy = _s_centers[_fi]
                        elif not _son and _s_centers:
                            _cx, _cy = _s_centers[0]
                        if _cx is None:
                            _cx, _cy = W // 2, H // 2
                            if _son:
                                render_report.append(
                                    f"stamp-khong-do-duoc-khung part={p['id']} on={_son}")
                        try:
                            _at = float(_st.get("at", 0) or 0)
                        except (TypeError, ValueError):
                            _at = 0.0
                        _sidx = _tpl_base + _n_slots + _sn
                        _stamp_args += ["-loop", "1", "-framerate", "30",
                                        "-t", str(cdur), "-i", str(_spng)]
                        _stamp_chains.append(
                            f"[{_sidx}:v]format=yuva420p[stamp{_sn}];")
                        _en = (f":enable='gte(t,{_at:.3f})'"
                               if _at > 0 else "")
                        _stamp_chains.append(
                            f"[{_stamp_cur}][stamp{_sn}]overlay="
                            f"x='{int(round(_cx))}-w/2':y='{int(round(_cy))}-h/2'"
                            f"{_en}[{_stamp_cur}s{_sn}];")
                        _stamp_cur = f"{_stamp_cur}s{_sn}"
                        _sn += 1
                if _reveal_ok:
                    fc = (
                        f"[0:v]{vf},format=yuva420p[v0];"
                        f"{_ovf}"
                        f"{''.join(_slot_chains)}"
                        f"{''.join(_stamp_chains)}"
                        f"[{_stamp_cur}]format=yuv420p[vout]")
                    _tpl_inputs_args = []
                    for _rp in _stage_pngs:
                        _tpl_inputs_args += ["-loop", "1", "-framerate", "30",
                                             "-t", str(cdur), "-i", str(_rp)]
                else:
                    fc = (
                        f"[0:v]{vf},format=yuva420p[v0];"
                        f"{_ovf}"
                        f"[v0][ov]overlay=x='{_ox}':y='{_oy}'[v1];"
                        f"{''.join(_slot_chains)}"
                        f"{''.join(_stamp_chains)}"
                        f"[{_stamp_cur}]format=yuv420p[vout]")
                    _tpl_inputs_args = ["-loop", "1", "-framerate", "30",
                                        "-t", str(cdur), "-i", str(static_png)]
                run(["ffmpeg", "-y", "-v", "error",
                     *base_args,
                     *_tpl_inputs_args,
                     *_slot_args,
                     *_stamp_args,
                     "-filter_complex", fc, "-map", "[vout]",
                     "-c:v", "libx264", "-preset", "veryfast",
                     "-crf", "23", "-pix_fmt", "yuv420p",
                     "-an", str(clip)], timeout=300)

            elif img:
                _vf = f"{vf},format=yuv420p" if (is_video_broll or _blurfill) else vf
                run(["ffmpeg", "-y", "-v", "error", *base_args,
                     "-vf", _vf, "-c:v", "libx264", "-preset", "veryfast",
                     "-crf", "23", "-pix_fmt", "yuv420p",
                     "-an", str(clip)], timeout=300)
            else:
                # A26 (05/11/2026, lệnh CEO): thiếu mọi ảnh của part thì
                # CHẶN như BGM thiếu — không render clip nền đen lặng lẽ
                # rồi vẫn DRAFT-OK như trước. Dự phòng cho trường hợp
                # video b-roll tồn tại ở bước kiểm trước vòng lặp nhưng
                # ffprobe hỏng nên rơi về ảnh mà cũng không có ảnh.
                print(f"RENDER-ERROR {pid}: anh-thieu-nen-den part={p['id']} scene={order} — "
                      f"khong co anh canh seg_{order}_{rand6(pid, 'img', str(order))}.jpg/png/webp "
                      f"hay b-roll — dung render, giong preflight", file=sys.stderr)
                return 1
            clip_files.append(clip)
            clip_durs.append(p["duration"])

        # 2. nối video bằng xfade fade 0.5s (quy tắc voicepart + 500ms)
        vonly = tmp / "video.mp4"
        if len(clip_files) == 1:
            run(["ffmpeg", "-y", "-v", "error", "-i", str(clip_files[0]),
                 "-c", "copy", str(vonly)], timeout=600)
        else:
            fc_parts = []
            last = "0:v"
            off = clip_durs[0]  # điểm bắt đầu chuyển cảnh đầu = hết part 1
            for i in range(1, len(clip_files)):
                tr = "fade"
                out = f"vx{i}"
                fc_parts.append(
                    f"[{last}][{i}:v]xfade=transition={tr}:"
                    f"duration={XFADE_D}:offset={off:.3f}[{out}]")
                last = out
                off += clip_durs[i]
            fc = ";".join(fc_parts)
            cmd = ["ffmpeg", "-y", "-v", "error"]
            for c in clip_files:
                cmd += ["-i", str(c)]
            cmd += ["-filter_complex", fc, "-map", f"[{last}]",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-pix_fmt", "yuv420p",
                    str(vonly)]
            run(cmd, timeout=900)

        # 3. nối audio (WAV từng segment, đã gồm pause)
        alst = tmp / "audio.txt"
        alst.write_text("".join(
            f"file '{build / 'audio' / 'voice' / sc['audio_file']}'\n"
            for sc in tts["scenes"]), encoding="utf-8")
        afull = tmp / "audio.wav"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(alst), "-c", "copy", str(afull)], timeout=300)

        # 4. mux + burn phụ đề karaoke + mix SFX
        # Karaoke phải khớp tỉ lệ hiện tại: nếu input.json đổi tỉ lệ (vd
        # 16:9 -> 9:16) sau lần chạy karaoke cuối mà không chạy lại karaoke,
        # .ass cũ sẽ burn phụ đề sai vị trí (MarginV của tỉ lệ cũ). Phát hiện
        # và chạy lại karaoke trước khi mux thay vì burn sai lặng lẽ.
        ass = build / "subtitles" / "karaoke.ass"
        try:
            _exp_mv = int(H * (0.20 if not wide else 0.07))
            _regen = False
            _reason = ""
            if ass.exists():
                _style = next((ln for ln in ass.read_text(encoding="utf-8").splitlines()
                               if ln.startswith("Style:")), "")
                _fields = _style.split(",")
                _mv = int(_fields[21]) if len(_fields) > 21 else -1
                _font = _fields[1].strip() if len(_fields) > 1 else ""
                if _font != "Anton":
                    # Font phụ đề DUY NHẤT là Anton (CEO chốt 30/10/2026,
                    # karaoke.py đã ghi Anton). .ass cũ còn ghi font khác
                    # (vd DejaVu Sans) thì chạy lại karaoke trước khi burn,
                    # nếu không bản render lại của project cũ sẽ lặng lẽ
                    # đốt phụ đề bằng font cũ. File MP4 cũ đã xuất không
                    # bị đụng — chỉ lần render mới dùng Anton.
                    _regen, _reason = True, f"Fontname {_font!r} != 'Anton'"
                elif _mv != _exp_mv:
                    _regen, _reason = True, f"MarginV {_mv} != {_exp_mv}"
                elif (ass.stat().st_mtime < (proj / "input.json").stat().st_mtime
                      or ass.stat().st_mtime < (proj / "tts.json").stat().st_mtime):
                    _regen, _reason = True, "input/tts mới hơn .ass"
            if _regen:
                print(f"KARAOKE-REGEN {_reason}, chạy lại karaoke.py")
                _rr = subprocess.run([str(FACTORY / ".venv" / "bin" / "python"),
                                str(FACTORY / "bin" / "karaoke.py"), pid],
                               capture_output=True, text=True, timeout=180)
                # B1: chạy lại karaoke thất bại (returncode != 0) thì code
                # vẫn burn .ass cũ ở dưới mà trước đây không để lại dấu
                # vết nào (returncode không được kiểm tra). Chỉ ghi báo
                # cáo, không đổi hành vi.
                if _rr.returncode != 0:
                    render_report.append(
                        f"karaoke-regen-loi-dung-ass-cu part=- file={ass}")
        except Exception as _e:
            print(f"KARAOKE-REGEN bỏ qua (lỗi {_e}), dùng .ass hiện có")
            render_report.append(
                f"karaoke-regen-loi-dung-ass-cu part=- file={ass}")
        sub_src = ass if ass.exists() else build / "subtitles" / "synced_cues.srt"
        vf_sub = f"subtitles={esc_filter_path(str(sub_src))}"

        # SFX: mỗi part có broll.sfx -> phát tại part.startSec + offsetSec
        plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
        # Sửa 30/10/2026 (TOPIC-040 cắt scene10): tra scene theo order thay vì
        # chỉ số order-1 — sau khi cắt cảnh, order không còn liên tục (1-9,11,12)
        # nên plan["scenes"][order-1] vừa sai scene vừa IndexError ở order cuối.
        plan_by_order = {s.get("order"): s for s in plan["scenes"]}
        # B9 (05/11/2026, lệnh CEO, lựa chọn A): tra partIdx bằng cách khớp
        # part["id"] với part cùng id trong tts.json — không parse hậu tố
        # "-part-<số>" từ ID nữa. ID không đúng mẫu (vd "part-1") từng làm
        # rsplit trả 1 phần tử -> IndexError -> SFX bị bỏ lặng, không ghi
        # report, không in gì. Part nào không khớp id trong tts.json thì ghi
        # sfx-skip-id-la vào report thay vì bỏ lặng.
        tts_partidx = {p["id"]: p["partIdx"] for p in tts["parts"]
                       if isinstance(p.get("partIdx"), int)}
        sfx_dir = FACTORY / "sfx"
        # R4-42 (07/11/2026, DEC-050): _seen_sfx là dict (id SFX, mốc ms)
        # -> tập các ô `on` đã phát ở mốc đó; None trong tập nghĩa là SFX
        # của part (không có ô) đã phát — dedup với mọi SFX cùng mốc.
        _seen_sfx = {}
        sfx_events = []
        for sc in tts["scenes"]:
            order = sc["order"]
            pstart = {p["partIdx"]: p["startSec"]
                      for p in tts["parts"] if p["sceneOrder"] == order}
            pend = {p["partIdx"]: p["endSec"]
                    for p in tts["parts"] if p["sceneOrder"] == order}
            for part in plan_by_order.get(order, {}).get("parts", []):
                _br = part.get("broll") or {}
                # SFX của part + SFX riêng từng dấu (cơ chế danh sách dấu
                # 06/11/2026): mỗi dấu mang thud riêng (offsetSec = at);
                # dấu đơn cũ không có sfx riêng thì dùng sfx của part (đã
                # có trong danh sách, không cộng thêm).
                _specs = []
                if _br.get("sfx"):
                    _specs.append((_br["sfx"], None))
                for _st in _normalize_stamps(_br):
                    if _st.get("sfx"):
                        _specs.append((_st["sfx"], _st.get("on")))
                for sfx, _on in _specs:
                    # R3-23 (09/11/2026, rà soát lần 3): SFX dict thiếu khóa
                    # `id` — trước đây đọc sfx['id'] trực tiếp nên crash
                    # KeyError; nay báo lỗi rõ và dừng render.
                    _sid = sfx.get("id") if isinstance(sfx, dict) else None
                    if not (isinstance(_sid, str) and _sid.strip()):
                        print(f"RENDER-ERROR {pid}: SFX trong plan thiếu khóa 'id' "
                              f"(part={part.get('id')}) — ghi rõ id SFX trong plan",
                              file=sys.stderr)
                        return 1
                    f = sfx_dir / f"{_sid}.mp3"
                    if not f.exists():
                        # B8 (05/11/2026, lệnh CEO, lựa chọn A): SFX khai trong
                        # plan nhưng file mp3 không tồn tại thì CHẶN như BGM
                        # (13B) — in RENDER-ERROR, dừng trước ffmpeg trộn
                        # cuối, không render thiếu tiếng rồi DRAFT-OK nữa.
                        # Trước đây chỉ ghi sfx-thieu-bo-qua vào report rồi
                        # render tiếp, trái với cửa chặn preflight (A26).
                        print(f"RENDER-ERROR {pid}: SFX da chon {f} khong ton tai — dung render, giong preflight",
                              file=sys.stderr)
                        return 1
                    pidx = tts_partidx.get(part.get("id"))
                    if pidx is None:
                        render_report.append(
                            f"sfx-skip-id-la part={part.get('id')} sfx={_sid} — "
                            f"không khớp part nào trong tts.json, không tra được partIdx")
                        continue
                    at = pstart.get(pidx)
                    if at is None:
                        render_report.append(
                            f"sfx-skip-id-la part={part.get('id')} partIdx={pidx} — "
                            f"không có startSec trong tts.json")
                        continue
                    # SFX dừng chậm nhất khi chuyển part (luật CEO 31/10/2026):
                    # mixer trước đây phát nguyên file SFX (adelay, không cắt),
                    # nên typing_fast 6.37s trên part 3.39s lấn ~3s sang part
                    # sau, riser 3.0s trên part móc lại 1.7s lấn ~1s. Cắt đuôi
                    # file theo cuối part, fade-out 0.05s tránh click ở điểm
                    # cắt; SFX bắt đầu sau cuối part thì bỏ luôn.
                    _start = max(0.0, at + float(sfx.get("offsetSec", 0)))  # kẹp >=0: adelay âm làm ffmpeg lỗi (section-title offset -0.2 ở part đầu video, đã đo 11/11/2026)
                    _pend = pend.get(pidx)
                    if _pend is None:
                        render_report.append(
                            f"sfx-skip-id-la part={part.get('id')} partIdx={pidx} — "
                            f"không có endSec trong tts.json")
                        continue
                    _dur = _pend - _start
                    if _dur <= 0:
                        print(f"SFX-SKIP {_sid} part {pidx}: bắt đầu "
                              f"{_start:.2f}s sau cuối part {_pend:.2f}s")
                        continue
                    # typing: thời gian gõ theo độ dài văn bản HIỂN THỊ trong
                    # template (inputs.text), KHÔNG theo thời gian part/giọng
                    # đọc — đính chính CEO 31/10/2026 (bản loop trước đó hiểu
                    # sai: lấy thời gian part). Tốc độ 0.1s/ký tự (10 ký tự/
                    # giây, tính cả dấu cách); vẫn chặn trên bằng cuối part.
                    if "typing" in _sid:
                        _txt = ((part.get("broll") or {}).get("inputs") or {}).get("text") or ""
                        if _txt:
                            _dur = min(_dur, len(_txt) * 0.1)
                            print(f"SFX-TYPE {_sid} part {pidx}: "
                                  f"{len(_txt)} ký tự -> {_dur:.2f}s "
                                  f"(part còn {_pend - _start:.2f}s)")
                    # QA Chợ nổi 26/10/2026, lỗi 4: heavy_thud_slam ở volume 0.6
                    # cộng với giọng + BGM đã chạm trần 564 mẫu ở 0 dBFS. SFX
                    # nặng (thud/slam/boom) bị giới hạn mặc định ở 0.4 trong
                    # tầng mix, bất kể plan khai cao hơn; limiter cuối (bên
                    # dưới) là lớp bảo vệ thứ hai để không bao giờ chạm trần.
                    _vol = float(sfx.get("volume", 0.6))
                    if any(k in _sid for k in ("thud", "slam", "boom")):
                        _vol = min(_vol, 0.4)
                    # Dedup (06/11/2026, sửa R4-42 07/11/2026 DEC-050):
                    # SFX của dấu trùng SFX của part (cùng id + cùng mốc
                    # ms) thì chỉ phát một lần. 2 dấu KHÁC ô ảnh (on khác
                    # nhau) thì mỗi dấu giữ tiếng riêng — không dedup.
                    # Dấu không có on (None) dedup như SFX part (hành vi
                    # cũ, an toàn).
                    _key = (_sid, int(max(0.0, at + float(sfx.get("offsetSec", 0))) * 1000))
                    _seen_on = _seen_sfx.get(_key)
                    if _seen_on is not None and (
                            None in _seen_on or _on is None or _on in _seen_on):
                        render_report.append(
                            f"sfx-trung-bo-qua part={part['id']} file={_sid}")
                        continue
                    if _seen_on is None:
                        _seen_sfx[_key] = {_on}
                    else:
                        _seen_on.add(_on)
                    sfx_events.append({"file": f,
                                       "ms": int(max(0.0, at + float(sfx.get("offsetSec", 0))) * 1000),
                                       "dur": round(_dur, 3),
                                       "loop": "typing" in _sid,
                                       "vol": _vol})

        out = proj / "export" / f"{pid}_preview.mp4"
        out.parent.mkdir(parents=True, exist_ok=True)
        total_dur = sum(p["duration"] for p in tts["parts"])

        cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(vonly), "-i", str(afull)]
        for ev in sfx_events:
            cmd += ["-i", str(ev["file"])]
        bgm = plan.get("bgm") or {}
        bgm_file = FACTORY / "bgm" / bgm.get("file", "") if bgm.get("file") else None
        # 13B (05/11/2026): plan khai BGM nhưng file không tồn tại thì CHẶN,
        # như preflight — không render không nhạc lặng lẽ nữa. Plan không
        # khai BGM thì không phải lỗi, vẫn render bình thường.
        if bgm.get("file") and not bgm_file.exists():
            print(f"RENDER-ERROR {pid}: BGM da chon {bgm_file} khong ton tai — dung render, giong preflight",
                  file=sys.stderr)
            return 1
        if bgm_file and bgm_file.exists():
            cmd += ["-i", str(bgm_file)]

        fc = [f"[0:v]{vf_sub}[vout]"]
        amix_ins = ["[1:a]"]
        for i, ev in enumerate(sfx_events):
            _dur = ev["dur"]
            _fd = min(0.05, _dur)
            # typing: _dur đã là thời gian gõ theo text hiển thị (tính ở
            # trên) — file ngắn hơn _dur thì lặp, dài hơn thì cắt.
            _loop = "aloop=loop=-1:size=2e9," if ev.get("loop") else ""
            fc.append(f"[{i + 2}:a]aresample=44100,{_loop}atrim=0:{_dur:.3f},"
                      f"asetpts=PTS-STARTPTS,"
                      f"afade=t=out:st={_dur - _fd:.3f}:d={_fd:.3f},"
                      f"adelay={ev['ms']}|{ev['ms']},"
                      f"volume={ev['vol']}[s{i}]")
            amix_ins.append(f"[s{i}]")
        fc.append(f"{''.join(amix_ins)}amix=inputs={len(amix_ins)}:normalize=0[vmix]")

        if bgm_file and bgm_file.exists():
            bi = 2 + len(sfx_events)  # chỉ số input của BGM
            # loop BGM phủ hết video, volume nền ~ -18dB, fade-out 2s cuối
            fc.append(
                f"[{bi}:a]aresample=44100,aloop=loop=-1:size=2e9,volume=0.12,"
                f"afade=t=out:st={max(0, total_dur - 2):.1f}:d=2[bgm]")
            # ducking: nhạc tự hạ khi có giọng nói (sidechain = voice mix)
            # [vmix] dùng 2 lần nên phải asplit
            fc.append("[vmix]asplit=2[vmix_sc][vmix_main]")
            fc.append(
                "[bgm][vmix_sc]sidechaincompress=threshold=0.02:ratio=8:"
                "attack=200:release=600:makeup=1[ducked]")
            fc.append("[vmix_main][ducked]amix=inputs=2:normalize=0[aout]")
            bgm_label = f" bgm={bgm.get('id')}"
        else:
            fc.append("[vmix]anull[aout]")
            bgm_label = ""
        # Limiter cuối, QA Chợ nổi 26/10/2026: amix normalize=0 cộng giọng
        # + SFX + BGM có thể vượt 1.0 và chạm trần trước khi vào AAC. Giới
        # hạn ở 0.89 (-1 dB) để không bao giờ còn mẫu 0 dBFS, bất kể volume
        # SFX trong plan khai bao nhiêu.
        fc.append("[aout]alimiter=limit=0.89:level=false[aout_lim]")

        cmd += ["-filter_complex", ";".join(fc),
                "-map", "[vout]", "-map", "[aout_lim]",
                # yuv420p bắt buộc (11/2026): điện thoại chỉ giải mã tới
                # 4:2:0, libx264 mặc định ra 4:4:4 gây đen hình có tiếng.
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-shortest",
                "-movflags", "+faststart", str(out)]
        run(cmd, timeout=900)
        print(f"DRAFT-OK file={out} size={out.stat().st_size//1024}KB "
              f"subs={sub_src.name} sfx={len(sfx_events)}{bgm_label}")
        # B1 (đợt sửa an toàn 01/11/2026): báo cáo fallback — chỉ cộng thêm
        # log + file cạnh MP4, không đụng vào MP4 vừa render xong.
        if render_report:
            _report_lines = [f"RENDER-REPORT {e}" for e in render_report]
        else:
            _report_lines = ["RENDER-REPORT: không có fallback"]
        for _line in _report_lines:
            print(_line)
        (out.parent / f"{pid}_render_report.txt").write_text(
            "\n".join(_report_lines) + "\n", encoding="utf-8")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
