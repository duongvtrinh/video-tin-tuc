# Bộ nhớ vận hành — bàn giao cho chi nhánh mới

Bản sao lưu có chọn lọc từ bộ nhớ của chi nhánh gốc, để tài khoản Muse mới
clone repo về đọc và học lại cách vận hành công ty — không phải tự mò lại
từ đầu. Snapshot ngày **09/11/2026** (quyết định mới nhất ghi trong file:
DEC-200 — viết lại toàn bộ file này theo lệnh CEO).

- Đây là **bản tóm tắt đã đúc kết**, không thay thế tài liệu chuẩn. Luật đầy
  đủ nằm ở `BOOTSTRAP.md`, `company-os/google-sheet-spec.md`,
  `company-os/bot-sop.md`, 4 skill trong `company-os/skills/` (Production,
  QA, Scout, COO) và body 4 lịch cron trong `company-os/crons/daily/`.
  Khi hai bên lệch nhau, tài liệu chuẩn thắng; khi luật đổi, cập nhật file
  này trong cùng lần đổi.
- Lịch sử quyết định đầy đủ nằm ở tab **DECISIONS** trong workbook dùng
  chung (DEC-001 đến DEC-200). File này chỉ tóm tắt luật đang chạy + lý do
  đằng sau; tra cứu DEC-xxx trong tab DECISIONS để đọc nguyên văn.
- File này **không chứa** giá trị riêng của bất kỳ chi nhánh nào (xem mục
  Cảnh báo). Chi nhánh mới phải tự khai báo các giá trị của mình (§16).

## Cảnh báo — đừng copy giá trị của chi nhánh khác

- **Email khai báo (định danh chi nhánh) là của riêng từng chi nhánh.**
  Mỗi tài khoản Muse phải tự khai báo email của mình sau khi clone, không
  copy email chi nhánh khác, không dùng email Drive/GitHub/Facebook thay
  thế. Hệ thống không cho agent đọc email đăng nhập của chính nó, nên email
  này phải do CEO nói cho tài khoản đó, tài khoản đó tự ghi vào MEMORY.md
  của chính nó. Chưa khai báo thì không nhận dòng COO_TASKS nào, báo về
  chat chính để CEO khai báo trước, không đoán.
- **ID chat phòng, số hạn mức/token, mã md5, link Drive từng video** cũng
  là của riêng từng chi nhánh / từng thời điểm — không có trong file này,
  trừ §14 là snapshot lịch sử có ghi ngày giờ đọc.
  Chat phòng mới tự tạo và liệt kê qua `chat.list`; hạn mức đọc lại tại
  thời điểm upload.
- **Được copy nguyên văn:** ID repo, ID workbook dùng chung, ID thư mục
  Drive dùng chung (mục 2) — vì đó là tài nguyên dùng chung mọi chi nhánh.

## 1. Mô hình công ty — phương án B (lệnh CEO 08/11/2026)

- Một người làm media. Mỗi tài khoản Muse là một **chi nhánh độc lập**,
  tự sản xuất video, có COO điều phối cùng các phòng chức năng.
- Mỗi chi nhánh định danh bằng một **email khai báo** (email tài khoản Muse
  đang hoạt động, do CEO cung cấp). Các phòng trong cùng chi nhánh dùng
  chung định danh này khi báo cáo vào Sheet để ký nhận/xác nhận người hoàn
  thành và phân biệt với chi nhánh khác.
- **CEO chỉ ra lệnh qua tab CEO_REPORTS** (ghi quyết định/lệnh vào cột G
  CEO_REPLY). **Lệnh từ chat chính hay COO đều tính là lệnh của COO.**
  Các phòng chức năng và COO chỉ nhận lệnh từ CEO duy nhất qua CEO_REPORTS.
- **Kênh báo cáo:** mọi phòng (Production, QA, Scout) báo cáo kết quả /
  tiến độ cho COO; chỉ COO báo cáo với CEO, và chỉ qua tab CEO_REPORTS
  khi vấn đề nghiêm trọng (DEC-111). Báo cáo thường kỳ của COO ghi vào
  nhật ký ngày `~/memory/YYYY-MM-DD.md`, không ghi vào CEO_REPORTS.
- **COO có toàn quyền điều phối** hoạt động của công ty một cách độc lập,
  không phụ thuộc CEO — tự điều phối để hoàn thành ca làm việc, hoặc sản
  xuất nhiều video nhất có thể. Nếu tasks bị kẹt thì COO hướng dẫn làm task
  tiếp theo đã được claimed trong ca.
- Chat chính là kênh CEO nhắn tin. Agent ở chat chính là điều phối viên
  (COO): nhận nhiệm vụ, phân tích, tự động điều phối đến đúng phòng bằng
  `chat.send_message` (không hỏi CEO phải giao cho phòng nào, trừ khi nhiệm
  vụ mơ hồ), theo dõi tiến độ, tổng hợp kết quả. CEO chỉ làm việc ở chat
  chính, không tự đi từng phòng để ghép kết quả.

## 2. Tài nguyên dùng chung (mọi chi nhánh dùng chung)

- Repo (private, giữ private): `duongvtrinh/vieneu-media-company`,
  nhánh `main`. Đẩy lên GitHub chỉ sau khi CEO đọc phân tích và duyệt riêng
  (mục 9).
- Workbook vận hành: **"Video HQ — Tin Tức"**,
  spreadsheetId `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`, múi giờ
  Asia/Saigon, 7 tab: TOPICS / TASKS / QA_LOG / DECISIONS / COO_TASKS /
  CEO_REPORTS / COO_CHECKIN.
- Thư mục Drive: **"Video Muse"**,
  folderId `1bA21n3Y3YiY6HSjLUEFmxnJXLnjtSJGc`, đã cấp quyền anyone with
  link (writer, allowFileDiscovery=false) từ 05/11/2026. Không tự tạo thư
  mục khác, không tự đổi quyền thư mục.
- Workbook cũ CHỈ ĐỌC (xem spec), không ghi vào đó. Mọi luật cũ gắn với workbook này (cổng Approved + cột O "Duyệt" + không có *-DRAFT) đã bãi bỏ.

## 3. Luật điều phối — cốt lõi

- **Một nhiệm vụ = một chủ sở hữu duy nhất.** Trước khi giao, kiểm tra
  TASKS và thư mục project, khóa nhiệm vụ bằng dòng TASKS STATUS=CLAIMED
  (không ghi đè, không xóa dòng cũ). Nếu nhiệm vụ đã có chủ sở hữu, đã có
  DRAFT hoặc đang chạy ở một phòng, chat chính KHÔNG giao lại, KHÔNG spawn
  subagent song song làm cùng nhiệm vụ, mà chỉ theo dõi phòng đó.
- **Phòng ban chỉ làm nhiệm vụ khi được giao qua đúng 1 trong 3 kênh:**
  (1) chat chính / COO — lệnh điều phối của COO; (2) lịch bot đã được CEO
  duyệt (kể cả bot-pipeline); (3) COO qua tab COO_TASKS. Phòng không tự
  phát sinh nhiệm vụ sản xuất mới chỉ vì đọc Sheet hay lịch sử fork. Scout
  vẫn quét / ghi chủ đề và tự chấm theo ca; Sản xuất chỉ sản xuất khi có
  giao việc cụ thể với ID chủ đề, đủ cổng READY.
- **Vượt phạm vi thì ghi 1 dòng vào tab CEO_REPORTS, không tự quyết:**
  chi tiền, cam kết ngoài, đăng nền tảng, affiliate, chia sẻ Drive công
  khai, push GitHub, thay đổi quyền thư mục Drive, thay đổi chuẩn. Chỉ ghi
  khi vấn đề vượt quyền COO và đã thử mọi cách trong thẩm quyền (DEC-111).
- Kết quả chưa qua QA, chưa có link Drive thì ghi rõ là bản nháp chưa duyệt.
- **Báo cáo xong thì LÀM TIẾP, không chờ tin tiếp theo** (bài học
  TOPIC-277, 08/11/2026): báo cáo là ghi chú tiến độ, không phải xin phép
  và không phải điểm dừng — sau khi báo cáo tự lấy việc tiếp theo thì làm
  ngay bước dedup + nghiên cứu trong cùng lượt làm việc.

## 4. Cổng sản xuất — READY

- Chỉ sản xuất chủ đề đồng thời thỏa cả 3 điều kiện: TOPICS.STATUS = READY
  VÀ TOPIC_ID đã có (không trống) VÀ chưa có dòng TASKS nào cho TOPIC_ID
  đó. Không có ngoại lệ vượt cổng — ghi "vượt cổng" trong lệnh hay trong
  dòng COO_TASKS đều không mở cổng. Không còn cổng kiểm tra QA_LOG trước
  khi claim (DEC-157 đã bãi bỏ theo DEC-171, 09/11/2026).
- Chỉ CEO flip READY (từ APPROVED) và tự nhập TOPIC_ID. Scout ghi chủ đề
  mới luôn để TOPIC_ID trống; pipeline BỎ QUA dòng READY mà TOPIC_ID trống
  và ghi báo cáo để CEO nhập ID.
- TASKS là nguồn duy nhất: video đang làm/chờ QA đều thể hiện bằng dòng
  TASKS (CLAIMED/BUILDING/REVIEW/RETURNED); không kiểm tra thư mục
  projects hay tiến trình máy để quyết định có làm hay không.
- Production được tự tạo dòng CLAIMED khi nhận giao trực tiếp (DEC-082):
  sau khi đọc lại TASKS theo TOPIC_ID ngay trước khi ghi; chỉ cho chủ đề
  đã giao trực tiếp, đã đủ cổng READY.
- Nếu dòng TASKS đã có mà ASSIGNEE trống, Production điền ASSIGNEE = email
  khai báo của mình ngay khi nhận việc (B12). Bàn giao mà D trống thì ghi
  "chưa xác định — hỏi CEO", không tự lấy email khai báo thay thế
  (DEC-098/R4-09-B). D có nhưng khác email khai báo thì email khai báo
  thắng + báo COO (A19).

## 5. Pipeline — nhận theo lô

- Scout và Pipeline chạy lúc 06:00 Asia/Saigon hàng ngày.
- Mỗi ca pipeline NHẬN 1 LẦN tối đa **3 chủ đề READY mới** theo thứ tự
  Sheet, đánh dấu ngay bằng dòng TASKS STATUS=CLAIMED (ASSIGNEE = email
  khai báo của chi nhánh mình), rồi lần lượt tạo và bàn giao từng video
  trong lô (sản xuất tuần tự, không song song).
  Lịch sử trần: 5 (DEC-078/T3-B) → 4 (DEC-102, 08/11/2026 11:18) → 3
  (DEC-199, 09/11/2026, hiệu lực từ ca 06:00 09/11/2026). Luật đổi trần
  không hồi tố (DEC-116): trần mới chỉ áp cho ca claim sau thời điểm đổi;
  lô đã claim trước đó giữ nguyên (vd lô 10:00 ngày 08/11 đã claim 5
  hợp lệ theo trần 5 còn hiệu lực lúc claim).
- Mỗi ca nhận đủ 3 chủ đề READY mới, **không trừ** số video đang làm dở
  trong ngày. Video đang làm dở từ NGÀY CŨ thì bỏ qua theo quy tắc ngày
  hiện tại — không chặn việc nhận lô mới. Không còn cơ chế nhận tiếp khi
  QA báo DELIVERED; khi một video trong lô DELIVERED thì Production TỰ
  LẤY video kế tiếp trong lô (DEC-032) — chỉ lấy chủ đề đã CLAIMED trong
  cùng lô, ASSIGNEE = email khai báo của mình, UPDATED_AT = ngày hôm nay.
  Production được bắt đầu video kế tiếp trong lô trong lúc video trước
  đang REVIEW chờ verdict (nới DEC-032 theo DEC-106, vẫn chỉ làm 1 video
  tại một thời điểm).
- **Không giới hạn số video ĐÃ BÀN GIAO/ca hay /ngày** — chỉ trần NHẬN (3 chủ đề/ca) vẫn còn. DELIVERED trong ngày chỉ để báo cáo.
- **Quy tắc ngày hiện tại:** chỉ quan tâm ngày hiện tại; việc đang làm dở
  từ ngày cũ (CLAIMED/BUILDING/REVIEW/RETURNED/BLOCKED) thì bỏ qua, không
  chặn hàng đợi ngày hôm nay — không áp cho chủ đề READY (READY vẫn lấy
  theo thứ tự Sheet dù phát hiện ngày nào). Ngoại lệ duy nhất: bước cứu
  lô cũ qua đêm (DEC-117) — chỉ ca 06:00 mới liệt kê các dòng TASKS của
  chi nhánh mình ở CLAIMED/BUILDING/REVIEW/RETURNED/BLOCKED/APPROVED mà J
  là ngày trước ngày hôm nay để COO quyết giữ/bỏ từng video; giữ thì phòng
  cập nhật J sang ngày hôm nay khi chạm vào ("nhận lại"), bỏ thì COO ghi
  CANCELLED.
- **Cửa chặn hạn mức (DEC-263 — thay DEC-156/DEC-201/DEC-202):** đầu ca chạy lệnh subscription-status status, đọc % tuần đã dùng trực tiếp trong dòng 'Usage: N% of ... weekly limit' — nếu N ≥ 95% thì claim 0 chủ đề READY mới trong ca đó (chặn tạo video mới, không cần báo cáo), chỉ để video đang làm dở hoàn thành; token thêm là khoản dự phòng cho việc khác, không dùng để sản xuất video; nếu lệnh không đọc được N thì dùng số Sheet dự phòng (dòng COO_CHECKIN mới nhất của chính chi nhánh, rồi TASKS.L QUOTA); nếu cả hai đều không đọc được thì ghi "không đọc được" vào báo cáo ca và vẫn đi tiếp. Cửa chặn này áp dụng toàn công ty: Scout cũng dừng quét/chấm/ghi chủ đề khi N ≥ 95% (ca dừng hẳn, không báo cáo ca); khi hạn mức tuần được reset thì số trực tiếp tự hạ, công ty hoạt động trở lại bình thường, không cần lệnh mở lại. TASKS.L và COO_CHECKIN chỉ còn là bản ghi để CEO kiểm tra.
- **BLOCKED — phân loại rồi bỏ qua trong-lô (DEC-104):** dòng TASKS ở
  BLOCKED có ASSIGNEE = email khai báo của chi nhánh mình và UPDATED_AT
  là ngày hôm nay thì pipeline đọc M BLOCKER và phân loại theo mã 2 ký tự
  đầu M (bảng mã DEC-158): lỗi riêng video (nhóm 1: G1 thiếu tư liệu — gồm
  cả "tìm ảnh hết ứng viên mà không có file đạt" theo DEC-177; G2 trùng
  chủ đề; G3 nhân vật nhạy cảm/phiên tòa; G4 brief thiếu góc/khán giả; G5
  CEO/COO yêu cầu dừng; G6 vòng QA trả lại mà lỗi gốc không sửa được) thì
  KHÔNG dừng hàng đợi — Production lấy video CLAIMED kế tiếp chưa tắc
  trong cùng lô, video BLOCKED nằm lại chờ COO; lỗi hệ thống (nhóm 2: S1
  TTS hỏng, S2 render/preflight/template hỏng, S3 Drive/Sheets lỗi, S4
  worker/phòng không phản hồi, S5 quyền thư mục Drive) hoặc M trống/mơ hồ
  thì DỪNG cho đến khi COO gỡ tắc hoặc hủy; **2 video cùng mã lý do trong
  ngày thì DỪNG** (cầu chì — đếm theo mã 2 ký tự đầu M, DEC-172). Dòng của
  chi nhánh khác hoặc ASSIGNEE trống thì KHÔNG chặn — bỏ qua, nhận chủ đề
  khác, ghi các dòng đó (TOPIC_ID + STATUS + ASSIGNEE) vào báo cáo ca để
  COO xác định chủ. COO chỉ gỡ tắc / hủy dòng BLOCKED của chi nhánh mình;
  Production được ghi BLOCKED (chỉ lỗi riêng video nhóm 1, lý do bắt buộc
  vào M BLOCKER + điểm dừng vào K PROD_NOTES) nhưng không tự gỡ. Tắc
  >24h thì ghi 1 dòng vào CEO_REPORTS (DEC-111).
- **BUILDING cũ (DEC-105):** pipeline đầu ca đọc giờ vào BUILDING trong
  K; qua 2 lần đầu ca không có ghi chú K mới thì hỏi Production,
  Production trả lời trong 1 ca (bước + lỗi + cần gì), nhóm 1 thì ghi
  BLOCKED rồi lấy video kế tiếp trong lô, nhóm 2 thì dừng; không trả lời
  tới đầu ca sau thì COO giao lại (kiểm tra trước, tiếp tục từ điểm dừng
  trong K theo luật resume). Chỉ xét video ngày hôm nay; video ngày cũ chỉ
  xử lý ở bước cứu lô cũ 06:00 (DEC-117).
- **REVIEW cũ (DEC-106):** pipeline đầu ca đọc giờ nộp REVIEW trong K;
  qua 1 ca (khoảng 4 giờ) không có verdict trong QA_LOG thì hỏi QA, QA
  trả lời trong 1 ca (đang chấm tới đâu, verdict khi nào); Production khi
  chuyển REVIEW phải nhắn chat QA kèm ID video + DRAFT_LINK. Nếu QA trả
  lại video đang chờ thì Production tạm dừng video đang làm (ghi điểm dừng
  vào K), sửa video bị trả trước, nộp lại, rồi quay lại theo luật resume.
  QA không trả lời tới đầu ca sau thì COO giao lại cho QA (ID + DRAFT_LINK);
  giao lại thêm 1 ca vẫn im thì ghi 1 dòng vào CEO_REPORTS (DEC-111).
- **Vòng lặp RETURNED (DEC-107):** leo thang lại mỗi khi số lần trả tăng
  sau lần đầu (leo thang gửi về chat COO; mốc lần trả thứ 2 do PIPELINE
  đếm từ QA_LOG và nhắn, không phải QA — DEC-181; cùng số lần trả thì
  không nhắn lại); trần 3 lần trả thì Production DỪNG sửa, pipeline nhắn
  trực tiếp chat COO ngay khi đủ 3 lần trả, COO quyết trước 06:00 hôm sau
  (DEC-154); chỉ 1 lần sửa tiếp (a) duy nhất — bị trả lần 4 thì COO chỉ
  chọn BLOCKED nhóm 1 hoặc CANCELLED. QA khi trả phải ghi rõ lỗi nào đã
  trả trước đó ("lỗi lặp lại" vào QA_LOG.E ISSUES + tin nhắn cho
  Production); Production phải ĐỔI cách sửa khi lỗi lặp.
- **Video đã duyệt chưa upload (DEC-108 + mở rộng DEC-155):** pipeline
  đầu ca kiểm tra TASKS.C=APPROVED hoặc QA_LOG APPROVED mà TASKS chưa
  DELIVERED (kể cả dòng đang kẹt ở REVIEW/BUILDING mà QA_LOG đã có
  APPROVED) rồi nhắn QA upload ngay + ghi vào báo cáo ca (kiểm tra phiên
  bản video trước khi nhắn); QA báo ngay mọi lỗi upload; TASKS.C nằm lại
  APPROVED khi chưa có link thật; quá 1 ca chưa upload xong thì pipeline
  báo chat COO + COO giao lại cho QA (điểm dừng giao lại tối đa 2 lần,
  DEC-153).
- **Rảnh mà còn việc (DEC-109):** pipeline đầu ca kiểm tra không có video
  nào BUILDING/REVIEW/RETURNED mà còn dòng CLAIMED thì nhắn Production
  lấy video CLAIMED đầu tiên theo thứ tự Sheet làm tiếp + ghi vào báo cáo
  ca; Production xác nhận trong 1 ca, lấy video cũ nhất đang chờ trước;
  tới đầu ca sau vẫn chưa BUILDING thì pipeline báo chat COO + COO giao
  lại cho Production.
- **Kiểm tra đầu ca R7:** đọc số dòng + ID lớn nhất (chỉ tính dòng ĐÃ CÓ
  ID) của TOPICS và TASKS làm mốc cho ca sau. Số dòng GIẢM hoặc ID lớn
  nhất LÙI thì làm việc bình thường, KHÔNG dừng ca, KHÔNG báo cáo.

## 6. Scout — tìm và chấm chủ đề

- 2 phòng (Báo, Group) quét theo ca; mỗi phòng TỰ CHẤM chủ đề của mình
  trong cùng lượt quét (chat Scoring đã đóng 07/11/2026, C3).
- Thang 100: HOT 30 / AUDIENCE 20 / FRESH 20 / FEASIBLE 15 / SOURCED 15.
  TOTAL (cột J) luôn là công thức `=SUM(E:I)`. APPROVED khi tổng ≥70 VÀ
  quan tâm (HOT+AUDIENCE) ≥30; HOLD khi 50–69 hoặc tổng ≥70 nhưng quan tâm
  <30; REJECTED khi <50; DUPLICATE khi trùng sự kiện. Điểm quan tâm bắt
  buộc có số liệu bằng chứng trong NOTES.
- Scout KHÔNG BAO GIỜ ghi READY. TOPIC_ID để trống khi ghi mới; khử trùng
  theo tiêu đề/sự kiện. Mỗi ca báo cáo về chat COO (ca trống cũng báo 1
  dòng).
- **Cửa chặn hạn mức (DEC-263 — thay DEC-202):** đầu ca chạy lệnh subscription-status status, đọc % tuần đã dùng trực tiếp trong dòng 'Usage: N% of ... weekly limit' — nếu N ≥ 95% thì công ty tạm thời dừng hoạt động: Scout KHÔNG quét, KHÔNG chấm, KHÔNG ghi chủ đề mới trong ca đó (ca dừng hẳn, không phải ca trống), KHÔNG báo cáo ca. Khi hạn mức tuần được reset thì số trực tiếp tự hạ, hoạt động trở lại bình thường, không cần lệnh mở lại. Nếu lệnh không đọc được N thì dùng số Sheet dự phòng (dòng COO_CHECKIN mới nhất của chính chi nhánh, rồi TASKS.L QUOTA); nếu cả hai đều không đọc được thì ghi "không đọc được" vào báo cáo ca và vẫn quét tiếp. TASKS.L và COO_CHECKIN chỉ còn là bản ghi để CEO kiểm tra.
- **Điểm chỉ là gợi ý, không can thiệp quyết định duyệt của CEO; nội dung
  chủ đề mới là yếu tố CEO dùng để quyết định duyệt. Chỉ trạng thái READY
  mới quyết định có sản xuất video hay không.**

## 7. QA và bàn giao

- Verdict ghi 2 chỗ trong cùng lần chấm: 1 dòng mới vào QA_LOG
  (append-only, sai thì ghi dòng đính chính mới, không sửa/xóa dòng cũ) +
  TASKS (F QA_VERDICT, G RETURNS +1 khi RETURNED, C STATUS, J
  UPDATED_AT).
- Khi duyệt: upload NGAY trong cùng lượt duyệt lên thư mục Drive "Video
  Muse" và ghi TASKS: C=DELIVERED, H DRIVE_LINK, I MD5, F=APPROVED, J;
  đồng thời ghi dòng APPROVED vào QA_LOG.
- **Ký nhận + hạn mức (lệnh CEO 04/11/2026):** QA ghi vào TASKS.L QUOTA
  email người sản xuất + hạn mức còn lại tại thời điểm upload, chỉ bằng
  chữ, không chụp ảnh. Không đọc được thì ghi "không đọc được", không bịa.
  Bàn giao chỉ tính là xong khi dòng TASKS đã có đủ DRIVE_LINK + MD5 +
  người sản xuất + hạn mức trong TASKS.L QUOTA; thiếu 1 trong các mục thì
  báo cáo ghi "chưa xong bước Drive + Sheet". Người sản xuất = email khai
  báo trong bộ nhớ của tài khoản; nếu email bàn giao khác email khai báo
  thì email khai báo thắng, QA báo COO kèm cả hai email (A19).
- Khi trả: QA_LOG RESULT=RETURNED + TASKS C=RETURNED, G+1, rồi nhắn TRỰC
  TIẾP chat Sản xuất từng lỗi kèm mốc giây + cách sửa. Production sửa và
  nộp lại (STATUS quay lại REVIEW) — vòng lặp REVIEW ↔ RETURNED. Đếm leo
  thang theo QA_LOG, không theo TASKS.G.
- Thẻ phê duyệt upload Drive hết hạn sau 30 phút thì chạy lại upload 1 lần
  để lấy thẻ mới (không tính là thử lại ẩu); gặp 429/403 thì DỪNG, ghi
  blocker, không thử lại. Khi thẻ hết hạn, báo rõ "chưa xong bước Drive +
  Sheet vì thẻ phê duyệt hết hạn" và báo ngay cho COO.
- QA chấm 3 cửa (kỹ thuật sạch, đẹp, giữ người xem) + cửa hồ sơ/provenance
  (nhật ký tìm ảnh thật từng cảnh; AI generic / nền xanh rêu không kèm nhật
  ký tìm ảnh = trả lại). Chi tiết ở skill media-video-tech-qa.

## 8. COO và kênh CEO → COO

### COO_TASKS — 7 cột A–G (cột DEADLINE đã xóa 08/11/2026)

- CEO chỉ điền 2 ô: B ASSIGNEE_EMAIL (email tài khoản Muse nhận việc) +
  C TASK (việc chính). Cột A để trống.
- COO điểm danh tại tab COO_CHECKIN (Bước 0) rồi đọc tab đúng 1 lần lúc 06:00 +07 đầu ca (lịch coo-scan-0600); việc
  giao sau 06:00 đọc 06:00 hôm sau. Chỉ nhận dòng B = email khai báo của
  mình VÀ E chưa "Hoàn thành" VÀ F còn trống; không có dòng thì im lặng,
  không thông báo gì. Ngoại lệ: quét ngoài 06:00 chỉ khi có lệnh trực tiếp
  của COO, lệnh đó được ghi vào CEO_REPORTS; lần quét đó vẫn theo đủ 3
  điều kiện nhận dòng.
- COO ghi ID `COO-YYYYMMDD-NN` (ngày đọc/nhận, số thứ tự theo ngày) vào A
  trước khi phân việc ở D; chuyển E sang "Đang làm" ngay khi ghi ID. COO
  tự phân việc ở D và giao phòng qua chat, không chờ CEO, không hỏi lại
  trừ khi mơ hồ/vượt phạm vi.
- Hoàn thành trên cùng dòng: E = Hoàn thành, F COMPLETED_AT dạng
  "YYYY-MM-DD HH:MM +07", G RESULT (viết ngắn + link; chỉ khi tắc mới ghi
  "cần CEO"). Thiếu F/G thì chưa xong — COO giữ cập nhật E/F/G để CEO đọc
  kết quả.
- COO chỉ bàn giao video đã duyệt (QA tải lên Drive ngay trong lượt duyệt;
  COO không tự tải lên hay chuyển thay QA).

### CEO_REPORTS — 9 cột A–I, kênh leo thang COO → CEO + lệnh CEO

- A REPORT_ID (dạng RPT-YYYYMMDD-mail@domain.com-NN, mail@domain.com = email khai báo đầy đủ của chi nhánh; COO ghi A–F), B DATE_REPORTED, C ASSIGNEE_EMAIL, D ISSUE,
  E TRIED, F NEEDS_DECISION, G CEO_REPLY, H APPLIED_BY, I DATE.
- COO chỉ ghi 1 dòng khi vấn đề nghiêm trọng (DEC-111): vượt quyền COO
  VÀ đã thử mọi cách trong thẩm quyền (chi tiền, cam kết ngoài, thay đổi
  không đảo ngược, pháp lý, tắc >24h, xung đột, vượt ngân sách, lỗi hệ
  thống); một vấn đề một dòng; không gửi việc COO tự quyết được, việc CEO
  đã quyết, việc thường kỳ. Không đặt hạn trả lời — CEO trả lời khi rảnh
  (DEC-115).
- **Đọc và thực hiện lệnh CEO:** CEO ghi quyết định vào G CEO_REPLY (kèm
  ngày trả lời trong cùng ô G). Phòng chức năng ĐẦU TIÊN đọc lệnh ghi H
  APPLIED_BY (tên phòng mình) + I DATE (ngày nhận lệnh) rồi thực thi NGAY,
  không chờ COO. Chỉ đọc lệnh khi H và I đều trống (dòng đã có H hoặc I
  thì đã có phòng khác đọc/thực thi — bỏ qua, không thực hiện lại) VÀ C
  ASSIGNEE_EMAIL = email khai báo của chi nhánh mình. Pipeline đọc phản
  hồi CEO đầu mỗi ca (bước 2(g) trong body cron prod-pipeline) và COO đọc ở ca quét 06:00 — chỉ đọc /
  chuyển lời, không ghi gì vào CEO_REPORTS.
- **Đối chiếu liên chi nhánh trước khi kết luận durable:** trước khi ghi
  kết luận "chưa sản xuất / chờ CEO quyết" về một chủ đề, phải đọc live
  TASKS + QA_LOG + Drive theo TOPIC_ID và ghi kèm thời điểm kiểm chứng.

## 9. Cách làm việc với CEO

- CEO quyết mọi lựa chọn vật chất sau khi thấy phương án kèm ưu/nhược.
  **Với bất kỳ yêu cầu phân tích nào, luôn lên các phương án để CEO quyết
  định, không tự quyết thay CEO sau khi phân tích.** Trình từng việc một,
  quyết xong việc này mới sang việc tiếp theo.
- **Trước bất kỳ lần push GitHub nào, gửi phân tích cho COO để COO trình
  CEO qua CEO_REPORTS đọc trước** (file nào đổi, đổi gì, vì sao, rủi ro và
  ảnh hưởng gì); chỉ push sau khi CEO duyệt riêng. Phê duyệt sửa file
  không phải là phê duyệt push. Không tự push ngay sau khi sửa xong.
- Giải thích đơn giản, ví dụ cụ thể TRƯỚC, rồi mới nói kỹ thuật. Khi sự
  thật đã đổi so với lúc phát hiện vấn đề, kiểm chứng lại live và trình
  lại bằng số liệu mới, nói rõ cái gì đã đổi.
- Tin nhắn ngắn, trực tiếp, làm việc cụ thể thay vì giải thích cách làm.
  Chỉ hỏi đúng phần còn thiếu, một lần một câu hỏi.

## 10. Luật media — ảnh thật trước

- Kịch bản Việt Nam: **thử ảnh thật từ bài báo về đúng vụ việc / bài đăng
  công khai trước** (tìm bằng nhiều từ khóa tiếng Việt, nhiều cụm từ đồng
  nghĩa, ghi nhật ký từng cảnh trong `media-log.json` + `broll-plan.json`);
  chỉ dùng AI làm fallback khi đã thử nhiều từ khóa mà không có ứng viên
  phù hợp, và ghi rõ là ảnh AI minh họa, kèm câu "AI từ prompt, không có
  ảnh tham chiếu, đã thử các từ khóa:...". Không bao giờ ghi nhãn
  "AI generic".
- `keywordsTried` trong media-log phải là **danh sách chuỗi** (cụm từ);
  danh sách dict làm preflight chặn toàn bộ scene.
- Ảnh báo không logo/watermark/chữ thì dùng thẳng kèm ghi nguồn (theo
  quyết định chịu rủi ro của CEO 29/10/2026). Có logo/watermark/chữ thì
  crop trước; nếu không crop được thì AI-regenerate dùng chính ảnh gốc làm
  tham chiếu ("Tạo ảnh giống ảnh tham chiếu, chỉ loại bỏ chữ hoặc
  watermark trên ảnh"), không bao giờ phỏng lại bằng text-prompt.
- Cửa chặn code A20 (`bin/preflight.py`): chặn khi scene thiếu nhật ký tìm
  kiếm, thiếu nguồn (`mediaSource.source` trống), hoặc chỉ có nền xanh rêu.
- Nền xanh rêu kẻ ô (`#1C372A`, kẻ `#2A4D3B`, ô 80px, không chữ) là
  placeholder, **không bao giờ tính là ảnh**; scene chỉ có nền này vẫn tính
  là thiếu ảnh ở tầng hồ sơ/QA. Thẻ chữ (card) không thay thế ảnh.
- Nhân vật có tên: nhóm A (nhân vật công chúng có nhiều thông tin công
  khai đã kiểm chứng, vd tổng thống Mỹ, Messi, Chủ tịch nước Tô Lâm) được
  tạo chân dung AI nếu cần thiết, sau khi đã tìm ảnh thật mà không có ứng
  viên phù hợp, vẫn phải ghi rõ là ảnh AI minh họa không phải ảnh thật;
  nhóm B (nhân vật thiếu thông tin) chỉ góc rộng/sau lưng/bóng mờ/vật
  chứng, không cận mặt, không dùng tên làm chỉ dẫn ngoại hình; không chắc
  thì xếp nhóm B. Chi tiết ở `company-os/media-search/LOGIC.md` (chuẩn).
- Nhánh Việt Nam: ảnh chỉ từ báo/mạng xã hội về đúng vụ việc — **không
  dùng Wikipedia hay Stock cho ảnh** (ngoại lệ Wikipedia/Stock chỉ cho
  video). Stock Pixabay/Pexels đã nối qua Secure Vault (connector
  custom.pixabay / custom.pexels, đã kiểm chứng live 08/11/2026) nhưng
  không đổi luật ảnh theo nhánh này.

## 11. Sản xuất — chuỗi làm việc + bẫy đã biết

- Chuỗi: tạo project + `build_plan.py` → CSV pronunciation prepass →
  normalize (TTS venv) → xem `build/norm_chunks.json` → `abbr_dict.json`
  nếu cần → normalize lại → TTS (`tts_batch.py`, TTS venv) → ảnh
  (`gen_images.py`, factory venv; scene đã có ảnh thật thì job được bỏ qua)
  → karaoke → preflight → select_bgm → renderDraft → export (720x1280,
  giọng Hữu Quân, tốc độ 1.0).
- **Bẫy TTS (DEC-037):** `tts_batch.py` bỏ qua part đã có WAV hợp lệ.
  Sau khi sửa voiceText/voice/speed của part nào thì XÓA WAV của part đó
  trước khi chạy lại TTS; sau khi tách/gộp/đánh lại số part thì XÓA TOÀN
  BỘ WAV của scene bị ảnh hưởng (cả part files lẫn voice_seg).
- **Móc lại ở ~50% video** (dải đã duyệt 44,9–59,9%): lên kế hoạch từ đầu,
  QA trả lại nếu ngoài dải.
- Kiểm tra mẫu cấm TRÊN FILE CUỐI (script.json/plan) sau MỖI lần sửa
  voiceText, không chỉ lúc tạo plan lần đầu (bản kiểm tra trong
  build_plan.py đã từng bỏ sót 1 hit thật). Tối đa 1 câu hỏi thật/video.
- Số liệu trong voiceText giữ nguyên ký hiệu (`10%`, `35°C`, `$5`); ngày
  tháng viết bằng chữ ("ngày 3 tháng 11"); khoảng năm viết bằng chữ
  ("giai đoạn từ năm 2021 đến năm 2030") vì dấu en-dash làm TTS đọc chậm.
- Số từ karaoke phải khớp đúng từng từ với các part không template, 0
  WARN; token số dài đọc chậm là HỢP LỆ, không phải lỗi timing.
- Dài video: đề xuất 2–3 phút, dài hơn được khi nội dung đã kiểm chứng;
  bàn giao phải ghi thời lượng thật, không làm tròn vào "trong đề xuất".
- Chi tiết đầy đủ ở skill media-video-production.

## 12. Cấu trúc Sheet (đang chạy)

- TOPICS 13 cột A–M (A TOPIC_ID, B TITLE, C SOURCE, D DISCOVERED, E–I
  điểm, J TOTAL = công thức `=SUM(E:I)`, K STATUS dropdown NEW / APPROVED
  / READY / HOLD / REJECTED / DUPLICATE, L ANGLE, M NOTES). Cột N
  APPROVED_AT đã bỏ. Scout ghi dòng mới (TOPIC_ID để trống); CEO ghi A TOPIC_ID + flip K APPROVED→READY; Production/Pipeline chỉ đọc.
- TASKS 15 cột A–O: A TOPIC_ID, B TITLE, C STATUS, D ASSIGNEE,
  E DRAFT_LINK, F QA_VERDICT, G RETURNS, H DRIVE_LINK, I MD5,
  J UPDATED_AT (chỉ ngày, dạng YYYY-MM-DD), K PROD_NOTES (Production),
  L QUOTA (QA), M BLOCKER (COO), N DUP_NOTE (Pipeline), **O FACEBOOK —
  tồn tại live, do bên khác quản lý, để nguyên, không động vào** (DEC-081).
  Một cột, một người viết (R2): Production viết C/E/K/J; QA viết F/G/H/I/L;
  Pipeline viết A/B/D lúc claim. C/J/D chấp nhận "ghi sau thắng"; ai ghi C
  phải ghi thêm lý do + thời gian vào cột ghi chú của mình trong cùng lần
  ghi.
- QA_LOG 6 cột A–F (VIDEO_ID, VERSION, DATE, RESULT, ISSUES, REPO_NOTE),
  append-only.
- DECISIONS 7 cột A–G: A DECISION_ID, B ISSUE, C OPTION_A, D OPTION_B,
  E COO_PROPOSAL, F CEO_DECISION, G DATE (ngày quyết). Ghi đủ 7 giá trị
  A–G cho mỗi quyết định đã chốt; người ghi là COO.
- COO_TASKS 7 cột A–G (mục 8).
- CEO_REPORTS 9 cột A–I: G = CEO_REPLY, H = APPLIED_BY, I = DATE (mục 8).
- Múi giờ workbook: Asia/Saigon. Mọi dropdown strict.

## 13. Lịch bot (4 lịch công ty)

- 1 Scout (06:00) + 1 Pipeline (06:00) + hoc-hoi 20:00 (đọc Sheet + improvement-log.md, xuất mục log ĐỀ XUẤT về chat COO; không tự sửa file chuẩn, không push — quyết CEO 11/11/2026) + coo-scan 06:00 (mục 8). Tất cả daily, múi giờ Asia/Saigon, báo
  cáo về chat COO (delivery về chat COO).
- ID lịch: prod-pipeline-0600, scout-scan-0600, coo-scan-0600,
  bot-hoc-hoi-2000.
  Owner goal trong file mẫu (mặc định chung): vieneu-media-company-bootstrap.
  Owner goal thật của chi nhánh này: vieneu-media-company-repo-setup — cả 4 lịch đang chạy đều thuộc goal này.
- Bộ mẫu trong `company-os/crons/daily/` + hướng dẫn
  `company-os/scheduled-tasks-setup.md`: body mẫu giống body lịch đang chạy
  trừ 5 placeholder `{{CHAT_ID_SCOUT_BAO}}`, `{{CHAT_ID_SCOUT_GROUP}}`,
  `{{CHAT_ID_SAN_XUAT}}`, `{{CHAT_ID_QA}}`, `{{CHAT_ID_COO}}`. **Không copy nguyên văn:**
  thay 5 ID chat phòng theo tài khoản mới qua `chat.list`, kiểm tra trước
  khi tạo (grep `{{` = 0, grep UUID/@vuachim = 0). Không tự cài lịch khi
  clone — chỉ cài khi CEO nói "cài bộ lịch mẫu".
- Sửa lịch chỉ qua `cron.update` (body đầy đủ đã sửa); file `.md` dưới
  `workspace/goals/<goal>/crons/` là bản sao chỉ đọc — sửa file đó không
  đổi lịch đang chạy.

## 14. Trạng thái hiện tại (09/11/2026 ~02:30 +07)

- TASKS: 45 dòng dữ liệu (44 DELIVERED + 1 CANCELLED), **0 dòng đang làm
  dở**. Tối 08/11/2026 CEO đã xóa 9 dòng cuối (TOPIC-277 BUILDING + 278,
  279, 283, 284, 287, 291, 292, 294 CLAIMED) vì Production không làm việc
  dù ở trạng thái CLAIMED/BUILDING — KHÔNG khôi phục. Các chủ đề vẫn READY
  trong TOPICS.
- Ca pipeline 06:00 09/11 dừng theo DEC-202 (token tuần 100% > 95%, claim 0; Scout không quét); claim lại từ ca 18:00 sau reset 14:14.
- Hạn mức (đọc lần cuối lúc upload TOPIC-273, 15:12 08/11/2026): tuần Muse
  đã dùng 100%, còn 0%, reset 09/11 lúc 14:14 +07; token thêm còn ~892M.
  Đọc lại hạn mức tại mỗi lần upload (TASKS.L QUOTA).
- DECISIONS đã ghi tới DEC-200 (dòng 201) — snapshot tại thời điểm viết lại file này (09/11/2026). Rà soát lần 7 đã xong toàn bộ
  37 mục (DEC-161→DEC-197) + DEC-198 (đính chính phát hiện sai về cột G)
  + DEC-199 (trần 3). Rà soát lần 6 (42 mục) đang chờ CEO quyết từng cái.
- Chủ đề chờ CEO: Kraków (83đ, APPROVED, TOPIC_ID còn trống — 09/11 là
  ngày cuối quốc tang Ba Lan 8–9/11, hết mới thì khó làm) và TOPIC-295
  (bánh mì Quảng Ngãi, 74đ, APPROVED — cần flip READY mới sản xuất được).
- TOPIC-233: Drive có bản nháp 348s từ 05/11/2026 trong khi hồ sơ nói chưa
  từng sản xuất — chờ CEO quyết, không tự sản xuất.
- TOPIC-219: CANCELLED 07/11/2026 theo quy tắc ngày hiện tại; không sửa,
  không re-render khi chưa có giao việc mới.
- TOPIC-250: video đã duyệt thuộc chi nhánh khác; chi nhánh này KHÔNG nộp
  QA, không làm lại.

## 15. Bài học lớn (vì sao có các luật trên)

- **TOPIC-219 (04/11/2026):** hai bản nháp đều dùng toàn ảnh AI, không
  tìm ảnh thật — CEO phản hồi "tất cả đều là ảnh AI". Từ đó ảnh thật trước
  là cửa chặn cứng (mục 10), QA trả lại nếu thiếu nhật ký tìm ảnh.
- **TOPIC-232 (05/11/2026):** thẻ phê duyệt upload Drive hết hạn sau 30
  phút → thao tác không chạy, không ghi dòng Sheet, không chuyển sang
  Duyệt. Cách tránh: chắc CEO đã cấp phép toàn quyền hoặc đang có mặt để
  bấm thẻ trong 30 phút; hết hạn thì chạy lại 1 lần lấy thẻ mới và báo COO
  ngay (mục 7).
- **TOPIC-277 (08/11/2026):** Production tự lấy video lúc 15:13 rồi báo
  cáo xong DỪNG, không làm tiếp — video chưa từng được bắt đầu, CEO xóa
  dòng. Từ đó: báo cáo xong thì LÀM TIẾP trong cùng lượt (mục 3).
- **Đọc dòng dài (bài học L7, 08/11/2026; học lại 09/11/2026 khi đổi trần
  4→3):** dòng dài trong file có thể bị cắt khi đọc — đọc đủ dòng bằng
  `sed -n` / `grep -o` có ngữ cảnh trước khi kết luận; grep nhiều cách diễn
  đạt; bộ lọc `grep -v` có thể nuốt cả dòng dài chứa cả cụm đúng lẫn cụm
  sai. Kiểm chứng bằng diff và quét không lọc.
- **Kiểm chứng live trước khi kết luận về cấu trúc Sheet (DEC-198,
  09/11/2026):** đừng suy số cột của một tab từ các dòng dữ liệu — đọc
  header live. Một lần báo nhầm "DECISIONS chỉ có 6 cột" (thực tế 7 cột
  A–G, G=DATE) đã khiến CEO phải đính chính và ghi DEC-198.
- **Mất dòng trên Sheet dùng chung:** workbook cũ mất 151 dòng 06_Topics
  qua một đêm 06→07/11/2026 (không rõ ai xóa); một dòng tab 08 của
  TOPIC-232 đã ghi ngày 05/11 rồi mất. Vì vậy R7: mất dòng không dừng ca,
  không báo cáo; và không xóa dòng Sheet khi chưa snapshot + CEO duyệt.
- **TOPIC-228/184 (08/11/2026, DEC-080):** CEO quyết bỏ cả hai, không
  khôi phục vào workbook mới dù nội dung gốc vẫn còn trong file baseline
  ca Scout 06:00 ngày 06/11. Quyết bỏ là quyết bỏ — phòng không ghi lại
  dù sự kiện diễn ra.
- **TOPIC-004 v2** đã lên Drive từ 29/10/2026 mà chưa từng có dòng theo
  dõi nào; CEO quyết giữ nguyên checklist, không sửa — bản ghi thiếu vẫn
  để đó, chưa có quyết định khôi phục.

## 16. Chi nhánh mới — danh sách khai báo (B1)

Sau khi clone repo xong, chat chính CHỦ ĐỘNG hỏi CEO bổ sung các thông tin
sau (không chờ CEO tự biết phải cung cấp gì). CEO trả lời trong chat chính
(gộp một lần hoặc từng mục); agent lưu từng câu trả lời vào MEMORY.md của
chính nó ngay khi nhận được (nguyên văn, kèm ngày giờ) rồi xác nhận lại
những gì đã lưu và còn thiếu mục nào. Mục nào chưa trả lời thì ghi "chưa
xác định" và dừng đúng bước cần nó, không đoán.

1. **Email khai báo** (định danh chi nhánh — xem Cảnh báo đầu file).
2. Workbook vận hành (dùng chung — mục 2; nếu CEO chỉ workbook khác thì
   ghi rõ ID).
3. Thư mục Drive "Video Muse" (dùng chung — mục 2).
4. Repo (dùng chung — mục 2).
5. Cấp phép toàn quyền cho QA (để QA hoàn tất bàn giao Drive mà không hỏi
   lại trong chat; thẻ hệ thống vẫn hiện mỗi lần upload và cần bấm trong
   30 phút).
6. Lịch bot (4 lịch mục 13 — chỉ cài khi CEO nói "cài bộ lịch mẫu").
7. Facebook (chỉ khi công ty có nhu cầu — tài khoản/mục đích do CEO nói).
8. Ngưỡng inline voice — ĐÃ QUYẾT: 10.000.000 byte (file trên 10 MB đi
   đường chunked download; chỉ thông báo, không hỏi). Đã kiểm chứng 09/11/2026: code getMediaUrl = 10.000.000 byte, khớp quyết định.
9. Đường dẫn factory — ĐÃ QUYẾT, ĐÃ GHI VÀO REPO (tài khoản mới không sửa
   đường dẫn; chỉ thông báo, không hỏi).
10. API key Pixabay + Pexels qua Secure Vault (key miễn phí: pixabay.com/api,
    pexels.com/api; không nhập key vào chat; sau khi cấp, tạo connector
    custom.pixabay/custom.pexels rồi kiểm chứng bằng 1 lần search_stock thật).
    Thiếu key thì lớp stock báo SKIPPED, Production rơi về AI — không chặn
    ca quét. Không ghi giá trị key vào MEMORY.md. Tham số Vault và đường kiểm chứng xem BOOTSTRAP §2.1 mục 10.

---

_Snapshot 09/11/2026 — chi nhánh gốc. Khi luật đổi, cập nhật file này trong
cùng lần đổi. Quyết định mới nhất trong file: DEC-200 (viết lại toàn bộ file
này theo lệnh CEO 09/11/2026).
Tra cứu đầy đủ: tab DECISIONS trong workbook dùng chung._
