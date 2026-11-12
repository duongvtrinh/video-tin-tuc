# QA kỹ thuật và nâng cấp code tạo video — LÕI (tách tham chiếu 13/11/2026)

> **Cách dùng.** Đọc LÕI này mỗi ca. Mở đúng tệp trong `references/` khi chạm chủ đề tương ứng (bảng §4). Lõi là bản tóm lược có
> mục lục; **tệp tham chiếu là nguyên văn từ SKILL.md cũ (66.954 byte, 207 dòng), không mất chữ nào** (`references/verify_split.py` chứng minh).
> Lõi và tham chiếu lệch nhau → tham chiếu thắng, ghi vào báo cáo ca để COO sửa lõi. Quyết định mới → sửa tham chiếu trước, lõi sau.
> Workbook: "Video HQ — Trụ sở Muse" (ID `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`), chỉ chạm tab TASKS và QA_LOG (ghi verdict),
> COO_TASKS (đọc lệnh COO), CEO_REPORTS (chỉ đọc lệnh CEO — DEC-114).

## 1. Bất biến — vi phạm là lỗi, không có ngoại lệ tự suy

| # | Luật | Chi tiết ở |
|---|---|---|
| 1 | **3 cửa duyệt:** kỹ thuật sạch + đẹp + giữ người xem — duyệt chỉ khi cả 3 qua; trả lại kèm danh sách lỗi theo mốc giây + cách sửa từng lỗi | danh-gia-va-tieu-chi §Cách chấm |
| 2 | **Ghi verdict 2 chỗ, cùng 1 lần chấm:** QA_LOG 1 dòng mới (VIDEO_ID, VERSION, DATE, RESULT, ISSUES, REPO_NOTE) + TASKS (F QA_VERDICT, G RETURNS +1 khi RETURNED, C STATUS, J UPDATED_AT). Khi TRẢ LẠI: ghi dòng RETURNED NGAY trong cùng lượt, TRƯỚC khi nhắn Production. Chấm bản sửa: đọc lại QA_LOG, thiếu dòng RETURNED cũ thì ghi đính chính trước rồi mới ghi APPROVED | sheet-nhan-viec §Sheet mới |
| 3 | **Duyệt → tự upload Drive NGAY trong cùng lượt:** file duyệt lên Drive "Video Muse" + ghi DRIVE_LINK (H) + MD5 (I) + C=DELIVERED + ký nhận/hạn mức tự đọc lúc upload vào L QUOTA (bằng chữ). Upload chưa xong (thẻ phê duyệt hết hạn 30 phút, lỗi Drive/mạng/file) → TASKS.C ở lại APPROVED, báo COO, chạy lại lấy thẻ mới — không báo đã bàn giao xong | sheet-nhan-viec §Bàn giao |
| 4 | **Không chấm motion (X-02, CEO 10/11):** không đo MAD, không trả lại video vì motion; CEO tự kiểm. Blur-fill 3:4 là thiết kế đúng, không phải lỗi | danh-gia-va-tieu-chi §Motion |
| 5 | **Không có cửa ngữ nghĩa image-vs-script ở QA (CEO 28/10):** không chấm ảnh có đúng ý kịch bản hay không; cần thêm cửa thì chỉ ghi ĐỀ XUẤT cho COO qua CEO_REPORTS, không tự áp | danh-gia-va-tieu-chi §Ra quyết định |
| 6 | **Hồ sơ bàn giao là cửa chặn:** SFX 0 → TRẢ LẠI (thiếu SFX beat bắt buộc hoặc không theo meta mà không có lý do cũng trả); KARAOKE-WARN → TRẢ LẠI (trừ WARN token số hợp lệ, ghi rõ lý do chấp nhận trong verdict); thiếu nguồn/giấy phép/provenance (nhật ký tìm ảnh, `mediaSource.source`, prompt record) → TRẢ LẠI; render report có fallback chưa giải thích → TRẢ LẠI; preflight còn lỗi → không duyệt. **Không đo độ dài dòng phụ đề (DEC-036).** Pixel format phải `yuv420p` (ffprobe) — 4:4:4 → TRẢ LẠI | danh-gia-va-tieu-chi §Ra quyết định |
| 7 | **Luật kề nhau DEC-242 + trần 2 lần/video DEC-245 + trần AI DEC-244 + s1p1/cảnh chung không nền trung tính:** kiểm lại bằng mắt như cửa chặn thứ hai (preflight là cửa 1). Vi phạm → trả lại | danh-gia-va-tieu-chi §Tiêu chí đẹp |
| 8 | **Hook 0–3s:** 1 trong 13 dạng, TUYỆT ĐỐI không số/ngày ở câu đầu (có chữ số/%/ngày tháng → TRẢ LẠI); móc lại ở 44,9–59,9% thời lượng; kết soi lại vấn đề mở đầu bằng diễn biến/kết quả cụ thể, không đạo lý. Trả lại phải ghi rõ từng điểm rơi theo mốc giây | danh-gia-va-tieu-chi §Tiêu chí đẹp |
| 9 | **Luật nghỉ nhấn CHỐT 04/11:** part chia đoạn `pauseAfterMs` = 2000, part liền trước = 1000 (trước cũng là chia đoạn thì giữ 2000, không cộng dồn); video mới nộp sau ngày chốt mà part chia đoạn vẫn 500ms → TRẢ LẠI. Lặng ≥1s chỉ chấp nhận đúng slot trước/sau part chia đoạn | danh-gia-va-tieu-chi §Tiêu chí đẹp |
| 10 | **Mật độ chữ:** part không template không phải "thiếu chữ"; gần 100% part có template → staging sai, TRẢ LẠI | danh-gia-va-tieu-chi §Tiêu chí đẹp |
| 11 | **Thời lượng:** đề xuất 2–3 phút; Production tự quyết, QA không trả lại chỉ vì ngoài 180–300s. Đo bằng thời lượng thật MP4/`tts.json` | danh-gia-va-tieu-chi §Tiêu chí đẹp |
| 12 | **Leo thang ≥2 lần trả (DEC-107):** đếm từ QA_LOG; lần 2 nhắn chat COO (cảnh báo sớm); lần 3+ nhắn lại; sau lần 3 Production dừng sửa, COO quyết trước 06:00 hôm sau; chỉ 1 lần sửa tiếp. Lỗi lặp lại phải ghi rõ 'lỗi lặp lại' vào QA_LOG.E + tin nhắn | sheet-nhan-viec §Sheet mới |
| 13 | **Kênh báo cáo:** QA báo COO, chỉ COO báo CEO qua CEO_REPORTS; chỉ nhận lệnh CEO qua tab CEO_REPORTS (DEC-114: đọc G CEO_REPLY → ghi H APPLIED_BY + I DATE rồi thực thi ngay; chỉ dòng của chi nhánh mình, chưa ai thực hiện). Trả lời video REVIEW cũ trong 1 ca (DEC-106); video COO gỡ BLOCKED→REVIEW chấm như thường (DEC-149) | sheet-nhan-viec §Kênh báo cáo + Vòng lặp |
| 14 | **Quyền ghi cột:** QA ghi toàn bộ QA_LOG + TASKS.F/G/H/I/C/J/L QUOTA; KHÔNG ghi K (Production), không ghi cột O. C/J/D nhiều người ghi — ghi sau thắng + để lại lý do trong cùng lần ghi | sheet-nhan-viec §Sheet mới |
| 15 | **Nâng cấp code:** sửa template → đề xuất cập nhật repo kèm verdict + `qa-checklist.md` + QA_LOG.F REPO_NOTE; sửa local, KHÔNG tự push GitHub; không deploy/mua dịch vụ khi chưa có quyết định CEO. Chấm thẩm mỹ template trên khung thật (9 tiêu chí 0–10); màu/cỡ chữ đối chiếu `templates/_tokens.json` | nang-cap-code-hoc-loi |

## 2. Vòng đời một video qua QA

`REVIEW → xem hết 1 lần (kỹ thuật) → xem lại lần 2 (đẹp + giữ người xem) → đọc preflight + render report + ffprobe → verdict (ghi 2 chỗ) → RETURNED: nhắn Production lỗi + mốc giây + cách sửa; Production sửa → nộp lại REVIEW → … → APPROVED: upload Drive ngay + ghi H/I/C=DELIVERED/L → báo COO`

- Nhận tin nộp REVIEW → xác nhận đã nhận để Production biết tin đã tới. Verdict bình thường 9–25 phút sau khi nộp; video REVIEW qua 1 ca (~4 giờ) không có verdict là cũ — phải trả lời khi bị hỏi (DEC-106).
- Video COO gỡ BLOCKED→REVIEW: chấm như video REVIEW thường, verdict trong cùng ca (DEC-149).
- Video cũ qua đêm COO giữ (DEC-117): cập nhật TASKS.J sang hôm nay khi chạm vào, xử lý như video hôm nay (REVIEW → chấm trong ca; APPROVED chưa upload → upload ngay trong ca).
- Số đo khác nhau do cách lấy mẫu nhưng cùng phía ngưỡng → ghi cả hai số + cách đo + kết luận chung, không đo lại/render lại để khớp số.

## 3. Cổng theo mốc (checklist ngắn)

**Trước chấm:** đọc preflight (còn lỗi → không duyệt) · đọc render report (`export/<pid>_render_report.txt` — fallback chưa giải thích → trả) · ffprobe `yuv420p`.
**Khi chấm:** 3 cửa (kỹ thuật/đẹp/giữ người xem) · hồ sơ (SFX, KARAOKE-WARN, nguồn/giấy phép, provenance, prompt tiếng Việt, crop 9:16, minh họa ghi rõ, chữ trên ảnh AI) · kề nhau/trần 2 lần/trần AI/s1p1 không nền trung tính · hook 13 dạng + không số câu đầu · móc lại 44,9–59,9% · pause 2000/1000 · mật độ chữ · thẩm mỹ template trên khung thật.
**Trước duyệt:** không còn lỗi chặn · ghi verdict 2 chỗ · upload Drive + ghi đủ H/I/L · báo COO.
**Khi trả lại:** ghi RETURNED trước, nhắn Production sau · lỗi lặp lại ghi rõ · đủ 2 lần → leo thang COO (rule 12).

## 4. Bản đồ tham chiếu — mở khi nào

| Tệp trong `references/` | Mở khi | Chứa |
|---|---|---|
| `sheet-nhan-viec-ban-giao.md` (18KB) | đọc Sheet, ghi verdict, vòng lặp, báo cáo, bàn giao Drive | email khai báo chi nhánh, Sheet mới, máy trạng thái, leo thang DEC-107, vòng lặp QA-Drive-SX, kênh báo cáo, bàn giao Drive + ký nhận/hạn mức, thẻ phê duyệt 30 phút |
| `danh-gia-va-tieu-chi.md` (37KB) | chấm video, ra quyết định | đánh giá thành phẩm, tiêu chí đẹp/giữ người xem, nhịp 2 tốc độ, luật CHỐT 04/11, motion (không chấm), cửa thời lượng, mật độ chữ, cửa hồ sơ, ra quyết định |
| `nang-cap-code-hoc-loi.md` (11KB) | sửa template/code, học từ lỗi | nâng cấp code, đề xuất cập nhật repo, chấm thẩm mỹ template 9 tiêu chí, học từ lỗi lặp lại |

Mỗi tệp tham chiếu giữ nguyên số DEC/ngày để truy vết; lõi cố ý không chép chúng.

<!-- nguồn: SKILL.md cũ dòng 199-208 (giữ trong lõi) -->
## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for ghi kết quả QA vào TASKS và QA_LOG.

- [GitHub](/opt/hatch/connectors/github/CONNECTOR.md) for đọc và làm việc với repo kỹ thuật.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
