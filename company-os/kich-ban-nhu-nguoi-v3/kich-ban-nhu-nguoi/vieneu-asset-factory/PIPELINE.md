# VieNeu Asset Factory — Hợp đồng pipeline

## Vai trò
- **Agent Muse (chat)**: làm toàn bộ bước AI-text: đọc tin tức → viết kịch bản → chia
  phân cảnh → chia voice part + dàn B-roll (đọc 9 skill trong `skills/` + catalog 34
  template trong `templates/`) → sinh prompt ảnh. Ghi kết quả ra file JSON.
- **App (artifact)**: dashboard + chạy các bước nặng qua privileged actions
  (TTS batch, tạo ảnh song song, đóng gói ZIP). Đọc/ghi cùng thư mục project.

## Cây thư mục project
```
~/workspace/vieneu-media-company/vieneu-asset-factory/projects/<project_id>/
├── input.json          # {name, topic|url, mode: idea|url|paste, aspectRatio, lang, density, created_at}
├── script.json         # {topic, content, sentences[]}
├── broll-plan.json     # (agent ghi) scenes[] + parts[] + broll{templateId,inputs,sfx,...} + prompt ảnh
├── tts.json            # (tts_batch.py ghi) parts/scenes + audio_file + duration/startSec/endSec
├── build/              # cây thư mục chuẩn VieNeu (project.json, timeline.json, ...)
│   ├── audio/voice/parts/*.wav , audio/voice/voice_seg_*.wav
│   ├── audio/sfx/*.mp3 (copy từ factory/sfx)
│   ├── media/images/seg_<order>_<rand6>.jpg
│   ├── media/broll/broll_seg_<order>_part_<p>_<rand6>.jpg
│   ├── subtitles/synced_cues.srt , sentences.srt
│   ├── googleFlow/config.json
│   └── README_HUONG_DAN.txt
└── export/<project_id>.zip   # chứa thư mục <project_id>/ ở root
```

## Quy tắc đặt tên file (single source of truth: `bin/filename.py`)
- Ảnh cảnh:    `seg_<order>_<rand6>.jpg`                    (rand6 = md5("pid|img|order"))
- Ảnh b-roll:  `broll_seg_<order>_part_<partIdx>_<rand6>.jpg` (rand6 = md5("pid|broll|order|partIdx"))
- WAV segment: `voice_seg_<order>_<rand6>.wav`               (rand6 = md5("pid|seg|order"))
- WAV part:    `parts/part_<order>_<partIdx>_<rand6>.wav`    (rand6 = md5("pid|part|order|partIdx"))
- App KHÔNG tự đặt tên — luôn gọi `python3 bin/filename.py <pid> <kind> ...`

## Scripts
| Script | Chạy bằng | Vào / ra |
|---|---|---|
| `bin/tts_batch.py <pid>` | `TTS venv` (máy gốc: `vieneu-tts/.venv`, bản clone: `vieneu-tts/.venv` — xem `_tts_dir()` trong `tts_batch.py`) | broll-plan.json → build/audio/voice/** + tts.json. Multi-voice: part có thể ghi đè `"voice"` (vd quote-card đọc giọng khác) |
| `bin/preflight.py <pid>` | `python3` | checklist trước xuất: audio/ảnh/karaoke/template inputs/BGM; chặn cả khi SFX đã chọn nhưng file mp3 không tồn tại trong thư mục sfx (lựa chọn A26, 05/11/2026); luật 12/11/2026: cảnh mọi part đã có file riêng không cần ảnh cảnh chung, ảnh cảnh chung và s1p1 không được là nền trung tính; ảnh scene và ảnh b-roll phải giải mã được hết bằng PIL (lựa chọn B10, 05/11/2026 — file cắt dở vẫn >0 byte cũng chặn) |
| `bin/extract_claims.py <pid>` | `python3` | trích số liệu/ngày tháng/tên riêng để agent kiểm chứng trước TTS |
| `bin/thumbnail.py <pid> ["Tiêu đề"]` | `python3` | 3 mẫu thumbnail YouTube 1280x720 vào export/ |
| `bin/normalize_chunks.py <pid>` | `TTS venv` (như trên) | broll-plan.json → build/norm_chunks.json (chuẩn hoá ĐÚNG NHƯ engine đọc: normalize_to_chunks_v3_with_gaps, max_chars=140 + cặp câu gốc↔chuẩn hoá) |
| `bin/script_lint.py <kịch bản> --facts <dữ kiện>` | python3 (chỉ thư viện chuẩn) | kịch bản + dữ kiện đã kiểm chứng → danh sách LỖI/CẢNH BÁO (mẫu cấm, nhịp câu, số lệch dữ kiện). Chạy TRƯỚC `tts_batch.py` (skill media-video-production, bước 3b). Luật viết: `skills/SCRIPT_DOCTRINE.md`. |
| `bin/karaoke.py <pid>` | `factory venv` (xem BOOTSTRAP §3; có underthesea+numpy) | tts.json + norm_chunks.json + WAV parts → karaoke.json/ass + sent_cues.json. NGUYÊN TẮC: chữ HIỂN THỊ giữ đúng kịch bản gốc ("1991", "GDP"); timing align từng chữ gốc→span chữ chuẩn hoá (VAD), chia dòng ≤5 từ không cắt từ ghép, {\kf} #FBBF24 |
| `bin/render_template.py` | `factory venv` (xem BOOTSTRAP §3; có weasyprint+numpy) | CLI: `<template_id> <inputs.json> <W> <H> <out.png>` → render HTML/CSS template (điền inputs, bỏ box-shadow) thành RGBA: WeasyPrint render 2 lần trên nền trắng/đen → matting tách alpha thật (giữ nền bán trong suốt của card) → crop theo alpha |
| `bin/select_bgm.py <pid> [--mood M]` | `python3` | chọn BGM từ bgm/bgm_catalog.json (24 track Kevin MacLeod CC-BY 4.0, 8 mood: news/calm/dramatic/funny/inspirational/suspense/sad/upbeat) theo mood hoặc tự đoán từ topic → ghi vào broll-plan.json |
| `bin/render_draft.py <pid>` | python3 (gọi venv qua subprocess cho template) | MP4 nháp: mỗi part = clip ảnh b-roll/scene + **motion tuyệt đối + smoothstep** (zoom tối đa 1,05, seed theo project, không lặp liên tiếp) + **composite chữ B-roll template** (đúng thiết kế HTML/CSS, nền trong suốt) → nối clip bằng **xfade fade 0,5s cho mọi chuyển cảnh** (hardcode fade; clip kéo dài +0,5s để overlap nên tổng thời lượng khớp audio) → + WAV giọng đọc + mix SFX (broll.sfx {id,offsetSec,volume} tại part.startSec+offset, adelay+amix) + **BGM loop với ducking** (sidechaincompress: nhạc tự hạ khi có giọng nói, volume nền 0.12, fade-out 2s) + burn karaoke.ass. Thiếu ảnh thì in RENDER-ERROR và dừng trước khi chạy ffmpeg, không render clip nền đen, không DRAFT-OK (lựa chọn A26, 05/11/2026). SFX đã chọn nhưng file mp3 không tồn tại cũng in RENDER-ERROR và dừng như BGM (lựa chọn B8, 05/11/2026) |
| `bin/assemble_project.py <pid>` | python3 | tts.json + build/media/** → build/{project.json,timeline.json,...} + export/<pid>.zip (ZIP chứa toàn bộ build/ trừ `silence_*`, `_thumb_*` và `render_page.html`, cộng `broll-plan.json`, `abbr_dict.json` nếu có, và file BGM thật vào `audio/bgm/` nếu plan chọn BGM — xem mục "Hằng số pipeline đã chốt") |
| `bin/validate_project.py <pid> [--zip]` | python3 | kiểm tra tương thích schema 2.0, exit 0 = đạt |
| `bin/filename.py` | python3 | đặt tên file chuẩn |
| `bin/gen_images.py jobs.json` | `factory venv` | đọc file jobs.json (mỗi job: ảnh AI `{prompt, out, orientation}` hoặc card `{card_pid, card_order, out}`) và tạo ảnh cho các job media (bỏ qua job đã có file out, trừ job khai `force: true`). Job card render xong thì gen_images.py ghi cờ `isMossGrid: true` vào scene đó trong plan (lựa chọn A21, 05/11/2026) — cảnh có cờ là nền rêu giữ chỗ, không phải ảnh thật. File out đã có chỉ được bỏ qua khi giải mã được hết (lựa chọn A23, 05/11/2026) — file hỏng/không mở được thì tạo lại. KHÔNG nhận `<pid>` — cách gọi cũ `gen_images.py <pid>` trong bảng này trước đây là sai (sửa Giai đoạn 4, 05/11/2026; cách gọi đúng xem docstring đầu `bin/gen_images.py`) | buildGenImageJobs không tạo job cho cảnh đã có ảnh thật (lựa chọn A22, 05/11/2026) — muốn thay ảnh thật thì xóa ảnh trước bằng action clearSceneImage. |
| `bin/render_scene_card.py <pid> <order> <out.jpg>` | `factory venv` | render nền xanh rêu kẻ ô, không chữ, cho một scene (được gen_images gọi với job card; sửa 05/11/2026, thay card chữ cũ). Cách gọi cũ `render_scene_card.py <pid>` thiếu `<order>` và `<out.jpg>` là sai (sửa Giai đoạn 4, 05/11/2026). Ngoại lệ cardImage: đường dẫn tương đối chỉ tra trong `build/media/images` của project; không thấy thì in `CARDIMAGE-MISSING` rồi rơi về nền rêu, không bao giờ nhặt file theo CWD (lựa chọn A29, 05/11/2026) |
| `bin/build_render_page.py <pid>` | python3 | tạo trang HTML seekable (nhúng lib/render-engine.js + data project) để render frame capture |
| `bin/square_crop.py <in> <out.jpg>` | python3 | cắt ảnh ngang/vuông thành vuông lấy giữa khung (không phải focus chủ thể) |
| `bin/render_template_anim.py` | `factory venv` | đường render Chrome đã NGHỈ HƯU, không dùng cho render mới |

## Hằng số pipeline đã chốt (Giai đoạn 4, 05/11/2026)

Một mặc định, một nguồn cho mỗi hằng số dưới đây; file nào trước đây
lệch đã sửa về giá trị này (xem docstring đầu mỗi file). Khi cần đổi
một hằng số, đổi ở mọi file liệt kê, không đổi lẻ một chỗ.

- **aspectRatio mặc định: `9:16` (video dọc)** khi `input.json` thiếu
  field. Khung: 9:16 → 720x1280, còn lại → 1280x720. Áp dụng ở
  `render_draft.py`, `karaoke.py`, `build_render_page.py`,
  `assemble_project.py`, `render_scene_card.py` (file cuối đã mặc định
  9:16 từ trước; 4 file đầu trước đây mặc định 16:9).
- **Vị trí phụ đề: MarginV = 20% chiều cao khi dọc, 7% khi ngang** cho
  cả MP4 (`karaoke.py` ghi vào `.ass`, `render_draft.py` kiểm tra lại
  trước khi burn) và preview (`lib/render-engine.js`: `subsDiv`
  `bottom: 20%` khi dọc, `7%` khi ngang — trước đây preview ghim 7% cả
  hai chiều nên video dọc lệch MP4). Font phụ đề: `40 * (min(W,H)/480)`
  ở cả hai đường, font duy nhất Anton. Vị trí chữ template: cùng công
  thức 20%/7% (trừ full-stage phủ kín khung, `preview-banner` /
  `keyword-block` sát đáy, `clip-caption` sát đáy 3%).
- **Motion / chuyển cảnh:** 6 preset cùng thứ tự ở mọi nơi —
  `zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down`
  (`render_draft.py` MOTIONS, `build_render_page.py` MOTIONS,
  `render-engine.js` MOTION_ORDER); chuỗi motion của từng part do
  `random.Random(f"motion-{pid}")` duyệt theo thứ tự render, tránh lặp
  liền trước, host gắn vào `part.motion` (thiếu thì engine fallback
  hash + cảnh báo). Zoom tối đa 1.05, chuyển cảnh fade 0.5s.
- **Preview chỉ là xấp xỉ (KHÔNG ghi "khớp render" cho các điểm này):**
  pan blur-fill — preview pan ngang 12% ≈ 121px một chiều so với render
  240px, pan dọc 2% ≈ 20px so với render ≈ 46px (đo đợt D3, 01/11/2026;
  lề phủ của fg preview không đủ để khớp nếu không phóng to fg);
  easing — CSS `cubic-bezier(0.42,0,0.58,1)` chỉ xấp xỉ smoothstep
  `s=t*t*(3-2*t)` của ffmpeg; độ mờ nền — CSS `blur(30px) + scale(1.1)`
  so với ffmpeg `gblur sigma=25`; co chữ template — preview vẽ HTML
  đúng cỡ stage, MP4 vẽ PNG rồi co 92%W/80%H (trừ full-stage). Muốn khớp
  hẳn phải đo lại bằng mắt trong tab Preview trước khi đổi, không đổi
  mò theo số.
- **Accent:** một bảng màu duy nhất — `render_template.py` ACCENT_HEX
  (`gold #FBBF24, red #EF4444, cyan #22D3EE, green #22C55E, pink
  #F472B6, purple #A78BFA, orange #FB923C`), `render-engine.js`
  `_accentMap` khớp từng giá trị. Thứ tự ưu tiên MP4: `inputs.accent` →
  `accent.default` trong meta → vàng. Preview đạt cùng thứ tự khi host
  gắn `part.tplAccent = accent.default` (build_render_page.py đã gắn;
  host khác phải gắn tương tự, nếu không preview rơi về vàng trong khi
  MP4 dùng accent của meta).
- **Chunk TTS/karaoke 140 ký tự:** `normalize_chunks.py` MAX_CHARS=140
  là nơi duy nhất giữ giới hạn này, để gương theo infer() của engine
  Vieneu v3 Nano; mã nguồn engine không nằm trong repo này nên chưa
  kiểm chứng được giới hạn hiện tại của engine. Timing karaoke KHÔNG
  phụ thuộc biên chunk (karaoke dùng cặp câu gốc↔chuẩn hoá + VAD trên
  WAV thật), nên engine chunk khác biên không làm lệch timing karaoke;
  chỉ danh sách `chunks` trong `norm_chunks.json` là không còn gương
  đúng chunk synthesis. `tts_batch.py` không tự chunk — đưa nguyên
  voiceText của part cho engine.
- **Pause:** per-part. `tts_batch.py` đã per-part từ trước
  (`part.pauseAfterMs` → plan → 180ms); `assemble_project.py` trước đây
  dùng pause chung của plan cho mọi part trong timeline — đã sửa về
  per-part (Giai đoạn 4), vì vậy `timeline.json` nay khớp duration thật
  trong `tts.json`.
- **ZIP của assemble:** chứa toàn bộ `build/` trừ file `silence_*`, `_thumb_*` và `render_page.html` (lựa chọn B31, 06/11/2026),
  cộng `broll-plan.json` ở root `<pid>/`, `abbr_dict.json` nếu có, và
  file BGM thật vào `<pid>/audio/bgm/` nếu plan chọn BGM và file tồn
  tại trong `factory/bgm/` (thiếu file BGM đã chọn thì chặn: render in `RENDER-ERROR` và dừng trước khi chạy ffmpeg, assemble in `ASSEMBLE-ERROR`, xóa ZIP tạm và dừng; plan không chọn BGM thì vẫn render bình thường — sửa 05/11/2026, lựa chọn A11/13B).
  Lưu ý: `timeline.json`/`project.json` hiện không trỏ tới
  `audio/bgm/` — file BGM trong ZIP là bản kèm theo để máy khác có nhạc
  mà không cần `factory/bgm/`; Studio muốn dùng phải tự nối theo
  `plan.bgm` trong `broll-plan.json` kèm theo.
- **Chặn (exit 1) vs cảnh báo (exit 0) — nhất quán hai công cụ:**
  cả `preflight.py` và `validate_project.py` đều exit 1 khi và chỉ khi
  có lỗi chặn, cảnh báo không tính vào exit code. `preflight.py` chỉ
  dùng cho project factory, TRƯỚC render/assemble (chặn: xem docstring
  đầu file). `validate_project.py` chỉ hợp lệ SAU assemble, cho gói
  Studio export (chặn: xem docstring đầu file); dùng validate cho
  project factory chưa assemble sẽ FAIL sai "thiếu project.json".

## Privileged actions của app (gọi script trên)
- `createProject(input)` → tạo thư mục + input.json, trả project_id
  (`project_<YYYYMMDDHHMMSS>_<6 số ngẫu nhiên>`)
- `saveScript(pid, scriptJson)` / `savePlan(pid, planJson)` → ghi file (agent trong chat
  cũng có thể ghi trực tiếp, app đọc lại)
- `runTTS(pid, force?)` → chạy tts_batch.py (có thể mất vài phút, trả về khi xong).
  tts_batch bỏ qua WAV đã có, trừ `--force` hoặc từ điển mới hơn WAV, nên
  chạy lại sau timeout chỉ làm tiếp phần chưa xong.
- `generateImages(pid)` → hai đường, xem mục "Tạo ảnh" dưới đây. Job đã có
  file out hợp lệ thì `gen_images.py` bỏ qua (trừ job khai `force: true`),
  nên chạy lại sau timeout chỉ làm tiếp phần chưa xong.
- `runNormalize(pid)` → chạy normalize_chunks.py bằng TTS venv (chuẩn hoá ĐÚNG NHƯ
  engine đọc; lần đầu để rà abbr_dict rồi mới chạy TTS — xem luật abbr trong skill Sản xuất)
- `runKaraoke(pid)` → chạy karaoke.py
- `runPreflight(pid)` → chạy preflight.py. Preflight CHẶN (exit 1) khi scene
  thiếu ảnh — [sửa 12/11/2026] chỉ với cảnh còn part chưa có ảnh/video riêng; cảnh mà mọi part đã có file riêng không cần ảnh cảnh chung; ảnh cảnh chung trùng file `neutral-bg/` hoặc part đầu tiên của video dùng nền trung tính cũng CHẶN (trước lựa chọn A26, 05/11/2026 render sẽ ra clip nền đen cho scene đó — nay render thiếu ảnh cũng tự dừng với RENDER-ERROR, không còn ra clip nền đen — đây là LỖI, không phải
  cảnh báo). Preflight CHẶN (exit 1) cả khi SFX đã chọn nhưng file mp3 không tồn tại trong thư mục sfx (lựa chọn A26, 05/11/2026). Preflight CHẶN (exit 1) cả khi scene thiếu nguồn media (mediaSource.source trống/thiếu) hoặc thiếu nhật ký tìm ảnh (media-log.json không có, scene không có mục nhật ký, keywordsTried trống) — cửa chặn ảnh thật, lệnh CEO 05/11/2026 (lựa chọn A20); scene chỉ có nền xanh rêu kẻ ô cũng chặn ở đây. Thời lượng không còn mức chặn: chỉ cảnh báo khi tổng <120s hoặc
  >180s (lệnh CEO 29/10/2026: Production tự quyết độ dài, không cần xin ngoại
  lệ; ghi thời lượng thật vào bàn giao).
- `startRenderDraft(pid)` + `getRenderStatus(pid)` → render draft chạy nền,
  poll trạng thái thay vì chờ đồng bộ. Đây là đường đã sửa timeout 30s
  cho render; `runTTS`/`generateImages` vẫn là action đồng bộ nên vẫn
  có thể timeout ở video dài — xem "Timeout 30s" trong
  `docs/REPO_VS_APP.md`.
- `selectBgm(pid, mood?)` / `listBgm()` → chạy select_bgm.py / đọc
  bgm_catalog.json (24 track, 8 mood) — PHẢI chạy trước startRenderDraft vì
  render đọc plan.bgm để mix nhạc
- `renderTemplate(templateId, inputs)` → chạy render_template.py, trả PNG
  (tiện ích; render_draft cũng gọi qua subprocess)
- `listTemplates()` → đọc catalog templates/ trong repo (34 template;
  `_themes.json` là file theme chung, không phải template)
- `exportProject(pid)` → chạy assemble + validate, trả đường dẫn zip
- `listProjects()` / `getProject(pid)` / `deleteProject(pid)`
- App KHÔNG chứa pipeline riêng: mọi action trên đều gọi script trong
  `bin/` của repo này. Sửa pipeline thì sửa trong repo, xem
  `docs/REPO_VS_APP.md`.

## Tạo ảnh
- Ảnh AI: lệnh `/opt/hatch/bin/media-generation --orientation landscape "<prompt>"` (16:9),
  `--orientation portrait` (9:16). Output: file ảnh → app copy vào đúng tên.
- Ảnh cảnh card chữ: scene không có sceneImagePrompt/mediaPrompt (như
  topic004, hormuz002) KHÔNG đi qua media-generation. App phải xây job
  card cho `bin/gen_images.py`
  (`{"card_pid": "<pid>", "card_order": <order>, "out": "...jpg"}`) hoặc gọi
  trực tiếp `bin/render_scene_card.py <pid> <order> <out>`. Trước đây app
  chỉ xây job AI nên plan card chữ trả jobCount 0 — đó là thiếu đường
  card, không phải plan thiếu ảnh.
- Tuyệt đối không dùng blob:/data: URL trong JSON — chỉ file thật trong build/.
- Tuyệt đối không tự đặt tên file ngẫu nhiên: tên file phải lấy từ
  `bin/filename.py`, nếu không render ra MP4 nền đen (xem "Bài học đặt
  tên ảnh" dưới đây).

## Tương thích local (validate_project.py kiểm tra)
- JSON UTF-8, ensure_ascii=False (không \uXXXX); URL `/projects/<pid>/...`
- timeline.json version 2.0, key camelCase chuẩn, không chứa key bị strip
- voiceText nối lại phải khớp 100% scene text (lossless)
- templateId active, đủ inputs bắt buộc, đúng maxLength, sfx id tồn tại

## Từ điển viết tắt (abbr_dict) — lớp sau sea-g2p, độc lập với vieneu-tts
- Xem `ABBR_DICT.md` và `bin/abbr_expand.py`. Agent rà soát norm_chunks để tìm
  viết tắt sea-g2p đọc sai, ghi cách đọc đúng vào `<project>/abbr_dict.json`.
- `normalize_chunks.py` và `tts_batch.py` cùng áp từ điển trước khi gọi engine
  (speech_text), karaoke không cần sửa (pairs giữ câu gốc để hiển thị).
- Sau khi tạo/sửa từ điển: chạy lại normalize → tts_batch (part có từ điển mới
  hơn WAV sẽ đọc lại, dùng `--force` cho chắc) → karaoke → render.
- Không sửa gì trong `vieneu-tts/`; app `runTTS` gọi tts_batch nên tự áp
  từ điển khi project có file này.

## Sửa lỗi render template/video (2026-10-25, đối chiếu preview↔video 2 project)
- `bin/render_template.py`: regex strip shadow cũ `[^;]+` ăn qua dấu `}` khi
  shadow là khai báo cuối rule → nuốt rule kế tiếp (16/29 template từng bị:
  stat-counter mất unit + value trắng thay vì vàng, date-stamp text đen,
  versus-split thành đĩa vàng + badge VS vô hình...). Đã sửa thành
  `[^;}]+;?`. Audit: so output regex cũ/mới trên toàn bộ templates/.
- `bin/render_template.py`: pdftoppm `-r 72` → `-r 96` (WeasyPrint ghi 1 CSS px
  = 1pt nên -r 72 cho PNG 0.75x → overlay video nhỏ hơn preview ~28%).
  Nay 1 CSS px = 1 PNG px, overlay khớp kích thước preview.
- `bin/render_template_anim.py`: không còn animation hữu hạn (label/sublabel
  rỗng → fade-in không chạy) thì chụp 1 frame tĩnh đã settle thay vì
  `ANIM-FAIL` rơi về WeasyPrint (đó là nguyên nhân typewriter bị cắt chữ
  bên trái ở bản dọc). Template full-stage (union bbox phủ kín khung) giữ
  nguyên kích thước, không co 92%/80% (meta.json thêm `"fullstage"`).
- `bin/render_draft.py`: overlay tĩnh full-stage (PNG đúng tỉ lệ + ≥90%
  khung) phủ kín khung thay vì co lại; trước bước mux, tự kiểm tra
  karaoke.ass: MarginV sai tỉ lệ hiện tại hoặc .ass cũ hơn input/tts.json
  → chạy lại karaoke.py (in `KARAOKE-REGEN`), lỗi thì giữ .ass cũ + cảnh báo.
- `templates/stat-counter/style.css`: hàng value+unit đổi từ flex sang
  `display:block; white-space:nowrap` (WeasyPrint không nới card theo
  flex row → unit wrap 2 dòng chồng lên label); trình duyệt render giống
  hệt (căn giữa, baseline, một dòng).
- Quy tắc chung rút ra: preview (Chrome) là ground truth; mọi đường render
  video (WeasyPrint tĩnh / Chrome anim) phải cho ra cùng bố cục, màu,
  kích thước với preview — kiểm chứng bằng cách chụp cả hai rồi đối chiếu.
- Điều chỉnh template theo feedback user (2026-10-25): typewriter-reveal
  padding ngang 14.2vmin → 22vmin (đo thực tế chữ trái nhất từ 14.3% →
  22.1% khung); headline-banner nền rgba(8,10,16,.9) → .65 (mờ, ảnh nền
  xuyên qua nhẹ, chữ vẫn đọc rõ — CSS dùng chung nên preview và video
  cùng đổi); versus-split 9:16 xếp trên/dưới thay vì trái/phải — CSS đã
  có sẵn @media portrait nhưng WeasyPrint không đánh giá @media
  orientation nên video 9:16 vẫn xếp ngang: đã thêm class portrait vào
  <body> của host-page render tĩnh + anim (theo W,H) và block
  `body.portrait ...` song song với @media (16:9 không đổi).

## Bài học đặt tên ảnh (2026-10-25, 4 video trend)
- Mọi file ảnh phải dùng đúng tên suy ra từ `bin/filename.py` (`rand6(pid, 'img'|'broll', ...)` md5) — render_draft, preflight, thumbnail, preview (build_render_page.py `part_image`, handlers-preview.ts `partImagePath`) đều tra cứu theo tên này, KHÔNG glob theo hậu tố ngẫu nhiên (lựa chọn A24, 05/11/2026).
- Lỗi đã gặp: img_jobs tạo bằng `random.seed` → render ra MP4 nền đen hoàn toàn (không ảnh nào khớp tên), preflight cảnh báo "Scene chưa có ảnh", thumbnail báo "không có ảnh nền". Sửa bằng cách đổi tên file về đúng tên chuẩn rồi render lại; từ đó img_jobs của video 2–4 được viết lại theo `filename.rand6` trước khi chạy gen_images.
