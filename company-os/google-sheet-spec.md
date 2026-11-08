# Bảng điều phối — Công ty 1 người

Workbook: Video HQ — Trụ sở Muse (spreadsheetId `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`)

Tạo mới từ spec này thì tạo đủ 6 tab dưới đây với đúng tên tab và đúng
hàng tiêu đề, kèm dropdown validation cho TOPICS.K, TASKS.C, QA_LOG.D,
COO_TASKS.E, CEO_REPORTS.H (APPLIED_BY — Sản xuất / Scout / kỹ thuật QA / COO); dữ liệu bắt đầu trống. Cùng tài khoản thì dùng tiếp workbook
đang chạy, không tạo mới, không ghi đè. Workbook cũ "HQ - Công ty 1 người — CŨ (chỉ đọc)"
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
| CEO | COO_TASKS | Chỉ 2 ô: B email nhận việc, C Việc chính (cột A để trống) | Cột A (ID), E, F, G |
| CEO | TOPICS | Cột A TOPIC_ID (tự nhập khi duyệt/lật READY, bằng công cụ riêng bên ngoài, đảm bảo không trùng ID) + cột K STATUS — chỉ flip APPROVED → READY | Điểm E–I, J TOTAL |
| CEO | DECISIONS | Chỉ cột F CEO_DECISION + G DATE | Cột A–E |
| COO | DECISIONS | Cột A DECISION_ID, B ISSUE, C OPTION_A, D OPTION_B (ghi nhận) + E COO_PROPOSAL | Cột F quyết định của CEO |
| COO | COO_TASKS | A (ID), D, E, F, G — chỉ dòng có cột B = email khai báo của mình | Dòng có cột B là email khác |
| CEO | CEO_REPORTS | G CEO_REPLY (ghi quyết định kèm ngày trả lời trong cùng ô G; chỉ ghi khi trả lời trên dòng COO đã gửi) | A–F, H, I |
| COO | CEO_REPORTS | A–F khi gửi báo cáo mới (REPORT_ID, DATE_REPORTED, ASSIGNEE_EMAIL, ISSUE, TRIED, NEEDS_DECISION) | G, H, I |
| Phòng thi hành (Sản xuất / Scout / kỹ thuật QA / COO) | CEO_REPORTS | H APPLIED_BY, I DATE — chỉ ghi khi G CEO_REPLY đã có giá trị (ghi ngay khi đọc, rồi thực thi ngay); phòng nào đọc trước ghi trước, đã có tên thì không ghi đè | A–G |
| COO | TASKS | Chỉ theo dõi tiến độ; ghi C = BLOCKED/CANCELLED + M BLOCKER khi tắc/huỷ; gỡ BLOCKED (về BUILDING/REVIEW) hoặc hủy khi nguyên nhân đã gỡ/không gỡ được — chỉ COO được gỡ/hủy | Không ghi đè, không xóa dòng đã có, không tự tạo dòng CLAIMED thay Pipeline/Production |
| Scout (Báo + Group) | TOPICS | Dòng chủ đề mới: B–I điểm + K STATUS (kết quả chấm) + L + M; cột A TOPIC_ID ĐỂ TRỐNG khi ghi mới (quyết CEO 07/11/2026, phương án E cho R4-04 — Scout không tự sinh ID) | Cột A TOPIC_ID; không flip READY |
| Production | TASKS | Dòng CLAIMED của chủ đề mình được giao; C BUILDING/REVIEW, E DRAFT_LINK, J UPDATED_AT, K PROD_NOTES; C BLOCKED (chỉ lỗi riêng video nhóm 1) + M BLOCKER (lý do bắt buộc) | Dòng của người khác; không tự tạo CLAIMED cho chủ đề chưa READY |
| Kỹ thuật QA | TASKS | F QA_VERDICT, G RETURNS, H DRIVE_LINK, I MD5, J UPDATED_AT, C RETURNED/APPROVED/DELIVERED, L QUOTA (ký nhận + hạn mức lúc upload) | Dòng của video mình không duyệt |
| Kỹ thuật QA | QA_LOG | Dòng verdict mới của mình (append-only) | Không sửa/xoá dòng log đã có |
| Pipeline (bot) | TASKS | Dòng CLAIMED mới cho chủ đề READY (A–D + J) + N DUP_NOTE khi trùng CLAIMED | Chủ đề chưa READY |

Quy tắc chung cho mọi tab: không ghi đè, không xóa dòng đã có; ai cũng chỉ
ghi đúng tab và cột của mình trong bảng trên. Luật chống đua: R1 tham
chiếu bằng TOPIC_ID khi đã có; chủ đề chưa có ID thì tham chiếu tạm bằng
tiêu đề, không bao giờ bằng số dòng; R3 đọc lại theo ID ngay trước khi ghi
(claim-then-verify); R7 chỉ đọc số dòng + ID lớn nhất (chỉ tính dòng đã có ID) để nắm trạng thái hiện tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất lùi KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026: làm việc bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab BASELINE hay file baseline.json. ID
trống là bình thường, không phải lỗi.

**C/J/D nhiều người viết — ghi sau thắng + để lại lý do (quyết CEO 07/11/2026, R4-10 phương án C):** TASKS.C STATUS có 3 người viết (Production: CLAIMED/BUILDING/REVIEW/BLOCKED — chỉ lỗi riêng video nhóm 1, lý do bắt buộc vào M; QA: RETURNED/APPROVED/DELIVERED; COO: BLOCKED/CANCELLED — chỉ COO được gỡ BLOCKED hoặc hủy), TASKS.J UPDATED_AT có 2 người viết (Production, QA), TASKS.D ASSIGNEE có 2 người viết (Production lúc claim, COO lúc giao qua COO_TASKS) — đây là ngoại lệ có chủ đích của R2, KHÔNG viết lại bảng theo 'một cột một người viết theo trạng thái' và KHÔNG sửa R2 thành 'tại một thời điểm'. Khi xung đột (vd video đang REVIEW: QA ghi C=APPROVED trong khi COO ghi C=BLOCKED), chấp nhận **ghi sau thắng** (last write wins) — lần ghi sau thắng, không có quy tắc ai thắng theo vai trò. Bù lại, ai ghi TASKS.C thì TRONG CÙNG LẦN GHI đó phải ghi thêm lý do + thời gian vào cột ghi chú của mình, để lần ghi sau còn lần ra được: Production → K PROD_NOTES (lý do + thời gian khi ghi C=CLAIMED/BUILDING/REVIEW; và M BLOCKER khi ghi C=BLOCKED); QA → QA_LOG cột E ISSUES ghi lý do + TASKS.F QA_VERDICT (RETURNED/APPROVED/DELIVERED; DELIVERED ghi thêm ký nhận + hạn mức vào L QUOTA như cũ, QA không ghi K); COO → M BLOCKER (lý do + thời gian khi ghi C=BLOCKED/CANCELLED); Pipeline (khi ghi C=CLAIMED lúc nhận lô) → lý do là ca nhận lô, ghi vào báo cáo ca (liệt kê TOPIC_ID đã nhận + giờ nhận); khi dừng vì trùng CLAIMED thì ghi N DUP_NOTE như luật A3/R4-05.

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
ghi vào báo cáo ca để COO báo cáo CEO qua CEO_REPORTS nhập ID.

READY đã có dòng TASKS — kể cả DELIVERED — thì pipeline bỏ qua, không claim lại (quyết CEO 09/11/2026, R8-16 phương án B).

Trước khi ghi kết luận 'chưa sản xuất / chờ CEO quyết' về một chủ đề, phải đọc live TASKS + QA_LOG + Drive theo TOPIC_ID và ghi kèm thời điểm kiểm chứng (quyết CEO 09/11/2026, R8-04 phương án A).

Điểm (E–I) và TOTAL (J) chỉ là THAM KHẢO cho quyết định của CEO — điểm
không chặn sản xuất, không phải cổng. Chỉ trạng thái READY mới quyết
định có sản xuất video hay không.

Không có ngoại lệ vượt cổng. Cách duy nhất để có READY là CEO tự flip
trên Sheet; ghi "vượt cổng" trong lệnh chat, trong dòng COO_TASKS hay ở
bất cứ đâu khác đều KHÔNG mở cổng. Lệnh trực tiếp cho chủ đề chưa đủ cổng
thì chờ CEO flip READY trên Sheet trước, rồi mới giao/dựng. Lệnh trực
tiếp không miễn QA, không miễn ghi rõ nguồn.

## Quy tắc điều phối từ Chat chính (lệnh CEO 04/11/2026, sau vụ trùng TOPIC-219)

Chat chính là kênh CEO nhắn tin; agent ở chat chính là điều phối viên
(COO), tự động điều phối nhiệm vụ đến đúng phòng liên quan, theo dõi,
tổng hợp kết quả. Lệnh từ chat chính hay COO đều tính là lệnh của COO
(lệnh CEO 08/11/2026, phương án B). Các phòng chức năng và COO chỉ nhận
lệnh từ CEO duy nhất qua tab CEO_REPORTS. Một nhiệm vụ = một chủ sở hữu
duy nhất, khóa bằng dòng TASKS STATUS = CLAIMED (ASSIGNEE = email khai
báo) trước khi làm; cấm chạy song song cùng nhiệm vụ ở chat chính và
phòng ban. Phòng ban chỉ làm nhiệm vụ khi được giao cụ thể từ chat chính
(hoặc từ lịch bot đã được CEO duyệt, hoặc từ COO qua tab COO_TASKS; lệnh từ chat chính hay COO đều tính là lệnh của COO),
không tự phát sinh nhiệm vụ sản xuất mới chỉ vì đọc Sheet hay lịch sử
fork. Các phòng báo cáo kết quả cho COO; chỉ COO báo cáo với CEO, qua
tab CEO_REPORTS. Quy tắc đầy đủ: xem BOOTSTRAP §8.

Ba kênh giao việc duy nhất — ngoài 3 kênh này, không kênh nào khác được
giao việc sản xuất:
1. Chat chính / COO — lệnh điều phối của COO (tính là lệnh của COO; CEO chỉ ra lệnh qua CEO_REPORTS).
2. Lịch bot đã được CEO duyệt — kể cả Pipeline (xem
   `company-os/bot-sop.md`).
3. COO qua tab COO_TASKS — COO giao cho phòng qua chat, từ dòng lệnh
   CEO ở tab COO_TASKS (xem mục COO_TASKS và skill media-coo).

## Tabs và cột (hàng 1 = tiêu đề, đúng thứ tự)

### TOPICS
TOPIC_ID | TITLE | SOURCE | DISCOVERED | HOT (30) | AUDIENCE (20) | FRESH (20) | FEASIBLE (15) | SOURCED (15) | TOTAL (100) | STATUS | ANGLE | NOTES
Ghi chú: (30)/(20)/… trong dòng header trên là chú thích trọng số thang điểm, không phải chữ header live; header live là HOT | AUDIENCE | FRESH | FEASIBLE | SOURCED | TOTAL, trọng số đầy đủ nằm trong note các cột E–J (0–30 / 0–20 / 0–20 / 0–15 / 0–15, TOTAL =SUM(E:I)).
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
thêm theo ID. Cửa chặn hạn mức tuần (DEC-202): trên 95% token tuần thì Scout dừng quét/chấm/ghi — xem mục Nhận theo lô.
Scout tuyệt đối không tự nhập TOPIC_ID; CEO khi nhập TOPIC_ID phải lật READY trong cùng lần (không nhập ID rồi để APPROVED); pipeline khi claim kiểm tra cả hai (READY + TOPIC_ID) và báo COO nếu gặp READY mà TOPIC_ID trống hoặc APPROVED mà đã có TOPIC_ID (quyết CEO 09/11/2026, R8-18 phương án A).
APPROVED ≥70đ quá 48h chưa READY thì Scout chấm lại FRESH (và TOTAL) ở ca quét tiếp theo, ghi chú 'chờ READY từ <ngày>'; quá 72h vẫn chưa READY thì COO nhắc CEO 1 lần qua CEO_REPORTS (quyết CEO 09/11/2026, R8-34 phương án A).

### TASKS — nguồn sự thật duy nhất
TOPIC_ID | TITLE | STATUS | ASSIGNEE | DRAFT_LINK | QA_VERDICT | RETURNS | DRIVE_LINK | MD5 | UPDATED_AT | PROD_NOTES | QUOTA | BLOCKER | DUP_NOTE | FACEBOOK
Cột O FACEBOOK — tồn tại live (41/53 dòng có dữ liệu, vd "Đã đăng Facebook — Tiền Thông Minh — https://facebook.com/reel/1171365755350560/ — 06/11/2026"), do bên khác quản lý, chưa chuẩn hóa (quyết CEO 08/11/2026, DEC-120, R5-15 phương án C): chưa có luật ai ghi/ghi khi nào/định dạng chuẩn, không phải bước bàn giao; chi nhánh này để nguyên, không động vào (DEC-081).
Máy trạng thái: CLAIMED → BUILDING → REVIEW ↔ RETURNED (sửa → BUILDING → nộp lại REVIEW) → APPROVED → DELIVERED (hoặc → BLOCKED nhóm 2 khi upload không chạy được, DEC-153); + BLOCKED / CANCELLED. Không có đường RETURNED → APPROVED: mọi bản sửa đều phải qua REVIEW + verdict mới trong QA_LOG. Mỗi video có một dòng TASKS khi được
giao (STATUS = CLAIMED, ASSIGNEE = email khai báo); dòng chuyển BUILDING
khi Production bắt đầu, REVIEW khi nộp QA (E DRAFT_LINK), RETURNED khi
QA trả lại (F QA_VERDICT, G RETURNS tăng 1), APPROVED khi QA duyệt,
DELIVERED khi đã có H DRIVE_LINK + I MD5 thật. BUILDING cũ (quyết CEO 08/11/2026, DEC-105 phương án A): video vẫn BUILDING qua 2 lần đầu ca liên tiếp mà không có ghi chú K mới thì pipeline hỏi Production (bước hiện tại + lỗi + cần gì); Production trả lời trong 1 ca, lỗi nhóm 1 thì ghi BLOCKED rồi lấy video kế tiếp trong lô, lỗi hệ thống thì dừng; không trả lời tới đầu ca sau thì COO giao lại (kiểm tra trước, tiếp tục từ điểm dừng trong K theo luật resume; chỉ xét dòng TASKS.J UPDATED_AT là ngày hôm nay, video ngày cũ chỉ xử lý ở ca 06:00 theo DEC-117). REVIEW cũ (quyết CEO 08/11/2026, DEC-106 phương án A): video vẫn REVIEW qua 1 ca (khoảng 4 giờ) mà không có verdict trong QA_LOG thì pipeline hỏi QA; QA trả lời trong 1 ca; Production được bắt đầu video kế tiếp trong lô trong lúc chờ verdict (nới DEC-032; chỉ xét dòng TASKS.J là ngày hôm nay, video ngày cũ chỉ xử lý ở ca 06:00 theo DEC-117). Vòng lặp RETURNED (quyết CEO 08/11/2026, DEC-107 phương án A): leo thang lại mỗi khi số lần trả tăng sau lần đầu; trần 3 lần trả thì Production dừng sửa, COO quyết trước 06:00 hôm sau (sửa tiếp 1 lần với cách khác — chỉ 1 lần (a) duy nhất, bị trả lần 4 thì chỉ còn BLOCKED nhóm 1 hoặc hủy; quá hạn thì pipeline ghi vào báo cáo ca ‘COO chưa quyết — cần CEO quyết’ và COO ghi CEO_REPORTS khi quá 24h kể từ lần trả thứ 3) (quyết CEO 08/11/2026, DEC-154). Video đã duyệt chưa upload (quyết CEO 08/11/2026, DEC-108 phương án A): pipeline đầu ca kiểm tra TASKS.C=APPROVED hoặc QA_LOG APPROVED mà TASKS chưa DELIVERED rồi nhắn QA upload ngay (mở rộng theo DEC-155, R5-37 phương án A: kiểm cả dòng TASKS đang BUILDING/REVIEW mà QA_LOG đã có APPROVED do ghi TASKS lỗi giữa chừng; trước khi nhắn upload, đối chiếu md5 đã duyệt với DRAFT_LINK hiện tại — nếu khác version thì không nhắn upload mà báo COO, tránh upload nhầm version cũ chưa xong); QA báo ngay mọi lỗi upload; quá 1 ca chưa xong thì COO giao lại cho QA. Rảnh mà còn việc (quyết CEO 08/11/2026, DEC-109 phương án A): pipeline đầu ca kiểm tra không có video BUILDING/REVIEW/RETURNED mà còn CLAIMED thì nhắn Production lấy video đầu tiên theo thứ tự Sheet; quá 1 ca chưa BUILDING thì COO giao lại cho Production. BLOCKED: video tắc — lỗi riêng video (nhóm 1) thì pipeline bỏ qua trong-lô, Production lấy video CLAIMED kế tiếp chưa tắc trong cùng lô; lỗi hệ thống (nhóm 2) hoặc chưa rõ lý do thì dừng hàng đợi pipeline cho đến khi COO gỡ tắc hoặc hủy (CANCELLED).

Điểm dừng giao lại (quyết CEO 08/11/2026, DEC-153 phương án B): mỗi video chỉ được giao lại tối đa 2 lần (lần 1 pipeline nhắn phòng, lần 2 COO giao lại); đã giao lại 2 lần mà vẫn chưa xong thì pipeline không nhắn phòng nữa, chỉ ghi vào báo cáo ca để COO quyết BLOCKED/CANCELLED hoặc CEO quyết qua CEO_REPORTS. Video APPROVED quá 2 lần giao lại mà vẫn chưa upload được thì COO ghi TASKS.C = BLOCKED (nhóm 2, lỗi hệ thống) + lý do vào M BLOCKER — đường chuyển APPROVED→BLOCKED.

Mã lý do BLOCKED (quyết CEO 08/11/2026, DEC-158 phương án A): khi ghi M BLOCKER, bắt buộc ghi mã lý do chuẩn ở đầu ô, sau đó mới ghi lý do + thời gian. Nhóm 1 (lỗi riêng video): G1 thiếu tư liệu đã kiểm chứng (gồm tìm ảnh hết ứng viên mà không có file đạt — gộp theo quyết CEO 09/11/2026), G2 trùng chủ đề/video đã làm, G3 nhân vật nhạy cảm hoặc phiên tòa đang diễn ra không có phương án minh họa an toàn, G4 brief thiếu góc làm hoặc khán giả mục tiêu, G5 CEO/COO yêu cầu dừng video đó, G6 vòng QA trả lại mà lỗi gốc không sửa được cho video này. Nhóm 2 (lỗi hệ thống): S1 TTS hỏng, S2 render/preflight/template hỏng, S3 Drive/Sheets lỗi, S4 worker/phòng không phản hồi, S5 quyền thư mục Drive. Pipeline đếm ‘cùng lý do’ cho cầu chì theo mã 2 ký tự đầu ô M (DEC-172), không đếm theo text tự do; M trống/mơ hồ thì mặc định nhóm 2 (dừng hàng đợi) như cũ.
**Nhận theo lô (quyết CEO 08/11/2026, T3 phương án B):** mỗi ca nhận 1 lần tối đa 3 chủ đề READY mới theo thứ tự Sheet (tối đa 12 claim/ngày), không trừ số video đang làm dở trong ngày; tổng số video đang làm cùng lúc có thể vượt 3. (Trần đổi 4→3 theo quyết CEO 09/11/2026, DEC-199; hiệu lực từ ca 06:00 09/11/2026, không hồi tố theo DEC-116.) Ngoại lệ (quyết CEO 08/11/2026, DEC-156 phương án B; sửa theo quyết CEO 09/11/2026, DEC-201): đầu ca đọc TASKS.L QUOTA mới nhất của chi nhánh — nếu token tuần đã đạt trên 95% thì claim 0 chủ đề READY mới trong ca đó (chặn tạo video mới, không cần báo cáo riêng việc claim 0; báo cáo ca vẫn làm bình thường cho video đang dở), chỉ để video đang làm dở hoàn thành; token thêm là khoản dự phòng cho việc khác, không dùng để sản xuất video; nếu không đọc được quota thì ghi "không đọc được" vào báo cáo ca và vẫn đi tiếp. Cửa chặn này áp dụng toàn công ty (quyết CEO 09/11/2026, DEC-202): Scout cũng dừng quét/chấm/ghi chủ đề khi token tuần trên 95% (ca dừng hẳn, không báo cáo ca); khi hạn mức tuần được reset thì công ty hoạt động trở lại bình thường, không cần lệnh mở lại. Ngoại lệ: cron coo-scan-0600 và bot-hoc-hoi-2000 không thuộc diện dừng (DEC-202). Luật đổi trần không hồi tố (quyết CEO 08/11/2026, DEC-116, R5-11 phương án A): trần 4 (DEC-102, có hiệu lực 11:18 08/11) chỉ áp cho ca claim sau thời điểm đó; lô 10:00 ngày 08/11 đã claim 5 (TOPIC-273/277/278/279/283) hợp lệ theo trần 5 còn hiệu lực lúc claim, giữ nguyên cả 5, không nhả. Video đang làm dở từ NGÀY CŨ thì bỏ qua theo quy tắc ngày hiện tại — ngoại trừ bước cứu lô cũ dưới đây.
**Cứu lô cũ qua đêm (quyết CEO 08/11/2026, DEC-117 phương án A):** chỉ ca 06:00 mới làm — pipeline liệt kê các dòng TASKS của chi nhánh mình ở CLAIMED / BUILDING / REVIEW / RETURNED / BLOCKED / APPROVED mà TASKS.J UPDATED_AT là ngày trước ngày hôm nay, báo COO quyết giữ/bỏ từng video trong ca đó. Giữ → phòng liên quan tiếp tục video, cập nhật TASKS.J sang ngày hôm nay khi chạm vào (coi như "nhận lại", xử lý như video hôm nay); bỏ → COO ghi TASKS.C = CANCELLED + lý do vào M BLOCKER. Dòng cũ chưa có quyết định thì liệt kê lại ở ca 06:00 hôm sau. Quy tắc ngày hiện tại vẫn giữ nguyên cho các ca khác và cho việc nhận lô mới.
Quy tắc ghi: xem Bảng phân quyền ghi Sheet ở đầu spec (ai ghi tab nào,
cột nào); bàn giao phải có link kết quả trong Sheet.
QA tải video đã duyệt lên thư mục Drive "Video Muse" ngay trong lượt duyệt
và ghi link thật vào đây (H DRIVE_LINK + I MD5, STATUS = DELIVERED) +
ghi verdict vào QA_LOG; không bịa link, không tự tạo thư mục khác, không
tự thay đổi quyền thư mục (thư mục "Video Muse" đã được CEO cấp quyền
anyone with link ngày 05/11/2026).
**Thẻ phê duyệt upload Drive hết hạn sau 30 phút (lệnh CEO 05/11/2026, tiền lệ TOPIC-232):** lệnh upload lên Drive hiện thẻ phê duyệt, chỉ cho 30 phút để bấm; hết 30 phút không có quyết định thì thẻ tự hết hạn (approval_expired / Timed out), thao tác không chạy, file không lên Drive. Tiền lệ: thẻ gửi 10:52:57 +07, hết hạn 11:22:57 +07, Timed out 11:23:02 +07 — không phải bị từ chối, không phải file hỏng hay thư mục sai quyền. Cách xử lý đúng là **chạy lại upload một lần để hệ thống cấp thẻ mới** (không tính là "thử lại ẩu"); cấp phép toàn quyền của CEO cho QA hoàn tất bàn giao mà không hỏi lại trong chat **không tắt được thẻ hệ thống** — thẻ vẫn hiện mỗi lần upload, cần bấm trong 30 phút; upload Drive không có standing Allow. **Khi gặp thẻ hết hạn, QA phải báo ngay cho COO; COO ghi lại thông báo tình trạng vào cột G "Kết quả hoàn thành" của dòng COO_TASKS tương ứng (ghi tạm thời trong khi nhiệm vụ vẫn ở "Đang làm", cột F thời gian hoàn thành vẫn để trống), để CEO đọc tab COO_TASKS là biết vấn đề ở đâu, không phải chờ tới khi xong mới biết. Khi nhiệm vụ hoàn thành sau đó, COO cập nhật lại cột G bằng kết quả cuối cùng kèm link. Quy tắc này khác với 429/403/rate-limit: gặp 429/403 thì dừng nhánh, ghi blocker, không thử lại.**
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
thái chưa phải "Hoàn thành" VÀ cột F Thời gian hoàn thành còn trống.
Dòng đã E = "Hoàn thành" + có F thì bỏ qua. Chữ ký định danh (lệnh CEO 05/11/2026): cột B được đối chiếu với email khai báo đã lưu trong bộ nhớ của chính tài khoản Muse đó, không đối chiếu bằng email đăng nhập hệ thống (hệ thống không cho agent đọc email này). Tài khoản mới clone repo về phải khai báo email và lưu vào bộ nhớ của mình trước ca quét đầu tiên, tên COO chính là email khai báo đó; chưa có email khai báo thì không nhận dòng tab COO_TASKS nào, phải báo CEO qua CEO_REPORTS để CEO khai báo. Cột E chỉ dùng 4 giá trị:
Assigned / Đang làm / Hoàn thành / Tắc; COO chuyển sang "Đang làm" ngay
khi ghi ID. Cột F COMPLETED_AT chỉ ghi khi hoàn thành, dạng YYYY-MM-DD HH:MM +07. Ngày
trong ID COO-YYYYMMDD-NN lấy theo ngày COO đọc/nhận (không còn cột ngày giao); số thứ tự NN tính theo ngày COO đọc/nhận; ID chỉ duy nhất trong phạm vi một tài khoản Muse + email
cột B. "Blocked" không phải giá trị cột E tab COO_TASKS — E chỉ dùng 4 giá trị trên; nếu cần ghi tắc ở nơi khác thì chỉ dùng "Blocked" cho TASKS (C = BLOCKED), không ghi vào E tab COO_TASKS.
- COO tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID TASKS (TOPIC_ID)
nào nếu có), tự giao cho các phòng qua chat, tự theo dõi ở TASKS. CEO
không cần đọc TASKS, không cần đọc chi tiết phân việc.
- COO báo cáo qua Sheet trên cùng dòng tab COO_TASKS: E = Hoàn thành, F = thời
gian hoàn thành dạng "YYYY-MM-DD HH:MM +07", G = Kết quả hoàn thành (viết
ngắn + link bằng chứng nếu có, chỉ khi tắc mới ghi "cần CEO" trong này).
CEO chỉ cần đọc E, F, G ở tab COO_TASKS là biết việc xong chưa, kết quả gì.
Thiếu E, F hoặc G thì chưa tính là báo cáo xong.

### QA_LOG (append-only)
VIDEO_ID | VERSION | DATE | RESULT | ISSUES | REPO_NOTE
RESULT chuẩn hoá bằng dropdown: APPROVED / RETURNED. Append-only (R5):
ghi sai thì ghi dòng đính chính mới, không sửa/xoá dòng log đã có.
Video bị trả 2 lần chưa có verdict Duyệt sau đó thì leo thang về chat COO;
các lần trả thêm sau đó thì leo thang LẠI mỗi khi số lần trả tăng (quyết
CEO 08/11/2026, DEC-107 phương án A). Sau lần trả thứ 3 Production dừng sửa, COO quyết trước 06:00 hôm sau; chỉ 1 lần sửa tiếp (a) duy nhất (DEC-154).

### DECISIONS — chỉ CEO quyết
DECISION_ID | ISSUE | OPTION_A | OPTION_B | COO_PROPOSAL | CEO_DECISION | DATE

### COO_TASKS — tab nhiệm vụ riêng cho COO, 7 cột (lệnh CEO 04/11/2026, bỏ cột "Ngày CEO giao" ngày 05/11/2026; bỏ cột DEADLINE ngày 08/11/2026)
ID (COO tự ghi, CEO để trống) | Tài khoản Muse nhận việc (email) | Việc chính (CEO giao) | Phân việc chi tiết (COO tự phân) | Trạng thái | Thời gian hoàn thành | Kết quả hoàn thành
Ghi chú: dòng trên là nhãn nghĩa tiếng Việt; header live là mã tiếng Anh (ID | ASSIGNEE_EMAIL | TASK | DETAIL | STATUS | COMPLETED_AT | RESULT).
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
email của mình (đối chiếu bằng email khai báo trong bộ nhớ), cột E chưa phải "Hoàn thành" và cột F còn trống. Việc CEO giao sau 06:00
được đọc vào 06:00 hôm sau. Dòng email khác thì bỏ
qua. Dòng đã E = "Hoàn thành" + có Thời gian hoàn thành thì bỏ qua.
- Ngoại lệ quét ngoài 06:00 (lệnh CEO 05/11/2026, mục A32): lệnh quét ngoại lệ ngoài 06:00 (lệnh trực tiếp của COO) được ghi vào CEO_REPORTS; lần quét đó vẫn theo đủ các điều kiện nhận dòng (cột B = email khai báo của mình, cột E chưa "Hoàn thành", cột F còn trống). Ngoài lệnh trực tiếp của COO, COO không tự quét thêm lần nào trong ngày.
- COO làm: tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID TASKS (TOPIC_ID)
nào nếu có), giao cho phòng qua chat, tự theo dõi ở TASKS. TASKS
vẫn là nơi theo dõi video và các phòng; tab COO_TASKS không thay thế TASKS.
- CEO chỉ theo dõi kết quả: đọc cột E, F, G ở tab COO_TASKS là đủ. COO báo cáo
trên cùng dòng: E = Hoàn thành, F = thời gian hoàn thành dạng
"YYYY-MM-DD HH:MM +07", G = Kết quả hoàn thành (viết ngắn + link bằng
chứng nếu có, chỉ khi tắc mới ghi "cần CEO" trong này). Thiếu E, F hoặc G
thì chưa tính là xong. Cột E chỉ dùng 4 giá trị Assigned / Đang làm / Hoàn thành / Tắc; "Blocked" không phải giá trị cột E tab COO_TASKS (nếu cần ghi tắc ở nơi khác thì chỉ dùng cho TASKS (C = BLOCKED), không ghi vào E tab COO_TASKS).
- Ngoại lệ CEO → COO qua Sheet (lệnh CEO 04/11/2026): CEO chỉ giao việc chính, không cần chat trực tiếp, bằng dòng ở tab COO_TASKS có cột B là email tài khoản Muse nhận việc. COO đọc tab COO_TASKS đúng 1 lần lúc 06:00 +07 mỗi ngày, chỉ nhận dòng chưa hoàn thành có cột B = email của mình, cột E chưa phải "Hoàn thành" và cột F còn trống, tự phân việc chi tiết và giao cho các phòng qua chat, rồi báo cáo hoàn thành lại qua Sheet trên cùng dòng, đủ E = Hoàn thành + F + G của tab COO_TASKS. CEO chỉ theo dõi kết quả hoàn thành ở tab COO_TASKS. Trong đường này, lệnh của COO cho phòng chức năng có nguồn gốc từ lệnh CEO qua Sheet nên phòng tuân theo, không phải là phòng tự phát sinh việc.

### CEO_REPORTS — tab báo cáo duy nhất COO → CEO + kênh lệnh duy nhất CEO → COO/các phòng, 9 cột (lệnh CEO 08/11/2026, DEC-110; bỏ cột STATUS theo DEC-113; mở rộng thành kênh duy nhất theo phương án B, lệnh CEO 08/11/2026)
REPORT_ID | DATE_REPORTED | ASSIGNEE_EMAIL | ISSUE | TRIED | NEEDS_DECISION | CEO_REPLY | APPLIED_BY | DATE
Tab này là kênh duy nhất COO báo cáo CEO và kênh duy nhất CEO ra lệnh cho COO/các phòng. COO chỉ gửi báo cáo lên tab này khi vấn đề nghiêm trọng (vượt quyền COO, không điều phối được); vấn đề COO điều phối được thì không gửi báo cáo đến CEO_REPORTS (lệnh CEO 08/11/2026). COO ghi dòng mới (A–F) khi báo cáo nghiêm trọng hoặc khi cần CEO quyết; CEO ghi quyết định/lệnh vào G CEO_REPLY trên cùng dòng (hoặc ghi dòng mới khi là lệnh mới); phòng thi hành ghi tên mình vào H APPLIED_BY ngay khi đọc lệnh và thực thi ngay lập tức. Lệnh CEO (trong G CEO_REPLY) được các phòng áp dụng trực tiếp, không chờ chuyển lời.
- COO ghi (chỉ A–F): REPORT_ID dạng RPT-YYYYMMDD-BBB-NN (BBB = 3 số đầu email khai báo của chi nhánh, vd 006 cho 006@vuachim.com; NN = số thứ tự trong ngày của chi nhánh đó; không trùng trong phạm vi chi nhánh — 2 chi nhánh khác BBB nên không bao giờ trùng toàn cục; quyết CEO 08/11/2026, DEC-121, R5-05 phương án A); DATE_REPORTED dạng "YYYY-MM-DD HH:MM +07"; ASSIGNEE_EMAIL là email khai báo của chi nhánh gửi báo cáo (cùng cách dùng như cột B tab COO_TASKS và cột D TASKS — chỉ email khai báo mới tính là định danh chi nhánh; trống thì ghi "chưa xác định — hỏi CEO", không đoán); ISSUE viết ngắn kèm bằng chứng/link; TRIED ghi cách COO đã thử và kết quả; NEEDS_DECISION là câu hỏi cụ thể cần CEO quyết, kèm phương án nếu có. Cột H APPLIED_BY để trống khi tạo dòng, chờ phòng thi hành ghi.
- Gửi báo cáo leo thang khi nào (lệnh CEO 08/11/2026, DEC-111): COO chỉ gửi lên CEO_REPORTS khi vấn đề vượt quyền COO VÀ đã thử mọi cách trong thẩm quyền (chi tiền, cam kết ngoài, thay đổi không đảo ngược, pháp lý, tắc > 24h, xung đột, vượt ngân sách, lỗi hệ thống không sửa được); một vấn đề một dòng, không trùng dòng chưa có CEO_REPLY (G trống); không gửi việc COO tự quyết được, việc CEO đã quyết, việc thường kỳ. CEO_REPORTS chỉ nhận vấn đề nghiêm trọng: vấn đề COO điều phối được thì không gửi báo cáo đến CEO_REPORTS. Luật lọc chi tiết ở skill COO.
- CEO ghi: CEO_REPLY (chỉ CEO ghi, cột G) — CEO ghi quyết định kèm ngày trả lời trong cùng ô G (vd "Quyết: ... (08/11/2026)"). DATE (cột I) do phòng đầu tiên đọc lệnh ghi ngày nhận lệnh, dạng "YYYY-MM-DD HH:MM +07" (lệnh CEO 08/11/2026, phương án A).
- Phòng thi hành (lệnh CEO 08/11/2026): APPLIED_BY (H) ghi tên phòng chức năng ĐẦU TIÊN đọc được lệnh của CEO (Sản xuất / Scout / kỹ thuật QA / COO, có dropdown); phòng đó ghi tên mình vào H ngay khi đọc và thực thi ngay lập tức, không chờ COO chuyển lời. Bất kỳ phòng chức năng nào đọc được lệnh đều có quyền thực hiện, không cần COO mới được đọc. Chỉ đọc lệnh có C ASSIGNEE_EMAIL = email khai báo của chi nhánh mình (chỉ trong giới hạn quản lý của công ty mình). Chỉ đọc và thực hiện các lệnh chưa thực hiện — APPLIED_BY (H) và DATE (I) đều trống; dòng đã có APPLIED_BY hoặc DATE thì đã có phòng khác đọc/thực thi, bỏ qua, không thực hiện lại. Phòng nào đọc trước ghi trước, đã có tên thì không ghi đè. DATE (I) ghi ngày phòng nhận lệnh. Dòng chưa có CEO_REPLY (G trống) là dòng đang chờ CEO.
- Ai đọc phản hồi CEO (lệnh CEO 08/11/2026, DEC-112 phương án A; bổ sung lệnh CEO 08/11/2026): để phản hồi không bị bỏ sót, pipeline đọc CEO_REPORTS đầu mỗi ca (bước 2(g) trong body cron prod-pipeline — chỉ dòng của chi nhánh mình có CEO_REPLY mới từ ca trước tới nay, chuyển lời tới phòng liên quan kèm REPORT_ID, ghi vào báo cáo ca) và COO đọc thêm ở ca quét 06:00 (Bước 6 trong body cron coo-scan-0600 — phản hồi mới từ 06:00 hôm qua tới nay, chuyển lời hoặc tự thực hiện theo phản hồi). Cả hai chỉ đọc và chuyển lời, không ghi gì vào CEO_REPORTS; bất kỳ phòng chức năng nào đọc được lệnh đều có quyền thực hiện ngay lập tức, không cần COO mới được đọc; phòng vẫn áp dụng trực tiếp từ CEO_REPLY, không chờ chuyển lời mới làm. Chỉ đọc lệnh có C ASSIGNEE_EMAIL = email khai báo của chi nhánh mình. Chỉ đọc và thực hiện các lệnh chưa thực hiện — APPLIED_BY (H) và DATE (I) đều trống; dòng đã có APPLIED_BY hoặc DATE thì đã có phòng khác đọc/thực thi, bỏ qua, không thực hiện lại.
- Cột H APPLIED_BY có dropdown 4 giá trị: Sản xuất / Scout / kỹ thuật QA / COO.

## Quy tắc leo thang lên CEO
Chỉ leo thang khi: chi tiền, cam kết bên ngoài, thay đổi không đảo ngược,
pháp lý, tắc > 24h, xung đột giữa 2 nhân viên, vượt ngân sách, lỗi hệ thống không sửa được. Video bị
trả ≥ 2 lần chưa có verdict Duyệt sau đó thì leo thang về chat COO
(đếm từ QA_LOG) — leo thang lại mỗi khi số lần trả tăng; sau lần trả thứ 3 Production dừng sửa, COO quyết trước 06:00 hôm sau (quyết CEO 08/11/2026, DEC-107 phương án A; sửa DEC-154 — chỉ 1 lần sửa tiếp (a) duy nhất, quá hạn thì pipeline ghi vào báo cáo ca ‘COO chưa quyết — cần CEO quyết’). Chủ sở hữu bước ghi CEO_REPORTS cho video đủ 3 lần trả quá hạn là coo-scan Bước 7 (R6-14).
Việc tắc/vượt quyền COO thì ghi vào CEO_REPORTS (không ghi vào DECISIONS); chỉ việc COO tự quyết được mới ghi DECISIONS để CEO xem sau (COO ghi A–D vào tab DECISIONS khi ghi nhận việc đó + đề xuất vào cột E COO_PROPOSAL; CEO chỉ ghi F CEO_DECISION + G DATE).
Báo cáo cần CEO quyết thì COO ghi vào tab CEO_REPORTS (xem mục CEO_REPORTS), CEO trả lời trên cùng dòng; các phòng đọc phản hồi CEO và áp dụng trực tiếp, không chờ COO chuyển lời.
