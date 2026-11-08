# SOP 2 bot tự động — công ty truyền thông một người

Nguồn: 4 lịch cron đang chạy (CEO ủy quyền chế độ bot tự động hoàn toàn:
bot chạy KHÔNG cần hỏi CEO trước, không cần chờ phê duyệt cho các bước
trong phạm vi dưới đây; bước nào vượt phạm vi thì dừng nhánh đó lại và
ghi blocker, không tự mở rộng phạm vi). Cùng tài khoản thì dùng tiếp 4
lịch + workbook + chat hiện có; khác tài khoản thì tạo lại đúng nhịp và
nội dung dưới đây, thay ID workbook/chat bằng ID mới. Cron là cấu hình
của tài khoản; bản mẫu nằm trong repo tại company-os/crons/ (xem company-os/scheduled-tasks-setup.md) — chỉ cài khi CEO duyệt. bot-hoc-hoi chạy hằng ngày 20:00
Asia/Saigon (quyết CEO 07/11/2026, R4-14 phương án A, DEC-019; cron
bot-hoc-hoi-2000) — xem mục bot-hoc-hoi cuối file.

Workbook: "Video HQ — Trụ sở Muse" (spreadsheetId
`1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`; cùng tài khoản: dùng tiếp
workbook đang chạy, không tạo mới, không ghi đè; khác tài khoản: tạo mới
từ `company-os/google-sheet-spec.md` — đủ 5 tab: TOPICS, TASKS, QA_LOG,
DECISIONS, COO_TASKS). Đọc/ghi Sheet bằng connector Google Sheets.
Không sửa MEMORY.md trong ca bot; quan sát ghi vào nhật ký ngày.
Pipeline thuộc lịch bot đã được CEO duyệt (kênh giao việc số 2 trong 3
kênh duy nhất — xem BOOTSTRAP §8), không phải kênh riêng ngoài 3 kênh
đó.

## SCOUT — 4 ca/ngày (06:00, 10:00, 14:00, 18:00)

Vai trò: Scout tự động (2 phòng: Scout-Báo + Scout-Group, mỗi phòng tự chấm chủ đề của mình trong cùng lượt quét — chat Scoring đã đóng ngày 07/11/2026, quyết định C3). Skill: media-scout. Tối đa 15 lượt tìm kiếm/ca, tối đa 10 chủ đề mới/ca. Mục tiêu hệ thống: mỗi ca NHẬN tối đa 5 chủ đề READY, làm tuần tự theo thứ tự Sheet cho tới khi hết lô (trần NHẬN 5/ca vẫn còn; chỉ trần đếm 5 video đã bàn giao/ca mới bãi bỏ theo R4-02 ngày 07/11/2026 vì TASKS.J chỉ có ngày nên không đếm được theo ca — không giới hạn số video đã bàn giao/ngày); thực tế mỗi video ~40–70 phút nên một cửa sổ 4h làm được ~2–4 video.

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
6. Ghi chủ đề mới vào TOPICS đã chấm xong trong một lần ghi, đúng thứ tự cột: TOPIC_ID ĐỂ TRỐNG (Scout không tự sinh ID — quyết CEO 07/11/2026, phương án E cho R4-04; chỉ CEO nhập TOPIC_ID khi duyệt/lật READY, bằng công cụ riêng bên ngoài, đảm bảo không trùng; chủ đề không duyệt thì tiếp tục bỏ trống), TITLE, SOURCE (tên nguồn + link nếu có), DISCOVERED (ngày hôm nay, dạng YYYY-MM-DD), HOT / AUDIENCE / FRESH / FEASIBLE / SOURCED (điểm theo thang 30+20+20+15+15=100), TOTAL, STATUS theo thang và cửa quan tâm (≥70 và quan tâm Hot + Khán giả ≥30 → APPROVED; 50–69 → HOLD; ≥70 nhưng quan tâm <30 → HOLD + tín hiệu chờ vào NOTES; <50 → REJECTED; trùng → DUPLICATE + tiêu đề (và ID nếu có) của chủ đề gốc vào NOTES), ANGLE (góc kể + vì sao thú vị, 2 câu), NOTES ("Bot lang thang tự động" + số liệu bằng chứng cho điểm quan tâm; "Nghi trùng <tiêu đề hoặc TOPIC-xxx nếu có ID>" nếu có). Điểm và TOTAL chỉ là THAM KHẢO cho quyết định của CEO — điểm không chặn sản xuất; chỉ READY mới quyết định sản xuất. Đọc lại tab sau khi ghi để xác nhận số dòng đã tăng đúng (R3 — đọc lại theo tiêu đề ngay trước khi ghi).
7. Không có bàn giao Scoring: chat Scoring đã đóng (C3); chủ đề APPROVED chờ CEO flip READY (TOPICS.K APPROVED → READY) và CEO tự nhập TOPIC_ID khi flip (bằng công cụ riêng bên ngoài, đảm bảo không trùng). Không nhắn chat Scoring.

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không sửa Drive, không bịa nguồn/link/điểm/ngày,
không ghi đè hay xóa dòng đã có. Gặp 429/403/rate-limit thì dừng tìm
kiếm của ca ngay, không thử lại cùng truy vấn trong ca.

Báo cáo: LUÔN nhắn về chat chính cuối mỗi ca (kể cả ca trống): (a) có chủ đề mới được ghi (kèm tiêu đề + điểm + STATUS; TOPIC_ID nếu đã có), hoặc (b) có blocker MỚI (tìm kiếm bị chặn hoàn toàn, ghi Sheet thất bại). Ca trống (không có chủ đề mới, không có blocker mới) thì báo 1 dòng ngắn 'ca X: không có chủ đề mới' — KHÔNG im lặng. Ca 06:00 báo cáo NGAY lúc 06:00 (ngoại lệ khung proactivity 06:30–21:30 — quyết CEO 07/11/2026, R4-15 phương án A, DEC-020: CEO cần biết kết quả ca đầu ngày trước khi ra quyết định).

## PIPELINE — 4 ca/ngày (06:00, 10:00, 14:00, 18:00)

Vai trò: điều phối pipeline (một ca của lịch bot đã được CEO duyệt). Chat nhân viên: Sản xuất, Kỹ thuật QA. Gửi nhiệm vụ bằng chat.send_message; nếu công cụ nhắn chat không có trong ca này thì chỉ ghi dòng CLAIMED vào TASKS và ghi rõ vào kết quả ca để main agent chuyển tiếp, không coi là lỗi ca.

A. Giao Sản xuất — cổng READY + NHẬN THEO LÔ tối đa 5/ca (lệnh CEO 07/11/2026, thay thế luật tuần tự + R4-03; bỏ trần đếm theo R4-02 ngày 07/11/2026): đọc TOPICS và TASKS. Chỉ giao chủ đề đồng thời thỏa cả hai điều kiện: TOPICS.STATUS = READY VÀ TOPIC_ID đã có (không trống) VÀ chưa có dòng TASKS nào cho TOPIC_ID đó. TASKS là nguồn duy nhất (quyết CEO 07/11/2026, R4-11 phương án B): không kiểm tra thư mục projects hay tiến trình máy — video đang làm/chờ QA đều thể hiện bằng dòng TASKS (CLAIMED/BUILDING/REVIEW/RETURNED, trong đó REVIEW là chờ QA). Hạn chế đã chấp nhận: TASKS không thấy trạng thái render/TTS trên máy nếu project chưa ghi TASKS. Chủ đề APPROVED nhưng STATUS chưa phải READY thì KHÔNG giao, không tạo video từ chủ đề đó. Chủ đề READY mà TOPIC_ID trống thì BỎ QUA (không claim được vì TASKS cần TOPIC_ID), ghi vào báo cáo ca để CEO nhập ID. Điểm và TOTAL chỉ là tham khảo cho quyết định của CEO — điểm không chặn sản xuất; chỉ READY mới quyết định sản xuất. Không giới hạn số video ĐÃ BÀN GIAO/ca hay /ngày (chỉ trần đếm 5 video đã bàn giao/ca mới bãi bỏ theo R4-02 — TASKS.J chỉ có ngày nên không đếm được theo ca; trần NHẬN tối đa 5 chủ đề READY/ca vẫn còn); NHẬN THEO LÔ: mỗi ca NHẬN 1 LẦN tối đa 5 chủ đề READY theo thứ tự Sheet, đánh dấu ngay bằng dòng TASKS CLAIMED (ASSIGNEE = email khai báo của chi nhánh mình) để các chi nhánh khác biết đã có người làm; sau đó lần lượt tạo 5 video (sản xuất tuần tự từng video một qua Production → QA → bàn giao Drive), không sản xuất song song. Mỗi ca nhận đủ 5 chủ đề READY mới, không trừ số video đang làm dở trong ngày (quyết CEO 08/11/2026, T3 phương án B); tổng số video đang làm cùng lúc có thể vượt 5. Video đang làm dở từ NGÀY CŨ thì bỏ qua theo quy tắc ngày hiện tại. Không còn cơ chế nhận tiếp theo sự kiện QA báo DELIVERED — việc nhận chủ đề chỉ xảy ra 1 lần đầu ca, theo lô; khi một video trong lô DELIVERED thì Production TỰ LẤY video kế tiếp trong lô (lệnh CEO 07/11/2026, DEC-032 — không chờ pipeline giao lại; chỉ lấy chủ đề đã CLAIMED trong cùng lô, ASSIGNEE = email khai báo của mình, UPDATED_AT = ngày hôm nay; video trước BLOCKED thì dừng chờ COO gỡ tắc; video đầu tiên của lô vẫn do pipeline giao), hết lô thì chờ ca sau nhận lô mới. Đầu ca kiểm tra: ghi nhận video đang làm của mình TRONG NGÀY (CLAIMED/BUILDING/REVIEW/RETURNED, ASSIGNEE = email khai báo của tài khoản, UPDATED_AT là ngày hôm nay) để báo cáo ca; số video đang làm dở KHÔNG trừ vào số chủ đề mới được nhận — mỗi ca nhận đủ 5 chủ đề READY mới; video đang làm của chi nhánh khác (ASSIGNEE là email khác) hoặc ASSIGNEE trống thì KHÔNG phải của mình — bỏ qua, ghi các dòng đó (TOPIC_ID + STATUS + ASSIGNEE) vào báo cáo ca để COO xác định chủ; chỉ video BLOCKED mà TASKS.D ASSIGNEE = email khai báo của tài khoản của chi nhánh mình VÀ TASKS.J UPDATED_AT là ngày hôm nay mới dừng hàng đợi, cho đến khi COO gỡ tắc hoặc hủy (CANCELLED); video BLOCKED từ NGÀY CŨ (UPDATED_AT không phải ngày hôm nay) thì bỏ qua theo quy tắc ngày hiện tại — không dừng hàng đợi, ghi vào báo cáo ca để COO xác định chủ/xử lý; video BLOCKED của chi nhánh khác (ASSIGNEE là email khác) hoặc ASSIGNEE trống thì KHÔNG dừng hàng đợi — nhận chủ đề READY khác như bình thường, ghi các dòng đó vào báo cáo ca để COO xác định chủ; COO chỉ gỡ tắc/hủy dòng BLOCKED của chi nhánh mình. Chọn tối đa 5 chủ đề READY ĐÃ CÓ TOPIC_ID theo thứ tự Sheet. Chủ đề READY mà TOPIC_ID trống thì bỏ qua, ghi vào báo cáo ca để CEO nhập ID. Ghi từng dòng TASKS CLAIMED (ASSIGNEE = email khai báo của tài khoản) rồi đọc lại theo ID (R3 claim-then-verify từng chủ đề): nếu có 2 dòng CLAIMED cùng TOPIC_ID thì chủ đề đó dừng ngay, ghi Blocker vào TASKS.N DUP_NOTE, báo chat chính (các chủ đề còn lại trong lô vẫn làm tiếp). Gửi tin nhắn cho chat Sản xuất cho video ĐẦU TIÊN trong lô (các video sau trong lô Production TỰ LẤY khi video trước DELIVERED theo lệnh CEO 07/11/2026, DEC-032 — pipeline không giao lần lượt nữa; video trước BLOCKED thì dừng chờ COO gỡ tắc), trong đó có đủ: tiêu đề, góc làm, lưu ý pháp lý nếu có (ví dụ phiên tòa đang diễn ra thì ghi rõ "theo cáo trạng / theo lời khai tại tòa", không kết luận tội danh), và nhắc luật: kịch bản giọng người viết; thời lượng do Sản xuất tự quyết (đề xuất 2–3 phút, dài hơn vẫn được khi nội dung đã kiểm chứng, không cắt kịch bản đã kiểm chứng chỉ để vừa chuẩn cũ, không xin ngoại lệ); tìm media theo luật phân nhánh hiện hành (kịch bản Việt Nam: ảnh chỉ từ nguồn gốc, không dùng Wikipedia/Stock cho ảnh; video từ Wikipedia/Stock được dùng nếu qua cửa bối cảnh cứng; kịch bản nước ngoài: Wikipedia + Stock + nguồn chung; mọi media cho kịch bản Việt Nam qua cửa bối cảnh cứng; ưu tiên ảnh/video thực tế của đúng sự kiện trước minh họa chung chung); tự động hóa không tab duyệt thủ công. Không giao chủ đề DUPLICATE, không giao chủ đề đã có dòng TASKS. Nếu ca này không có chủ đề nào thỏa cả hai điều kiện thì KHÔNG giao gì, KHÔNG tạo video, mà gửi báo cáo về chat chính nêu rõ "chưa có chủ đề READY đang chờ" rồi kết thúc bước A. C/J/D nhiều người viết — ghi sau thắng + để lại lý do (quyết CEO 07/11/2026, R4-10 phương án C): TASKS.C STATUS có 3 người viết (Production: CLAIMED/BUILDING/REVIEW; QA: RETURNED/APPROVED/DELIVERED; COO: BLOCKED/CANCELLED), TASKS.J UPDATED_AT có 2 người viết (Production, QA), TASKS.D ASSIGNEE có 2 người viết (Production lúc claim, COO lúc giao qua COO_TASKS) — chấp nhận ghi sau thắng khi xung đột (lần ghi sau thắng, không có quy tắc ai thắng theo vai trò); ai ghi TASKS.C thì trong cùng lần ghi phải ghi thêm lý do + thời gian vào cột ghi chú của mình (Production→K PROD_NOTES, QA→QA_LOG cột E ISSUES + TASKS.F QA_VERDICT, COO→M BLOCKER, Pipeline→lý do nhận lô ghi vào báo cáo ca, trùng CLAIMED ghi N DUP_NOTE).

B. Bàn giao Drive: đọc QA_LOG và TASKS. Thư mục bàn giao đã được CEO xác nhận là thư mục Drive "Video Muse" (quyền anyone with link đã được CEO cấp; tìm bằng Drive files list với q name = 'Video Muse', không tự đoán ID). Quy định mới 29/10/2026 (lệnh CEO): QA tải lên NGAY trong lượt duyệt, nên bước B này chỉ là lưới bắt sót — chỉ khi có verdict APPROVED đã qua mà TASKS vẫn chưa DELIVERED (thiếu H DRIVE_LINK hoặc I MD5) thì mới nhắn chat QA tải file đã duyệt lên đúng thư mục Video Muse đó và ghi link thật vào TASKS (H DRIVE_LINK + I MD5, STATUS = DELIVERED); khi ghi link, ghi luôn vào TASKS.L QUOTA đủ email người sản xuất theo quy tắc thống nhất và hạn mức lúc upload do QA tự đọc lại tại thời điểm upload, bằng chữ, không chụp màn hình. Tuyệt đối không bịa link, không tự tạo thư mục khác, không tự thay đổi quyền thư mục (thư mục "Video Muse" đã được CEO cấp quyền anyone with link ngày 05/11/2026).

C. Leo thang: nếu một video có từ 2 lần QA Trả lại trong QA_LOG (đếm RESULT = RETURNED theo VIDEO_ID) mà chưa có verdict Duyệt sau đó, và chưa từng leo thang video đó (kiểm tra nhật ký ngày các ngày trước), thì nhắn về chat chính một lần để CEO xử lý. Đã leo thang rồi thì không nhắc lại.

D. Nếu gặp 429/403/rate-limit thì dừng
nhánh đó, ghi blocker vào nhật ký ngày, không chờ, không thử lại ẩu. Riêng thẻ phê duyệt upload Drive hết hạn sau 30 phút (approval_expired / Timed out) thì KHÔNG dừng hẳn: **Thẻ phê duyệt upload Drive hết hạn sau 30 phút (lệnh CEO 05/11/2026, tiền lệ TOPIC-232):** lệnh upload lên Drive hiện thẻ phê duyệt, chỉ cho 30 phút để bấm; hết 30 phút không có quyết định thì thẻ tự hết hạn (approval_expired / Timed out), thao tác không chạy, file không lên Drive. Tiền lệ: thẻ gửi 10:52:57 +07, hết hạn 11:22:57 +07, Timed out 11:23:02 +07 — không phải bị từ chối, không phải file hỏng hay thư mục sai quyền. Cách xử lý đúng là **chạy lại upload một lần để hệ thống cấp thẻ mới** (không tính là "thử lại ẩu"); cấp phép toàn quyền của CEO cho QA hoàn tất bàn giao mà không hỏi lại trong chat **không tắt được thẻ hệ thống** — thẻ vẫn hiện mỗi lần upload, cần bấm trong 30 phút; upload Drive không có standing Allow. **Khi gặp thẻ hết hạn, QA phải báo ngay cho COO; COO ghi lại thông báo tình trạng vào cột H "Kết quả hoàn thành" của dòng COO_TASKS tương ứng (ghi tạm thời trong khi nhiệm vụ vẫn ở "Đang làm", cột G thời gian hoàn thành vẫn để trống), để CEO đọc tab COO_TASKS là biết vấn đề ở đâu, không phải chờ tới khi xong mới biết. Khi nhiệm vụ hoàn thành sau đó, COO cập nhật lại cột H bằng kết quả cuối cùng kèm link. Quy tắc này khác với 429/403/rate-limit: gặp 429/403 thì dừng nhánh, ghi blocker, không thử lại.**

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không bịa link/số liệu, không ghi đè hay xóa dòng đã
có, không sửa MEMORY.md.

Báo cáo: nhắn về chat chính khi có nhiệm vụ sản xuất mới được giao, có
leo thang mới, có blocker MỚI, HOẶC khi ca này không có chủ đề nào READY
đang chờ (báo cáo "chưa có chủ đề READY" và bỏ qua tạo video). Ca không thuộc các trường hợp trên thì im lặng, kết quả chỉ lưu trong lịch sử ca.

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
(company-os/google-sheet-spec.md) và bot-sop này. Workbook "Video HQ —
Trụ sở Muse" (5 tab: TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS).
Cron này CHỈ ĐỌC Sheet + skill + nhật ký, KHÔNG ghi vào Sheet (không
ghi TOPICS/TASKS/QA_LOG/DECISIONS/COO_TASKS); mọi cải tiến áp dụng vào
repo local thì KHÔNG push GitHub.

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
   nhật ký ngày trong 7 ngày gần nhất, và các skill + spec hiện tại.
4. Vòng học-hỏi — tìm mẫu lặp: chỉ tính mẫu có bằng chứng từ 2 video
   trở lên, ví dụ: cùng một lỗi QA/preflight lặp lại, cùng một mẫu câu
   kịch bản bị trả, cùng một khái niệm media hay bị tìm lệch hoặc rơi về
   fallback, cùng một template gây lỗi, chủ đề điểm cao nhưng sản xuất
   kém (hoặc ngược lại), chu kỳ sản xuất dài bất thường ở cùng một khâu.
   Ghi rõ mỗi mẫu: tên mẫu, số video ảnh hưởng, bằng chứng (tên video,
   mốc thời gian, file, dòng QA log).
5. Vòng học-hỏi — áp dụng cải tiến có bằng chứng (mỗi cải tiến phải
   kèm: mẫu lỗi, bằng chứng, cách sửa, cách kiểm chứng): (a) sửa
   template theo đúng luật QA template-to-repo đã chốt (ghi template
   id, file đổi trong templates/<id>/, tăng version, lý do kèm mốc thời
   gian, bằng chứng trước/sau, kết quả render thử; cập nhật repo local,
   KHÔNG push GitHub); (b) bổ sung ghi chú đã kiểm chứng vào skill
   Production/QA/Scout (mẫu câu cấm mới, cụm tìm media mới, bẫy hay
   gặp, cách tránh); (c) cập nhật phần tương ứng trong spec/bot-sop khi
   quy trình đổi. Sửa xong phải kiểm chứng lại (đọc lại file/skill đã
   sửa, chạy kiểm tra liên quan nếu có) trước khi báo cáo.
6. Ghi log: mỗi cải tiến đã áp dụng ghi vào nhật ký ngày (mọi cải tiến,
   kèm bằng chứng) và báo về chat chính để ghi vào DECISIONS (cải tiến
   code/template hoặc đổi quy trình/chuẩn — cron KHÔNG tự ghi vào
   Sheet; workbook mới không còn tab 12_Repo_Updates). Không ghi đè hay
   xóa dòng đã có.
7. Đề xuất cần CEO quyết (chỉ ghi lại, KHÔNG tự áp dụng): mọi ý tưởng
   đụng tới giới hạn cứng hoặc chuẩn đã chốt — đổi lệnh tự quyết độ dài
   (đề xuất 2–3 phút, Production tự quyết; chuẩn 180-300s đã bãi theo
   lệnh CEO tối 29/10/2026, xem A5), đổi 3 cửa QA, đổi thang điểm chấm
   chủ đề (thang 100 trong skill media-scout), đổi phạm vi công ty,
   đăng nền tảng, affiliate, chi tiền, push GitHub, thay đổi quyền thư
   mục Drive, xóa dữ liệu. Những đề xuất này chỉ xuất hiện trong báo
   cáo về chat chính, kèm lý do và bằng chứng, để CEO quyết.
8. Nếu không tìm thấy mẫu lặp đủ bằng chứng thì KHÔNG bịa cải tiến: ca
   này im lặng về phần học-hỏi (chỉ báo phần kiểm mẫu), kết quả lưu
   trong lịch sử ca.

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không bịa nguồn/link/số liệu/bằng chứng, không ghi đè
hay xóa dòng đã có, không sửa MEMORY.md. Gặp 429/403/rate-limit thì dừng nhánh đó, ghi blocker, không chờ, không thử lại ẩu. Riêng thẻ phê duyệt upload Drive hết hạn sau 30 phút thì chạy lại upload một lần để lấy thẻ mới, và báo cho COO ghi tình trạng vào cột H "Kết quả hoàn thành" của dòng COO_TASKS tương ứng.

Báo cáo: nhắn về chat chính: (a) kết quả kiểm mẫu — kể cả khi tất cả
đều khớp thì báo ngắn 1 dòng (số chủ đề đã kiểm, đều khớp); khi lệch
thì báo chi tiết từng chủ đề (điểm gốc, điểm kiểm lại, lệch cột nào,
nguồn có đúng vụ việc không) + đề xuất; (b) liệt kê từng cải tiến đã áp
dụng kèm bằng chứng và file đổi, nếu có; (c) đề xuất cần CEO quyết, nếu
có; (d) blocker MỚI, nếu có. Ca không có gì mới ngoài kiểm mẫu đều khớp
thì chỉ báo 1 dòng kiểm mẫu, không báo thêm phần học-hỏi.
