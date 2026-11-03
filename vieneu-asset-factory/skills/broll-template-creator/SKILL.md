---
name: broll-template-creator
description: Rèn template B-roll tái sử dụng cho VieNeu Studio theo kiến trúc 3 lớp (base/accent/motion), hỗ trợ SVG dữ liệu an toàn và motion hooks. Tương thích renderer Puppeteer và chính sách bảo mật allowlist.
---

# Thợ rèn Template (Template Smith)

## 1. Vai trò
Bạn rèn vũ khí cho director: template tái sử dụng. Mỗi template phải trả lời: *nó minh họa ý niệm nào mà template hiện có chưa làm được?* Nếu ý niệm đã có template phủ ≥80% → không rèn mới.

## 2. Kiến trúc 3 lớp (bắt buộc)

1. **Base layer** — `template.html` (partial, allowlist) + `style.css` (scope `.broll-<id>`).
2. **Accent layer** — chỉ dùng `var(--broll-accent)`; cấm hardcode màu.
3. **Motion layer** — KHÔNG tự định nghĩa animation cứng; nhận từ hệ thống qua 4 khái niệm: `entrance` / `content` / `exit` / `stagger_interval` (do motion-composer gán). Template khai báo `supportsMotion: true` và class hooks.

## 3. Quy chuẩn bảo mật & kỹ thuật

### A. HTML (allowlist)
- Thẻ: `div`, `span`, `strong`, `em`, `b`, `i`, `p`, `br`, `small`, `section`, `h1`–`h4`, `ul`, `ol`, `li`.
- Cấm: `script`, `style`, `iframe`, `img`, `video`, `svg` (xem mục 4 cho ngoại lệ), `canvas`, `a`, `button`, `form`, `input`, event handler.
- Thuộc tính: `class`, `style`, `aria-hidden`, `role`. Cấm placeholder trong thuộc tính.
- Placeholder: `{{text}}`, `{{sublabel}}`, `{{label}}`, `{{value}}`, `{{unit}}`, `{{items}}` — chỉ trong nội dung text.

### B. System enums (wrapper quản lý, không đặt trong HTML)
- `accent`: `gold`, `red`, `cyan`, `green`, `violet`, `white`, `orange`, `pink` → `var(--broll-accent)`.
- `position`: `top`, `center`, `bottom`, `left`, `right` (wrapper canh).
- `animation` (hiệu ứng vào): `fade`, `slide-up`, `slide-left`, `slide-right`, `pop`, `wipe`, `none`.
- Hiệu ứng nội dung (`content`): `typewriter`, `stagger`, `count-up`, `draw-on`, `none` — khai báo riêng, không trộn vào `animation`.

### C. CSS
- Mọi selector bắt đầu `.broll-<template_id>`; cấm class hệ thống (`.broll-shell`, `.broll-tpl`...).
- Cấm `url()`, `image-set()`, `@import`, `@font-face`, `@charset`, ký tự `\`.
- Luôn có rule `:empty { display: none }` cho phần tử rỗng.
- Font: `var(--vst-font-family, 'Be Vietnam Pro', sans-serif)`.

### D. Vùng an toàn
Tránh 22% đáy (phụ đề) + 10% đỉnh (UI mạng xã hội). Test 9:16, 16:9, 1:1.

## 4. SVG dữ liệu an toàn (tầng đồ họa mở rộng)

Subset trắng cho file `template.svg` (riêng, validator kiểm tra riêng):
- Thẻ: `svg`, `g`, `rect`, `circle`, `line`, `polyline`, `path`, `text`.
- Thuộc tính: chỉ hình học/số (`x`, `y`, `width`, `height`, `cx`, `cy`, `r`, `d`, `points`, `fill`, `stroke`, `stroke-width`, `opacity`, `font-size`, `text-anchor`, `transform` với `translate`/`scale` số).
- Cấm tuyệt đối: `script`, `on*`, `href`, `xlink:href`, `foreignObject`, `image`, `use`, SMIL `<animate>`.
- Mọi số hiển thị bind từ `inputs`; thiếu → ẩn.

## 5. meta.json (mở rộng, tương thích ngược)
```json
{"id": "...", "tier": 1, "status": "active",
 "capability": ["stat", "so sánh"],
 "recommendedThemes": ["finance", "general"],
 "preferredGenres": ["finance"],
 "supportsLayers": true, "supportsMotion": true,
 "defaultMotion": {"entrance": {"type": "pop", "durationMs": 420}},
 "safeZone": {"topPercent": 10, "bottomPercent": 22}}
```
- `status`: `active` | `draft` | `retired`. Thư mục `_drafts/` không bao giờ active.
- `capability` (làm được gì) tách khỏi `recommendedThemes` (hay dùng ở đâu). Theme không phải bộ lọc tuyệt đối.
- `exampleInputs` phải tuân thủ cùng chính sách với skill (không dạy ví dụ vi phạm).

## 6. Quy trình draft → duyệt
1. Đặt id (2–48 ký tự) → viết file vào `_drafts/<id>/`.
2. Chạy validator (`validate_template` + nhánh SVG).
3. Render thử 3 khổ hình với inputs mẫu + inputs rỗng.
4. User duyệt → sang catalog active. Template 90 ngày không ai chọn → `retired`.

## 7. Khi nào KHÔNG rèn mới
- Ý niệm đã phủ ≥80%. Chỉ cần 1 lần duy nhất (dùng footage/graphic đơn giản). Chưa có validator cho tầng muốn dùng.
