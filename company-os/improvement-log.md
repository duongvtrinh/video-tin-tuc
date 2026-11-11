# Improvement Log — Sổ vấn đề & cải tiến dùng chung toàn công ty

File này là **nơi chuẩn duy nhất** ghi mọi vấn đề và cải tiến quy trình của VieNeu Media Company (quyết CEO 11/11/2026). Mọi chi nhánh đọc file này khi bootstrap và trước mỗi ca bot-hoc-hoi; mọi chi nhánh đều thêm được mục mới và xem được mục của nhau.

## Luật ghi

1. **Chỉ ghi nối thêm.** Không sửa, không xóa mục đã có. Ngoại lệ duy nhất: cập nhật trường **Trạng thái** của một mục khi có quyết định/áp dụng — và việc cập nhật đó đi qua chat chính trong đợt hợp nhất.
2. **Mỗi mục có ID duy nhất:** `IMP-<YYYYMMDD>-<mã chi nhánh>-<số thứ tự 2 chữ số>` (mã chi nhánh = phần trước @ của email khai báo, ví dụ `003`). Ngày trong ID là ngày tạo mục.
3. **Trạng thái:** `ĐỀ XUẤT` → `ĐÃ DUYỆT` → `ĐÃ ÁP DỤNG` (ghi kèm mã commit ở cột Áp dụng tại), hoặc `TỪ CHỐI`.
4. **Cách một mục lên được file này:** phòng/bot phát hiện vấn đề hoặc đề xuất cải tiến thì ghi mục vào **bản local** của file này với trạng thái ĐỀ XUẤT và gửi nguyên văn mục đó về chat COO. Chat chính hợp nhất các mục vào bản repo và đẩy lên GitHub trong các đợt sửa đã được CEO duyệt (đúng quy tắc hỏi trước khi đẩy repo). Chỉ có một điểm hợp nhất để tránh các chi nhánh ghi đè file của nhau.
5. **Cải tiến chỉ thành sự thật khi trạng thái là ĐÃ ÁP DỤNG** — tức thay đổi đã nằm trong file chuẩn trên repo. Sửa ở bản local của một chi nhánh không tính là cải tiến của công ty.
6. Bot-hoc-hoi đọc file này trước khi đề xuất (không đề xuất trùng mục đã có); kết quả của bot là mục log ở trạng thái ĐỀ XUẤT, không tự sửa file chuẩn.

## Mẫu một mục

| ID | Ngày tạo | Chi nhánh | Loại | Mô tả (vấn đề / cải tiến + bằng chứng) | Thay đổi đề xuất (file + nội dung) | Trạng thái | Áp dụng tại |
| --- | --- | --- | --- | --- | --- | --- | --- |

## Các mục

| ID | Ngày tạo | Chi nhánh | Loại | Mô tả | Thay đổi đề xuất | Trạng thái | Áp dụng tại |
| --- | --- | --- | --- | --- | --- | --- | --- |
| IMP-20261111-003-01 | 2026-11-11 | 003@vuachim.com | Vấn đề | BOOTSTRAP.md ghi cứng "47 file" cho app-tao-video ở 4 chỗ trong khi repo có 48 file — chặn đứng phiên cài đặt 11/11/2026 (mục kiểm toán A1) | Thay BOOTSTRAP.md bằng bản v3: bỏ số đếm cứng, đối chiếu theo manifest + sổ migration | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (BOOTSTRAP v3) — commit eba2130 |
| IMP-20261111-003-02 | 2026-11-11 | 003@vuachim.com | Vấn đề | Kết quả "trả đủ 4 project" của máy cũ bị ghi như kỳ vọng cho máy mới (A2) | v3 mục C5 ghi rõ danh sách project trống là đạt trên máy mới | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (BOOTSTRAP v3) — commit eba2130 |
| IMP-20261111-003-03 | 2026-11-11 | 003@vuachim.com | Vấn đề | branch-memory mục 13 đếm thiếu placeholder (ghi 4, thực tế 5 — thiếu CHAT_ID_COO) (A3) | Sửa mục 13 thành 5 placeholder | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (branch-memory.md) — commit 83f9226 |
| IMP-20261111-003-04 | 2026-11-11 | 003@vuachim.com | Vấn đề | branch-memory mục 13 ghi slug goal của file mẫu như slug của chi nhánh (A4) | Ghi tách bạch 2 dòng: slug mẫu chung / slug thật của chi nhánh | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (branch-memory.md) — commit 83f9226 |
| IMP-20261111-003-05 | 2026-11-11 | 003@vuachim.com | Vấn đề | Đặc tả COO_TASKS tiếng Việt lệch nhãn tiếng Anh thật trên workbook (A5) | Thêm ghi chú chuẩn vào google-sheet-spec: khóa tiếng Anh là chuẩn hiện hành | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (google-sheet-spec.md) — commit 68322bb |
| IMP-20261111-003-06 | 2026-11-11 | 003@vuachim.com | Cải tiến | Cửa chặn hạn mức tuần đọc TASKS.L (văn bản tự do, dễ cũ, dễ nhầm chi nhánh trong workbook dùng chung) (B1) | Chốt COO_CHECKIN.TOKENS_LEFT (% dạng số, dòng điểm danh mới nhất của chính chi nhánh) là nguồn chuẩn duy nhất cho cửa chặn; TASKS.L chỉ là hồ sơ bàn giao | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (body Scout/Pipeline/COO, skill, bot-sop, branch-memory, spec, BOOTSTRAP v3) — commit eba2130, 5a39e38, 6bf433c, 208793c, 7528c93, 83f9226, 68322bb, 69168f6, 1a8d87d |
| IMP-20261111-003-07 | 2026-11-11 | 003@vuachim.com | Cải tiến | Mốc leo thang RETURNED chỉ nằm trong nhật ký ngày — mất nhật ký là trùng/sót leo thang (B2) | Ghi mốc ESC:<số lần trả>:<ngày> nối thêm vào TASKS.N của chính dòng video | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (body Pipeline + file mẫu, bot-sop) — commit 6bf433c, 7528c93 |
| IMP-20261111-003-08 | 2026-11-11 | 003@vuachim.com | Cải tiến | Lô cũ qua đêm và dòng vô chủ không có hạn chót leo thang khi COO không quyết (B3 + B10) | Mốc 2 buổi sáng liên tiếp chưa quyết → COO ghi CEO_REPORTS trong ca quét | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (body Pipeline bước 2h/13, body COO Bước 8, bot-sop) — commit 6bf433c, 208793c, 7528c93 |
| IMP-20261111-003-09 | 2026-11-11 | 003@vuachim.com | Cải tiến | Quy tắc email người sản xuất cho TASKS.L có hai cách diễn đạt có thể lệch nhau (B4) | Một bản duy nhất trong bộ nhớ (mục khai báo); skill QA, skill Production và body Pipeline rút thành câu trỏ về | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (2 skill, body Pipeline) — commit 6bf433c, b032cae, f864c41 |
| IMP-20261111-003-10 | 2026-11-11 | 003@vuachim.com | Cải tiến | Cải tiến của bot-hoc-hoi áp dụng ở local, không có đường vào repo — các chi nhánh lệch nhau âm thầm (B5) | Lập file log này; bot chỉ xuất mục ĐỀ XUẤT; chat chính hợp nhất + áp dụng + đẩy repo sau khi CEO duyệt | ĐÃ ÁP DỤNG | Chính file này + body bot-hoc-hoi + bot-sop + branch-memory — commit 4e9137f, 5160d33, 7528c93, 83f9226 |
| IMP-20261111-003-11 | 2026-11-11 | 003@vuachim.com | Vấn đề | Hai đường truy cập Facebook (connector qua Accounts Center / đăng nhập trình duyệt qua vault) dễ bị hiểu là một (B6) | Tách bạch trong BOOTSTRAP v3 mục D5 | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (BOOTSTRAP v3) — commit eba2130 |
| IMP-20261111-003-12 | 2026-11-11 | 003@vuachim.com | Cải tiến | Server TTS chết lặng sau khi máy ảo thay mới, Pipeline chỉ phát hiện giữa ca sau khi đã nhận lô (B7) | Kiểm tra health TTS ở đầu ca Pipeline: thử khởi động lại 1 lần; không đạt thì không nhận lô | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (body Pipeline bước 1, bot-sop) — commit 6bf433c, 7528c93 |
| IMP-20261111-003-13 | 2026-11-11 | 003@vuachim.com | Vấn đề | search_media.py ưu tiên biến môi trường trước Secure Vault mà không tài liệu nào ghi (B8) | Ghi thứ tự ưu tiên credential + chuẩn vault vào media-search/LOGIC.md | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (LOGIC.md) — commit 9265db9 |
| IMP-20261111-003-14 | 2026-11-11 | 003@vuachim.com | Ghi nhận | Đua nhận chủ đề giữa các chi nhánh khi 3 ca 06:00 chạy đồng thời — đã có claim-then-verify + kiểm tra trùng sau ghi đỡ trước khi giao sản xuất (B9) | Giữ nguyên thiết kế; ghi nhận chính thức trong bot-sop là lựa chọn đã chấp nhận có ý thức | ĐÃ ÁP DỤNG | Đợt sửa 11/11/2026 (bot-sop) — commit 7528c93 |
| IMP-20261111-003-15 | 2026-11-11 | 003@vuachim.com | Cải tiến | Luật suy ra theo ngày ("claim/ngày", "ca/ngày") âm thầm sai mỗi khi đổi bộ lịch | Bỏ hẳn khỏi mọi văn bản chuẩn/skill/file mẫu/body lịch; trần chỉ ghi theo ca (đã thực hiện ở đợt dọn trước trong cùng ngày) | ĐÃ ÁP DỤNG | Các commit dọn luật theo ngày 11/11/2026 (801c24d, 296652e, 2e786b1) + sửa tại máy cho 8 file còn lại |
