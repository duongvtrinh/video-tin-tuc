# BOOTSTRAP — Dựng lại toàn bộ hệ thống từ repo này (đọc trước khi làm gì khác)

Repo này là monorepo duy nhất cần clone. Nguyên tắc: làm đúng thứ tự
dưới đây. Mỗi bước có kiểm chứng và kết quả kỳ vọng. Bước nào kiểm
chứng fail thì DỪNG, ghi lại lệnh + output, báo người vận hành — không
tự chế, không bỏ qua bước kiểm chứng, không đoán. "Dựng xong" chỉ được
kết luận khi tất cả kiểm chứng đều pass.

## 0. Clone (repo RIÊNG TƯ)

Clone repo này về máy Muse mới. Quyền đọc qua cùng tài khoản GitHub /
Muse GitHub App, KHÔNG BAO GIỜ chuyển repo sang public.

## 1. Điều kiện tiên quyết (không có trong git, phải tự có)

- `ffmpeg` cài sẵn; Python 3.12 (khớp venv factory đang chạy; riêng TTS chạy được từ Python 3.10+ theo README của nó).
- Tài khoản Google riêng để liên kết Sheet/Drive qua connector
  (không nhập mật khẩu vào chat, không ghi vào git).
- Mạng tới HuggingFace để tải model TTS lần đầu (vài trăm MB).
- KHÔNG cần mật khẩu, token hay bộ nhớ của Muse cũ. Mọi credential
  liên kết lại từ đầu.

## 2. VieNeu TTS (`vieneu-tts/`)

- Chạy `./start.sh` trong `vieneu-tts/` → tạo venv, cài requirements,
  tải model.
- Kiểm chứng: `.venv/bin/python tts_cli.py --text "Xin chào cả nhà!"
  --voice "Hữu Quân" --speed 1.0 --out out.wav` → ra file WAV nghe được (chạy ở terminal khác vì `start.sh` kết thúc bằng `uvicorn` foreground).
  Kỳ vọng theo README: lần đầu load model ~7 giây, RAM ~450MB,
  giới hạn 5000 ký tự/request.
- Lưu ý: `.venv/` (~896MB) và model cache KHÔNG nằm trong git, đừng
  tìm trong repo.

## 3. Asset Factory (`vieneu-asset-factory/`)

- Tạo venv của factory và cài dependency (bắt buộc trước khi chạy script):
  `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
  trong `vieneu-asset-factory/` (Pillow, numpy, weasyprint, underthesea,
  websocket-client, yt-dlp). Hệ thống cần thêm: `ffmpeg` và font Anton (templates
  dùng Anton — cài từ Google Fonts vào `~/.fonts` rồi `fc-cache`).
- Quy tắc venv (bắt buộc): script factory (`karaoke.py`,
  `preflight.py`, `render_draft.py`...) chạy bằng venv của factory;
  riêng `tts_batch.py` và `normalize_chunks.py` PHẢI chạy bằng venv
  của TTS vì bộ chuẩn hoá sea-g2p nằm trong đó (đường dẫn venv TTS
  resolve theo `_tts_dir()` trong `tts_batch.py`: biến `VIENEU_TTS_DIR`,
  rồi `vieneu-tts`, rồi `vieneu-tts-api`).
- Kiểm chứng: `python -m py_compile bin/*.py` không lỗi;
  `ffmpeg -version` chạy được; đọc `PIPELINE.md` để nắm đúng thứ tự
  createProject → saveScript/savePlan → runTTS → generateImages →
  runNormalize → runKaraoke → runPreflight → selectBgm → startRenderDraft → exportProject.

## 4. Skills (logic vận hành — đây là "bối cảnh" được share)

- Copy 4 skill từ `company-os/skills/` vào `custom-skills/` của Muse
  mới: `media-coo`, `media-scout`, `media-video-production`,
  `media-video-tech-qa`. (Skill `media-topic-scoring` đã đóng cùng chat
  Scoring ngày 07/11/2026, quyết định C3 — thang điểm đã chuyển vào
  `media-scout`, không copy skill này nữa.)
- Đọc kỹ trước khi chạy: `media-video-production` (pipeline, luật TTS,
  luật media), `media-video-tech-qa` (3 cửa QA), `media-scout`
  (luật quét nguồn công khai + chấm điểm ngay trong cùng lượt quét:
  thang 100 + cửa quan tâm Hot + Khán giả ≥ 30), `media-coo`
  (phối hợp qua Sheet).
- Các luật đã chốt nằm trong skill, không nằm trong MEMORY của Muse cũ
  — đó là lý do dựng lại được mà không cần bộ nhớ cũ.
- Bắt buộc đọc `company-os/media-search/LOGIC.md`, đặc biệt bài học
  TOPIC-219 04/11/2026: tìm ảnh thật từ bài báo về đúng vụ việc / bài
  đăng công khai trước, AI từ prompt chỉ là fallback khi đã thử nhiều
  từ khóa mà không có ứng viên phù hợp, nền xanh rêu kẻ ô vuông (không chữ) không thay thế ảnh.
  Hai điều bắt buộc theo LOGIC.md (mục 2 và mục 5 — bổ sung 05/11/2026, mục A30): (a) nhật ký tìm ảnh là bắt buộc cho mỗi cảnh — từ khóa đã thử, ứng viên tìm được (link + nguồn), phân loại và lý do loại, thiếu nhật ký thì cảnh đó chưa đủ điều kiện render; (b) QA TRẢ LẠI video nếu thiếu nhật ký, không duyệt im lặng.
  Tài khoản Muse mới clone repo về mà bỏ qua mục này sẽ lặp lại đúng
  sai sót TOPIC-219 (toàn ảnh AI / nền xanh rêu kẻ ô vuông dù bài gốc đã có ảnh thật).

**Khai báo chữ ký định danh cho tài khoản Muse mới (lệnh CEO 05/11/2026 — bắt buộc trước ca quét tab COO_TASKS đầu tiên):**
- Hệ thống Muse không cho agent đọc email đăng nhập của chính nó, nên email trong cột B tab COO_TASKS không thể tự đối chiếu bằng hệ thống. Mỗi tài khoản Muse phải khai báo email của mình một lần và lưu vào bộ nhớ của chính tài khoản đó như chữ ký định danh.
- Cách khai: CEO nói cho tài khoản đó biết email của nó (qua chat chính hoặc chat COO); tài khoản đó ghi vào MEMORY.md dòng: "Email khai báo của tài khoản Muse này: <email> — dùng làm chữ ký định danh, đối chiếu cột B tab COO_TASKS" và lưu tên COO chính là email khai báo đó (ví dụ COO (006@vuachim.com) — tên COO là email khai báo, không phải tên người).
- Bộ nhớ là của từng tài khoản, không đi kèm repo khi clone: tài khoản khác clone repo về sẽ có bộ nhớ trống, phải khai lại từ đầu, không được copy email của tài khoản cũ sang, không được dùng email dịch vụ khác (Drive/GitHub/Facebook) thay thế.
- Nếu bộ nhớ chưa có email khai báo, COO không được nhận bất kỳ dòng tab COO_TASKS nào; phải báo CEO qua CEO_REPORTS để CEO khai báo trước, không đoán. Email khai báo là khai báo, không phải xác thực hệ thống: khai sai thì tài khoản sẽ nhận nhầm dòng hoặc bỏ qua dòng đúng, CEO chịu trách nhiệm về email đã khai cho từng tài khoản.

## Khởi tạo tài khoản Muse mới (mục duy nhất, các skill/spec chỉ trỏ về đây)

Khi một tài khoản Muse mới clone repo về, làm đúng 3 nhóm việc — cài đặt, khai báo, kiểm chứng — rồi mới bắt đầu ca quét tab COO_TASKS đầu tiên. Không bước nào được đoán, không bước nào được bỏ. (Chốt ngày 06/11/2026 theo lệnh CEO — phương án A.)

### 0. Mô hình vận hành công ty (CEO mô tả 06/11/2026)

1. **CEO** ra lệnh duy nhất qua tab CEO_REPORTS; lệnh từ chat chính hay COO đều tính là lệnh của COO. CEO giao nhiệm vụ cho COO qua Sheet tab COO_TASKS.
2. **Mỗi tài khoản Muse là một chi nhánh công ty độc lập**, tự sản xuất video, có COO
   quản lý điều phối công việc cùng các bộ phận chức năng khác.
3. **Mỗi chi nhánh được định danh bằng một Email** (người dùng cung cấp email của tài
   khoản Muse đang hoạt động). Khi COO hoặc các bộ phận chức năng gửi báo cáo vào Sheet
   thì dùng chung định danh này để xác nhận/ký nhận danh tính người hoàn thành công
   việc, để phân biệt với các chi nhánh công ty khác.
4. **Định danh của chi nhánh phải khai báo khi Muse vừa được clone về** (gợi ý là email
   của tài khoản Muse đang hoạt động) — xem mục 1.8 và 2.2.
5. Hệ quả: Sheet vận hành dùng chung cho nhiều chi nhánh; luật một nhiệm vụ = một chủ sở
   hữu và khóa bằng dòng TASKS CLAIMED càng quan trọng để tránh hai chi nhánh làm trùng một việc
   (mục 3.4). Các phòng trong cùng một chi nhánh dùng chung định danh chi nhánh khi báo
   cáo; không dùng email của chi nhánh khác hay email dịch vụ khác thay thế.


### 1. Cài đặt bổ sung — những gì tài khoản mới phải có trước khi làm việc

#### 1.1 Kết nối tài khoản (qua luồng kết nối chính thức, không nhập mật khẩu vào chat)

| # | Kết nối | Dùng để làm gì | Kiểm chứng xong khi |
| --- | --- | --- | --- |
| 1 | **GitHub** — tài khoản `duongvtrinh` | Clone repo private `duongvtrinh/vieneu-media-company`, nhánh `main` | Đọc được repo, đúng nhánh `main`, repo vẫn private |
| 2 | **Google Sheets** | Workbook vận hành `Video HQ — Trụ sở Muse` (ID `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`) — dùng workbook đang chạy, **không tạo mới, không ghi đè** | Đếm đủ 7 tab (TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN), tab COO_TASKS đúng 7 cột A–G, tab CEO_REPORTS đúng 9 cột A–I, tab COO_CHECKIN đúng 3 cột A–C (xem mục 3.2) |
| 3 | **Google Drive** | Thư mục `Video Muse` (ID `1bA21n3Y3YiY6HSjLUEFmxnJXLnjtSJGc`) — chỉ bàn giao video đã QA duyệt lên đây | Mở được thư mục, thấy file TOPIC-232 đã bàn giao |
| 4 | **Facebook** (chỉ khi làm việc Facebook) | Liên kết lại qua Meta Accounts Center | CEO xác nhận đã liên kết — `facebook-cli me` không chứng minh được |

#### 1.2 Môi trường trên máy (kiểm theo BOOTSTRAP §0–§3, thiếu thì cài theo BOOTSTRAP)

- `ffmpeg`, Python 3.12, Pillow (PIL), `bun`.
- Factory venv (`vieneu-asset-factory/.venv`) và TTS venv (`vieneu-tts/.venv`) + engine VieNeu
  giọng đọc (11 giọng preset: Adam, Ái Hân, Mỹ Duyên, Đức Trí, Hữu Quân, Xuân Tiên, Mai Anh,
  Trúc Ly, Anh Khôi, Minh Quân, Mạnh Dũng).
- App-tao-video đúng **47 file** (không phải 48) — đếm bằng
  `find app-tao-video -type f | wc -l`; khác 47 thì dừng và báo COO, không tự sửa số.

#### 1.3 Tài sản nhị phân — đã nằm trong git từ 04/11/2026, clone là có

- `vieneu-asset-factory/sfx/`: đủ 8 file `.mp3` khác 0 byte.
- `vieneu-asset-factory/bgm/`: đủ 24 track (3 track/mood: calm, dramatic, funny,
  inspirational, news, sad, suspense, upbeat) + `README.md` + `bgm_catalog.json`.
- Thiếu thì khôi phục từ bản backup trên Drive theo BOOTSTRAP §7, không tự tải nguồn khác.

#### 1.4 Skills — đồng bộ 2 bản, kiểm md5 phải khớp

- 4 skill trong repo (`company-os/skills/`) phải khớp tuyệt đối với bản custom
  (`~/workspace/custom-skills/`): media-coo, media-scout,
  media-video-production, media-video-tech-qa. (Skill `media-topic-scoring`
  đã đóng cùng chat Scoring ngày 07/11/2026, quyết định C3.)
- Kiểm chứng bằng lệnh (không ghi mã md5 cố định vào đây — mã đổi sau mỗi lần sửa skill, bảng ghi sẵn sẽ cũ ngay): chạy `md5sum ~/workspace/custom-skills/media-*/SKILL.md ~/workspace/vieneu-media-company/company-os/skills/media-*/SKILL.md` rồi đối chiếu từng cặp (media-coo, media-scout, media-video-production, media-video-tech-qa; + stub media-topic-scoring đã đóng, chỉ để lưu lịch sử) — 5/5 cặp phải khớp tuyệt đối. Tài khoản mới copy skill từ repo sang custom
  rồi kiểm lại md5; lệch thì dừng và báo COO.

#### 1.5 Chat nhân viên — tạo mới 5 chat, mỗi chat một skill

Scout - Báo, Scout - Group, Sản xuất, Kỹ thuật QA, COO. Mỗi chat gắn đúng skill
của phòng đó (2 chat Scout dùng chung skill media-scout, đã gộp chấm điểm).
Phòng chỉ làm việc khi được giao qua đúng 1 trong 3 kênh (mục 3.4).

#### 1.6 Artifact "App tạo video" — tài khoản mới tự build từ repo

- Build bằng `artifact.create_web_fullstack`, tên "App tạo video", slug `app-tao-video`,
  từ đúng 47 file repo. Lần build đầu (05/11/2026): platformVersion 28,
  typecheck đạt, 14/14 test script-prompt pass, `listProjects` trả đủ 4 project thật.
- Tài khoản mới build lần đầu sẽ tự có các sửa app từ B-series (B18–B41) vì build từ
  source repo hiện tại — không cần làm thêm bước nào cho các sửa đó.
- Sau này, mỗi lần sửa code app xong thì build lại mới có hiệu lực trên app đang chạy;
  sửa factory Python thì có hiệu lực ngay cho lần chạy pipeline sau.

#### 1.7 Lịch — mặc định KHÔNG tạo lịch nào

- Không bật Scout (4 ca/ngày: 06:00, 10:00, 14:00, 18:00), Pipeline
  (4 ca/ngày, cùng giờ) hay bot-hoc-hoi (chạy hằng ngày 20:00 — cron
  bot-hoc-hoi-2000, quyết CEO 07/11/2026, DEC-019; Q6 đã đóng) trừ khi
  CEO duyệt riêng.

#### 1.8 Chat chính chủ động hỏi bổ sung thông tin — ngay sau khi clone xong (lệnh CEO 06/11/2026)

- **Thời điểm:** ngay sau khi clone xong, đọc BOOTSTRAP (§0–§4) và kiểm tra môi trường
  xong (mục 1.2). Chat chính **KHÔNG chờ CEO tự biết phải cung cấp gì** — Chat chính là
  bên chủ động gửi tin nhắn hỏi.
- **Nội dung tin nhắn:** Chat chính gửi 1 tin nhắn liệt kê đúng các thông tin còn thiếu
  để công ty vận hành (danh sách mục 2.1), dưới dạng câu hỏi, kèm ví dụ mẫu cho từng
  mục. Mẫu tin nhắn:
  > Chào CEO, tôi đã clone repo xong. Để công ty vận hành được, tôi cần CEO cung cấp
  > thêm các thông tin sau (trả lời gộp một lần hoặc trả lời từng mục đều được, tôi sẽ
  > lưu từng câu trả lời vào bộ nhớ; mục 8–9 đã quyết, chỉ thông báo):
  > 1. Email khai báo của tài khoản Muse này là gì? (vd 006@vuachim.com — dùng làm chữ
  > ký định danh, đối chiếu cột B tab COO_TASKS)
  > 2. Workbook vận hành có phải "Video HQ — Trụ sở Muse" không? (xác nhận dùng workbook
  > đang chạy, không tạo mới)
  > 3. Thư mục Drive bàn giao có phải "Video Muse" không? Quyền hiện tại ra sao?
  > 4. Repo GitHub có phải duongvtrinh/vieneu-media-company, nhánh main, private không?
  > 5. CEO có cấp phép toàn quyền cho QA hoàn tất bàn giao không? (để QA chạy lại upload
  > mà không hỏi lại trong chat; thẻ phê duyệt của hệ thống vẫn hiện mỗi lần upload và vẫn
  > cần bấm trong 30 phút)
  > 6. Lịch bot có bật không? Mặc định: không bật — chỉ bật khi CEO duyệt riêng. Nếu bật thì gồm:
  >    - Pipeline 4 ca/ngày (06:00, 10:00, 14:00, 18:00): sản xuất video đã duyệt (mỗi ca nhận tối đa 3 chủ đề READY, làm tuần tự; không giới hạn số video đã bàn giao/ngày).
  >    - Scout 4 ca/ngày (cùng giờ): tìm chủ đề được quan tâm + chấm điểm ngay trong cùng lượt quét.
  >    - bot-hoc-hoi: chạy hằng ngày 20:00 (cron bot-hoc-hoi-2000, quyết CEO 07/11/2026, DEC-019; Q6 đã đóng); rút bài học từ lỗi lặp lại có bằng chứng, cải tiến
  >      template/skill/SOP; đổi chuẩn thì chỉ đề xuất để CEO quyết.
  >    - COO quét COO_TASKS 06:00 hàng ngày (cron coo-scan-0600, quyết CEO 08/11/2026, DEC-099): điểm danh tại tab COO_CHECKIN (Bước 0, lệnh CEO 09/11/2026) trước, rồi đọc tab COO_TASKS, nhận dòng của chi nhánh mình, giao phòng, xác nhận E–G; không có dòng thì im lặng. Đọc thêm CEO_REPORTS (Bước 6 trong body cron coo-scan-0600, quyết CEO 08/11/2026, DEC-112): phản hồi CEO mới từ 06:00 hôm qua tới nay, chuyển lời cho phòng liên quan hoặc tự thực hiện theo phản hồi.
  >    - Cửa chặn hạn mức tuần (quyết CEO 09/11/2026, DEC-202): đầu ca đọc TASKS.L QUOTA mới nhất của chi nhánh — nếu token tuần đã đạt trên 95% thì dừng hẳn ca này (Scout không quét/chấm/ghi, pipeline claim 0 chủ đề READY mới; ca dừng hẳn, không báo cáo ca); khi hạn mức tuần được reset thì công ty hoạt động trở lại bình thường, không cần lệnh mở lại; token thêm là dự phòng, không dùng để sản xuất video.
  > 7. Facebook đã liên kết lại qua Meta Accounts Center chưa? (không bắt buộc cho video;
  > cần kết nối để quét bài viết, group. Tôi không tự tham gia group mới, không tự đăng.)
  > 8. Ngưỡng inline voice đã quyết: 10.000.000 byte — file trên 10 MB đi đường
  > chunked download. (Mục này đã quyết, chỉ thông báo, không cần CEO trả lời.)
  > 9. Đường dẫn factory đã quyết, đã ghi vào repo — tài khoản mới không sửa
  > đường dẫn. (Mục này đã quyết, chỉ thông báo, không cần CEO trả lời.)
  > 10. CEO có cấp API key Pixabay và Pexels không? (key miễn phí, tạo tại
  > pixabay.com/api và pexels.com/api — để Production tìm ảnh thật thay vì rơi về AI.
  > Tôi sẽ gửi link Secure Vault để CEO nhập từng key; không nhập key vào chat.
  > Tham số Vault và đường kiểm chứng xem BOOTSTRAP §2.1 mục 10.)
- **CEO trả lời trong chat chính** — gộp một lần hoặc từng mục đều được.
- **Agent lưu vào bộ nhớ ngay khi nhận được từng câu trả lời:** ghi nguyên văn câu trả
  lời vào `MEMORY.md` của chính tài khoản này (kèm ngày giờ nhận), theo đúng mẫu câu ở
  mục 2.2; rồi xác nhận lại với CEO những gì đã lưu và còn thiếu mục nào.
- Mục nào CEO chưa trả lời thì ghi "chưa xác định" và dừng đúng bước cần nó — không
  đoán, không dùng thông tin của dịch vụ khác thay thế.
- Chỉ khi đã có đủ các mục bắt buộc (email khai báo, workbook, Drive, repo) thì mới ghi
  vào bộ nhớ ở mục 2.2 và đi tiếp sang ca quét đầu tiên ở mục 3.2.


### 2. Khai báo bổ sung — CEO cung cấp, tài khoản mới ghi vào bộ nhớ của chính nó

#### 2.1 CEO cung cấp qua chat chính — 2 bảng: phải cung cấp (A) và đã quyết chỉ đọc (B)

CEO cung cấp bằng cách **trả lời tin nhắn hỏi bổ sung của Chat chính ở mục 1.8**. Chỉ thiếu 1 trong 4 mục bắt buộc (1–4) mới dừng; mục 10 thiếu vẫn đi tiếp; mục 8–9 đã quyết, không hỏi CEO.

**Bảng A — CEO phải cung cấp** (mục 1–7 + 10; mục 10 là tùy chọn, thiếu vẫn đi tiếp):

| # | Thông tin | Ghi chú |
| --- | --- | --- |
| 1 | **Email khai báo của tài khoản Muse này** (vd `006@vuachim.com`) | **BẮT BUỘC.** Chữ ký định danh duy nhất. Đối chiếu **cột B** tab COO_TASKS, làm email người sản xuất ghi vào TASKS.L QUOTA. Tên COO chính là email này. **Đây chính là định danh của chi nhánh** (mục 0): mọi phòng trong chi nhánh dùng chung email này khi báo cáo lên Sheet để ký nhận người hoàn thành công việc. |
| 2 | **Workbook vận hành** — `Video HQ — Trụ sở Muse`, xác nhận dùng workbook đang chạy | 7 tab (TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN), tên tiếng Anh VIẾT HOA, không đánh số. Công ty khác thì tạo workbook mới từ spec — đúng 7 tab, bắt đầu trống. |
| 3 | **Thư mục Drive "Video Muse"** + quyền hiện tại | Chỉ bàn giao lên đúng thư mục này. **Không tự tạo thư mục khác, không tự thay đổi quyền.** Quyền anyone with link (nếu có) là do CEO cấp. |
| 4 | **Repo GitHub** — `duongvtrinh/vieneu-media-company`, nhánh `main`, private | Clone đúng repo này. Đọc BOOTSTRAP + 4 skill trước khi làm việc. |
| 5 | **Cấp phép toàn quyền cho QA hoàn tất bàn giao** (có hay không) | Bắt buộc trước lần upload Drive đầu tiên. Nếu chưa cấp: QA phải chắc CEO đang có mặt để bấm thẻ phê duyệt trong 30 phút. Nếu đã cấp: QA được chạy lại upload mà không hỏi lại trong chat — nhưng **thẻ phê duyệt của hệ thống vẫn hiện mỗi lần upload và vẫn cần bấm trong 30 phút**; cấp phép không tắt được thẻ hệ thống. |
| 6 | **Lịch bot có bật không** | Mặc định KHÔNG bật (xem 1.7). |
| 7 | **Facebook** — đã liên kết lại qua Meta Accounts Center chưa | Không bắt buộc cho lần khởi tạo video; bắt buộc trước khi làm việc Facebook. |
| 10 | **API key Pixabay + Pexels** — cấp qua Secure Vault, không nhập key vào chat (TÙY CHỌN — thiếu vẫn đi tiếp) | Key miễn phí: Pixabay tại pixabay.com/api, Pexels tại pexels.com/api. Chat chính gửi link Secure Vault (`credentials.request_api_access`: Pixabay `query_param:key`, host `pixabay.com`; Pexels `custom_header:Authorization`, host `api.pexels.com`) để CEO nhập từng key; sau khi lưu xong, tạo connector doc + helper (`custom.pixabay` / `custom.pexels`, xem `~/workspace/custom-connectors/`) rồi kiểm chứng bằng 1 lần `search_stock` thật qua `company-os/media-search/search_media.py`. Thiếu key thì lớp stock báo SKIPPED và Production rơi về AI — không chặn ca quét, nhưng ảnh thật sẽ thiếu. **Không bao giờ ghi giá trị key vào MEMORY.md, file hay log.** |

**Bảng B — Đã quyết, không hỏi, chỉ đọc** (mục 8–9):

| # | Thông tin | Ghi chú |
| --- | --- | --- |
| 8 | **Ngưỡng inline voice (4C) — ĐÃ QUYẾT: 10.000.000 byte** | Quyết 05/11/2026, đã sửa trong `handlers-media.ts` `getMediaUrl`. File trên 10 MB đi đường chunked download. |
| 9 | **Đường dẫn factory (3C/A25) — ĐÃ QUYẾT, ĐÃ GHI VÀO REPO** | `core.ts` có `resolveFactory`/`resolveSearchMedia` (env → layout repo → layout cũ); đã kiểm chứng trên máy artifact thật trong lần rebuild 05/11 (`listProjects` trả đủ 4 project). Tài khoản mới không sửa đường dẫn. |

#### 2.2 Tài khoản mới ghi vào `MEMORY.md` của chính nó — làm ngay sau khi CEO cung cấp 2.1

Ghi đúng mẫu câu, đúng thứ tự. **Không copy MEMORY.md của tài khoản cũ. Không dùng email
Drive/GitHub/Facebook thay email khai báo.**

**Bước 1 — Dòng khai báo (bắt buộc, trước mọi ca quét tab COO_TASKS):**

```
Email khai báo của tài khoản Muse này: <email CEO đã cung cấp> — dùng làm chữ ký định danh, đối chiếu cột B tab COO_TASKS
```

Đây là **định danh của chi nhánh** (mục 0): gợi ý là email của tài khoản Muse đang hoạt
động; cả chi nhánh dùng chung định danh này khi báo cáo lên Sheet.

**Bước 2 — Tên COO (bắt buộc, cùng lúc với Bước 1):**

```
Tên COO chính là email khai báo này (COO (<email khai báo>))
```

**Bước 3 — Quy tắc cột TASKS.L QUOTA (bắt buộc):**

```
Quy tắc thống nhất email người sản xuất (ghi vào TASKS.L QUOTA): email người sản xuất = email khai báo trong bộ nhớ của tài khoản Muse này; thứ tự lấy email là (1) email Production ghi ở cột D (ASSIGNEE) của dòng TASKS CLAIMED, nếu có và khớp email khai báo — email khai báo thắng khi khác nhau; (2) nếu cột D trống hoặc bàn giao ghi "chưa xác định" thì ghi "chưa xác định — hỏi CEO" và lúc đó hỏi CEO (không tự lấy email khai báo trong bộ nhớ thay thế — quyết CEO 08/11/2026, R4-09 phương án B).
```

**Bước 4 — Cấp phép toàn quyền cho QA (chỉ ghi khi CEO đã cấp ở 2.1 mục 5):**

```
CEO cấp phép toàn quyền cho Kỹ thuật QA ngày <ngày> lúc <giờ> +07: QA được chạy lại upload Drive và hoàn tất bàn giao Drive + Sheet mà không hỏi lại CEO trong chat; thẻ phê duyệt của hệ thống cho lệnh upload vẫn hiện theo luật hệ thống và cần bấm trong 30 phút, đó không phải là hỏi lại.
```

Nếu CEO chưa cấp thì **không ghi dòng này**.

**Bước 5 — Ghi nhận API key Pixabay/Pexels (chỉ ghi khi CEO đã cấp ở 2.1 mục 10):**

```
API key Pixabay và Pexels đã cấp qua Secure Vault ngày <ngày>: connector custom.pixabay và custom.pexels đã tạo, kiểm chứng bằng search_stock "<từ khóa thử>" trả <n> ứng viên (<n> Pixabay + <n> Pexels). Không ghi giá trị key.
```

Nếu CEO chưa cấp thì **không ghi dòng này**, ghi "chưa xác định" ở mục 10 và vẫn đi tiếp (thiếu key không chặn ca quét).

**Bước 6 — Tự kiểm tra bộ nhớ (bắt buộc):** đọc lại `MEMORY.md`, xác nhận các dòng
Bước 1, 2, 3 đều có, đúng chính tả email, không có email khác xen vào. Bước 4 và
Bước 5 chỉ kiểm tra khi CEO đã cấp (chưa cấp thì ghi "chưa xác định" ở mục tương ứng). Thiếu 1 dòng thì
coi như chưa khai báo xong — quay lại Bước 1, không đi tiếp.


### 3. Quy trình chuẩn — làm đủ từng bước, không bỏ bước

#### 3.1 Nguyên tắc vàng

1. **Một tài khoản Muse = một bộ nhớ riêng.** Bộ nhớ không đi kèm repo khi clone.
2. **Không đoán bất cứ thông tin nào.** Không có thì ghi "chưa xác định — hỏi CEO" và dừng đúng bước đó.
3. **Hệ thống không cho agent đọc email đăng nhập của chính nó.** Mọi đối chiếu dùng email khai báo (mục 2.2).
4. **Chưa có email khai báo thì chưa làm gì với tab COO_TASKS.** COO không nhận dòng nào, không ghi ID, không phân việc, không tạo lịch, không sản xuất.
5. **Mọi lần push GitHub đều chờ CEO duyệt riêng.** Trước push, gửi COO bản phân tích để COO trình CEO qua CEO_REPORTS đọc trước (file nào đổi, đổi gì, vì sao, rủi ro và ảnh hưởng gì); chỉ push sau khi CEO duyệt riêng. Làm xong các bước dưới đây vẫn **CHƯA push**.

#### 3.2 Kiểm chứng trước ca quét tab COO_TASKS đầu tiên — đủ 7 điểm, thiếu 1 điểm bắt buộc thì dừng

1. **Repo:** đúng `duongvtrinh/vieneu-media-company`, nhánh `main`, private; đã đọc BOOTSTRAP, spec, bot-sop, LOGIC và 4 skill; app-tao-video đúng 47 file.
2. **Bộ nhớ:** đã có email khai báo (Bước 6 ở mục 2.2 đã qua). Chưa có thì dừng, báo COO.
3. **Workbook:** đúng workbook "Video HQ — Trụ sở Muse", đủ 7 tab (TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN), tab COO_TASKS đúng **7 cột**: A ID, B Tài khoản Muse nhận việc (email), C Việc chính, D Phân việc chi tiết, E Trạng thái, F Thời gian hoàn thành, G Kết quả hoàn thành; tab CEO_REPORTS đúng **9 cột** A–I (REPORT_ID, DATE_REPORTED, ASSIGNEE_EMAIL, ISSUE, TRIED, NEEDS_DECISION, CEO_REPLY, APPLIED_BY, DATE); tab COO_CHECKIN đúng **3 cột** A–C (ASSIGNEE_EMAIL, TOKENS_LEFT, DATE). Không tạo workbook mới, không đổi tên tab, không xóa dòng cũ.
4. **Thư mục Drive:** đúng thư mục "Video Muse" theo 2.1 mục 3. Không tự tạo thư mục khác, không tự thay đổi quyền.
5. **Tài sản nhị phân:** sfx đủ 8 file `.mp3`, bgm đủ 24 track + `README.md` + `bgm_catalog.json` (mục 1.3).
6. **Lịch:** chưa tạo lịch nào trừ khi có dòng tab COO_TASKS giao hoặc CEO duyệt riêng (mục 1.7). Ca quét tab COO_TASKS đầu tiên là **06:00 Asia/Saigon** đầu ca; việc giao sau 06:00 đọc vào 06:00 hôm sau. Lệnh quét ngoại lệ ngoài 06:00 (lệnh trực tiếp của COO) được ghi vào CEO_REPORTS — lần quét đó vẫn theo đủ điều kiện nhận dòng.
7. **Stock:** chạy 1 lần `search_stock` thật qua `company-os/media-search/search_media.py`; có ứng viên thì ghi nhận, SKIPPED thì ghi "chưa xác định" ở mục 10 và vẫn đi tiếp (không chặn).
8. **Cửa chặn hạn mức tuần (quyết CEO 09/11/2026, DEC-202): đầu ca đọc TASKS.L QUOTA mới nhất của chi nhánh — nếu token tuần đã đạt trên 95% thì dừng hẳn ca này (Scout không quét/chấm/ghi, pipeline claim 0 chủ đề READY mới; ca dừng hẳn, không báo cáo ca); khi hạn mức tuần được reset thì công ty hoạt động trở lại bình thường, không cần lệnh mở lại; token thêm là dự phòng, không dùng để sản xuất video. (kiểm chứng trước ca quét đầu tiên).

#### 3.3 Ca quét tab COO_TASKS — từng bước

0. Điểm danh đầu ca tại tab COO_CHECKIN (Bước 0 trong body cron coo-scan-0600, lệnh CEO 09/11/2026): ghi 1 dòng mới vào cuối tab (append, không sửa dòng cũ) gồm A ASSIGNEE_EMAIL = email khai báo, B TOKENS_LEFT = 'Tuần đã dùng X%, token thêm còn Y' lấy từ TASKS.L QUOTA mới nhất, C DATE = ngày hôm nay dạng YYYY-MM-DD; L không đọc được thì B = 'không đọc được', không bịa số. Chỉ 1 dòng/ngày; điểm danh làm mỗi ngày kể cả khi không có dòng COO_TASKS nào thỏa.
1. Cửa chặn hạn mức tuần (quyết CEO 09/11/2026, DEC-202): đầu ca đọc TASKS.L QUOTA mới nhất của chi nhánh — nếu token tuần đã đạt trên 95% thì dừng hẳn ca này (Scout không quét/chấm/ghi, pipeline claim 0 chủ đề READY mới; ca dừng hẳn, không báo cáo ca); khi hạn mức tuần được reset thì công ty hoạt động trở lại bình thường, không cần lệnh mở lại; token thêm là dự phòng, không dùng để sản xuất video.
2. Đọc tab COO_TASKS đúng 1 lần lúc 06:00 +07 đầu ca (hoặc theo lệnh trực tiếp của COO ghi vào CEO_REPORTS).
3. Chỉ nhận dòng thỏa **cả 3 điều kiện**: (a) cột **B** = email khai báo trong bộ nhớ; (b) cột **E** chưa phải "Hoàn thành"; (c) cột **F** còn trống. Dòng email khác thì bỏ qua ("không khớp email khai báo của mình").
4. Ghi ID vào cột A **trước khi phân việc**: dạng `COO-YYYYMMDD-NN`. **Ngày trong ID lấy theo ngày COO đọc/nhận** (không còn cột ngày giao — đã bỏ hẳn 05/11/2026). Số thứ tự NN tính theo ngày đọc/nhận. Chưa có ID thì không phân việc.
5. Chuyển E sang "Đang làm" ngay khi ghi ID. Cột E chỉ dùng 4 giá trị: Assigned / Đang làm / Hoàn thành / Tắc. "Blocked" **không phải** giá trị E tab COO_TASKS.
6. Tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID TASKS (TOPIC_ID) nào nếu có), tự giao cho các phòng qua chat, không chờ CEO, không hỏi lại trừ khi mơ hồ hoặc vượt phạm vi.
7. Báo cáo trên cùng dòng khi xong: E = Hoàn thành, F = `YYYY-MM-DD HH:MM +07`, G = kết quả (viết ngắn + link bằng chứng; chỉ khi tắc mới ghi "cần CEO" trong G). Công thức hoàn thành thống nhất: **"Thiếu E, F hoặc G thì chưa xong."**
8. **3 kênh giao việc duy nhất:** (1) chat chính — tính là lệnh của COO (lệnh CEO 08/11/2026, phương án B); (2) lịch bot đã được CEO duyệt (kể cả Pipeline); (3) COO qua tab COO_TASKS. Phòng không tự phát sinh nhiệm vụ sản xuất mới chỉ vì đọc Sheet hay lịch sử fork.

#### 3.4 Cổng sản xuất — đủ cả 2 mới được giao (cổng READY, từ 07/11/2026)

Chủ đề chỉ được giao khi đồng thời: (1) TOPICS.STATUS = **READY** VÀ TOPIC_ID đã có (không trống) (chủ đề mới do **Scout** chấm xong ghi STATUS = APPROVED / HOLD / REJECTED / DUPLICATE ngay trong cùng lượt quét, TOPIC_ID để trống; chỉ CEO flip STATUS từ APPROVED → READY, và tự nhập TOPIC_ID bằng công cụ riêng bên ngoài, đảm bảo không trùng); (2) **chưa có dòng TASKS nào** cho TOPIC_ID đó. TASKS là nguồn duy nhất (quyết CEO 07/11/2026, R4-11 phương án B): không kiểm tra thư mục projects hay tiến trình máy — video đang làm/chờ QA đều thể hiện bằng dòng TASKS (CLAIMED/BUILDING/REVIEW/RETURNED, trong đó REVIEW là chờ QA). Hạn chế đã chấp nhận: TASKS không thấy trạng thái render/TTS trên máy nếu project chưa ghi TASKS. Chủ đề READY mà TOPIC_ID trống thì pipeline bỏ qua (không claim được vì TASKS cần TOPIC_ID), ghi vào báo cáo ca để COO báo cáo CEO qua CEO_REPORTS nhập ID. Điểm (E–I) và TOTAL (J) chỉ là tham khảo cho quyết định của CEO — điểm không chặn sản xuất; chỉ READY mới quyết định sản xuất.

- **Không có ngoại lệ vượt cổng READY.** Cách duy nhất để có READY là CEO tự flip 1 ô TOPICS.K từ APPROVED → READY trên Sheet và tự nhập TOPIC_ID (cột A) bằng công cụ riêng bên ngoài, đảm bảo không trùng ID; ghi "vượt cổng" trong lệnh chat hay dòng tab COO_TASKS đều **không** mở cổng. Lệnh trực tiếp cho chủ đề chưa đủ cổng thì chờ cho tới khi CEO flip READY.
- Một nhiệm vụ = một chủ sở hữu duy nhất. Trước khi giao, kiểm tra TASKS, khóa bằng dòng TASKS STATUS = CLAIMED (ASSIGNEE = email khai báo) (không ghi đè, không xóa dòng cũ). Đã có chủ sở hữu/dòng TASKS/đang chạy thì không giao lại, không spawn song song. **Chỉ Pipeline (bot) và Production được tạo dòng CLAIMED** (COO không tạo); khi Production nhận việc mà dòng CLAIMED đã có sẵn nhưng cột D (ASSIGNEE) còn trống thì điền ngay email khai báo của mình trước mọi bước khác. Hai dòng CLAIMED cùng TOPIC_ID: dòng tạo sau dừng ngay, ghi Blocker vào cột ghi chú của dòng mình (TASKS.N DUP_NOTE nếu dòng do Pipeline tạo, TASKS.K PROD_NOTES nếu dòng do Production tạo), báo COO.
- Luật chống đua: R1 tham chiếu bằng TOPIC_ID khi đã có; chủ đề chưa có ID thì tham chiếu tạm bằng tiêu đề, không bao giờ bằng số dòng; R3 claim-then-verify — đọc lại theo ID ngay trước khi ghi; R7 chỉ đọc số dòng + ID lớn nhất (chỉ tính dòng đã có ID) để nắm trạng thái hiện tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất lùi KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026: làm việc bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab BASELINE hay file baseline.json. ID trống là bình thường, không phải lỗi.

#### 3.5 Cửa chặn ảnh thật trước AI — làm đúng thứ tự

1. Kịch bản Việt Nam: **bỏ qua Wikipedia và Stock hoàn toàn**; chỉ tìm ảnh thật từ nguồn gốc bằng từ khóa tiếng Việt (bài báo về đúng vụ việc, bài đăng công khai, tìm kiếm hình ảnh). Ảnh báo không logo/watermark/chữ được dùng thẳng kèm ghi nguồn theo quyết định chịu rủi ro của CEO 29/10/2026.
2. Chỉ sau khi thử nhiều từ khóa mà không có ứng viên phù hợp mới được tạo AI từ prompt, ghi rõ "AI từ prompt, không có ảnh tham chiếu, đã thử các từ khóa: …" — **cấm ghi chung chung "AI generic"**.
3. Ảnh có logo/watermark/chữ: **cắt (crop) trước**; nếu cắt không sửa được thì AI tạo lại **từ chính ảnh gốc làm tham chiếu**, prompt của CEO: "Tạo ảnh giống ảnh tham chiếu, chỉ loại bỏ chữ hoặc watermark trên ảnh"; bắt buộc đối chiếu trực quan với ảnh gốc, méo thì loại. Không tạo từ prompt chữ khi không có ảnh tham chiếu. Hồ sơ = URL gốc + prompt + ghi chú + kết quả đối chiếu + ghi chú rủi ro CEO.
4. **Nhật ký từ khóa bắt buộc cho mỗi cảnh** (từ khóa đã thử, ứng viên + link + nguồn, phân loại, lý do loại). QA **TRẢ LẠI** video nếu cảnh AI thiếu nhật ký. Cửa này **đã có trong code**: preflight chặn khi scene thiếu `mediaSource.source`, thiếu `media-log.json` hoặc thiếu `keywordsTried`, và chặn cả scene nền rêu có gắn nguồn (B7); `gen_images` chỉ bỏ qua file khi giải mã được hết bằng PIL (A23).
5. **Nền xanh rêu không thay thế ảnh:** nền `#1C372A`, kẻ ô vuông 80px (lưới `#2A4D3B`, dày 2px), **không thêm bất kỳ chữ nào**; ngoại lệ duy nhất là scene khai `cardImage` thì dùng chính ảnh đó làm nền, **vẫn không chữ**. Scene chỉ có nền này vẫn tính là **thiếu ảnh**; 3 giây đầu không được là nền xanh rêu trơn. `cardImage`/`bgImage` khai mà file không tồn tại hoặc nằm ngoài project: in `CARDIMAGE-MISSING` ra stderr rồi rơi về nền rêu, không chặn.
6. **Ranh giới AI cho nhân vật có tên (LOGIC.md là nơi chuẩn):** Nhóm A (nhân vật công chúng có nhiều thông tin công khai đã kiểm chứng — vd tổng thống Mỹ, Messi, Chủ tịch nước Tô Lâm): được tạo chân dung AI **chỉ khi cần thiết** (đã tìm ảnh thật mà không có ứng viên phù hợp), chỉ dùng thông tin công khai đã kiểm chứng, ghi rõ "ảnh AI minh họa, không phải ảnh thật". Nhóm B (nhân vật thiếu thông tin): chỉ góc rộng / sau lưng / bóng mờ / bàn tay (chỉ khi là vật chứng, vd bàn tay đang ký giấy tờ — không cận cảnh bàn tay để nhận diện người) / vật chứng / ngoại cảnh / ghế trống; **không cận mặt, không dùng tên làm chỉ dẫn ngoại hình**. Không chắc thì xếp nhóm B.

#### 3.6 Hằng số pipeline — dùng đúng số đã chốt, không tự đổi

- Khung hình mặc định **9:16** (720x1280). Phụ đề: lề dọc **20%**, lề ngang **7%**.
- TTS chunk tối đa **140 ký tự** (`normalize_chunks.py` `MAX_CHARS = 140`). Pause sau mỗi part mặc định **180ms**.
- ZIP bàn giao gồm **file BGM thật** + `broll-plan.json` + `abbr_dict.json` (trừ `silence_*`, `_thumb_*`, `render_page.html`); `timeline.json`/`project.json` không trỏ `audio/bgm/` (khác biệt có chủ ý, đã ghi rõ).
- **BGM thiếu file thì CHẶN:** preflight exit 1, render in `RENDER-ERROR`, assemble in `ASSEMBLE-ERROR` và xóa ZIP tạm. Plan không chọn BGM thì vẫn render bình thường. BGM đã chọn nhưng `bgm.file` trống/thiếu cũng chặn.
- Preview và render đều nhận **jpg/png/webp**, tra đúng tên rand6, không glob. `pickMedia`: timeout **60 giây**, cap **100 MB**, kiểm content-type và magic bytes.
- Thời lượng: **đề xuất 2–3 phút, Production tự quyết**; QA không trả lại video chỉ vì thời lượng (lệnh CEO tối 29/10/2026; chuẩn 180–300s đã bãi).
- `safeId()` chặn id rỗng / chỉ dấu chấm / chứa `..` / ký tự ngoài `[A-Za-z0-9._-]`; `deleteProjectForever` có lớp chặn thứ hai.
- Ngưỡng inline voice **10.000.000 byte** (4C, mục 2.1).

#### 3.7 Bàn giao Drive + Sheet — chỉ tính là xong khi đủ email người sản xuất + hạn mức

1. Chỉ bàn giao video **đã được QA duyệt**. QA tải lên **NGAY trong cùng lượt duyệt** lên thư mục Drive "Video Muse", không chờ ca pipeline; Pipeline chỉ làm lưới bắt sót.
2. Ghi link thật vào TASKS trên cùng dòng video (H DRIVE_LINK + I MD5, STATUS = DELIVERED) và ghi verdict vào QA_LOG; không bịa link, không tự tạo thư mục khác, không tự thay đổi quyền thư mục.
3. Cùng dòng TASKS đó phải ghi vào L QUOTA đủ 2 thông tin (quyết CEO 07/11/2026, R4-05 — Q1 đã đóng):

- **Email người sản xuất (email tài khoản Muse)** — theo quy tắc mục 2.2 Bước 3.
- **Hạn mức còn lại (Muse tuần + hạn mức khác)** — **QA TỰ ĐỌC lại hạn mức tại thời điểm upload** (lựa chọn 8A); chỉ ghi bằng chữ, **KHÔNG chụp ảnh màn hình**, vd "Muse tuần đã dùng 10%, còn 90%, reset 9/11 lúc 14:14 +07; token thêm còn 1B". Không đọc được thì ghi "không đọc được", không bịa số.

4. Thiếu 1 trong 2 thông tin thì chưa tính là bàn giao xong — báo cáo ghi "chưa xong bước Drive + Sheet". Video cũ bàn giao trước 04/11/2026 thì để trống, không điền ngược.
5. Sau khi bàn giao xong, TASKS chuyển sang DELIVERED; COO đóng dòng tab COO_TASKS bằng E = Hoàn thành, F và G đầy đủ (mục 3.3). QA không tự ghi vào tab COO_TASKS.
6. **Snapshots (12B):** chỉ bảng DB `snapshots` đã xóa (migration 0004 `DROP TABLE snapshots`); tính năng snapshot trên filesystem vẫn sống (giữ 30 bản, tự snapshot trước save/render). Không xóa tính năng.

#### 3.8 TUYỆT ĐỐI KHÔNG làm trong lần khởi tạo

1. Không push GitHub khi chưa có CEO duyệt riêng sau phân tích.
2. Không tự tạo thư mục Drive khác, không tự thay đổi quyền thư mục, không tự chia sẻ Drive công khai.
3. Không đoán email, không dùng email Drive/GitHub/Facebook thay email khai báo, không copy email/MEMORY của tài khoản cũ.
4. Không sản xuất khi chưa đủ cổng 2 điều kiện; không tự tạo dòng TASKS cho chủ đề chưa duyệt; không sản xuất hàng loạt không kiểm soát.
5. Không tự phát sinh nhiệm vụ sản xuất mới chỉ vì đọc Sheet hay lịch sử fork; chỉ làm việc khi được giao qua đúng 1 trong 3 kênh.
6. Không chi tiền, không cam kết ngoài, không đăng nền tảng, không affiliate, không ghi số liệu views/follow/doanh thu/hoa hồng (publish-checklist.md là tài liệu lịch sử, **KHÔNG dùng làm checklist hiện hành**).
7. Không sửa kết quả chấm điểm trong TOPICS; không tự flip TOPICS.STATUS thành READY (chỉ CEO flip); không sửa migration đã áp dụng; không sửa tay file `.generated` (build lại để đồng bộ — contract đã được tạo lại chính thức ngày 05/11/2026); không chạy `bun run build`; không sửa bundle đã build dưới `~/workspace/ts-spaces/<slug>/.space-build/`; không chạy sqlite/script trực tiếp vào `app.db`.
8. Không đổi tên tab Sheet (tên tiếng Anh VIẾT HOA, không đánh số — TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN), không xóa dòng trong Workbook cũ CHỈ ĐỌC (xem spec), không dùng lệnh Drive ghi đè lên file Google Sheet.
9. Không bịa nguồn/link/điểm số, không ghi "đã xóa bằng AI" khi chưa có output đối chiếu thật, không ghi "AI generic" để lấp hồ sơ, không gắn nhãn ảnh AI là "tư liệu thật".

#### 3.9 Xử lý khi gặp sự cố trong lần khởi tạo

- **Thẻ phê duyệt upload Drive hết hạn (30 phút):** KHÔNG phải bị từ chối, KHÔNG phải file hỏng. Không ghi dòng TASKS thiếu DRIVE_LINK/MD5, không chuyển TASKS sang DELIVERED; báo COO "chưa xong bước Drive + Sheet vì thẻ phê duyệt hết hạn"; **chạy lại upload để hệ thống cấp thẻ mới** (thẻ mới vẫn cần bấm trong 30 phút); trước khi chạy lại, chắc chắn CEO đã cấp phép toàn quyền cho QA **hoặc** CEO đang có mặt để bấm thẻ.
- **Email người sản xuất thiếu thông tin (cột D trống hoặc bàn giao ghi "chưa xác định"):** ghi "chưa xác định — hỏi CEO" và hỏi CEO (không tự lấy email khai báo trong bộ nhớ thay thế — quyết CEO 08/11/2026, R4-09 phương án B).
- **Không còn chủ đề đủ cổng:** báo ngắn về chat COO, không tự sản xuất chủ đề chưa đủ cổng, không tự tạo dòng TASKS cho chủ đề chưa duyệt.
- **Lỗi 429/403/rate-limit:** dừng nhánh đó, ghi blocker vào nhật ký ngày, **không thử lại**.
- **Thẻ phê duyệt hệ thống vẫn hiện dù đã cấp phép toàn quyền:** đó là luật hệ thống, không phải QA hỏi lại.
- **Quyền phê duyệt (để CEO cài trước, không phải để agent cài):** nhiều quyền cài trước Allow ở Settings > Permissions để khỏi hỏi lại từng lần; nhưng **không đạt "không bao giờ hỏi lại" cho mọi thứ** — upload Drive vẫn hiện thẻ mỗi lần và không có standing Allow; mạng trực tiếp không có lựa chọn Allow; upload file mới qua trình duyệt và đăng artifact vẫn hỏi lại mỗi lần; mua hàng vẫn cần phê duyệt mỗi lần (trừ phê duyệt thanh toán của một lịch đã tạo bao các lần mua sau cùng lịch, cùng cửa hàng, cùng phương thức thanh toán). Agent **không cài được** các quyền này từ trong chat — CEO phải cài ở màn hình Settings của app.


## 5. Google Sheet (dữ liệu vận hành, không phải code)

- Cùng tài khoản: tìm workbook theo tên "Video HQ — Trụ sở Muse" qua
  connector, dùng tiếp Sheet đang chạy (spreadsheetId
  `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`), không tạo mới,
  không ghi đè. Workbook cũ CHỈ ĐỌC (xem spec) (đã snapshot 07/11/2026).
- Khác tài khoản: tạo workbook mới từ
  `company-os/google-sheet-spec.md` — đúng 7 tab
  (TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN), kèm dropdown
  validation cho các cột STATUS/RESULT, bắt đầu trống, không chép
  dữ liệu cũ.
- Tuyệt đối không dùng lệnh Drive ghi đè lên file Google Sheet.

## 6. Drive + Facebook + app

- Drive: tìm/tạo thư mục "Video Muse" theo tên qua connector; thư mục "Video Muse" đã được CEO cấp quyền anyone with link ngày 05/11/2026; không tự tạo thư mục khác, không tự thay đổi quyền thư mục.
- Facebook: liên kết lại qua Meta Accounts Center (một tài khoản dùng
  chung); bot không tự tham gia group mới.
- App `app-tao-video` là artifact, không phải repo git: cùng tài khoản
  thì dùng chung artifact, khác tài khoản thì tạo lại app bằng
  artifact tools. Khi tạo lại, CHÉP NGUYÊN TOÀN BỘ cây `app-tao-video/`
  (47 file: client/src App.tsx + lib.ts + 11 component theo tab; server/src
  priv/ 9 module + privileged.ts + actions.ts + schema.ts + script-prompt.ts
  + script-prompt.test.ts; drizzle 0001–0003; theme.css, config, space.json —
  kể cả `AGENTS.md`, `DATA-PLAN.md`, `bun.lock`, `bunfig.toml`,
  `client/build.mjs`, `client/index.html`, `client/src/api.ts`,
  `client/src/globals.d.ts`, `client/src/main.tsx`,
  `server/.generated/privileged.contract.ts`,
  `drizzle/meta/_journal.json`; thiếu một file cũng có thể vỡ build) vào artifact mới — KHÔNG viết lại giao diện
  từ mô tả, vì giao diện nằm trong chính code đó (App.tsx, theme.css)
  nên chép nguyên thì giao diện giống hệt app cũ. Bản build `client/dist`, `server/dist` và `.tsbuildinfo` KHÔNG nằm trong repo (sản phẩm build, build lại khi tạo artifact).

app.db không chuyển qua git nên chỉ state trong app.db (jobs, trash, auto_progress) là trống khi mở app mới; danh sách project vẫn hiện nếu FACTORY trỏ đúng cùng một factory dùng chung, vì project đọc từ thư mục factory, không nằm trong app.db (đó là dữ liệu, không phải giao diện).

> Ghi chú M23: dependency `file:/opt/hatch/skills/spaces/ts-runtime/dist/space-sdk.tgz` trong `package.json` do runtime artifact của Muse cung cấp khi tạo lại app, không nằm trong repo và không cần chép tay — trên máy clone, `bun install` sẽ không resolve được đường dẫn này nếu chạy ngoài Muse, nhưng app vốn chỉ chạy qua artifact nên không chặn clone-and-run theo §6.

> Kiểm tra sau khi rebuild (lệnh CEO 05/11/2026, mục A27 — KHÔNG sửa tay file `.generated`, chỉ kiểm chứng sau khi build sinh lại). Kết quả lần rebuild 05/11/2026 (đã xong — ghi để lần sau khỏi kiểm lại từ đầu; lần rebuild sau vẫn kiểm lại 4 mục này vì code đã đổi thêm):
> - `server/.generated/privileged.contract.ts` không còn `saveInput` sống (đã gỡ khỏi nguồn theo 12B; contract cũ còn sót dòng 273-279), và có đủ các lệnh mới: `clearSceneImage` (A22), trường `isMossGrid` trong scene (A21) — đã đạt trong rebuild 05/11/2026.
> - Typecheck TypeScript phải qua cho các sửa từ 05/11/2026 (11A, A21, A22, A24, 4C — trước đó chỉ mới kiểm tra transpile, chưa typecheck) — đã qua trong môi trường build 05/11/2026 theo báo cáo builder (local không chạy được typecheck vì repo chưa từng `bun install`, xem B4).
> - Contract sinh ra `.generated/privileged.contract.ts` đã tái sinh ngày 05/11/2026 bằng extractor chính thức (không sửa tay): hết entry `saveInput` sống (chỉ còn trong comment), có đủ `clearSceneImage` + `isMossGrid`; sinh lại lần 2 cho diff rỗng; test 14/14 pass.
> - `FACTORY`/`SEARCH_MEDIA` trong `core.ts` trỏ đúng trên máy artifact thật (A25 — đã quyết và ghi vào repo ngày 05/11/2026; rebuild 05/11/2026 kiểm chứng: `listProjects` trả đủ 4 project thật trên máy artifact).

## 7. Tài sản nhị phân (ĐÃ nằm trong git từ 04/11/2026 — clone là có)

- 8 file `vieneu-asset-factory/sfx/*.mp3` (boom_sub_impact,
  cinematic_riser, heavy_thud_slam, paper_rip, punch_impact, radar_glitch,
  typing_fast, whoosh_fast) và thư mục nhạc nền `vieneu-asset-factory/bgm/`
  (24 track Kevin MacLeod CC-BY 4.0 + bgm_catalog.json + README.md, giữ
  nguyên 8 thư mục mood calm/dramatic/funny/inspirational/news/sad/
  suspense/upbeat): ĐÃ NẰM TRONG REPO từ ngày 04/11/2026, đẩy lên bằng
  giao diện web GitHub (GitHub connector chỉ nhận nội dung UTF-8 nên
  không push được file nhị phân) và đã kiểm chứng qua API GitHub
  (đủ 34 file, đúng cây thư mục, không còn file .gitkeep tạm). Clone mới
  có sẵn nhạc + SFX, không cần tải thêm.
- Bản dự phòng trên Drive vẫn còn và vẫn khớp: thư mục Drive "sfx"
  (đủ 8 file, kiểm chứng md5 8/8 ngày 04/11/2026) và thư mục Drive "bgm"
  (26 file, đối chiếu md5 + dung lượng đủ 26/26 ngày 04/11/2026). Chỉ
  dùng đến khi bản trong repo mất hoặc hỏng — tải về đúng đường dẫn
  trên rồi đối chiếu lại.
- Lưu ý cho lần đẩy sau: nhạc/SFX mới hoặc thay đổi vẫn phải đi qua
  giao diện web GitHub, không qua connector. Các đợt đẩy text qua
  connector trước đó không động đến file ngoài danh sách đẩy, nhưng sau
  mỗi lần đẩy vẫn kiểm tra lại cây bgm/ và sfx/ trên remote.
- Nếu sfx/ rỗng, assemble_project.py cảnh báo rõ (ZIP ra không có SFX)
  và validate_project chặn export của plan có broll.sfx. Nếu bgm/ chưa
  có, select_bgm.py exit 2 và preflight báo "BGM không tồn tại"
  (không crash mù, không lặng lẽ). Danh sách track + license nằm trong
  `vieneu-asset-factory/bgm/bgm_catalog.json`.
- `projects/` cũ (project nguồn, MP4, thư mục work): không phải code,
  không nằm trong git, Muse mới bắt đầu trống; project cũ cần thì chép
  qua Drive (riêng, không qua git). Bài học 29/10: `projects/` từng mất
  mà không rõ nguyên nhân — backup `projects/` ra Drive định kỳ, đừng
  trông chờ git.

## 8. Lịch bot + chat nhân viên (tạo lại, không có trong git)

- 10 lịch cron công ty chạy thật: Scout 4 ca/ngày (06:00, 10:00, 14:00, 18:00),
  Pipeline 4 ca/ngày (cùng giờ), bot-hoc-hoi hằng ngày 20:00 (cron
  bot-hoc-hoi-2000, quyết CEO 07/11/2026, R4-14 phương án A, DEC-019;
  Q6 đã đóng) và COO quét COO_TASKS 06:00 hàng ngày (cron coo-scan-0600, quyết CEO 08/11/2026, DEC-099) — tạo đúng nội dung trong `company-os/bot-sop.md` (SOP
  đầy đủ: bước làm, giới hạn cứng, quy tắc báo cáo). Cron là cấu hình
  của tài khoản; bản mẫu nằm trong repo tại company-os/crons/ (xem company-os/scheduled-tasks-setup.md) — chỉ cài khi CEO duyệt.
- 4 chat nhân viên (Scout-Báo, Scout-Group, Sản xuất, Kỹ thuật
  QA — 2 chat Scout dùng chung skill media-scout, đã gộp chấm điểm) +
  chat COO, phối hợp qua Sheet. (Chat Scoring đã đóng ngày 07/11/2026,
  quyết định C3.)
- Quy tắc điều phối từ Chat chính (lệnh CEO 04/11/2026, sau vụ trùng
  TOPIC-219; kênh báo cáo/lệnh đổi theo phương án B, lệnh CEO 08/11/2026):
  Chat chính là kênh CEO nhắn tin; agent ở chat chính là điều phối viên
  (COO), tự động điều phối nhiệm vụ đến đúng phòng liên quan, theo dõi,
  tổng hợp kết quả. Lệnh từ chat chính hay COO đều tính là lệnh của COO.
  Các phòng chức năng và COO chỉ nhận lệnh từ CEO duy nhất qua tab
  CEO_REPORTS. Một nhiệm vụ = một chủ sở hữu duy nhất, khóa bằng
  dòng TASKS STATUS = CLAIMED (ASSIGNEE = email khai báo) trước khi
  làm; cấm chạy song song cùng nhiệm vụ ở chat chính và phòng ban.
  Phòng ban chỉ làm nhiệm vụ khi được giao cụ thể từ chat chính (hoặc
  từ lịch bot đã được CEO duyệt, hoặc từ COO qua tab COO_TASKS; lệnh từ chat chính hay COO đều tính là lệnh của COO), không
  tự phát sinh nhiệm vụ sản xuất mới chỉ vì đọc Sheet hay lịch sử fork.
  Các phòng báo cáo kết quả cho COO; chỉ COO báo cáo với CEO, qua tab
  CEO_REPORTS.
  Không có ngoại lệ vượt cổng READY (lệnh CEO 05/11/2026, mục B16,
  phương án B — bãi bỏ A33/9A; cổng đổi thành READY ngày 07/11/2026):
  chỉ sản xuất chủ đề đủ cả 3 điều kiện TOPICS.STATUS = READY +
  TOPIC_ID đã có (không trống) + chưa có dòng TASKS nào cho TOPIC_ID
  đó (TASKS là nguồn duy nhất — quyết CEO 07/11/2026, R4-11 phương án B: không kiểm tra thư mục projects hay tiến trình máy; hạn chế đã chấp nhận: TASKS không thấy trạng thái render/TTS trên máy nếu project chưa ghi TASKS); cách duy nhất để có READY là CEO tự
  flip 1 ô TOPICS.K từ APPROVED → READY trên Sheet và tự nhập TOPIC_ID
  (cột A) bằng công cụ riêng bên ngoài, đảm bảo không trùng ID, ghi
  "vượt cổng" ở bất cứ đâu đều không mở cổng. Chủ đề READY mà TOPIC_ID
  trống thì pipeline bỏ qua, ghi vào báo cáo ca để COO báo cáo CEO qua CEO_REPORTS nhập ID. Điểm (E–I) và
  TOTAL (J) chỉ là tham khảo cho quyết định của CEO — điểm không chặn
  sản xuất; chỉ READY mới quyết định sản xuất.
  Pipeline: không giới hạn số video ĐÃ BÀN GIAO/ca hay /ngày (trần NHẬN tối đa 3 chủ đề READY/ca vẫn còn); Cửa chặn hạn mức tuần (quyết CEO 09/11/2026, DEC-202): đầu ca đọc TASKS.L QUOTA mới nhất của chi nhánh — nếu token tuần đã đạt trên 95% thì dừng hẳn ca này (Scout không quét/chấm/ghi, pipeline claim 0 chủ đề READY mới; ca dừng hẳn, không báo cáo ca); khi hạn mức tuần được reset thì công ty hoạt động trở lại bình thường, không cần lệnh mở lại; token thêm là dự phòng, không dùng để sản xuất video. NHẬN THEO LÔ (quyết CEO 07/11/2026, thay thế luật tuần tự + R4-03): mỗi ca NHẬN 1 LẦN tối đa 3 chủ đề READY theo thứ tự Sheet (tối đa 12 claim/ngày), đánh dấu ngay bằng dòng TASKS CLAIMED (ASSIGNEE = email khai báo của chi nhánh mình) để các chi nhánh khác biết đã có người làm; sau đó lần lượt tạo 3 video (sản xuất tuần tự từng video một), không sản xuất song song. Video ĐẦU TIÊN của lô do pipeline giao; các video sau trong lô Production TỰ LẤY khi video trước DELIVERED (lệnh CEO 07/11/2026, DEC-032 — chỉ lấy chủ đề đã CLAIMED trong cùng lô, ASSIGNEE = email khai báo của mình, UPDATED_AT = ngày hôm nay; video trước BLOCKED (lỗi riêng video, nhóm 1) thì lấy video CLAIMED kế tiếp chưa tắc trong cùng lô (ngoại lệ DEC-032, quyết CEO 08/11/2026, DEC-104 phương án A); video trước BLOCKED (lỗi hệ thống, nhóm 2, hoặc chưa rõ lý do) thì dừng chờ COO gỡ tắc). Mỗi ca nhận đủ 3 chủ đề READY mới, không trừ số video đang làm dở trong ngày (quyết CEO 08/11/2026, T3 phương án B); tổng số video đang làm cùng lúc có thể vượt 3. Video đang làm dở từ NGÀY CŨ thì bỏ qua theo quy tắc ngày hiện tại. Không còn cơ chế nhận tiếp theo sự kiện QA báo DELIVERED — việc nhận chủ đề chỉ xảy ra 1 lần đầu ca, theo lô. Video BLOCKED mà TASKS.D ASSIGNEE = email khai báo của tài khoản của chi nhánh mình VÀ TASKS.J UPDATED_AT là ngày hôm nay thì pipeline đọc M BLOCKER và phân loại (quyết CEO 08/11/2026, DEC-104 phương án A): lỗi riêng video (nhóm 1) thì KHÔNG dừng hàng đợi — Production lấy video CLAIMED kế tiếp chưa tắc trong cùng lô, video BLOCKED nằm lại chờ COO; lỗi hệ thống (nhóm 2) hoặc M trống/mơ hồ thì dừng hàng đợi cho đến khi COO gỡ tắc hoặc hủy (CANCELLED); 2 video BLOCKED trở lên cùng mã lý do (DEC-158) trong ngày thì dừng (nghi lỗi hệ thống trá hình); Kiểm tra BUILDING cũ mỗi ca (quyết CEO 08/11/2026, DEC-105 phương án A): pipeline đọc giờ vào BUILDING trong K PROD_NOTES; video vẫn BUILDING qua 2 lần đầu ca liên tiếp mà không có ghi chú K mới thì hỏi Production (bước hiện tại + lỗi + cần gì); Production trả lời trong 1 ca, lỗi nhóm 1 thì ghi BLOCKED rồi lấy video kế tiếp trong lô, lỗi hệ thống thì dừng; không trả lời tới đầu ca sau thì COO giao lại (kiểm tra trước, tiếp tục từ điểm dừng trong K theo luật resume). Kiểm tra REVIEW cũ mỗi ca (quyết CEO 08/11/2026, DEC-106 phương án A): pipeline đọc giờ nộp REVIEW trong K PROD_NOTES; video vẫn REVIEW qua 1 ca (khoảng 4 giờ) mà không có verdict trong QA_LOG thì hỏi QA (đang chấm tới đâu, verdict khi nào); QA trả lời trong 1 ca; Production được bắt đầu video kế tiếp trong lô trong lúc chờ verdict (nới DEC-032, vẫn chỉ làm 1 video tại một thời điểm); QA không trả lời tới đầu ca sau thì COO giao lại cho QA (ID video + DRAFT_LINK). Vòng lặp RETURNED (quyết CEO 08/11/2026, DEC-107 phương án A): đủ 2 lần trả thì leo thang 1 lần về chat COO; các lần trả thêm sau đó thì leo thang LẠI mỗi khi số lần trả tăng (QA nhắn lúc verdict + pipeline kiểm tra đầu ca, cùng số lần trả thì không nhắn lại); sau lần trả thứ 3 Production dừng sửa, báo COO quyết trước 06:00 hôm sau (sửa tiếp 1 lần với cách khác — chỉ 1 lần (a) duy nhất, bị trả lần 4 thì chỉ còn BLOCKED nhóm 1 hoặc hủy; quá hạn thì pipeline ghi vào báo cáo ca ‘COO chưa quyết — cần CEO quyết’ và COO ghi CEO_REPORTS khi quá 24h) (DEC-154); QA ghi rõ lỗi lặp lại thì Production phải đổi cách sửa. Video đã duyệt chưa upload (quyết CEO 08/11/2026, DEC-108 phương án A): pipeline đầu ca kiểm tra TASKS.C=APPROVED hoặc QA_LOG APPROVED mà TASKS chưa DELIVERED rồi nhắn QA upload ngay + ghi vào báo cáo ca; QA báo ngay mọi lỗi upload (không chỉ hết hạn thẻ); quá 1 ca chưa upload xong thì pipeline báo chat COO + COO giao lại cho QA; quá 2 lần giao lại mà vẫn chưa upload được thì COO ghi TASKS.C = BLOCKED (nhóm 2) + lý do vào M BLOCKER và ghi CEO_REPORTS, pipeline không nhắn QA nữa (DEC-153). Rảnh mà còn việc (quyết CEO 08/11/2026, DEC-109 phương án A): pipeline đầu ca kiểm tra không có video nào BUILDING/REVIEW/RETURNED mà còn dòng CLAIMED thì nhắn Production lấy video CLAIMED đầu tiên theo thứ tự Sheet làm tiếp + ghi vào báo cáo ca; Production xác nhận trong 1 ca; tới đầu ca sau vẫn chưa BUILDING thì pipeline báo chat COO + COO giao lại cho Production. video BLOCKED từ NGÀY CŨ (UPDATED_AT không phải ngày hôm nay) thì bỏ qua theo quy tắc ngày hiện tại — không dừng hàng đợi, ghi vào báo cáo ca để COO xác định chủ/xử lý; video BLOCKED của chi nhánh khác (ASSIGNEE là email khác) hoặc ASSIGNEE trống thì KHÔNG dừng hàng đợi, ghi vào báo cáo ca để COO xác định chủ; COO chỉ gỡ tắc/hủy dòng BLOCKED của chi nhánh mình. C/J/D nhiều người viết — ghi sau thắng + để lại lý do (quyết CEO 07/11/2026, R4-10 phương án C): TASKS.C STATUS có 3 người viết (Production: CLAIMED/BUILDING/REVIEW/BLOCKED — chỉ lỗi riêng video nhóm 1, lý do bắt buộc vào M; QA: RETURNED/APPROVED/DELIVERED; COO: BLOCKED/CANCELLED — chỉ COO được gỡ BLOCKED hoặc hủy), TASKS.J UPDATED_AT có 2 người viết (Production, QA), TASKS.D ASSIGNEE có 2 người viết (Production lúc claim, COO lúc giao qua COO_TASKS) — chấp nhận ghi sau thắng khi xung đột (lần ghi sau thắng, không có quy tắc ai thắng theo vai trò); ai ghi TASKS.C thì trong cùng lần ghi phải ghi thêm lý do + thời gian vào cột ghi chú của mình (Production→K PROD_NOTES (và M BLOCKER khi ghi BLOCKED), QA→QA_LOG cột E ISSUES + TASKS.F QA_VERDICT, COO→M BLOCKER, Pipeline→lý do nhận lô ghi vào báo cáo ca, trùng CLAIMED ghi N DUP_NOTE).

## 9. Kiểm chứng cuối ("dựng xong" khi nào)

- TTS sample ra WAV; factory scripts compile OK; ffmpeg OK; SFX mp3
  và bgm đã chép đủ (nếu render cần).
- 4 skill đã đọc; Sheet mới "Video HQ — Trụ sở Muse" đủ 7 tab
  (không chấp nhận Sheet cũ); thư mục Drive tìm thấy theo tên.
- Dựng 1 video test bằng đúng pipeline (`PIPELINE.md`) → preflight
  ĐẠT, karaoke lines > 0 ở part không template, MP4 720x1280.
- Chỉ khi tất cả pass mới nhận việc thật. Fail ở đâu dừng ở đó.
