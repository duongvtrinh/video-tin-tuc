---
name: broll-template-creator
description: Tạo hoặc nâng cấp template B-roll cho VieNeu Studio theo đúng engine thật (render tĩnh WeasyPrint → PNG trong suốt), schema meta.json specVersion 2, bảng token trong repo và bộ validator tự động. Dùng khi cần thêm template mới, sửa template, hoặc quyết định có nên tạo template mới hay không.
---

# Thợ rèn Template (v4 — khớp engine thực, 11/11/2026)

> Bản v3 mô tả kiến trúc 3 lớp (accent/motion), `tier`, `recommendedThemes`, `_drafts/`, font Be Vietnam Pro và lớp SVG —
> **không cái nào tồn tại trong engine/catalog** (đã đối chiếu code và 42 template). Bản này thay thế hoàn toàn.
> Tài liệu tham chiếu đầy đủ: `docs/TEMPLATE_SPEC.md`. Danh sách template hiện có: `docs/TEMPLATE_CATALOG.md`.

## 1. Có nên tạo template mới không?
Làm đủ 3 bước, dừng ở bước đầu tiên trả lời "không":
1. Đọc `docs/TEMPLATE_CATALOG.md`. Ý niệm cần minh họa đã có template phủ ≥80% (so `whenToUse`/`notFor`)? → **không tạo**, dùng template đó hoặc thêm biến thể input.
2. Cần đúng 1 lần cho đúng 1 video? → dùng footage/ảnh, **không tạo**.
3. Ý niệm lặp lại ở nhiều video và không template nào làm được? → tạo. Ghi rõ trong `description` nó KHÁC template gần nhất ở đâu (vd `share-bar` ≠ `compare-bars`: cơ cấu 100% vs giá trị tuyệt đối).

## 2. Engine thật hoạt động thế nào (ràng buộc bắt buộc)
- Render **tĩnh** bằng WeasyPrint 70: HTML+CSS → PNG, bằng 2 lần render nền trắng/đen rồi tính alpha. **Không có animation** (không `@keyframes`, không `animation:`); chuyển động do pipeline video xử lý ở ngoài.
- WeasyPrint **không** hỗ trợ: `:has`, `radial-gradient` với color-stop 2 vị trí, `box-shadow`/`text-shadow` (engine cắt khi render tĩnh — đừng dựa vào chúng để đọc được chữ).
- Placeholder `{{tên}}` thiếu hoặc không khai trong meta sẽ bị thay bằng chuỗi rỗng **thầm lặng** → mọi placeholder phải có trong `meta.inputs`.
- Kích thước tính bằng `vmin` (khung 9:16: 1 vmin = cạnh ngắn). Thẻ overlay rộng tối đa `528px`.
- `position` và `animation` trong `meta.inputs` **không có tác dụng** (engine không đọc) — không khai mới; template cũ đã đánh `noEffect`.

## 3. Quy chuẩn thiết kế (kiểm tự động trong validator)
- **Màu:** chỉ lấy từ `templates/_tokens.json` (accent + ink `#080A10` + chữ 3 nấc `#FFFFFF/#CBD5E1/#94A3B8` + nền rêu + màu theme). Màu theo `accent` dùng `var(--broll-accent)`. Ngoại lệ chỉ khi khai trong `paletteExceptions` (cần CEO duyệt). → mã M11.
- **Cỡ chữ:** `clamp(min px, N vmin, max px)` với N thuộc thang `typeScaleVmin` (2.5·2.8·3.4·3.9·4.3·5.0·6.5·8.5·11.0·15.0·23.1). → M11.
- **Font:** `'Anton', Arial, sans-serif`. Chữ dài: `overflow-wrap:anywhere`. Phần tử tùy chọn: `.broll-x-y:empty{display:none}`.
- **Class:** mọi class bắt đầu `broll-<tên ngắn>`. → M10.
- **Nền toàn màn hình:** dùng `var(--broll-bg,#1C372A)` và `var(--broll-grid,#2A4D3B)` để theme đổi được diện mạo (`plan.theme`); giá trị dự phòng = màu rêu cũ nên hình mặc định không đổi.
- **Thứ tự CSS khi ẩn/hiện theo `count`:** quy tắc ẩn mặc định (`display:none`) và quy tắc hiện theo `count` phải nằm **SAU** mọi khai báo `display` cùng độ ưu tiên của phần tử đó. (Lỗi thật khi tạo `share-bar`: hàng 4 vẫn hiện ở `count=3` vì `.broll-sb-item{display:flex}` khai sau đè lên.)

## 4. Quy trình
1. Tạo `templates/<id>/` gồm `template.html`, `style.css`, `meta.json`. Sao từ template **gần nhất** làm khung, không viết từ trắng.
2. `meta.json` đủ khóa `specVersion 2` (xem `docs/TEMPLATE_SPEC.md` §2): mỗi input có `maxLength`; enum có `values`; input số có `min/max/integer` (hoặc `pattern` nếu dùng làm CSS như `poll-vote`); `placement`; `neutralBgEligible`; `sfx` là object; `themes` thuộc `_themes.json`; `exampleInputs` hợp lệ; `constraints` cho quan hệ giữa input (tổng = 100, bắt buộc theo `count`).
3. `python3 bin/validate_templates.py` → **0 ERROR** (WARN có lý do thì ghi chú).
4. Render thật: `python3 bin/render_template.py <id> '<json inputs>' 720 1280 out.png`, **xem ảnh**, và thử **tải xấu nhất**: mọi input dài đúng `maxLength` bằng chữ rộng (`M`, `W`), `count` lớn nhất, input tùy chọn để trống. Ảnh phải rộng ≤ 540px ở khung 540 và không chữ đè/tràn.
5. Hồi quy: render lại toàn bộ catalog, so điểm ảnh với bản trước khi sửa — template cũ phải **giống hệt** (render xác định 100%).
6. `python3 bin/gen_catalog.py` (cập nhật `docs/TEMPLATE_CATALOG.md`), chạy `python3 tests/test_meta_check.py`.
7. Ghi `changelog` trong meta (không nhét lịch sử vào `description`). Tăng `version` khi đổi hình/hành vi; chỉ đổi metadata thì không cần.

## 5. Không làm
- Không hardcode ID template trong code engine (đặt vị trí = `placement` trong meta).
- Không chép tên template vào skill/doctrine — trỏ về `docs/TEMPLATE_CATALOG.md` (7 tên không tồn tại từng nằm trong tài liệu).
- Không dùng SVG/ảnh nhúng ngoài input `image`: pipeline chưa có đường xử lý/kiểm chứng cho `template.svg`.
- Không khai SFX ngoài 8 file chuẩn; SFX nặng (thud/slam/boom) ≤ 0.4; `offsetSec` ≥ 0.
