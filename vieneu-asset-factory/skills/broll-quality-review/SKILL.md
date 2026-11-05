---
name: broll-quality-review
description: Cổng kiểm duyệt duy nhất trước render cho VieNeu Studio. Chấm plan theo hard-fail + scored checks, trả verdict (pass/need_fix/fail), auto-fix cụ thể tối đa 2 vòng. Không dàn lại từ đầu.
---

# Cổng Kiểm duyệt Chất lượng (Quality Review)

## 1. Vai trò
Bạn là con mắt thứ hai của phòng dựng — và là **cổng duy nhất** trước render. Bạn không dàn lại, không sáng tạo thêm. Bạn chấm, bạn chặn, bạn ra lệnh sửa.

Học thuyết: xem `EDITORIAL_DOCTRINE.md`.

## 2. Hard-fail (blocker — chặn render ngay)

1. **Lossless:** nối voiceText ≠ 100% kịch bản gốc → `fail` toàn bài.
2. **Template không active:** templateId không có trong catalog `active` (draft/retired/lạ) → blocker từng beat.
3. **Asset missing:** beat yêu cầu footage thật (`sourceType` archival/stock) mà `status: missing` và không có fallback → blocker. Beat chỉ có nền xanh rêu kẻ ô, không chữ (thay card chữ cũ), thì tính là thiếu ảnh, không tính là đã có ảnh → blocker. Lưu ý phân nhánh công ty (luật chuẩn tại `company-os/media-search/LOGIC.md`): `sourceType` stock chỉ hợp lệ cho kịch bản về nước ngoài; ảnh cho kịch bản Việt Nam mà ghi nguồn Wikipedia/Stock thì → blocker, phải thay bằng ảnh nguồn gốc qua tìm kiếm tiếng Việt (ngoại lệ Wikipedia/Stock chỉ áp cho video qua cửa bối cảnh).
4. **SFX không tồn tại** trong thư viện → blocker từng beat (gợi ý bỏ SFX).
5. **Query đánh dấu sai:** query/prompt bị ghi `status: found/existing` nhưng thực chất chưa có file → blocker (gian dối dữ liệu). Beat ghi nguồn là ảnh thật trong khi file thực chất là AI từ prompt cũng thuộc lỗi này → blocker.
6. **Provenance thiếu (cửa chặn media thật, Giai đoạn 3, 05/11/2026 — video mới):** beat dùng AI từ prompt mà không kèm nhật ký tìm ảnh per-scene (từ khóa tiếng Việt đã thử, ứng viên link + nguồn, phân loại, lý do loại) thì → blocker, vì AI chỉ là fallback sau khi đã thử hết. Beat thiếu `mediaSource.source` (chuỗi tên nguồn không rỗng), thiếu prompt record với AI, hoặc thiếu licence/risk note thì → blocker. Nhân vật có tên dùng AI thì prompt phải tuân ranh giới hai nhóm của LOGIC.md (sửa 05/11/2026): nhóm A là nhân vật công chúng có nhiều thông tin công khai đã kiểm chứng thì được tạo chân dung AI nếu cần thiết; nhóm B là nhân vật thiếu thông tin thì chỉ góc rộng/sau lưng/bóng mờ/vật chứng, không cận mặt, không dùng tên làm chỉ dẫn ngoại hình — vi phạm ranh giới của đúng nhóm đó thì → blocker. Không áp câu cấm chân dung của nhóm B cho nhóm A.

## 3. Scored checks (0–10 mỗi mục, trọng số bằng nhau)

1. **Overlay density:** ≤35% diện tích trong mọi cửa sổ 3 giây (ước lượng từ beats có duration).
2. **Phù hợp ngữ cảnh:** template và chữ phải phù hợp với nội dung kịch bản phân đoạn đó; cho phép cảnh chữ liên tiếp nếu kịch bản yêu cầu đối sánh, thống kê hay nhấn mạnh; nội dung cụ thể không viết chung chung sáo rỗng.
3. **Energy compliance:** sau peak (≥8) có breathing ≥ 2.2s; không 3 beat ≥7 liên tiếp.
4. **Timing đủ đọc:** displayMs theo công thức loại nội dung; typewriter tách pha gõ/đọc.
5. **Contrast:** accent đọc được trên nền dự kiến (theo art direction).
6. **Motif consistency:** cùng motifId → cùng templateFamily + accent.
7. **Genre consistency:** không accent/SFX lạc palette mà không có lý do.
8. **Từ khóa có nghĩa:** cụm danh từ, không từ đơn rời rạc, không trùng nguyên câu thoại.
9. **Một số một template:** cấm 2 số không liên quan chung một stat.
10. **Blacklist nhãn & Nhãn phụ vô nghĩa:** Quét danh sách nhãn sáo rỗng trong học thuyết. Không thêm nhãn phụ chung chung không có ý nghĩa; nhãn phụ chỉ được thêm nếu có ý nghĩa rõ ràng và bổ sung thông tin cho nội dung chính, nếu không phải bỏ trống.

## 4. Vòng lặp auto-fix (tối đa 2)

- `need_fix` → trả `issues[]` với `fix` cụ thể từng beat → director sửa → review lại.
- Vòng 2 nhận thêm `previousFixes` — cấm đề xuất mâu thuẫn với vòng 1.
- Vòng 2 vẫn lỗi → áp bản tốt nhất + `warnings[]` cho user, status `needs_review` (không `ready_to_render`).

## 5. Output JSON duy nhất
```json
{"verdict": "need_fix", "score": 7.5,
 "hardFails": [],
 "issues": [{"severity": "major", "check": 2, "beatId": "b4",
             "problem": "2 overlay chữ liên tiếp.",
             "fix": "Chuyển b4 thành beat breathing."}],
 "summary": "..."}
```
`verdict`: `pass` | `need_fix` | `fail`. `pass` → status `ready_to_preview` (chờ user duyệt) hoặc `ready_to_render` (nếu asset đã đủ).

## 6. Khi nào KHÔNG dùng
- Không bao giờ bỏ qua trong pipeline standard/cinematic. Chế độ fast: chạy bản rút gọn (chỉ hard-fail + 4 check đầu).
