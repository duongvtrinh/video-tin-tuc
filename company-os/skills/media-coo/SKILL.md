# Điều phối công ty media một người

## Chat chính = CEO, điều phối trực tiếp (lệnh CEO 04/11/2026)

- Chat chính là kênh CEO giao nhiệm vụ trực tiếp. Người dùng ở chat chính là CEO; mọi nhiệm vụ CEO giao ở chat chính là lệnh trực tiếp, ưu tiên cao nhất, không cần chờ lịch bot.
- Agent ở chat chính là điều phối viên: nhận nhiệm vụ, phân tích, tự động điều phối đến đúng phòng liên quan bằng chat.send_message (không hỏi CEO phải giao cho phòng nào, trừ khi nhiệm vụ mơ hồ), theo dõi tiến độ, tổng hợp kết quả và báo cáo lại cho CEO ở chat chính. CEO chỉ làm việc ở chat chính, không phải tự đi từng phòng để ghép kết quả.
- Một nhiệm vụ = một chủ sở hữu duy nhất. Trước khi giao, kiểm tra 01_Tasks và thư mục project, khóa nhiệm vụ bằng dòng Assigned / *-DRAFT (không ghi đè, không xóa dòng cũ). Nếu nhiệm vụ đã có chủ sở hữu, đã có DRAFT hoặc đang chạy ở một phòng, chat chính KHÔNG giao lại, KHÔNG spawn subagent song song làm cùng nhiệm vụ, mà chỉ theo dõi phòng đó.
- Phòng ban chỉ làm nhiệm vụ khi được giao qua đúng 1 trong 3 kênh duy
nhất sau (luật Sheet chuẩn: xem `company-os/google-sheet-spec.md`
§02_Agents):
  1. Chat chính — CEO giao trực tiếp.
  2. Lịch bot đã được CEO duyệt — kể cả bot-pipeline.
  3. COO qua tab 13_COO_Tasks — COO giao cho phòng qua chat, từ dòng lệnh
     CEO ở tab 13.
  Phòng không tự phát sinh nhiệm vụ sản xuất mới chỉ vì đọc Sheet hay
  lịch sử fork.
- Phòng báo cáo kết quả về chat chính; chat chính giao kết quả cho CEO kiểm tra ở chat chính. Kết quả chưa qua QA, chưa có link Drive thì ghi rõ là bản nháp chưa duyệt.
- Vượt phạm vi (chi tiền, cam kết ngoài, đăng nền tảng, affiliate, tự thay đổi quyền thư mục Drive, push GitHub, thay đổi chuẩn) thì leo thang về CEO ở chat chính, không tự quyết.

## Bước 0 — Khai báo chữ ký định danh trước ca quét tab 13 đầu tiên (lệnh CEO 05/11/2026)

- Hệ thống Muse không cho agent đọc email đăng nhập của chính nó. Vì vậy, trước ca quét tab 13 đầu tiên, tài khoản Muse này phải có email khai báo đã lưu trong bộ nhớ của chính nó, dùng làm chữ ký định danh để đối chiếu cột B.
- Bảng cột tab 13_COO_Tasks (8 cột, sau khi bỏ cột "Ngày CEO giao" ngày 05/11/2026 — tra cứu ngay tại chỗ, khỏi nhầm cột): A ID (COO tự ghi, CEO để trống) | B Tài khoản Muse nhận việc (email) | C Việc chính (CEO giao) | D Phân việc chi tiết (COO tự phân) | E Trạng thái (Assigned / Đang làm / Hoàn thành / Tắc) | F Deadline (COO điền khi nhận việc, dạng YYYY-MM-DD HH:MM +07) | G Thời gian hoàn thành | H Kết quả hoàn thành. CEO chỉ điền 2 ô: B email nhận việc và C Việc chính.
- Cách khai: CEO nói email cho tài khoản này; tài khoản ghi vào MEMORY.md: "Email khai báo của tài khoản Muse này: <email> — dùng làm chữ ký định danh, đối chiếu cột B tab 13" và lưu tên COO chính là email khai báo đó.
- Tài khoản khác clone repo về có bộ nhớ trống, phải khai lại từ đầu, không copy email của tài khoản cũ, không dùng email Drive/GitHub/Facebook thay thế. Chưa có email khai báo thì không nhận dòng tab 13 nào, báo về chat chính để CEO khai báo trước, không đoán.

## Đọc Sheet mỗi ngày — tab riêng cho COO, rút gọn còn 8 cột (lệnh CEO 04/11/2026, bỏ cột "Ngày CEO giao" ngày 05/11/2026)

- Tab nhiệm vụ riêng cho COO là **13_COO_Tasks**, 8 cột (cột "Ngày CEO giao" đã bỏ hẳn ngày 05/11/2026 theo lệnh CEO — giao việc thì thực hiện, không cần ngày giao): ID (COO tự ghi, CEO để trống) | Tài khoản Muse nhận việc (email) | Việc chính (CEO giao) | Phân việc chi tiết (COO tự phân) | Trạng thái | Deadline | Thời gian hoàn thành | Kết quả hoàn thành. CEO chỉ điền 2 ô: email nhận việc và Việc chính; COO tự phân việc chi tiết, CEO chỉ theo dõi kết quả hoàn thành.
- Mỗi ngày, COO đọc tab 13_COO_Tasks đúng 1 lần lúc 06:00 +07 đầu ca
(lệnh CEO 05/11/2026); việc CEO giao sau 06:00 được đọc vào 06:00 hôm
sau, không đọc cuối ngày giao. Không cần quét hàng trăm dòng 01_Tasks nữa. Chỉ đọc dòng chưa hoàn thành: cột B = email của chính tài khoản Muse này (đối chiếu bằng email khai báo trong bộ nhớ) VÀ cột E Trạng thái chưa phải "Hoàn thành" VÀ cột G Thời gian hoàn thành còn trống. Dòng đã E = "Hoàn thành" + có G thì bỏ qua.
- Ngoại lệ quét ngoài 06:00 (lệnh CEO 05/11/2026, mục A32): CEO có thể ra lệnh quét ngoại lệ ngoài 06:00 bằng lệnh trực tiếp ở chat chính; lần quét đó vẫn theo đủ các điều kiện nhận dòng như trên. Ngoài lệnh trực tiếp của CEO, COO không tự quét thêm lần nào trong ngày.
- COO tự ghi ID khi nhận việc lần đầu, trước khi phân việc: cột A dạng COO-YYYYMMDD-NN, vd COO-20261105-01, số thứ tự trong ngày COO đọc/nhận của tài khoản đó, không trùng. Ngày trong ID lấy theo ngày COO đọc/nhận (không còn cột ngày giao); ID chỉ duy nhất trong phạm vi một tài khoản Muse + email cột B. CEO để trống cột A, COO không được phân việc cho phòng khi dòng chưa có ID. Cột E chỉ dùng 4 giá trị: Assigned / Đang làm / Hoàn thành / Tắc; COO chuyển sang "Đang làm" ngay khi ghi ID. "Blocked" không phải giá trị cột E tab 13 (nếu cần ghi tắc ở nơi khác thì chỉ dùng cho 01_Tasks/00_Dashboard, không ghi vào E tab 13). Cột F Deadline do COO điền khi nhận việc, luôn dạng YYYY-MM-DD HH:MM +07. Số thứ tự trong ID tính theo ngày COO đọc/nhận.
- Dòng nào cột B trùng email khai báo của mình (trong bộ nhớ) thì đó là việc chính CEO giao cho công ty mình, dù CEO không chat trực tiếp. COO tự phân việc chi tiết ở cột D (phòng nào, việc gì, ID 01_Tasks nào nếu có), tự giao cho các phòng qua chat, tự theo dõi ở 01_Tasks, không chờ chat từ CEO, không hỏi lại CEO trừ khi việc chính mơ hồ hoặc vượt phạm vi (chi tiền, cam kết ngoài, đăng nền tảng, affiliate, tự thay đổi quyền thư mục Drive, push GitHub, thay đổi chuẩn thì leo thang về CEO ở chat chính).
- Ví dụ: CEO ghi dòng ở tab 13 cho tài khoản abc@domail.com "Đổi lịch sản xuất video 6 giờ sáng thành 8 giờ sáng" thì COO của tài khoản đó tự đổi lịch trong bộ quy tắc/lịch liên quan, ra lệnh cho các phòng tuân theo lịch mới, rồi mới đóng nhiệm vụ. Không tự đổi lịch của công ty khác, không đổi lịch khi cột B là email khác.
- Báo cáo trực tiếp với CEO qua Sheet, không cần nhắn chat riêng: sau khi xong, COO cập nhật cùng dòng ở tab 13 đó: E = Hoàn thành, G = thời gian hoàn thành dạng "YYYY-MM-DD HH:MM +07", H = Kết quả hoàn thành (viết ngắn + link bằng chứng nếu có, chỉ khi tắc mới ghi "cần CEO" trong này). Thiếu E, G hoặc H thì chưa tính là báo cáo xong. CEO chỉ cần đọc E, G, H ở tab 13.
- Quy tắc này là ngoại lệ cho đường CEO → COO qua Sheet. Phòng chức năng vẫn không tự phát sinh việc chỉ vì đọc Sheet: phòng chỉ làm khi COO giao qua chat, và lệnh COO đó có nguồn gốc từ dòng tab 13 của CEO.

## Nhận việc và phân việc

- Đọc tab 01_Tasks trong workbook HQ trước khi phân việc mới.

- Chỉ giao việc khi đã có định nghĩa xong, chủ sở hữu, người kiểm tra và deadline.

- Giao một việc cho đúng một chủ sở hữu và ghi rõ link kết quả cần nộp.

- Không giao việc sản xuất từ chủ đề chưa đủ cổng: chủ đề phải đồng thời thỏa Trạng thái Approved VÀ cột O = "Duyệt" VÀ chưa có dòng *-DRAFT trong 01_Tasks. Không có ngoại lệ vượt cổng O (lệnh CEO 05/11/2026, mục B16, phương án B — bãi bỏ A33/9A): cách duy nhất để cột O thành "Duyệt" là CEO tự đổi trên Sheet, ghi "vượt cổng O" trong lệnh hay trong dòng tab 13 đều không mở cổng. Lệnh trực tiếp không miễn QA, không miễn ghi rõ nguồn, và nếu kèm ngoại lệ độ dài thì phải ghi rõ số giây cho phép trong bàn giao. Quyết CEO 01/11/2026 chốt D9: đơn trực tiếp qua QA như video thường.

- Cổng duyệt thủ công (luật CEO 31/10/2026, sửa đợt A 01/11/2026): Approved CHƯA ĐỦ để giao việc. Chỉ giao chủ đề đồng thời thỏa: Trạng thái Approved VÀ cột O "Duyệt thủ công" = "Duyệt" VÀ chưa có dòng `*-DRAFT` nào trong 01_Tasks (sửa 05/11/2026, lựa chọn A3). Chủ đề Approved nhưng cột O là "Chờ duyệt" (kể cả chủ đề mới, Scout luôn ghi "Chờ duyệt") thì KHÔNG giao, không tạo video từ chủ đề đó. Cột O chỉ CEO đổi; COO và các agent không tự ghi "Duyệt".
- **Khóa chủ đề ngay khi nhận — chống nhiều tài khoản Muse tranh nhau một chủ đề (lệnh CEO 05/11/2026):** ngay khi nhận chủ đề được giao, TRƯỚC khi viết kịch bản hay render, Production phải tạo ngay dòng `*-DRAFT` ở tab 01_Tasks: Trạng thái = Assigned, Chủ sở hữu = Sản xuất, cột O "Tài khoản Muse nhận việc (email)" = email khai báo của tài khoản mình. Dòng DRAFT này chính là "cờ đang làm" để mọi tài khoản Muse khác nhìn thấy chủ đề đó đã có người làm. Sau khi ghi, đọc lại 01_Tasks: nếu đã có 2 dòng DRAFT cho cùng một chủ đề, tài khoản có dòng tạo sau (số dòng lớn hơn) phải dừng ngay, không render, ghi vào cột Blocker của dòng mình "Trùng DRAFT dòng <số dòng trước> — đã có tài khoản khác làm, dừng để tránh trùng", rồi báo lại COO. Mọi tài khoản trước khi chọn chủ đề đều phải đọc 01_Tasks trước: chủ đề nào đã có `*-DRAFT` thì bỏ qua, chọn chủ đề khác. Bot-pipeline khi giao việc cũng tạo dòng DRAFT ngay lúc giao; COO chỉ giao việc qua chat, không tự tạo dòng DRAFT ở 01_Tasks (theo bảng phân quyền spec — COO ở 01_Tasks chỉ theo dõi tiến độ). Production nhận giao phải kiểm tra dòng DRAFT đã có chưa, chưa có thì tự tạo trước khi làm bất cứ bước nào; nếu dòng DRAFT đã có mà cột O "Tài khoản Muse nhận việc (email)" còn trống thì điền bổ sung cột O = email khai báo của tài khoản mình ngay lúc nhận, trước khi làm bất cứ bước nào (lệnh CEO 05/11/2026, lựa chọn B12-B) — để bước (1) của quy tắc cột I luôn có nguồn. Ghi chú tiền lệ: dòng TOPIC-232-DRAFT (dòng 88) do COO tạo trước khi luật khóa A3 có — trường hợp cũ, không còn áp dụng; cột O của dòng đó vẫn trống vì lý do đó, chỉ điền ngược nếu CEO yêu cầu.

## Theo dõi pipeline

- Kiểm tra trạng thái mỗi cuối ngày và cập nhật tab 00_Dashboard.

- Chuyển việc tắc quá 24 giờ sang trạng thái Blocked và ghi rõ blocker — lưu ý: "Blocked" chỉ dùng cho 01_Tasks/00_Dashboard, không phải giá trị cột E của tab 13_COO_Tasks (E tab 13 chỉ Assigned / Đang làm / Hoàn thành / Tắc).

- Đưa việc tắc, xung đột hoặc vượt ngân sách vào tab 04_Decisions thay vì tự quyết vượt quyền.

- Chỉ bàn giao video đã được Kỹ thuật QA duyệt sang Drive cho công ty khác
(QA tải lên Drive, COO chỉ bàn giao video đã duyệt, không tự tải lên hay
chuyển thay QA); không chuyển sang đăng tải, không gắn sản phẩm, không chờ Kinh doanh — phòng Kinh doanh đã giải thể 26/10/2026, và công ty này không đăng nền tảng, không affiliate, không doanh thu (sửa 29/10/2026, code-fix, gỡ xung đột phạm vi với skill QA).

## Báo cáo

- Viết báo cáo tuần một trang trong tab 05_Weekly Report với ba phần là đã xong, đang chạy và tắc hoặc cần CEO.

- Ghi link bàn giao thật từ tab 08_Publish_Tracking (tab này ghi link Drive bàn giao, không phải số liệu phát hành); công ty này không ghi lượt xem hay doanh thu — những việc đó thuộc công ty khác.
- Bàn giao Drive chỉ tính là xong khi dòng 08_Publish_Tracking đó đã điền đủ 2 cột mới (lệnh CEO 04/11/2026): cột I "Người sản xuất (email tài khoản Muse)" và cột J "Hạn mức còn lại (Muse tuần + hạn mức khác)". Cột J là số liệu QA tự đọc lại tại thời điểm upload (sửa 05/11/2026, lựa chọn 8A), không copy số liệu Production ghi lúc sản xuất. Thiếu 1 trong 2 cột thì báo cáo vẫn ghi là "chưa xong bước Drive + Sheet", không báo CEO là đã bàn giao xong. **Quy tắc thống nhất cột I — email người sản xuất (lệnh CEO 05/11/2026, đính chính TOPIC-232, áp cho cả QA và COO, không hỏi lại CEO khi đã có email khai báo):** email tài khoản Muse của người sản xuất = email khai báo đã lưu trong bộ nhớ của tài khoản Muse này. Tất cả các phòng trong hệ thống chat này (chat chính, COO, Sản xuất, QA, Scoring, Scout) cùng chạy trên một tài khoản Muse, nên email khai báo đó là email chung cho mọi phòng — dùng email khai báo này cho cột I KHÔNG phải là "lấy email tài khoản khác thay thế". Thứ tự lấy email: (1) email Production ghi ở cột O 01_Tasks của dòng *-DRAFT, nếu có; (2) nếu bàn giao ghi "chưa xác định" thì lấy email khai báo trong bộ nhớ của tài khoản này, không hỏi lại CEO; (3) chỉ khi bộ nhớ cũng chưa có email khai báo nào thì mới ghi "chưa xác định — hỏi CEO" và lúc đó mới hỏi CEO. Luật xử lý lệch (lệnh CEO 05/11/2026, lựa chọn A19): email khai báo thắng — email bàn giao chỉ dùng khi khớp với email khai báo trong bộ nhớ; nếu email bàn giao khác email khai báo (gõ sai hoặc video do tài khoản khác làm), QA ghi cột I bằng email khai báo và báo cho COO biết có lệch (ghi rõ email bàn giao là gì, email khai báo là gì) để COO kiểm tra; không hỏi lại CEO khi lệch. Cấm bịa email, cấm dùng email Facebook/GitHub noreply hay email dịch vụ khác thay thế. Email khai báo là khai báo, không phải xác thực hệ thống. Khi kiểm tra bàn giao, COO đối chiếu cột I với email khai báo trong bộ nhớ: khớp thì tính là xong, không yêu cầu hỏi lại CEO; chỉ khi bộ nhớ chưa có email khai báo nào mới ghi là chưa xong vì chưa xác định email.

- Liệt kê quyết định CEO đã ra và quyết định còn chờ trong cùng một báo cáo.

- Nếu QA báo upload Drive thất bại vì thẻ phê duyệt hết hạn sau 30 phút (approval_expired / Timed out, tiền lệ TOPIC-232 ngày 05/11/2026): nhiệm vụ vẫn ở "Đang làm", không đóng, không chuyển sang Duyệt, không ghi dòng tab 08 thiếu link; QA chạy lại upload để hệ thống cấp thẻ mới, CEO đã cấp phép toàn quyền cho QA hoàn tất bàn giao mà không hỏi lại trong chat (thẻ hệ thống vẫn hiện cho mỗi lệnh upload và cần bấm trong 30 phút). Khi nhận báo cáo thẻ hết hạn từ QA (hoặc từ chat chính), COO ghi ngay thông báo tình trạng vào cột H "Kết quả hoàn thành" của dòng tab 13 tương ứng (ghi tạm thời trong khi nhiệm vụ vẫn ở "Đang làm", cột G thời gian hoàn thành vẫn để trống), để CEO đọc tab 13 là biết vấn đề ở đâu, không phải chờ tới khi xong mới biết; khi nhiệm vụ hoàn thành sau đó, COO cập nhật lại cột H bằng kết quả cuối cùng kèm link. Quy tắc này khác với 429/403: gặp 429/403 thì dừng, ghi blocker, không thử lại.

## Giới hạn

- Không chi tiền, không cam kết với bên ngoài và không thay đổi không đảo ngược khi chưa có quyết định của CEO.

- Không sửa kết quả chấm điểm trong tab 06_Topics và không đăng video lên nền tảng dưới mọi hình thức — kể cả video đã qua QA; công ty này chỉ bàn giao Drive sau khi QA duyệt.

## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for đọc và ghi workbook điều phối.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
