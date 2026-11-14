# Kế hoạch áp dụng gói "Kịch bản như người v3.0" (CEO gửi 16:35 12/11/2026)

Gói đã giải nén tại `~/workspace/company-os/kich-ban-nhu-nguoi-v3/kich-ban-nhu-nguoi/` (zip gốc: `~/workspace/user/files/kich-ban-nhu-nguoi-v3_0_f1ss.zip`). Tôi đã đọc hết: `DOC-TRUOC.md`, `PHAN-TICH-SKILL-KICH-BAN.md`, `thay-doi.patch` (toàn bộ), `SCRIPT_DOCTRINE.md`, `script_lint.py` (toàn bộ), và chạy thử `patch --dry-run` trên file live.

## 1. Gói này là gì

Hai thay đổi, độc lập nhau nhưng chung một đợt:

**A. Ảnh/video cho cảnh chung và part s1p1 (luật media mới, ghi là "quy tắc CEO 12/11/2026")**
- Cảnh mà MỌI part đã có ảnh/video riêng (kể cả cảnh chỉ có 1 part) → KHÔNG tìm/tạo ảnh cảnh chung; preflight không đòi.
- Cảnh có cả part có và part chưa có → lấy 1 ảnh/video của part đại diện làm ảnh cảnh chung (qua luật kề nhau DEC-242 + trần 2 lần/video DEC-245); không qua được thì xử lý như cảnh không có ảnh.
- Cảnh không part nào có ảnh/video riêng → BẮT BUỘC có ảnh/video cảnh chung, không để màn hình đen.
- Ảnh cảnh chung và part s1p1 (part đầu tiên của video) KHÔNG BAO GIỜ là nền trung tính (`neutral-bg/`) — phải là ảnh thật; preflight chặn bằng code (md5 trùng thư viện nền + nhật ký ghi `trung-tinh`).

**B. Câu mở đầu kịch bản (luật viết mới, ghi là "quy tắc CEO 12/11/2026")**
- Câu đầu tiên là 1 trong 13 dạng (tuyên bố sốc, câu hỏi dẫn dắt, câu hỏi đặt vấn đề, câu suy ngẫm, câu khẳng định mô tả cả nội dung, nghịch lý, hình ảnh lạ, lời nhân chứng, lời hứa bị phá, điều ai cũng tưởng, người xem trong tình huống, người trả giá, đính chính tin lan truyền), TUYỆT ĐỐI không số liệu, không ngày tháng. Số liệu/cảnh cụ thể dời xuống câu thứ 2.
- Kèm theo: học thuyết viết kịch bản (`SCRIPT_DOCTRINE.md` — voice card, 5 quyết định trước khi viết, vòng mở 20–25 giây, cấm theo LỚP chức năng C1–C9, bảng Trước/Sau, 3 bài rà tai), prompt app viết lại, 3 prompt Video Studio viết lại, công cụ kiểm tra cơ học mới `bin/script_lint.py` (chạy TRƯỚC TTS, exit 1 khi còn LỖI).

**File mới (3):** `vieneu-asset-factory/skills/SCRIPT_DOCTRINE.md`, `vieneu-asset-factory/bin/script_lint.py`, `PHAN-TICH-SKILL-KICH-BAN.md` (báo cáo phân tích, không phải file chạy).

**File sửa theo patch (11):** `app-tao-video/server/src/script-prompt.ts` + `script-prompt.test.ts`; `company-os/media-search/LOGIC.md` (mục 8 mới + sửa mục 1, 2, 4, 7); `company-os/qa-checklist.md`; `company-os/skills/media-video-production/SKILL.md` (6 hunk); `company-os/skills/media-video-tech-qa/SKILL.md`; `vieneu-asset-factory/PIPELINE.md`; `vieneu-asset-factory/bin/preflight.py`; `vieneu-asset-factory/prompts/video_script_{generate,optimize,outline}.txt`.

## 2. Sáu điểm cần CEO quyết TRƯỚC KHI làm

**2.1. 13 dạng hay chỉ 5 dạng?** Lệnh CEO 12/11 trong báo cáo phân tích ghi 5 dạng gốc (sốc / câu hỏi dẫn dắt / câu hỏi đặt vấn đề / suy ngẫm / khẳng định mô tả cả nội dung). Gói thêm 8 biến thể (dạng 6–13) với lý do "chủ đề nào cũng có cách mở hợp". Doctrine mục 3.1 ghi rõ dạng 1–5 là danh sách gốc của CEO, dạng 6–13 là biến thể thêm. Chốt: **giữ 13 hay cắt về đúng 5?** Nếu cắt về 5 thì phải sửa doctrine 3.1 + `script-prompt.ts` + test + 3 prompt (thêm việc, vẫn làm được trong đợt).

**2.2. Luật câu mở đầu THAY luật hook cũ ở câu đầu tiên — xác nhận rõ.** Luật live hiện hành (29/10 + 31/10): hook = cảnh/sự kiện cụ thể + xung đột + quy mô bằng con số, không câu hỏi tu từ rỗng. Luật mới: câu 1 KHÔNG số/ngày, con số dời xuống câu 2; câu 1 ĐƯỢC là câu hỏi (và đó là câu hỏi duy nhất của cả bài). Đây là đảo ngược một phần luật hook đã chốt. Doctrine §9 đã ghi cách hiểu thống nhất ("luật 12/11 thay luật cũ ở câu ĐẦU TIÊN; con số/cảnh cụ thể vẫn bắt buộc nhưng dời xuống câu thứ 2"), và patch sửa đúng các chỗ đó trong skill (mục "Câu mở đầu kịch bản", mục "Cấu trúc mở đầu"). Cần CEO xác nhận: **đồng ý thay ở câu đầu tiên, giữ nguyên từ câu 2 trở đi.**

**2.3. Câu kết trong skill QA — gói chưa sửa, thêm vào đợt này.** Patch giữ nguyên câu *"Kết video phải có kết luận rõ ràng và một câu chốt đáng nhớ, không kết lửng, không lặp lại mở đầu"* trong skill QA (và trong `qa-checklist.md`). Câu này mâu thuẫn với luật cấm kết luận đạo lý — chính báo cáo phân tích §7.2 đã chỉ ra và đề nghị sửa thành: *"Kết video phải soi lại vấn đề mở đầu bằng một diễn biến hoặc kết quả cụ thể và có một câu chốt cụ thể, ngắn; không kết lửng, không rút bài học, không lặp nguyên văn mở đầu."* Đề xuất: **sửa luôn 1 câu này ở 2 file** (QA skill + qa-checklist.md) trong đợt, vì không sửa thì Production viết đúng luật vẫn có thể bị QA trả lại.

**2.4. Đổi mặc định độ dài app 240 giây → 150–180 giây?** Báo cáo §7.3 khuyến nghị (mặc định 240s ≈ 1.000 tiếng trong khi khung đề xuất 2–3 phút ≈ 500–750 tiếng; dữ kiện mỏng + mục tiêu dài là nguồn độn chữ lớn nhất). Gói chưa làm (DOC-TRUOC không nhắc). Chốt: **đổi hay giữ 240s?** Chỉ đổi giá trị mặc định trong `ScriptTab.tsx`, không đổi luật độ dài.

**2.5. Ghi thay đổi ở đâu: local trước rồi push repo, hay sửa thẳng repo?** Theo quyết CEO 12/11, repo `video-tin-tuc` là chuẩn; push cần duyệt riêng. Đề xuất: **áp local → kiểm chứng đạt → push một đợt lên repo** (cần CEO bấm duyệt push riêng sau khi xem kết quả kiểm chứng). Lưu ý: gói ghi đường dẫn gốc `vieneu-media-company-main/` (tên repo cũ); repo live nay là `video-tin-tuc`.

**2.6. Ba file app chưa sửa — làm cùng đợt hay để sau?** `client/src/lib.ts` (dòng 169–170: cảnh nào thiếu `imageFile` là blocker), `server/src/priv/handlers-projects.ts`, `server/src/priv/projects.ts` vẫn đòi ảnh cảnh cho mọi cảnh. Đã kiểm chứng: `lib.ts` đúng là còn chặn ở tầng app. Muốn luật A chạy trọn trong app thì sửa 3 chỗ này theo điều kiện "cảnh còn part chưa có ảnh/video riêng". App sửa qua builder (không sửa trực tiếp source app). Chốt: **làm cùng đợt (qua builder) hay để sau?** Nếu để sau, luật A chỉ chạy đủ ở pipeline script; app vẫn đòi ảnh cảnh cho mọi cảnh.

## 3. Kiểm chứng patch trên file live (đã chạy `patch --dry-run` 16:xx 12/11, trên bản sao file live)

- **Áp sạch 9/11 file:** `script-prompt.ts` + test, `LOGIC.md`, `qa-checklist.md`, QA skill, `preflight.py`, 3 prompt `video_script_*.txt`.
- **Skill Production: 5/6 hunk áp được.** Hunk #1 (đoạn Preflight, dòng 66) fail — nguyên nhân đã xác định: dòng cần đổi giống hệt bản live (1.624 ký tự, đối chiếu từng ký tự), fail do các dòng ngữ cảnh xung quanh khác sau đợt hợp nhất Phase 1. Cách sửa: **sửa tay đúng 1 dòng đó** (thêm "[sửa 12/11/2026] lỗi này CHỈ áp cho cảnh còn ít nhất 1 part chưa có ảnh/video riêng…" + 2 lỗi chặn nền trung tính mới), kiểm chứng bằng grep.
- **PIPELINE.md: 2/2 hunk fail.** Bản live (bản repo sau Phase 1) viết ngắn hơn ở cả 2 chỗ: dòng `preflight.py` trong bảng Scripts chỉ ghi "checklist trước xuất: audio/ảnh/karaoke/template inputs/BGM" (không có đoạn SFX/PIL dài như patch base), và đoạn `runPreflight` cũng khác wording. Cách sửa: **sửa tay 2 chỗ theo đúng ý nghĩa patch** (thêm luật 12/11 vào bảng + đoạn runPreflight), kiểm chứng bằng đọc lại.
- **File mới:** copy `SCRIPT_DOCTRINE.md` → `vieneu-asset-factory/skills/`, `script_lint.py` → `vieneu-asset-factory/bin/` (chmod +x, `py_compile` đạt).

## 4. Các bước thực hiện (sau khi CEO duyệt kế hoạch + chốt mục 2)

**GĐ 0 — Backup (như Phase 1).** Sao lưu toàn bộ 11 file đích + 2 skill + `PIPELINE.md` + định nghĩa cron liên quan (không đổi cron đợt này) vào `~/workspace/backups/kich-ban-v3-20261112/` kèm checksum. Không ghi workbook, không chạm lịch bot.

**GĐ 1 — Áp thay đổi.**
1. Áp patch cho 9 file sạch (`patch -p1`, kiểm chứng 0 hunk fail).
2. Sửa tay 3 chỗ fail (Production skill hunk #1; PIPELINE.md 2 chỗ) + sửa câu kết QA ở 2 file (mục 2.3).
3. Copy 2 file mới (doctrine + lint). Nếu CEO chốt mục 2.1 = chỉ 5 dạng thì sửa doctrine 3.1 + prompt + test + 3 prompt trước khi áp.
4. Kiểm chứng: `patch --dry-run` lại đạt 100%; grep các chuỗi khóa (13 dạng / 5 dạng, "TUYỆT ĐỐI không có số liệu", "s1p1", "neutral-bg", "script_lint" trong skill + PIPELINE); `py_compile` đạt `script_lint.py` + `preflight.py`.

**GĐ 2 — Kiểm chứng code trên dữ liệu thật (chưa chạy mô hình, chưa dựng video mới).**
1. `script_lint.py`: chạy lên 3–5 kịch bản thật đã QA duyệt (vd TOPIC-274, 271, 265, 251, 250) — kỳ vọng ĐẠT hoặc chỉ CẢNH BÁO nhẹ; hiệu chỉnh ngưỡng nhịp R1 (cv ≥ 0,45) / R2 (câu ngắn ≥ 12%) nếu kịch bản đã duyệt mà lint báo sai hàng loạt (báo cáo §6: ngưỡng hiện chỉ hiệu chỉnh từ 2 fixture, là heuristic). Chạy thêm 1 kịch bản cố tình vi phạm (câu đầu có số, "Không chỉ… mà còn…", 2 câu hỏi) — phải ra LỖI K3/C1/C2/Q1 và exit 1.
2. `preflight.py` mới: chạy trên project test — (a) cảnh mà mọi part đã có file riêng → KHÔNG đòi ảnh cảnh chung; (b) cảnh còn part chưa có file riêng mà thiếu ảnh cảnh chung → chặn exit 1; (c) s1p1 dùng nền trung tính → chặn; (d) ảnh cảnh chung trùng md5 thư viện `neutral-bg/` → chặn. Dùng project test hiện có, không dùng chủ đề live.
3. `script-prompt.test.ts`: chạy `bun test` sau khi áp patch (qua builder, xem GĐ 3).

**GĐ 3 — App (qua builder, không sửa trực tiếp source).**
1. Áp `script-prompt.ts` + test qua `artifact.edit`, chạy `bun test server/src/script-prompt.test.ts` đạt.
2. Nếu CEO chốt mục 2.6 = làm cùng đợt: builder sửa 3 file app (lib.ts, handlers-projects.ts, projects.ts) theo điều kiện "cảnh còn part chưa có ảnh/video riêng", kiểm chứng trong app (mở project test, cảnh đủ part riêng không còn bị chặn thiếu ảnh cảnh).
3. Nếu CEO chốt mục 2.4 = đổi mặc định: đổi `ScriptTab.tsx` 240 → 150–180 giây trong cùng lần builder.

**GĐ 4 — Thử nghiệm A/B (theo báo cáo §7.1 — cách duy nhất biết "giữ chân" có tốt hơn không).**
Cùng dữ kiện, 3–5 chủ đề thật: một bản prompt cũ, một bản mới; chạy lint cả hai; đưa cả hai vào QA mù. Sau khi đăng, so tỷ lệ còn xem ở giây 3, giây 15 và thời gian xem trung bình. Chỉ kết luận sau khi có số liệu; không tuyên bố cải tiến chỉ vì lint đạt.

**GĐ 5 — Ghi chép + push repo (push cần duyệt riêng).**
Ghi nhật ký ngày (bài học rút ra thì ghi lên tab LEARNINGS) + cập nhật `TEMPLATE_VERSIONS.md` nếu liên quan (không); push các file đổi lên `video-tin-tuc` sau khi CEO bấm duyệt push. Không push file test, không push `app.db`.

## 5. Rủi ro / giới hạn — nói thẳng (từ báo cáo §6)

- **Chưa chạy prompt mới qua mô hình thật của app** nên chưa biết văn thật ra sao. Bản `script_human.txt` trong phân tích là viết tay theo học thuyết; bản `script_ai.txt` là văn mô phỏng, không phải đầu ra thật của prompt cũ.
- **Ngưỡng nhịp câu là heuristic** (hiệu chỉnh từ đúng 2 fixture). Cần chạy lint lên vài kịch bản thật đã duyệt để chỉnh lại (GĐ 2.1).
- **Lint không đo "hay".** Kịch bản qua lint vẫn có thể nhạt; kịch bản bị cảnh báo vẫn có thể ổn. Lint chặn lỗi cơ học; rà tai và đối chiếu nguồn vẫn là việc của người viết.
- **Prompt dài gấp ~3 lần.** Có rủi ro mô hình chép ví dụ trong prompt (vd cầu X); đã có dòng cấm chép, nhưng cần quan sát vài lần chạy đầu.
- **13 dạng phải xoay giữa các video liên tiếp** — mở bằng cùng một khuôn nhiều video liền là dấu hiệu "mùi AI" mới (doctrine 3.1).
- **Chỉ áp cho video mới.** Video đã duyệt không làm lại chỉ vì đổi luật viết.

## 6. Việc KHÔNG làm trong đợt này

- Không sửa app Cách A ngoài `script-prompt.ts` (trừ khi CEO chốt mục 2.4/2.6).
- Không làm mục 7.4 của báo cáo (lint sau khi sinh + 1 lượt viết lại trong `generateScriptAI` — cần sửa `actions.ts`, chưa có cách test lời gọi inference).
- Không đổi luật CEO nào khác; mọi luật cũ (giọng 29/10, luận điểm 30/10, ký hiệu 30/10, 3 nhịp 31/10, đa nguồn 03/11, nghỉ nhấn 04/11) giữ nguyên — chỉ thêm cách làm và thay luật hook ở câu đầu tiên (mục 2.2).
- Không push GitHub khi chưa duyệt riêng. Không chạm cron, workbook, chat nhân viên.

## 7. Thứ tự duyệt

1. CEO đọc kế hoạch này, chốt 6 điểm ở mục 2 (nhất là **2.1: 13 hay 5 dạng** và **2.6: có sửa 3 file app luôn không**).
2. Tôi làm GĐ 0–2, báo kết quả kiểm chứng (lint + preflight trên dữ liệu thật).
3. GĐ 3 (app qua builder) → GĐ 4 (A/B) → GĐ 5 (ghi chép + push, duyệt riêng).
