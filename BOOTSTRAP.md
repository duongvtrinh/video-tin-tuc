# BOOTSTRAP v2 — Dựng lại hệ thống VieNeu Media Company trên máy mới

> **Bản chính thức từ ngày 11/11/2026** — đây là `BOOTSTRAP.md` hiện hành của repo private `duongvtrinh/vieneu-media-company`. Bản hướng dẫn cũ được lưu dự phòng ngay trong repo tại file `BOOTSTRAP-legacy-2026-11-11.md` (và trong lịch sử git); cần tra lại bản cũ thì mở file đó.
> Nội dung rút từ một phiên cài đặt thật ngày 11/11/2026, trong đó phần cài đặt kỹ thuật chỉ mất khoảng 10 phút nhưng quá trình bị chặn hỏi lại 4–5 lần vì quyền, đăng nhập và số liệu trong hướng dẫn cũ tự mâu thuẫn.

## Mục đích và nguyên tắc

Tài liệu này dựng lại toàn bộ hệ thống sản xuất video trên một máy Muse mới, gồm bốn thành phần: `vieneu-tts/` (đọc văn bản thành giọng nói), `vieneu-asset-factory/` (dựng tài sản và video), `app-tao-video/` (ứng dụng Tạo Video) và `company-os/` (kỹ năng và logic vận hành).

Nguyên tắc quan trọng nhất của bản v2 là tách hai loại việc vốn bị trộn lẫn trong bản cũ:

- **Cài máy** (Phần C) là việc kỹ thuật thuần túy: clone repo, cài thư viện, tải model, dựng lại ứng dụng và chạy kiểm chứng. Loại việc này có tiêu chí xong rõ ràng, làm tự động được và phải chạy một mạch tới khi đạt.
- **Kích hoạt vận hành** (Phần D) là việc cần CEO trả lời hoặc xác nhận: email định danh, workbook Google Sheets, thư mục Drive, quyền bàn giao, lịch bot. Loại việc này làm sau khi cài máy xong và không được chặn cài đặt.

Ba quy tắc áp dụng cho toàn bộ tài liệu:

1. Mỗi con số hoặc sự kiện chỉ ghi ở một chỗ duy nhất. Các phần khác trỏ về chỗ đó, không ghi lặp con số của mình.
2. Đối chiếu file theo danh sách chuẩn (manifest), không theo một con số đếm cứng. Số file thay đổi hợp lệ khi có migration hoặc file mới được đăng ký đúng quy trình.
3. Bước nào kiểm chứng không đạt thì dừng đúng bước đó, ghi lại lệnh và kết quả, rồi báo CEO. Không tự chế cách khác, không bỏ qua kiểm chứng, không đoán thông tin còn thiếu — thông tin chưa có thì dùng giá trị mặc định đã ghi ở Phần B và đi tiếp.

## Phần A — Mẫu tin nhắn mở đầu CEO gửi trước khi bắt đầu

Đây là bước làm đầu tiên, trước cả khi clone. Ở phiên cài đặt thật, các điểm chặn lớn nhất không nằm ở kỹ thuật mà ở quyền: lời dặn “toàn quyền, không hỏi lại” nói chung chung, hoặc ghi trong repo hay trong bộ nhớ, đều không được hệ thống tính là cấp quyền. Quyền chỉ có giá trị khi chính CEO nói trong chat chính và liệt kê đủ cụ thể từng thao tác.

CEO copy nguyên văn mẫu dưới đây vào chat chính và gửi, kèm bảng trả lời ở Phần B nếu đã sẵn sàng:

> Tôi cấp quyền cho Muse thực hiện các thao tác cài đặt sau trên máy này, không cần hỏi lại từng thao tác:
>
> 1. Clone repo private `duongvtrinh/vieneu-media-company`, nhánh `main`, về `~/workspace/vieneu-media-company` bằng git qua tài khoản GitHub đã liên kết.
> 2. Chạy script cài đặt trong `vieneu-tts/`, tạo môi trường ảo (venv) cho VieNeu TTS và cài các gói Python theo `requirements.txt` của nó.
> 3. Tải model TTS từ HuggingFace về máy trong lần chạy đầu tiên.
> 4. Tạo venv trong `vieneu-asset-factory/`, cài các gói Python theo `requirements.txt` của nó, tạo sẵn các thư mục dữ liệu runtime trống (gồm cả `projects/`), cài font Anton vào `~/.fonts` rồi chạy `fc-cache`, và kiểm chứng `yt-dlp` chạy được từ venv (xem mục C3.1).
> 5. Copy 4 skill từ `company-os/skills/` sang thư mục skill tùy chỉnh của Muse và kiểm tra mã md5 khớp từng cặp.
> 6. Dựng lại artifact “App Tạo Video” từ toàn bộ file nguồn của `app-tao-video/` bằng công cụ artifact.
> 7. Chạy các kiểm chứng sau cài đặt ở Phần C: tạo file WAV mẫu bằng TTS, biên dịch thử các script của factory, kiểm tra `ffmpeg`, kiểm tra `yt-dlp --version` từ venv của factory, kiểm tra server TTS và kiểm tra ứng dụng tạo / đọc / xóa project thử.
>
> Các khai báo vận hành của tôi nằm ở bảng Bước 0 đính kèm. Mục nào tôi chưa trả lời thì dùng giá trị mặc định ghi trong bảng và đi tiếp, không dừng cài đặt.

Ba ghi chú trung thực cần đọc trước khi gửi mẫu trên:

- Chữ viết trong repo, trong tài liệu này hay trong bộ nhớ của Muse **không thay thế được** lời cấp quyền của CEO trong chat chính. Đây là luật của hệ thống, không phải lựa chọn của người viết hướng dẫn.
- Thẻ phê duyệt của hệ thống vẫn có thể hiện ở một số thao tác (ví dụ tải lên Drive) kể cả sau khi CEO đã cấp quyền trong chat. Cấp quyền trong chat không tắt được thẻ hệ thống, và thẻ vẫn cần được bấm trong thời hạn của nó.
- CEO nên ở lại online cho tới khi qua bước đăng nhập GitHub. Lần đăng nhập đầu tiên trên máy mới có thể đòi mã xác thực gửi qua email. Nên kết nối Gmail với Muse **trước khi bắt đầu** để Muse tự đọc mã; nếu Gmail chưa kết nối, CEO sẽ phải tự đọc email và gửi mã vào chat như đã xảy ra ở phiên 11/11/2026.

## Phần B — Bước 0: CEO trả lời trước khi clone

Chat chính chủ động gửi bảng này cho CEO ngay khi bắt đầu, không chờ CEO tự biết phải cung cấp gì. CEO trả lời gộp một lần hoặc từng mục đều được; câu trả lời được lưu vào bộ nhớ của chính tài khoản Muse này ngay khi nhận.

| # | Mục cần khai báo | Bắt buộc? | Mặc định nếu CEO chưa trả lời |
| --- | --- | --- | --- |
| 1 | Email định danh của chi nhánh (email của tài khoản Muse này, dùng làm chữ ký định danh và đối chiếu cột B của tab COO_TASKS) | Bắt buộc để vận hành, không chặn cài máy | Ghi “chưa xác định”. Cài máy vẫn đi tiếp; chưa có email thì chưa nhận dòng COO_TASKS nào |
| 2 | Xác nhận workbook vận hành dùng bản đang chạy: “Video HQ — Trụ sở Muse”, không tạo mới, không ghi đè | Bắt buộc để vận hành, không chặn cài máy | Dùng workbook đang chạy theo Phần D; không tạo workbook mới |
| 3 | Xác nhận thư mục Drive bàn giao dùng thư mục đang chạy: “Video Muse”, và quyền hiện tại của thư mục | Bắt buộc để vận hành, không chặn cài máy | Dùng thư mục đang chạy; không tự tạo thư mục khác, không tự đổi quyền |
| 4 | Quyền bàn giao toàn quyền cho QA: QA có được tự chạy lại việc tải video lên Drive và hoàn tất bàn giao mà không hỏi lại trong chat không? | Cần trả lời trước lần bàn giao đầu tiên | Chưa cấp. Khi bàn giao, QA phải chắc CEO đang có mặt để bấm thẻ phê duyệt của hệ thống trong thời hạn |
| 5 | Lịch bot có bật không? | Không bắt buộc | **Tắt.** Không tạo lịch Scout, Pipeline, bot học hỏi hay quét COO_TASKS nào cho tới khi CEO duyệt riêng từng lịch |
| 6 | Facebook đã liên kết lại qua Meta Accounts Center chưa? | Tùy chọn — không cần cho sản xuất video | Chưa liên kết. Bỏ qua mọi việc Facebook cho tới khi CEO xác nhận |
| 7 | API key Pixabay và Pexels (để tìm ảnh thật thay vì rơi về ảnh AI) | Tùy chọn — thiếu vẫn đi tiếp | Chưa cấp. Lớp ảnh stock báo bỏ qua (SKIPPED) và quy trình vẫn chạy; key khi cấp phải nhập qua Secure Vault, không nhập vào chat, không ghi giá trị key vào bất kỳ file nào |

Hai mục đã quyết, chỉ thông báo, không hỏi CEO: ngưỡng file giọng nói inline là 10.000.000 byte (file lớn hơn đi đường tải theo đoạn), và đường dẫn factory đã ghi sẵn trong repo — tài khoản mới không sửa đường dẫn.

## Phần C — Cài đặt máy

Làm đúng thứ tự C0 đến C5. Mỗi bước ghi rõ thư mục làm việc, lệnh, kết quả mong đợi và thời lượng ước tính để người chạy biết khi nào một lần chờ lâu là bình thường và khi nào là lỗi thật.

### C0. Kiểm tra tiên quyết — báo thiếu tất cả trong một lần

- **Thư mục làm việc:** thư mục gốc của máy (`~`)
- **Lệnh:** chạy một script kiểm tra duy nhất (đề xuất bổ sung vào repo dưới tên `check-prereqs.sh`) lần lượt kiểm tra: `ffmpeg -version`, `python3 --version`, `bun --version`, thư viện hệ thống `libsndfile` (TTS cần thư viện này trên Linux), dung lượng đĩa trống bằng `df -h`, và kết nối mạng tới HuggingFace. Script in ra một bảng đạt / thiếu cho **toàn bộ** mục rồi mới kết thúc; thiếu mục nào thì liệt kê hết trong cùng một lần chạy, không dừng ở mục đầu tiên.
- **Kết quả mong đợi:** mọi mục đều đạt. Phiên bản đã kiểm chứng thật trên máy cài ngày 11/11/2026: ffmpeg 8.1.2, Python 3.12.3, bun 1.4.4, đĩa còn trống khoảng 148 GB — mức này là dư cho repo (khoảng 313 MB sau giải nén), hai venv và model TTS. Font Anton chưa có ở bước này là bình thường; font được cài ở bước C3.
- **Thời lượng ước tính:** dưới 1 phút.

Thiếu mục nào thì cài bổ sung mục đó rồi chạy lại script kiểm tra. Không bắt đầu C1 khi bảng kiểm tra còn mục thiếu, trừ font Anton.

### C1. Clone repo bằng git

- **Thư mục làm việc:** `~/workspace/`
- **Lệnh:** clone qua tài khoản GitHub đã liên kết của Muse: `git clone` repo `duongvtrinh/vieneu-media-company`, nhánh `main`, vào `~/workspace/vieneu-media-company`. Nếu lần đăng nhập đầu đòi mã xác thực email, Muse đọc mã từ Gmail đã kết nối (xem Phần A) và CEO xác nhận ngay trong lúc còn online.
- **Kết quả mong đợi:** thư mục đích có đủ 4 thư mục cấp cao nhất — `app-tao-video/`, `company-os/`, `vieneu-asset-factory/`, `vieneu-tts/` — cùng `README.md` và tài liệu bootstrap; repo vẫn ở trạng thái private, đúng nhánh `main`.
- **Thời lượng ước tính:** vài phút, tùy mạng (repo khoảng 300 MB).

Không dùng bản ZIP tải qua trình duyệt thay cho clone git. ZIP chỉ là đường dự phòng khi git không dùng được, vì ZIP mất lịch sử git nên sau này không đẩy code lên repo được. Repo là private và **không bao giờ** được chuyển sang public để tiện clone.

### C2. VieNeu TTS — tách script chỉ-cài-đặt khỏi chạy server

Script hiện tại `vieneu-tts/start.sh` gộp ba việc vào một lệnh: tạo venv, cài thư viện, rồi khởi động server ở chế độ foreground (chạy mãi không tự kết thúc). Người hoặc agent chạy script này sẽ không biết cài đặt đã xong hay chưa. Bản v2 đề xuất tách một script chỉ-cài-đặt (đề xuất tên `install.sh`) làm đúng ba việc — tạo venv, cài gói theo `requirements.txt`, kiểm tra thư viện `soundfile` nhập được — rồi thoát kèm mã lỗi rõ ràng. Chạy server là một lệnh riêng, thực hiện sau khi cài đặt đã được xác nhận xong.

- **Thư mục làm việc:** `~/workspace/vieneu-media-company/vieneu-tts/`
- **Lệnh:** chạy script chỉ-cài-đặt; sau đó khởi động server bằng lệnh chạy server riêng ở cổng 8000, chạy nền để kiểm chứng ở bước tiếp theo.
- **Kết quả mong đợi (đã kiểm chứng thật ngày 11/11/2026):** venv tạo xong, dung lượng khoảng 912 MB; model TTS tải từ HuggingFace trong lần chạy đầu mất khoảng 85 giây; kiểm tra sức khỏe của server ở cổng 8000 trả về trạng thái ok, 11 giọng, tần số lấy mẫu 24 kHz.
- **Kiểm chứng âm thanh:** chạy `.venv/bin/python tts_cli.py --text "Xin chào cả nhà!" --voice "Hữu Quân" --speed 1.0 --out out.wav` — kết quả là file WAV định dạng 24 kHz, nghe được. Ở phiên thật, file mẫu dài 1,10 giây.
- **Thời lượng ước tính:** 3–6 phút, phần lớn là tải model lần đầu.

Lưu ý đã biết trước: kết nối tới HuggingFace có thể đứt giữa chừng khi tải model và tự thử lại thành công. Ghi nhận việc thử lại trong báo cáo tiến độ, không coi đó là lỗi phải dừng. Ngược lại, nếu script chỉ-cài-đặt báo thiếu `libsndfile` thì đó là lỗi thật — cài thư viện hệ thống theo hướng dẫn trong thông báo lỗi rồi chạy lại.

### C3. Asset Factory — venv, font Anton và thư mục runtime

- **Thư mục làm việc:** `~/workspace/vieneu-media-company/vieneu-asset-factory/`
- **Lệnh:**

  ```bash
  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
  mkdir -p projects
  ```

  Sau đó cài font Anton từ Google Fonts vào `~/.fonts` và chạy `fc-cache` để hệ thống nhận font.

- **Kết quả mong đợi:** các gói trong `requirements.txt` cài đủ — gồm Pillow, numpy, weasyprint, underthesea, websocket-client và yt-dlp; hệ thống nhận diện được font Anton; thư mục `projects/` tồn tại.
- **Kiểm chứng:** `python -m py_compile bin/*.py` chạy không lỗi, và `ffmpeg -version` chạy được.
- **Thời lượng ước tính:** 2–4 phút.

Bước tạo thư mục `projects/` là bắt buộc, không phải tùy chọn. Thư mục này chứa dữ liệu runtime nên không nằm trong git; trên máy mới nó không tồn tại sẵn. Ở phiên cài đặt thật, thiếu thư mục này khiến App Tạo Video lỗi khi liệt kê project ngay ở lần kiểm tra đầu tiên, và chỉ hết lỗi sau khi thư mục trống được tạo. Cùng nguyên tắc, mọi thư mục dữ liệu runtime khác mà factory cần nhưng không nằm trong git đều phải được tạo trống ở bước này và liệt kê tại đây — danh sách đó chỉ ghi ở đoạn này.

Đọc thêm `PIPELINE.md` trong thư mục factory để nắm thứ tự pipeline trước khi sản xuất video thật. Việc đọc này thuộc Phần D, không chặn kiểm chứng ở bước này.

### C3.1. yt-dlp — tải video Facebook và bẫy PATH phải tránh

Mục này tách riêng vì yt-dlp là điểm dễ gây lỗi “chưa cài” giả nhất trên máy mới, dù bước C3 đã cài đúng mọi thứ.

- **Vai trò:** yt-dlp dùng để tải video/reel Facebook công khai qua script `vieneu-asset-factory/bin/dl_facebook_video.py`.
- **Không cần cài riêng ở cấp hệ thống:** yt-dlp đã nằm trong `requirements.txt` của factory, chốt phiên bản `yt-dlp==2026.10.26`, và được cài vào venv của factory ở bước C3.
- **Thư mục làm việc:** `~/workspace/vieneu-media-company/vieneu-asset-factory/`
- **Kiểm chứng sau cài:** chạy `.venv/bin/yt-dlp --version` trong thư mục factory. Kết quả mong đợi đúng `2026.10.26` — đã kiểm chứng thật trên máy vừa cài ngày 11/11/2026.
- **Thời lượng ước tính:** dưới 1 phút cho kiểm chứng; thời gian tải video tùy dung lượng và mạng.

**Bẫy PATH — phần quan trọng nhất, đã kiểm chứng thực tế ngày 11/11/2026:** script `dl_facebook_video.py` tìm yt-dlp trên PATH (bằng `shutil.which`) và gọi lệnh `yt-dlp` theo PATH. Máy mới không có yt-dlp hệ thống. Hệ quả đã gặp thật:

- Chạy `.venv/bin/python bin/dl_facebook_video.py ...` mà **chưa kích hoạt venv** thì script báo `DL-ERROR` kiểu “yt-dlp chưa cài”, dù gói đã cài xong trong venv.
- Thêm `.venv/bin` vào PATH thì yt-dlp chạy thật; lần kiểm chứng đó chỉ còn lỗi ở bước tải vì dùng link thử không có thật.

Vì vậy, lỗi “yt-dlp chưa cài” từ script này **không có nghĩa là chưa cài** — trước hết phải kiểm tra PATH và trạng thái kích hoạt venv.

**Cách chạy đúng — bắt buộc kích hoạt venv trước khi chạy script:**

```bash
source .venv/bin/activate
# hoặc tương đương: PATH="$PWD/.venv/bin:$PATH"
python bin/dl_facebook_video.py <url-video-facebook> <output.mp4> [--cookies <cookies.txt>]
```

Cú pháp đầy đủ: `python bin/dl_facebook_video.py <url-video-facebook> <output.mp4> [--cookies <cookies.txt>]`. Thành công, script in `DL-OK` kèm tên file, độ phân giải, thời lượng và dung lượng; thất bại in `DL-ERROR`.

**Điều kiện dùng:**

- Không có cookies thì chỉ tải được video công khai, không cần đăng nhập. Video riêng tư hoặc trong nhóm kín cần `--cookies` với file `cookies.txt` do CEO xuất; tuyệt đối không commit file cookies vào repo.
- Trước khi tải phải kiểm tra tính nguyên gốc của video bằng trình duyệt thực (luật CEO ngày 10/11/2026, hiện chỉ ghi trong skill `media-video-production`): video đã bị chèn logo hoặc phụ đề do bên khác reupload thì bỏ qua, không tải, và ghi lý do vào media-log.
- Video tải về chỉ là ứng viên: ghi media-log (link + nguồn + phân loại) và vẫn phải qua soi trực quan như mọi tư liệu khác.

**Phụ thuộc đi kèm:** yt-dlp cần `ffmpeg` để ghép file (script dùng `--merge-output-format mp4`, định dạng `bv+ba/b`) và `ffprobe` để kiểm tra file tải về; cả hai đã nằm trong kiểm tra tiên quyết C0. Script có sẵn cờ `--no-check-certificates` vì proxy ra ngoài của máy dùng chứng chỉ tự ký (đã kiểm chứng ngày 09/11/2026).

**Bảo trì:** yt-dlp thường hỏng khi Facebook thay đổi. Khi tải lỗi hàng loạt thì cập nhật số phiên bản chốt trong `requirements.txt` lên bản mới nhất, cài lại vào venv, rồi kiểm chứng lại bằng `--version` và một lần tải thử video công khai thật. Không tự cập nhật lẻ ngoài `requirements.txt` để tránh lệch phiên bản giữa các máy.

**Đề xuất sửa dứt điểm — ĐỀ XUẤT chờ CEO duyệt, chưa có trong repo:** sửa `dl_facebook_video.py` để tự tìm yt-dlp theo thư mục của chính Python đang chạy (`sys.executable`) thay vì phụ thuộc PATH. Khi đó bẫy PATH biến mất và không cần nhớ kích hoạt venv nữa. Chưa được duyệt thì vẫn áp dụng cách chạy đúng ở trên.

### C4. Skills — copy đúng 4 skill và kiểm md5 đúng 4 cặp

- **Thư mục làm việc:** `~/workspace/vieneu-media-company/company-os/skills/`
- **Lệnh:** copy 4 thư mục skill sang thư mục skill tùy chỉnh của Muse (`~/workspace/custom-skills/`), rồi chạy `md5sum` trên file `SKILL.md` của từng skill ở cả hai nơi và đối chiếu từng cặp.
- **Danh sách đúng 4 skill:** `media-coo`, `media-scout`, `media-video-production`, `media-video-tech-qa`. Skill `media-topic-scoring` đã đóng (thang điểm đã chuyển vào `media-scout`), không copy.
- **Kết quả mong đợi:** 4 cặp md5 khớp tuyệt đối — không phải 5 cặp. Bản hướng dẫn cũ mâu thuẫn ở đúng chỗ này: một nơi ghi copy 4 skill, nơi khác lại đòi kiểm khớp 5 cặp, trong khi repo chỉ có 4 thư mục skill. Bản v2 chốt một con số duy nhất: **4**.
- **Thời lượng ước tính:** dưới 1 phút.

Sau khi copy, đọc kỹ cả 4 skill cùng `company-os/media-search/LOGIC.md` trước ca làm việc đầu tiên. Các luật vận hành đã chốt nằm trong skill, không nằm trong bộ nhớ của máy cũ — đó là lý do máy mới dựng lại được mà không cần bộ nhớ cũ.

### C5. App Tạo Video — dựng lại theo manifest, không đếm số cứng

- **Thư mục làm việc:** `~/workspace/vieneu-media-company/app-tao-video/`
- **Lệnh:** dựng lại artifact “App Tạo Video” (slug `app-tao-video`) bằng công cụ artifact, chép nguyên toàn bộ cây nguồn — không viết lại giao diện từ mô tả, vì giao diện nằm trong chính mã nguồn đó.
- **Cách đối chiếu mới:** so cây nguồn với **manifest** — danh sách file chuẩn kèm theo repo (đề xuất bổ sung một file danh sách trong repo, liệt kê từng đường dẫn). File có trong manifest thì phải có trên máy và khớp nội dung; file migration mới được tính là hợp lệ khi nó đã được đăng ký trong sổ migration của app, `drizzle/meta/_journal.json`. Khác manifest mà không giải thích được bằng sổ đăng ký thì mới dừng và báo CEO.
- **Thời lượng ước tính:** 5–10 phút.

Bài học thật đằng sau quy tắc này: hướng dẫn cũ ghi cứng “đúng 47 file, khác thì dừng” ở ít nhất bốn chỗ. Repo thực tế có **48 file**, vì migration `drizzle/0004_drop_snapshots_table.sql` được thêm vào sau khi con số 47 được viết. Migration này hoàn toàn hợp lệ — nó đã đăng ký ở mục thứ tư trong `drizzle/meta/_journal.json`, và chính hướng dẫn cũ ở phần mô tả logic cũng ghi bảng snapshots đã bị xóa bằng đúng migration 0004 đó. Con số cứng sai đã chặn đứng cả quá trình cài đặt và tốn thêm một vòng xác minh. Từ bản v2, không tài liệu nào được ghi lại con số 47 hay 48 như một điều kiện dừng; chỉ manifest và sổ đăng ký migration mới có quyền quyết định.

Một ngoại lệ phải ghi rõ: file trong `server/.generated/` là file do hệ thống **tự sinh ra khi dựng** ứng dụng. File tự sinh không thuộc manifest nguồn, không đưa vào đối chiếu, và không sửa tay — khi mã nguồn thay đổi, dựng lại ứng dụng để file này sinh lại cho khớp. Bản chép cũ của file này từng nằm trong repo và đã lỗi thời so với chính mã nguồn của nó; giữ nó trong đối chiếu chỉ tạo thêm một điểm chặn giả.

**Kết quả mong đợi trên máy mới:** ứng dụng mở được, quy trình 6 bước (Kịch bản → Phân cảnh → Media → TTS & Karaoke → Preview → Render) hiển thị đúng, và danh sách project **trống**. Trống là đạt — máy mới chưa có project nào, vì project đọc từ thư mục factory của chính máy này. Không kỳ vọng thấy 4 project như trên máy cũ. Kiểm chứng bằng một vòng thật: tạo project thử → đọc lại (đúng mặc định khung 9:16, tiếng Việt) → xóa mềm → xóa hẳn; sau khi xóa, thư mục project phải sạch lại.

## Phần D — Kích hoạt vận hành (làm sau khi cài máy xong)

Phần này không chặn cài đặt. Mục nào chưa làm được vì CEO chưa trả lời ở Phần B thì ghi “chưa xác định” và để lại, không quay sang chặn Phần C.

1. **Kết nối Google Sheets và Drive** qua luồng kết nối chính thức của Muse — không nhập mật khẩu vào chat, không ghi thông tin đăng nhập vào git. Kiểm chứng workbook: mở được workbook đang chạy ở Phần B và đếm đủ 7 tab (TOPICS, TASKS, QA_LOG, DECISIONS, COO_TASKS, CEO_REPORTS, COO_CHECKIN), đồng thời kiểm số cột của các tab COO_TASKS, CEO_REPORTS và COO_CHECKIN theo đặc tả trong `company-os/google-sheet-spec.md`. Kiểm chứng Drive: mở được đúng thư mục bàn giao đã xác nhận ở Phần B. Không tạo workbook hay thư mục mới thay thế.
2. **Khai báo email định danh vào bộ nhớ** của chính tài khoản này, ngay khi CEO trả lời mục 1 ở Phần B: ghi email khai báo (dùng làm chữ ký định danh, đối chiếu cột B tab COO_TASKS), ghi tên COO chính là email đó, và ghi quy tắc email người sản xuất cho cột hạn mức. Không copy bộ nhớ hay email của tài khoản cũ; không dùng email của dịch vụ khác (Drive, GitHub, Facebook) thay cho email khai báo. Chưa có email khai báo thì tài khoản này chưa nhận bất kỳ dòng COO_TASKS nào.
3. **Tạo các chat nhân viên:** Scout – Báo, Scout – Group, Sản xuất, Kỹ thuật QA và COO, mỗi chat gắn đúng skill của phòng đó (hai chat Scout dùng chung `media-scout`). Phòng chỉ làm việc khi được giao qua một trong ba kênh: chat chính, COO qua tab COO_TASKS, hoặc lịch bot đã được CEO duyệt.
4. **Lịch bot:** mặc định không tạo lịch nào. Các lịch Scout (4 ca/ngày), Pipeline (4 ca/ngày), bot học hỏi (hằng ngày) và quét COO_TASKS (06:00 hằng ngày) chỉ được tạo khi CEO duyệt riêng, theo nội dung mẫu trong `company-os/crons/` và `company-os/scheduled-tasks-setup.md`.
5. **Facebook và API key stock:** chỉ liên kết Facebook qua Meta Accounts Center khi CEO xác nhận ở Phần B; chỉ tạo kết nối Pixabay / Pexels sau khi CEO nhập key qua Secure Vault, và kiểm chứng bằng một lần tìm ảnh stock thật. Thiếu cả hai mục này, sản xuất video vẫn đi tiếp.

## Phần E — Sự cố đã gặp thật và cách phòng

| Sự cố trong phiên 11/11/2026 | Nguyên nhân | Cách phòng trong bản v2 |
| --- | --- | --- |
| Clone ẩn danh bằng git thất bại | Repo là private, clone thẳng không có quyền đọc | Clone bằng git qua tài khoản GitHub đã liên kết (C1); không chuyển repo sang public |
| Đăng nhập GitHub đòi mã xác thực qua email, CEO phải tự đọc và gửi mã | Gmail chưa kết nối với Muse nên Muse không tự đọc được mã | Kết nối Gmail trước khi bắt đầu; CEO ở lại online tới khi qua bước đăng nhập (Phần A) |
| Lời “toàn quyền, không hỏi lại” đã nói và ghi vào bộ nhớ nhưng quá trình vẫn bị chặn qua đêm | Quyền ghi trong bộ nhớ hoặc nói chung chung không qua được kiểm tra của hệ thống | Mẫu cấp quyền cụ thể ở Phần A, do CEO gửi trong chat chính trước khi bắt đầu |
| Quá trình dừng vì app có 48 file trong khi hướng dẫn ghi 47 | Con số 47 ghi cứng ở nhiều chỗ và không được cập nhật khi thêm migration 0004 | Đối chiếu theo manifest và sổ đăng ký migration; mỗi con số chỉ ghi ở một chỗ (C5) |
| App lỗi khi liệt kê project ngay lần kiểm tra đầu trên máy mới | Thư mục runtime `vieneu-asset-factory/projects/` không nằm trong git nên chưa tồn tại | Tạo sẵn các thư mục runtime trống ở bước C3 |
| File hợp đồng tự sinh trong repo lệch so với mã nguồn của chính nó | File do hệ thống sinh khi dựng bị đưa vào repo và vào đối chiếu như file nguồn | File tự sinh không thuộc manifest, không đối chiếu, không sửa tay; dựng lại để sinh lại (C5) |
| Tải model từ HuggingFace đứt kết nối giữa chừng | Mạng không ổn định trong lần tải đầu khoảng 85 giây | Ghi trước trong C2: việc tự thử lại là bình thường, không coi là lỗi dừng |
| Script tải video báo “yt-dlp chưa cài” dù đã cài | Script tìm yt-dlp trên PATH, máy không có yt-dlp hệ thống, venv chưa kích hoạt | Mục C3.1: kiểm chứng `.venv/bin/yt-dlp --version` và bắt buộc kích hoạt venv trước khi chạy script; đề xuất sửa script theo `sys.executable` |

## Tiêu chí “cài xong”

Chỉ kết luận cài đặt hoàn tất khi **cả 5 kiểm chứng của Phần C đều đạt**:

1. Script kiểm tra tiên quyết (C0) báo đủ mọi mục: ffmpeg, Python 3.12, bun, `libsndfile`, đĩa trống và mạng tới HuggingFace.
2. Repo đã clone bằng git vào đúng đường dẫn, đúng nhánh `main`, vẫn private (C1).
3. Server TTS khỏe ở cổng 8000 (trạng thái ok, 11 giọng, 24 kHz) và file WAV mẫu bằng giọng Hữu Quân nghe được (C2).
4. Factory biên dịch không lỗi, font Anton đã nhận, thư mục `projects/` tồn tại (C3), và yt-dlp trong venv trả đúng phiên bản chốt trong `requirements.txt` (C3.1); 4 skill đã copy và 4 cặp md5 khớp tuyệt đối (C4).
5. App Tạo Video dựng xong, đối chiếu manifest đạt, và vòng tạo → đọc → xóa project thử đi qua hết với danh sách project cuối cùng trống đúng như máy mới (C5).

Thiếu một kiểm chứng thì báo đúng kiểm chứng đó chưa đạt, kèm lệnh và kết quả đã ghi lại — không kết luận “xong phần lớn”. Phần D chưa làm xong không làm thay đổi kết luận cài máy; nó được báo riêng dưới tiêu đề kích hoạt vận hành.

---

*Ghi chú: bản v2 này đã được CEO duyệt và đưa vào repo ngày 11/11/2026, thay `BOOTSTRAP.md` bản cũ. Bản cũ nằm tại `BOOTSTRAP-legacy-2026-11-11.md` trong cùng repo để dự phòng.*
