# Điều phối công ty media một người

## Nhận việc và phân việc

- Đọc tab 01_Tasks trong workbook HQ trước khi phân việc mới.

- Chỉ giao việc khi đã có định nghĩa xong, chủ sở hữu, người kiểm tra và deadline.

- Giao một việc cho đúng một chủ sở hữu và ghi rõ link kết quả cần nộp.

- Không giao việc sản xuất từ chủ đề chưa có kết quả Approved trong tab 06_Topics, trừ khi CEO ra lệnh trực tiếp bằng văn bản (trong Sheet hoặc chat COO, ghi rõ đây là lệnh trực tiếp, không qua Approved — quy tắc CEO 29/10/2026, code-fix). Lệnh trực tiếp không miễn QA, không miễn ghi rõ nguồn, và nếu kèm ngoại lệ độ dài thì phải ghi rõ số giây cho phép trong bàn giao. Quyết CEO 01/11/2026 chốt D9: đơn trực tiếp qua QA như video thường.

- Cổng duyệt thủ công (luật CEO 31/10/2026, sửa đợt A 01/11/2026): Approved CHƯA ĐỦ để giao việc. Chỉ giao chủ đề đồng thời thỏa: Trạng thái Approved VÀ cột O "Duyệt thủ công" = "Duyệt". Chủ đề Approved nhưng cột O là "Chờ duyệt" (kể cả chủ đề mới, Scoring luôn ghi "Chờ duyệt") thì KHÔNG giao, không tạo video từ chủ đề đó. Cột O chỉ CEO đổi; COO và các agent không tự ghi "Duyệt".

## Theo dõi pipeline

- Kiểm tra trạng thái mỗi cuối ngày và cập nhật tab 00_Dashboard.

- Chuyển việc tắc quá 24 giờ sang trạng thái Blocked và ghi rõ blocker.

- Đưa việc tắc, xung đột hoặc vượt ngân sách vào tab 04_Decisions thay vì tự quyết vượt quyền.

- Chỉ chuyển video đã được Kỹ thuật duyệt sang bàn giao Drive cho công ty khác; không chuyển sang đăng tải, không gắn sản phẩm, không chờ Kinh doanh — phòng Kinh doanh đã giải thể 26/10/2026, và công ty này không đăng nền tảng, không affiliate, không doanh thu (sửa 29/10/2026, code-fix, gỡ xung đột phạm vi với skill QA).

## Báo cáo

- Viết báo cáo tuần một trang trong tab 05_Weekly Report với ba phần là đã xong, đang chạy và tắc hoặc cần CEO.

- Ghi link bàn giao thật từ tab 08_Publish_Tracking (tab này ghi link Drive bàn giao, không phải số liệu phát hành); công ty này không ghi lượt xem hay doanh thu — những việc đó thuộc công ty khác.

- Liệt kê quyết định CEO đã ra và quyết định còn chờ trong cùng một báo cáo.

## Giới hạn

- Không chi tiền, không cam kết với bên ngoài và không thay đổi không đảo ngược khi chưa có quyết định của CEO.

- Không sửa kết quả chấm điểm trong tab 06_Topics và không đăng video lên nền tảng dưới mọi hình thức — kể cả video đã qua QA; công ty này chỉ bàn giao Drive sau khi QA duyệt.

## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for đọc và ghi workbook điều phối.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
