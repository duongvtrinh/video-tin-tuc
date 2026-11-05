#!/usr/bin/env python3
"""ĐÃ NGHỈ HƯU — đợt D6, CEO quyết 01/11/2026. KHÔNG còn đường nào gọi
script này nữa (render_draft.py đã xóa nhánh động, chỉ còn đường tĩnh
WeasyPrint). Giữ file làm lưu trữ, không chạy, không sửa. Giai đoạn 5
(05/11/2026) nhắc lại theo quy tắc "dọn code chết CHỈ BẰNG GHI CHÚ":
file này KHÔNG bị xóa, không được gọi lại, không được phục hồi nhánh
động từ đây mà không có quyết định riêng của CEO. Đường động
Chrome chưa từng chạy được trong môi trường này (cần Hatch WebGL domain
policy) và từ đợt strip animation 31/10 không template nào còn keyframes.

Nội dung cũ (chỉ để đọc lịch sử):
Render animation CSS của 1 b-roll template thành chuỗi PNG alpha.

Khác render_template.py (WeasyPrint -> 1 ảnh tĩnh): script này chạy template
bằng headless Chrome thật, seek animation bằng Web Animations API
(pause + currentTime) rồi chụp từng frame PNG trong suốt. Dùng cho bản nháp
MP4 ffmpeg để chữ template chuyển động thay vì dán chết 1 ảnh tĩnh.

    python3 render_template_anim.py <template_id> <inputs_json> <W> <H> <outdir>

Ghi: <outdir>/seq_%03d.png (đã crop theo union alpha + scale theo luật
composite_center 92%W/80%H), <outdir>/hold.png (frame cuối),
<outdir>/meta.json {window_sec, fps, n_frames, width, height}.
Thoát 1 khi template không có animation hữu hạn (fallback ảnh tĩnh).
Chạy bằng asset-factory/.venv (có websocket-client + pillow).
"""
import base64
import html as htmlmod
import json
import math
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)

ACCENT = "#FBBF24"
FPS = 30
MAX_WINDOW = 5.0  # giây, chặn animation vô hạn (nháy con trỏ...)


def find_chrome() -> str:
    for cand in ("/opt/meta-chromium/chrome",):
        if Path(cand).exists():
            return cand
    for name in ("chromium", "chrome", "google-chrome"):
        p = shutil.which(name)
        if p:
            return p
    raise RuntimeError("no chrome binary found")


def fill_placeholders(tpl: str, inputs: dict) -> str:
    def rep(m):
        key = m.group(1)
        v = inputs.get(key, "")
        if key == "items":
            # checklist: chuỗi nhiều dòng (hoặc list) -> <li> đúng CSS thiết kế
            if isinstance(v, list):
                lines = [str(x) for x in v if str(x).strip()]
            else:
                lines = [ln for ln in str(v).splitlines() if ln.strip()]
            return "".join(
                f'<li class="broll-item">{htmlmod.escape(ln)}</li>'
                for ln in lines)
        ev = htmlmod.escape(str(v))
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", ev)
    return re.sub(r"\{\{(\w+)\}\}", rep, tpl)


def main() -> int:
    if len(sys.argv) < 6:
        print("usage: render_template_anim.py <tid> <inputs_json> <W> <H> "
              "<outdir>", file=sys.stderr)
        return 2
    tid, inputs_json, W, H, outdir = sys.argv[1:6]
    W, H = int(W), int(H)
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    inputs = json.loads(inputs_json)
    tdir = FACTORY / "templates" / tid
    html_path = tdir / "template.html"
    css_path = tdir / "style.css"
    if not html_path.exists():
        print("ANIM-FAIL no template", file=sys.stderr)
        return 1
    body = fill_placeholders(html_path.read_text(encoding="utf-8"),
                             inputs or {})
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    # KHÔNG strip box-shadow/text-shadow: screenshot alpha thật giữ được bóng mềm
    # class orientation cho template (như render_template.py).
    orient = "portrait" if H > W else "landscape"
    page = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;padding:0;background:transparent;overflow:hidden}}
:root {{--broll-accent:{ACCENT}; }}
.stage{{width:{W}px;height:{H}px;display:flex;align-items:center;
justify-content:center}}
{css}</style></head><body class="{orient}"><div class="stage">{body}</div></body></html>"""
    page_path = outdir / "_page.html"
    page_path.write_text(page, encoding="utf-8")

    port, prof = 9411, "/tmp/chrome_tpl_anim"
    shutil.rmtree(prof, ignore_errors=True)
    proc = subprocess.Popen(
        [find_chrome(), "--headless", "--no-sandbox", "--disable-gpu",
         "--disable-dev-shm-usage", f"--remote-debugging-port={port}",
         "--remote-allow-origins=*", f"--user-data-dir={prof}",
         f"--window-size={W},{H}", "--force-device-scale-factor=1",
         "--hide-scrollbars", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        import websocket
        time.sleep(8)
        tabs = json.loads(urllib.request.urlopen(
            f"http://127.0.0.1:{port}/json/list", timeout=10).read())
        pages = [t for t in tabs if t.get("type") == "page"]
        ws = websocket.create_connection(
            (pages[0] if pages else tabs[0])["webSocketDebuggerUrl"],
            timeout=60)
        mid = [0]

        def cmd(method, params=None, timeout=60):
            mid[0] += 1
            ws.send(json.dumps({"id": mid[0], "method": method,
                                "params": params or {}}))
            t_end = time.time() + timeout
            while time.time() < t_end:
                m = json.loads(ws.recv())
                if m.get("id") == mid[0]:
                    return m.get("result", {})
            raise TimeoutError(method)

        cmd("Page.enable")
        cmd("Emulation.setDeviceMetricsOverride",
            {"width": W, "height": H, "deviceScaleFactor": 1, "mobile": False})
        cmd("Emulation.setDefaultBackgroundColorOverride",
            {"color": {"r": 0, "g": 0, "b": 0, "a": 0}})
        cmd("Page.navigate", {"url": "file://" + str(page_path)})
        for _ in range(20):
            r = cmd("Runtime.evaluate",
                    {"expression": "document.readyState",
                     "returnByValue": True})
            if r.get("result", {}).get("value") == "complete":
                break
            time.sleep(0.5)
        time.sleep(1)
        # cửa sổ animation = max(delay + duration*iterations) của animation
        # HỮU HẠN (bỏ qua vô hạn như nháy con trỏ); trình duyệt tự tính calc/var
        r = cmd("Runtime.evaluate", {
            "expression":
            "(()=>{let w=0;for(const a of document.getAnimations({subtree:true}))"
            "{const t=a.effect.getTiming();if(t.iterations===Infinity)continue;"
            "const d=(typeof t.duration==='number')?t.duration:0;"
            "w=Math.max(w,t.delay+d*t.iterations);}return w/1000;})()",
            "returnByValue": True})
        window = float(r.get("result", {}).get("value") or 0)
        if window <= 0:
            # Không có animation hữu hạn (vd: label/sublabel rỗng bị
            # display:none nên fade-in không chạy, chỉ còn nháy con trỏ
            # vô hạn): vẫn chụp 1 frame tĩnh đã settle thay vì báo lỗi
            # để rơi về WeasyPrint (render khác hẳn trình duyệt).
            print("ANIM-STATIC no finite animation, single settled frame")
            window = 0.0
        else:
            window = min(window, MAX_WINDOW)
        n = max(1, math.ceil(window * FPS))
        raw = outdir / "_raw"
        raw.mkdir(exist_ok=True)
        for i in range(n):
            t = i / FPS
            cmd("Runtime.evaluate", {
                "expression":
                f"document.getAnimations({{subtree:true}}).forEach(a=>"
                f"{{a.pause();a.currentTime={int(t*1000)};}})"})
            r = cmd("Page.captureScreenshot", {"format": "png"})
            (raw / f"f_{i:03d}.png").write_bytes(
                base64.b64decode(r["data"]))
        ws.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except Exception:
            proc.kill()
        shutil.rmtree(prof, ignore_errors=True)

    # union bbox theo alpha + scale theo luật composite_center (92%W/80%H)
    frames = []
    x0 = y0 = 10 ** 9
    x1 = y1 = -1
    for f in sorted(raw.glob("f_*.png")):
        im = Image.open(f).convert("RGBA")
        frames.append(im)
        alpha = im.getchannel("A")
        bbox = alpha.getbbox()
        if bbox:
            x0, y0 = min(x0, bbox[0]), min(y0, bbox[1])
            x1, y1 = max(x1, bbox[2]), max(y1, bbox[3])
    if not frames or x1 < 0:
        print("ANIM-FAIL empty frames", file=sys.stderr)
        return 1
    # Template full-stage (root position:absolute;inset:0: lớp phủ toàn khung
    # như typewriter/section-title) phải giữ nguyên kích thước khung, KHÔNG
    # co về 92%W/80%H như card thường (nếu không sẽ thành hình chữ nhật
    # lơ lửng với viền nền chưa phủ, khác hẳn preview).
    fullstage = (x0 <= 2 and y0 <= 2 and x1 >= W - 2 and y1 >= H - 2)
    pad = 6
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(W, x1 + pad), min(H, y1 + pad)
    bw, bh = x1 - x0, y1 - y0
    scale = 1.0 if fullstage else min(1.0, (W * 0.92) / bw, (H * 0.80) / bh)
    nw, nh = max(1, int(bw * scale)), max(1, int(bh * scale))
    for i, im in enumerate(frames):
        crop = im.crop((x0, y0, x1, y1))
        if scale < 1.0:
            crop = crop.resize((nw, nh), Image.LANCZOS)
        crop.save(outdir / f"seq_{i:03d}.png")
    shutil.copy(outdir / f"seq_{n-1:03d}.png", outdir / "hold.png")
    (outdir / "meta.json").write_text(json.dumps({
        "template_id": tid, "window_sec": round(window, 3), "fps": FPS,
        "n_frames": n, "width": nw, "height": nh,
        "fullstage": fullstage}, ensure_ascii=False))
    shutil.rmtree(raw, ignore_errors=True)
    page_path.unlink(missing_ok=True)
    print(f"ANIM-OK {tid} window={window:.2f}s frames={n} size={nw}x{nh}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
