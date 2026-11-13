# SOP 2 bot tự động — công ty truyền thông một người

Nguồn: 6 lịch cron công ty đang chạy (coo-scan 03:00 + Scout 04:00 + Pipeline 05:00 + Scout 13:00 + Pipeline 14:00 + hoc-hoi 20:00) (CEO ủy quyền chế độ bot tự động hoàn toàn:
bot chạy KHÔNG cần hỏi CEO trước, không cần chờ phê duyệt cho các bước
trong phạm vi dưới đây; bước nào vượt phạm vi thì dừng nhánh đó lại và
ghi blocker, không tự mở rộng phạm vi). Cùng tài khoản thì dùng tiếp 6
lịch + workbook + chat hiện có; khác tài khoản thì tạo lại đúng nhịp và
nội dung dưới đây, thay ID workbook/chat bằng ID mới. Cron là cấu hình
của tài khoản; bản mẫu nằm trong repo tại company-os/crons/ (xem company-os/scheduled-tasks-setup.md — nơi duy nhất liệt kê bộ lịch) — chỉ cài khi CEO duyệt. bot-hoc-hoi chạy hằng ngày 20:00
Asia/Saigon (quyết CEO 07/11/2026, R4-14 phương án A, DEC-019; cron
bot-hoc-hoi-2000) — xem mục bot-hoc-hoi cuối file.

Workbook: "Video HQ — Tin Tức" (spreadsheetId
`1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`; cùng tài khoản: dùng tiếp
workbook đang chạy, không tạo mới, không ghi đè; khác tài khoản: tạo mới
từ `company-os/google-sheet-spec.md` — đủ 8 tab: TOPICS, TASKS, QA_LOG,
DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN, SHIFT_CHECKIN). Đọc/ghi Sheet bằng connector Google Sheets.
Không sửa MEMORY.md trong ca bot; quan sát ghi vào nhật ký ngày.
Pipeline thuộc lịch bot đã được CEO duyệt (kênh giao việc số 2 trong 3
kênh duy nhất — xem BOOTSTRAP §8), không phải kênh riêng ngoài 3 kênh
đó.

## SCOUT — ca 04:00 và 13:00 hàng ngày

Vai trò: Scout tự động (2 phòng: Scout-Báo + Scout-Group, mỗi phòng tự chấm chủ đề của mình trong cùng lượt quét — chat Scoring đã đóng ngày 07/11/2026, quyết định C3). Skill: media-scout. Tối đa 15 lượt tìm kiếm/ca, tối đa 10 chủ đề mới/ca.

0. Cửa chặn hạn mức tuần (quyết CEO 13/11/2026, DEC-263 — thay DEC-202): đầu ca chạy lệnh subscription-status status, đọc % tuần đã dùng trực tiếp trong dòng 'Usage: N% of ... weekly limit' — nếu N ≥ 95% thì dừng hẳn ca này: không quét, không chấm, không ghi chủ đề, không báo cáo ca. Khi hạn mức tuần được reset thì số trực tiếp tự hạ, hoạt động trở lại bình thường, không cần lệnh mở lại. Token thêm là khoản dự phòng cho việc khác, không dùng để sản xuất video. Nếu lệnh không đọc được N thì dùng số Sheet dự phòng theo chuỗi duy nhất DEC-263 (N4-A 13/11/2026): dòng COO_CHECKIN mới nhất của chính chi nhánh (mới nhất = DATE lớn nhất, hòa thì hàng cuối cùng; ASSIGNEE_EMAIL = email khai báo của mình), rồi TASKS.L QUOTA của dòng DELIVERED có D = email khai báo của mình và L không trống; nếu cả hai đều không đọc được thì ghi "không đọc được" vào báo cáo ca và vẫn quét tiếp. Số Sheet chỉ là dự phòng khi lệnh lỗi; khi lệnh đọc được, số trực tiếp là chuẩn duy nhất.

1. Đọc skill Scout và áp dụng đúng luật quét của nó (skill media-scout nay đã gộp chấm điểm).
2. "Lang thang" trên nguồn CÔNG KHAI: browser.search (vertical news cho
   tin Việt Nam) và social.search (xu hướng công khai, ranking
   engagement, tin trong 72 giờ). Chỉ dùng nguồn công khai, không đăng
   nhập, không nhắn tin, không bình luận, không đăng bài, không tham
   gia group.
3. Quét group công khai và page nhiều tương tác (CHỈ group công khai và
   page nhiều tương tác, KHÔNG quét các group tài khoản đã tham gia):
   tín hiệu chính từ social.search (bài công khai nhiều tương tác trên
   Facebook/Instagram/Threads, gồm fanpage lớn) và browser.search
   (vertical news) để đối chiếu. Với mỗi ứng viên, kiểm tra thêm bằng
   facebook-cli groups search theo từ khóa (kết quả thường mỏng — không
   có thì thôi, không ép); nếu có group công khai liên quan thì đọc
   groups posts --sort-by MOST_REACTS của group đó. Nếu facebook-cli
   chưa liên kết thì bỏ qua bước kiểm tra group. CHỈ ĐỌC: không đăng,
   không bình luận, không nhắn tin, không tham gia group, không kết bạn.
4. Phân tích đáng làm TRƯỚC KHI GHI: tương tác cao chưa đủ. Một chủ đề
   chỉ được ghi khi đồng thời: (1) tương tác cao thật, có số liệu cụ
   thể; (2) có góc kể rõ sau 2 câu tóm tắt; (3) kiểm chứng được bằng
   nguồn tin cậy; (4) dựng được video trong 1 ngày bằng công cụ hiện
   có; (5) có phương án minh họa an toàn. Thiếu một trong năm thì BỎ
   QUA, không ghi. KHÔNG ghi: tin giả dù lan truyền mạnh, drama cá
   nhân, gossip đời tư, nội dung cổ vũ bạo lực/phạm pháp, nội dung chỉ
   là quảng cáo/fan content không có câu chuyện, nội dung chỉ hút tương
   tác bằng giật gân mà không có thông tin.
5. Khử trùng: đọc TOPICS, TASKS và QA_LOG theo TIÊU ĐỀ/SỰ KIỆN (chủ đề chưa duyệt chưa có ID nên không khử trùng theo TOPIC_ID được; chủ đề đã có ID thì đối chiếu thêm theo ID). Trùng là cùng sự kiện/người/số liệu/câu chuyện dù wording khác, kể cả chủ đề đã làm trong 90 ngày với cùng góc. Chủ đề trùng thì ghi STATUS = DUPLICATE + tiêu đề (và ID nếu có) của chủ đề gốc vào NOTES, không tự ghi APPROVED. Đầu ca kiểm tra toàn vẹn (R7) trước khi ghi: chỉ đọc số dòng + ID lớn nhất (chỉ tính dòng đã có ID) để nắm trạng thái hiện tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất lùi KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026: làm việc bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab BASELINE hay file baseline.json. ID trống là bình thường, không phải lỗi.
6. Ghi chủ đề mới vào TOPICS đã chấm xong trong một lần ghi, đúng thứ tự cột: TOPIC_ID ĐỂ TRỐNG (Scout không tự sinh ID — quyết CEO 07/11/2026, phương án E cho R4-04; chỉ CEO nhập TOPIC_ID khi duyệt/lật READY, bằng công cụ riêng bên ngoài, đảm bảo không trùng; chủ đề không duyệt thì tiếp tục bỏ trống), TITLE, SOURCE (tên nguồn + link nếu có), DISCOVERED (ngày hôm nay, dạng YYYY-MM-DD), HOT / AUDIENCE / FRESH / FEASIBLE / SOURCED (điểm theo thang 30+20+20+15+15=100), TOTAL, STATUS theo thang và cửa quan tâm (quan tâm (HOT + AUDIENCE) ≥ 30/50 xét TRƯỚC tổng, tổng ≥70 → APPROVED; 50–69 → HOLD; ≥70 nhưng quan tâm <30 → HOLD + tín hiệu chờ vào NOTES; <50 → REJECTED; trùng → DUPLICATE + tiêu đề (và ID nếu có) của chủ đề gốc vào NOTES), ANGLE (góc kể + vì sao thú vị, 2 câu), NOTES ("Bot lang thang tự động" + số liệu bằng chứng cho điểm quan tâm; "Nghi trùng <tiêu đề hoặc TOPIC-xxx nếu có ID>" nếu có). Điểm và TOTAL chỉ là THAM KHẢO cho quyết định của CEO — điểm không chặn sản xuất; chỉ READY mới quyết định sản xuất. Đọc lại tab sau khi ghi để xác nhận số dòng đã tăng đúng (R3 — đọc lại theo tiêu đề ngay trước khi ghi).
7. Không có bàn giao Scoring: chat Scoring đã đóng (C3); chủ đề APPROVED chờ CEO flip READY (TOPICS.K APPROVED → READY) và CEO tự nhập TOPIC_ID khi flip (bằng công cụ riêng bên ngoài, đảm bảo không trùng).

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không sửa Drive, không bịa nguồn/link/điểm/ngày,
không ghi đè hay xóa dòng đã có. Gặp 429/403/rate-limit thì dừng tìm
kiếm của ca ngay, không thử lại cùng truy vấn trong ca.

Báo cáo: LUÔN nhắn về chat COO cuối mỗi ca (kể cả ca trống): (a) có chủ đề mới được ghi (kèm tiêu đề + điểm + STATUS; TOPIC_ID nếu đã có), hoặc (b) có blocker MỚI (tìm kiếm bị chặn hoàn toàn, ghi Sheet thất bại). Ca trống (không có chủ đề mới, không có blocker mới) thì báo 1 dòng ngắn 'ca X: không có chủ đề mới' — KHÔNG im lặng. Ca 06:00 báo cáo NGAY lúc 06:00 (ngoại lệ khung proactivity 06:30–21:30 — quyết CEO 07/11/2026, R4-15 phương án A, DEC-020: COO cần biết kết quả ca đầu ngày trước khi ra quyết định).

## PIPELINE — ca 05:00 và 14:00 hàng ngày

Vai trò: điều phối pipeline (một ca của lịch bot đã được CEO duyệt). Chat nhân viên: Sản xuất, Kỹ thuật QA. Gửi nhiệm vụ bằng chat.send_message; nếu công cụ nhắn chat không có trong ca này thì chỉ ghi dòng CLAIMED vào TASKS và ghi rõ vào kết quả ca để main agent chuyển tiếp, không coi là lỗi ca.

A. Giao Sản xuất — cổng READY + NHẬN THEO LÔ tối đa 3/ca (lệnh CEO 07/11/2026, thay thế luật tuần tự + R4-03; bỏ trần đếm theo R4-02 ngày 07/11/2026): đọc TOPICS và TASKS. Chỉ giao chủ đề đồng thời thỏa đủ cả 3 điều kiện: TOPICS.STATUS = READY VÀ TOPIC_ID đã có (không trống) VÀ chưa có dòng TASKS nào cho TOPIC_ID đó. TASKS là nguồn duy nhất (quyết CEO 07/11/2026, R4-11 phương án B): không kiểm tra thư mục projects hay tiến trình máy — video đang làm/chờ QA đều thể hiện bằng dòng TASKS (CLAIMED/BUILDING/REVIEW/RETURNED, trong đó REVIEW là chờ QA). Hạn chế đã chấp nhận: TASKS không thấy trạng thái render/TTS trên máy nếu project chưa ghi TASKS. Chủ đề APPROVED nhưng STATUS chưa phải READY thì KHÔNG giao, không tạo video từ chủ đề đó. Chủ đề READY mà TOPIC_ID trống thì BỎ QUA (không claim được vì TASKS cần TOPIC_ID), ghi vào báo cáo ca để COO báo cáo CEO qua CEO_REPORTS nhập ID. Điểm và TOTAL chỉ là tham khảo cho quyết định của CEO — điểm không chặn sản xuất; chỉ READY mới quyết định sản xuất. Không giới hạn số video ĐÃ BÀN GIAO/ca hay /ngày (chỉ trần đếm 5 video đã bàn giao/ca mới bãi bỏ theo R4-02 — TASKS.J chỉ có ngày nên không đếm được theo ca; trần NHẬN tối đa 3 chủ đề READY/ca vẫn còn); NHẬN THEO LÔ: mỗi ca NHẬN 1 LẦN tối đa 3 chủ đề READY theo thứ tự Sheet, đánh dấu ngay bằng dòng TASKS CLAIMED (ASSIGNEE = email khai báo của chi nhánh mình) để các chi nhánh khác biết đã có người làm; sau đó lần lượt tạo 3 video (sản xuất tuần tự từng video một qua Production → QA → bàn giao Drive), không sản xuất song song. Luật đổi trần không hồi tố (quyết CEO 08/11/2026, DEC-116, R5-11 phương án A): trần 4 (DEC-102, có hiệu lực 11:18 08/11) chỉ áp cho ca claim sau thời điểm đó; lô 10:00 ngày 08/11 đã claim 5 (TOPIC-273/277/278/279/283) hợp lệ theo trần 5 còn hiệu lực lúc claim, giữ nguyên cả 5, không nhả. Mỗi ca nhận đủ 3 chủ đề READY mới, không trừ số video đang làm dở trong ngày (quyết CEO 08/11/2026, T3 phương án B); tổng số video đang làm cùng lúc có thể vượt 3. Ngoại lệ (quyết CEO 08/11/2026, DEC-156 phương án B; sửa theo quyết CEO 13/11/2026, DEC-263 — thay DEC-201): đầu ca chạy lệnh subscription-status status, đọc % tuần đã dùng trực tiếp trong dòng 'Usage: N% of ... weekly limit' (nguồn chuẩn duy nhất cho cửa chặn) — nếu N ≥ 95% thì claim 0 chủ đề READY mới trong ca đó (chặn tạo video mới, không cần báo cáo riêng việc claim 0; báo cáo ca vẫn làm bình thường cho video đang dở), chỉ để video đang làm dở hoàn thành; token thêm là khoản dự phòng cho việc khác, không dùng để sản xuất video; nếu lệnh không đọc được thì dùng số Sheet dự phòng (dòng điểm danh COO_CHECKIN mới nhất của chính chi nhánh, rồi TASKS.L QUOTA); nếu cả hai đều không đọc được thì ghi "không đọc được" vào báo cáo ca và vẫn đi tiếp. Cửa chặn này áp dụng toàn công ty (quyết CEO 09/11/2026, DEC-202): Scout cũng dừng quét/chấm/ghi chủ đề khi token tuần trên 95% (ca dừng hẳn, không báo cáo ca); khi hạn mức tuần được reset thì công ty hoạt động trở lại bình thường, không cần lệnh mở lại. Video đang làm dở từ NGÀY CŨ thì bỏ qua theo quy tắc ngày hiện tại — ngoại trừ bước cứu lô cũ dưới đây. Cứu lô cũ qua đêm (quyết CEO 08/11/2026, DEC-117 phương án A): chỉ ca 05:00 mới làm — pipeline liệt kê các dòng TASKS của chi nhánh mình ở CLAIMED / BUILDING / REVIEW / RETURNED / BLOCKED / APPROVED mà TASKS.J là ngày trước ngày hôm nay, nhắn COO quyết giữ/bỏ từng video trong ca đó; giữ → phòng liên quan tiếp tục video, cập nhật J sang ngày hôm nay khi chạm vào; bỏ → COO ghi CANCELLED + lý do vào M BLOCKER; chưa quyết thì liệt kê lại ở ca 05:00 hôm sau. Không còn cơ chế nhận tiếp theo sự kiện QA báo DELIVERED — việc nhận chủ đề chỉ xảy ra 1 lần đầu ca, theo lô; khi một video trong lô DELIVERED thì Production TỰ LẤY video kế tiếp trong lô (lệnh CEO 07/11/2026, DEC-032 — không chờ pipeline giao lại; chỉ lấy chủ đề đã CLAIMED trong cùng lô, ASSIGNEE = email khai báo của mình, UPDATED_AT = ngày hôm nay; video trước BLOCKED (lỗi riêng video, nhóm 1) thì lấy video CLAIMED kế tiếp chưa tắc trong cùng lô (ngoại lệ DEC-032, quyết CEO 08/11/2026, DEC-104 phương án A); video trước BLOCKED (lỗi hệ thống, nhóm 2, hoặc chưa rõ lý do) thì dừng chờ COO gỡ tắc; video đầu tiên của lô vẫn do pipeline giao), hết lô thì chờ ca sau nhận lô mới. Đầu ca kiểm tra: ghi nhận video đang làm của mình TRONG NGÀY (CLAIMED/BUILDING/REVIEW/RETURNED, ASSIGNEE = email khai báo của tài khoản, UPDATED_AT là ngày hôm nay) để báo cáo ca; số video đang làm dở KHÔNG trừ vào số chủ đề mới được nhận — mỗi ca nhận đủ 3 chủ đề READY mới; video đang làm của chi nhánh khác (ASSIGNEE là email khác) hoặc ASSIGNEE trống thì KHÔNG phải của mình — bỏ qua, ghi các dòng đó (TOPIC_ID + STATUS + ASSIGNEE) vào báo cáo ca để COO xác định chủ; video BLOCKED mà TASKS.D ASSIGNEE = email khai báo của tài khoản của chi nhánh mình VÀ TASKS.J UPDATED_AT là ngày hôm nay thì pipeline đọc M BLOCKER và phân loại (quyết CEO 08/11/2026, DEC-104 phương án A): lỗi riêng video (nhóm 1) thì KHÔNG dừng hàng đợi — Production lấy video CLAIMED kế tiếp chưa tắc trong cùng lô, video BLOCKED nằm lại chờ COO; lỗi hệ thống (nhóm 2) hoặc M trống/mơ hồ thì dừng hàng đợi cho đến khi COO gỡ tắc hoặc hủy (CANCELLED); 2 video BLOCKED trở lên cùng mã lý do (DEC-158) trong ngày thì dừng (nghi lỗi hệ thống trá hình); Kiểm tra BUILDING cũ mỗi ca (quyết CEO 08/11/2026, DEC-105 phương án A): pipeline đọc giờ vào BUILDING trong K PROD_NOTES; video vẫn BUILDING qua 2 lần đầu ca liên tiếp mà không có ghi chú K mới thì hỏi Production (bước hiện tại + lỗi + cần gì); Production trả lời trong 1 ca, lỗi nhóm 1 thì ghi BLOCKED rồi lấy video kế tiếp trong lô, lỗi hệ thống thì dừng; không trả lời tới đầu ca sau thì COO giao lại (kiểm tra trước, tiếp tục từ điểm dừng trong K theo luật resume; chỉ xét dòng TASKS.J là ngày hôm nay, video ngày cũ chỉ xử lý ở ca 05:00 theo DEC-117). Kiểm tra REVIEW cũ mỗi ca (quyết CEO 08/11/2026, DEC-106 phương án A): pipeline đọc giờ nộp REVIEW trong K PROD_NOTES; video vẫn REVIEW qua 1 ca (05:00→14:00 là 9 giờ; 14:00→05:00 hôm sau là 15 giờ) mà không có verdict trong QA_LOG thì hỏi QA (đang chấm tới đâu, verdict khi nào); QA trả lời trong 1 ca; Production được bắt đầu video kế tiếp trong lô trong lúc chờ verdict (nới DEC-032, vẫn chỉ làm 1 video tại một thời điểm); QA không trả lời tới đầu ca sau thì COO giao lại cho QA (ID video + DRAFT_LINK; chỉ xét dòng TASKS.J là ngày hôm nay, video ngày cũ chỉ xử lý ở ca 05:00 theo DEC-117). Vòng lặp RETURNED (quyết CEO 08/11/2026, DEC-107 phương án A): đủ 2 lần trả thì leo thang 1 lần về chat COO; các lần trả thêm sau đó thì leo thang LẠI mỗi khi số lần trả tăng (QA nhắn lúc verdict + pipeline kiểm tra đầu ca, cùng số lần trả thì không nhắn lại); sau lần trả thứ 3 Production dừng sửa, báo COO quyết trước 03:00 hôm sau (sửa tiếp 1 lần với cách khác — chỉ 1 lần (a) duy nhất, bị trả lần 4 thì chỉ còn BLOCKED nhóm 1 hoặc hủy; quá hạn thì pipeline ghi vào báo cáo ca ‘COO chưa quyết — cần CEO quyết’ và COO ghi CEO_REPORTS khi quá 24h) (DEC-154); QA ghi rõ lỗi lặp lại thì Production phải đổi cách sửa. Video đã duyệt chưa upload (quyết CEO 08/11/2026, DEC-108 phương án A): pipeline đầu ca kiểm tra TASKS.C=APPROVED hoặc QA_LOG APPROVED mà TASKS chưa DELIVERED rồi nhắn QA upload ngay (mở rộng theo DEC-155, R5-37 phương án A: kiểm cả dòng TASKS đang BUILDING/REVIEW mà QA_LOG đã có APPROVED do ghi TASKS lỗi giữa chừng; trước khi nhắn upload, đối chiếu md5 đã duyệt với DRAFT_LINK hiện tại — nếu khác version thì không nhắn upload mà báo COO, tránh upload nhầm version cũ chưa xong) + ghi vào báo cáo ca; QA báo ngay mọi lỗi upload (không chỉ hết hạn thẻ); quá 1 ca chưa upload xong thì pipeline nhắn COO giao lại cho QA; quá 2 lần giao lại mà vẫn chưa upload được thì COO ghi TASKS.C = BLOCKED (nhóm 2) + lý do vào M BLOCKER và ghi CEO_REPORTS, pipeline không nhắn QA nữa (DEC-153). Rảnh mà còn việc (quyết CEO 08/11/2026, DEC-109 phương án A): pipeline đầu ca kiểm tra không có video nào BUILDING/REVIEW/RETURNED mà còn dòng CLAIMED thì nhắn Production lấy video CLAIMED đầu tiên theo thứ tự Sheet làm tiếp + ghi vào báo cáo ca; Production xác nhận trong 1 ca; tới đầu ca sau vẫn chưa BUILDING thì pipeline nhắn COO giao lại cho Production. Đọc phản hồi CEO trên CEO_REPORTS (quyết CEO 08/11/2026, DEC-112 phương án A; bổ sung lệnh CEO 08/11/2026): pipeline đầu ca đọc các dòng của chi nhánh mình có G CEO_REPLY không trống VÀ H APPLIED_BY + I DATE đều trống (lệnh chưa thực hiện — dòng đã có APPLIED_BY hoặc DATE thì đã có phòng khác đọc/thực thi, bỏ qua, không chuyển lại), chuyển lời tới phòng liên quan kèm REPORT_ID + nội dung phản hồi, ghi vào báo cáo ca; dòng đã chuyển lời ở ca trước thì không chuyển lại; chỉ đọc và chuyển lời, không ghi gì vào CEO_REPORTS. video BLOCKED từ NGÀY CŨ (UPDATED_AT không phải ngày hôm nay) thì bỏ qua theo quy tắc ngày hiện tại — không dừng hàng đợi, ghi vào báo cáo ca để COO xác định chủ/xử lý; video BLOCKED của chi nhánh khác (ASSIGNEE là email khác) hoặc ASSIGNEE trống thì KHÔNG dừng hàng đợi — nhận chủ đề READY khác như bình thường, ghi các dòng đó vào báo cáo ca để COO xác định chủ; COO chỉ gỡ tắc/hủy dòng BLOCKED của chi nhánh mình. Chọn tối đa 3 chủ đề READY ĐÃ CÓ TOPIC_ID theo thứ tự Sheet. Chủ đề READY mà TOPIC_ID trống thì bỏ qua, ghi vào báo cáo ca để COO báo cáo CEO qua CEO_REPORTS nhập ID. Ghi từng dòng TASKS CLAIMED (ASSIGNEE = email khai báo của tài khoản) rồi đọc lại theo ID (R3 claim-then-verify từng chủ đề): nếu có 2 dòng CLAIMED cùng TOPIC_ID thì chủ đề đó dừng ngay, ghi Blocker vào TASKS.N DUP_NOTE, báo lại chat COO (các chủ đề còn lại trong lô vẫn làm tiếp). Đua nhận chủ đề giữa các chi nhánh khi các ca 05:00/14:00 chạy đồng thời là tình huống đã được thiết kế chấp nhận (quyết CEO 11/11/2026): claim-then-verify + kiểm tra trùng ngay sau khi ghi bắt được va chạm trước khi giao sản xuất, nên không cần khóa cứng hay lệch giờ chạy. Gửi tin nhắn cho chat Sản xuất cho video ĐẦU TIÊN trong lô (các video sau trong lô Production TỰ LẤY khi video trước DELIVERED theo lệnh CEO 07/11/2026, DEC-032 — pipeline không giao lần lượt nữa; video trước BLOCKED (lỗi riêng video, nhóm 1) thì lấy video CLAIMED kế tiếp chưa tắc trong cùng lô (ngoại lệ DEC-032, quyết CEO 08/11/2026, DEC-104 phương án A); video trước BLOCKED (lỗi hệ thống, nhóm 2, hoặc chưa rõ lý do) thì dừng chờ COO gỡ tắc), trong đó có đủ: tiêu đề, góc làm, lưu ý pháp lý nếu có (ví dụ phiên tòa đang diễn ra thì ghi rõ "theo cáo trạng / theo lời khai tại tòa", không kết luận tội danh), và nhắc luật: kịch bản giọng người viết; thời lượng do Sản xuất tự quyết (đề xuất 2–3 phút, dài hơn vẫn được khi nội dung đã kiểm chứng, không cắt kịch bản đã kiểm chứng chỉ để vừa chuẩn cũ, không xin ngoại lệ); tìm media theo luật phân nhánh hiện hành (kịch bản Việt Nam: ảnh chỉ từ nguồn gốc, không dùng Wikipedia/Stock cho ảnh; video từ Wikipedia/Stock được dùng nếu qua cửa bối cảnh cứng; kịch bản nước ngoài: Wikipedia + Stock + nguồn chung; mọi media cho kịch bản Việt Nam qua cửa bối cảnh cứng; ưu tiên ảnh/video thực tế của đúng sự kiện trước minh họa chung chung); tự động hóa không tab duyệt thủ công. Không giao chủ đề DUPLICATE, không giao chủ đề đã có dòng TASKS. Nếu ca này không có chủ đề nào thỏa đủ cả 3 điều kiện thì KHÔNG giao gì, KHÔNG tạo video, mà gửi báo cáo về chat COO nêu rõ "chưa có chủ đề READY đang chờ" rồi kết thúc bước A. C/J/D nhiều người viết — ghi sau thắng + để lại lý do (quyết CEO 07/11/2026, R4-10 phương án C): TASKS.C STATUS có 3 người viết (Production: CLAIMED/BUILDING/REVIEW/BLOCKED — chỉ lỗi riêng video nhóm 1, lý do bắt buộc vào M; QA: RETURNED/APPROVED/DELIVERED; COO: BLOCKED/CANCELLED — chỉ COO được gỡ BLOCKED hoặc hủy), TASKS.J UPDATED_AT có 2 người viết (Production, QA), TASKS.D ASSIGNEE có 2 người viết (Production lúc claim, COO lúc giao qua COO_TASKS) — chấp nhận ghi sau thắng khi xung đột (lần ghi sau thắng, không có quy tắc ai thắng theo vai trò); ai ghi TASKS.C thì trong cùng lần ghi phải ghi thêm lý do + thời gian vào cột ghi chú của mình (Production→K PROD_NOTES (và M BLOCKER khi ghi BLOCKED), QA→QA_LOG cột E ISSUES + TASKS.F QA_VERDICT, COO→M BLOCKER, Pipeline→lý do nhận lô ghi vào báo cáo ca, trùng CLAIMED ghi N DUP_NOTE).

Ghi chú về timeout_secs (quyết CEO 08/11/2026, DEC-159, R5-41): timeout_secs: 7200 trong 4 file cron pipeline là ngân sách thời gian chạy yêu cầu cho phiên pipeline (các bước kiểm tra đầu ca + giao việc + báo cáo của chính phiên đó), không phải cửa sổ ca 4 giờ và không cắt công việc của Production/QA — các phòng làm việc ở chat riêng theo DEC-032 nên không bị timeout của phiên pipeline cắt; runtime còn nâng ngân sách tối thiểu theo chu kỳ chạy của lịch, nên con số 7200 không phải điểm cắt cứng đúng ở 2 giờ. Video BUILDING kẹt được DEC-105 xử lý (pipeline hỏi Production khi video qua 2 lần đầu ca không có ghi chú K mới; không trả lời tới đầu ca sau thì COO giao lại); DEC-109 giữ nguyên, không nới.

Kiểm tra TTS đầu ca (quyết CEO 11/11/2026): pipeline gọi health của server TTS (cổng 8000) trước khi nhận lô; không đạt thì thử khởi động lại server một lần (chạy nền theo hướng dẫn trong vieneu-tts/, chờ model nạp rồi kiểm tra lại); vẫn không đạt thì báo cáo ca ghi rõ 'TTS chưa sẵn sàng' và không nhận lô trong ca đó — tránh nhận lô rồi tắc giữa chừng như lỗi hệ thống nhóm 2.

B. Bàn giao Drive: đọc QA_LOG và TASKS. Thư mục bàn giao đã được CEO xác nhận là thư mục Drive "Video Muse" (quyền anyone with link đã được CEO cấp; tìm bằng Drive files list với q name = 'Video Muse', không tự đoán ID). Quy định mới 29/10/2026 (lệnh CEO): QA tải lên NGAY trong lượt duyệt, nên bước B này chỉ là lưới bắt sót — chỉ khi có verdict APPROVED đã qua mà TASKS vẫn chưa DELIVERED (thiếu H DRIVE_LINK hoặc I MD5) thì mới nhắn chat QA tải file đã duyệt lên đúng thư mục Video Muse đó và ghi link thật vào TASKS (H DRIVE_LINK + I MD5, STATUS = DELIVERED); khi ghi link, ghi luôn vào TASKS.L QUOTA đủ email người sản xuất theo quy tắc thống nhất và hạn mức lúc upload do QA tự đọc lại tại thời điểm upload, bằng chữ, không chụp màn hình. Tuyệt đối không bịa link, không tự tạo thư mục khác, không tự thay đổi quyền thư mục (thư mục "Video Muse" đã được CEO cấp quyền anyone with link ngày 05/11/2026).

C. Leo thang (quyết CEO 08/11/2026, DEC-107 phương án A): nếu một video có từ 2 lần QA Trả lại trong QA_LOG (đếm RESULT = RETURNED theo VIDEO_ID) mà chưa có verdict Duyệt sau đó thì nhắn về chat COO: lần đầu (đủ 2 lần trả) nhắn 1 lần; các lần trả thêm sau đó (lần 3, 4…) thì nhắn LẠI mỗi khi số lần trả tăng (QA nhắn lúc verdict + pipeline kiểm tra đầu ca, cùng số lần trả thì không nhắn lại). Trạng thái đã leo thang của mỗi video ghi bằng mốc ESC trong TASKS.N của chính dòng video (dạng 'ESC:<số lần trả>:<ngày>', ghi nối thêm, không ghi đè nội dung DUP_NOTE — quyết CEO 11/11/2026): chưa có mốc ESC là chưa từng leo thang; nhắn lại chỉ khi số lần trả tăng so với mốc ESC gần nhất, và mỗi lần nhắn đều ghi mốc ESC mới (nhật ký ngày vẫn ghi để người đọc nhưng không còn là căn cứ quyết định). Sau lần trả thứ 3 Production dừng sửa, báo COO quyết trước 03:00 hôm sau (sửa tiếp 1 lần với cách khác — chỉ 1 lần (a) duy nhất, bị trả lần 4 thì chỉ còn BLOCKED nhóm 1 hoặc hủy; quá hạn thì pipeline ghi vào báo cáo ca ‘COO chưa quyết — cần CEO quyết’ và COO ghi CEO_REPORTS khi quá 24h) (DEC-154). Chủ sở hữu bước ghi CEO_REPORTS quá hạn là coo-scan Bước 7 (R6-14). QA ghi rõ lỗi lặp lại ("lỗi lặp lại") vào QA_LOG.E + tin nhắn; Production phải đổi cách sửa khi lỗi lặp lại.

D. Nếu gặp 429/403/rate-limit thì dừng
nhánh đó, ghi blocker vào nhật ký ngày, không chờ, không thử lại ẩu. Riêng thẻ phê duyệt upload Drive hết hạn sau 30 phút (approval_expired / Timed out) thì KHÔNG dừng hẳn: **Thẻ phê duyệt upload Drive hết hạn sau 30 phút (lệnh CEO 05/11/2026, tiền lệ TOPIC-232):** lệnh upload lên Drive hiện thẻ phê duyệt, chỉ cho 30 phút để bấm; hết 30 phút không có quyết định thì thẻ tự hết hạn (approval_expired / Timed out), thao tác không chạy, file không lên Drive. Tiền lệ: thẻ gửi 10:52:57 +07, hết hạn 11:22:57 +07, Timed out 11:23:02 +07 — không phải bị từ chối, không phải file hỏng hay thư mục sai quyền. Cách xử lý đúng là **chạy lại upload một lần để hệ thống cấp thẻ mới** (không tính là "thử lại ẩu"); cấp phép toàn quyền của CEO cho QA hoàn tất bàn giao mà không hỏi lại trong chat **không tắt được thẻ hệ thống** — thẻ vẫn hiện mỗi lần upload, cần bấm trong 30 phút; upload Drive không có standing Allow. **Khi gặp thẻ hết hạn, QA phải báo ngay cho COO; COO ghi lại thông báo tình trạng vào cột G "Kết quả hoàn thành" của dòng COO_TASKS tương ứng (ghi tạm thời trong khi nhiệm vụ vẫn ở "Đang làm", cột F thời gian hoàn thành vẫn để trống), để CEO đọc tab COO_TASKS là biết vấn đề ở đâu, không phải chờ tới khi xong mới biết. Khi nhiệm vụ hoàn thành sau đó, COO cập nhật lại cột G bằng kết quả cuối cùng kèm link. Quy tắc này khác với 429/403/rate-limit: gặp 429/403 thì dừng nhánh, ghi blocker, không thử lại.**

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không bịa link/số liệu, không ghi đè hay xóa dòng đã
có, không sửa MEMORY.md.

Báo cáo: nhắn về chat COO khi có nhiệm vụ sản xuất mới được giao, có
leo thang mới, có blocker MỚI, HOẶC khi ca này không có chủ đề nào READY
đang chờ (báo cáo "chưa có chủ đề READY" và bỏ qua tạo video). Ca không thuộc các trường hợp trên thì im lặng, kết quả chỉ lưu trong lịch sử ca.

## COO-SCAN — hằng ngày 03:00

Vai trò: COO điểm danh tại tab COO_CHECKIN (Bước 0, lệnh CEO 09/11/2026) rồi quét tab COO_TASKS 1 lần/ngày lúc 03:00 +07 đầu ca (cron coo-scan-0300, quyết CEO 08/11/2026, DEC-099). Đọc tab COO_TASKS, chỉ nhận dòng có cột B = email khai báo của chi nhánh mình và cột E chưa "Hoàn thành": ghi ID COO-YYYYMMDD-NN vào A, chuyển E sang "Đang làm", tự phân việc ở D, giao cho phòng qua chat, rồi xác nhận hoàn thành trên cùng dòng (E = Hoàn thành, F thời gian hoàn thành, G kết quả). Không có dòng thì im lặng. Việc lô cũ/dòng vô chủ do Pipeline báo cáo: nếu một mục đã xuất hiện trong báo cáo ca của 2 buổi sáng liên tiếp mà chưa có quyết định (giữ/bỏ, hoặc xác định chủ) thì COO ghi 1 dòng CEO_REPORTS xin CEO quyết ngay trong ca quét này (mốc leo thang theo quyết CEO 11/11/2026, cùng họ DEC-111). Đọc thêm CEO_REPORTS (Bước 6 trong body cron coo-scan-0300) theo DEC-112 (phản hồi CEO mới từ 03:00 hôm qua tới nay, chuyển lời cho phòng liên quan hoặc tự thực hiện theo phản hồi). Chi tiết đầy đủ: xem BOOTSTRAP §3.3 và spec mục COO_TASKS (cùng skill media-coo).

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền, không push GitHub, không sửa MEMORY.md. Gặp 429/403/rate-limit thì dừng nhánh đó, ghi blocker, không thử lại ẩu.

## bot-hoc-hoi — hằng ngày 20:00

Tần suất: mỗi ngày 20:00 Asia/Saigon (quyết CEO 07/11/2026, R4-14
phương án A, DEC-019). Cron bot-hoc-hoi-2000 đã tạo 07/11/2026, đang
chạy (Q6 đã đóng).

Vai trò: (1) kiểm mẫu — biện pháp bù (c) cho quyết C3 (gộp Scout +
Scoring: mất lớp kiểm độc lập "không chấm chủ đề do mình quét", bù bằng
(a) điểm quan tâm bắt buộc có số liệu bằng chứng trong NOTES, (b) cổng
READY của CEO, (c) hoc-hoi kiểm mẫu); (2) vòng học-hỏi — biến lỗi lặp
lại thành cải tiến vĩnh viễn cho quy trình, để hệ thống ngày một thông
minh hơn — nhưng chỉ cải tiến khi có bằng chứng, không bịa cải tiến,
không nới lỏng chuẩn.

Skill và quy trình: media-scout, media-video-production,
media-video-tech-qa (phòng Scoring đã đóng ngày 07/11/2026 theo quyết
C3; skill media-topic-scoring đã ngừng dùng), spec
(company-os/google-sheet-spec.md) và bot-sop này. Workbook "Video HQ — Tin Tức" (8 tab: TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN, SHIFT_CHECKIN). Luật kề nhau + trần AI + nền trung tính (DEC-242/243/244, quy tắc CEO 09/11/2026): xem skill media-video-production, mục 'Luật kề nhau', và LOGIC.md (nguyên tắc 6, 7) — không nhắc lại ở đây.
Cron này CHỈ ĐỌC Sheet + skill + nhật ký, KHÔNG ghi vào Sheet (không
ghi TOPICS/TASKS/QA_LOG/DECISIONS/COO_TASKS/CEO_REPORTS/COO_CHECKIN); mọi vấn đề/cải tiến ghi vào company-os/improvement-log.md theo bước 5–6; KHÔNG tự sửa file chuẩn, KHÔNG push GitHub.

0. Đồng bộ log học hỏi chéo (quyết CEO 13/11/2026 — học hỏi chéo): đầu ca, kéo bản company-os/improvement-log.md trên repo (GitHub API get_file_contents, repo duongvtrinh/video-tin-tuc, nhánh main) và hợp nhất mọi dòng IMP chưa có trong bản local vào bản local (chỉ thêm, không sửa/xóa dòng đã có). Sau đó mới đọc log local để đề xuất (bước 3) — để thấy được bài học của các chi nhánh khác và không đề xuất trùng mục đã có. Nếu không kéo được log repo (lỗi mạng/API) thì ghi blocker và dùng bản local tiếp, không dừng ca.

1. Kiểm tra toàn vẹn đầu ca (R7): chỉ đọc số dòng + ID lớn nhất (chỉ
   tính các dòng ĐÃ CÓ ID) của TOPICS và TASKS để nắm trạng thái hiện
   tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất (đã có) lùi
   KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026, R4-12: làm việc
   bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab
   BASELINE hay file baseline.json.
2. Kiểm mẫu (chức năng chính): đọc ngẫu nhiên 2–3 chủ đề đã được chấm
   trong ngày (TOPICS có điểm E–I và NOTES, DISCOVERED = hôm nay); kiểm
   lại từng cột điểm (HOT/AUDIENCE/FRESH/FEASIBLE/SOURCED) + nguồn
   (SOURCE) + số liệu bằng chứng trong NOTES. Ghi rõ mỗi chủ đề kiểm:
   TOPIC_ID (hoặc tiêu đề nếu chưa có ID), điểm gốc, điểm kiểm lại,
   khớp/lệch ở cột nào, nguồn có đúng vụ việc không. Nếu trong ngày
   không có chủ đề nào được chấm thì ghi rõ "ngày này không có chủ đề
   mới được chấm" và bỏ qua bước kiểm mẫu.
3. Vòng học-hỏi — thu thập: đọc QA_LOG và TASKS trong 7 ngày gần nhất
   (verdict Duyệt/Trả lại, lý do trả, số lần trả mỗi video), DECISIONS,
   nhật ký ngày trong 7 ngày gần nhất, và các skill + spec hiện tại, cùng company-os/improvement-log.md (để không đề xuất trùng mục đã có).
4. Vòng học-hỏi — tìm mẫu lặp: chỉ tính mẫu có bằng chứng từ 2 video
   trở lên, ví dụ: cùng một lỗi QA/preflight lặp lại, cùng một mẫu câu
   kịch bản bị trả, cùng một khái niệm media hay bị tìm lệch hoặc rơi về
   fallback, cùng một template gây lỗi, chủ đề điểm cao nhưng sản xuất
   kém (hoặc ngược lại), chu kỳ sản xuất dài bất thường ở cùng một khâu.
   Ghi rõ mỗi mẫu: tên mẫu, số video ảnh hưởng, bằng chứng (tên video,
   mốc thời gian, file, dòng QA log).
5. Vòng học-hỏi — ghi mục log cải tiến (quyết CEO 11/11/2026, thay mô hình tự áp dụng vào repo local): mỗi mẫu lặp đủ bằng chứng thành một mục trong company-os/improvement-log.md (ID dạng IMP-<YYYYMMDD>-<chi nhánh>-<số thứ tự>; đủ các trường: ngày, chi nhánh, loại vấn đề/cải tiến, mô tả, bằng chứng, thay đổi đề xuất ghi rõ file + nội dung trước/sau), ghi nối thêm vào bản local của file log với trạng thái ĐỀ XUẤT và gửi nguyên văn mục đó về chat COO. Bot KHÔNG tự sửa template/skill/spec như một cải tiến đã xong, KHÔNG push GitHub — thay đổi chỉ vào file chuẩn sau khi CEO duyệt, do chat chính áp dụng và đẩy lên repo, rồi trạng thái mục log chuyển ĐÃ ÁP DỤNG kèm mã commit.
6. Ghi log: các mục log đã tạo ở bước 5 cũng ghi tóm tắt vào nhật ký ngày (kèm ID mục) để tra cứu; nhật ký ngày không thay thế improvement-log.md — file log trên repo mới là nơi chuẩn duy nhất để các chi nhánh xem được mục của nhau. Không ghi đè hay xóa mục đã có.
7. Đề xuất cần CEO quyết (chỉ ghi lại, KHÔNG tự áp dụng): mọi ý tưởng
   đụng tới giới hạn cứng hoặc chuẩn đã chốt — đổi lệnh tự quyết độ dài
   (đề xuất 2–3 phút, Production tự quyết; chuẩn 180-300s đã bãi theo
   lệnh CEO tối 29/10/2026, xem A5), đổi 3 cửa QA, đổi thang điểm chấm
   chủ đề (thang 100 trong skill media-scout), đổi phạm vi công ty,
   đăng nền tảng, affiliate, chi tiền, push GitHub, thay đổi quyền thư
   mục Drive, xóa dữ liệu. Những đề xuất này chỉ xuất hiện trong báo
   cáo về chat COO, kèm lý do và bằng chứng, để COO leo thang qua CEO_REPORTS khi cần CEO quyết.
8. Nếu không tìm thấy mẫu lặp đủ bằng chứng thì KHÔNG bịa cải tiến: ca
   này im lặng về phần học-hỏi (chỉ báo phần kiểm mẫu), kết quả lưu
   trong lịch sử ca.

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không bịa nguồn/link/số liệu/bằng chứng, không ghi đè
hay xóa dòng đã có, không sửa MEMORY.md. Gặp 429/403/rate-limit thì dừng nhánh đó, ghi blocker, không chờ, không thử lại ẩu. Riêng thẻ phê duyệt upload Drive hết hạn sau 30 phút thì chạy lại upload một lần để lấy thẻ mới, và báo cho COO ghi tình trạng vào cột G "Kết quả hoàn thành" của dòng COO_TASKS tương ứng.

Báo cáo: nhắn về chat COO: (a) kết quả kiểm mẫu — kể cả khi tất cả
đều khớp thì báo ngắn 1 dòng (số chủ đề đã kiểm, đều khớp); khi lệch
thì báo chi tiết từng chủ đề (điểm gốc, điểm kiểm lại, lệch cột nào,
nguồn có đúng vụ việc không) + đề xuất; (b) liệt kê từng cải tiến đã áp
dụng kèm bằng chứng và file đổi, nếu có; (c) đề xuất cần CEO quyết, nếu
có; (d) blocker MỚI, nếu có. Ca không có gì mới ngoài kiểm mẫu đều khớp
thì chỉ báo 1 dòng kiểm mẫu, không báo thêm phần học-hỏi.
