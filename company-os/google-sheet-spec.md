# Bảng điều phối — Công ty 1 người

Workbook: HQ - Công ty 1 người

Tạo mới từ spec này thì tạo đủ 14 tab dưới đây với đúng tên tab và đúng
hàng tiêu đề, dữ liệu bắt đầu trống. Cùng tài khoản thì dùng tiếp workbook
đang chạy, không tạo mới, không ghi đè. Tuyệt đối không dùng lệnh Drive
ghi đè lên file Google Sheet (Drive thay toàn bộ file, mất các tab khác);
sửa từng ô qua Sheets API.

## Bảng phân quyền ghi Sheet (chuẩn duy nhất cho luật Sheet — các file khác chỉ trỏ tới đây, không chép lại)

| Ai ghi | Tab | Cột / dòng được ghi | Không được ghi |
|---|---|---|---|
| CEO | 13_COO_Tasks | Chỉ 2 ô: B email nhận việc, C Việc chính (cột A để trống) | Cột A (ID), E, F, G, H của tab 13 |
| CEO | 06_Topics | Cột O "Duyệt thủ công" (đổi thành "Duyệt") | Điểm số, Trạng thái do Scoring chấm |
| CEO | 04_Decisions | Cột "Quyết định của CEO", "Ngày quyết" | — |
| COO | 00_Dashboard | Toàn tab, cập nhật cuối ngày | — |
| COO | 04_Decisions | Chỉ cột "Đề xuất của COO" | Cột quyết định của CEO |
| COO | 13_COO_Tasks | A (ID), D (phân việc), E, F, G, H — chỉ dòng có cột B = email khai báo của mình (trong bộ nhớ) | Dòng có cột B là email khác |
| COO | 01_Tasks | Chỉ theo dõi tiến độ | Không ghi đè, không xóa dòng đã có, không tự tạo dòng *-DRAFT thay Production / bot-pipeline |
| Scout (kể cả bot-lang-thang) | 06_Topics | Dòng chủ đề mới, trừ các cột điểm; cột O ghi "Chờ duyệt" | Các cột điểm (Scoring chấm), cột O "Duyệt" |
| Scoring | 06_Topics | Các cột điểm (Hot, Khán giả, Mới, Khả thi, Rõ nguồn), Tổng, Trạng thái | Cột O "Duyệt thủ công" |
| Production (kể cả bot-pipeline giao) | 01_Tasks | Dòng *-DRAFT của chủ đề mình được giao; chuyển sang Review kèm link bản nháp khi nộp QA | Dòng của người khác; không tự tạo DRAFT cho chủ đề chưa đủ cổng duyệt |
| Production | 10_Media_Sources | Dòng media đã chọn cho video mình dựng | Dòng của video khác |
| Kỹ thuật QA | 01_Tasks | Kết quả QA / trạng thái của video mình duyệt | Dòng của người khác |
| Kỹ thuật QA | 08_Publish_Tracking | Link video, cột I, cột J của video mình duyệt (xem tab 08) | Cột I/J của video mình không duyệt |
| Kỹ thuật QA | 11_QA_Log, 12_Repo_Updates | Dòng log QA và đề xuất cập nhật repo của mình | — |
| Bot-pipeline | 01_Tasks | Dòng *-DRAFT trạng thái Assigned cho chủ đề đã đủ cổng duyệt | Chủ đề chưa đủ cổng duyệt |

Quy tắc chung cho mọi tab: không ghi đè, không xóa dòng đã có; ai cũng chỉ
ghi đúng tab và cột của mình trong bảng trên.

## Tabs và cột (hàng 1 = tiêu đề, đúng thứ tự)

### 00_Dashboard
Mục | Nội dung
COO cập nhật cuối ngày: việc đang chạy, việc tắc, việc cần CEO.

### 01_Tasks — nguồn sự thật duy nhất
ID | Việc | Định nghĩa xong | Chủ sở hữu | Người kiểm tra | Ưu tiên | Trạng thái | Deadline | Link kết quả | Blocker | Cần CEO? | Hoàn thành? | Ngày hoàn thành | Cờ khôi phục | Tài khoản Muse nhận việc (email) | Thời gian hoàn thành | Nhiệm vụ đã thực hiện (báo cáo qua Sheet)
Trạng thái dùng thực tế: Assigned, Review, Duyệt (dữ liệu cũ có ghi "Duyet").
Mỗi video có một dòng *-DRAFT khi được giao; dòng DRAFT chuyển Review khi
nộp QA, Duyệt khi QA duyệt kèm link Drive thật.
Quy tắc ghi: xem Bảng phân quyền ghi Sheet ở đầu spec (ai ghi tab nào,
cột nào); bàn giao phải có link kết quả trong Sheet.
CEO giao việc chính qua Sheet cho COO, COO tự phân việc chi tiết, CEO chỉ
theo dõi kết quả hoàn thành (lệnh CEO 04/11/2026, rút gọn):
- CEO chỉ ghi việc chính ở tab 13_COO_Tasks, không ghi chi tiết: cột B email nhận việc, cột C Việc chính, cột A ID để trống. Ví dụ:
CEO ghi dòng cho tài khoản abc@domail.com "Đổi lịch sản xuất video 6 giờ
sáng thành 8 giờ sáng" — chỉ vậy thôi, COO sẽ tự ghi ID khi nhận việc. Cột "Ngày CEO giao" đã bỏ hẳn ngày 05/11/2026 theo lệnh CEO.
- Mỗi ngày, COO đọc tab 13_COO_Tasks đúng 1 lần lúc 06:00 +07 (đầu ca, lệnh
CEO 05/11/2026): việc CEO giao sau 06:00 sẽ được đọc vào 06:00 sáng hôm
sau. Chỉ đọc dòng chưa hoàn thành: cột B = email của mình VÀ cột E Trạng
thái chưa phải "Hoàn thành" VÀ cột G Thời gian hoàn thành còn trống.
Dòng đã E = "Hoàn thành" + có G thì bỏ qua. Chữ ký định danh (lệnh CEO 05/11/2026): cột B được đối chiếu với email khai báo đã lưu trong bộ nhớ của chính tài khoản Muse đó, không đối chiếu bằng email đăng nhập hệ thống (hệ thống không cho agent đọc email này). Tài khoản mới clone repo về phải khai báo email và lưu vào bộ nhớ của mình trước ca quét đầu tiên, tên COO chính là email khai báo đó; chưa có email khai báo thì không nhận dòng tab 13 nào, phải báo về chat chính để CEO khai báo. Cột E chỉ dùng 4 giá trị:
Assigned / Đang làm / Hoàn thành / Tắc; COO chuyển sang "Đang làm" ngay
khi ghi ID. Cột F Deadline do COO điền khi nhận việc, luôn dạng YYYY-MM-DD HH:MM +07 (chuẩn hóa 05/11/2026, lựa chọn 7A — không dùng dạng ngày thuần). Ngày
trong ID COO-YYYYMMDD-NN lấy theo ngày COO đọc/nhận (không còn cột ngày giao); số thứ tự NN tính theo ngày COO đọc/nhận; ID chỉ duy nhất trong phạm vi một tài khoản Muse + email
cột B. "Blocked" không phải giá trị cột E tab 13 — E chỉ dùng 4 giá trị trên; nếu cần ghi tắc ở nơi khác thì chỉ dùng "Blocked" cho 01_Tasks/00_Dashboard, không ghi vào E tab 13.
- COO tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID 01_Tasks nào
nếu có), tự giao cho các phòng qua chat, tự theo dõi ở 01_Tasks. CEO
không cần đọc 01_Tasks, không cần đọc chi tiết phân việc.
- COO báo cáo qua Sheet trên cùng dòng tab 13: E = Hoàn thành, G = thời
gian hoàn thành dạng "YYYY-MM-DD HH:MM +07", H = Kết quả hoàn thành (viết
ngắn + link bằng chứng nếu có, chỉ khi tắc mới ghi "cần CEO" trong này).
CEO chỉ cần đọc E, G, H ở tab 13 là biết việc xong chưa, kết quả gì.
Thiếu E, G hoặc H thì chưa tính là báo cáo xong.

### 02_Agents
Tên Muse | Vai trò | Phạm vi được quyết | Phạm vi KHÔNG được quyết | Chat / kênh | Ca cập nhật | Cờ khôi phục
Vai trò hiện tại (lệnh CEO 04/11/2026): Chat chính là kênh CEO giao nhiệm vụ trực tiếp; agent ở chat chính là điều phối viên, tự động điều phối nhiệm vụ đến đúng phòng liên quan, theo dõi, tổng hợp kết quả và báo cáo lại cho CEO ở chat chính. Các phòng: COO (chat riêng, điều phối vận hành) + 5 phòng (Scout-Báo, Scout-Group, Scoring, Sản xuất, Kỹ thuật QA), mỗi phòng một chat; 2 chat Scout dùng chung skill media-scout. Một nhiệm vụ = một chủ sở hữu duy nhất, khóa bằng dòng Assigned / *-DRAFT trước khi làm; cấm chạy song song cùng nhiệm vụ ở chat chính và phòng ban (bài học vụ trùng TOPIC-219 ngày 04/11/2026).
Ba kênh giao việc duy nhất — ngoài 3 kênh này, không kênh nào khác được
giao việc sản xuất:
1. Chat chính — CEO giao trực tiếp (lệnh trực tiếp, ưu tiên cao nhất).
2. Lịch bot đã được CEO duyệt — kể cả bot-pipeline (xem
   `company-os/bot-sop.md`).
3. COO qua tab 13_COO_Tasks — COO giao cho phòng qua chat, từ dòng lệnh
   CEO ở tab 13 (xem tab 13_COO_Tasks và skill media-coo).
Cổng duyệt là duy nhất, không có ngoại lệ vượt cổng (lệnh CEO 05/11/2026, mục B16, phương án B — bãi bỏ ngoại lệ vượt cổng của A33/9A): chủ đề chỉ được sản xuất khi đủ cả ba điều kiện — Trạng thái Approved VÀ cột O = "Duyệt" VÀ chưa có dòng *-DRAFT nào trong 01_Tasks. Cách duy nhất để cột O thành "Duyệt" là chính CEO tự đổi trên Sheet; ghi "vượt cổng O" trong lệnh chat, trong dòng tab 13 hay ở bất cứ đâu khác đều KHÔNG mở cổng. Lệnh trực tiếp cho chủ đề chưa đủ cổng thì chờ CEO đổi O trên Sheet trước, rồi mới giao/dựng. Lệnh trực tiếp không miễn QA, không miễn ghi rõ nguồn.
Ngoại lệ CEO → COO qua Sheet (lệnh CEO 04/11/2026, xem tab 13_COO_Tasks): CEO chỉ giao việc chính, không cần chat trực tiếp, bằng dòng ở tab 13_COO_Tasks có cột B là email tài khoản Muse nhận việc. COO đọc tab 13 đúng 1 lần lúc 06:00 +07 mỗi ngày, chỉ nhận dòng chưa hoàn thành có cột B = email của mình, cột E chưa phải "Hoàn thành" và cột G còn trống, tự phân việc chi tiết và giao cho các phòng qua chat, rồi báo cáo hoàn thành lại qua Sheet trên cùng dòng, đủ E = Hoàn thành + G + H của tab 13. CEO chỉ theo dõi kết quả hoàn thành ở tab 13. Trong đường này, lệnh của COO cho phòng chức năng có nguồn gốc từ lệnh CEO qua Sheet nên phòng tuân theo, không phải là phòng tự phát sinh việc.

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
đánh dấu "Duyệt", chỉ CEO đổi cột này. Ngoại lệ lệnh trực tiếp: xem
§02_Agents (không chép lại điều kiện ở đây).

### 07_Affiliate_Products
Mã | Sản phẩm | Link affiliate | Hoa hồng | Trạng thái | Ghi chú
Tab thuộc công ty khác (đăng tải/affiliate/doanh thu); giữ tab để dữ liệu
không mất.

### 08_Publish_Tracking
ID Video | Tiêu đề / Chủ đề | Nền tảng | Ngày đăng | Link video | Trạng thái | MD5 | Cờ khôi phục | Người sản xuất (email tài khoản Muse) | Hạn mức còn lại (Muse tuần + hạn mức khác)
QA tải video đã duyệt lên thư mục Drive "Video Muse" ngay trong lượt duyệt
và ghi link thật vào đây + 01_Tasks; không bịa link, không tự tạo thư mục khác, không tự thay đổi quyền thư mục (thư mục "Video Muse" đã được CEO cấp quyền anyone with link ngày 05/11/2026).
**Thẻ phê duyệt upload Drive hết hạn sau 30 phút (lệnh CEO 05/11/2026, tiền lệ TOPIC-232):** lệnh upload lên Drive hiện thẻ phê duyệt, chỉ cho 30 phút để bấm; hết 30 phút không có quyết định thì thẻ tự hết hạn (approval_expired / Timed out), thao tác không chạy, file không lên Drive. Tiền lệ: thẻ gửi 10:52:57 +07, hết hạn 11:22:57 +07, Timed out 11:23:02 +07 — không phải bị từ chối, không phải file hỏng hay thư mục sai quyền. Cách xử lý đúng là **chạy lại upload một lần để hệ thống cấp thẻ mới** (không tính là "thử lại ẩu"); cấp phép toàn quyền của CEO cho QA hoàn tất bàn giao mà không hỏi lại trong chat **không tắt được thẻ hệ thống** — thẻ vẫn hiện mỗi lần upload, cần bấm trong 30 phút; upload Drive không có standing Allow. **Khi gặp thẻ hết hạn, QA phải báo ngay cho COO; COO ghi lại thông báo tình trạng vào cột H "Kết quả hoàn thành" của dòng tab 13 tương ứng (ghi tạm thời trong khi nhiệm vụ vẫn ở "Đang làm", cột G thời gian hoàn thành vẫn để trống), để CEO đọc tab 13 là biết vấn đề ở đâu, không phải chờ tới khi xong mới biết. Khi nhiệm vụ hoàn thành sau đó, COO cập nhật lại cột H bằng kết quả cuối cùng kèm link. Quy tắc này khác với 429/403/rate-limit: gặp 429/403 thì dừng nhánh, ghi blocker, không thử lại.**
Ký nhận + hạn mức (lệnh CEO 04/11/2026, áp từ video bàn giao sau ngày này;
video cũ đã bàn giao trước đó để trống 2 cột mới, không điền ngược số liệu
đoán): ngay sau bước upload Drive và ghi link vào Sheet, cùng dòng đó phải
điền đủ 2 cột mới, không được để trống rồi bàn giao:
- Cột I "Người sản xuất (email tài khoản Muse)": **Quy tắc thống nhất cột I — email người sản xuất (lệnh CEO 05/11/2026, đính chính TOPIC-232, áp cho cả QA và COO, không hỏi lại CEO khi đã có email khai báo):** email tài khoản Muse của người sản xuất = email khai báo đã lưu trong bộ nhớ của tài khoản Muse này. Tất cả các phòng trong hệ thống chat này (chat chính, COO, Sản xuất, QA, Scoring, Scout) cùng chạy trên một tài khoản Muse, nên email khai báo đó là email chung cho mọi phòng — dùng email khai báo này cho cột I KHÔNG phải là "lấy email tài khoản khác thay thế". Thứ tự lấy email: (1) email Production ghi ở cột O 01_Tasks của dòng *-DRAFT, nếu có; (2) nếu bàn giao ghi "chưa xác định" thì lấy email khai báo trong bộ nhớ của tài khoản này, không hỏi lại CEO; (3) chỉ khi bộ nhớ cũng chưa có email khai báo nào thì mới ghi "chưa xác định — hỏi CEO" và lúc đó mới hỏi CEO. Luật xử lý lệch (lệnh CEO 05/11/2026, lựa chọn A19): email khai báo thắng — email bàn giao chỉ dùng khi khớp với email khai báo trong bộ nhớ; nếu email bàn giao khác email khai báo (gõ sai hoặc video do tài khoản khác làm), QA ghi cột I bằng email khai báo và báo cho COO biết có lệch (ghi rõ email bàn giao là gì, email khai báo là gì) để COO kiểm tra; không hỏi lại CEO khi lệch. Cấm bịa email, cấm dùng email Facebook/GitHub noreply hay email dịch vụ khác thay thế. Email khai báo là khai báo, không phải xác thực hệ thống.
- Cột J "Hạn mức còn lại (Muse tuần + hạn mức khác)": chỉ ghi thông tin
chi tiết bằng chữ vào ô này, KHÔNG chụp ảnh màn hình, không đính kèm ảnh.
Ghi đúng tại thời điểm bàn giao — mốc là lúc upload Drive, và người đọc số là QA tự đọc lại hạn mức tại thời điểm upload (sửa 05/11/2026, lựa chọn 8A) — định dạng: "Muse tuần đã dùng X%, còn Y%,
reset <ngày> lúc <giờ> +07; <hạn mức khác> còn <số>;" — vd "Muse tuần đã dùng
10%, còn 90%, reset 9/11 lúc 14:14 +07; token thêm còn 1B". Muse báo mức
dùng theo hạn mức gói, không phải số token tuyệt đối, nên ghi đúng dạng
phần trăm + reset mà công cụ trạng thái gói trả về. "Hạn mức khác" là mọi
hạn mức khác đã dùng trong lần sản xuất đó mà đọc được (vd dung lượng
Drive còn lại, hạn mức tạo ảnh/video/TTS nếu có) — ghi từng loại một bằng
chữ, loại nào không đọc được thì ghi "không đọc được" kèm ngày giờ, loại
nào không áp dụng thì ghi "không áp dụng", tuyệt đối không bịa con số.
Cột này là bản ghi chữ tại thời điểm bàn giao, không cập nhật ngược sau
đó khi hạn mức thay đổi. Thông tin hạn mức Production ghi lúc sản xuất chỉ là tham khảo, không được sao sang cột J thay cho số QA tự đọc lúc upload.

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

### 13_COO_Tasks — tab nhiệm vụ riêng cho COO, rút gọn còn 8 cột (lệnh CEO 04/11/2026, bỏ cột "Ngày CEO giao" ngày 05/11/2026)
ID (COO tự ghi, CEO để trống) | Tài khoản Muse nhận việc (email) | Việc chính (CEO giao) | Phân việc chi tiết (COO tự phân) | Trạng thái | Deadline | Thời gian hoàn thành | Kết quả hoàn thành
Tab này được tách riêng vì 01_Tasks đã hàng trăm dòng, COO không quản lý
nổi nếu lệnh CEO → COO nằm lẫn trong đó. Tab 13 chỉ chứa lệnh CEO giao
cho COO, không chứa hàng trăm dòng video của các phòng.
- CEO chỉ điền 2 ô: email nhận việc (cột B) và Việc chính (cột C). Cột ID
(cột A) CEO để trống, không cần tự nghĩ mã. Không ghi chi tiết, không phân phòng,
không ghi link hay blocker. Ví dụ: "Đổi lịch sản xuất video 6 giờ sáng
thành 8 giờ sáng". Cột "Ngày CEO giao" đã bị bỏ hẳn ngày 05/11/2026 theo lệnh CEO — giao việc thì thực hiện, không cần ngày giao để làm gì; ngày trong ID lấy theo ngày COO đọc/nhận (xem dưới).
- COO tự ghi ID khi nhận việc lần đầu, trước khi phân việc: dạng
COO-YYYYMMDD-NN, vd COO-20261105-01, COO-20261105-02, số thứ tự trong
ngày COO đọc/nhận của tài khoản đó, không trùng. Ngày trong ID lấy theo ngày COO đọc/nhận, không lấy theo ngày CEO giao (không còn cột ngày giao). Từ lúc đó trở đi, mọi nhắc tới nhiệm
vụ đó đều dùng mã này.
- COO đọc: mỗi ngày đúng 1 lần lúc 06:00 +07 đầu ca (lệnh CEO 05/11/2026), chỉ
đọc dòng chưa hoàn thành có cột B =
email của mình (đối chiếu bằng email khai báo trong bộ nhớ), cột E chưa phải "Hoàn thành" và cột G còn trống. Việc CEO giao sau 06:00
được đọc vào 06:00 hôm sau. Dòng email khác thì bỏ
qua. Dòng đã E = "Hoàn thành" + có Thời gian hoàn thành thì bỏ qua.
- Ngoại lệ quét ngoài 06:00 (lệnh CEO 05/11/2026, mục A32): CEO có thể ra lệnh quét ngoại lệ ngoài 06:00 bằng lệnh trực tiếp ở chat chính; lần quét đó vẫn theo đủ các điều kiện nhận dòng (cột B = email khai báo của mình, cột E chưa "Hoàn thành", cột G còn trống). Ngoài lệnh trực tiếp của CEO, COO không tự quét thêm lần nào trong ngày.
- COO làm: tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID 01_Tasks
nào nếu có), giao cho phòng qua chat, tự theo dõi ở 01_Tasks. 01_Tasks
vẫn là nơi theo dõi video và các phòng; tab 13 không thay thế 01_Tasks.
- CEO chỉ theo dõi kết quả: đọc cột E, G, H ở tab 13 là đủ. COO báo cáo
trên cùng dòng: E = Hoàn thành, G = thời gian hoàn thành dạng
"YYYY-MM-DD HH:MM +07", H = Kết quả hoàn thành (viết ngắn + link bằng
chứng nếu có, chỉ khi tắc mới ghi "cần CEO" trong này). Thiếu E, G hoặc H
thì chưa tính là xong. Cột F Deadline do COO điền khi nhận việc, luôn dạng YYYY-MM-DD HH:MM +07. Cột E chỉ dùng 4 giá trị Assigned / Đang làm / Hoàn thành / Tắc; "Blocked" không phải giá trị cột E tab 13 (nếu cần ghi tắc ở nơi khác thì chỉ dùng cho 01_Tasks/00_Dashboard, không ghi vào E tab 13).

## Quy tắc leo thang lên CEO
Chỉ leo thang khi: chi tiền, cam kết bên ngoài, thay đổi không đảo ngược,
pháp lý, tắc > 24h, xung đột giữa 2 nhân viên, vượt ngân sách.
Còn lại COO tự quyết và ghi vào Decisions để CEO xem sau.
