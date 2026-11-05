#!/usr/bin/env python3
"""Render nền cảnh cho 1 scene không có prompt AI — KHÔNG CÒN CARD CHỮ.

    <factory-venv-python> bin/render_scene_card.py <project_id> <order> <out_jpg>

Logic mới, theo lệnh CEO ngày 05/11/2026, thay thế hoàn toàn card chữ cũ
(kicker + headline + dòng nguồn trên nền tối):
- Mặc định: nền xanh rêu đậm #1C372A, kẻ ô vuông đơn giản, KHÔNG THÊM BẤT KỲ
  CHỮ NÀO lên ảnh — không kicker, không headline, không dòng nguồn, không
  thanh accent, không template overlay (template nào cũng chứa chữ nên
  đều bị bỏ qua). Các field headline/kicker/source/cardTemplateId trong
  plan nếu còn thì bị bỏ qua, không vẽ.
- Ngoại lệ duy nhất: scene khai cardImage/bgImage thì dùng chính ảnh đó
  làm nền (cắt về đúng tỉ lệ khung, không bóp méo), vẫn không thêm chữ
  nào lên trên. Đây là trường hợp ảnh nền đã có, không phải nền xanh rêu.
  Hành vi fallback (lựa chọn 10B, 05/11/2026): nếu scene khai cardImage/bgImage
  mà file không tồn tại (cả đường dẫn tuyệt đối lẫn build/media/images/<tên file>),
  script in cảnh báo rõ ràng "CARDIMAGE-MISSING" ra stderr rồi mới rơi về nền
  xanh rêu kẻ ô — không chặn, không lặng lẽ.
  A29 (05/11/2026): đường dẫn tương đối chỉ được tra trong project
  (build/media/images/<tên file>); không thấy ở đó thì coi như thiếu,
  không bao giờ nhặt file trùng tên theo CWD của tiến trình gọi.
- Khung theo render_draft.py: 9:16 -> 720x1280, còn lại -> 1280x720.
- Ô vuông: cạnh 80px ở khung 720 (scale theo chiều rộng khung), kẻ bằng
  đường màu xanh rêu nhạt #2A4D3B, dày 2px.

Lưu ý về trạng thái biên tập (không đổi so với luật sau 04/11/2026):
nền xanh rêu này KHÔNG phải ảnh thật, KHÔNG phải ảnh AI, và KHÔNG thay
thế ảnh — scene chỉ có nền này vẫn tính là thiếu ảnh ở tầng hồ sơ/QA,
giống như card chữ cũ. Nó chỉ là nền trung tính để karaoke không phải
chạy trên nền đen, và để không còn chữ headline lặp lại lời thoại.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image, ImageDraw  # noqa: E402

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)


MOSS_BG = "#1C372A"      # xanh rêu đậm nền
MOSS_GRID = "#2A4D3B"    # xanh rêu nhạt hơn nền, kẻ ô


def hex_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def main() -> int:
    pid, order_s, out_path = sys.argv[1], sys.argv[2], Path(sys.argv[3])
    order = int(order_s)
    proj = FACTORY / "projects" / pid
    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    scene = next((s for s in plan.get("scenes", []) if s.get("order") == order), None)
    if scene is None:
        print(f"không thấy scene order={order}", file=sys.stderr)
        return 1

    W, H = (720, 1280) if inp.get("aspectRatio", "9:16") == "9:16" else (1280, 720)

    # Ngoại lệ duy nhất: có ảnh nền khai sẵn thì dùng ảnh đó, không chữ.
    # 10B: khai mà file không tồn tại thì cảnh báo rõ rồi mới rơi về nền rêu.
    _card_img = scene.get("cardImage") or scene.get("bgImage")
    if _card_img:
        _p = Path(str(_card_img))
        if not _p.is_absolute():
            # A29 (05/11/2026): duong dan tuong doi CHI duoc tra trong
            # project (build/media/images/<ten file>). Khong thay o do thi
            # coi nhu thieu — KHONG giu duong dan tuong doi de CWD cua
            # tien trinh goi vo tinh nhat nham file trung ten.
            _p = proj / "build" / "media" / "images" / _p.name
        # B42 (06/11/2026, lệnh CEO, lựa chọn A): đường tuyệt đối phải
        # nằm trong project (resolve cả symlink/..); ngoài project, file
        # thiếu, hoặc mở không được thì đều CARDIMAGE-MISSING rồi rơi về
        # nền rêu — không crash traceback.
        _bg_im = None
        if _p.is_absolute() and _p.exists() and not _p.resolve().is_relative_to(proj.resolve()):
            print(f"CARDIMAGE-MISSING scene {order}: khai cardImage/bgImage={_card_img} nam ngoai project, roi ve nen xanh reu #1C372A ke o",
                  file=sys.stderr)
        elif not _p.exists():
            print(f"CARDIMAGE-MISSING scene {order}: khai cardImage/bgImage={_card_img} nhung file khong ton tai, roi ve nen xanh reu #1C372A ke o",
                  file=sys.stderr)
        else:
            try:
                _bg_im = Image.open(_p).convert("RGB")
            except Exception as _exc:
                print(f"CARDIMAGE-MISSING scene {order}: khai cardImage/bgImage={_card_img} mo khong duoc ({_exc}), roi ve nen xanh reu #1C372A ke o",
                      file=sys.stderr)
        if _bg_im is not None:
            _sw, _sh = _bg_im.size
            _scale = max(W / _sw, H / _sh)
            _nw, _nh = round(_sw * _scale), round(_sh * _scale)
            _bg_im = _bg_im.resize((_nw, _nh), Image.LANCZOS)
            _x, _y = (_nw - W) // 2, (_nh - H) // 2
            img = _bg_im.crop((_x, _y, _x + W, _y + H))
            out_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(out_path, "JPEG", quality=90)
            print(f"BG-IMAGE-OK {out_path} {W}x{H} (khong chu)")
            return 0

    # Mặc định: nền xanh rêu, kẻ ô vuông, không chữ.
    img = Image.new("RGB", (W, H), hex_rgb(MOSS_BG))
    draw = ImageDraw.Draw(img)
    step = round(80 * (W / 720))
    for x in range(step, W, step):
        draw.line([(x, 0), (x, H)], fill=hex_rgb(MOSS_GRID), width=2)
    for y in range(step, H, step):
        draw.line([(0, y), (W, y)], fill=hex_rgb(MOSS_GRID), width=2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=90)
    print(f"GRID-OK {out_path} {W}x{H} (nen xanh reu, ke o, khong chu)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
