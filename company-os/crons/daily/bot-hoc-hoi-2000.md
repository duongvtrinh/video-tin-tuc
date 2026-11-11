---
id: bot-hoc-hoi-2000
title: Hoc-hoi kiểm mẫu + vòng học-hỏi lúc 20:00 hàng ngày
enabled: true
mode: task
schedule:
  kind: daily
  timezone: Asia/Saigon
  time: 20:00:00
timeout_secs: 7200
owner: goal:vieneu-media-company-bootstrap
---
Ca hoc-hoi theo quyết CEO 07/11/2026 — R4-14 phương án A (DEC-019): 20:00 Asia/Saigon mỗi ngày. Workbook mới "Video HQ — Trụ sở Muse" (spreadsheet 1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE). Workbook cũ CHỈ ĐỌC (xem spec).

Vai trò: (1) kiểm mẫu — biện pháp bù (c) cho quyết C3 (gộp Scout + Scoring: mất lớp kiểm độc lập "không chấm chủ đề do mình quét", bù bằng (a) điểm quan tâm bắt buộc có số liệu bằng chứng trong NOTES, (b) cổng READY của CEO, (c) hoc-hoi kiểm mẫu); (2) vòng học-hỏi — biến lỗi lặp lại thành cải tiến vĩnh viễn cho quy trình, để hệ thống ngày một thông minh hơn — nhưng chỉ cải tiến khi có bằng chứng, không bịa cải tiến, không nới lỏng chuẩn.

Cron này CHỈ ĐỌC Sheet + skill + nhật ký, KHÔNG ghi vào Sheet (không ghi TOPICS/TASKS/QA_LOG/DECISIONS/COO_TASKS/CEO_REPORTS/COO_CHECKIN); chỉ báo cáo về chat COO. Mọi vấn đề/cải tiến phát hiện được ghi thành mục trong company-os/improvement-log.md (bước 5–6); KHÔNG tự sửa file chuẩn của repo như một cải tiến đã xong, KHÔNG push GitHub.

Tab/cột mới — tham chiếu bằng TOPIC_ID khi đã có; chủ đề chưa có ID thì tham chiếu tạm bằng tiêu đề, không bao giờ bằng số dòng (R1):
- TOPICS (13 cột A–M; cột N APPROVED_AT đã bỏ theo quyết CEO 07/11/2026, R4-20 phương án B): A TOPIC_ID (khoá — ĐỂ TRỐNG khi ghi mới; CEO nhập khi duyệt/lật READY), B TITLE, C SOURCE, D DISCOVERED, E–I điểm (HOT 30 / AUDIENCE 20 / FRESH 20 / FEASIBLE 15 / SOURCED 15), J TOTAL, K STATUS (dropdown: NEW / APPROVED / READY / HOLD / REJECTED / DUPLICATE), L ANGLE, M NOTES.
- TASKS: A TOPIC_ID, B TITLE, C STATUS (CLAIMED / BUILDING / REVIEW / RETURNED / APPROVED / DELIVERED / BLOCKED / CANCELLED), D ASSIGNEE, E DRAFT_LINK, F QA_VERDICT, G RETURNS, H DRIVE_LINK, I MD5, J UPDATED_AT, K PROD_NOTES, L QUOTA, M BLOCKER, N DUP_NOTE, O FACEBOOK (do bên khác quản lý).
- QA_LOG: A VIDEO_ID, B VERSION, C DATE, D RESULT (APPROVED / RETURNED), E ISSUES, F REPO_NOTE.
- DECISIONS: A DECISION_ID, B ISSUE, C OPTION_A, D OPTION_B, E COO_PROPOSAL, F CEO_DECISION, G DATE.
- COO_TASKS: A ID, B ASSIGNEE_EMAIL, C TASK, D DETAIL, E STATUS (Assigned / Đang làm / Hoàn thành / Tắc), F COMPLETED_AT, G RESULT.
- CEO_REPORTS (9 cột A–I: A REPORT_ID, B DATE_REPORTED, C ASSIGNEE_EMAIL, D ISSUE, E TRIED, F NEEDS_DECISION, G CEO_REPLY, H APPLIED_BY, I DATE): ĐƯỢC đọc làm dữ liệu học-hỏi (các vấn đề leo thang + cách CEO quyết), KHÔNG ghi vào tab này.

Mỗi ca chạy:
1. Kiểm tra toàn vẹn đầu ca (R7): chỉ đọc số dòng + ID lớn nhất (chỉ tính các dòng ĐÃ CÓ ID) của TOPICS và TASKS để nắm trạng thái hiện tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất (đã có) lùi KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026, R4-12: làm việc bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab BASELINE hay file baseline.json. Số dòng tăng là bình thường (Sheet dùng chung, chi nhánh khác có thể ghi thêm). ID trống là bình thường, không phải lỗi.
2. Kiểm mẫu (chức năng chính): đọc ngẫu nhiên 2–3 chủ đề đã được chấm trong ngày (TOPICS có điểm E–I và NOTES, DISCOVERED = hôm nay); kiểm lại từng cột điểm (HOT/AUDIENCE/FRESH/FEASIBLE/SOURCED) + nguồn (SOURCE) + số liệu bằng chứng trong NOTES. Ghi rõ mỗi chủ đề kiểm: TOPIC_ID (hoặc tiêu đề nếu chưa có ID), điểm gốc, điểm kiểm lại, khớp/lệch ở cột nào, nguồn có đúng vụ việc không. Nếu trong ngày không có chủ đề nào được chấm thì ghi rõ "ngày này không có chủ đề mới được chấm" và bỏ qua bước kiểm mẫu.
3. Vòng học-hỏi — thu thập: đọc QA_LOG và TASKS trong 7 ngày gần nhất (verdict Duyệt/Trả lại, lý do trả, số lần trả mỗi video), DECISIONS, CEO_REPORTS (các vấn đề leo thang + cách CEO quyết), nhật ký ngày trong 7 ngày gần nhất, và các skill + spec hiện tại cùng company-os/improvement-log.md (để không đề xuất trùng mục đã có) (media-scout, media-video-production, media-video-tech-qa; phòng Scoring đã đóng ngày 07/11/2026 theo quyết C3, skill media-topic-scoring đã ngừng dùng).
4. Vòng học-hỏi — tìm mẫu lặp: chỉ tính mẫu có bằng chứng từ 2 video trở lên, ví dụ: cùng một lỗi QA/preflight lặp lại, cùng một mẫu câu kịch bản bị trả, cùng một khái niệm media hay bị tìm lệch hoặc rơi về fallback, cùng một template gây lỗi, chủ đề điểm cao nhưng sản xuất kém (hoặc ngược lại), chu kỳ sản xuất dài bất thường ở cùng một khâu, video bị QA trả vì part đứng yên >5s / thiếu đo motion PNG 2fps trước khi nộp. Ghi rõ mỗi mẫu: tên mẫu, số video ảnh hưởng, bằng chứng (tên video, mốc thời gian, file, dòng QA log).
5. Vòng học-hỏi — ghi mục log cải tiến (quyết CEO 11/11/2026, thay mô hình tự áp dụng vào repo local của DEC-019): mỗi mẫu lặp đủ bằng chứng (kèm: mẫu lỗi, bằng chứng, cách sửa đề xuất, cách kiểm chứng) thành một mục trong company-os/improvement-log.md — ID dạng IMP-<YYYYMMDD>-<chi nhánh>-<số thứ tự>, đủ các trường: ngày, chi nhánh (email khai báo), loại (vấn đề / cải tiến), mô tả, bằng chứng, thay đổi đề xuất ghi rõ file + nội dung trước/sau — ghi nối thêm vào bản local của file log với trạng thái ĐỀ XUẤT và gửi nguyên văn mục đó về chat COO. Bot KHÔNG tự sửa template/skill/spec như một cải tiến đã xong: thay đổi chỉ vào file chuẩn sau khi CEO duyệt, do chat chính áp dụng và đẩy lên repo, rồi trạng thái mục log chuyển ĐÃ ÁP DỤNG kèm mã commit.
6. Ghi log: các mục log đã tạo ở bước 5 cũng ghi tóm tắt vào nhật ký ngày ~/memory/YYYY-MM-DD.md (kèm ID mục) để tra cứu; nhật ký ngày không thay thế improvement-log.md — file log trên repo mới là nơi chuẩn duy nhất để các chi nhánh xem được mục của nhau. Không ghi đè hay xóa dòng/mục đã có.
7. Đề xuất cần CEO quyết (chỉ ghi lại, KHÔNG tự áp dụng): mọi ý tưởng đụng tới giới hạn cứng hoặc chuẩn đã chốt — đổi lệnh tự quyết độ dài (đề xuất 2–3 phút, Production tự quyết; chuẩn 180-300s đã bãi theo lệnh CEO tối 29/10/2026, xem A5), đổi 3 cửa QA, đổi thang điểm chấm chủ đề (thang 100 trong skill media-scout), đổi phạm vi công ty, đăng nền tảng, affiliate, chi tiền, push GitHub, thay đổi quyền thư mục Drive, xóa dữ liệu. Những đề xuất này chỉ xuất hiện trong báo cáo về chat COO, kèm lý do và bằng chứng, để COO leo thang qua CEO_REPORTS khi cần CEO quyết.
8. Báo cáo kết quả ca chạy về chat COO: (a) kết quả kiểm mẫu — kể cả khi tất cả đều khớp thì báo ngắn 1 dòng (số chủ đề đã kiểm, đều khớp); khi lệch thì báo chi tiết từng chủ đề (điểm gốc, điểm kiểm lại, lệch cột nào, nguồn có đúng vụ việc không) + đề xuất; (b) liệt kê từng mục log cải tiến đã tạo (ID mục + tóm tắt + trạng thái ĐỀ XUẤT), nếu có; (c) đề xuất cần CEO quyết, nếu có; (d) blocker MỚI, nếu có. Ca không có gì mới ngoài kiểm mẫu đều khớp thì chỉ báo 1 dòng kiểm mẫu, không báo thêm phần học-hỏi. Nếu không tìm thấy mẫu lặp đủ bằng chứng thì KHÔNG bịa cải tiến: ca này im lặng về phần học-hỏi (chỉ báo phần kiểm mẫu), kết quả lưu trong lịch sử ca.

Giới hạn: không đăng nền tảng, không gắn affiliate, không chi tiền, không push GitHub, không bịa nguồn/link/số liệu/bằng chứng, không ghi đè hay xóa dòng đã có, không sửa MEMORY.md. Gặp 429/403/rate-limit thì dừng nhánh đó, ghi blocker, không chờ, không thử lại ẩu.
