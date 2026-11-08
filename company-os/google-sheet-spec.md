# Bảng điều phối — Công ty 1 người

Workbook: Video HQ — Trụ sở Muse (spreadsheetId `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`)

Tạo mới từ spec này thì tạo đủ 5 tab dưới đây với đúng tên tab và đúng
hàng tiêu đề, kèm dropdown validation cho TOPICS.K, TASKS.C, QA_LOG.D,
COO_TASKS.E; dữ liệu bắt đầu trống. Cùng tài khoản thì dùng tiếp workbook
đang chạy, không tạo mới, không ghi đè. Workbook cũ "HQ - Công ty 1 người"
(`1P6DumLF_eIXmo7h8Qrpk-rpVy7xmqtf5ztVIFsiXZ3I`) chỉ đọc — dữ liệu cũ còn
trong đó và trong snapshot 07/11/2026. Tuyệt đối không dùng lệnh Drive
ghi đè lên file Google Sheet (Drive thay toàn bộ file, mất các tab khác);
sửa từng ô qua Sheets API.

Các tab cũ đã bỏ khỏi Sheet mới (thiết kế lại 07/11/2026): 00_Dashboard,
02_Agents, 03_SOP, 05_Weekly Report, 07_Affiliate_Products, 09_Skills,
10_Media_Sources, 12_Repo_Updates. SOP thật là 4 skill files +
bot-sop.md, không sống trong Sheet. Hồ sơ media thật là `broll-plan.json`
trong từng project (trường `mediaSource`); QA đọc plan trực tiếp, không
còn tab Media_Sources. Log thay đổi template/code sống ở nhật ký ngày +
`TEMPLATE_VERSIONS.md` + thư mục template-audit.

## Bảng phân quyền ghi Sheet (chuẩn duy nhất cho luật Sheet — các file khác chỉ trỏ tới đây, không chép lại)

| Ai ghi | Tab mới | Cột / dòng được ghi | Không được ghi |
|---|---|---|---|
| CEO | COO_TASKS | Chỉ 2 ô: B email nhận việc, C Việc chính (cột A để trống) | Cột A (ID), E, F, G, H |
| CEO | TOPICS | Cột A TOPIC_ID (tự nhập khi duyệt/lật READY, bằng công cụ riêng bên ngoài, đảm bảo không trùng ID) + cột K STATUS — chỉ flip APPROVED → READY | Điểm E–I, J TOTAL |
| CEO | DECISIONS | Cột A DECISION_ID, B ISSUE, C OPTION_A, D OPTION_B (ghi qua chat chính khi ghi nhận quyết định) + cột F "Quyết định của CEO", G "Ngày quyết" | — |
| COO | DECISIONS | Chỉ cột E "Đề xuất của COO" | Cột F quyết định của CEO |
| COO | COO_TASKS | A (ID), D, E, F, G, H — chỉ dòng có cột B = email khai báo của mình | Dòng có cột B là email khác |
| COO | TASKS | Chỉ theo dõi tiến độ; ghi C = BLOCKED/CANCELLED + M BLOCKER khi tắc/huỷ | Không ghi đè, không xóa dòng đã có, không tự tạo dòng CLAIMED thay Pipeline/Production |
| Scout (Báo + Group) | TOPICS | Dòng chủ đề mới: B–I điểm + K STATUS (kết quả chấm) + L + M; cột A TOPIC_ID ĐỂ TRỐNG khi ghi mới (quyết CEO 07/11/2026, phương án E cho R4-04 — Scout không tự sinh ID) | Cột A TOPIC_ID; không flip READY |
| Production | TASKS | Dòng CLAIMED của chủ đề mình được giao; C BUILDING/REVIEW, E DRAFT_LINK, K PROD_NOTES | Dòng của người khác; không tự tạo CLAIMED cho chủ đề chưa READY |
| Kỹ thuật QA | TASKS | F QA_VERDICT, G RETURNS, H DRIVE_LINK, I MD5, C RETURNED/APPROVED/DELIVERED, L QUOTA (ký nhận + hạn mức lúc upload) | Dòng của video mình không duyệt |
| Kỹ thuật QA | QA_LOG | Dòng verdict mới của mình (append-only) | Không sửa/xoá dòng log đã có |
| Pipeline (bot) | TASKS | Dòng CLAIMED mới cho chủ đề READY (A–D + J) + N DUP_NOTE khi trùng CLAIMED | Chủ đề chưa READY |

Quy tắc chung cho mọi tab: không ghi đè, không xóa dòng đã có; ai cũng chỉ
ghi đúng tab và cột của mình trong bảng trên. Luật chống đua: R1 tham
chiếu bằng TOPIC_ID khi đã có; chủ đề chưa có ID thì tham chiếu tạm bằng
tiêu đề, không bao giờ bằng số dòng; R3 đọc lại theo ID ngay trước khi ghi
(claim-then-verify); R7 chỉ đọc số dòng + ID lớn nhất (chỉ tính dòng đã có ID) để nắm trạng thái hiện tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất lùi KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026: làm việc bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab BASELINE hay file baseline.json. ID
trống là bình thường, không phải lỗi.

**C/J/D nhiều người viết — ghi sau thắng + để lại lý do (quyết CEO 07/11/2026, R4-10 phương án C):** TASKS.C STATUS có 3 người viết (Production: CLAIMED/BUILDING/REVIEW; QA: RETURNED/APPROVED/DELIVERED; COO: BLOCKED/CANCELLED), TASKS.J UPDATED_AT có 2 người viết (Production, QA), TASKS.D ASSIGNEE có 2 người viết (Production lúc claim, COO lúc giao qua COO_TASKS) — đây là ngoại lệ có chủ đích của R2, KHÔNG viết lại bảng theo 'một cột một người viết theo trạng thái' và KHÔNG sửa R2 thành 'tại một thời điểm'. Khi xung đột (vd video đang REVIEW: QA ghi C=APPROVED trong khi COO ghi C=BLOCKED), chấp nhận **ghi sau thắng** (last write wins) — lần ghi sau thắng, không có quy tắc ai thắng theo vai trò. Bù lại, ai ghi TASKS.C thì TRONG CÙNG LẦN GHI đó phải ghi thêm lý do + thời gian vào cột ghi chú của mình, để lần ghi sau còn lần ra được: Production → K PROD_NOTES (lý do + thời gian khi ghi C=CLAIMED/BUILDING/REVIEW); QA → QA_LOG cột E ISSUES ghi lý do + TASKS.F QA_VERDICT (RETURNED/APPROVED/DELIVERED; DELIVERED ghi thêm ký nhận + hạn mức vào L QUOTA như cũ, QA không ghi K); COO → M BLOCKER (lý do + thời gian khi ghi C=BLOCKED/CANCELLED); Pipeline (khi ghi C=CLAIMED lúc nhận lô) → lý do là ca nhận lô, ghi vào báo cáo ca (liệt kê TOPIC_ID đã nhận + giờ nhận); khi dừng vì trùng CLAIMED thì ghi N DUP_NOTE như luật A3/R4-05.

## §02 — Cổng sản xuất (READY) — duy nhất, không có ngoại lệ

Chủ đề chỉ được sản xuất khi đồng thời:
1. TOPICS.STATUS = READY (CEO flip 1 ô TOPICS.K từ APPROVED → READY) VÀ TOPIC_ID đã có (không trống);
2. Chưa có dòng TASKS nào cho TOPIC_ID đó.

TASKS là nguồn duy nhất (quyết CEO 07/11/2026, R4-11 phương án B): không kiểm tra thư mục projects hay tiến trình máy — video đang làm/chờ QA đều thể hiện bằng dòng TASKS (CLAIMED/BUILDING/REVIEW/RETURNED, trong đó REVIEW là chờ QA). Hạn chế đã chấp nhận: TASKS không thấy trạng thái render/TTS trên máy nếu project chưa ghi TASKS.

TOPIC_ID (cột A) ĐỂ TRỐNG khi Scout ghi chủ đề mới; chỉ khi CEO duyệt
(lật STATUS sang READY) thì CEO TỰ NHẬP TOPIC_ID bằng công cụ riêng bên
ngoài, đảm bảo không trùng ID (quyết CEO 07/11/2026, phương án E cho
R4-04). Chủ đề không duyệt thì TOPIC_ID tiếp tục bỏ trống. Các ID cũ
(TOPIC-001…TOPIC-289) giữ nguyên, không viết lại. Dòng READY mà TOPIC_ID
trống thì pipeline BỎ QUA (không claim được vì TASKS cần TOPIC_ID) và
ghi vào báo cáo ca để CEO nhập ID.

Điểm (E–I) và TOTAL (J) chỉ là THAM KHẢO cho quyết định của CEO — điểm
không chặn sản xuất, không phải cổng. Chỉ trạng thái READY mới quyết
định có sản xuất video hay không.

Không có ngoại lệ vượt cổng. Cách duy nhất để có READY là CEO tự flip
trên Sheet; ghi "vượt cổng" trong lệnh chat, trong dòng COO_TASKS hay ở
bất cứ đâu khác đều KHÔNG mở cổng. Lệnh trực tiếp cho chủ đề chưa đủ cổng
thì chờ CEO flip READY trên Sheet trước, rồi mới giao/dựng. Lệnh trực
tiếp không miễn QA, không miễn ghi rõ nguồn.

## Quy tắc điều phối từ Chat chính (lệnh CEO 04/11/2026, sau vụ trùng TOPIC-219)

Chat chính là kênh CEO giao nhiệm vụ trực tiếp; agent ở chat chính là
điều phối viên, tự động điều phối nhiệm vụ đến đúng phòng liên quan,
theo dõi, tổng hợp kết quả và báo cáo lại cho CEO ở chat chính. Một
nhiệm vụ = một chủ sở hữu duy nhất, khóa bằng dòng TASKS STATUS =
CLAIMED (ASSIGNEE = email khai báo) trước khi làm; cấm chạy song song
cùng nhiệm vụ ở chat chính và phòng ban. Phòng ban chỉ làm nhiệm vụ khi
được giao cụ thể từ chat chính (hoặc từ lịch bot đã được CEO duyệt, hoặc
từ COO qua tab COO_TASKS), không tự phát sinh nhiệm vụ sản xuất mới chỉ
vì đọc Sheet hay lịch sử fork. Quy tắc đầy đủ: xem BOOTSTRAP §8.

Ba kênh giao việc duy nhất — ngoài 3 kênh này, không kênh nào khác được
giao việc sản xuất:
1. Chat chính — CEO giao trực tiếp (lệnh trực tiếp, ưu tiên cao nhất).
2. Lịch bot đã được CEO duyệt — kể cả Pipeline (xem
   `company-os/bot-sop.md`).
3. COO qua tab COO_TASKS — COO giao cho phòng qua chat, từ dòng lệnh
   CEO ở tab COO_TASKS (xem mục COO_TASKS và skill media-coo).

## Tabs và cột (hàng 1 = tiêu đề, đúng thứ tự)

### TOPICS
TOPIC_ID | TITLE | SOURCE | DISCOVERED | HOT (30) | AUDIENCE (20) | FRESH (20) | FEASIBLE (15) | SOURCED (15) | TOTAL (100) | STATUS | ANGLE | NOTES
Thang điểm: Hot 30 + Khán giả 20 + Mới 20 + Khả thi 15 + Rõ nguồn 15
= 100; điểm quan tâm (Hot + Khán giả) xét trước tổng: ≥70 và quan tâm
≥30 → APPROVED; 50–69 → HOLD; ≥70 nhưng quan tâm <30 → HOLD; <50 →
REJECTED; trùng = DUPLICATE + tiêu đề (và ID nếu có) của chủ đề gốc vào
NOTES. Điểm quan tâm bắt buộc có số liệu bằng chứng trong NOTES. Scout
chấm ngay lúc ghi (không còn hàng chờ chấm điểm, không còn phòng Scoring
riêng).
Điểm (E–I) và TOTAL (J) chỉ là THAM KHẢO cho quyết định của CEO (quyết
CEO 07/11/2026, phương án E cho R4-04) — điểm không chặn sản xuất, không
phải cổng; chỉ READY mới quyết định sản xuất. TOPIC_ID (cột A) ĐỂ TRỐNG
khi Scout ghi chủ đề mới; chỉ CEO nhập khi duyệt (lật READY), bằng công
cụ riêng bên ngoài, đảm bảo không trùng. Chủ đề không duyệt thì tiếp tục
bỏ trống. Khử trùng chủ đề chưa duyệt theo tiêu đề/sự kiện (chưa có ID
nên không khử trùng theo TOPIC_ID được); chủ đề đã có ID thì đối chiếu
thêm theo ID.

### TASKS — nguồn sự thật duy nhất
TOPIC_ID | TITLE | STATUS | ASSIGNEE | DRAFT_LINK | QA_VERDICT | RETURNS | DRIVE_LINK | MD5 | UPDATED_AT | PROD_NOTES | QUOTA | BLOCKER | DUP_NOTE
Máy trạng thái: CLAIMED → BUILDING → REVIEW ↔ RETURNED → APPROVED →
DELIVERED; + BLOCKED / CANCELLED. Mỗi video có một dòng TASKS khi được
giao (STATUS = CLAIMED, ASSIGNEE = email khai báo); dòng chuyển BUILDING
khi Production bắt đầu, REVIEW khi nộp QA (E DRAFT_LINK), RETURNED khi
QA trả lại (F QA_VERDICT, G RETURNS tăng 1), APPROVED khi QA duyệt,
DELIVERED khi đã có H DRIVE_LINK + I MD5 thật. BLOCKED: video tắc —
dừng hàng đợi pipeline cho đến khi COO gỡ tắc hoặc hủy (CANCELLED).
**Nhận theo lô (quyết CEO 08/11/2026, T3 phương án B):** mỗi ca nhận 1 lần tối đa 5 chủ đề READY mới (theo thứ tự Sheet), không trừ số video đang làm dở trong ngày; tổng số video đang làm cùng lúc có thể vượt 5. Video đang làm dở từ NGÀY CŨ thì bỏ qua theo quy tắc ngày hiện tại.
Quy tắc ghi: xem Bảng phân quyền ghi Sheet ở đầu spec (ai ghi tab nào,
cột nào); bàn giao phải có link kết quả trong Sheet.
QA tải video đã duyệt lên thư mục Drive "Video Muse" ngay trong lượt duyệt
và ghi link thật vào đây (H DRIVE_LINK + I MD5, STATUS = DELIVERED) +
ghi verdict vào QA_LOG; không bịa link, không tự tạo thư mục khác, không
tự thay đổi quyền thư mục (thư mục "Video Muse" đã được CEO cấp quyền
anyone with link ngày 05/11/2026).
**Thẻ phê duyệt upload Drive hết hạn sau 30 phút (lệnh CEO 05/11/2026, tiền lệ TOPIC-232):** lệnh upload lên Drive hiện thẻ phê duyệt, chỉ cho 30 phút để bấm; hết 30 phút không có quyết định thì thẻ tự hết hạn (approval_expired / Timed out), thao tác không chạy, file không lên Drive. Tiền lệ: thẻ gửi 10:52:57 +07, hết hạn 11:22:57 +07, Timed out 11:23:02 +07 — không phải bị từ chối, không phải file hỏng hay thư mục sai quyền. Cách xử lý đúng là **chạy lại upload một lần để hệ thống cấp thẻ mới** (không tính là "thử lại ẩu"); cấp phép toàn quyền của CEO cho QA hoàn tất bàn giao mà không hỏi lại trong chat **không tắt được thẻ hệ thống** — thẻ vẫn hiện mỗi lần upload, cần bấm trong 30 phút; upload Drive không có standing Allow. **Khi gặp thẻ hết hạn, QA phải báo ngay cho COO; COO ghi lại thông báo tình trạng vào cột H "Kết quả hoàn thành" của dòng COO_TASKS tương ứng (ghi tạm thời trong khi nhiệm vụ vẫn ở "Đang làm", cột G thời gian hoàn thành vẫn để trống), để CEO đọc tab COO_TASKS là biết vấn đề ở đâu, không phải chờ tới khi xong mới biết. Khi nhiệm vụ hoàn thành sau đó, COO cập nhật lại cột H bằng kết quả cuối cùng kèm link. Quy tắc này khác với 429/403/rate-limit: gặp 429/403 thì dừng nhánh, ghi blocker, không thử lại.**
Ký nhận + hạn mức (lệnh CEO 04/11/2026, áp từ video bàn giao sau ngày này;
video cũ đã bàn giao trước đó để trống, không điền ngược số liệu đoán):
ngay sau bước upload Drive và ghi link vào Sheet, cùng dòng TASKS đó phải
ghi vào L QUOTA đủ 2 thông tin (quyết CEO 07/11/2026, R4-05 — Q1 đã đóng):
- Email người sản xuất (email tài khoản Muse): **Quy tắc thống nhất — email người sản xuất (lệnh CEO 05/11/2026, đính chính TOPIC-232, áp cho cả QA và COO, không hỏi lại CEO khi đã có email khai báo):** email tài khoản Muse của người sản xuất = email khai báo đã lưu trong bộ nhớ của tài khoản Muse này. Tất cả các phòng trong hệ thống chat này (chat chính, COO, Sản xuất, QA, Scout) cùng chạy trên một tài khoản Muse, nên email khai báo đó là email chung cho mọi phòng — dùng email khai báo này cho L QUOTA KHÔNG phải là "lấy email tài khoản khác thay thế". Thứ tự lấy email: (1) email Production ghi ở cột D (ASSIGNEE) của dòng TASKS CLAIMED, nếu có; (2) nếu cột D trống hoặc bàn giao ghi "chưa xác định" thì ghi "chưa xác định — hỏi CEO" và lúc đó hỏi CEO (không tự lấy email khai báo trong bộ nhớ thay thế — quyết CEO 08/11/2026, R4-09 phương án B). Luật xử lý lệch (lệnh CEO 05/11/2026, lựa chọn A19): email khai báo thắng — email bàn giao chỉ dùng khi khớp với email khai báo trong bộ nhớ; nếu email bàn giao khác email khai báo (gõ sai hoặc video do tài khoản khác làm), QA ghi L QUOTA bằng email khai báo và báo cho COO biết có lệch (ghi rõ email bàn giao là gì, email khai báo là gì) để COO kiểm tra; không hỏi lại CEO khi lệch. Cấm bịa email, cấm dùng email Facebook/GitHub noreply hay email dịch vụ khác thay thế. Email khai báo là khai báo, không phải xác thực hệ thống.
- Hạn mức còn lại (Muse tuần + hạn mức khác): chỉ ghi thông tin chi tiết
bằng chữ vào L QUOTA, KHÔNG chụp ảnh màn hình, không đính kèm ảnh.
Ghi đúng tại thời điểm bàn giao — mốc là lúc upload Drive, và người đọc số là QA tự đọc lại hạn mức tại thời điểm upload (sửa 05/11/2026, lựa chọn 8A) — định dạng: "Muse tuần đã dùng X%, còn Y%,
reset <ngày> lúc <giờ> +07; <hạn mức khác> còn <số>;" — vd "Muse tuần đã dùng
10%, còn 90%, reset 9/11 lúc 14:14 +07; token thêm còn 1B". Muse báo mức
dùng theo hạn mức gói, không phải số token tuyệt đối, nên ghi đúng dạng
phần trăm + reset mà công cụ trạng thái gói trả về. "Hạn mức khác" là mọi
hạn mức khác đã dùng trong lần sản xuất đó mà đọc được (vd dung lượng
Drive còn lại, hạn mức tạo ảnh/video/TTS nếu có) — ghi từng loại một bằng
chữ, loại nào không đọc được thì ghi "không đọc được" kèm ngày giờ, loại
nào không áp dụng thì ghi "không áp dụng", tuyệt đối không bịa con số.
Thông tin này là bản ghi chữ tại thời điểm bàn giao, không cập nhật ngược sau
đó khi hạn mức thay đổi. Thông tin hạn mức Production ghi lúc sản xuất chỉ là tham khảo, không được sao sang L QUOTA thay cho số QA tự đọc lúc upload.
Thiếu 1 trong 2 thông tin thì chưa tính là bàn giao xong — báo cáo ghi
"chưa xong bước Drive + Sheet".
CEO giao việc chính qua Sheet cho COO, COO tự phân việc chi tiết, CEO chỉ
theo dõi kết quả hoàn thành (lệnh CEO 04/11/2026, rút gọn):
- CEO chỉ ghi việc chính ở tab COO_TASKS, không ghi chi tiết: cột B email nhận việc, cột C Việc chính, cột A ID để trống. Ví dụ:
CEO ghi dòng cho tài khoản abc@domail.com "Đổi lịch sản xuất video 6 giờ
sáng thành 8 giờ sáng" — chỉ vậy thôi, COO sẽ tự ghi ID khi nhận việc. Cột "Ngày CEO giao" đã bỏ hẳn ngày 05/11/2026 theo lệnh CEO.
- Mỗi ngày, COO đọc tab COO_TASKS đúng 1 lần lúc 06:00 +07 (đầu ca, lệnh
CEO 05/11/2026): việc CEO giao sau 06:00 sẽ được đọc vào 06:00 sáng hôm
sau. Chỉ đọc dòng chưa hoàn thành: cột B = email của mình VÀ cột E Trạng
thái chưa phải "Hoàn thành" VÀ cột G Thời gian hoàn thành còn trống.
Dòng đã E = "Hoàn thành" + có G thì bỏ qua. Chữ ký định danh (lệnh CEO 05/11/2026): cột B được đối chiếu với email khai báo đã lưu trong bộ nhớ của chính tài khoản Muse đó, không đối chiếu bằng email đăng nhập hệ thống (hệ thống không cho agent đọc email này). Tài khoản mới clone repo về phải khai báo email và lưu vào bộ nhớ của mình trước ca quét đầu tiên, tên COO chính là email khai báo đó; chưa có email khai báo thì không nhận dòng tab COO_TASKS nào, phải báo về chat chính để CEO khai báo. Cột E chỉ dùng 4 giá trị:
Assigned / Đang làm / Hoàn thành / Tắc; COO chuyển sang "Đang làm" ngay
khi ghi ID. Cột F Deadline do COO điền khi nhận việc, luôn dạng YYYY-MM-DD HH:MM +07 (chuẩn hóa 05/11/2026, lựa chọn 7A — không dùng dạng ngày thuần). Ngày
trong ID COO-YYYYMMDD-NN lấy theo ngày COO đọc/nhận (không còn cột ngày giao); số thứ tự NN tính theo ngày COO đọc/nhận; ID chỉ duy nhất trong phạm vi một tài khoản Muse + email
cột B. "Blocked" không phải giá trị cột E tab COO_TASKS — E chỉ dùng 4 giá trị trên; nếu cần ghi tắc ở nơi khác thì chỉ dùng "Blocked" cho TASKS (C = BLOCKED), không ghi vào E tab COO_TASKS.
- COO tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID TASKS (TOPIC_ID)
nào nếu có), tự giao cho các phòng qua chat, tự theo dõi ở TASKS. CEO
không cần đọc TASKS, không cần đọc chi tiết phân việc.
- COO báo cáo qua Sheet trên cùng dòng tab COO_TASKS: E = Hoàn thành, G = thời
gian hoàn thành dạng "YYYY-MM-DD HH:MM +07", H = Kết quả hoàn thành (viết
ngắn + link bằng chứng nếu có, chỉ khi tắc mới ghi "cần CEO" trong này).
CEO chỉ cần đọc E, G, H ở tab COO_TASKS là biết việc xong chưa, kết quả gì.
Thiếu E, G hoặc H thì chưa tính là báo cáo xong.

### QA_LOG (append-only)
VIDEO_ID | VERSION | DATE | RESULT | ISSUES | REPO_NOTE
RESULT chuẩn hoá bằng dropdown: APPROVED / RETURNED. Append-only (R5):
ghi sai thì ghi dòng đính chính mới, không sửa/xoá dòng log đã có.
Video bị trả 2 lần chưa có verdict Duyệt sau đó thì leo thang lên CEO
một lần.

### DECISIONS — chỉ CEO quyết
DECISION_ID | ISSUE | OPTION_A | OPTION_B | COO_PROPOSAL | CEO_DECISION | DATE

### COO_TASKS — tab nhiệm vụ riêng cho COO, 8 cột (lệnh CEO 04/11/2026, bỏ cột "Ngày CEO giao" ngày 05/11/2026)
ID (COO tự ghi, CEO để trống) | Tài khoản Muse nhận việc (email) | Việc chính (CEO giao) | Phân việc chi tiết (COO tự phân) | Trạng thái | Deadline | Thời gian hoàn thành | Kết quả hoàn thành
Tab này được tách riêng vì TASKS đã hàng trăm dòng, COO không quản lý
nổi nếu lệnh CEO → COO nằm lẫn trong đó. Tab COO_TASKS chỉ chứa lệnh CEO giao
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
- COO làm: tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID TASKS (TOPIC_ID)
nào nếu có), giao cho phòng qua chat, tự theo dõi ở TASKS. TASKS
vẫn là nơi theo dõi video và các phòng; tab COO_TASKS không thay thế TASKS.
- CEO chỉ theo dõi kết quả: đọc cột E, G, H ở tab COO_TASKS là đủ. COO báo cáo
trên cùng dòng: E = Hoàn thành, G = thời gian hoàn thành dạng
"YYYY-MM-DD HH:MM +07", H = Kết quả hoàn thành (viết ngắn + link bằng
chứng nếu có, chỉ khi tắc mới ghi "cần CEO" trong này). Thiếu E, G hoặc H
thì chưa tính là xong. Cột F Deadline do COO điền khi nhận việc, luôn dạng YYYY-MM-DD HH:MM +07. Cột E chỉ dùng 4 giá trị Assigned / Đang làm / Hoàn thành / Tắc; "Blocked" không phải giá trị cột E tab COO_TASKS (nếu cần ghi tắc ở nơi khác thì chỉ dùng cho TASKS (C = BLOCKED), không ghi vào E tab COO_TASKS).
- Ngoại lệ CEO → COO qua Sheet (lệnh CEO 04/11/2026): CEO chỉ giao việc chính, không cần chat trực tiếp, bằng dòng ở tab COO_TASKS có cột B là email tài khoản Muse nhận việc. COO đọc tab COO_TASKS đúng 1 lần lúc 06:00 +07 mỗi ngày, chỉ nhận dòng chưa hoàn thành có cột B = email của mình, cột E chưa phải "Hoàn thành" và cột G còn trống, tự phân việc chi tiết và giao cho các phòng qua chat, rồi báo cáo hoàn thành lại qua Sheet trên cùng dòng, đủ E = Hoàn thành + G + H của tab COO_TASKS. CEO chỉ theo dõi kết quả hoàn thành ở tab COO_TASKS. Trong đường này, lệnh của COO cho phòng chức năng có nguồn gốc từ lệnh CEO qua Sheet nên phòng tuân theo, không phải là phòng tự phát sinh việc.

## Quy tắc leo thang lên CEO
Chỉ leo thang khi: chi tiền, cam kết bên ngoài, thay đổi không đảo ngược,
pháp lý, tắc > 24h, xung đột giữa 2 nhân viên, vượt ngân sách. Video bị
trả ≥ 2 lần chưa có verdict Duyệt sau đó thì leo thang lên CEO một lần
(đếm từ QA_LOG).
Còn lại COO tự quyết và ghi vào DECISIONS để CEO xem sau.
