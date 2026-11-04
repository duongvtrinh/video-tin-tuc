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
ID | Việc | Định nghĩa xong | Chủ sở hữu | Người kiểm tra | Ưu tiên | Trạng thái | Deadline | Link kết quả | Blocker | Cần CEO? | Hoàn thành? | Ngày hoàn thành | Cờ khôi phục
Trạng thái dùng thực tế: Assigned, Review, Duyệt (dữ liệu cũ có ghi "Duyet").
Mỗi video có một dòng *-DRAFT khi được giao; dòng DRAFT chuyển Review khi
nộp QA, Duyệt khi QA duyệt kèm link Drive thật.
Quy tắc ghi: mỗi agent chỉ sửa dòng mang tên mình; chỉ COO sửa 00_Dashboard
và 04_Decisions; bàn giao phải có link kết quả trong Sheet.

### 02_Agents
Tên Muse | Vai trò | Phạm vi được quyết | Phạm vi KHÔNG được quyết | Chat / kênh | Ca cập nhật | Cờ khôi phục
Vai trò hiện tại (lệnh CEO 04/11/2026): Chat chính là kênh CEO giao nhiệm vụ trực tiếp; agent ở chat chính là điều phối viên, tự động điều phối nhiệm vụ đến đúng phòng liên quan, theo dõi, tổng hợp kết quả và báo cáo lại cho CEO ở chat chính. Các phòng: COO (chat riêng, điều phối vận hành) + 5 phòng (Scout-Báo, Scout-Group, Scoring, Sản xuất, Kỹ thuật QA), mỗi phòng một chat; 2 chat Scout dùng chung skill media-scout. Một nhiệm vụ = một chủ sở hữu duy nhất, khóa bằng dòng Assigned / *-DRAFT trước khi làm; cấm chạy song song cùng nhiệm vụ ở chat chính và phòng ban (bài học vụ trùng TOPIC-219 ngày 04/11/2026).

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
ID Video | Tiêu đề / Chủ đề | Nền tảng | Ngày đăng | Link video | Trạng thái | MD5 | Cờ khôi phục
QA tải video đã duyệt lên thư mục Drive "Video Muse" ngay trong lượt duyệt
và ghi link thật vào đây + 01_Tasks; không bịa link, không tự chia sẻ
công khai thư mục (quyết định riêng của CEO).

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
