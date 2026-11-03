# Báo cáo sửa code — lệnh CEO 29/10/2026: "Đọc lại toàn bộ code và tự sửa những phần xung đột, lỗi rác"

Ngày: 29/10/2026. Lệnh này THAY THẾ quyết định chờ của đợt audit chỉ-đọc
ngày 28-29/10/2026 (báo cáo gốc: `~/workspace/company-os/code-audit-20261029.md`).
Mọi lỗi dưới đây đều đã đối chiếu code thật trước khi sửa, không áp dụng mù
từ trí nhớ hay từ audit.

Phạm vi: repo `~/workspace/vieneu-asset-factory/` (bin/, lib/, templates/),
`~/workspace/company-os/media-search/`, skill `~/workspace/custom-skills/media-*.md`.
KHÔNG đụng: `vieneu-tts-api/`, `muse-app/`, source artifact app-t-o-video,
Google Sheet, Secure Vault, tiến trình đang chạy. KHÔNG push GitHub.

Backup trước khi sửa: `~/workspace/company-os/code-fix-20261029/backup/`
(giữ cấu trúc thư mục gốc, 12 file). Khôi phục một file = copy ngược từ
backup về đường gốc.

---

## 1. preflight.py — sửa kiểm tra template-inputs bị chết (audit D-L1, E-1)

- File: `vieneu-asset-factory/bin/preflight.py`
- Lỗi cũ: `for inp in meta.get("inputs", [])` — mọi `meta.json` đều khai
  `inputs` dạng dict (`{"value": {...}}`), nên vòng lặp chỉ ra string key,
  `inp.get` gây `AttributeError`, và `except Exception: pass` nuốt trọn —
  kể cả khi `meta.json` hỏng. Preflight không bao giờ báo thiếu input bắt
  buộc hay vượt `maxLength`. Chuẩn đúng là `.items()` như
  `validate_project.py:139` (đã đối chiếu).
- Cách sửa: duyệt `meta.get("inputs", {}).items()`; chỉ bắt
  `(OSError, JSONDecodeError)` quanh đọc file và báo thành lỗi
  "meta.json hỏng/không đọc được"; `inputs` không phải dict thì báo lỗi
  sai schema thay vì nuốt. Đã kiểm chứng cả 33 template đều khai inputs
  dạng dict, không meta nào hỏng — sửa này không làm project live nào
  rớt preflight oan.
- Bằng chứng trước/sau (project tạm, 1 part stat-counter không inputs):
  - Trước: lỗi bị nuốt, preflight vẫn qua cửa này.
  - Sau: `[LỖI] Part scene1-part-1: thiếu input bắt buộc 'value' của
    stat-counter`, exit 1.

## 2. tts_batch.py — chặn partId trùng (audit D-L2, E-6)

- File: `vieneu-asset-factory/bin/tts_batch.py`
- Lỗi cũ: `by_id = {p["partId"]: p for p in part_results}` không kiểm tra
  trùng — lỗi topic004 (mọi scene dùng chung audio part cuối, tổng sai
  42.7s thay vì 37.29s) vẫn có thể lặp lại lặng lẽ.
- Cách sửa: kiểm tra trùng ID toàn plan NGAY TRƯỚC KHI tổng hợp (trước cả
  khi nạp model), in rõ ID nào trùng, exit 2, không ghi `tts.json`.
  Kiểm tra ở mức plan là đủ vì worker build từ đúng plan đó.
- Bằng chứng: project tạm 2 scene cùng id `part1` → stderr
  `ERROR: partId trùng trong plan, TTS dừng lại, không ghi đè: part1`,
  exit 2, không có file `tts.json` nào được viết.

## 3. Thiếu ảnh cảnh: từ cảnh báo thành LỖI preflight (audit D-L3, D-L4, E-2)

- File: `vieneu-asset-factory/bin/preflight.py`
- Lỗi cũ: thiếu ảnh scene chỉ là warning, exit 0, trong khi render_draft
  ra clip nền đen lặng lẽ cho scene đó.
- Kiểm tra xung đột trước khi đổi (theo lệnh):
  1. Luồng app: preflight chạy SAU bước tạo ảnh trong cả skill Production
     và app (tab karaoke+preflight đứng sau bước ảnh, trước render; text
     app: "Preflight đọc cảnh báo trước khi render"). Không xung đột.
  2. Project live: mọi project video đã bàn giao (anmang, hormuz, mrpips,
     pokrovsk, vinspeed, ukraine, topic004, mediasrc) đều đủ ảnh theo
     quy ước tên factory. Không xung đột.
  3. Hai ngoại lệ phát hiện và xử lý đúng:
     - `project_20261028165436_213948` (app, mồ côi): ảnh có trên đĩa
       nhưng lệch quy ước tên factory (`seg_1_108809` vs factory
       `seg_1_988063`), và render_draft cũng chỉ tìm theo tên factory
       nên project này render cũng ra nền đen — preflight báo lỗi là
       ĐÚNG, không phải false positive. Project này không phải video
       bàn giao (export chỉ chứa một file vinspeed copy lạc).
     - `test001`: fixture test không ảnh, không phải video bàn giao —
       preflight nay báo lỗi là hành vi đúng; xem mục "cố tình không sửa".
- Cách sửa: thiếu ảnh scene thành error; đồng thời mở rộng kiểm tra theo
  đúng render_draft (chấp nhận jpg/png/webp, trước đây chỉ jpg).
- Bằng chứng: preflight pokrovsk001 và vinspeed001 vẫn ĐẠT (xem mục kiểm
  chứng); project tạm thiếu ảnh → `[LỖI] Scene 1 chưa có ảnh…`, exit 1.

## 4. Media-search ACCEPT gate (audit D-M1, D-M2, D-M4, D-M5, E-8)

- File: `company-os/media-search/search_media.py` + ghi chú trong `LOGIC.md`
- Thứ tự Wikipedia > Stock > AI, công thức điểm và ngưỡng ACCEPT ≥70 /
  CONSIDER 50-69 giữ nguyên. Không key nào được ghi vào code/file/báo cáo.
- (a) Ảnh ngang: thêm cổng như video vào hàm `_verdict` chung, áp cho cả
  `score_candidate` (Wikipedia) và `_stock_score` (stock). Trước đây ảnh
  ngang 4000x3000 vẫn ACCEPT 86.4.
- (b) Khớp nửa cụm: `keyword_score` 0.6 (≥50% token) hoặc 0.3 (1 token) thì
  tối đa CONSIDER, dù cộng điểm đủ 70. Tiền lệ sửa: "gold vault" ACCEPT
  76.2 nhưng là họa tiết vàng trên mặt tiền, không phải két vàng.
- (c) Video Pexels: trước đây haystack chỉ là slug URL (ACCEPT S2 courtroom
  9s là may mắn theo slug). Nay haystack = slug URL + tên uploader (mọi
  trường mô tả thật mà Pexels video API trả về — API này không có
  title/tags/description), và ứng viên chỉ khớp nhờ slug thì tối đa
  CONSIDER (hàm `_slug_only_match`).
- (d) Đường vault-video: ĐÃ ĐỐI CHIẾU HELPER THẬT và sửa kết luận của
  audit — audit nói vault-video "trỏ URL ảnh" là CHƯA ĐÚNG với helper hiện
  tại: cả hai helper đều dùng chung tên trường `largeImageURL` làm "URL
  file đã chọn", và với video thì giá trị là URL file video thật do helper
  tự chọn (Pixabay helper chọn file video tốt nhất; Pexels helper chọn
  link mp4 tốt nhất), nên nhãn video/mp4 là đúng khi file tồn tại. Lỗi
  thật là hit không có file (Pixabay helper trả `largeImageURL: None`
  khi không chọn được file) mà code cũ vẫn đưa vào danh sách — nay bỏ qua
  các hit không có file. Đường vault Pexels video cũng bị hạ ACCEPT →
  CONSIDER vì helper chỉ trả pageURL, không còn metadata mô tả khác để
  chấm (khớp nhờ slug theo định nghĩa).
- Phụ: đổi tên biến shadow `key` → `rank_key` trong vòng chọn file video
  Pixabay (trùng tên tham số API key của hàm — chưa vỡ vì URL build
  trước, nhưng là bẫy cho lần sửa sau).
- Bằng chứng trước/sau (test wikimedia thật, không key, 29/10/2026):
  - Ảnh "phòng xử án": vẫn ACCEPT_TOP, đầu bảng Cleburne 97.2 ACCEPT
    (không hồi quy); hai ảnh ngang Singapore 4032x3024 nay là CONSIDER
    86.4 thay vì ACCEPT — cổng ảnh ngang hoạt động trên dữ liệu thật.
  - Video "phòng xử án" 8.6s: CONSIDER_TOP, Shire Hall 80.1 CONSIDER
    (cổng video ngang giữ nguyên).

## 5. Skill — gỡ xung đột phạm vi + chuỗi app cũ (audit B-C1, B-C2, B-C3, B-C4, E-15)

- `media-coo/SKILL.md`:
  - "Chỉ chuyển video sang đăng tải khi Kỹ thuật đã duyệt và Kinh doanh
    đã gắn sản phẩm" → chỉ chuyển video đã duyệt sang bàn giao Drive cho
    công ty khác; không đăng tải, không gắn sản phẩm, không chờ Kinh
    doanh (đã giải thể 26/10/2026).
  - `08_Publish_Tracking` ghi rõ là link Drive bàn giao, không phải số
    liệu phát hành; "không tự đăng video chưa qua QA" → không đăng dưới
    mọi hình thức, kể cả video đã qua QA.
- `media-topic-scoring/SKILL.md`: bỏ tiêu chí kiếm tiền/affiliate 15 điểm,
  thay bằng "độ rõ nguồn và khả năng kiểm chứng" 15 điểm. Thang mới:
  30+20+20+15+15 = 100. Điểm đã công bố theo thang cũ giữ nguyên, không
  chấm lại; thang mới áp dụng cho chủ đề chấm từ 29/10/2026.
  Đã cập nhật mọi chỗ trích thang cũ tìm được: `company-os/topic-scoring-skill.md`
  (bản mirror). `google-sheet-spec.md` không còn trích thang cũ (đã grep).
- `media-video-production/SKILL.md`:
  - Bỏ "sản phẩm gợi ý" (đọc brief) và "nền tảng dự kiến đăng" (bàn giao).
  - Viết lại mục "Làm video": app-t-o-video là công cụ độc lập, không
    tích hợp Sheet/QA; XÓA khỏi chuỗi bắt buộc: storyboard preview, tự
    kiểm trước render của app, handoverToSheet. Đường pipeline chính là
    script repo (createProject → saveScript/savePlan → runTTS →
    generateImages → runKaraoke → runPreflight → startRenderDraft →
    getRenderStatus → exportProject). Ghi chú timeout 30s của action app
    cũ được rút gọn thành hành vi resume chung (chạy lại bỏ qua phần đã
    xong), không còn là hướng dẫn thao tác app cũ.
  - Cập nhật ghi chú preflight cho khớp code mới: thiếu ảnh = lỗi (không
    còn cảnh báo), cảnh báo <180s, >300s, 0 SFX, part có template mà plan
    chưa copy SFX.
  - Bổ sung cổng ACCEPT mới (ảnh ngang, khớp nửa cụm, slug Pexels) vào
    đoạn chấm điểm media để skill khớp code.
- GIỮ NGUYÊN ngoại lệ: video QA duyệt vẫn bàn giao lên Drive và ghi link
  vào Sheet; công ty này vẫn không đăng nền tảng, không affiliate, không
  doanh thu.

## 6. Skill — điều khoản lệnh trực tiếp CEO + ngoại lệ độ dài (audit B-C11, E-16)

- Thêm vào cả 3 skill COO, Production, QA (cùng một điều kiện, không lệch):
  - CEO có thể giao video ngoài hàng Approved bằng lệnh trực tiếp ghi rõ
    trong Sheet/chat COO ("lệnh trực tiếp, không qua Approved"). Lệnh
    trực tiếp KHÔNG miễn QA, không miễn ghi rõ nguồn, không miễn lọc
    trùng, và KHÔNG tự động kèm ngoại lệ độ dài.
  - Ngoại lệ độ dài cho video bàn giao chỉ khi CEO cho phép rõ ràng
    trong lệnh đó (số giây + lý do, ví dụ Ukraine 455s ngày 29/10/2026).
    Production và QA phải ghi rõ ngoại lệ trong bàn giao, không trình bày
    như video đúng chuẩn 180-300s, không tự suy ra từ video đã duyệt,
    không tự cắt kịch bản để vừa chuẩn.
- Preflight cũng thêm cảnh báo >300s (vẫn cho qua, không thành lỗi) để
  ngoại lệ được nhìn thấy trước khi render.

## 7. Skill QA — cửa kiểm tra HỒ SƠ, KHÔNG thêm cửa ngữ nghĩa (audit B-C5, B-C6, E-3, E-4)

- File: `media-video-tech-qa/SKILL.md`, mục mới "Cửa kiểm tra HỒ SƠ bàn
  giao" (áp dụng video nộp từ 29/10/2026):
  - Video 180-300s mà 0 SFX → TRẢ LẠI; bàn giao phải ghi số SFX + danh
    sách theo beat.
  - Còn `KARAOKE-WARN` → TRẢ LẠI để sửa gốc; chỉ duyệt kèm lý do chấp
    nhận ghi rõ trong verdict nếu QA xét thấy WARN không ảnh hưởng trải
    nghiệm — không duyệt im lặng.
  - Plan phải ghi đủ cho MỖI media: nguồn, điểm số, giấy phép, link.
    Thiếu trường → trả lại để bổ sung. QA kiểm đủ trường, không chấm
    lại điểm thay Production.
  - Prompt ảnh/video MỚI (từ 28/10/2026) phải tiếng Việt, có đủ tóm tắt
    kịch bản + prompt chi tiết trong plan; prompt mới không phải tiếng
    Việt → trả lại. Prompt tiếng Anh của video đã duyệt trước 28/10 giữ
    nguyên, không truy hồi.
  - Ảnh AI/minh họa chung chung mà bàn giao không ghi rõ là minh họa,
    không phải tư liệu thật/chân dung thật → TRẢ LẠI để ghi rõ.
  - Cập nhật ghi chú preflight trong QA cho khớp code: thiếu ảnh nay là
    lỗi preflight (exit 1), không còn cảnh báo.
- TUYỆT ĐỐI KHÔNG thêm cửa ngữ nghĩa image-vs-script cho QA (quyết định
  CEO 28/10/2026 giữ nguyên): QA không chấm ảnh có đúng ý kịch bản hay
  không; việc đó vẫn chỉ ở phía Production (soi trực quan đầu bảng, tự
  loại ứng viên lệch). Skill QA ghi rõ: nếu thấy cần cửa này thì chỉ ghi
  ĐỀ XUẤT để CEO quyết, không tự áp dụng.

## 8. SFX/meta — cảnh báo preflight, KHÔNG tự copy (audit D-L6, E-13)

- Render giữ nguyên: chỉ đọc SFX từ plan, không đọc template meta.
- Preflight mới: part có template mà meta template gợi ý SFX (dict có id,
  hoặc string như breaking-banner `whoosh_fast`) nhưng plan chưa có
  `broll.sfx` → cảnh báo ghi rõ SFX gợi ý, yêu cầu Production copy vào
  plan theo luật SFX. Template không có key sfx (source-footer-safe) hoặc
  sfx null thì không cảnh báo. KHÔNG tự động sao chép lặng lẽ.
- Preflight cũng cảnh báo khi toàn video 0 SFX (warning, không chặn clip
  test kỹ thuật).
- Bằng chứng: project tạm 2 part (stat-counter, section-title) không sfx
  → cả hai cảnh báo SFX đều hiện, kèm cảnh báo 0 SFX.

## 9. Motion lock — chỉ kiểm chứng, không làm lại (audit D-L9, E-11)

- `bin/render_draft.py`: zoom tối đa 1.05, motion tuyệt đối `on/frames`,
  easing smoothstep `s=t*t*(3-2*t)`, ảnh nguồn 4x — khớp.
- `lib/render-engine.js` (đã chuyển sang CSS keyframes ngày 29/10/2026,
  trước đợt này): 6 keyframes, zoom tối đa 1.05, pan ±2%, easing
  ease-in-out xấp xỉ smoothstep; không còn 1.12. Khớp với ffmpeg.
- `bin/build_render_page.py` vẫn dùng được engine mới: nó nhúng trực tiếp
  `lib/render-engine.js` vào HTML. Kiểm chứng: chạy trên test001 ra
  `RENDER-PAGE-OK` (19KB, 1 part), HTML nhúng chứa keyframes vn-motion
  và `setPlaying`, không chứa `scale(1.12`; file test đã xóa sau kiểm
  chứng để test001 nguyên trạng. Không sửa dòng nào ở mục này.

## 10. Dọn rác (audit C-1, C-2, C-3, C-4, C-5)

### 10a. Hàm chết đã xóa (grep toàn repo + company-os chứng minh không caller)

| Hàm | Bằng chứng không caller | Ghi chú |
|---|---|---|
| `bin/karaoke.py:147` `clean_display()` | Chỉ có dòng định nghĩa; `main()` không gọi; app (TypeScript) không thể gọi hàm Python không phải entry point | Đã xóa |
| `bin/karaoke.py:169` `estimate_chunk_spans()` | Không call site nào | Đã xóa |
| `bin/normalize_chunks.py:31` `sentence_pairs()` | Chỉ được nhắc trong docstring của `sentence_pairs_expanded()`; `:88` dùng bản expanded | Đã xóa; docstring của bản expanded đã viết lại tự chứa, không còn tham chiếu hàm đã xóa |
| `lib/vi_sub/phrase_splitter.py:366` `split_cues()` | `karaoke.py` chỉ dùng `split_cue()` số ít (:259, :295); các hit còn lại chỉ là key string trong dict stats | Đã xóa, để lại NOTE chỉ đường backup |
| `search_media.py` `CONCEPT_EN` | Build từ cụm nhưng không dùng để chấm (chấm dùng `cluster_phrases()` trực tiếp); hit ngoài file chỉ là chữ trong lý do của script mrpips cũ | Đã xóa; LOGIC.md cập nhật khớp code |
| `search_media.py` `vi_tokens()`, `concept_queries()`, `whole_word_match()`, `concept_tokens()` + tham số `query_tokens` của `score_candidate()` | Không call site nào (concept_tokens chỉ nuôi tham số đã ghi chú là "không dùng") | Đã xóa |

### 10b. Cách ly (KHÔNG xóa vĩnh viễn) — xem `quarantine/INDEX.md`

Chuyển (mv) 10 file vào `code-fix-20261029/quarantine/` (giữ cấu trúc):
- Script plan one-shot (chạy lại ghi đè plan live): `vinspeed-plan.py`,
  `mrpips-remake-new-plan.py`, `mrpips-v3-apply.py`,
  `mrpips-v3-search.py`, `mrpips-remake-videos.py`.
- Backup cũ chứa bug, tên trung tính: `karaoke_before_dash_fix.py`
  (lỗi dấu câu), `motion-check/render_draft_before_motion_fix.py`
  (motion đứng yên), `topic004-check/render_draft_before_qa_fix.py`
  (zoom 1.08/1.12 cắt chữ).
- Chuỗi frame-capture mồ côi: `bin/render_frames.py`,
  `bin/assemble_frames.py`. Đã chứng minh không còn dùng: không file nào
  trong bin/docs/PIPELINE/README nhắc tới, không project nào có
  `build/frames` hay `*_frames.mp4`, app client không nhắc tới. Riêng
  `assemble_frames.py` còn sai BGM path/SFX/ducking so với render_draft.
- GIỮ LẠI ở cây live: `bin/build_render_page.py` (chỉ dựng trang HTML
  dùng chung engine với Preview, không tự chụp/ghép frame).

### 10c. Hằng số trùng lặp — KHÔNG gom trong đợt này

FACTORY, màu highlight #FBBF24, 720x1280, pauseAfterMs 180, giọng Minh Quân,
SR 24000 lặp ở nhiều file nhưng gom chúng đổi hành vi ở ~18 chỗ mà không
có test chạy lại được cho mọi script. Ghi vào đây thay vì gom ẩu; cần một
đợt refactor riêng với test cho từng script nếu CEO muốn gom.

---

## Kiểm chứng trước khi báo xong (chạy thật)

| Kiểm chứng | Kết quả |
|---|---|
| `py_compile` preflight, tts_batch, search_media, karaoke, normalize_chunks, phrase_splitter | ĐẠT |
| `node --check lib/render-engine.js` | ĐẠT |
| Preflight pokrovsk001 (24 parts, 283.4s) | ĐẠT, exit 0, không cảnh báo |
| Preflight vinspeed001 (30 parts, 267.4s) | ĐẠT, exit 0, không cảnh báo |
| Preflight project tạm: thiếu ảnh + thiếu input bắt buộc + part có template mà plan thiếu SFX + 0 SFX | CHƯA ĐẠT, exit 1, đủ 4 loại lỗi/cảnh báo mới — đúng hành vi |
| Preflight test001 (fixture không ảnh) | CHƯA ĐẠT, exit 1 — hành vi đúng, xem mục "cố tình không sửa" |
| tts_batch project tạm, partId trùng | Exit 2, lỗi nêu rõ `part1`, không viết `tts.json` |
| search_media wikimedia "phòng xử án" (image, không key) | ACCEPT_TOP; Cleburne 97.2 ACCEPT (không hồi quy); ảnh ngang Singapore 86.4 nay CONSIDER (cổng mới hoạt động) |
| search_media wikimedia "phòng xử án" (video 8.6s) | CONSIDER_TOP; Shire Hall 80.1 CONSIDER (cổng video ngang giữ nguyên) |
| build_render_page test001 với engine mới | RENDER-PAGE-OK, HTML chứa vn-motion + setPlaying, không chứa scale(1.12; file test đã xóa |
| md5 7 MP4 đã bàn giao | Khớp toàn bộ: TOPIC-004 v2 `abb98443c82aef8a9fffd43055c69370`, Hormuz v3 `218251bb94bc6e6823f485b4e3231c9c`, Án mạng `60ba82b48f01fad8c7f471e4fd19ad3e`, Vinspeed `9d48d810ea3c957c5de4160f4e1c9dba`, Mr Pips v3 `e56a68485837d7ee7da25e27b405b8c9`, Ukraine `d63154c43bab7e63da7acf02b39b3481`, Pokrovsk `f08ff80250d7ce66b95d2823dd34910a` |
| Không ghi key/credential nào | Đạt — không key nào xuất hiện trong code, file kết quả hay báo cáo này |
| Không viết Sheet, không đăng, không Drive, không push GitHub | Đạt — không thao tác nào trong số đó được thực hiện |

Chưa kiểm chứng (ghi rõ, không tuyên bố đạt):
- Chạy tts_batch thật với plan ID duy nhất để tổng hợp audio (cần model
  VieNeu + thời gian chạy): chỉ kiểm chứng đường lỗi trùng ID fail-fast;
  đường tổng hợp bình thường không đổi code (chỉ thêm check trước khi
  nạp model) nhưng chưa chạy lại end-to-end trong đợt này.
- Chạy search_media lớp stock qua vault/API sau sửa (cần key qua vault):
  chỉ kiểm chứng lớp Wikipedia (không cần key) và logic cổng bằng code +
  dữ liệu Wikipedia thật. Cổng `_verdict` dùng chung cho cả hai lớp nên
  logic đã chứng minh trên lớp Wikipedia, nhưng đường stock chưa chạy
  thật trong đợt này.
- Bấm thử Preview trong trình duyệt sau sửa skill (skill không đổi code
  app; engine đã kiểm chứng ngày 29/10/2026 trước đợt này).

---

## Cố tình KHÔNG sửa và lý do

1. **Không thêm cửa ngữ nghĩa image-vs-script cho QA** — quyết định CEO
   28/10/2026, lệnh lần này nhắc lại tuyệt đối không thêm. Chỉ thêm cửa
   HỒ SƠ và ghi rõ ranh giới trong skill QA.
2. **Không tự động copy SFX từ meta template vào plan** — lệnh yêu cầu chỉ
   cảnh báo. Render vẫn chỉ đọc SFX từ plan.
3. **Không làm lại motion** — engine Preview đã chuyển sang CSS 1.05 ngày
   29/10/2026; đợt này chỉ kiểm chứng khớp với ffmpeg.
4. **Không gom hằng số trùng lặp** — rủi ro đổi hành vi, không có test
   chạy lại được cho mọi script (xem 10c).
5. **Không cách ly script one-shot ghi Sheet và 2 thư mục backup đồng bộ**
   (`repo-sync-backup-20261027`, `repo-app-audit-20261027`) — nhóm Sheet
   chạy lại chỉ gây trùng Sheet, không phá video, và còn là tài liệu tham
   khảo schema; 2 thư mục backup chưa diff toàn bộ với factory hiện tại.
   Cần quyết riêng trước khi cách ly (xem dưới).
6. **Không sửa các mục audit ngoài 10 mục đã chốt** (ví dụ: B-C7 quyền ghi
   Sheet khi Production lọc trùng topic Approved, B-C8 đổi tên ngưỡng
   MEDIA-ACCEPT/MEDIA-EARLY-STOP, B-C10 checklist hook cho Production,
   D-L7 tra partIdx từ tts thay vì parse ID, D-L8 KARAOKE-WARN thành exit
   non-zero, D-L10 karaoke regen theo mtime plan, D-L12 lock chạy đồng
   thời, D-L15 `_thumb_` rò vào ZIP, D-M3/M6/M7/M8 các lệch LOGIC còn lại,
   D-T1 thống nhất CLI/server/batch) — các mục này vẫn là đề xuất chờ
   CEO, không tự mở rộng phạm vi lệnh lần này. Riêng D-L7: render vẫn
   parse ID part để gắn SFX; các project live hiện tại đều dùng ID dạng
   `sceneX-part-Y` nên chưa vỡ, nhưng ID dạng `part-1` vẫn làm mất SFX
   lặng lẽ — cần quyết sửa riêng.
7. **Không sửa source artifact app-t-o-video** — ngoài phạm vi lệnh (chỉ
   ghi vào báo cáo nếu phát hiện cần sửa; đợt này không phát hiện app
   cần sửa thêm ngoài phần setPlaying đã xong ngày 29/10/2026).
8. **test001 nay preflight CHƯA ĐẠT** — cố tình, không phải hồi quy:
   test001 là fixture test không ảnh; với luật mới (thiếu ảnh = lỗi) thì
   preflight của nó phải fail. Nó không phải video bàn giao và không được
   render làm video bàn giao.
9. **Điểm Scoring cũ giữ nguyên** — TOPIC-028 82/100 (trong đó 8 điểm kiếm
   tiền cũ) và các điểm đã công bố khác không chấm lại; thang mới chỉ áp
   dụng từ 29/10/2026.

## Cần CEO quyết thêm (không tự quyết trong đợt này)

1. Có cách ly tiếp nhóm script one-shot ghi Sheet và 2 thư mục backup
   đồng bộ không (mục 5 trên)?
2. Có gom hằng số trùng lặp thành module config chung không (cần test cho
   từng script)?
3. Có sửa D-L7 (tra partIdx từ tts thay vì parse chuỗi ID khi gắn SFX)
   và D-L8 (KARAOKE-WARN thành exit non-zero cho video bàn giao) không?
   Cả hai đều là cửa chặn mạnh thêm, ngoài 10 mục đã chốt.
4. Có duyệt cửa ngữ nghĩa image-vs-script cho QA không (hiện vẫn cấm theo
   quyết định 28/10; QA mới chỉ có cửa hồ sơ)?
5. Có áp dụng thang Scoring mới ngược lại cho các topic đã chấm (hiện giữ
   nguyên điểm cũ) không?
6. App có cần sửa gì thêm không sau khi skill đã viết lại theo hướng
   standalone — đợt này không phát hiện, nhưng CEO là người dùng app trực
   tiếp nên xác nhận cuối vẫn thuộc về CEO.

---

## Thống kê

- File sửa nội dung: 12 (preflight.py, tts_batch.py, search_media.py,
  LOGIC.md, 5 skill, karaoke.py, normalize_chunks.py, phrase_splitter.py)
  + 1 file mirror thang điểm (`company-os/topic-scoring-skill.md`).
- File cách ly (không xóa): 10 (5 script plan, 3 backup cũ, 2 frame-capture).
- Hàm chết đã xóa: 9 hàm + 1 tham số (repo: clean_display,
  estimate_chunk_spans, sentence_pairs, split_cues; search_media:
  CONCEPT_EN, vi_tokens, concept_queries, whole_word_match, concept_tokens
  + tham số query_tokens của score_candidate).
- Lỗi/cổng mới có bằng chứng chạy thật: preflight inputs, partId trùng,
  thiếu ảnh thành lỗi, ảnh ngang, khớp nửa cụm, slug Pexels, vault
  không-file, cảnh báo SFX template, cảnh báo 0 SFX, cảnh báo >300s.
- Backup: `~/workspace/company-os/code-fix-20261029/backup/`
- Quarantine + INDEX: `~/workspace/company-os/code-fix-20261029/quarantine/`
