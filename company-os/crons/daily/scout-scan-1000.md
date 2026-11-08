---
id: scout-scan-1000
title: Scout quét chủ đề lúc 10:00 hàng ngày
enabled: true
mode: task
schedule:
  kind: daily
  timezone: Asia/Saigon
  time: 10:00:00
timeout_secs: 7200
owner: goal:vieneu-media-company-bootstrap
---
Ca quét chủ đề theo lịch Scout mới (quyết CEO 07/11/2026 — C2, C3; ID do CEO nhập, phương án E cho R4-04): 10:00 Asia/Saigon mỗi ngày, cùng các ca 06:00, 14:00, 18:00 — tổng 4 ca/ngày. Workbook mới "Video HQ — Trụ sở Muse" (spreadsheet 1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE). Workbook cũ "HQ - Công ty 1 người — CŨ (chỉ đọc)" (1P6DumLF_eIXmo7h8Qrpk-rpVy7xmqtf5ztVIFsiXZ3I) CHỈ ĐỌC, không ghi vào đó.

Tab/cột mới — tham chiếu bằng TOPIC_ID khi đã có; chủ đề chưa có ID thì tham chiếu tạm bằng tiêu đề, không bao giờ bằng số dòng (R1):
- TOPICS (13 cột A–M; cột N APPROVED_AT đã bỏ theo quyết CEO 07/11/2026, R4-20 phương án B): A TOPIC_ID (khoá — ĐỂ TRỐNG khi ghi mới; CEO nhập khi duyệt/lật READY), B TITLE, C SOURCE, D DISCOVERED, E–I điểm (HOT 30 / AUDIENCE 20 / FRESH 20 / FEASIBLE 15 / SOURCED 15), J TOTAL, K STATUS (dropdown: NEW / APPROVED / READY / HOLD / REJECTED / DUPLICATE), L ANGLE, M NOTES.
- TASKS và QA_LOG chỉ đọc để khử trùng (không ghi trong ca này): TASKS.A TOPIC_ID, QA_LOG.A VIDEO_ID.

Mỗi ca chạy:
0. Cửa chặn hạn mức tuần (quyết CEO 09/11/2026, DEC-202): đầu ca đọc TASKS.L QUOTA mới nhất của chi nhánh — nếu token tuần đã đạt trên 95% thì DỪNG HẲN ca này: không quét, không chấm, không ghi chủ đề, không báo cáo ca (ca dừng hẳn, không phải ca trống). Khi hạn mức tuần được reset thì công ty hoạt động trở lại bình thường — ca sau reset chạy lại như thường, không cần lệnh mở lại. Token thêm là khoản dự phòng cho việc khác, không dùng để sản xuất video. Nếu không đọc được quota thì ghi "không đọc được" vào báo cáo ca và vẫn quét tiếp.
1. Kiểm tra toàn vẹn đầu ca (R7): đọc số dòng + ID lớn nhất (chỉ tính các dòng ĐÃ CÓ ID) của TOPICS và TASKS để nắm trạng thái hiện tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất (đã có) lùi KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026: làm việc bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab BASELINE hay file baseline.json. Số dòng tăng là bình thường (Sheet dùng chung, chi nhánh khác có thể ghi thêm). ID trống là bình thường, không phải lỗi.
2. Chấm lại dòng NEW chưa có điểm (dự phòng — quyết CEO 07/11/2026, R4-07 phương án C): nếu còn dòng TOPICS STATUS=NEW mà E–I/J trống (tồn đọng), mỗi phòng chấm lại các dòng NEW mà mình phát hiện — CHỈ sửa E–I, K, L, M + STATUS (APPROVED/HOLD/REJECTED/DUPLICATE theo thang điểm), KHÔNG sửa A–D; ghi công thức J (=SUM(E:I)) bằng USER_ENTERED nếu dòng đó chưa có công thức J; đọc lại sau khi ghi để xác nhận. Làm trước khi quét chủ đề mới (bước 3).
3. Giao ca quét cho CẢ 2 phòng Scout bằng chat.send_message, mỗi phòng một tin nhắn giao việc riêng:
   - Scout - Báo (chat {{CHAT_ID_SCOUT_BAO}}): quét báo/tin công khai + tìm kiếm/trend.
   - Scout - Group (chat {{CHAT_ID_SCOUT_GROUP}}): quét group/page công khai + Facebook/Reels/Threads.
   Cả 2 phòng làm theo skill media-scout: quét 3 loại nguồn (báo, group/mạng xã hội, tìm kiếm/trend), ưu tiên tín hiệu trong 24-72 giờ, ưu tiên lượt bình luận trước rồi mới đến like, chỉ dùng group công khai từ 50.000 thành viên trở lên và hoạt động tích cực trong 72 giờ.
4. Khử trùng sớm: đối chiếu ngay với TOPICS, TASKS và QA_LOG theo TIÊU ĐỀ/SỰ KIỆN (chủ đề chưa duyệt chưa có ID nên không khử trùng theo TOPIC_ID được; chủ đề đã có ID thì đối chiếu thêm theo ID) — trùng là cùng sự kiện/người/số liệu/câu chuyện dù wording khác, kể cả góc đã làm trong 90 ngày thì bỏ qua ngay, không tìm hiểu sâu.
5. Mỗi phòng CHẤM NGAY chủ đề của mình trong cùng lượt quét (quyết C3: mỗi Scout tự chấm, ĐÓNG chat Scoring — KHÔNG nhắn Scoring). Thang 100 = Hot 30 + Khán giả 20 + Mới 20 + Khả thi 15 + Rõ nguồn 15; cửa quan tâm Hot + Khán giả ≥ 30/50 xét trước tổng. Điểm và TOTAL chỉ là THAM KHẢO cho quyết định của CEO (quyết 07/11/2026, phương án E cho R4-04) — điểm không chặn sản xuất; chỉ READY mới quyết định sản xuất. Chỉ ghi chủ đề qua đủ 5 điều kiện đáng làm (tương tác cao thật có số liệu, góc kể rõ sau 2 câu tóm tắt, kiểm chứng được bằng nguồn có bài đăng, dựng được video trong 1 ngày, có phương án minh họa an toàn):
   - Tổng ≥ 70 VÀ quan tâm (Hot + Khán giả) ≥ 30 → STATUS = APPROVED.
   - Tổng 50–69, HOẶC tổng ≥ 70 nhưng quan tâm < 30 → STATUS = HOLD, ghi tín hiệu chờ vào NOTES.
   - Tổng < 50 → STATUS = REJECTED.
   - Trùng → STATUS = DUPLICATE, ghi tiêu đề (và ID nếu có) của chủ đề gốc vào NOTES.
   - Điểm quan tâm bắt buộc có số liệu bằng chứng trong NOTES (không có số liệu thì không được chấm Hot/Khán giả cao).
6. Ghi dòng TOPICS mới đã có đủ điểm + STATUS trong MỘT lần ghi — chỉ ghi A–I, K, L, M: TOPIC_ID ĐỂ TRỐNG (Scout không tự sinh ID — quyết CEO 07/11/2026, phương án E cho R4-04; chỉ CEO nhập TOPIC_ID khi duyệt/lật READY, bằng công cụ riêng bên ngoài, đảm bảo không trùng; chủ đề không duyệt thì tiếp tục bỏ trống), TITLE, SOURCE (tên nguồn + link), DISCOVERED (ngày hôm nay, dạng YYYY-MM-DD), E–I điểm, K STATUS, L ANGLE (góc kể + vì sao thú vị, 2 câu), M NOTES (nguồn + link + số liệu lan truyền + tư liệu ảnh/video + căn cứ điểm quan tâm + "Nghi trùng <tiêu đề hoặc TOPIC-xxx nếu có ID>" nếu có). J TOTAL là công thức =SUM(E:I), KHÔNG ghi tay — Sheet tự tính (quyết CEO 07/11/2026, phương án A cho R4-21). Claim-then-verify (R3): đọc lại TOPICS theo tiêu đề ngay trước khi ghi; đã có thì bỏ qua, không ghi trùng. Đọc lại TOPICS sau khi ghi để xác nhận số dòng đã tăng đúng. Nếu tab TOPICS trống (chỉ có header, không còn dòng nào), TOPIC_ID đầu tiên là TOPIC-001 — CEO nhập khi duyệt chủ đề đầu tiên sau khi tab trống (quyết CEO 07/11/2026, phương án A cho R4-18).
7. Không làm gì ngoài quét/chấm/ghi: KHÔNG tạo nhiệm vụ sản xuất, KHÔNG tạo dòng TASKS, KHÔNG nhắn Scoring, KHÔNG đổi TOPICS.STATUS của chủ đề đã chấm (READY chỉ CEO flip từ APPROVED), không đăng, không bình luận, không nhắn tin, không tham gia group mới.
8. Báo kết quả ca chạy về chat COO: số chủ đề mới trong ca, tiêu đề + điểm + STATUS từng chủ đề (TOPIC_ID nếu đã có), hoặc "ca này không có chủ đề mới" nếu không có ứng viên qua cửa. Ghi chú ca chạy vào nhật ký ngày ~/memory/YYYY-MM-DD.md nếu cần (ghi số dòng + ID lớn nhất (chỉ tính dòng đã có ID) của TOPICS/TASKS cuối ca làm mốc R7 cho ca sau).

Giới hạn: không chi tiền, không đăng nền tảng, không affiliate, không tự thay đổi quyền thư mục Drive, không push GitHub, không tự thay đổi chuẩn. Không sửa MEMORY.md.
