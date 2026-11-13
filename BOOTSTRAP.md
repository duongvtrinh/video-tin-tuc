# BOOTSTRAP v3 — Dựng lại hệ thống VieNeu Media Company trên tài khoản Muse mới

> **Bản chính thức v3 — CEO duyệt ngày 11/11/2026. Bản này thay toàn bộ hướng dẫn cũ (bản cũ lưu trữ tại `BOOTSTRAP-legacy-2026-11-11.md`).**
> Bản v3 hợp nhất ba nguồn đã kiểm chứng: bản hướng dẫn gốc trong repo (chi tiết vận hành đầy đủ nhất, gồm mục khai báo 2.1/2.2 và kiểm chứng 7 điểm), bản v2 (cấu trúc tách cài máy / kích hoạt vận hành, mẫu cấp quyền, manifest thay số cứng) và toàn bộ bài học thật của phiên cài đặt + vận hành ngày 11/11/2026 (kết nối vault cho API key, đăng nhập Facebook qua vault, sự cố lịch bị lưu trữ, kỷ luật hỏi trước khi sửa repo, bỏ luật suy ra theo ngày).
> **Quy tắc một nguồn:** `BOOTSTRAP.md` trong repo (chính file này) là bản duy nhất hiện hành. Mọi bản sao tại máy (bản giải nén ZIP, bản nháp trong thư mục goal) đều là bản cũ theo định nghĩa — trước khi dùng hay tải lên bất kỳ file nào trùng tên, phải đối chiếu với bản trên repo (số dòng + dòng đầu + commit mới nhất).

## Mục đích và nguyên tắc

Tài liệu này dựng lại toàn bộ hệ thống sản xuất video trên một tài khoản Muse mới, gồm bốn thành phần: `vieneu-tts/` (đọc văn bản thành giọng nói), `vieneu-asset-factory/` (dựng tài sản và video), `app-tao-video/` (ứng dụng Tạo Video) và `company-os/` (kỹ năng và logic vận hành).

Hai loại việc phải tách bạch:

- **Cài máy** (Phần C) là việc kỹ thuật thuần túy: lấy repo về, cài thư viện, tải model, dựng lại ứng dụng và chạy kiểm chứng. Tiêu chí xong rõ ràng, làm một mạch tới khi đạt.
- **Kết nối + kích hoạt vận hành** (Phần D và E) là việc cần CEO trả lời hoặc xác nhận: khai báo định danh, kết nối Google/GitHub/Facebook/kho key, tạo chat nhân viên, tạo lịch bot. Làm sau cài máy, không chặn cài máy.

Sáu quy tắc áp dụng cho toàn bộ tài liệu:

1. Mỗi con số hoặc sự kiện chỉ ghi ở một chỗ duy nhất; các phần khác trỏ về chỗ đó, không ghi lặp con số của mình.
2. Đối chiếu file theo danh sách chuẩn (manifest) và sổ đăng ký, không theo số đếm cứng. Số file thay đổi hợp lệ khi có migration hoặc file mới được đăng ký đúng quy trình.
3. **Không ghi luật suy ra theo ngày.** Trần và giới hạn chỉ ghi theo ca/lượt chạy (ví dụ: tối đa 3 chủ đề READY mỗi ca). Cấm ghi tổng suy ra từ số lịch kiểu "claim/ngày" hay "ca/ngày" trong luật, skill, tài liệu và body lịch — mỗi lần thêm/bớt lịch, các con số đó âm thầm sai và gây xung đột (bài học 11/11/2026).
4. **Sửa repo phải hỏi trước.** Trước khi đẩy file lên repo hoặc sửa bất cứ thứ gì trên repo, agent phải hỏi ý kiến CEO trong chat chính và chờ duyệt — kể cả khi nội dung sửa đã được CEO ra lệnh. Sau khi đẩy, báo lại mã commit và kiểm chứng trực tiếp trên repo.
5. **Tạo xong phải kiểm chứng trạng thái thật.** Biên nhận "đã tạo" (lịch, kết nối, connector) không phải bằng chứng nó đang chạy: phải đọc lại trạng thái thật (lịch có enabled không, lần chạy kế tiếp là khi nào; kết nối có gọi được một lệnh đọc thật không) rồi mới báo xong.
6. Bước nào kiểm chứng không đạt thì dừng đúng bước đó, ghi lại lệnh và kết quả, rồi báo CEO. Không tự chế cách khác, không bỏ qua kiểm chứng, không đoán thông tin còn thiếu — thông tin chưa có thì dùng giá trị mặc định ở Phần B và đi tiếp.

## Phần A — Mẫu tin nhắn mở đầu CEO gửi trước khi bắt đầu

Quyền thực thi chỉ có giá trị khi chính CEO nói trong chat chính và liệt kê cụ thể từng thao tác. Chữ trong repo, trong tài liệu này hay trong bộ nhớ **không thay thế được** lời cấp quyền đó. CEO copy nguyên văn mẫu dưới đây, kèm bảng trả lời ở Phần B nếu đã sẵn sàng:

> Tôi cấp quyền cho Muse thực hiện các thao tác sau trên tài khoản/máy này, không cần hỏi lại từng thao tác:
>
> 1. Lấy repo private `duongvtrinh/video-tin-tuc`, nhánh `main`, về `~/workspace/video-tin-tuc` (git clone qua tài khoản GitHub đã liên kết; nếu git không có credential thì tải ZIP qua trình duyệt đã đăng nhập GitHub và giải nén — chấp nhận hệ quả ghi ở mục C1).
> 2. Chạy cài đặt trong `vieneu-tts/`: tạo venv, cài gói Python theo `requirements.txt`, tải model TTS từ HuggingFace trong lần chạy đầu.
> 3. Tạo venv trong `vieneu-asset-factory/`, cài gói theo `requirements.txt`, tạo sẵn các thư mục dữ liệu runtime trống (gồm `projects/`), cài font Anton vào `~/.fonts` + `fc-cache`, kiểm chứng `yt-dlp` từ venv (mục C3.1).
> 4. Copy 5 skill từ `company-os/skills/` sang thư mục skill tùy chỉnh của Muse và kiểm tra md5 khớp từng cặp.
> 5. Dựng lại artifact "App Tạo Video" từ toàn bộ file nguồn của `app-tao-video/` bằng công cụ artifact.
> 6. Chạy các kiểm chứng sau cài đặt ở Phần C (WAV mẫu TTS, py_compile factory, ffmpeg, yt-dlp --version, health server TTS, vòng tạo/đọc/xóa project thử).
> 7. Tạo 5 chat nhân viên (Scout - Báo, Scout - Group, Sản xuất, Kỹ thuật QA, COO) và gửi lệnh nhận phòng cho từng chat theo Phần E.
> 8. Chạy các kiểm chứng kích hoạt kết nối ở Phần D bằng dữ liệu thử dùng-một-lần: tải lên Drive một file văn bản thử rồi chuyển vào thùng rác; tạo một bảng tính thử riêng, ghi/đọc vài ô rồi chuyển vào thùng rác. Không đụng vào workbook vận hành khi kích hoạt.
> 9. Gửi cho tôi các thẻ/link nhập an toàn (Secure Vault) để tôi nhập: key Pixabay, key Pexels, thông tin đăng nhập Facebook — và sau khi tôi nhập xong, dựng connector + helper cho hai key và đăng nhập thử Facebook bằng trình duyệt để kiểm chứng.
>
> Các khai báo vận hành của tôi nằm ở bảng Bước 0 đính kèm. Mục nào tôi chưa trả lời thì dùng mặc định trong bảng và đi tiếp, không dừng cài đặt.
> **Không nằm trong quyền này:** sửa hoặc đẩy file lên repo GitHub — việc đó hỏi ý kiến tôi riêng từng lần.

Ba ghi chú trung thực cần đọc trước khi gửi:

- Thẻ phê duyệt của hệ thống vẫn hiện ở một số thao tác (ví dụ tải lên Drive) kể cả sau khi CEO đã cấp quyền trong chat. Cấp quyền trong chat không tắt được thẻ hệ thống; thẻ cần được bấm trong thời hạn của nó (thẻ upload Drive: 30 phút).
- CEO nên ở lại online cho tới khi qua bước đăng nhập GitHub: lần đăng nhập đầu trên máy mới có thể đòi mã xác thực gửi qua email. Nên kết nối Gmail với Muse **trước khi bắt đầu** để Muse tự đọc mã; nếu Gmail chưa kết nối, CEO phải tự đọc email và gửi mã vào chat (đã xảy ra ở phiên 11/11/2026 và được ghi vào bộ nhớ như một khoảng trống đã biết).
- Key và mật khẩu chỉ nhập qua Secure Vault. Không ai — kể cả trong mẫu tin nhắn này — gửi key/mật khẩu dạng chữ vào chat, vào file hay vào log.

## Phần B — Bước 0: khai báo thông tin công ty

Ngay sau khi clone xong và kiểm tra môi trường xong, **chat chính chủ động gửi tin nhắn hỏi bổ sung** cho CEO (không chờ CEO tự biết phải cung cấp gì), liệt kê các mục dưới đây kèm ví dụ mẫu. CEO trả lời gộp một lần hoặc từng mục đều được; agent lưu từng câu trả lời vào bộ nhớ ngay khi nhận, theo đúng mẫu câu ở mục B2, rồi xác nhận lại đã lưu gì và còn thiếu gì.

### B1. Bảng khai báo

**Bảng A — CEO phải cung cấp** (thiếu 1 trong 4 mục bắt buộc 1–4 thì dừng đúng bước cần nó; các mục còn lại thiếu vẫn đi tiếp):

| # | Thông tin | Bắt buộc? | Ghi chú / mặc định |
| --- | --- | --- | --- |
| 1 | **Email khai báo của tài khoản Muse này** (ví dụ `006@vuachim.com`) | **Bắt buộc để vận hành** | Chữ ký định danh duy nhất của chi nhánh: đối chiếu cột B tab COO_TASKS, là email người sản xuất ghi vào TASKS.L QUOTA, và tên COO chính là email này. Không dùng email Drive/GitHub/Facebook thay thế. Chưa có thì ghi "chưa xác định" và chưa nhận dòng COO_TASKS nào |
| 2 | **Workbook vận hành** — xác nhận dùng workbook đang chạy "Video HQ — Tin Tức" (ID `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`) | **Bắt buộc để vận hành** | Không tạo mới, không ghi đè. Đủ 8 tab: TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN, SHIFT_CHECKIN. Công ty khác hẳn thì mới tạo workbook mới từ `company-os/google-sheet-spec.md`, bắt đầu trống |
| 3 | **Thư mục Drive bàn giao** — xác nhận thư mục "Video Muse" (ID `1bA21n3Y3YiY6HSjLUEFmxnJXLnjtSJGc`) và quyền hiện tại | **Bắt buộc để vận hành** | Chỉ bàn giao lên đúng thư mục này. Không tự tạo thư mục khác, không tự thay đổi quyền; quyền anyone-with-link là do CEO cấp |
| 4 | **Repo GitHub** — xác nhận `duongvtrinh/video-tin-tuc`, nhánh `main`, private | **Bắt buộc** | Đọc BOOTSTRAP + 5 skill trước khi làm việc. Repo không bao giờ chuyển public để tiện clone |
| 5 | **Cấp phép toàn quyền cho QA hoàn tất bàn giao** (có/không) | Cần trước lần upload Drive đầu tiên | Đã cấp: QA tự chạy lại upload và hoàn tất bàn giao không hỏi lại trong chat — nhưng thẻ phê duyệt hệ thống vẫn hiện mỗi lần và phải bấm trong 30 phút; cấp phép không tắt được thẻ. Chưa cấp: lúc bàn giao phải chắc CEO đang có mặt để bấm thẻ |
| 6 | **Lịch bot có bật không** | Không bắt buộc | Mặc định **tắt** — chỉ tạo khi CEO duyệt riêng (xem Phần E4). Bộ lịch hiện hành nằm ở Phần E4, không liệt kê lại ở đây |
| 7 | **Facebook** — đăng nhập qua Secure Vault + liên kết Accounts Center khi cần làm việc Facebook | Tùy chọn | Không bắt buộc cho sản xuất video. Quy trình ở Phần D5 |
| 8 | **Gmail đã kết nối chưa** | Nên có trước khi đăng nhập GitHub | Chưa kết nối thì CEO phải tự gửi mã xác thực email vào chat khi GitHub đòi; ghi nhận khoảng trống này vào bộ nhớ |
| 9 | **API key Pixabay + Pexels** | Tùy chọn — thiếu vẫn đi tiếp | Key miễn phí tại pixabay.com/api và pexels.com/api. Nhập qua Secure Vault theo Phần D4. Thiếu key thì lớp stock báo SKIPPED và Production rơi về ảnh AI — không chặn vận hành |

**Bảng B — Đã quyết, chỉ thông báo, không hỏi:**

| # | Thông tin | Nội dung đã chốt |
| --- | --- | --- |
| 10 | Ngưỡng inline voice | 10.000.000 byte — file lớn hơn đi đường tải theo đoạn (quyết 05/11/2026) |
| 11 | Đường dẫn factory | Đã ghi sẵn trong repo (core.ts tự phân giải) — tài khoản mới không sửa đường dẫn |
| 12 | Cửa chặn hạn mức tuần | Đầu ca chạy lệnh subscription-status status, đọc % tuần đã dùng trực tiếp trong dòng 'Usage: N% of ... weekly limit' (quyết CEO 13/11/2026, DEC-263 — thay DEC-202); N ≥ 95% thì Scout dừng hẳn ca (không quét/chấm/ghi, không báo cáo ca), Pipeline nhận 0 chủ đề READY mới (báo cáo ca vẫn làm cho video đang dở). Ca quét COO_TASKS được miễn cửa chặn này. Nếu lệnh không đọc được N thì dùng số Sheet dự phòng (dòng COO_CHECKIN mới nhất của chính chi nhánh, rồi TASKS.L QUOTA). TASKS.L và COO_CHECKIN chỉ còn là bản ghi để CEO kiểm tra. Reset hạn mức thì số trực tiếp tự hạ, hoạt động lại bình thường, không cần lệnh mở lại |

### B2. Ghi vào bộ nhớ của chính tài khoản — mẫu câu bắt buộc

Ngay khi CEO trả lời Bảng A, ghi vào `MEMORY.md` của chính tài khoản này đúng các mẫu câu sau, đúng thứ tự. **Không copy bộ nhớ của tài khoản cũ.**

Bước 1 — dòng khai báo (bắt buộc, trước mọi ca quét COO_TASKS):

```
Email khai báo của tài khoản Muse này: <email CEO cung cấp> — dùng làm chữ ký định danh, đối chiếu cột B tab COO_TASKS
```

Bước 2 — tên COO (bắt buộc, cùng lúc với Bước 1):

```
Tên COO chính là email khai báo này (COO (<email khai báo>))
```

Bước 3 — quy tắc email người sản xuất (bắt buộc):

```
Quy tắc thống nhất email người sản xuất (ghi vào TASKS.L QUOTA): email người sản xuất = email khai báo trong bộ nhớ của tài khoản Muse này; thứ tự lấy email là (1) email Production ghi ở cột D (ASSIGNEE) của dòng TASKS CLAIMED, nếu có và khớp email khai báo — email khai báo thắng khi khác nhau; (2) nếu cột D trống hoặc bàn giao ghi "chưa xác định" thì ghi "chưa xác định — hỏi CEO" và lúc đó hỏi CEO (không tự lấy email khai báo trong bộ nhớ thay thế — quyết CEO 08/11/2026, R4-09 phương án B).
```

Bước 4 — cấp phép QA (chỉ ghi khi CEO đã cấp ở mục 5):

```
CEO cấp phép toàn quyền cho Kỹ thuật QA ngày <ngày> lúc <giờ> +07: QA được chạy lại upload Drive và hoàn tất bàn giao Drive + Sheet mà không hỏi lại CEO trong chat; thẻ phê duyệt của hệ thống cho lệnh upload vẫn hiện theo luật hệ thống và cần bấm trong 30 phút, đó không phải là hỏi lại.
```

Bước 5 — ghi nhận key stock (chỉ ghi khi đã cấp và kiểm chứng xong ở Phần D4):

```
API key Pixabay và Pexels đã cấp qua Secure Vault ngày <ngày>: connector custom.pixabay và custom.pexels đã tạo, kiểm chứng bằng search_stock "<từ khóa thử>" trả ứng viên từ cả hai nguồn (vault). Không ghi giá trị key.
```

Bước 6 — tự kiểm tra bộ nhớ (bắt buộc): đọc lại `MEMORY.md`, xác nhận Bước 1–3 đều có, đúng chính tả email, không có email khác xen vào; Bước 4–5 có đúng với những gì CEO đã cấp. Thiếu một dòng bắt buộc thì coi như chưa khai báo xong — quay lại Bước 1, không đi tiếp.

## Phần C — Cài đặt máy

Làm đúng thứ tự C0 đến C5. Mỗi bước có thư mục làm việc, lệnh, kết quả mong đợi và thời lượng ước tính.

### C0. Kiểm tra tiên quyết — báo thiếu tất cả trong một lần

- **Thư mục:** `~`. **Lệnh:** một lượt kiểm tra duy nhất bằng script `check-prereqs.sh` ở gốc repo (`bash ~/workspace/video-tin-tuc/check-prereqs.sh`): kiểm tra `ffmpeg -version`, `python3 --version`, `bun --version`, thư viện hệ thống `libsndfile`, `df -h`, mạng tới HuggingFace. In bảng đạt/thiếu cho **toàn bộ** mục rồi mới kết thúc; thiếu thì liệt kê hết một lần, không dừng ở mục đầu tiên.
- **Kết quả mong đợi:** mọi mục đạt. Đã kiểm chứng thật 11/11/2026: ffmpeg 8.1.2, Python 3.12.3, bun 1.4.4, đĩa trống ~148 GB (repo ~313 MB sau giải nén, hai venv + model vẫn dư). Font Anton chưa có ở bước này là bình thường (cài ở C3). **Thời lượng:** dưới 1 phút.

### C1. Lấy repo về máy

- **Thư mục:** `~/workspace/`. **Đường chính:** `git clone` repo `duongvtrinh/video-tin-tuc` nhánh `main` qua tài khoản GitHub đã liên kết (đăng nhập GitHub xem Phần D1 — làm trước hoặc ngay tại bước này; nếu GitHub đòi mã email, đọc từ Gmail đã kết nối hoặc nhờ CEO gửi mã).
- **Đường dự phòng đã dùng thật 11/11/2026:** nếu git trên máy không có credential cho repo private (clone ẩn danh chắc chắn thất bại), đăng nhập GitHub bằng trình duyệt (thông tin đăng nhập lấy từ Secure Vault) rồi tải ZIP của nhánh `main` và giải nén vào `~/workspace/video-tin-tuc`. Hệ quả phải chấp nhận và ghi vào bộ nhớ: bản ZIP **không có `.git`** — về sau mọi thay đổi lên repo phải đi qua giao diện web GitHub, và quy tắc một nguồn (đầu tài liệu) áp dụng nghiêm ngặt cho mọi file trùng tên.
- **Kết quả mong đợi:** thư mục đích có đủ 4 thư mục cấp cao nhất — `app-tao-video/`, `company-os/`, `vieneu-asset-factory/`, `vieneu-tts/` — cùng `README.md` và `BOOTSTRAP.md`. **Thời lượng:** vài phút tùy mạng (repo ~300 MB).
- **Nối layout clone với đường dẫn vận hành (bắt buộc, làm ngay sau clone):** nhiều file vận hành trong repo (unit systemd TTS, script watchdog, body lịch watchdog, app core.ts) dùng đường dẫn `~/workspace/company-os/`, `~/workspace/asset-factory/`, `~/workspace/vieneu-tts-api/` (layout máy gốc). Tạo 3 symlink để các đường đó trỏ đúng vào bản clone — không có 3 symlink này, dịch vụ TTS, watchdog và app đều không tìm thấy file:
  ```bash
  ln -s ~/workspace/video-tin-tuc/vieneu-asset-factory ~/workspace/asset-factory
  ln -s ~/workspace/video-tin-tuc/company-os ~/workspace/company-os
  ln -s ~/workspace/video-tin-tuc/vieneu-tts ~/workspace/vieneu-tts-api
  ```
  Kiểm chứng: `ls -l ~/workspace/asset-factory ~/workspace/company-os ~/workspace/vieneu-tts-api` đều hiện symlink trỏ vào `video-tin-tuc/`. (App core.ts từ 14/11/2026 đã tự nhận thêm đường clone `video-tin-tuc/` nên app chạy được cả khi thiếu symlink — nhưng unit systemd và script watchdog vẫn cần symlink, nên vẫn phải tạo đủ 3.)

### C2. VieNeu TTS

Script `vieneu-tts/start.sh` gộp tạo venv + cài thư viện + chạy server foreground vào một lệnh — chạy nó sẽ không biết cài xong hay chưa. Cách làm đã kiểm chứng: cài đặt và chạy server là hai việc riêng — chạy script chỉ-cài-đặt `vieneu-tts/install.sh` trước (tạo venv + cài gói theo `requirements.txt` + kiểm tra import soundfile, không chạy server), rồi mới chạy server riêng khi cần.

- **Thư mục:** `~/workspace/video-tin-tuc/vieneu-tts/`
- **Kết quả mong đợi (kiểm chứng thật 11/11/2026):** venv ~912 MB; model tải từ HuggingFace lần đầu ~85 giây (đứt kết nối giữa chừng rồi tự thử lại thành công là bình thường — ghi nhận, không coi là lỗi dừng); health ở cổng 8000 trả ok, 11 giọng, sample rate 24 kHz.
- **Kiểm chứng âm thanh:** `.venv/bin/python tts_cli.py --text "Xin chào cả nhà!" --voice "Hữu Quân" --speed 1.0 --out out.wav` → WAV 24 kHz nghe được (phiên thật: 1,10 giây).
- **Lưu ý vận hành:** server chạy nền bằng nohup sẽ không tự sống lại sau khi máy ảo thay mới — trước ca sản xuất đầu tiên mỗi ngày phải kiểm tra health cổng 8000, chết thì khởi động lại. **Thời lượng:** 3–6 phút.

### C3. Asset Factory — venv, font Anton, thư mục runtime

- **Thư mục:** `~/workspace/video-tin-tuc/vieneu-asset-factory/`
- **Lệnh:** `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`, rồi `mkdir -p projects`; cài font Anton vào `~/.fonts` và chạy `fc-cache`:
  ```bash
  mkdir -p ~/.fonts
  curl -L -o ~/.fonts/Anton-Regular.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf
  fc-cache -f
  ```
  Kiểm chứng: `fc-list | grep -i anton` phải hiện `Anton-Regular.ttf: Anton:style=Regular`.
- **Kết quả mong đợi:** gói cài đủ (Pillow, numpy, weasyprint, underthesea, websocket-client, yt-dlp — phiên bản đã kiểm chứng: Pillow 13.0.0, numpy 2.5.4, weasyprint 70.0, underthesea 9.5.0, websocket-client 1.9.0+, yt-dlp 2026.10.26); `fc-list` thấy Anton; thư mục `projects/` tồn tại.
- **Kiểm chứng:** `.venv/bin/python -m py_compile bin/*.py` không lỗi; `ffmpeg -version` chạy được. **Thời lượng:** 2–4 phút.
- Thư mục `projects/` là **bắt buộc**: nó chứa dữ liệu runtime nên không nằm trong git; thiếu nó, App Tạo Video lỗi ngay khi liệt kê project ở lần kiểm tra đầu (đã gặp thật). Mọi thư mục runtime khác factory cần mà không nằm trong git cũng phải tạo trống tại bước này và liệt kê tại đây.

### C3.1. yt-dlp và bẫy PATH

- yt-dlp đã nằm trong `requirements.txt` của factory (chốt `yt-dlp==2026.10.26`), **không cài riêng cấp hệ thống** — máy mới không có yt-dlp trên PATH và điều đó là bình thường.
- **Kiểm chứng:** trong thư mục factory, `.venv/bin/yt-dlp --version` phải trả đúng phiên bản chốt trong `requirements.txt`.
- **Bẫy đã kiểm chứng thật:** `bin/dl_facebook_video.py` tìm yt-dlp trên PATH bằng `shutil.which`. Chạy script bằng python của venv mà **chưa kích hoạt venv** (hoặc chưa thêm `.venv/bin` vào PATH) sẽ báo "yt-dlp chưa cài" dù gói đã cài đúng. Cách chạy đúng: `source .venv/bin/activate` rồi mới `python bin/dl_facebook_video.py <url> <output.mp4> [--cookies <file>]`.
- Điều kiện dùng: không cookies thì chỉ tải video công khai; video riêng tư cần file cookies do CEO xuất, **không commit vào repo**. Trước khi tải phải kiểm tra tính nguyên gốc bằng trình duyệt thực (luật trong skill `media-video-production`). Script cần `ffmpeg`/`ffprobe` (đã có ở C0) và dùng sẵn `--no-check-certificates` vì proxy của máy dùng chứng chỉ tự ký.
- Bảo trì: yt-dlp hay hỏng khi Facebook thay đổi — cập nhật số phiên bản chốt trong `requirements.txt`, cài lại vào venv, kiểm chứng lại `--version` + một lần tải thử video công khai. (Đề xuất sửa script tự tìm yt-dlp theo `sys.executable` — ĐỀ XUẤT chờ CEO duyệt, chưa làm.)

### C4. Skills — copy đúng 5 skill, kiểm md5 đúng 5 cặp

- **Thư mục:** `~/workspace/video-tin-tuc/company-os/skills/` → copy sang `~/workspace/custom-skills/`, rồi `md5sum` file `SKILL.md` từng cặp và đối chiếu.
- **Đúng 5 skill:** `media-coo`, `media-scout`, `media-video-production`, `media-video-tech-qa`, `thumbnail-xep-lop`. Skill `media-topic-scoring` đã đóng (điểm đã chuyển vào `media-scout`), không copy. Mọi con số trong mục này là **5** — bản cũ từng tự mâu thuẫn 4/5, bản này chốt một chỗ duy nhất.
- Sau khi copy, đọc kỹ cả 5 skill cùng `company-os/media-search/LOGIC.md` trước ca làm việc đầu tiên. **Thời lượng:** dưới 1 phút.

### C5. App Tạo Video — dựng lại theo manifest, không đếm số cứng

- **Thư mục:** `~/workspace/video-tin-tuc/app-tao-video/`. **Lệnh:** dựng lại artifact "App Tạo Video" (slug `app-tao-video`) bằng công cụ artifact, chép nguyên toàn bộ cây nguồn — không viết lại giao diện từ mô tả. Quy tắc của app (trong `app-tao-video/AGENTS.md`): không tự build từ thư mục, không chạy `bun run build`, không sửa tay file bundle hay `.generated` — chỉ dùng công cụ artifact.
- **Đối chiếu theo manifest:** file nguồn phải khớp danh sách chuẩn trong `app-tao-video/MANIFEST.md` (danh sách đường dẫn + số lượng file, sinh từ cây repo; khi thêm/bớt file nguồn thì cập nhật manifest trong cùng đợt); file migration mới chỉ hợp lệ khi đã đăng ký trong `drizzle/meta/_journal.json`. **Không dùng số đếm file cứng làm điều kiện dừng** — bài học thật: hướng dẫn cũ ghi cứng 47 file, repo có 48 (thêm migration `0004_drop_snapshots_table.sql` hợp lệ), và con số sai đó đã chặn cả phiên cài đặt.
- File trong `server/.generated/` do hệ thống tự sinh khi dựng: không thuộc manifest, không đối chiếu, không sửa tay.
- **Kết quả mong đợi trên máy mới:** app mở được, quy trình 6 bước (Kịch bản → Phân cảnh → Media → TTS & Karaoke → Preview → Render) hiển thị đúng, danh sách project **trống** (đúng — project đọc từ factory của chính máy này). Kiểm chứng bằng một vòng thật: tạo project thử → đọc lại (mặc định 9:16, tiếng Việt) → xóa; xong thì danh sách sạch lại. **Thời lượng:** 5–10 phút.

## Phần D — Các kết nối cần thiết

Thứ tự khuyến nghị: D1 GitHub (trước C1) → D2 Drive → D3 Sheets → D4 key stock → D5 Facebook. Mọi kết nối đều qua luồng chính thức của Muse hoặc Secure Vault; **không nhập mật khẩu/key vào chat, không ghi credential vào file, bộ nhớ hay log**. Mỗi kết nối chỉ tính là xong khi qua được lệnh kiểm chứng thật ghi ở cuối mục (quy tắc 5).

### D1. GitHub

- Lưu thông tin đăng nhập github.com vào Secure Vault (thẻ nhập an toàn), để trình duyệt dùng khi cần. Đăng nhập thử: mở repo, thấy đúng repo private, nhánh `main`.
- Nếu GitHub đòi mã xác thực qua email: ưu tiên đọc từ Gmail đã kết nối; chưa kết nối Gmail thì CEO tự đọc email và gửi mã vào chat (ghi nhận khoảng trống ở Bảng A mục 8).

### D2. Google Drive

- Kết nối qua luồng kết nối chính thức. Kiểm chứng bằng API/lệnh đọc thật: thư mục "Video Muse" (ID ở Bảng A mục 3) mở được, đúng chủ sở hữu, đúng quyền hiện tại (anyone-with-link writer nếu CEO đã cấp) — chỉ đọc để xác nhận, không đổi quyền.
- **Kích hoạt quyền tải lên (làm một lần, cần mục 8 của mẫu cấp quyền Phần A):** tải lên một file văn bản thử nhỏ vào thư mục bàn giao, chờ CEO bấm thẻ phê duyệt hệ thống, xác nhận file xuất hiện, rồi chuyển file thử vào thùng rác (khôi phục được 30 ngày). Không dùng file công việc thật cho lần kích hoạt này.

### D3. Google Sheets

- Kết nối qua luồng chính thức (độc lập với Drive — Drive thông không có nghĩa Sheets đã thông; phiên 11/11/2026 phải kết nối Sheets riêng ở bước sau).
- **Kích hoạt quyền sửa (một lần):** tạo một bảng tính thử **riêng**, ghi vài ô, đọc lại đối chiếu, rồi chuyển bảng thử vào thùng rác. Tuyệt đối không ghi thử lên workbook vận hành.
- **Đối chiếu workbook với spec** (`company-os/google-sheet-spec.md`): đủ 8 tab (TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN, SHIFT_CHECKIN); số cột theo thứ tự tab là 13/15/6/7/7/9/3/4. Lưu ý đã kiểm chứng 11/11/2026: tab COO_TASKS trên workbook thật dùng **khóa tiếng Anh** (ID, ASSIGNEE_EMAIL, TASK, DETAIL, STATUS, COMPLETED_AT, RESULT) — đúng thứ tự và ý nghĩa 7 cột của spec dù nhãn chữ khác văn bản spec; vận hành theo khóa thật trên workbook.

### D4. API key Pixabay + Pexels qua Secure Vault

Đây là quy trình đã chạy thật và kiểm chứng ngày 11/11/2026; làm đúng từng bước:

1. **Đăng ký kết nối API** bằng `credentials.request_api_access` với thông số cố định:
   - Pixabay: provider `pixabay`, placement `query_param:key`, hosts `["pixabay.com"]` (endpoint ảnh `https://pixabay.com/api/`, video `https://pixabay.com/api/videos/`).
   - Pexels: provider `pexels`, placement `custom_header:Authorization`, hosts `["api.pexels.com"]` (key đặt trong header `Authorization` dạng key trần, **không** có tiền tố Bearer).
   Gửi link nhập an toàn cho CEO; CEO nhập key tại trang của nhà cung cấp (key Pixabay xem tại pixabay.com/api/docs khi đã đăng nhập tài khoản Pixabay).
2. **Dựng connector doc:** chạy scaffold `scaffold-connector-docs --provider <pixabay|pexels>` để tạo `~/workspace/custom-connectors/custom.<provider>/CONNECTOR.md` rồi điền theo đúng mẫu (placement và hosts như trên; không ghi giá trị key ở bất kỳ đâu).
3. **Viết helper** `~/workspace/custom-connectors/custom.<provider>/bin/<provider>_search.py` theo đúng giao diện mà `company-os/media-search/search_media.py` gọi ở đường vault:
   - Cách gọi: `[python, helper, "--query", <từ khóa tiếng Anh>, "--media-type", <image|video>]`, timeout 60 giây.
   - Đầu ra: JSON trên stdout dạng `{"hits": [...]}`; mỗi hit có `tags`, `pageURL`, `largeImageURL`, `imageWidth`, `imageHeight`, `duration`. Hit có `largeImageURL` rỗng sẽ bị bỏ qua.
   - Với video, helper tự chọn **một** file tốt nhất làm `largeImageURL` (ưu tiên chiều cao ≥ 720 trước, rồi gần tỉ lệ 9:16 nhất, rồi cao hơn), và `imageWidth`/`imageHeight`/`duration` là của file/video đó. Với ảnh Pexels, `tags` là trường `alt`, `largeImageURL` là bản portrait nếu có.
   - Helper lấy credential qua surrogate từ `/opt/muse/skills/custom-connector-setup/bin/dynamic_credentials.py` (`url_with_surrogate_query_param` cho Pixabay, `add_surrogate_to_request` cho Pexels), tắt redirect trên request đã xác thực, và `py_compile` đạt trước khi nói là chạy được. Key thật chỉ được hệ thống hoán đổi ở request ra đúng host đã đăng ký — helper không bao giờ thấy key.
   - Lưu ý cơ chế của search_media.py: nó thử biến môi trường `PIXABAY_API_KEY`/`PEXELS_API_KEY` trước; không có env mới đi đường vault và báo nguồn là `pixabay (vault)` / `pexels (vault)`. Vận hành chuẩn của công ty là đường vault — không đặt key vào env.
4. **Kiểm chứng hai lớp:** (a) chạy helper trực tiếp một lần tìm ảnh và một lần tìm video — phải ra hit thật; lần gọi đầu tiên bị timeout qua proxy có thể là lỗi thoáng qua, thử lại một lần trước khi kết luận key hỏng (đã gặp thật với Pixabay). (b) chạy trọn đường qua công cụ công ty: `python3 company-os/media-search/search_media.py stock --en-keywords "ocean waves" --media-type image` — kết quả phải có ứng viên với `source` là `pixabay (vault)` và/hoặc `pexels (vault)`. Chỉ khi (b) đạt mới ghi Bước 5 ở mục B2.
5. Nếu gặp 401/403: kiểm tra request có mang credential không, host đã đăng ký chưa, placement có đúng không; chỉ khi request đã mang credential mà vẫn bị từ chối mới đăng ký lại kết nối với `reconnect: true`.

### D5. Facebook

- Lưu thông tin đăng nhập facebook.com vào Secure Vault bằng thẻ nhập an toàn cho trang `https://www.facebook.com/login` (mục 9 của mẫu cấp quyền Phần A).
- **Đăng nhập thử bằng trình duyệt** ngay sau khi CEO nhập xong: mở facebook.com, đăng nhập bằng thông tin đã lưu; đạt khi thấy trang chủ/bảng tin kèm tên tài khoản. Phiên 11/11/2026 đăng nhập thẳng, không gặp xác thực hai lớp hay checkpoint; nếu gặp checkpoint/mã xác nhận thì **dừng ở bước đó và báo CEO**, không tự vượt qua. Chỉ kiểm tra đăng nhập: không đăng bài, không nhắn tin, không đổi cài đặt.
- Việc quét bài/group qua connector Facebook là phạm vi riêng; liên kết Accounts Center làm theo tài liệu connector khi CEO yêu cầu. Bot không tự tham gia group mới, không tự đăng.
- Nhắc bảo mật một lần cho CEO: nên bật xác thực hai lớp cho tài khoản Meta.

### D6. Gmail (khuyến nghị)

- Kết nối Gmail trước khi đăng nhập GitHub lần đầu (xem D1). Nếu chưa kết nối, ghi vào bộ nhớ đúng một dòng sự thật: "Gmail chưa kết nối với Muse" kèm hệ quả (mã xác thực phải gửi tay qua chat) — để các phiên sau không tưởng là đã có.

## Phần E — Kích hoạt vận hành (sau khi cài máy xong)

Phần này không chặn cài đặt. Mục nào chưa làm được vì CEO chưa trả lời ở Phần B thì ghi "chưa xác định" và để lại.

### E1. Khai báo vào bộ nhớ

Làm đủ mục B2 (Bước 1–6) ngay khi CEO trả lời. Đây là điều kiện trước mọi ca quét COO_TASKS: chưa có email khai báo thì dừng ở bước vận hành, báo CEO — nhưng không quay lại chặn Phần C/D.

### E2. Tạo 5 chat nhân viên

Tạo và gửi lệnh nhận phòng cho từng chat: **Scout - Báo** và **Scout - Group** (cùng skill `media-scout`), **Sản xuất** (`media-video-production`), **Kỹ thuật QA** (`media-video-tech-qa`), **COO** (`media-coo`). Nội dung nhận phòng tối thiểu: vai trò + skill của phòng; ID workbook và ID thư mục Drive (lấy ở Bảng A — không ghi lặp con số ở đây, trỏ về Bảng A); email khai báo đọc từ bộ nhớ; và quy tắc kênh giao việc — phòng chỉ làm việc khi được giao qua một trong ba kênh: (1) chat chính, (2) COO qua tab COO_TASKS, (3) lịch bot đã được CEO duyệt.

### E3. Quyền bàn giao của QA

Nếu CEO đã cấp ở Bảng A mục 5, ghi Bước 4 của B2 vào bộ nhớ và thông báo rõ cho phòng QA trong lệnh nhận phòng: QA được tự chạy lại upload Drive và hoàn tất bàn giao không hỏi lại trong chat; thẻ phê duyệt hệ thống vẫn hiện mỗi lần upload, phải bấm trong 30 phút — quyền này không tắt được thẻ.

### E4. Bộ lịch bot — tạo đủ bộ và kiểm chứng trạng thái thật

**Bộ lịch hiện hành** (chốt ngày 11/11/2026, bổ sung tts-watchdog ngày 13/11/2026 — chi tiết đầy đủ ở `company-os/scheduled-tasks-setup.md`, tài liệu đó là chuẩn cho riêng việc lịch; mục này chỉ tóm các điểm không được sai). Tất cả chạy hằng ngày, múi giờ `Asia/Saigon`, kết quả báo về chat COO (trừ tts-watchdog báo về chat chính), owner là goal bootstrap của chính tài khoản này. Trước khi tạo lịch, tạo goal bootstrap của tài khoản này (slug `vieneu-media-company-bootstrap`, tên "VieNeu Media Company Bootstrap") — goal này làm owner cho cả 7 lịch (xem `scheduled-tasks-setup.md` mục "Cách tạo từng lịch", bước 0). Chưa có goal thì chưa tạo lịch.

| ID lịch | Giờ chạy | Việc chính |
| --- | --- | --- |
| coo-scan-0300 | 03:00 | COO điểm danh tại tab COO_CHECKIN rồi quét tab COO_TASKS; không có dòng của mình thì im lặng |
| scout-scan-0600 | 04:00 | Scout quét chủ đề + chấm điểm ngay trong cùng lượt quét (ca sáng; ID giữ nguyên, giờ dời từ 06:00 theo quyết CEO 13/11/2026) |
| prod-pipeline-0500 | 05:00 | Pipeline nhận 1 lô tối đa 3 chủ đề READY mỗi ca, sản xuất tuần tự Production → QA → bàn giao Drive |
| scout-scan-1300 | 13:00 | Scout quét chủ đề + chấm điểm ngay trong cùng lượt quét (ca chiều) |
| prod-pipeline-1400 | 14:00 | Pipeline nhận 1 lô tối đa 3 chủ đề READY mỗi ca, sản xuất tuần tự Production → QA → bàn giao Drive |
| bot-hoc-hoi-2000 | 20:00 | Học-hỏi: rút bài học từ lỗi lặp lại có bằng chứng, cải tiến template/skill/SOP (đổi chuẩn chỉ đề xuất để CEO quyết) |
| tts-watchdog | mỗi 30 phút | Giám sát server TTS: kiểm tra /health (cổng 8000); lỗi thì cài lại unit systemd từ bản chuẩn + restart tối đa 2 lần; khỏe thì im lặng, chỉ báo chat chính khi đã phải restart hoặc vẫn không lên |

### E5. Kiểm chứng trước ca quét COO_TASKS đầu tiên — đủ 7 điểm

Thiếu 1 điểm bắt buộc thì dừng ca quét, báo CEO:

1. **Repo + tài liệu:** đúng repo/nhánh/private; đã đọc BOOTSTRAP, spec Sheet, bot-sop, LOGIC và 5 skill; App Tạo Video đối chiếu manifest đạt (mục C5).
2. **Bộ nhớ:** đã qua Bước 6 của B2 (có email khai báo, tên COO, quy tắc TASKS.L).
3. **Workbook:** đúng workbook ở Bảng A, đủ 8 tab, số cột 13/15/6/7/7/9/3/4 (chi tiết khóa cột xem mục D3). Không tạo mới, không đổi tên tab, không xóa dòng cũ.
4. **Drive:** đúng thư mục ở Bảng A, mở được; quyền tải lên đã kích hoạt (mục D2).
5. **Tài sản nhị phân:** sfx đủ 8 file `.mp3`; bgm đủ 24 track + `README.md` + `bgm_catalog.json` (đã nằm trong git — clone là có, chỉ đếm kiểm chứng).
6. **Lịch:** trạng thái thật đúng như E4 đã kiểm chứng; ca quét COO_TASKS được miễn cửa chặn hạn mức tuần (Bảng B mục 12).
7. **Stock:** chạy 1 lần `search_stock` thật (mục D4 bước 4b). Có ứng viên từ nguồn vault là đạt; chưa có key thì ghi "chưa xác định" ở Bảng A mục 9 và vẫn đi tiếp.

### E6. Kỷ luật repo khi vận hành

- Mọi thay đổi lên repo (file mẫu lịch, skill, tài liệu, code) đều theo quy tắc 4: hỏi CEO trong chat chính → chờ duyệt → đẩy → báo mã commit + kiểm chứng trên repo. Lời duyệt cho một đợt không tự kéo dài sang đợt sau.
- Khi sửa body một lịch đang chạy, cập nhật file mẫu tương ứng trong repo **trong cùng đợt** (sau khi được duyệt) để mẫu và lịch thật không lệch nhau; ngược lại, sửa file mẫu mà không sửa lịch đang chạy thì lịch vẫn chạy theo body cũ — phải nói rõ điều này khi trình duyệt.
- Trước khi tải lên một file trùng tên, đối chiếu phiên bản đang ở trên repo (số dòng, đoạn đầu, commit mới nhất) với bản định tải — sự cố trộn bản hướng dẫn ngày 11/11/2026 (mục F) bắt đầu từ việc bỏ qua bước này.

## Phần F — Sự cố đã gặp thật và cách phòng

| Sự cố | Nguyên nhân | Cách phòng trong bản v3 |
| --- | --- | --- |
| Clone ẩn danh bằng git thất bại | Repo private, clone thẳng không có quyền | D1 + C1: đăng nhập GitHub qua vault trước; ZIP qua trình duyệt là đường dự phòng có ghi hệ quả |
| Đăng nhập GitHub đòi mã email, CEO phải tự đọc và gửi mã | Gmail chưa kết nối với Muse | D6: kết nối Gmail trước; CEO online tới khi qua bước đăng nhập (Phần A) |
| Lời "toàn quyền, không hỏi lại" đã nói và ghi vào bộ nhớ nhưng quá trình vẫn bị chặn | Quyền ghi trong bộ nhớ/nói chung chung không qua được kiểm tra hệ thống | Mẫu cấp quyền cụ thể ở Phần A, CEO gửi trong chat chính trước khi bắt đầu |
| Quá trình dừng vì app có 48 file trong khi hướng dẫn ghi 47 | Số 47 ghi cứng ở nhiều chỗ, không cập nhật khi thêm migration 0004 | C5: đối chiếu manifest + sổ migration; mỗi con số ghi một chỗ |
| App lỗi khi liệt kê project trên máy mới | Thư mục runtime `projects/` không nằm trong git | C3: tạo sẵn thư mục runtime trống |
| File tự sinh trong repo lệch với mã nguồn của chính nó | File `.generated` bị đưa vào đối chiếu như file nguồn | C5: file tự sinh không thuộc manifest, không sửa tay |
| Tải model HuggingFace đứt kết nối giữa chừng | Mạng không ổn định ở lần tải đầu | C2: tự thử lại là bình thường, không coi là lỗi dừng |
| Script tải video báo "yt-dlp chưa cài" dù đã cài | Script tìm yt-dlp trên PATH, venv chưa kích hoạt | C3.1: kiểm chứng `.venv/bin/yt-dlp --version`, bắt buộc kích hoạt venv khi chạy script |
| Lần gọi Pixabay đầu tiên timeout, tưởng key hỏng | Proxy ra ngoài chậm thoáng qua | D4 bước 4: thử lại một lần trước khi kết luận; lần thử lại trả kết quả dưới 1 giây |
| Bộ lịch báo "đã tạo đủ, đã bật" nhưng thật ra ca phụ không còn, Scout bị tắt/lưu trữ và chưa từng chạy | Chỉ tin biên nhận tạo lịch, không đọc lại trạng thái thật | E4: kiểm chứng sau tạo 4 bước, gồm đối chiếu lần chạy kế tiếp và lịch sử chạy sáng hôm sau |
| Agent đẩy thay đổi lên repo khi CEO mới ra lệnh sửa nội dung, chưa hỏi riêng việc đẩy | Suy diễn quyền đẩy từ lần duyệt trước | Quy tắc 4 + E6: sửa repo/đẩy repo luôn hỏi riêng từng đợt; mẫu cấp quyền Phần A ghi rõ việc này không nằm trong quyền cài đặt |
| Hai bản BOOTSTRAP bị trộn: bản v2 (214 dòng) bị ghi đè bởi bản cũ đã sửa (501 dòng) trong một đợt đẩy vội | Tải file trùng tên mà không đối chiếu phiên bản đang ở trên repo | Quy tắc một nguồn ở đầu tài liệu + E6: đối chiếu số dòng/đoạn đầu/commit trước khi tải thay thế |
| Luật "12 claim/ngày", "4 ca/ngày" âm thầm sai khi đổi bộ lịch, gây xung đột giữa các tài liệu | Con số suy ra từ số lịch bị ghi lặp ở nhiều văn bản chuẩn | Quy tắc 3: chỉ ghi trần theo ca; khi đổi bộ lịch không còn con số tổng/ngày nào phải sửa theo |

## Tiêu chí "cài xong"

**Cài máy xong** khi cả 5 kiểm chứng Phần C đều đạt:

1. C0: đủ ffmpeg, Python, bun, libsndfile, đĩa trống, mạng HuggingFace.
2. C1: repo đã về đúng đường dẫn, đúng nhánh `main`, vẫn private.
3. C2: server TTS khỏe ở cổng 8000 (ok, 11 giọng, 24 kHz) và WAV mẫu giọng Hữu Quân nghe được.
4. C3 + C3.1 + C4: factory biên dịch không lỗi, font Anton đã nhận, `projects/` tồn tại, yt-dlp trong venv đúng phiên bản chốt; 5 skill đã copy, 5 cặp md5 khớp.
5. C5: App Tạo Video dựng xong, đối chiếu manifest đạt, vòng tạo → đọc → xóa project thử đi qua hết, danh sách cuối cùng trống đúng như máy mới.

**Vận hành sẵn sàng** khi thêm đủ các mục sau (báo riêng với kết luận cài máy):

1. Khai báo: B2 Bước 1–6 hoàn tất và tự kiểm tra đạt.
2. Kết nối: D1–D5 kiểm chứng thật đạt (Drive/Sheets gồm cả kích hoạt bằng dữ liệu thử; stock đạt ở mức `search_stock` trọn đường hoặc ghi rõ "chưa xác định" nếu CEO chưa cấp key; Facebook đăng nhập thử đạt hoặc CEO chưa yêu cầu).
3. Chat nhân viên: đủ 5 chat, đã nhận phòng (E2); quyền QA đúng như CEO cấp (E3).
4. Lịch bot: nếu CEO duyệt bật — đủ bộ theo E4 và đã qua kiểm chứng trạng thái thật; nếu chưa duyệt — ghi rõ "lịch đang tắt theo mặc định".
5. Kiểm chứng 7 điểm ở E5 đạt, sẵn sàng cho ca quét COO_TASKS đầu tiên.

Thiếu mục nào thì báo đúng mục đó chưa đạt, kèm lệnh và kết quả đã ghi lại — không kết luận "xong phần lớn".

---

*Ghi chú soạn bản: v3 đã tích hợp 15 quyết định kiểm toán ngày 11/11/2026 (nguồn hạn mức chuẩn COO_CHECKIN, mốc leo thang TASKS.N, mốc 2 buổi sáng cho lô cũ, file improvement-log dùng chung, health TTS đầu ca). v3 hợp nhất bản gốc (501 dòng, lưu tại BOOTSTRAP-legacy-2026-11-11.md), bản v2 (214 dòng, đã duyệt 11/11/2026) và các quyết định + sự cố ngày 11/11/2026. Bản này là BOOTSTRAP.md trong repo kể từ đợt thay ngày 11/11/2026. Đợt sửa 14/11/2026 (kiểm tra cài mới): đã làm xong script check-prereqs.sh, install.sh cho TTS và file manifest của app (không còn là đề xuất); đề xuất còn chờ duyệt duy nhất là sửa dl_facebook_video.py tự tìm yt-dlp theo sys.executable.*
