# Gói thay đổi 12/11/2026 — ảnh/video cảnh chung + s1p1, câu mở đầu kịch bản

Giải nén đè lên thư mục gốc `vieneu-media-company-main/`. `thay-doi.patch` là diff của các file SỬA so với bản gốc (`patch -p1 < thay-doi.patch`); 3 file MỚI nằm sẵn trong gói.

## A. Ảnh/video cho cảnh chung và part s1p1
- Mọi part đã có ảnh/video riêng (kể cả cảnh 1 part) → không tạo ảnh cảnh chung; preflight không đòi.
- Có cả part có và chưa có → lấy 1 ảnh/video của part đại diện làm ảnh cảnh chung (qua luật kề nhau + trần 2 lần/video).
- Không part nào có → bắt buộc có ảnh/video cảnh chung, không để màn hình đen.
- Ảnh cảnh chung và s1p1 không bao giờ là nền trung tính — preflight chặn bằng code.
- Sửa: `bin/preflight.py`, skill sản xuất (mục mới), `media-search/LOGIC.md` (mục 8), skill QA, `qa-checklist.md`, `PIPELINE.md`.

## B. Câu mở đầu kịch bản
- Câu đầu là 1 trong 13 dạng, tuyệt đối không số liệu, không ngày tháng; số liệu và cảnh cụ thể dời xuống câu 2.
- Mới: `skills/SCRIPT_DOCTRINE.md` (mục 3.1 có bảng 13 dạng, cách chọn, ràng buộc), `bin/script_lint.py`, `PHAN-TICH-SKILL-KICH-BAN.md`.
- Sửa: `script-prompt.ts` + `script-prompt.test.ts`, 3 file `prompts/video_script_*.txt`, skill sản xuất, skill QA, `qa-checklist.md`.

## script_lint.py (bản gọn)
Chỉ kiểm chất lượng viết và số liệu: mẫu cấm C1–C9, câu hỏi Q1/Q2, nhịp câu, câu mở đầu K1/K3/K4, đối chiếu số với dữ kiện V1. Không kiểm ký hiệu/định dạng/cách đọc (do bộ chuẩn hoá của VieNeu-TTS lo).

## Chưa sửa
`app-tao-video/client/src/lib.ts`, `server/src/priv/handlers-projects.ts`, `server/src/priv/projects.ts` vẫn đòi ảnh cảnh cho mọi cảnh (chặn ở tầng app). Muốn luật mới chạy trọn trong app thì sửa 3 chỗ này theo điều kiện "cảnh còn part chưa có ảnh/video riêng".
