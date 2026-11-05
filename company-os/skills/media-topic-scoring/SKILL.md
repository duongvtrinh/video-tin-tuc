# Chấm điểm chủ đề video

## Kiểm tra loại ngay

- Kiểm tra trùng lặp trong tab 06_Topics và loại ngay chủ đề cùng góc đã làm trong 90 ngày.

- Loại ngay chủ đề tin giả, chưa kiểm chứng hoặc không có nguồn đáng tin.

- Loại ngay chủ đề không dựng được thành video ngắn trong một ngày.

## Chấm điểm

- Chấm độ hot tối đa 30 điểm theo tốc độ lan truyền trong 24 đến 72 giờ.

- Chấm độ phù hợp khán giả tối đa 20 điểm theo tệp theo dõi và khả năng chia sẻ.

- Chấm tính mới tối đa 20 điểm theo góc riêng và mức độ chưa bị làm nát.

- Chấm khả thi sản xuất tối đa 15 điểm theo tư liệu, giọng đọc và công cụ dựng hiện có.

- Chấm độ rõ nguồn và khả năng kiểm chứng tối đa 15 điểm theo nguồn đã nêu, số liệu có đối chiếu được và mức độ tin cậy của nguồn (sửa 29/10/2026, code-fix: tiêu chí kiếm tiền/affiliate cũ đã bỏ vì phòng Kinh doanh đã giải thể và công ty này không làm affiliate/doanh thu).

## Ra quyết định

- Thang mới (sửa 29/10/2026, code-fix): hot 30 + phù hợp khán giả 20 + mới 20 + khả thi sản xuất 15 + rõ nguồn/kiểm chứng 15 = 100. Điểm đã công bố trước ngày sửa theo thang cũ giữ nguyên, không chấm lại (quy tắc không sửa điểm sau công bố); thang mới chỉ áp dụng cho chủ đề chấm từ 29/10/2026 trở đi.

- Ghi Approved khi tổng từ 70 điểm trở lên VÀ điểm quan tâm từ 30 trở lên, và ghi rõ góc làm. Điểm quan tâm = điểm Hot + điểm Khán giả (tối đa 50).

- Cổng duyệt thủ công (luật CEO 31/10/2026, sửa đợt A 01/11/2026): Approved chỉ có nghĩa là ĐỦ ĐIỀU KIỆN để CEO duyệt thủ công, chưa phải là lệnh dựng. Khi ghi chủ đề mới, Scout ghi cột O "Duyệt thủ công" = "Chờ duyệt"; chỉ CEO đổi cột này thành "Duyệt" VÀ chủ đề chưa có dòng `*-DRAFT` nào trong 01_Tasks thì ca pipeline mới giao dựng (sửa 05/11/2026, lựa chọn A3). Scoring không tự ghi "Duyệt" vào cột O và không giao việc dựng.

- Cửa tiên quyết về mức độ quan tâm (quy tắc CEO 29/10/2026): cửa này xét TRƯỚC tổng điểm — một chủ đề không ai quan tâm thì không vào sản xuất dù mới, khả thi và rõ nguồn tới đâu. Chủ đề tổng từ 70 trở lên nhưng điểm quan tâm dưới 30 thì ghi Hold, không phải Rejected, kèm tín hiệu chờ: "chờ tín hiệu quan tâm rõ hơn trong 24 giờ (tương tác mạng xã hội tăng hoặc độ phủ báo chí rộng hơn)". Quan tâm có thể tăng theo thời gian nên Hold là trạng thái chờ đúng nghĩa, không phải loại bỏ.

- Bằng chứng cho điểm quan tâm: điểm Hot và Khán giả phải có căn cứ là số liệu đã ghi trong Ghi chú của chủ đề — bằng chứng chính là tương tác mạng xã hội của bài công khai (lượt thích/bình luận/chia sẻ/lượt xem), bằng chứng hỗ trợ là nhiều báo chính thống cùng đưa tin trong ngày. Không chấm điểm quan tâm theo cảm giác; chủ đề chỉ có một bài báo đơn lẻ, không tương tác mạng xã hội và không có báo khác cùng đưa thì khó đạt cửa này.

- Không chấm lại các chủ đề đã công bố vì cửa này: đã kiểm chứng trên TOPIC-029 đến 052 — mọi chủ đề Approved đều có điểm quan tâm từ 30 trở lên (thấp nhất là TOPIC-041 đúng 30), nên cửa 30 không đổi kết quả nào đã công bố; cửa chỉ chặn các chủ đề tương lai có tổng cao nhưng ít người quan tâm.

- Ghi Hold khi tổng từ 50 đến 69 điểm, HOẶC tổng từ 70 trở lên nhưng điểm quan tâm (Hot + Khán giả) dưới 30, và ghi rõ tín hiệu cần chờ thêm trong 24 giờ.

- Ghi Rejected khi tổng dưới 50 điểm và ghi lý do bằng một dòng.

- Ghi Duplicate khi trùng và ghi ID chủ đề gốc.

## Giới hạn

- Không chấm chủ đề do chính mình quét trừ khi COO phân lại bằng văn bản trong Sheet.

- Không sửa điểm sau khi đã công bố kết quả trừ khi có dữ liệu mới và ghi rõ lý do sửa.

## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for chấm và ghi kết quả vào tab 06_Topics.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
