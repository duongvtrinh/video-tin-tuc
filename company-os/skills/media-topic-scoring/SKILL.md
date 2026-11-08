# RETIRED — Skill chấm điểm chủ đề (media-topic-scoring)

**Trạng thái: NGỪNG HOẠT ĐỘNG từ 07/11/2026 theo quyết định CEO C3 (gộp Scout + Scoring). File skill gốc `~/workspace/custom-skills/media-topic-scoring/SKILL.md` KHÔNG bị xoá — chỉ ngừng dùng. File này chỉ để ghi lại quyết định, không phải skill vận hành.**

## Đã xảy ra

- Chat Scoring đã ĐÓNG. Không còn agent Scoring riêng, không còn hàng đợi Pending Scoring, không còn tin nhắn Scout → Scoring.
- Việc chấm điểm đã gộp vào mỗi phòng Scout (Báo và Group tách riêng): mỗi phòng tự chấm chủ đề của mình trong cùng lượt quét, ghi dòng TOPICS đã có điểm + STATUS trong một lần ghi.
- Công thức chấm (HOT 30 + AUDIENCE 20 + FRESH 20 + FEASIBLE 15 + SOURCED 15 = 100; APPROVED khi tổng ≥70 VÀ điểm quan tâm HOT+AUDIENCE ≥30; HOLD khi tổng 50–69 hoặc quan tâm <30; REJECTED khi tổng <50; DUPLICATE ghi ID gốc) đã chuyển nguyên vẹn sang skill `media-scout` (mục "Ghi chủ đề + chấm trong cùng lượt"). Mọi quy tắc chấm (bằng chứng điểm quan tâm bằng số liệu trong NOTES, không sửa điểm sau công bố, HOLD → APPROVED chỉ khi COO ra lệnh chấm lại bằng văn bản) nay sống ở đó.
- Cổng READY của CEO không đổi: APPROVED chỉ là đủ điều kiện; chỉ CEO flip TOPICS.STATUS APPROVED → READY mới mở cổng dựng.
- Lớp kiểm "không chấm chủ đề do mình quét" đã mất theo quyết định gộp; bù bằng: điểm quan tâm bắt buộc có số liệu bằng chứng trong NOTES + cổng READY của CEO + hoc-hoi kiểm mẫu chấm.

## Hàng đợi Pending Scoring cũ

- 10 chủ đề Pending Scoring trên Sheet cũ (tính đến sáng 07/11/2026) đã được 2 phòng Scout chấm xong trong ca 10:00 07/11/2026 (tất cả APPROVED, quyết R4-07 C) — hàng đợi đã hết, không còn việc chờ chấm.

## Không dùng file này để làm gì

- Không chấm điểm theo file này nữa. Agent nào cần chấm điểm thì đọc skill `media-scout`.
- Không xoá file skill gốc `media-topic-scoring/SKILL.md` (giữ làm lịch sử; quyết định khôi phục Scoring — nếu CEO ra lệnh sau này — sẽ mở lại từ file gốc đó).
