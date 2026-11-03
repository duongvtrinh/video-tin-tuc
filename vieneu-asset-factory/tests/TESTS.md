# Kiểm thử trong repo (đợt B4, 01/11/2026)

Các test này CHƯA bắt buộc trong pipeline — chạy tay sau mỗi đợt sửa
render/karaoke/template/preview. Không có bước pipeline nào gọi chúng nên
chúng không chặn ai cho tới khi đợt D quyết định siết.

## 1. Self-test engine preview — `tests/engine_selftest.js`

Bản sao nguyên văn script chẩn đoán ngày 01/11/2026 (đã chứng minh engine
vô tội trong vụ CSS Tailwind bóp khung preview).

```sh
node tests/engine_selftest.js
```

Đọc output, phải thấy ở mọi mốc seek:

- `fgWrap` cố định: `left=0 right=0 top=160px height=960px`,
  `overflow=hidden`, `animationName=(none)`.
- Phần tử nhận animation là ảnh bên trong (`img`/`fgImg`), không phải cửa sổ.
- `covers=true` ở cả hai đầu keyframe (from và to).
- Part video hiện `fgVid` đúng box cửa sổ, `currentTime` đồng bộ.

Script chỉ in chẩn đoán, không tự kết luận pass/fail — người chạy đọc các
dòng trên mà kết luận.

## 2. Bảng kiểm tra template — `tests/check_templates.py`

Script ngày 31/10/2026 (đã render 34/34 mẫu, 0 lỗi), đã chỉnh nhẹ cho chạy
từ repo: thư mục ra lấy từ biến môi trường `TEMPLATE_CHECK_OUT`
(mặc định giữ đường cũ trong company-os để không ghi đè bản 31/10),
docstring sửa cho đúng luật hiện tại (không template nào ở top nữa).

```sh
TEMPLATE_CHECK_OUT=/tmp/template-check-20261101 \
  ~/workspace/asset-factory/.venv/bin/python tests/check_templates.py
```

Kết quả: khung JPG từng template + tờ tổng hợp + manifest. So sánh với
bản 31/10/2026 khi nghi template đổi hình.

## 3. Kiểm thử hồi quy clip đã render — `tests/regression_clip.py`

```sh
~/workspace/asset-factory/.venv/bin/python tests/regression_clip.py <project_id>
```

Kiểm tra trên MP4 đã render (không render lại): khung 720x1280 (với
project 9:16), không part nền đen (mean >= 8), part không template nào
cũng có karaoke lines > 0, part ảnh ngang/vuông có dải mờ yếu hơn hẳn
cửa sổ nét (tỉ lệ gradient < 0.5 ở cả hai dải). In `REG-PASS`/`REG-FAIL`
từng mục, exit 0 khi tất cả pass.

Đã chạy smoke trên `patriot001` ngày 01/11/2026: `REG-SUMMARY PASS`
(13 part, part template bỏ qua check lines, ảnh dọc bỏ qua check blur
đúng thiết kế).
