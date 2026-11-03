# VieNeu Asset Factory — mã nguồn lõi

Mã nguồn lõi của hệ thống sản xuất video dọc VieNeu Asset Factory trên Muse:
kịch bản → chia scene → B-roll → ảnh AI → TTS → video nháp MP4 → project ZIP
tương thích schema 2.0 với VieNeu Studio local.

## Gồm có gì

- `bin/` — script pipeline: `normalize_chunks`, `tts_batch`, `karaoke`,
  `render_draft`, `render_template`, `render_template_anim`, `assemble_project`,
  `validate_project`, `preflight`, `thumbnail`, `select_bgm`, `extract_claims`,
  `abbr_expand`, `filename` (chuẩn tên file media), `gen_images` (ảnh AI +
  ảnh card chữ qua `render_scene_card`, job đã xong thì bỏ qua để chạy
  lại sau timeout không làm lại từ đầu).
- `templates/` — catalog B-roll template (meta.json + HTML/CSS), gồm
  `clip-caption`, `comment-frame`, `story-title` và các template tin tức/thể thao.
- `skills/` — skill b-roll: `broll-director` và các skill hỗ trợ, kèm
  `EDITORIAL_DOCTRINE.md`.
- `docs/` — tài liệu bổ sung: `UX_SPEC.md` (đặc tả giao diện app),
  `SFX_MANIFEST.md`, `BGM_MANIFEST.md`, `TEXT_DENSITY_RULES.md` (quy tắc mật độ
  chữ cho B-roll — agent dàn cảnh PHẢI đọc cùng `EDITORIAL_DOCTRINE.md` và
  `broll-director` trước khi viết `broll-plan.json`, vì Doctrine gốc không khóa
  cứng tỷ lệ chữ nên không có tài liệu này agent dễ gắn chữ cho mọi part),
  `REPO_VS_APP.md` (audit 27/10/2026: repo vs app khác nhau ở đâu, đã sửa
  gì ở repo, giới hạn nào vẫn thuộc về app).
- `lib/` — thư viện phụ đề tiếng Việt (`vi_sub`) và render engine JS.
- `prompts/` — prompt dùng cho các bước AI.
- `PIPELINE.md`, `ABBR_DICT.md` — tài liệu pipeline và quy tắc đọc viết tắt.

## KHÔNG có trong repo này

- Giao diện app trên Muse (artifact web_fullstack): không nằm trong repo,
  sang Muse khác phải build lại app rồi nối worker vào mã này.
- `.venv/`, `projects/` (video/ảnh/audio đã sản xuất): nặng hoặc nhị phân, sao lưu riêng.
  (`bgm/` nhạc nền và `sfx/` hiệu ứng KHÔNG đi kèm repo này — lấy theo BOOTSTRAP §7
  của monorepo: 8 file SFX từ thư mục Drive 'sfx', thư mục bgm/ phải tải lên Drive trước.)
- VieNeu TTS (thư mục TTS trong monorepo là `vieneu-tts`, máy gốc dùng `vieneu-tts-api`,
  gồm `tts_cli.py` và model cache): thành phần
  riêng, cần có sẵn trên máy chạy pipeline; `tts_batch.py` và
  `normalize_chunks.py` phải chạy bằng venv của TTS đó.

## Chạy trên Muse khác

1. Clone repo này (private) về máy Muse mới.
2. Tạo venv, cài đặt Python cần thiết, có sẵn `ffmpeg`.
3. Chuẩn bị VieNeu TTS và thư viện nhạc nền (Kevin MacLeod, CC-BY 4.0) riêng.
4. Build lại app giao diện trên Muse mới, worker gọi script trong `bin/`.
