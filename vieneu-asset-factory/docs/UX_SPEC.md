# VieNeu Asset Factory — Mô tả UX chi tiết (để tái tạo app)

Tài liệu này mô tả **giao diện và hành vi của app artifact VieNeu Asset Factory**
để một Muse khác tái tạo lại gần giống nhất chức năng app hiện tại. Mã nguồn
pipeline (`bin/`), catalog template (`templates/`), skill (`skills/`) đã nằm
trong repo này; tài liệu này chỉ mô tả **lớp giao diện** chạy trên chúng.
Ngôn ngữ giao diện: tiếng Việt.

> Lưu ý quan trọng: artifact trên Muse **không có chức năng import**. Sang
> Muse khác phải **build lại artifact web_fullstack mới** từ mã trong repo
> này + đặc tả dưới đây, không phải copy artifact cũ sang. Dữ liệu vận hành
> (danh sách project, file kết quả trong app) không chuyển theo repo.

## 1. Tổng quan luồng làm việc

Người dùng đi theo pipeline: **ý tưởng/kịch bản → chia phân cảnh → chia
B-roll → TTS → tạo ảnh → xem trước (preview) → tải video nháp MP4 → đóng
gói ZIP** tương thích schema 2.0 với VieNeu Studio local. App là công cụ
sản xuất, còn các bước AI (viết kịch bản, chia cảnh, chia B-roll, chọn ảnh)
do agent của Muse thực hiện qua chat/skill, app chỉ hiển thị, cho duyệt/sửa
và chạy các bước máy (TTS, tạo ảnh, render, đóng gói).

## 2. Dashboard — "Quản lý dự án"

- Danh sách project: mỗi dòng gồm tên project, ngày tạo, trạng thái từng
  bước pipeline (ký hiệu ✓/… cho từng bước), số ảnh đã tạo.
- Các nút trên dashboard: **Mở workspace**, **Tải ZIP**, **Xóa**,
  **Tạo project mới**.
- Chế độ "Giao việc tự động" (đặt lịch cào tin tức) nằm trong kế hoạch gốc
  nhưng thuộc **Phase 2 — CHƯA build** (đã hoãn theo quyết định 2026-10-24:
  hoàn thiện app trước). Khi tái tạo, KHÔNG tự thêm chế độ này nếu người
  dùng không yêu cầu.
- Đăng Facebook lên Page thuộc **Phase 3 — CHƯA build** (chỉ sản xuất video
  "cho Facebook", việc đăng cần link Facebook + duyệt từng bài; tính đến
  2026-10-25 Facebook vẫn chưa link).

## 3. Workspace từng project — 6 khu vực

### 3.1. Ý tưởng / Link bài báo → Kịch bản
- Nhập topic hoặc dán URL bài báo → nút **"Nhờ agent tạo kịch bản"**
  (tạo task file, trả 1 câu lệnh để dán vào chat; agent chạy xong thì kịch
  bản tự hiện ở đây).
- Có nút **"Bỏ qua"** nếu đã có kịch bản.

### 3.2. Nhập kịch bản có sẵn
- Paste text → agent tách câu → lưu `script{topic, content, sentences}`.

### 3.3. Chia phân cảnh
- Hiển thị danh sách cảnh: text, số từ, thời lượng ước lượng.
- Cho sửa/gộp/tách thủ công trước khi chốt.
- Quy tắc: chia cảnh theo nhịp thị giác bằng **agent (skill broll-director)**,
  TUYỆT ĐỐI không chia bằng regex; câu luận điểm ("Điểm đầu tiên là…")
  giữ nguyên một part, một template.

### 3.4. Chia B-roll
- Hiển thị từng voice part + kế hoạch b-roll: template, loại media, prompt
  ảnh, SFX gợi ý.
- Cho duyệt/sửa từng part.
- B-roll phải bám catalog template thật trong `templates/` (meta.json) +
  cổng kiểm tra xác định (templateId tồn tại, đủ required keys, đúng
  maxLength). Template không tồn tại thì không được chọn.

### 3.5. Tạo ảnh/video
- Nút **"Tạo toàn bộ ảnh"** (chạy song song, thanh tiến độ từng ảnh), xem
  trước từng ảnh, nút **"Tạo lại"** từng ảnh.
- Part nào `mediaType=video` → gắn nhãn **"tạo video trên máy local"** +
  prompt đã nằm sẵn trong `googleFlow/config.json` (tạo video AI bị chặn
  theo khu vực với tài khoản đã dùng — app không tự render video AI).
- Tên file media theo chuẩn duy nhất trong `bin/filename.py`
  (`seg_*`, `broll_*` + rand6) — app và pipeline tra cứu đúng tên này.

### 3.6. Lưu dự án
- Nút **"Đóng gói & Tải ZIP"** → app ráp thư mục chuẩn → file ZIP.
- Trong ZIP kèm `README_HUONG_DAN.txt`: copy thư mục vào `projects/` trên
  máy local → mở VieNeu Studio → TTS → render.
- Lưu ý tương thích (đã kiểm chứng 2026-10-25): copy tay thư mục `<pid>/`
  vào `projects/` local thì load được; nút import ZIP của Studio local thì
  lỗi (nó đòi `project.json` ở gốc ZIP, còn factory đóng dưới tiền tố
  `<pid>/`).

## 4. Các khu vực chức năng đã build thêm (2026-10-23 → 2026-10-25)

### 4.1. Preview player — khu vực xem chính
- **Preview là giao diện xem CHÍNH, thuần HTML/CSS, hiển thị tức thì.**
  MP4 chỉ là nút **"Tải bản nháp"**.
- Player chạy bằng CSS: mỗi part có motion ngẫu nhiên gieo hạt theo partId
  (6 preset), nối part bằng crossfade 0.5s, B-roll overlay lấy từ chính
  `template.html`/CSS thật của template, karaoke chạy theo beat.
- JavaScript chỉ đồng bộ trạng thái rời rạc (~4 lần/giây), không điều khiển
  từng frame.
- Quy tắc voicepart + 500ms (người dùng chốt 2026-10-25): cửa sổ b-roll
  mỗi part = `[startSec, endSec + 500ms)`; trong 500ms đó lớp b-roll cũ nằm
  dưới stage part sau, stage mới fade-in 0.5s phủ đè tạo crossfade; hết
  cửa sổ thì lớp cũ bị gỡ khỏi DOM.
- **Frame-capture đã bị GỠ khỏi app theo quyết định người dùng 2026-10-24
  (không khả thi trên Muse). Khi tái tạo, KHÔNG thêm lại** trừ khi người
  dùng yêu cầu.

### 4.2. Chọn giọng đọc (theo từng part)
- Dropdown giọng đọc cho từng part (11 giọng VieNeu TTS), hỗ trợ đa giọng
  trong một video (ví dụ lời trích dẫn dùng giọng khác).
- Chạy batch TTS theo từng part, đo thời lượng WAV thật để căn timeline.

### 4.3. Chọn nhạc nền (BGM)
- Bộ chọn BGM: 24 track Kevin MacLeod CC-BY 4.0, chia 8 mood
  (calm, dramatic, funny, inspirational, news, sad, suspense, upbeat).
- Agent tự đoán mood theo chủ đề → ghi vào `broll-plan.json`.
- Khi render: BGM lặp (loop), âm lượng 0.12, sidechain ducking theo giọng
  đọc, fade-out 2 giây cuối video. Ghi công tự động vào README của ZIP.

### 4.4. Tỉ lệ khung hình 9:16 / 16:9
- Nút chuyển tỉ lệ trong `input.json` (`aspectRatio`).
- Karaoke: font 54px ở cả hai tỉ lệ; MarginV 20% chiều cao khi 9:16,
  7% khi 16:9. Pill karaoke trong preview bám đáy 20% (9:16) / 7% (16:9).

### 4.5. Thumbnail, fact-check, preflight
- **Thumbnail:** 3 kiểu YouTube tự động cho mỗi project.
- **Fact-check:** trích xuất claims từ kịch bản thành checklist, chạy
  TRƯỚC khi TTS; chỉ dùng số liệu đã kiểm chứng.
- **Preflight:** cổng kiểm tra chặn lỗi trước khi xuất; phải đạt mới cho
  đóng gói.

### 4.6. Các thao tác khác (đối chiếu action thật của app)
- Tạo/xóa/mở project, lưu kịch bản, lưu kế hoạch, xem template, xem
  karaoke, xem file media/ảnh, chọn BGM, lấy file BGM, đặt tỉ lệ, đặt
  giọng đọc, chạy TTS, tạo ảnh, tạo thumbnail, render preview, chạy
  preflight, trích claims, tạo lại một part, xem trạng thái job, tải
  preview, tải ZIP, xuất project.
- Job chạy nền: app hiển thị trạng thái job (đang chạy/xong/lỗi), không
  treo giao diện khi render lâu.

## 5. Quy tắc hiển thị và phụ đề (bất di bất dịch)

- **Hiển thị = đúng nguyên văn kịch bản:** số ("1991"), chữ viết tắt
  ("GDP", "NATO"), hoa/thường giữ nguyên. Chuẩn hóa phát âm chỉ nằm
  trong engine TTS, không đổi chữ hiển thị.
- Phụ đề karaoke: từng từ tô vàng `#FBBF24` theo nhịp đọc (`{\k}`),
  ≤5 từ/dòng, không tách cụm từ, font 54px.
- Part nào có template chữ thật thì **ẩn phụ đề hoàn toàn** (subsHidden),
  chỉ part ảnh nền mới hiện phụ đề — trừ template khai `"hidesSubs": false`
  (ví dụ `story-title`) thì vẫn hiện phụ đề.
- Template full-stage không bị co; template có vị trí `position` trong
  meta thì overlay bám đúng vị trí đó (`top` → y=3%H, `bottom` →
  y=H-h-3%H, còn lại giữa khung).
- Người dùng **không thích bo tròn**: border-radius ≤6px toàn bộ, chỉ giữ
  50% cho hình tròn thật.
- CSS template mới tránh CSS Grid, flexbox đầy đủ, hàm `min()`,
  `@media orientation`, `-webkit-text-stroke` (WeasyPrint không hỗ trợ);
  dùng block/float, width%+max-width, đơn vị `vmin`.

## 6. Mô hình dữ liệu project (schema 2.0)

- `project.json`, `timeline.json` (version "2.0", camelCase),
  `subtitles/sentences.srt` + `synced_cues.srt`, `karaoke.ass`,
  `media/images/`, `media/broll/`, `audio/voice/`,
  `googleFlow/config.json`, cộng file làm việc `input.json`, `script.json`,
  `broll-plan.json`, `img_jobs.json`, `build/`, `export/` (MP4 + ZIP +
  3 thumbnail).
- File từ điển viết tắt `abbr_dict.json` ở gốc thư mục project (nếu có)
  được đóng vào ZIP ở `<pid>/abbr_dict.json`.
- BGM không nằm trong ZIP export (chỉ ghi công trong README).

## 7. Vấn đề mở đã biết (khi tái tạo thì giữ nguyên trạng thái, không tự "sửa")

- **Preview black flicker (2026-10-24, chưa xác nhận):** vệt đen nhấp nháy
  nửa dưới preview, chưa rõ chỉ ở điểm chuyển part hay liên tục, chỉ ở
  preview hay cả MP4. Giả thuyết chưa xác nhận: ảnh part sau chưa decode
  xong trong lúc crossfade 0.5s làm lộ nền đen. Bản sửa "decode trước khi
  fade" đã có trong build nhưng CHƯA được xác nhận — đang chờ người dùng
  trả lời.
- Độ mượt của preview thuần CSS và cơ chế refresh sau khi chạy lại TTS
  mới chỉ kiểm chứng bằng typecheck/review logic, chưa kiểm chứng bằng
  mắt trên project thật.
