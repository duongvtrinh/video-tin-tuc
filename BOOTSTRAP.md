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
  websocket-client). Hệ thống cần thêm: `ffmpeg` và font Anton (templates
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

- Copy 5 skill từ `company-os/skills/` vào `custom-skills/` của Muse
  mới: `media-coo`, `media-scout`, `media-topic-scoring`,
  `media-video-production`, `media-video-tech-qa`.
- Đọc kỹ trước khi chạy: `media-video-production` (pipeline, luật TTS,
  luật media), `media-video-tech-qa` (3 cửa QA), `media-topic-scoring`
  (thang 100 + cửa quan tâm Hot + Khán giả ≥ 30), `media-scout`
  (luật quét nguồn công khai), `media-coo` (phối hợp qua Sheet).
- Các luật đã chốt nằm trong skill, không nằm trong MEMORY của Muse cũ
  — đó là lý do dựng lại được mà không cần bộ nhớ cũ.
- Bắt buộc đọc `company-os/media-search/LOGIC.md`, đặc biệt bài học
  TOPIC-219 04/11/2026: tìm ảnh thật từ bài báo về đúng vụ việc / bài
  đăng công khai trước, AI generic chỉ là fallback khi đã thử nhiều
  từ khóa mà không có ứng viên phù hợp, card chữ không thay thế ảnh.
  Tài khoản Muse mới clone repo về mà bỏ qua mục này sẽ lặp lại đúng
  sai sót TOPIC-219 (toàn ảnh AI / card chữ dù bài gốc đã có ảnh thật).

## 5. Google Sheet (dữ liệu vận hành, không phải code)

- Cùng tài khoản: tìm workbook theo tên "HQ - Công ty 1 người" qua
  connector, dùng tiếp Sheet đang chạy (không tạo mới, không ghi đè).
- Khác tài khoản: tạo workbook mới từ
  `company-os/google-sheet-spec.md` — đúng 13 tab
  (`00_Dashboard` … `12_Repo_Updates`), bắt đầu trống, không chép
  dữ liệu cũ.
- Tuyệt đối không dùng lệnh Drive ghi đè lên file Google Sheet.

## 6. Drive + Facebook + app

- Drive: tìm/tạo thư mục "Video Muse" theo tên qua connector; KHÔNG tự
  chia sẻ công khai (quyết định của CEO).
- Facebook: liên kết lại qua Meta Accounts Center (một tài khoản dùng
  chung); bot không tự tham gia group mới.
- App `app-tao-video` là artifact, không phải repo git: cùng tài khoản
  thì dùng chung artifact, khác tài khoản thì tạo lại app bằng
  artifact tools. Khi tạo lại, CHÉP NGUYÊN TOÀN BỘ cây `app-tao-video/`
  (48 file: client/src App.tsx + lib.ts + 11 component theo tab; server/src
  priv/ 9 module + privileged.ts + actions.ts + schema.ts + script-prompt.ts
  + script-prompt.test.ts; drizzle 0001–0003; theme.css, config, space.json —
  kể cả `AGENTS.md`, `DATA-PLAN.md`, `bun.lock`, `bunfig.toml`,
  `client/build.mjs`, `client/index.html`, `client/src/api.ts`,
  `client/src/globals.d.ts`, `client/src/main.tsx`,
  `server/.generated/privileged.contract.ts`,
  `drizzle/meta/_journal.json`; thiếu một file cũng có thể vỡ build) vào artifact mới — KHÔNG viết lại giao diện
  từ mô tả, vì giao diện nằm trong chính code đó (App.tsx, theme.css)
  nên chép nguyên thì giao diện giống hệt app cũ. Bản build `client/dist`, `server/dist` và `.tsbuildinfo` KHÔNG nằm trong repo (sản phẩm build, build lại khi tạo artifact).

app.db không chuyển qua git nên app mới mở ra danh sách project trống (đó là dữ liệu, không phải giao diện).

> Ghi chú M23: dependency `file:/opt/hatch/skills/spaces/ts-runtime/dist/space-sdk.tgz` trong `package.json` do runtime artifact của Muse cung cấp khi tạo lại app, không nằm trong repo và không cần chép tay — trên máy clone, `bun install` sẽ không resolve được đường dẫn này nếu chạy ngoài Muse, nhưng app vốn chỉ chạy qua artifact nên không chặn clone-and-run theo §6.

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

- 3 lịch: `bot-lang-thang` 4 giờ, `bot-pipeline` 2 giờ,
  `bot-hoc-hoi` hằng ngày — tạo đúng nội dung trong
  `company-os/bot-sop.md` (SOP đầy đủ: bước làm, giới hạn cứng, quy tắc
  báo cáo). Cron là cấu hình của tài khoản, không nằm trong repo.
- 5 chat nhân viên (Scout-Báo, Scout-Group, Scoring, Sản xuất, Kỹ thuật
  QA — 2 chat Scout dùng chung skill media-scout) + chat COO, phối hợp
  qua Sheet.
- Quy tắc điều phối từ Chat chính (lệnh CEO 04/11/2026, sau vụ trùng
  TOPIC-219): Chat chính là kênh CEO giao nhiệm vụ trực tiếp; agent ở
  chat chính là điều phối viên, tự động điều phối nhiệm vụ đến đúng
  phòng liên quan, theo dõi, tổng hợp kết quả và báo cáo lại cho CEO
  ở chat chính. Một nhiệm vụ = một chủ sở hữu duy nhất, khóa bằng
  dòng Assigned / *-DRAFT trong 01_Tasks trước khi làm; cấm chạy song
  song cùng nhiệm vụ ở chat chính và phòng ban. Phòng ban chỉ làm
  nhiệm vụ khi được giao cụ thể từ chat chính (hoặc từ lịch bot đã
  được CEO duyệt, hoặc từ COO trong ca bot-pipeline), không tự phát
  sinh nhiệm vụ sản xuất mới chỉ vì đọc Sheet hay lịch sử fork.

## 9. Kiểm chứng cuối ("dựng xong" khi nào)

- TTS sample ra WAV; factory scripts compile OK; ffmpeg OK; SFX mp3
  và bgm đã chép đủ (nếu render cần).
- 5 skill đã đọc; Sheet đủ 13 tab (hoặc Sheet cũ tìm thấy theo tên);
  thư mục Drive tìm thấy theo tên.
- Dựng 1 video test bằng đúng pipeline (`PIPELINE.md`) → preflight
  ĐẠT, karaoke lines > 0 ở part không template, MP4 720x1280.
- Chỉ khi tất cả pass mới nhận việc thật. Fail ở đâu dừng ở đó.
