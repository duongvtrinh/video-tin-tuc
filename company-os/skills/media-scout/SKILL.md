# Quét trend làm video

## Chọn nguồn

- Quét ba loại nguồn trong mỗi ca là báo, group hoặc mạng xã hội và tìm kiếm hoặc trend.

- Ưu tiên tín hiệu trong 24 đến 72 giờ và ghi rõ thời điểm phát hiện.

- Ghi nguồn cụ thể cho mỗi chủ đề để Scoring có thể kiểm chứng lại.

- Group CÔNG KHAI ĐÔNG và HOẠT ĐỘNG TÍCH CỰC (quy tắc CEO 03/11/2026, thay cách tìm group chung chung trước đây): chỉ dùng group công khai từ 50.000 thành viên trở lên và hoạt động tích cực (có bài mới/thảo luận trong 72 giờ); KHÔNG dùng group nhỏ, ít hoạt động. Cách tìm (theo thứ tự): (1) social.search với ranking engagement bằng từ khóa tiếng Việt của chủ đề — từ các bài nhiều tương tác, lấy tên group/page nguồn (vanity trong URL dạng facebook.com/groups/<vanity>/), rồi kiểm tra bằng facebook-cli groups details --group-id '<vanity>' — chỉ giữ group có visibility OPEN và member_count từ 50000 trở lên; (2) facebook-cli groups search --keywords '<từ khóa tiếng Anh tương đương>' --sort-by LARGEST --limit 25 — LƯU Ý đã kiểm chứng 03/11: từ khóa tiếng Việt luôn trả về rỗng (giá vàng, bóng đá, trốn trại A2, sao băng, mưa lũ đều 0), chỉ từ khóa tiếng Anh mới trả về group (vd 'football' → group 238.000 thành viên) — nên đường này bắt buộc dùng từ khóa tiếng Anh và vẫn phải kiểm tra visibility OPEN bằng groups details vì kết quả search không kèm visibility. Group nhỏ hơn 50.000, không công khai, hoặc không hoạt động thì BỎ QUA. KHÔNG quét các group tài khoản đã tham gia. Chỉ đọc: không đăng, không bình luận, không nhắn tin, không tham gia group mới. Group/page là nguồn phát hiện và nguồn tư liệu; kiểm chứng KHÔNG giới hạn ở báo lớn chính thống (quy tắc CEO 03/11/2026: chủ đề nhạy cảm, scandal mà báo lớn không đăng vẫn được ghi khi có website khác đăng bài — nguồn chấp nhận là bất kỳ website nào có đăng bài, ưu tiên theo thứ tự SEO trên máy tìm kiếm thay vì chỉ lấy báo lớn; vẫn phải ghi rõ nguồn và phân biệt cáo buộc với kết luận) — chủ đề vẫn phải qua chuẩn ghi và qua Scoring chấm.

- Reels là nguồn chủ đề thịnh hành (quy tắc CEO 03/11/2026): quét Reels như một kênh riêng trong mỗi ca, vì Reels có cơ chế đẩy bài thịnh hành — tìm bằng social.search với từ khóa tiếng Việt (ranking engagement) rồi lọc kết quả dạng reel/video ngắn, xếp theo bình luận trước rồi mới đến like; với reel nhiều tương tác thì đọc bằng facebook-cli post read --url '<URL reel>' để lấy số liệu, nội dung và URL video làm tư liệu. BỎ QUA reel từ các page chuyên phim, nhạc (page mà nội dung chủ đạo là phim/nhạc, không phải page tin tức) — tín hiệu từ các page đó không tính, dù reel đang thịnh hành. Reel từ page tin tức, page cộng đồng tin tức vẫn tính bình thường, và vẫn phải qua cửa phân tích đáng làm + khử trùng sớm trước khi ghi.

- Threads là nguồn tin đa dạng (quy tắc CEO 03/11/2026): ngoài tín hiệu tương tác, tìm thêm thông tin trên Threads (social.search platform threads) để tổng hợp cho kịch bản — Threads có nhiều tin tức đa dạng, góc nhìn và chi tiết mà báo chính thống có thể không có (đã kiểm chứng 03/11: tìm 'giá vàng SJC' trả về hàng chục post tiếng Việt gồm bảng giá, biểu đồ, bình luận — giá trị chính là đa dạng góc nhìn, không phải lượt tương tác lớn); ghi URL post Threads làm tư liệu cùng với URL bài báo và URL post Facebook.

- Khi ghi chủ đề từ nguồn công khai: chỉ ghi chủ đề, tên nguồn + link và tín hiệu lan truyền tổng hợp (số tương tác/bình luận). KHÔNG ghi tên người đăng không phải nhân vật công chúng, câu chuyện cá nhân, số điện thoại hay nội dung riêng tư vào Sheet.

- Thứ tự đánh giá quan tâm (quy tắc CEO 03/11/2026): ƯU TIÊN LƯỢT BÌNH LUẬN trước, rồi mới xét lượt like — bài nhiều bình luận (thảo luận thật) xếp trên bài chỉ nhiều like. CLI groups posts chỉ sắp xếp theo reacts nên phải tự xếp lại theo comment_count rồi mới đến react_count; social.search phải đặt ranking engagement.

- Tư liệu cho Sản xuất (quy tắc CEO 03/11/2026): với chủ đề nhiều người quan tâm, thu thập và ghi vào cột Ghi chú (dạng dòng ghi nhãn) để Sản xuất giảm tải tìm kiếm/xác thực: (a) URL bài báo + URL post Facebook của chủ đề; (b) URL ảnh/video từ các post Facebook đó; (c) tìm thêm bằng từ khóa cùng chủ đề trên Facebook (social.search / groups posts --query) và lưu URL ảnh/video của các bài cùng chủ đề; (d) tìm từ khóa trên internet (browser.search news) xem báo chí nói gì và lưu URL ảnh/video từ các bài báo đó. Chỉ lưu tư liệu KHÔNG trùng lặp — cùng một ảnh/video dùng lại ở nhiều nguồn thì bỏ, chỉ giữ khi khác góc chụp/quay. Mục đích: Production đọc dòng chủ đề là có ngay nguồn kiểm chứng + tư liệu ảnh/video để dựng, không phải tìm lại từ đầu.

## Ghi chủ đề

- Trước khi ghi, phân tích đáng làm: tương tác cao chưa đủ — chủ đề chỉ được ghi khi đồng thời có tương tác cao thật (số liệu cụ thể), góc kể rõ sau 2 câu tóm tắt, kiểm chứng được bằng nguồn có bài đăng (không giới hạn báo lớn chính thống; ưu tiên thứ tự SEO trên máy tìm kiếm), dựng được video trong 1 ngày, và có phương án minh họa an toàn. Thiếu một thì bỏ qua, không ghi.

- Khi viết phương án minh họa an toàn trong Ghi chú (quy tắc CEO 31/10/2026): nếu sự kiện là cụ thể và đã xác minh được (có bài báo về đúng vụ việc kèm ảnh, địa điểm/nhân vật công chúng xác định được) thì phương án mặc định là ảnh thực tế của đúng sự kiện, không viết sẵn "minh họa generic" làm mặc định. Chỉ ghi minh họa generic khi sự kiện không có ảnh thực tế kiểm chứng được, hoặc khi cần bảo vệ riêng tư (nạn nhân, cá nhân không phải nhân vật công chúng).

- Ranh giới AI cho nhân vật có tên khi viết phương án minh họa (nhóm A/B theo LOGIC.md, lệnh CEO 05/11/2026): phân biệt nhóm A — nhân vật công chúng có nhiều thông tin công khai đã kiểm chứng (vd tổng thống Mỹ, Messi, Chủ tịch nước Tô Lâm), có thể tạo chân dung AI nếu cần thiết và vẫn phải ghi rõ là ảnh AI minh họa, không phải ảnh thật; và nhóm B — người thiếu thông tin hoặc đang trong vụ việc pháp lý nhạy cảm, chỉ góc rộng/sau lưng/bóng mờ/bàn tay (chỉ khi là vật chứng, ví dụ bàn tay đang ký giấy tờ — không cận cảnh bàn tay để nhận diện người)/vật chứng, không cận mặt, không dùng tên làm chỉ dẫn ngoại hình. Không chắc thì xếp nhóm B.

- Viết chủ đề bằng một câu rõ ràng và thêm góc khai thác trong hai câu.

- Khi viết chủ đề/góc có tỉ lệ %: không tự thêm mẫu số mà nguồn không nêu — bài học 03/11/2026 (ca học hỏi 03/11/2026): brief TOPIC-152 viết '7,7% dân số' trong khi cả 5 nguồn chỉ ghi 'chiếm khoảng 7,7%' không nêu mẫu số; kịch bản đã phải giữ wording gốc, không lặp lại mẫu số của brief. Quy tắc: nguồn không nêu mẫu số thì ghi trơ tỉ lệ; chỉ ghi mẫu số khi nguồn nêu rõ.

- Ghi vào tab 06_Topics với trạng thái Pending Scoring và không tự chấm điểm. Khi ghi chủ đề mới, Scout ghi cột O "Duyệt thủ công" = "Chờ duyệt" (sửa 05/11/2026, lựa chọn 9A); Scoring không động vào cột O, chỉ CEO đổi cột O thành "Duyệt".

- KHỬ TRÙNG SỚM (quy tắc CEO 03/11/2026, chống thất thoát tài nguyên): ngay khi quét được một ứng viên thịnh hành, ĐỌC NGAY 06_Topics, 01_Tasks và 11_QA_Log để đối chiếu — trùng là cùng sự kiện/người/số liệu/câu chuyện dù wording khác, kể cả góc đã làm trong 90 ngày. Nếu trùng thì BỎ QUA NGAY, không tìm hiểu sâu, không kiểm chứng thêm, không thu thập tư liệu, không mở rộng từ khóa cùng chủ đề. Chỉ ứng viên KHÔNG trùng mới được đi tiếp vào bước kiểm chứng sâu và thu thập tư liệu. Bước kiểm tra trước khi ghi vẫn giữ như chốt chặn cuối, nhưng không thay thế bước khử trùng sớm này.

- Kiểm tra lại tab 06_Topics trước khi ghi để tránh ghi trùng chủ đề đã có.

- Ghi ít nhất dấu hiệu lan truyền như lượt chia sẻ, bình luận hoặc tốc độ tăng tìm kiếm khi có số liệu.

## Loại chủ đề không ghi

- Không ghi tin chưa kiểm chứng hoặc tin giả dù đang lan truyền mạnh.

- Không ghi chủ đề chỉ hot vì drama cá nhân, gossip đời tư, quảng cáo/fan content không có câu chuyện, nội dung cổ vũ bạo lực/phạm pháp, hoặc nội dung chỉ hút tương tác bằng giật gân mà không có thông tin — dù tương tác cao.

- Không ghi chủ đề đã làm trong 90 ngày với cùng một góc khai thác.

- Không ghi chủ đề không thể dựng thành video ngắn trong một ngày bằng công cụ hiện có.

## Bàn giao

- Báo cho COO khi hết ca quét và ghi số lượng chủ đề mới trong ca đó.

- Giữ nguyên dòng đã ghi và không sửa điểm số hay kết quả chấm điểm.

## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for ghi chủ đề vào tab 06_Topics.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
