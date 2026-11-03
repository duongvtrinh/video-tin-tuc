# SOP 3 bot tự động — công ty truyền thông một người

Nguồn: 3 lịch cron đang chạy (CEO ủy quyền chế độ bot tự động hoàn toàn:
bot chạy KHÔNG cần hỏi CEO trước, không cần chờ phê duyệt cho các bước
trong phạm vi dưới đây; bước nào vượt phạm vi thì dừng nhánh đó lại và
ghi blocker, không tự mở rộng phạm vi). Cùng tài khoản thì dùng tiếp 3
lịch + workbook + chat hiện có; khác tài khoản thì tạo lại đúng nhịp và
nội dung dưới đây, thay ID workbook/chat bằng ID mới. Cron là cấu hình
của tài khoản, không nằm trong repo.

Workbook: "HQ - Công ty 1 người" (cùng tài khoản: dùng tiếp workbook đang
chạy, không tạo mới, không ghi đè; khác tài khoản: tạo mới từ
`company-os/google-sheet-spec.md` — đủ 13 tab). Đọc/ghi Sheet bằng
connector Google Sheets. Không sửa MEMORY.md trong ca bot; quan sát ghi
vào nhật ký ngày.

## bot-lang-thang — mỗi 4 giờ (06:57, 10:57, 14:57, 18:57, 22:57, 02:57)

Vai trò: Scout tự động. Skill: media-scout. Tối đa 15 lượt tìm kiếm/ca,
tối đa 10 chủ đề mới/ca. Mục tiêu hệ thống: tối thiểu 5 video/ngày,
không giới hạn trên — mỗi ca ghi đủ chủ đề đạt chuẩn, không dừng sớm.

1. Đọc skill Scout và áp dụng đúng luật quét của nó.
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
5. Khử trùng: đọc toàn bộ tab 06_Topics, các dòng video trong 01_Tasks
   và 11_QA_Log. Trùng là cùng sự kiện/người/số liệu/câu chuyện dù
   wording khác, kể cả chủ đề đã làm trong 90 ngày với cùng góc. Chủ đề
   nghi trùng vẫn được ghi nhưng phải ghi rõ "Nghi trùng TOPIC-xxx" ở
   cột Ghi chú để Scoring quyết, không tự kết luận Duplicate.
6. Ghi chủ đề mới vào 06_Topics đúng thứ tự cột: ID (số tiếp theo sau
   ID lớn nhất đang có trong tab, không tự đoán; sau đợt làm sạch
   29/10/2026, số TOPIC tiếp nối từ TOPIC-028 — chủ đề mới đầu tiên sau
   làm sạch là TOPIC-029; không đánh lại từ 001; nếu tab trống hoàn toàn
   thì bắt đầu từ TOPIC-029), Tiêu đề, Nguồn (tên nguồn + link nếu có),
   Ngày phát hiện (ngày hôm nay, dạng YYYY-MM-DD), Trạng thái "Pending
   Scoring", các cột điểm ĐỂ TRỐNG (Scoring chấm, Scout không chấm),
   Góc làm (góc kể + vì sao thú vị, 2 câu), Ghi chú "Bot lang thang tự
   động" (+ "Nghi trùng TOPIC-xxx" nếu có), Cờ khôi phục ĐỂ TRỐNG, cột
   O "Duyệt thủ công" ghi "Chờ duyệt" cho mọi chủ đề mới (chỉ khi CEO
   đổi cột này thành "Duyệt" thì ca pipeline mới giao dựng). Đọc lại tab
   sau khi ghi để xác nhận số dòng đã tăng đúng.
7. Gửi nhiệm vụ chấm điểm sang chat Scoring, liệt kê các TOPIC mới và
   nhắc chấm theo thang 30+20+20+15+15=100 (Hot 30, Khán giả 20, Mới 20,
   Khả thi 15, Rõ nguồn 15). Nếu công cụ nhắn chat không có trong ca
   này thì KHÔNG coi là lỗi ca: ghi rõ vào kết quả ca để main agent
   chuyển tiếp.

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không sửa Drive, không bịa nguồn/link/điểm/ngày,
không ghi đè hay xóa dòng đã có. Gặp 429/403/rate-limit thì dừng tìm
kiếm của ca ngay, không thử lại cùng truy vấn trong ca.

Báo cáo: chỉ nhắn về chat chính khi (a) có chủ đề mới được ghi kèm nhiệm
vụ Scoring đã gửi hoặc gửi thất bại, hoặc (b) có blocker MỚI (tìm kiếm
bị chặn hoàn toàn, ghi Sheet thất bại). Ca không có chủ đề mới thì im
lặng, kết quả chỉ lưu trong lịch sử ca.

## bot-pipeline — mỗi 2 giờ (các ca :15)

Vai trò: điều phối pipeline. Chat nhân viên: Sản xuất, Kỹ thuật QA. Gửi
nhiệm vụ bằng chat.send_message; nếu công cụ nhắn chat không có trong ca
này thì chỉ ghi dòng Assigned vào 01_Tasks và ghi rõ vào kết quả ca để
main agent chuyển tiếp, không coi là lỗi ca.

A. Giao Sản xuất — luật duyệt thủ công (CEO lệnh 31/10/2026, thay luật
giao tất cả Approved): đọc 06_Topics và 01_Tasks. Chỉ giao các chủ đề
đồng thời thỏa cả ba điều kiện: Trạng thái Approved VÀ cột O "Duyệt thủ
công" = "Duyệt" VÀ chưa có dòng *-DRAFT nào trong 01_Tasks. Chủ đề
Approved nhưng cột O chưa phải "Duyệt" (kể cả "Chờ duyệt" hay để trống)
thì KHÔNG giao, không tạo video từ chủ đề đó. Không giới hạn số lượng
chủ đề đã duyệt — các dòng Assigned xếp hàng để Sản xuất làm lần lượt
theo thứ tự điểm cao nhất trước, không cần chờ hết dòng In Progress.
Nếu nhiều chủ đề thì gửi MỘT tin nhắn tổng hợp cho chat Sản xuất, trong
đó mỗi chủ đề có đủ: tiêu đề, góc làm, lưu ý pháp lý nếu có (ví dụ
phiên tòa đang diễn ra thì ghi rõ "theo cáo trạng / theo lời khai tại
tòa", không kết luận tội danh), và nhắc luật: kịch bản giọng người viết;
thời lượng do Sản xuất tự quyết (đề xuất 2–3 phút, dài hơn vẫn được khi
nội dung đã kiểm chứng, không cắt kịch bản đã kiểm chứng chỉ để vừa
chuẩn cũ, không xin ngoại lệ); tìm media theo luật phân nhánh hiện hành
(kịch bản Việt Nam: ảnh chỉ từ nguồn gốc, không dùng Wikipedia/Stock
cho ảnh; video từ Wikipedia/Stock được dùng nếu qua cửa bối cảnh cứng;
kịch bản nước ngoài: Wikipedia + Stock + nguồn chung; mọi media cho kịch
bản Việt Nam qua cửa bối cảnh cứng; ưu tiên ảnh/video thực tế của đúng
sự kiện trước minh họa chung chung); tự động hóa không tab duyệt thủ
công. Sau đó ghi mỗi chủ đề một dòng *-DRAFT vào 01_Tasks với trạng thái
Assigned và Ghi chú "Bot tự động" + ngày hôm nay. Không giao chủ đề
Duplicate, không giao chủ đề đã có dòng DRAFT. Nếu ca này không có chủ
đề nào thỏa cả ba điều kiện (kể cả trường hợp có chủ đề Approved nhưng
chưa chủ đề nào được duyệt thủ công) thì KHÔNG giao gì, KHÔNG tạo video,
mà gửi báo cáo về chat chính nêu rõ "chưa có chủ đề duyệt thủ công đang
chờ" rồi kết thúc bước A. Mục tiêu: Sản xuất hoàn thành tối thiểu 5
video/ngày từ các chủ đề đã duyệt; nếu số chủ đề đã duyệt vượt quá 5 thì
giao hết, không cắt bớt.

B. Bàn giao Drive: đọc 11_QA_Log và 08_Publish_Tracking. Thư mục bàn giao
đã được CEO xác nhận ngày 29/10/2026 là thư mục Drive "Video Muse" (tìm
bằng Drive files list với q name = 'Video Muse', không tự đoán ID). Quy
định mới 29/10/2026 (lệnh CEO): QA tải lên NGAY trong lượt duyệt, nên
bước B này chỉ là lưới bắt sót — chỉ khi có verdict Duyệt đã qua mà
08_Publish_Tracking và 01_Tasks vẫn chưa có link thì mới nhắn chat QA tải
file đã duyệt lên đúng thư mục Video Muse đó và ghi link thật vào
08_Publish_Tracking và 01_Tasks. Tuyệt đối không bịa link, không tự tạo
thư mục khác, không tự chia sẻ công khai thư mục (thư mục hiện không
chia sẻ công khai; nếu cần chia sẻ thì đó là quyết định riêng của CEO,
không phải của ca này).

C. Leo thang: nếu một video có từ 2 lần QA Trả lại trong 11_QA_Log mà
chưa có verdict Duyệt sau đó, và chưa từng leo thang video đó (kiểm tra
nhật ký ngày các ngày trước), thì nhắn về chat chính một lần để CEO xử
lý. Đã leo thang rồi thì không nhắc lại.

D. Nếu gặp thẻ phê duyệt của người dùng, 429/403/rate-limit thì dừng
nhánh đó, ghi blocker vào nhật ký ngày, không chờ, không thử lại ẩu.

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không bịa link/số liệu, không ghi đè hay xóa dòng đã
có, không sửa MEMORY.md.

Báo cáo: nhắn về chat chính khi có nhiệm vụ sản xuất mới được giao, có
leo thang mới, có blocker MỚI, HOẶC khi ca này không có chủ đề nào được
duyệt thủ công đang chờ (báo cáo "chưa có chủ đề duyệt thủ công" và bỏ
qua tạo video). Ca không thuộc các trường hợp trên thì im lặng, kết quả
chỉ lưu trong lịch sử ca.

## bot-hoc-hoi — hằng ngày ~20:22

Vai trò: biến lỗi lặp lại thành cải tiến vĩnh viễn cho quy trình, để hệ
thống ngày một thông minh hơn — nhưng chỉ cải tiến khi có bằng chứng,
không bịa cải tiến, không nới lỏng chuẩn.

Skill và quy trình: media-scout, media-topic-scoring,
media-video-production, media-video-tech-qa, và tab 03_SOP trong Sheet.

1. Thu thập: đọc 11_QA_Log và 01_Tasks trong 7 ngày gần nhất (verdict
   Duyệt/Trả lại, lý do trả, số lần trả mỗi video), 12_Repo_Updates,
   nhật ký ngày trong 7 ngày gần nhất, và các skill + 03_SOP hiện tại.
2. Tìm mẫu lặp: chỉ tính mẫu có bằng chứng từ 2 video trở lên, ví dụ:
   cùng một lỗi QA/preflight lặp lại, cùng một mẫu câu kịch bản bị trả,
   cùng một khái niệm media hay bị tìm lệch hoặc rơi về fallback, cùng
   một template gây lỗi, chủ đề điểm cao nhưng sản xuất kém (hoặc ngược
   lại), chu kỳ sản xuất dài bất thường ở cùng một khâu. Ghi rõ mỗi mẫu:
   tên mẫu, số video ảnh hưởng, bằng chứng (tên video, mốc thời gian,
   file, dòng QA log).
3. Áp dụng cải tiến có bằng chứng (mỗi cải tiến phải kèm: mẫu lỗi, bằng
   chứng, cách sửa, cách kiểm chứng): (a) sửa template theo đúng luật QA
   template-to-repo đã chốt (ghi template id, file đổi trong
   templates/<id>/, tăng version, lý do kèm mốc thời gian, bằng chứng
   trước/sau, kết quả render thử; cập nhật repo local, KHÔNG push
   GitHub); (b) bổ sung ghi chú đã kiểm chứng vào skill Production/QA/
   Scout/Scoring (mẫu câu cấm mới, cụm tìm media mới, bẫy hay gặp, cách
   tránh); (c) cập nhật phần tương ứng trong 03_SOP khi quy trình đổi.
   Sửa xong phải kiểm chứng lại (đọc lại file/skill đã sửa, chạy kiểm
   tra liên quan nếu có) trước khi báo cáo.
4. Ghi log: mỗi cải tiến đã áp dụng ghi vào 12_Repo_Updates (nếu là
   code/template) và vào nhật ký ngày (mọi cải tiến, kèm bằng chứng).
   Không ghi đè hay xóa dòng đã có.
5. Đề xuất cần CEO quyết (chỉ ghi lại, KHÔNG tự áp dụng): mọi ý tưởng
   đụng tới giới hạn cứng hoặc chuẩn đã chốt — đổi chuẩn thời lượng
   180-300s, đổi 3 cửa QA, đổi thang điểm Scoring, đổi phạm vi công ty,
   đăng nền tảng, affiliate, chi tiền, push GitHub, chia sẻ Drive, xóa
   dữ liệu. Những đề xuất này chỉ xuất hiện trong báo cáo về chat chính,
   kèm lý do và bằng chứng, để CEO quyết.
6. Nếu không tìm thấy mẫu lặp đủ bằng chứng thì KHÔNG bịa cải tiến: ca
   này im lặng, kết quả chỉ lưu trong lịch sử ca.

Giới hạn cứng: không đăng nền tảng, không gắn affiliate, không chi tiền,
không push GitHub, không bịa nguồn/link/số liệu/bằng chứng, không ghi đè
hay xóa dòng đã có, không sửa MEMORY.md. Gặp 429/403/rate-limit hoặc thẻ
phê duyệt thì dừng nhánh đó, ghi blocker, không chờ, không thử lại ẩu.

Báo cáo: chỉ nhắn về chat chính khi (a) đã áp dụng ít nhất 1 cải tiến
(liệt kê từng cải tiến kèm bằng chứng và file đổi), hoặc (b) có đề xuất
cần CEO quyết, hoặc (c) có blocker MỚI. Ca không có gì mới thì im lặng.
