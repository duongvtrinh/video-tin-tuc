# Kế hoạch áp dụng skill thumbnail nhiều lớp vào sản xuất video

Ngày: 13/11/2026. Người đọc và quyết định: CEO.
Mục đích: trả lời câu hỏi "tận dụng skill thumbnail nhiều lớp cho sản xuất video như thế nào", kèm các phương án, chi phí, rủi ro và điểm cần CEO quyết.

## 1. Nghiên cứu: hiện trạng đã kiểm chứng

### 1.1. Skill thumbnail nhiều lớp là gì (đã chốt 13/11)

- Ảnh 9:16, 3 lớp xếp chồng: nền full toàn bộ, vật thể giữa, nhân vật cắt rời lớp trước.
- Nhân vật lệch trái hoặc phải ngẫu nhiên, không đặt giữa; mặt hướng vào giữa hoặc trực diện.
- Kích thước cố định theo chuẩn ảnh Iran 13/11: khoảng 70% chiều rộng và 55% chiều cao khung hình, đỉnh đầu ở khoảng 1/3 chiều cao.
- Thân dưới nhân vật hoà trộn vào nền, không cắt thẳng lề dưới; 1/4 dưới tối và trơn để chèn tiêu đề.
- Nhân vật luôn là lớp trên cùng, không chi tiết nào phủ lên trên.
- Được thêm tên thương hiệu hay tổ chức ngắn gọn ở nền khi cần chú thích ngữ cảnh.
- Mặt nhân vật là ảnh AI, chỉ gần giống người thật, không phải ảnh thật.
- Tối đa 4 lần tạo ảnh mỗi yêu cầu.

### 1.2. Thumbnail đã nối vào pipeline ở đâu

- Production đã tạo 1 ảnh thumbnail 9:16 bằng skill này sau `exportProject` cho mỗi video, ghi tên file vào `TASKS.K` (nối 13/11).
- Ảnh thumbnail hiện chỉ là file local + tên file trong Sheet. QA bàn giao lên Drive "Video Muse" chỉ có file MP4, không kèm ảnh thumbnail.
- Công ty khác phụ trách xuất bản. Ảnh bìa khi đăng thuộc việc của họ, nhưng công ty này có thể cung cấp sẵn file bìa kèm video.

### 1.3. Công cụ cũ đã có trong factory: `bin/thumbnail.py`

- Factory đã có sẵn `bin/thumbnail.py`: tạo thumbnail YouTube 1280x720 (16:9) tự động, chọn 2-3 khoảnh khắc đắt trong video (part có template chữ hoặc giữa scene), lấy ảnh nền thật từ video + phủ tiêu đề, ghi ra `projects/<id>/export/<id>_thumb_1.jpg (2, 3)`.
- Đây là triết lý khác skill mới: ảnh cũ lấy khung thật từ video (16:9), ảnh mới là ảnh AI xếp lớp (9:16).
- Kết luận: skill mới không thay thế `thumbnail.py`. Công cụ cũ vẫn có ích khi cần ảnh 16:9 từ khung thật.

### 1.4. App không có chỗ cho ảnh bìa

- Tìm trong code client của app (`app-tao-video/client/src/`): không có chỗ dùng thumbnail, poster hay cover cho project.
- Muốn app hiển thị ảnh bìa thì phải sửa app. Không nằm trong kế hoạch này trừ khi CEO yêu cầu riêng.

### 1.5. Công cụ ghép ảnh thật: chưa có

- Factory có Pillow 13.0.0 + numpy 2.5.4. Không có rembg (cắt nền tách người khỏi ảnh thật), không có opencv trong venv factory.
- Render engine có ghép lớp bằng PIL (alpha) trong đường render, nhưng không có cắt nền.
- Muốn ghép ảnh thật theo công thức lớp của skill thì phải thêm công cụ cắt nền (rembg hoặc dịch vụ tương đương) + viết script ghép. Đây là việc cần đầu tư, không có sẵn.

### 1.6. Luật media đang chặn gì

- s1p1 + ảnh cảnh chung bắt buộc là ảnh thật từ báo chí/mạng xã hội/Google (LOGIC.md §8d). AI chỉ khi đã thử hết không có ảnh (TOPIC-219) hoặc báo COO.
- preview-banner bắt buộc ảnh thật (DEC-274). Không được dùng ảnh AI cho preview-banner.
- Người thật có tên: ưu tiên ảnh thật; không có ảnh thật đã kiểm chứng thì làm ảnh AI theo prompt từ thông tin đã kiểm chứng và ghi rõ trong bàn giao là ảnh minh hoạ AI, không phải ảnh thật (quyết 30/10).
- Ảnh AI phải ghi rõ là ảnh minh hoạ AI trong bàn giao, không trình bày như ảnh thật hay chân dung thật.
- Người là cá nhân riêng tư (nạn nhân, nhân chứng): chỉ dùng ảnh chung chung (xa, lưng, bóng), không vẽ mặt.
- Hệ quả: ảnh thumbnail AI không thể mặc định làm ảnh s1p1 hay ảnh cảnh chung. Nó chỉ đi được đường ngoại lệ AI đã có sẵn, hoặc đi đường ảnh thật (mục 2.3).

### 1.7. Chủ đề nào hợp, chủ đề nào không

- Hợp: chủ đề có nhân vật công chúng rõ ràng làm trung tâm (chính trị, thể thao, lãnh đạo doanh nghiệp, người nổi tiếng). Đây là đa số tin tức của công ty.
- Không hợp: chủ đề số liệu không có nhân vật trung tâm. CEO đã nêu: giá vàng, giá xăng. Thêm vào cùng nhóm: tỷ giá, chứng khoán (chỉ số chung), thời tiết, giá điện nước. Với nhóm này, công thức "nhân vật lệch bên" không có nhân vật để đặt.
- Không dùng mặt: sự kiện không có nhân vật trung tâm (thiên tai, tai nạn, cháy nổ) và chủ đề mà nhân vật là cá nhân riêng tư. Với nhóm này chỉ dùng ảnh thật của sự kiện, không vẽ mặt AI.

### 1.8. Điểm khớp kỹ thuật giữa thumbnail và video

- Video đang làm là 9:16, đúng tỉ lệ thumbnail. Ảnh thumbnail thả vào làm b-roll hoặc ảnh trong template photo đều vừa khung, không cần xử lý tỉ lệ.
- 1/4 dưới của thumbnail tối và trơn. Phụ đề karaoke của video nằm ở đáy khung, nên nền tối này giúp chữ phụ đề đọc rõ hơn nếu ảnh được dùng làm b-roll có lời thoại.
- Ảnh thumbnail là file JPG phẳng (đã ghép xong 3 lớp). Engine video không tách lại được các lớp, chỉ dùng như một ảnh thường.

## 2. Các phương án

### Phương án A. Bàn giao ảnh thumbnail kèm video lên Drive (rủi ro thấp, làm ngay)

- Nội dung: Production đã tạo ảnh thumbnail sau mỗi video. QA khi duyệt xong thì upload cả 2 file lên Drive "Video Muse": file MP4 + file thumbnail JPG 9:16 (đặt tên `TOPIC-xxx-thumb.jpg`), ghi link thumbnail vào bàn giao (TASKS.K hoặc cột ghi chú bàn giao).
- Tác dụng: công ty xuất bản có sẵn ảnh bìa 9:16 đúng chuẩn để đăng TikTok/Facebook, không phải tự làm bìa. Ảnh bìa là thứ người xem thấy trước khi bấm xem, nên ảnh tốt giúp lượt xem.
- Cổng chủ đề: chỉ làm thumbnail cho chủ đề có nhân vật công chúng. Chủ đề số liệu (vàng, xăng, tỷ giá, thời tiết) thì không làm thumbnail theo công thức này (hoặc để trống, công ty xuất bản tự lo).
- Chi phí: gần như bằng 0 (ảnh đã tạo sẵn trong pipeline). Thêm 1 bước upload của QA + 1 dòng ghi chú bàn giao.
- Rủi ro: gần như không có. Không đổi nội dung video. Mặt AI chỉ xuất hiện trên ảnh bìa, không vào video.
- Cần thay đổi: skill QA (bước bàn giao Drive: upload 2 file thay vì 1) + Production (đặt tên file thumbnail theo quy ước `TOPIC-xxx-thumb.jpg`).
- Cần CEO quyết: có cho QA upload thêm file thumbnail lên Drive không.

### Phương án B. Dùng ảnh thumbnail AI làm khung hook đầu video (rủi ro trung bình)

- Nội dung: lấy ảnh thumbnail AI làm ảnh cho cảnh hook (s1p1 hoặc part mở đầu 0-3 giây), thay cho ảnh thật khi không tìm được ảnh thật của nhân vật/sự kiện.
- Tác dụng: khung hook có bố cục mạnh (nhân vật lớn, nền drama, 1/4 dưới tối giúp phụ đề rõ), đúng công thức đã kiểm chứng đẹp.
- Giới hạn: chỉ đi đường ngoại lệ AI đã có sẵn trong luật (đã thử hết không có ảnh thật, theo TOPIC-219, hoặc báo COO). Không bao giờ làm mặc định, không dùng cho preview-banner (DEC-274 cấm ảnh AI ở đó).
- Chi phí: gần như bằng 0 (ảnh đã có). QA thêm 1 điểm kiểm: mặt AI có giống người thật đến mức gây hiểu lầm không, và bàn giao phải ghi rõ là ảnh minh hoạ AI.
- Rủi ro: mặt AI của người thật hiện trong video vài giây dễ gây hiểu lầm hơn là trên ảnh bìa tĩnh. Nếu mặt sai nhiều, video bị xem là đưa ảnh giả. Đây là rủi ro lớn nhất của phương án này.
- Cần CEO quyết: có cho phép ảnh AI làm khung hook khi không có ảnh thật không, hay giữ nguyên luật ảnh thật cho s1p1.

### Phương án C. Ghép ảnh thật theo công thức lớp của skill (đầu tư, đúng luật nhất)

- Nội dung: tách riêng công thức bố cục của skill khỏi việc tạo ảnh AI, áp cho ảnh thật. Lấy ảnh thật của nhân vật (cắt nền tách người), ảnh thật của bối cảnh (nền phải), ảnh thật của vật thể giữa, ghép thành một ảnh 9:16 theo đúng luật: nhân vật lệch bên, kích thước 70%/55%, mặt hướng vào giữa, nền full, thân dưới hoà trộn, 1/4 dưới tối.
- Tác dụng: khung hook có bố cục đã kiểm chứng đẹp mà vẫn là ảnh thật 100%, không vi phạm luật ảnh thật cho s1p1, không có rủi ro mặt AI. Ảnh ghép xong dùng được cho s1p1, ảnh cảnh chung, hoặc làm b-roll.
- Chi phí: cần đầu tư. Cài rembg (hoặc dịch vụ cắt nền tương đương) vào factory, viết 1 script ghép ảnh (`bin/layered_compose.py`), kiểm chứng trên 2-3 video thật trước khi đưa vào pipeline. Ước lượng: 1 buổi làm tool + 1 buổi thí điểm.
- Rủi ro: cắt nền tự động có thể lỗi ở tóc, mép áo, nền phức tạp; cần QA soi khung thật như mọi ảnh khác. Ảnh ghép vẫn phải qua cổng bối cảnh cứng (ảnh Việt Nam phải là ảnh gốc Việt Nam).
- Cần CEO quyết: có đầu tư làm tool ghép ảnh thật không, và giao ai làm (Production hay task riêng).

### Phương án D. Template mới "hook xếp lớp" trong engine (đầu tư lớn nhất)

- Nội dung: làm 1 template mới nhận 3 input riêng (ảnh nhân vật, ảnh nền, ảnh vật thể) và tự ghép theo luật thumbnail ngay trong engine render, thay vì ghép sẵn thành 1 file JPG trước.
- Tác dụng: linh hoạt nhất (đổi từng lớp riêng, chỉnh vị trí, dùng lại cho nhiều video). Nhưng engine hiện render template từ ảnh đã có, ghép lớp trong template là việc mới.
- Chi phí: cao nhất (sửa engine + thiết kế template + kiểm chứng render + QA). Chỉ nên làm sau khi phương án C đã chứng minh công thức này hiệu quả trên video thật.
- Đề xuất: hoãn. Không làm trong đợt này.

### Phương án E. Giữ nguyên (không làm gì thêm)

- Thumbnail vẫn là file local + tên file trong TASKS.K như hiện tại. Công ty xuất bản tự làm ảnh bìa. Video không đổi.
- Đây là phương án mặc định nếu CEO không chọn phương án nào.

## 3. Đề xuất của tôi (CEO quyết, tôi không tự chọn)

- Làm ngay phương án A: bàn giao thumbnail kèm video lên Drive. Rủi ro gần bằng 0, tận dụng ảnh đã tạo sẵn, giúp công ty xuất bản có bìa 9:16 chuẩn.
- Thí điểm phương án C trên 2-3 video có nhân vật công chúng (chủ đề đã có ảnh thật tốt): làm tool ghép ảnh thật, so sánh khung hook ghép thật với khung hook ảnh thật đơn và với ảnh AI, rồi CEO xem và quyết có đưa vào pipeline không.
- Không làm phương án B làm mặc định. Giữ B ở đúng đường ngoại lệ AI đã có (chỉ khi không có ảnh thật), vì rủi ro mặt AI trong video.
- Hoãn phương án D cho đến khi C chứng minh hiệu quả.

## 4. Điểm CEO cần quyết (trả lời từng điểm)

1. Phương án A: QA có upload file thumbnail `TOPIC-xxx-thumb.jpg` lên Drive kèm video không? (Có / Không)
2. Phương án B: có cho phép ảnh thumbnail AI làm khung hook khi không có ảnh thật không, hay giữ nguyên luật ảnh thật cho s1p1? (Chỉ ngoại lệ như luật hiện tại / Không dùng AI cho hook)
3. Phương án C: có đầu tư tool ghép ảnh thật (rembg + script ghép + thí điểm 2-3 video) không? (Có, giao làm / Không)
4. Phương án D: hoãn hẳn hay đưa vào danh sách việc sau? (Hoãn / Để sau)
5. Cổng chủ đề: xác nhận nhóm không làm thumbnail là chủ đề số liệu (vàng, xăng, tỷ giá, chứng khoán, thời tiết) + sự kiện không có nhân vật trung tâm + cá nhân riêng tư. Có thêm nhóm nào không?

## 5. Nếu CEO duyệt A (+ C thí điểm): các bước tiếp theo

1. Đổi tên file thumbnail theo quy ước `TOPIC-xxx-thumb.jpg` (Production).
2. Sửa skill QA: bước bàn giao Drive upload 2 file (MP4 + thumbnail), ghi link thumbnail vào bàn giao.
3. Sửa skill Production: ghi rõ cổng chủ đề (chỉ làm thumbnail khi có nhân vật công chúng).
4. Chạy 1 ca thật để kiểm chứng: thumbnail lên Drive cùng video, công ty xuất bản xác nhận dùng được.
5. Nếu duyệt C: cài rembg, viết `bin/layered_compose.py`, thí điểm 2-3 video, CEO xem khung hook rồi quyết đưa vào pipeline hay không.
6. Ghi IMP vào improvement-log + đẩy repo sau khi CEO duyệt thay đổi skill (theo luật đẩy GitHub).
