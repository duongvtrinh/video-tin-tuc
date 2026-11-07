# Quét trend làm video (Sheet mới "Video HQ — Trụ sở Muse")

**Đã kích hoạt từ GĐ2 (07/11/2026, cắt hẳn sang Sheet mới). Thay thế skill media-scout cũ.**

- Workbook mới: "Video HQ — Trụ sở Muse" (spreadsheetId `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`). Workbook cũ "HQ - Công ty 1 người" chỉ đọc, KHÔNG ghi.
- Hai phòng Scout giữ tách riêng: Scout - Báo và Scout - Group, mỗi phòng quét nguồn của mình và TỰ CHẤM chủ đề của mình trong cùng lượt quét (quyết định CEO C3, 07/11/2026: gộp Scout + Scoring, ĐÓNG chat Scoring — không còn hàng đợi Pending Scoring, không nhắn Scoring nữa).
- Tab duy nhất ghi vào: TOPICS. Không ghi vào tab nào khác.

## Sheet mới — TOPICS (A–M)

- Một dòng cho một chủ đề. Khoá: cột A (TOPIC_ID).
- TOPICS: A TOPIC_ID | B TITLE | C SOURCE | D DISCOVERED | E HOT (30) | F AUDIENCE (20) | G FRESH (20) | H FEASIBLE (15) | I SOURCED (15) | J TOTAL (công thức `=SUM(E:I)`, không ghi tay) | K STATUS (dropdown NEW/APPROVED/READY/HOLD/REJECTED/DUPLICATE) | L ANGLE | M NOTES.
- Scout ghi TẤT CẢ các cột B–I, K, L, M trong MỘT lần ghi (dòng đã có điểm + STATUS; cột A TOPIC_ID ĐỂ TRỐNG). Không ghi dòng rồi nhắn người khác chấm — không còn lượt chấm riêng.
- TOPIC_ID: ĐỂ TRỐNG khi ghi chủ đề mới (quyết CEO 07/11/2026, phương án E cho R4-04). Scout KHÔNG tự sinh ID — không lấy "số tiếp nối ID lớn nhất", không chia dải chẵn/lẻ, không sinh ID-thời gian. Chỉ khi CEO duyệt (lật STATUS sang READY) thì CEO TỰ NHẬP TOPIC_ID bằng công cụ riêng bên ngoài, đảm bảo không trùng ID. Chủ đề không duyệt thì tiếp tục bỏ trống. Các ID cũ (TOPIC-001…TOPIC-289) giữ nguyên, không viết lại. Nếu tab TOPICS trống (chỉ có header, không còn dòng nào), TOPIC_ID đầu tiên là TOPIC-001 — CEO nhập khi duyệt chủ đề đầu tiên sau khi tab trống (quyết CEO 07/11/2026, phương án A cho R4-18).
- Một cột đúng một người viết (D6/R2): Scout chỉ ghi TOPICS.B–I, K, L, M. TOPIC_ID (A) và STATUS=READY chỉ CEO ghi. Cần sửa cột của vai trò khác thì nhắn cho vai trò đó, không tự sửa.
- Luật chống đua áp dụng (R1–R10, xem GĐ0 draft (file kế hoạch thiết kế lại Sheet, §3.4 — ~/workspace/user/files/K__ho_ch_thi_t_k__l_i_quy_tr_nh_Sheet.md)): R1 tham chiếu bằng TOPIC_ID khi đã có; chủ đề chưa có ID thì tham chiếu tạm bằng tiêu đề, không bao giờ bằng số dòng; R3 đọc lại TOPICS theo tiêu đề ngay trước khi ghi (khoảng cách đọc→ghi tính bằng giây); R4 ghi idempotent (ghi lại cùng giá trị không tạo trùng); R6 không xoá dòng, không đổi cấu trúc khi chưa báo trước + snapshot; R7 đầu mỗi ca: chỉ đọc số dòng + ID lớn nhất (chỉ tính các dòng ĐÃ CÓ ID) của TOPICS và TASKS để nắm trạng thái hiện tại (làm mốc cho ca sau). Số dòng giảm hoặc ID lớn nhất (đã có) lùi KHÔNG dừng ca, KHÔNG báo cáo (quyết CEO 07/11/2026: làm việc bình thường, không quan tâm mất dòng, không báo cáo). Không thêm tab BASELINE hay file baseline.json. (Tăng là bình thường vì Sheet dùng chung nhiều chi nhánh; ID trống là bình thường, không phải lỗi.)

## Chọn nguồn

- Quét ba loại nguồn trong mỗi ca là báo, group hoặc mạng xã hội và tìm kiếm hoặc trend.

- Ưu tiên tín hiệu trong 24 đến 72 giờ và ghi rõ thời điểm phát hiện.

- Ghi nguồn cụ thể cho mỗi chủ đề để CEO/QA có thể kiểm chứng lại.

- Group CÔNG KHAI ĐÔNG và HOẠT ĐỘNG TÍCH CỰC (quy tắc CEO 03/11/2026, thay cách tìm group chung chung trước đây): chỉ dùng group công khai từ 50.000 thành viên trở lên và hoạt động tích cực (có bài mới/thảo luận trong 72 giờ); KHÔNG dùng group nhỏ, ít hoạt động. Cách tìm (theo thứ tự): (1) social.search với ranking engagement bằng từ khóa tiếng Việt của chủ đề — từ các bài nhiều tương tác, lấy tên group/page nguồn (vanity trong URL dạng facebook.com/groups/<vanity>/), rồi kiểm tra bằng facebook-cli groups details --group-id '<vanity>' — chỉ giữ group có visibility OPEN và member_count từ 50000 trở lên; (2) facebook-cli groups search --keywords '<từ khóa tiếng Anh tương đương>' --sort-by LARGEST --limit 25 — LƯU Ý đã kiểm chứng 03/11: từ khóa tiếng Việt luôn trả về rỗng (giá vàng, bóng đá, trốn trại A2, sao băng, mưa lũ đều 0), chỉ từ khóa tiếng Anh mới trả về group (vd 'football' → group 238.000 thành viên) — nên đường này bắt buộc dùng từ khóa tiếng Anh và vẫn phải kiểm tra visibility OPEN bằng groups details vì kết quả search không kèm visibility. Group nhỏ hơn 50.000, không công khai, hoặc không hoạt động thì BỎ QUA. KHÔNG quét các group tài khoản đã tham gia. Chỉ đọc: không đăng, không bình luận, không nhắn tin, không tham gia group mới. Group/page là nguồn phát hiện và nguồn tư liệu; kiểm chứng KHÔNG giới hạn ở báo lớn chính thống (quy tắc CEO 03/11/2026: chủ đề nhạy cảm, scandal mà báo lớn không đăng vẫn được ghi khi có website khác đăng bài — nguồn chấp nhận là bất kỳ website nào có đăng bài, ưu tiên theo thứ tự SEO trên máy tìm kiếm thay vì chỉ lấy báo lớn; vẫn phải ghi rõ nguồn và phân biệt cáo buộc với kết luận) — chủ đề vẫn phải qua chuẩn ghi và qua chấm điểm trong cùng lượt.

- Reels là nguồn chủ đề thịnh hành (quy tắc CEO 03/11/2026): quét Reels như một kênh riêng trong mỗi ca, vì Reels có cơ chế đẩy bài thịnh hành — tìm bằng social.search với từ khóa tiếng Việt (ranking engagement) rồi lọc kết quả dạng reel/video ngắn, xếp theo bình luận trước rồi mới đến like; với reel nhiều tương tác thì đọc bằng facebook-cli post read --url '<URL reel>' để lấy số liệu, nội dung và URL video làm tư liệu. BỎ QUA reel từ các page chuyên phim, nhạc (page mà nội dung chủ đạo là phim/nhạc, không phải page tin tức) — tín hiệu từ các page đó không tính, dù reel đang thịnh hành. Reel từ page tin tức, page cộng đồng tin tức vẫn tính bình thường, và vẫn phải qua cửa phân tích đáng làm + khử trùng sớm trước khi ghi.

- Threads là nguồn tin đa dạng (quy tắc CEO 03/11/2026): ngoài tín hiệu tương tác, tìm thêm thông tin trên Threads (social.search platform threads) để tổng hợp cho kịch bản — Threads có nhiều tin tức đa dạng, góc nhìn và chi tiết mà báo chính thống có thể không có (đã kiểm chứng 03/11: tìm 'giá vàng SJC' trả về hàng chục post tiếng Việt gồm bảng giá, biểu đồ, bình luận — giá trị chính là đa dạng góc nhìn, không phải lượt tương tác lớn); ghi URL post Threads làm tư liệu cùng với URL bài báo và URL post Facebook.

- Khi ghi chủ đề từ nguồn công khai: chỉ ghi chủ đề, tên nguồn + link và tín hiệu lan truyền tổng hợp (số tương tác/bình luận). KHÔNG ghi tên người đăng không phải nhân vật công chúng, câu chuyện cá nhân, số điện thoại hay nội dung riêng tư vào Sheet.

- Thứ tự đánh giá quan tâm (quy tắc CEO 03/11/2026): ƯU TIÊN LƯỢT BÌNH LUẬN trước, rồi mới xét lượt like — bài nhiều bình luận (thảo luận thật) xếp trên bài chỉ nhiều like. CLI groups posts chỉ sắp xếp theo reacts nên phải tự xếp lại theo comment_count rồi mới đến react_count; social.search phải đặt ranking engagement.

- Tư liệu cho Sản xuất (quy tắc CEO 03/11/2026): với chủ đề nhiều người quan tâm, thu thập và ghi vào cột NOTES (dạng dòng ghi nhãn) để Sản xuất giảm tải tìm kiếm/xác thực: (a) URL bài báo + URL post Facebook của chủ đề; (b) URL ảnh/video từ các post Facebook đó; (c) tìm thêm bằng từ khóa cùng chủ đề trên Facebook (social.search / groups posts --query) và lưu URL ảnh/video của các bài cùng chủ đề; (d) tìm từ khóa trên internet (browser.search news) xem báo chí nói gì và lưu URL ảnh/video từ các bài báo đó. Chỉ lưu tư liệu KHÔNG trùng lặp — cùng một ảnh/video dùng lại ở nhiều nguồn thì bỏ, chỉ giữ khi khác góc chụp/quay. Mục đích: Production đọc dòng chủ đề là có ngay nguồn kiểm chứng + tư liệu ảnh/video để dựng, không phải tìm lại từ đầu.

## Ghi chủ đề + chấm trong cùng lượt (mới — gộp Scoring, C3)

- Trước khi ghi, phân tích đáng làm: tương tác cao chưa đủ — chủ đề chỉ được ghi khi đồng thời có tương tác cao thật (số liệu cụ thể), góc kể rõ sau 2 câu tóm tắt, kiểm chứng được bằng nguồn có bài đăng (không giới hạn báo lớn chính thống; ưu tiên thứ tự SEO trên máy tìm kiếm), dựng được video trong 1 ngày, và có phương án minh họa an toàn. Thiếu một thì bỏ qua, không ghi.

- Khi viết phương án minh họa an toàn trong NOTES (quy tắc CEO 31/10/2026): nếu sự kiện là cụ thể và đã xác minh được (có bài báo về đúng vụ việc kèm ảnh, địa điểm/nhân vật công chúng xác định được) thì phương án mặc định là ảnh thực tế của đúng sự kiện, không viết sẵn "minh họa generic" làm mặc định. Chỉ ghi minh họa generic khi sự kiện không có ảnh thực tế kiểm chứng được, hoặc khi cần bảo vệ riêng tư (nạn nhân, cá nhân không phải nhân vật công chúng).

- Ranh giới AI cho nhân vật có tên khi viết phương án minh họa (nhóm A/B theo LOGIC.md, lệnh CEO 05/11/2026): phân biệt nhóm A — nhân vật công chúng có nhiều thông tin công khai đã kiểm chứng (vd tổng thống Mỹ, Messi, Chủ tịch nước Tô Lâm), có thể tạo chân dung AI nếu cần thiết và vẫn phải ghi rõ là ảnh AI minh họa, không phải ảnh thật; và nhóm B — người thiếu thông tin hoặc đang trong vụ việc pháp lý nhạy cảm, chỉ góc rộng/sau lưng/bóng mờ/bàn tay (chỉ khi là vật chứng, ví dụ bàn tay đang ký giấy tờ — không cận cảnh bàn tay để nhận diện người)/vật chứng, không cận mặt, không dùng tên làm chỉ dẫn ngoại hình. Không chắc thì xếp nhóm B.

- Viết chủ đề bằng một câu rõ ràng và thêm góc khai thác trong hai câu (ghi vào TITLE và ANGLE).

- Khi viết chủ đề/góc có tỉ lệ %: không tự thêm mẫu số mà nguồn không nêu — bài học 03/11/2026 (ca học hỏi 03/11/2026): brief TOPIC-152 viết '7,7% dân số' trong khi cả 5 nguồn chỉ ghi 'chiếm khoảng 7,7%' không nêu mẫu số; kịch bản đã phải giữ wording gốc, không lặp lại mẫu số của brief. Quy tắc: nguồn không nêu mẫu số thì ghi trơ tỉ lệ; chỉ ghi mẫu số khi nguồn nêu rõ.

### Chấm điểm (công thức chuyển từ skill media-topic-scoring, chat đã đóng)

- Chấm 5 cột, thang 100: HOT tối đa 30 theo tốc độ lan truyền trong 24–72 giờ; AUDIENCE (phù hợp khán giả) tối đa 20 theo tệp theo dõi và khả năng chia sẻ; FRESH (tính mới) tối đa 20 theo góc riêng và mức độ chưa bị làm nát; FEASIBLE (khả thi sản xuất) tối đa 15 theo tư liệu, giọng đọc và công cụ dựng hiện có; SOURCED (rõ nguồn/kiểm chứng) tối đa 15 theo nguồn đã nêu, số liệu có đối chiếu được và mức độ tin cậy của nguồn. (Tiêu chí kiếm tiền/affiliate cũ đã bỏ vì phòng Kinh doanh đã giải thể và công ty này không làm affiliate/doanh thu.)
- Điểm quan tâm = HOT + AUDIENCE (tối đa 50). Cửa quan tâm xét TRƯỚC tổng điểm (quy tắc CEO 29/10/2026): một chủ đề không ai quan tâm thì không vào sản xuất dù mới, khả thi và rõ nguồn tới đâu.
- Điểm (HOT/AUDIENCE/FRESH/FEASIBLE/SOURCED) và TOTAL chỉ là THAM KHẢO cho quyết định của CEO (quyết CEO 07/11/2026, phương án E cho R4-04) — điểm không chặn sản xuất, không phải cổng. Chỉ trạng thái READY (do CEO flip) mới quyết định có sản xuất video hay không. Thang điểm và ngưỡng dưới đây chỉ để phân loại STATUS tham khảo cho CEO, không phải điều kiện sản xuất.
- Bằng chứng cho điểm quan tâm — BẮT BUỘC: điểm HOT và AUDIENCE phải có căn cứ là số liệu đã ghi trong NOTES của chủ đề — bằng chứng chính là tương tác mạng xã hội của bài công khai (lượt thích/bình luận/chia sẻ/lượt xem), bằng chứng hỗ trợ là nhiều báo chính thống cùng đưa tin trong ngày. Không chấm điểm quan tâm theo cảm giác; chủ đề chỉ có một bài báo đơn lẻ, không tương tác mạng xã hội và không có báo khác cùng đưa thì khó đạt cửa này.
- Ra quyết định (ghi STATUS trong cùng lần ghi dòng):
  - APPROVED khi tổng ≥70 VÀ điểm quan tâm ≥30, và ghi rõ góc làm (ANGLE). APPROVED chỉ có nghĩa là ĐỦ ĐIỀU KIỆN để CEO duyệt, chưa phải lệnh dựng — chỉ CEO flip APPROVED → READY mới mở cổng (D4); Scout không tự ghi READY, không giao việc dựng.
  - HOLD khi tổng 50–69, HOẶC tổng ≥70 nhưng điểm quan tâm <30 — kèm tín hiệu chờ trong NOTES: "chờ tín hiệu quan tâm rõ hơn trong 24 giờ (tương tác mạng xã hội tăng hoặc độ phủ báo chí rộng hơn)". Quan tâm có thể tăng theo thời gian nên HOLD là trạng thái chờ đúng nghĩa, không phải loại bỏ.
  - REJECTED khi tổng <50, ghi lý do bằng một dòng trong NOTES.
  - DUPLICATE khi trùng (xem khử trùng dưới), ghi tiêu đề (và TOPIC_ID nếu chủ đề gốc đã có) vào NOTES.
- Không sửa điểm sau khi đã công bố kết quả trừ khi có dữ liệu mới và ghi rõ lý do sửa. HOLD → APPROVED chỉ xảy ra khi COO ra lệnh chấm lại bằng văn bản (có dữ kiện mới), ghi rõ lý do vào NOTES; không tự chấm lại chủ đề đã công bố. REJECTED và DUPLICATE là trạng thái cuối (không chuyển tiếp). Làm rõ (quyết CEO 07/11/2026, R4-07 phương án C): "KHÔNG chấm lại chủ đề đã được chấm" nghĩa là KHÔNG chấm lại chủ đề ĐÃ CÓ điểm (đã có E–I, J, K) — KHÔNG cấm chấm dòng NEW chưa có điểm (xem mục "Chấm lại dòng NEW chưa có điểm" dưới đây).
- Lưu ý về mất lớp kiểm độc lập (C3): trước đây Scoring không chấm chủ đề do mình quét; nay mỗi phòng tự chấm chủ đề của mình. Bù lại: (a) điểm quan tâm bắt buộc có số liệu bằng chứng trong NOTES (cửa trên); (b) cổng READY của CEO không đổi — chấm sai vẫn không dựng được nếu CEO không flip READY; (c) hoc-hoi kiểm mẫu (cron bot-hoc-hoi-2000, mỗi ngày 20:00 Asia/Saigon — quyết CEO 07/11/2026, R4-14 phương án A, DEC-019).

### Chấm lại dòng NEW chưa có điểm (dự phòng — quyết CEO 07/11/2026, R4-07 phương án C)

- Áp dụng khi gặp dòng TOPICS STATUS=NEW mà E–I/J trống (tồn đọng sau migration, hoặc phòng quên chấm trong lượt quét). Dòng này CHƯA được chấm (chưa có điểm) nên KHÔNG thuộc diện "không chấm lại chủ đề đã được chấm" ở trên.
- Phòng nào phát hiện thì chấm lại, không cần phân công phòng nào chấm dòng nào — vì điểm chỉ là tham khảo cho quyết định của CEO (quyết CEO 07/11/2026, phương án E cho R4-04 và R4-07 phương án C: điểm không chặn sản xuất; NỘI DUNG chủ đề mới là yếu tố CEO dùng để quyết định duyệt).
- Chỉ sửa E–I, K, L, M + STATUS (APPROVED/HOLD/REJECTED/DUPLICATE theo thang điểm), KHÔNG sửa A–D (TOPIC_ID, TITLE, SOURCE, DISCOVERED). Ghi công thức J (`=SUM(E:I)`) bằng USER_ENTERED nếu dòng đó chưa có công thức J. Đọc lại sau khi ghi để xác nhận.
- Không áp dụng cho dòng đã có điểm (APPROVED/HOLD/REJECTED/DUPLICATE) — các dòng đó không chấm lại trừ khi có dữ kiện mới theo quy tắc ở trên.

### Khử trùng

- KHỬ TRÙNG SỚM (quy tắc CEO 03/11/2026, chống thất thoát tài nguyên): ngay khi quét được một ứng viên thịnh hành, ĐỌC NGAY TOPICS, TASKS và QA_LOG để đối chiếu — trùng là cùng sự kiện/người/số liệu/câu chuyện dù wording khác, kể cả góc đã làm trong 90 ngày. Nếu trùng thì BỎ QUA NGAY, không tìm hiểu sâu, không kiểm chứng thêm, không thu thập tư liệu, không mở rộng từ khóa cùng chủ đề. Chỉ ứng viên KHÔNG trùng mới được đi tiếp vào bước kiểm chứng sâu và thu thập tư liệu. Bước kiểm tra trước khi ghi vẫn giữ như chốt chặn cuối, nhưng không thay thế bước khử trùng sớm này. (Khử trùng theo TIÊU ĐỀ/SỰ KIỆN với TOPICS + TASKS + QA_LOG — chủ đề chưa duyệt chưa có ID nên không khử trùng theo TOPIC_ID được; chủ đề đã có ID thì đối chiếu thêm theo ID. R1: tham chiếu bằng TOPIC_ID khi đã có, bằng tiêu đề tạm thời khi chưa có ID, không bao giờ bằng số dòng.)
- Kiểm tra lại TOPICS trước khi ghi để tránh ghi trùng chủ đề đã có (R3: đọc lại ngay trước khi ghi, khoảng cách tính bằng giây).
- Ghi ít nhất dấu hiệu lan truyền như lượt chia sẻ, bình luận hoặc tốc độ tăng tìm kiếm khi có số liệu (ghi vào NOTES).

## Loại chủ đề không ghi

- Không ghi tin chưa kiểm chứng hoặc tin giả dù đang lan truyền mạnh.

- Không ghi chủ đề chỉ hot vì drama cá nhân, gossip đời tư, quảng cáo/fan content không có câu chuyện, nội dung cổ vũ bạo lực/phạm pháp, hoặc nội dung chỉ hút tương tác bằng giật gân mà không có thông tin — dù tương tác cao.

- Không ghi chủ đề đã làm trong 90 ngày với cùng một góc khai thác.

- Không ghi chủ đề không thể dựng thành video ngắn trong một ngày bằng công cụ hiện có.

## Bàn giao

- KHÔNG nhắn chat Scoring — chat đã đóng (C3). Chủ đề mới nằm trong TOPICS; CEO xem trong báo cáo ca pipeline gần nhất.
- Cuối ca LUÔN báo ngắn cho chat chính (kể cả ca trống): số chủ đề mới trong ca + danh sách tiêu đề và STATUS từng chủ đề (TOPIC_ID nếu đã có, vd chủ đề chấm lại; chủ đề mới ghi trong ca chưa có ID nên báo bằng tiêu đề). Ca trống (không có chủ đề mới) thì báo 1 dòng ngắn 'ca X: không có chủ đề mới' — KHÔNG im lặng. Ca 06:00 báo cáo NGAY lúc 06:00 (ngoại lệ khung proactivity 06:30–21:30 — quyết CEO 07/11/2026, R4-15 phương án A, DEC-020: CEO cần biết kết quả ca đầu ngày trước khi ra quyết định).
- Giữ nguyên dòng đã ghi và không sửa điểm số hay kết quả chấm điểm (trừ trường hợp sửa có dữ kiện mới ở mục trên).

## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for ghi chủ đề đã chấm vào tab TOPICS.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
