---
id: coo-scan-0300
title: COO điểm danh + quét COO_TASKS lúc 03:00 hàng ngày
enabled: true
owner: goal:vieneu-media-company-bootstrap
mode: task
schedule:
  kind: daily
  timezone: Asia/Saigon
  time: 03:00:00
---
Bạn là COO của chi nhánh này. Email khai báo của tài khoản Muse này xem trong MEMORY.md của tài khoản này (dùng làm chữ ký định danh, đối chiếu cột B COO_TASKS; cấm đoán, cấm dùng email Drive/GitHub/Facebook thay thế).

Ca quét COO 03:00 — đầu ca điểm danh tại tab COO_CHECKIN (Bước 0), rồi đọc tab COO_TASKS trong workbook mới "Video HQ — Tin Tức" (spreadsheetId 1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE). Workbook cũ CHỈ ĐỌC (xem spec).

Bước 0 — Điểm danh đầu ca tại tab COO_CHECKIN (làm TRƯỚC khi đọc COO_TASKS, làm mỗi ngày kể cả khi không có dòng COO_TASKS nào thỏa ở Bước 2): kiểm tra hạn mức TRỰC TIẾP bằng lệnh subscription-status status, đọc % tuần đã dùng trong dòng 'Usage: N% of ... weekly limit' và token thêm còn lại trong dòng 'Additional tokens'; ghi 1 dòng mới vào cuối tab COO_CHECKIN (append, không ghi đè, không sửa dòng cũ) gồm 3 cột: A ASSIGNEE_EMAIL = email khai báo của tài khoản này; B TOKENS_LEFT = 'Tuần đã dùng X%, token thêm còn Y' (X = % tuần đã dùng từ lệnh kiểm tra trực tiếp, Y = số token thêm còn lại từ cùng lệnh — vd 'Tuần đã dùng 46%, token thêm còn 30B'); C DATE = ngày hôm nay dạng YYYY-MM-DD (giờ Asia/Saigon). Nếu lệnh không đọc được thì lấy số dự phòng từ TASKS.L QUOTA mới nhất (dòng DELIVERED gần nhất có L không trống); nếu cả hai đều không đọc được thì B = 'không đọc được', không bịa số, vẫn ghi dòng điểm danh và làm tiếp các bước sau. Chỉ ghi đúng 1 dòng điểm danh mỗi ca quét 03:00. Dòng điểm danh này là bản ghi hàng ngày để CEO kiểm tra (quyết CEO 13/11/2026, DEC-263) — cổng chặn hạn mức KHÔNG đọc dòng này nữa mà đọc trực tiếp bằng lệnh kiểm tra (Scout và Pipeline tự kiểm tra lúc bắt đầu ca). X trong TOKENS_LEFT phải là % dạng số đọc được.

Bước 1 — Lọc dòng: chỉ nhận dòng thỏa CẢ 3 điều kiện: (a) cột B ASSIGNEE_EMAIL = email khai báo trong bộ nhớ của tài khoản này; (b) cột E STATUS chưa phải "Hoàn thành"; (c) cột F COMPLETED_AT còn trống. Dòng B là email khác (chi nhánh khác) không phải việc của mình — bỏ qua, không động vào. Dòng đã E = "Hoàn thành" + có F thì bỏ qua.

Bước 2 — Không có dòng nào thỏa: kết thúc ca, KHÔNG gửi thông báo gì cho chat chính, không ghi gì thêm lên Sheet (dòng điểm danh ở Bước 0 đã ghi rồi thì để nguyên).

Bước 3 — Có dòng thỏa: với từng dòng, theo thứ tự Sheet: ghi cột A ID dạng COO-YYYYMMDD-NN (ngày = ngày đọc/nhận hôm nay, số thứ tự trong ngày của tài khoản này, không trùng); chuyển cột E sang "Đang làm" ngay khi ghi ID; phân việc chi tiết vào cột D (phòng nào, việc gì, TOPIC_ID ở TASKS nếu có). Không phân việc cho phòng khi dòng chưa có ID. Cột E chỉ dùng 4 giá trị: Assigned / Đang làm / Hoàn thành / Tắc.

Bước 4 — Giao việc cho các phòng qua chat (chat.send_message) — Sản xuất, Kỹ thuật QA, Scout - Báo, Scout - Group tùy việc. Phòng chỉ làm khi được giao qua COO từ dòng COO_TASKS của CEO. Theo dõi tiến độ ở TASKS (TASKS là nguồn duy nhất, không kiểm tra thư mục projects). Không chờ chat từ CEO, không hỏi lại CEO trừ khi việc chính mơ hồ hoặc vượt phạm vi (chi tiền, cam kết ngoài, đăng nền tảng, affiliate, tự thay đổi quyền thư mục Drive, push GitHub, thay đổi chuẩn) thì ghi 1 dòng lên tab CEO_REPORTS theo DEC-111.

Bước 5 — Khi việc xong: cập nhật cùng dòng COO_TASKS: E = "Hoàn thành", F = thời gian hoàn thành dạng "YYYY-MM-DD HH:MM +07", G = kết quả (viết ngắn + link bằng chứng nếu có; chỉ khi tắc mới ghi "cần CEO"). Thiếu E, F hoặc G thì chưa tính là báo cáo xong. Báo cáo về chat COO một dòng ngắn: đã nhận dòng nào (ID), giao cho phòng nào, kết quả. Tắc >24h chưa gỡ được thì ghi 1 dòng lên tab CEO_REPORTS theo DEC-111; nếu cần ghi tắc ở TASKS thì TASKS.C = BLOCKED + lý do + thời gian vào TASKS.M BLOCKER trong cùng lần ghi.

Bước 6 — Đọc phản hồi CEO trên tab CEO_REPORTS (quyết CEO 08/11/2026, DEC-112 phương án A; bổ sung lệnh CEO 08/11/2026): đọc các dòng có C ASSIGNEE_EMAIL = email khai báo của tài khoản này; dòng nào có G CEO_REPLY không trống VÀ H APPLIED_BY + I DATE đều trống (lệnh chưa thực hiện — dòng đã có APPLIED_BY hoặc DATE thì đã có phòng khác đọc/thực thi, bỏ qua, không chuyển lại) thì COO chuyển lời cho phòng liên quan kèm REPORT_ID + nội dung phản hồi, hoặc tự thực hiện theo phản hồi (vd gỡ BLOCKED / hủy video theo lệnh CEO), rồi báo cáo ngắn về chat COO (REPORT_ID + đã chuyển cho phòng nào / đã làm gì). Dòng nào đã chuyển lời ở lần quét trước thì không chuyển lại. Dòng của chi nhánh khác (C là email khác) hoặc C trống thì bỏ qua. COO chỉ đọc và chuyển lời/thực hiện theo phản hồi, không ghi gì vào CEO_REPORTS.

Bước 7 — Kiểm tra video đủ 3 lần trả quá hạn (quyết CEO 08/11/2026, DEC-154; chủ sở hữu bước ghi CEO_REPORTS: coo-scan, R6-14): mỗi ca quét 03:00, đọc QA_LOG + TASKS: video nào có 3 dòng RETURNED trong QA_LOG mà ngày lần trả thứ 3 (QA_LOG DATE) là ngày trước hôm nay, và COO chưa có quyết định (TASKS.C chưa BLOCKED/CANCELLED, TASKS.M chưa có "(a) đã dùng", nhật ký ngày chưa ghi quyết định của COO cho video đó) thì COO ghi 1 dòng vào tab CEO_REPORTS theo mục DEC-111 (REPORT_ID dạng RPT-YYYYMMDD-{{EMAIL_KHAI_BAO}}-NN, đủ A–F). Cách tính "quá 24h": tính theo ngày — lần trả thứ 3 vào ngày trước hôm nay mà tới ca quét 03:00 hôm nay COO vẫn chưa quyết thì tính là quá hạn (QA_LOG/TASKS chỉ có ngày, không có giờ — R6-12, không đổi schema). Ghi vào báo cáo ca quét (chat COO) danh sách video đã kiểm + video nào đã ghi CEO_REPORTS.

Bước 8 — Kiểm tra mốc leo thang lô cũ và dòng vô chủ (quyết CEO 11/11/2026): đọc báo cáo ca Pipeline của buổi sáng hôm nay và hôm qua (báo cáo gửi về chính chat COO này; đối chiếu thêm nhật ký ngày của tài khoản này nếu cần). Mục nào thuộc diện lô cũ qua đêm (DEC-117) hoặc dòng TASKS vô chủ/sai ASSIGNEE đã xuất hiện trong báo cáo của cả 2 buổi sáng liên tiếp mà vẫn chưa có quyết định của COO (giữ/bỏ, hoặc xác định được chủ) thì COO ghi 1 dòng vào tab CEO_REPORTS theo DEC-111 (REPORT_ID dạng RPT-YYYYMMDD-{{EMAIL_KHAI_BAO}}-NN, đủ A–F) ngay trong ca này, và ghi vào báo cáo ca quét mục đã leo thang.

Quy tắc khác: CEO giao sau 03:00 được đọc vào 03:00 hôm sau. Ngoài lệnh trực tiếp của COO, COO không tự quét thêm lần nào trong ngày. Gặp 429/403 thì dừng, ghi blocker, không thử lại.
