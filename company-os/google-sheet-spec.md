# Bảng điều phối — Công ty 1 người

Workbook: HQ - Công ty 1 người

Tạo mới từ spec này thì tạo đủ 13 tab dưới đây với đúng tên tab và đúng
hàng tiêu đề, dữ liệu bắt đầu trống. Cùng tài khoản thì dùng tiếp workbook
đang chạy, không tạo mới, không ghi đè. Tuyệt đối không dùng lệnh Drive
ghi đè lên file Google Sheet (Drive thay toàn bộ file, mất các tab khác);
sửa từng ô qua Sheets API.

## Tabs và cột (hàng 1 = tiêu đề, đúng thứ tự)

### 00_Dashboard
Mục | Nội dung
COO cập nhật cuối ngày: việc đang chạy, việc tắc, việc cần CEO.

### 01_Tasks — nguồn sự thật duy nhất
ID | Việc | Định nghĩa xong | Chủ sở hữu | Người kiểm tra | Ưu tiên | Trạng thái | Deadline | Link kết quả | Blocker | Cần CEO? | Hoàn thành? | Ngày hoàn thành | Cờ khôi phục | Tài khoản Muse nhận việc (email) | Thời gian hoàn thành | Nhiệm vụ đã thực hiện (báo cáo qua Sheet)
Trạng thái dùng thực tế: Assigned, Review, Duyệt (dữ liệu cũ có ghi "Duyet").
Mỗi video có một dòng *-DRAFT khi được giao; dòng DRAFT chuyển Review khi
nộp QA, Duyệt khi QA duyệt kèm link Drive thật.
Quy tắc ghi: mỗi agent chỉ sửa dòng mang tên mình; chỉ COO sửa 00_Dashboard
và 04_Decisions; bàn giao phải có link kết quả trong Sheet.
CEO giao qua Sheet cho COO, COO báo cáo lại qua Sheet (lệnh CEO 04/11/2026,
bổ sung, không thay luật chat chính cho nhiệm vụ giao trực tiếp):
- CEO không cần chat trực tiếp mà giao bằng cách ghi một dòng ở 01_Tasks
với đầy đủ: Việc + Định nghĩa xong + Trạng thái Assigned + Deadline (nếu
có) + cột O "Tài khoản Muse nhận việc (email)" ghi đúng email của tài
khoản Muse quản lý công ty đó. Cột O là khóa phân biệt công ty: COO nào
đọc thấy email khác email của mình thì bỏ qua, không được nhận, không
được giao cho phòng của mình.
- Mỗi ngày, mỗi COO đọc 01_Tasks đúng 1 lần đầu ca và chỉ đọc dòng chưa
hoàn thành: cột O = email của mình VÀ Hoàn thành? chưa phải "Có" VÀ Thời
gian hoàn thành còn trống. Dòng đã Hoàn thành? = "Có" + có Thời gian hoàn
thành thì bỏ qua, trừ khi có dòng ID mới. Dòng chỉ có Trạng thái = Duyệt
mà chưa điền Hoàn thành?/Thời gian hoàn thành thì chưa tính là xong, COO
vẫn phải thấy và đóng nốt.
- Khi nhận đúng dòng của mình, COO tự thực hiện theo yêu cầu CEO và tự
giao cho các phòng chức năng qua chat phòng đó (Sheet là kênh CEO → COO,
chat vẫn là kênh COO → phòng), không chờ chat trực tiếp từ CEO, không hỏi
lại CEO trừ khi yêu cầu mơ hồ hoặc vượt phạm vi. Ví dụ: CEO ghi dòng cho
tài khoản abc@domail.com "Đổi lịch sản xuất video 6 giờ sáng thành 8 giờ
sáng" thì COO của tài khoản đó tự đổi lịch trong bộ quy tắc/lịch liên quan
(vd bot-sop, skill, lịch bot đã duyệt), ra lệnh cho các phòng chức năng
tuân theo lịch mới, rồi mới đóng nhiệm vụ.
- Báo cáo trực tiếp với CEO qua Sheet, không cần chat: sau khi xong việc,
COO cập nhật cùng dòng đó (không tạo dòng mới, không xóa dòng cũ): Trạng
thái = Duyệt (với video) hoặc trạng thái hoàn tất tương ứng, Hoàn thành?
= "Có", Ngày hoàn thành = ngày đó, cột P "Thời gian hoàn thành" ghi giờ
phút cụ thể dạng "YYYY-MM-DD HH:MM +07" (vd "2026-11-05 08:30 +07"), cột Q
"Nhiệm vụ đã thực hiện (báo cáo qua Sheet)" ghi rõ đã làm gì, đổi cái gì,
từ đâu sang đâu, đã ra lệnh cho phòng nào, link/bằng chứng ở đâu (vd "Đã
đổi lịch sản xuất video từ 6h sang 8h trong bot-sop và lịch bot, đã ra lệnh
cho Sản xuất và QA tuân theo lịch mới từ ngày ..."). CEO đọc Sheet là thấy
báo cáo hoàn thành, không cần COO nhắn chat riêng. Thiếu cột P hoặc Q thì
chưa tính là báo cáo xong.

### 02_Agents
Tên Muse | Vai trò | Phạm vi được quyết | Phạm vi KHÔNG được quyết | Chat / kênh | Ca cập nhật | Cờ khôi phục
Vai trò hiện tại (lệnh CEO 04/11/2026): Chat chính là kênh CEO giao nhiệm vụ trực tiếp; agent ở chat chính là điều phối viên, tự động điều phối nhiệm vụ đến đúng phòng liên quan, theo dõi, tổng hợp kết quả và báo cáo lại cho CEO ở chat chính. Các phòng: COO (chat riêng, điều phối vận hành) + 5 phòng (Scout-Báo, Scout-Group, Scoring, Sản xuất, Kỹ thuật QA), mỗi phòng một chat; 2 chat Scout dùng chung skill media-scout. Một nhiệm vụ = một chủ sở hữu duy nhất, khóa bằng dòng Assigned / *-DRAFT trước khi làm; cấm chạy song song cùng nhiệm vụ ở chat chính và phòng ban (bài học vụ trùng TOPIC-219 ngày 04/11/2026).
Ngoại lệ CEO → COO qua Sheet (lệnh CEO 04/11/2026, xem tab 01_Tasks): CEO có thể giao cho COO mà không cần chat trực tiếp, bằng dòng 01_Tasks có cột O là email tài khoản Muse nhận việc. COO đọc Sheet mỗi ngày, nhận đúng dòng email của mình, tự thực hiện và giao cho các phòng qua chat, rồi báo cáo hoàn thành lại qua Sheet (cột P, Q). Trong đường này, lệnh của COO cho phòng chức năng có nguồn gốc từ lệnh CEO qua Sheet nên phòng tuân theo, không phải là phòng tự phát sinh việc.

### 03_SOP
Phần | Nội dung

### 04_Decisions — chỉ CEO quyết
ID | Vấn đề | Phương án A | Phương án B | Đề xuất của COO | Quyết định của CEO | Ngày quyết | Cờ khôi phục

### 05_Weekly Report
Tuần | Đã xong | Đang chạy | Tắc / cần CEO | Tuần tới

### 06_Topics
ID | Tiêu đề | Nguồn | Ngày phát hiện | Trạng thái | Hot (30) | Khán giả (20) | Mới (20) | Khả thi (15) | Rõ nguồn (15) | Tổng (100) | Góc làm | Ghi chú | Cờ khôi phục | Duyệt thủ công
Thang Scoring: Hot 30 + Khán giả 20 + Mới 20 + Khả thi 15 + Rõ nguồn 15
= 100; ≥70 Approved nhưng cửa quan tâm Hot + Khán giả ≥30/50 xét trước
tổng; 50–69 Hold; <50 Rejected; trùng = Duplicate + ID gốc.
Cột O "Duyệt thủ công": chủ đề mới ghi "Chờ duyệt"; CHỈ chủ đề đồng thời
thỏa cả ba điều kiện — Trạng thái Approved VÀ cột O = "Duyệt" VÀ chưa có
dòng *-DRAFT nào trong 01_Tasks — mới được giao dựng; Production không tự
đánh dấu "Duyệt", chỉ CEO đổi cột này.

### 07_Affiliate_Products
Mã | Sản phẩm | Link affiliate | Hoa hồng | Trạng thái | Ghi chú
Tab thuộc công ty khác (đăng tải/affiliate/doanh thu); giữ tab để dữ liệu
không mất.

### 08_Publish_Tracking
ID Video | Tiêu đề / Chủ đề | Nền tảng | Ngày đăng | Link video | Trạng thái | MD5 | Cờ khôi phục | Người sản xuất (email tài khoản Muse) | Hạn mức còn lại (Muse tuần + hạn mức khác)
QA tải video đã duyệt lên thư mục Drive "Video Muse" ngay trong lượt duyệt
và ghi link thật vào đây + 01_Tasks; không bịa link, không tự chia sẻ
công khai thư mục (quyết định riêng của CEO).
Ký nhận + hạn mức (lệnh CEO 04/11/2026, áp từ video bàn giao sau ngày này;
video cũ đã bàn giao trước đó để trống 2 cột mới, không điền ngược số liệu
đoán): ngay sau bước upload Drive và ghi link vào Sheet, cùng dòng đó phải
điền đủ 2 cột mới, không được để trống rồi bàn giao:
- Cột I "Người sản xuất (email tài khoản Muse)": email của tài khoản Muse
đã thực hiện sản xuất video này (Production ghi trong bàn giao cho QA, QA
sao đúng email đó sang đây). Đây là chữ ký nhận trách nhiệm, không phải tên
phòng, không phải tên người dùng/CEO, không dùng email của tài khoản khác
(vd email Facebook, email GitHub noreply) thay thế. Nếu không xác định được
email thì ghi rõ "chưa xác định — hỏi CEO", không bịa email.
- Cột J "Hạn mức còn lại (Muse tuần + hạn mức khác)": chỉ ghi thông tin
chi tiết bằng chữ vào ô này, KHÔNG chụp ảnh màn hình, không đính kèm ảnh.
Ghi đúng tại thời điểm bàn giao, định dạng: "Muse tuần đã dùng X%, còn Y%,
reset <ngày> lúc <giờ> +07; <hạn mức khác> còn <số>;" — vd "Muse tuần đã dùng
10%, còn 90%, reset 9/11 lúc 14:14 +07; token thêm còn 1B". Muse báo mức
dùng theo hạn mức gói, không phải số token tuyệt đối, nên ghi đúng dạng
phần trăm + reset mà công cụ trạng thái gói trả về. "Hạn mức khác" là mọi
hạn mức khác đã dùng trong lần sản xuất đó mà đọc được (vd dung lượng
Drive còn lại, hạn mức tạo ảnh/video/TTS nếu có) — ghi từng loại một bằng
chữ, loại nào không đọc được thì ghi "không đọc được" kèm ngày giờ, loại
nào không áp dụng thì ghi "không áp dụng", tuyệt đối không bịa con số.
Cột này là bản ghi chữ tại thời điểm bàn giao, không cập nhật ngược sau
đó khi hạn mức thay đổi.

### 09_Skills
Skill | Mô tả | File | Trạng thái | Cờ khôi phục

### 10_Media_Sources
Video/Project | Cảnh/Part | File đã chọn | Nguồn | Link trang file | Giấy phép | Điểm số | Loại | Bằng chứng soi trực quan | Lý do loại các lớp khác

### 11_QA_Log
Video | Phiên bản | Ngày | Kết quả | Lỗi kèm mốc thời gian | Mã đề xuất repo | Cờ khôi phục
Video bị trả 2 lần chưa có verdict Duyệt sau đó thì leo thang lên CEO
một lần.

### 12_Repo_Updates
Template id | File đổi | Version tăng | Lý do QA kèm mốc thời gian | Bằng chứng trước/sau | Kết quả render thử | Trạng thái cập nhật local | Trạng thái push GitHub
Mỗi lần QA sửa template đều có đề xuất cập nhật repo cùng verdict; cập
nhật local bắt buộc, push GitHub riêng cần CEO duyệt.

## Quy tắc leo thang lên CEO
Chỉ leo thang khi: chi tiền, cam kết bên ngoài, thay đổi không đảo ngược,
pháp lý, tắc > 24h, xung đột giữa 2 nhân viên, vượt ngân sách.
Còn lại COO tự quyết và ghi vào Decisions để CEO xem sau.
