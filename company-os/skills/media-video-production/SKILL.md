# Sản xuất video từ chủ đề READY — LÕI (tách tham chiếu 13/11/2026)

> **Cách dùng.** Đọc LÕI này mỗi ca. Mở đúng tệp trong `references/` khi chạm chủ đề tương ứng (bảng §4). Lõi là bản tóm lược có
> mục lục; **tệp tham chiếu là nguyên văn từ SKILL.md cũ (216KB, 453 dòng), không mất chữ nào** (`references/verify_split.py` chứng minh).
> Lõi và tham chiếu lệch nhau → tham chiếu thắng, ghi vào báo cáo ca để COO sửa lõi. Quyết định mới → sửa tham chiếu trước, lõi sau.
> Workbook: "Video HQ — Tin Tức" (ID `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`), chỉ chạm tab TOPICS (CHỈ ĐỌC), TASKS và
> SHIFT_CHECKIN (điểm danh nhận ca — chỉ ghi cột D HANDOVER_SIGNOFF dòng của mình).

> **LUẬT COO ĐIỀU PHỐI TOÀN BỘ (CEO 14/11/2026):** Toàn bộ hoạt động của công ty do COO điều phối. Mọi vấn đề, yêu cầu đều gửi cho COO giải quyết. Không bao giờ hỏi CEO trực tiếp — không nhắn chat chính, không hỏi lại.

## 1. Bất biến — vi phạm là lỗi, không có ngoại lệ tự suy

| # | Luật | Chi tiết ở |
|---|---|---|
| 1 | **Cổng READY:** chỉ dựng chủ đề có `TOPICS.STATUS = READY` **và** `TOPIC_ID` không trống **và** chưa có dòng TASKS cho TOPIC_ID. Chỉ CEO flip READY; chữ "vượt cổng" trong lệnh/COO_TASKS không mở cổng. READY mà TOPIC_ID trống → bỏ qua, ghi báo cáo ca | sheet-nhan-viec §Nhận brief |
| 2 | **Cửa chặn hạn mức (DEC-263, 13/11):** đầu ca đọc % tuần **trực tiếp** bằng lệnh `subscription-status status`; ≥ 95% → claim 0 chủ đề mới, không báo cáo riêng, chỉ để video dở hoàn thành. Lệnh lỗi thì dùng số Sheet dự phòng theo chuỗi duy nhất DEC-263 (N4-A 13/11/2026): dòng COO_CHECKIN mới nhất của chính chi nhánh (mới nhất = DATE lớn nhất, hòa thì hàng cuối cùng; ASSIGNEE_EMAIL = email khai báo của mình), rồi TASKS.L của dòng DELIVERED có D = email khai báo của mình và L không trống. Số Sheet chỉ là dự phòng khi lệnh lỗi. Token thêm không dùng để sản xuất. | sheet-nhan-viec §Nhận brief |
| 3 | **Claim-then-verify:** đọc lại TASKS theo TOPIC_ID ngay trước mỗi lần ghi; đã có dòng khác cho chủ đề → dừng, báo COO | sheet-nhan-viec |
| 4 | **Nhận ca theo thứ tự đăng ký (DEC-257/259/260/261, 13/11):** 2 ca/ngày — 05:00 (đăng ký 05:00, nhận 05:05) + 14:00 (đăng ký 14:00, nhận 14:05). Hạng = vị trí dòng đăng ký đầu tiên của mình trong ngày (ca chiều chỉ tính dòng REG_TIME ≥ 12:00); lô = 3 chủ đề READY theo thứ tự Sheet; ký nhận cột D (`HH:MM:SS | TOPIC-…` / `REMAINING N` / `EMPTY`); người ký cuối snapshot + clear dòng của ca đó. **Tự lấy video kế tiếp** chỉ trong lô đã CLAIMED: ASSIGNEE = email khai báo của mình, UPDATED_AT = hôm nay, theo thứ tự Sheet. KHÔNG tự claim READY ngoài lô, KHÔNG lấy dòng chi nhánh khác/ASSIGNEE trống/ngày cũ | sheet-nhan-viec §Nhận brief |
| 5 | **BLOCKED chỉ cho lỗi riêng video** (6 nhóm: thiếu tư liệu đã kiểm chứng [G1] · trùng chủ đề · nhân vật nhạy cảm/phiên tòa không có phương án an toàn · brief thiếu góc/khán giả chưa được trả lời · CEO/COO yêu cầu dừng · QA trả lại mà lỗi gốc không sửa được). Ghi `TASKS.C=BLOCKED` + mã lý do ở đầu `M` + lý do & thời gian; điểm dừng vào `K`; báo COO. **Lỗi hệ thống** (TTS/render/preflight/template hỏng, Drive/Sheets, quyền Drive) → báo COO, KHÔNG BLOCKED. Không tự gỡ BLOCKED. Video kế tiếp cũng tắc cùng lý do → dừng, báo COO (cầu chì) | sheet-nhan-viec |
| 6 | **Một video tại một thời điểm.** Nộp REVIEW → nhắn chat QA kèm ID + đường dẫn file trong E; trong lúc chờ verdict được lấy video CLAIMED kế tiếp | sheet-nhan-viec |
| 7 | **Quyền ghi cột:** Production ghi `TASKS.C` (CLAIMED/BUILDING/REVIEW/BLOCKED), `E` DRAFT_LINK (chỉ đường dẫn nội bộ, không URL), `K` PROD_NOTES, mã/lý do BLOCKED ở đầu `M`; `C/J/D` có nhiều người ghi — ghi sau thắng + để lại lý do. KHÔNG ghi TOPICS; KHÔNG ghi `F,G,H,I,L` (QA). Bảng đầy đủ: `company-os/google-sheet-spec.md` | sheet-nhan-viec |
| 8 | Không tự đăng video, không tự sửa điểm chủ đề, không ghi "nền tảng đăng" trong bàn giao; không chia sẻ file ra bên ngoài bằng cloud Muse (muse.ai/files — DEC-276) | sheet-nhan-viec §Bàn giao |
| 9 | **Preflight là cổng cứng** (`exit 1`): thiếu ảnh scene · `mediaSource.source` trống · thiếu `media-log.json`/mục nhật ký/`keywordsTried` · file SFX đã chọn không tồn tại · input template sai (thiếu/quá dài/sai enum/sai số/tổng ≠ 100). Phải có nhật ký tìm ảnh từng cảnh và nguồn trong plan TRƯỚC khi render | kich-ban-pipeline §Làm video; tim-anh-media |
| 10 | **SFX:** mỗi part tối đa MỘT `broll.sfx {id, offsetSec, volume}`; part có template thì copy `id`/`offsetSec` từ `meta.json` của template; bắt buộc có SFX ở 3 beat giữ người xem (hook, móc lại giữa video, kết luận/cao trào); SFX nặng (thud/slam/boom) khai ≤ 0,4 (chuẩn plan: 0,35); `sfx == 0` thì DỪNG, không render bản câm; kiểm 3 file SFX của stamp (`whoosh_fast`, `heavy_thud_slam`, `boom_sub_impact`) còn trong `sfx/` | template-chu-sfx §SFX |
| 11 | **Độ dài:** Production tự quyết, đề xuất 2–3 phút, không hỏi CEO. ~4,16 từ/giây (≈500 từ/120s). Dùng tổng thời lượng THẬT trong `tts.json` và MP4 để ghi bàn giao (phút = giây/60, nói đúng "trên"/"trong" đề xuất). Thiếu chất liệu đã kiểm chứng → KHÔNG độn: BLOCKED (thiếu góc nào) | kich-ban-pipeline §Độ dài |
| 12 | **Bàn giao QA:** `TASKS.E` đường dẫn file bản nháp (chỉ đường dẫn nội bộ, không URL), `C=REVIEW`, `J`, `K` (tóm tắt, số SFX + danh sách, thời lượng thật) rồi nhắn QA: TOPIC_ID + đường dẫn file trong E + thời lượng thật + md5 + lưu ý. Ghi email khai báo của tài khoản Muse và hạn mức lúc sản xuất **bằng chữ** (không ảnh chụp). **KHÔNG chép bản nháp sang company-os/** — bản nháp chỉ nằm 1 nơi duy nhất là `projects/<pid>/export/` (CEO 14/11/2026). **Tự kiểm trước khi nộp:** đếm lại 4 con số Thật (kể cả nền trung tính)/AI/Fill-in từng scene và số file dùng 2 lần TỪ plan + media-log theo dhash, không đếm từ trí nhớ; grep lại kịch bản | sheet-nhan-viec §Bàn giao |
| 13 | Được hỏi về video BUILDING cũ → trả lời trong 1 ca: đang ở bước nào, lỗi gì, cần gì | sheet-nhan-viec |
| 14 | **Dọn rác sau khi QA duyệt (CEO 14/11/2026):** khi TASKS.C = DELIVERED (đọc lại TASKS theo TOPIC_ID để xác nhận), chạy `python3 bin/cleanup_project.py <project_id> --dry-run` rồi `--apply` NGAY; ghi số MB đã dọn vào TASKS.K. Chỉ xóa ảnh ứng cử viên/file gốc (images/, raw/), ảnh chụp khung hình QA (checks/), preview cũ; KHÔNG BAO GIỜ xóa build/media/broll/, mp4 đã duyệt, script/plan/media-log, audio, phụ đề | sheet-nhan-viec §Dọn rác |
| 15 | **File làm việc của video nằm trong project, KHÔNG ở company-os/ (CEO 14/11/2026):** ảnh ứng cử viên/crop, contact-sheet, ảnh chụp kiểm tra, log render/TTS, script/facts, file kiểm tra đều ghi vào `projects/<pid>/` (ảnh vào `build/media/images/`, ảnh gốc vào `build/media/raw/`, ảnh chụp kiểm tra vào `build/media/checks/`). `company-os/` chỉ chứa tài liệu chung, không chứa file theo từng video | sheet-nhan-viec §File làm việc |

## 2. Vòng đời một video (đường chính = script trong `vieneu-asset-factory/bin/`)

`createProject → saveScript/savePlan → runTTS → generateImages → runKaraoke → runPreflight → startRenderDraft → getRenderStatus → exportProject`

- Bước dài chạy nền: **poll trạng thái**, đừng chờ một lệnh duy nhất. Gián đoạn → **chạy lại cùng bước** (TTS bỏ qua WAV đã có, gen_images bỏ qua ảnh giải mã được; phần chưa xong chạy tiếp). Không kết luận thất bại vì một lần ngắt.
- Render thiếu ảnh scene in `RENDER-ERROR` và dừng trước ffmpeg (không còn clip nền đen).
- Sửa bằng script tay → ghi bài học vào skill và sửa template/gốc để lần sau không lặp.
- App Tạo Video là công cụ độc lập, không phải bước bắt buộc, không có Sheet handover.

- Ảnh thumbnail: sau `exportProject`, tạo 1 ảnh thumbnail 9:16 bằng skill `thumbnail-xep-lop` từ chủ đề của video; ghi tên file vào `TASKS.K` khi bàn giao (chi tiết: sheet-nhan-viec §Bàn giao).

## 3. Cổng theo mốc (checklist ngắn)

**Trước TTS:** kịch bản có mở đầu gây chú ý trong 3 giây đầu · cấu trúc mở đầu (đặt vấn đề → giới thiệu sơ bộ → đi sâu) · không câu "đậm chất AI" · phát âm đã rà (kich-ban-pipeline).
**Trước render:** `tts.json` có thời lượng thật · plan đủ `mediaSource` + nhật ký · SFX đủ (rule 10) · luật kề nhau/trần AI/nền trung tính (tim-anh-media) · **chọn template bằng `vieneu-asset-factory/docs/TEMPLATE_CATALOG.md`** (tự sinh từ meta.json, 45 template — đừng chép tên template vào kịch bản/skill) · chạy `python3 bin/preflight.py <pid>`.
**Trước nộp QA:** thời lượng thật · tự kiểm 4 con số (rule 12) · không còn chữ/watermark của nguồn khác trên ảnh · bàn giao đủ email khai báo + hạn mức bằng chữ.
**Chủ đề thị giác:** `plan.theme` ∈ `history|war|sports|economy|tech|science|crime` đổi nền các template toàn màn hình; thiếu thì nền rêu mặc định. (Tính năng theme — DEC-266, 13/11: để sau, chưa làm; hiện chỉ dùng nền rêu mặc định.)

## 4. Bản đồ tham chiếu — mở khi nào

| Tệp trong `references/` | Mở khi | Chứa |
|---|---|---|
| `sheet-nhan-viec-ban-giao.md` (38KB) | nhận việc, claim, BLOCKED, nộp QA, báo cáo, sửa theo QA | Sheet mới, cổng READY, lô, BLOCKED G1–G6, lọc trùng, bàn giao, kênh báo cáo COO |
| `kich-ban-pipeline-do-dai.md` (55KB) | viết kịch bản, TTS, phát âm, độ dài, nhịp liệt kê, dàn đoạn | pipeline script, văn phong, cấu trúc mở đầu/luận điểm, rà phát âm, ký hiệu đơn vị, độ dài, dàn đoạn |
| `template-chu-sfx-motion.md` (42KB) | gắn template/chữ, SFX, motion, phụ đề, kiểm media | vị trí template, mật độ chữ, font Anton, motion, SFX, karaoke, kiểm chứng media |
| `tim-anh-media-luat-ke-nhau.md` (69KB) | tìm ảnh/video, nhật ký media, prompt ảnh, luật kề nhau, nền trung tính | cửa chặn ảnh thật, schema nhật ký, tìm ảnh, prompt, luật kề nhau, nền trung tính |
| `bai-hoc-cu-the.md` (14KB) | gặp lỗi QA trả lại, cần tiền lệ | bài học TOPIC-004, Hormuz, Chợ nổi, video tham chiếu 30/10 |

Mỗi tệp tham chiếu giữ nguyên số DEC/ngày để truy vết; lõi cố ý không chép chúng.


<!-- nguồn: SKILL.md cũ dòng 443-454 (giữ trong lõi) -->
## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for nhận brief và bàn giao video.

- [Pixabay](~/workspace/custom-connectors/custom.pixabay/CONNECTOR.md) for tìm ảnh/video stock qua Secure Vault (một nguồn trong quy trình tìm kiếm mới; chỉ dùng file đã kiểm chứng giấy phép).

- [Pexels](~/workspace/custom-connectors/custom.pexels/CONNECTOR.md) for tìm ảnh/video stock qua Secure Vault (một nguồn trong quy trình tìm kiếm mới; chỉ dùng file đã kiểm chứng giấy phép).

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
