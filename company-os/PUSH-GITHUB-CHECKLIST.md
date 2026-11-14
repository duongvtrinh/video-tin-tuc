# Checklist đẩy lên repo GitHub `duongvtrinh/video-tin-tuc`

## Luật đứng (lệnh CEO tối 12/11/2026)

**LUÔN hỏi trước khi đẩy lên GitHub — không đẩy khi chưa thông báo và chưa được CEO duyệt.**
Mỗi lần đẩy: trình danh sách file + nội dung thay đổi + cách xử lý ghi chú local, chờ CEO bấm
duyệt, rồi mới đẩy. Luật này áp dụng cho mọi lần đẩy, kể cả đẩy "toàn bộ dự án".

## Quy tắc vệ sinh khi đẩy (repo dùng chung nhiều chi nhánh)

1. Mọi ghi chú đánh dấu là ghi chú riêng của một chi nhánh (ghi chú live của chi nhánh, ghi chú chỉ-bản-local, ghi chú bổ sung sau sự cố TOPIC-345) đều là nội dung CHỈ BẢN LOCAL — KHÔNG đẩy nguyên văn lên repo.
2. Email khai báo và mã chi nhánh của mỗi chi nhánh KHÔNG bao giờ xuất hiện trong file chung của repo (skill, spec, cron, doc) — repo cố ý không chứa giá trị riêng chi nhánh nào (§16 branch-memory). Trước khi đẩy, grep toàn bộ file sẽ đẩy để chắc không còn chuỗi email/mã chi nhánh của mình.
3. Nếu một thay đổi mang tính luật chung nhưng đang viết dưới dạng ghi chú local (vd luật lấy
   email từ MEMORY.md, cấm suy ra từ Sheet), thì khi đẩy phải viết lại dạng CHUNG, không kèm
   giá trị cụ thể của chi nhánh này.
4. **Học hỏi chéo — bài học đi kèm code (quyết CEO 14/11/2026):** mọi đợt đẩy đã duyệt mà thay đổi
   quy trình/code, nếu có bài học rút ra thì ghi bài học đó lên tab LEARNINGS (nguồn duy nhất)
   trước khi đẩy — không đẩy code mà quên chia sẻ bài học. Không còn file improvement-log.md
   (đã xóa 14/11/2026) và không còn mục IMP. **Luật lược email:** grep kiểm email/mã chi nhánh của mình = 0
   áp cho mọi file sẽ đẩy — không còn ngoại lệ nào (ngoại lệ duy nhất trước đây là
   improvement-log.md, đã xóa).

## Danh sách file sẽ đẩy (đợt sau khi CEO duyệt — kiểm lại bằng diff từng file với repo trước khi đẩy)

### Đẩy — luật v3.0, từ gói CEO gửi 12/11

- `vieneu-asset-factory/skills/SCRIPT_DOCTRINE.md` (MỚI)
- `vieneu-asset-factory/bin/script_lint.py` (MỚI)
- `vieneu-asset-factory/bin/preflight.py` (v3.0: luật ảnh cảnh chung/s1p1 + neutral-bg)
- `vieneu-asset-factory/PIPELINE.md` (v3.0: 2 chỗ + dòng script_lint.py)
- `vieneu-asset-factory/prompts/video_script_generate.txt`,
  `video_script_optimize.txt`, `video_script_outline.txt` (v3.0: viết lại)
- `company-os/media-search/LOGIC.md` (v3.0: mục 8 + sửa mục 1, 2, 4, 7)
- `company-os/qa-checklist.md` (v3.0: câu kết mới)
- `company-os/skills/media-video-production/SKILL.md` (v3.0 — PHẢI LƯỢC ghi chú mail chi
  nhánh trước khi đẩy)
- `company-os/skills/media-video-tech-qa/SKILL.md` (v3.0 — PHẢI LƯỢC ghi chú mail chi nhánh
  trước khi đẩy)

### Đẩy sau khi viết lại dạng chung (không kèm giá trị chi nhánh)

- Luật lấy email chi nhánh từ MEMORY.md + cấm suy ra từ Sheet → đưa vào skill
  Production/QA/Scout/COO dạng chung (mỗi chi nhánh tự đọc MEMORY.md của mình).
- Quy tắc REPORT_ID (DEC-264, thay DEC-121): luôn dùng email đầy đủ, bỏ mã BBB — cập nhật `google-sheet-spec.md` + `branch-memory.md` (cần CEO duyệt wording trước khi
  đẩy vì đây là spec chung).

### Không đẩy đợt này

- App `app-tao-video` (script-prompt.ts + test, lib.ts, handlers-projects.ts, projects.ts,
  ScriptTab 180s) — repo có thư mục app riêng, CHƯA đối chiếu; cần task đối chiếu riêng.
- `neutral-bg/` — đã có trên repo, không cần đẩy.
- 7 template nền rêu, 18 file engine Phase 1, `pronunciation_dict.csv` — đã khớp repo, không
  đổi.
- File backup, log, nhật ký ngày, file test (template-tests, kiem-chung-gd2) — không đẩy.

## Trình tự đẩy (sau khi CEO duyệt)

1. Diff từng file với repo (đọc trực tiếp đường dẫn/listing — `search_code` trên repo
   private trả 0 cho mọi truy vấn, không dùng để kết luận file vắng mặt).
2. Lược ghi chú local + grep kiểm email/mã chi nhánh của mình = 0 trong bộ file sẽ đẩy.
3. Đẩy qua `github push-files` (tối đa 2.000 file, 16 MiB/snapshot; file binary qua giao
   diện web).
4. Đọc lại repo xác minh từng file + ghi mã commit vào nhật ký ngày.
5. Báo CEO kết quả.
