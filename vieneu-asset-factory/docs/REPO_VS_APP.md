# Khác nhau giữa repo và app tại local — audit 27/10/2026

Audit này trả lời câu hỏi "repo và app khác nhau ở đâu", rồi ghi lại
những gì đã được đưa về repo trong đợt cập nhật 27/10/2026.
"Repo" ở đây là thư mục này (`~/workspace/vieneu-asset-factory/`,
symlink `~/workspace/asset-factory/`). "App" là artifact web_fullstack
`vieneu-asset-factory` trên Muse — giao diện + privileged actions,
KHÔNG phải một bản sao code pipeline nằm riêng trong repo.

## Kết luận ngắn

- **Repo là source of truth cho pipeline.** Mọi logic thật (TTS, karaoke,
  render, template, BGM, validate) đều nằm trong `bin/` + `templates/`
  của repo. App không chứa pipeline riêng.
- **App là lớp vỏ UI + action.** App đọc/ghi cùng thư mục
  `projects/<pid>/`, gọi script trong `bin/` qua privileged actions,
  và giữ trạng thái project (hasScript, hasPlan, hasTts, hasPreview…).
  Vì vậy app thấy được cả project tạo bằng script tay (topic004,
  hormuz001/002, anmang001) lẫn project tạo qua UI
  (`project_<timestamp>_<rand6>`).
- **Các sửa QA 26-27/10 đã nằm trong repo, không chỉ nằm trong app.**
  Đã kiểm chứng bằng diff với bản sao lưu trước khi đồng bộ upstream
  27/10 (`company-os/repo-sync-backup-20261027/`): chỉ có
  `bin/render_draft.py` khác sau đợt đồng bộ, và đó chính là sửa
  motion smoothstep 4x ngày 27/10. Các sửa còn lại đã có trong repo
  trước đợt audit này.

## Bảng khác nhau, đã kiểm chứng

| Hạng mục | Repo (bin/templates) | App (artifact) | Trạng thái sau audit |
|---|---|---|---|
| Motion | `render_draft.py`: smoothstep `s=t*t*(3-2*t)` trên `on/frames`, ảnh nguồn 4x, zoom tối đa 1.05, lề 96px/140px | Dùng đúng render_draft của repo qua `startRenderDraft` + `getRenderStatus` | Đã khớp. App không có motion riêng. |
| Footer nguồn | `templates/source-footer-safe`: tối đa 3 dòng, mỗi dòng ≤528px ở khung 720, lề phải ≥96px; `render_scene_card.py` dùng làm mặc định và cảnh báo khi nguồn cần >3 dòng | `listTemplates` thấy template này, `renderTemplate` trả RENDER-OK | Đã khớp. |
| Checklist | CSS chữ trắng `#fff` cho cả list và `li`; `render_template.py` chuyển items thành `<li class="broll-item">`, render tĩnh ép `opacity:1` | Dùng đúng template + render_template của repo | Đã khớp. |
| Section-title | Lớp phủ 35-45% (meta v1.2.0), không phủ tối 92-98% như cũ | Dùng đúng template của repo | Đã khớp. |
| Âm thanh | `render_draft.py`: SFX nặng cap 0.4, limiter cuối `alimiter=0.89` | Dùng đúng render_draft của repo | Đã khớp. |
| Card kết luận | `render_scene_card.py`: `cardImage` làm nền, phủ tối 35% | Dùng đúng script của repo | Đã khớp. |
| Video b-roll | `render_draft.py` nhận `.mp4` trong `media/broll/`, tắt tiếng, loop/cắt theo part; `assemble_project.py` ưu tiên URL `.mp4` | App chưa có action tạo video b-roll riêng; video b-roll phải tạo bằng media-generation CLI rồi đặt đúng tên file, repo mới render được | Khác nhau còn lại, ghi rõ ở dưới. |
| BGM/SFX | `bin/select_bgm.py`, `bgm/bgm_catalog.json` (24 track, 8 mood), `bgm/` + `sfx/` trong repo | `listBgm`/`selectBgm` trả đúng 24 track, 8 mood | Đã khớp (app hoàn thiện 26/10). |
| Mật độ chữ | `docs/TEXT_DENSITY_RULES.md` (upstream c9222959) + `bin/karaoke.py` ẩn phụ đề ở part có template chữ thật, trừ clip-caption/story-title | App không tự chọn template theo beat; agent dàn cảnh phải đọc tài liệu này trước khi viết plan | Khác nhau về trách nhiệm, không phải về code: app không thay agent. |
| Thời lượng bàn giao | `bin/preflight.py` từ 27/10: cảnh báo khi tổng <180s (chuẩn CEO 180-300s), không thành lỗi để clip test vẫn đạt | App không tự chặn video ngắn; Production/QA phải đọc cảnh báo preflight | Đã đưa vào repo, xem dưới. |

## Hai khác nhau thật sự, đã sửa ở repo trong đợt này

### 1. generateImages: app từng trả jobCount 0 cho plan card chữ

Nguyên nhân: `bin/gen_images.py` cũ chỉ biết job AI
(`prompt` → media-generation CLI). Các project thật topic004,
hormuz002 dùng ảnh cảnh card chữ, không có `sceneImagePrompt`/
`mediaPrompt`, nên app xây job AI được 0 job và trả jobCount 0.
Đó không phải plan thiếu ảnh, mà là gen_images chưa biết đường card.

Sửa ở repo (27/10/2026, không phá đường AI cũ):
- `bin/gen_images.py` nhận thêm job card:
  `{"card_pid": "<pid>", "card_order": <order>, "out": "...jpg"}`
  → chạy `bin/render_scene_card.py` bằng factory venv.
- App muốn tạo đủ ảnh cảnh phải xây cả hai loại job: job AI cho
  scene có prompt, job card cho scene không có prompt. Hoặc gọi
  `render_scene_card.py` trực tiếp cho scene không prompt — docstring
  của script đó đã ghi đúng hướng này.
- Tên file out vẫn phải lấy từ `bin/filename.py`. Tên sai là
  render ra MP4 nền đen, preflight cảnh báo "Scene chưa có ảnh".

### 2. Timeout 30s của action app vs script chạy dài

App action có ngân sách wall-clock 30s. Video dài (TTS, tạo ảnh,
render 68s, video 3-5 phút) vượt ngân sách này: lần chạy đầu timeout
dù tiến trình nền vẫn hoàn thành, lần chạy thứ hai mới thành công.
Render đã có đường nền (`startRenderDraft` + `getRenderStatus`),
nhưng `runTTS`/`generateImages` vẫn là action đồng bộ.

Sửa ở repo (27/10/2026, không đổi API app):
- `bin/gen_images.py`: job nào đã có file out >0 byte thì bỏ qua
  (`IMG-SKIP`), trừ khi job khai `"force": true`. Lần chạy thứ hai
  sau timeout chỉ làm tiếp phần chưa xong.
- `bin/tts_batch.py` đã có sẵn tính chất này từ trước: bỏ qua WAV
  đã có, trừ `--force` hoặc từ điển viết tắt mới hơn WAV.
- Hướng dẫn cho Production: khi action app timeout, KHÔNG kết luận
  thất bại, chạy lại cùng action và đọc log — phần đã xong sẽ được
  bỏ qua, phần chưa xong sẽ chạy tiếp. Chỉ khi chạy lại vẫn lỗi
  thì mới coi là lỗi thật.
- Giới hạn còn lại, thuộc về app (không sửa được từ repo):
  app cần thêm action start/poll cho TTS và generateImages giống
  như đã làm cho render draft, nếu muốn hết timeout hẳn. Cho tới
  lúc đó, đường chạy script trực tiếp vẫn là ngoại lệ được phép
  khi app không làm được việc đó, và phải ghi bài học về skill/app.

## Những gì KHÔNG khác nhau (đừng sửa lại vô ích)

- Template catalog: app `listTemplates` đọc đúng 33 template trong
  repo (số 34 trước đây đếm nhầm cả file `_themes.json`; đã sửa
  27/10/2026), và meta của cả 33 template khớp repo 100% (xem kiểm
  chứng listTemplates vs meta.json ngày 27/10/2026) trong
  repo, kể cả `source-footer-safe` và `checklist` v1.1.0,
  `section-title` v1.2.0. Sửa template thì sửa trong repo, app
  tự thấy.
- BGM catalog: app `listBgm` khớp repo (24 track, 8 mood, Kevin
  MacLeod CC-BY 4.0).
- Project: app `listProjects` thấy cả project script tay và project
  UI, vì cùng thư mục `projects/`. Không có hai kho project riêng.

## Những gì vẫn thuộc về app, không đưa vào repo

- Code server/UI của artifact, trạng thái action, ngân sách 30s,
  polling `getRenderStatus`. Repo không chứa code này (xem README:
  "KHÔNG có trong repo này"), nên audit này không sửa được chúng
  từ repo — chỉ sửa được repo để app dùng đúng và ghi rõ giới hạn.
- Video b-roll: repo render được video b-roll, nhưng app chưa có
  action tạo video b-roll. Tạo video b-roll vẫn làm bằng
  media-generation CLI (output video, orientation vertical), đặt
  đúng tên `broll_seg_<order>_part_<pi>_<rand6>.mp4`, rồi render
  qua app/script như bình thường.

## Quy tắc sau audit

1. Sửa pipeline thì sửa trong repo (`bin/` + `templates/`), không
   sửa riêng trong app rồi để repo cũ — lần đồng bộ sau sẽ mất sửa.
2. Sửa template thì sửa meta.json + CSS + ghi rõ lý do QA trong
   description của template, để app `listTemplates` tự mang theo
   bài học đó.
3. Thêm action app mới thì đồng thời cập nhật `PIPELINE.md` mục
   "Privileged actions của app" và tài liệu này, nếu không lần
   sau lại phải audit lại từ đầu.
4. Không push lên GitHub từ đợt này: repo local hiện không phải
   working tree git (được khôi phục bằng tải file, không phải
   clone), nên "cập nhật repo" ở đây là cập nhật file local.
   Muốn đưa lên upstream thì cần khởi tạo/clone repo riêng và
   soát diff trước khi push, không tự push.
5. Quy tắc CEO 27/10/2026 — QA sửa template thì phải đề xuất cập
   nhật repo: mọi sửa template do QA phát hiện (dù QA tự sửa hay
   QA yêu cầu Sản xuất sửa) đều phải kèm một đề xuất cập nhật repo
   trong bản đánh giá QA, ghi rõ template, file đổi, version tăng,
   lý do và bằng chứng render thử. Mục đích là tái sử dụng cho các
   tài khoản Muse khác: tài khoản khác lấy template từ repo này
   (clone sau khi push, hoặc copy thư mục `templates/`), không lấy
   từ project hay database của app. Cập nhật file repo local là
   bước bắt buộc; push lên GitHub là bước riêng, cần quyết định
   của CEO. Sửa chỉ đúng cho một video thì ghi rõ "không áp dụng
   repo", không đưa vào template chung.
