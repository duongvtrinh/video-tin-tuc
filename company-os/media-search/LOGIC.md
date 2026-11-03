# Logic tìm ảnh/video — từ khóa tiếng Việt khớp kịch bản, ảnh tự do dùng thẳng, ảnh có chữ/watermark xử lý bằng AI giữ nguyên ảnh gốc

Lệnh CEO 29/10/2026, thay thế HOÀN TOÀN logic Wikipedia > Stock > AI ngày
28/10/2026. Logic cũ (thứ tự Wikipedia > Stock > AI, script
`search_media.py`, chấm điểm 0-100 theo khái niệm/kích thước/giấy phép,
bảng khái niệm Anh, cụm linh hoạt `CONCEPT_CLUSTERS`) KHÔNG còn áp dụng
cho video mới. Script cũ chỉ còn giá trị lịch sử, không chạy cho video
mới. Tài liệu này là logic duy nhất cho việc tìm media, và đã gắn vào
skill Sản xuất cùng ngày.

## Phân nhánh theo chủ đề (bổ sung CEO 30/10/2026)

Áp trước mọi bước tìm, phân loại theo chủ thể chính của kịch bản:

- **Kịch bản về nước ngoài:** được dùng ảnh/video từ Wikipedia và Stock,
  cộng các nguồn chung (bài báo liên quan, bài đăng mạng xã hội công
  khai, tìm kiếm hình ảnh).
- **Kịch bản về Việt Nam:** ẢNH thì BỎ QUA Wikipedia và Stock hoàn toàn
  (kể cả stock miễn phí), chỉ lấy ảnh từ nguồn gốc qua tìm kiếm trên
  internet bằng từ khóa tiếng Việt (bài báo về đúng vụ việc, bài đăng
  mạng xã hội công khai liên quan). VIDEO có ngoại lệ (quy tắc CEO
  31/10/2026): video từ Wikipedia (Wikimedia Commons) và Stock (vd
  Pexels) ĐƯỢC DÙNG nếu vượt qua được cửa bối cảnh cứng (bối cảnh Việt
  Nam xác định được hoặc trung tính, không dấu hiệu nước ngoài rõ
  rệt); video không qua cửa thì loại; video qua cửa vẫn là minh họa
  chung chung, ghi nguồn + giấy phép, tắt tiếng, dọc 9:16. Ảnh khác
  tỷ lệ cắt về 720x1280 bám chủ thể; ảnh có watermark/chữ/logo thì AI
  chỉ xóa watermark/chữ/logo, giữ nguyên ảnh gốc.
- **Không bỏ cuộc ở cụm từ khóa đầu tiên:** một cụm không ra ảnh thì
  thử tiếp các cụm liên quan khác (từ đồng nghĩa, tên người/địa
  danh/sự vật khác trong cảnh, bối cảnh rộng hơn hoặc hẹp hơn); chỉ khi
  thử hết mà hoàn toàn không tìm thấy ứng viên phù hợp thì mới tạo AI.
- **Ưu tiên minh họa thực tế (bổ sung CEO 31/10/2026):** với sự kiện
  cụ thể đã xác minh được, cố gắng giữ minh họa thực tế sát kịch bản
  — tìm ảnh/video của đúng sự kiện/cảnh đó trước, minh họa chung
  chung chỉ là phương án dự phòng khi không tìm thấy ảnh thực tế,
  khi ràng buộc chủ đề ghi rõ generic, khi vướng riêng tư, hoặc khi
  ảnh thực tế không qua cửa bối cảnh. Ảnh thực tế vẫn phải tuân luật
  phân nhánh và cửa bối cảnh.

## Nguyên tắc

1. **Tìm bằng từ khóa TIẾNG VIỆT khớp kịch bản nhất** cho từng cảnh/part,
   rút từ `sceneScriptSummary` / `broll.scriptSummary`. Không dịch sang
   tiếng Anh, không dùng bảng khái niệm Anh cũ. Bỏ từ máy quay/dàn cảnh
   khỏi query (như "góc rộng", "lia chậm") — query phải là sự vật trong
   cảnh, không phải từ mô tả máy quay. Thử nhiều từ khóa đồng nghĩa
   tiếng Việt cho cùng một cảnh; ưu tiên ảnh trong bài viết về đúng vụ
   việc (nguồn của chủ đề) trước, rồi mới tìm ảnh chung.
2. **Nguồn tìm, chỉ công khai, chỉ đọc:** ảnh trong bài báo liên quan
   đến vụ việc, bài đăng mạng xã hội công khai, tìm kiếm hình ảnh
   Google. Không đăng nhập tài khoản cá nhân để lấy ảnh riêng tư, không
   đăng, không bình luận, không nhắn tin.
3. **Phân loại bắt buộc cho mỗi ứng viên, không được bỏ qua:**
   - **DÙNG THẲNG, giấy phép tự do đã kiểm chứng:** public domain,
     CC0, CC BY, CC BY-SA, hoặc giấy phép stock cho phép dùng
     (Pixabay/Pexels license) — kèm tác giả + link trang file khi giấy
     phép yêu cầu ghi công.
   - **DÙNG THẲNG, ảnh báo/mạng xã hội không logo/watermark/chữ, kèm
     ghi nguồn — theo quyết định chịu rủi ro của CEO (29/10/2026):**
     ảnh báo chí/mạng xã hội về đúng vụ việc, không có logo, watermark
     hay chữ dính trên ảnh, được dùng trực tiếp kèm ghi rõ nguồn (tên
     báo/trang + link). Nói rõ để không hiểu lầm về sau: ảnh này vẫn
     là tác phẩm có bản quyền — "đăng công khai" không phải là giấy
     phép, và thực tế ít bị đánh không có nghĩa là không thể bị đánh.
     CEO quyết định chấp nhận rủi ro này; nếu có khiếu nại thì gỡ/thay
     ảnh ngay. Ảnh có dấu hiệu agency (logo, watermark) sang nhóm xử lý AI dưới đây (chỉ xóa logo/watermark/chữ, giữ nguyên ảnh gốc); ảnh của cá nhân riêng tư cũng giữ nguyên như mọi ảnh khác (lệnh CEO tối 29/10/2026): chỉ xóa chữ/watermark nếu có, không đổi gì thêm.
   - **AI XÓA CHỮ/WATERMARK (giữ nguyên ảnh gốc, lệnh CEO tối 29/10/2026):** ảnh có logo, watermark, chữ dính trên ảnh, hoặc có dấu hiệu agency, bất kể chủ thể là ai (kể cả cá nhân riêng tư). Dùng AI chỉnh sửa để xóa CHỈ logo/watermark/chữ khỏi ảnh gốc, giữ nguyên toàn bộ phần còn lại của ảnh gốc (bố cục, người, vật, bối cảnh). KHÔNG tạo ảnh AI mới tương tự — chất lượng tạo ảnh AI của Muse hiện tại quá tệ nên không sinh ảnh tương tự nữa. Kết quả vẫn là ảnh gốc (đã xử lý), mang cùng trạng thái bản quyền như ảnh dùng thẳng, thuộc quyết định chịu rủi ro của CEO (có khiếu nại thì gỡ/thay ngay). Không có ứng viên dùng thẳng phù hợp thì tạo AI từ prompt kịch bản thuần (không có ảnh gốc để giữ).
4. **Ảnh gốc đã xóa chữ/watermark: kiểm tra đúng thứ, không sinh ảnh mới:** soi trực quan đối chiếu output với ảnh gốc — chữ/watermark/logo đã sạch, phần còn lại giữ nguyên (bố cục, người, vật, bối cảnh không đổi). Nếu AI làm biến dạng phần còn lại của ảnh thì loại và xử lý lại, không chuyển sang sinh ảnh tương tự. Bàn giao ghi rõ URL ảnh gốc + "ảnh gốc đã xóa chữ/watermark bằng AI, vẫn là ảnh gốc" + ghi chú quyết định chịu rủi ro của CEO.
5. **Không bao giờ ghi minh họa là "tư liệu thật"** của một sự kiện cụ
   thể, dù là ảnh tự do hay ảnh AI từ prompt. Nhân vật/sự kiện thiếu tư
   liệu đã kiểm chứng: giữ quy tắc chung chung 28/10/2026 (góc rộng,
   sau lưng/bóng mờ, tay, vật chứng, ngoại thất, ghế trống; không cận
   mặt, không tạo chân dung người thật cụ thể). Quy tắc chung chung này chỉ áp dụng cho ảnh AI từ prompt; ảnh thật tìm được thì giữ nguyên theo mục 3, không ép về dạng chung chung.

## Quy trình từng cảnh/part

- Đầu vào, lấy từ plan đã có: `sceneScriptSummary` /
  `broll.scriptSummary` bằng tiếng Việt, loại media (`image` hoặc
  `video`), và với video là thời lượng voice part thật trong `tts.json`
  (không ước tính). Với ảnh, khung đích là 720x1280, lề an toàn
  96px/140px cho chữ overlay.
- **Bước 1 — Tìm:** từ khóa tiếng Việt cho từng cảnh, thử nhiều từ
  khóa đồng nghĩa. Công cụ: CLI image-search
  (`/opt/hatch/bin/image-search "<từ khóa tiếng Việt>" --max-results N`,
  xem `/opt/muse/skills/image-search/SKILL.md`) cho ảnh web;
  `browser.search` (vertical news) + `social.search` cho bài viết/bài
  đăng liên quan; `browser.open` mở bài viết để lấy ảnh trong bài
  (footnote Images). Với bài đăng mạng xã hội, chỉ đọc bài công khai
  qua connector của nền tảng đó.
- **Bước 2 — Soi trực quan + phân loại:** xem ảnh toàn cảnh, đối chiếu
  với scriptSummary (đúng cảnh, đúng bối cảnh Việt Nam, không lệch ý
  đồ); kiểm tra logo/watermark/chữ dính trên ảnh và giấy phép/trang
  nguồn, rồi xếp vào một trong ba nhóm ở mục 3. Ứng viên lệch kịch bản
  thì loại, thử ứng viên tiếp theo. Không lấy mù top 1: khi top 1 và
  top 2 sát nhau, soi trực quan mới là người quyết.
- **Bước 3 — Quyết định:**
  - Giấy phép tự do đã kiểm chứng → dùng thẳng, ghi nguồn + giấy phép
    + link + tác giả (nếu giấy phép yêu cầu).
  - Ảnh báo/mạng xã hội không logo/watermark/chữ → dùng thẳng kèm ghi
    nguồn, theo quyết định chịu rủi ro của CEO (mục 3).
  - Ảnh có logo/watermark/chữ, dấu hiệu agency → xử lý AI xóa chữ/watermark giữ nguyên ảnh gốc theo mục 4, ghi URL ảnh gốc + ghi chú xử lý.
  - Ảnh tìm được có tỷ lệ khác 9:16 → tự cắt về 720x1280, chọn cửa sổ crop bám đúng chủ thể chính của cảnh (không cắt mù giữa khung), soi lại sau khi cắt để chắc chủ thể không bị cắt đầu/cắt người.
  - Không có ứng viên nào phù hợp → tạo AI từ prompt kịch bản thuần,
    ghi rõ "AI từ prompt, không có ảnh tham chiếu".
- **Video b-roll:** cùng quy trình; ứng viên video tự do phải có thời
  lượng gần voice part (cắt/lặp vừa phải, không lệch nhịp). AI video
  từ tham chiếu khi công cụ tạo video hoạt động; hiện tại tạo video AI
  bị chặn 403 theo khu vực (29/10/2026) nên fallback là ảnh + Ken
  Burns, và phải báo COO/QA nếu cảnh hook/quan trọng rơi vào fallback.
- **Gắn file:** ảnh vào `build/media/images/` theo tên
  `seg_<order>_<rand6>.jpg` (tính bằng `bin/filename.py`); video vào
  `build/media/broll/broll_seg_<order>_part_<pi>_<rand6>.mp4`, plan ghi
  `broll.mediaType="video"`, `keepAudio=false`, `sourceStartSec` nếu
  cần cắt từ clip dài hơn.

## Hồ sơ bàn giao cho QA (mỗi media, thiếu trường nào thì chưa đủ điều kiện render)

- Ảnh dùng thẳng: nguồn, link trang file, giấy phép đã kiểm chứng
  (với ảnh tự do) hoặc ghi nguồn báo/trang + ghi chú "dùng trực tiếp
  theo quyết định CEO 29/10/2026" (với ảnh báo/mạng xã hội không
  logo/watermark/chữ), tác giả (nếu giấy phép yêu cầu), ghi chú soi
  trực quan khớp kịch bản.
- Ảnh gốc đã xóa chữ/watermark bằng AI: URL ảnh gốc, ghi chú "ảnh gốc đã xóa chữ/watermark bằng AI, vẫn là ảnh gốc" + ghi chú quyết định chịu rủi ro của CEO, kết quả soi (chữ/watermark đã sạch, phần còn lại giữ nguyên).
- Ảnh AI từ prompt: prompt + ghi chú "AI từ prompt, không có ảnh tham
  chiếu".
- Video: thêm thời lượng so với voice part.
- Bắt buộc cho mọi media: trường `source` trong mediaSource phải là chuỗi tên nguồn không rỗng (không được thiếu, không được null) — app yêu cầu `source` dạng chuỗi nên thiếu là lỗi getProject 500 (tiền lệ 29/10/2026: topic029001, topic039001, topic037001).
- Quy tắc kiểm chứng tự động trước render vẫn giữ: thiếu một trường
  trong hồ sơ thì cảnh đó chưa đủ điều kiện render, Production phải tự
  bổ sung, không đẩy sang người duyệt.

## Lịch sử — logic cũ đã bị thay thế hoàn toàn ngày 29/10/2026

- Logic Wikipedia > Stock > AI (28/10/2026, script `search_media.py`,
  kiểm chứng bằng clip mediasrc001) bị loại bỏ vì ảnh Wikipedia/stock/
  AI tìm theo từ khóa khái niệm hầu hết không sát kịch bản — tiền lệ
  QA: đồng phục cảnh sát nước ngoài đội mũ caro, tòa nhà chính phủ
  Tokyo, phòng họp với người nước ngoài cho chủ đề công an Việt Nam;
  video stock phòng xử án đội tóc giả kiểu Anh-Mỹ. Nguyên nhân: từ
  khóa khái niệm không phân biệt được bối cảnh quốc gia, còn ảnh trong
  bài viết về đúng vụ việc thì cho biết cảnh thật trông ra sao.
- Điều chỉnh tối 29/10/2026 (CEO): ảnh báo/mạng xã hội không
  logo/watermark/chữ được dùng thẳng kèm ghi nguồn theo quyết định
  chịu rủi ro của CEO; chỉ ảnh có logo/watermark/chữ, dấu hiệu agency
  hoặc chủ thể riêng tư mới bắt buộc phái sinh AI.
- Các bài học cũ vẫn còn giá trị và đã được giữ lại trong logic mới:
  không lấy từ máy quay làm query, không lấy mù top 1, soi trực quan
  bắt buộc, video ưu tiên thời lượng gần voice part.
- Điều chỉnh tối 29/10/2026 (lệnh CEO, chất lượng tạo ảnh AI của Muse quá tệ): nhánh phái sinh đổi từ "tạo ảnh AI mới tương tự" sang "AI chỉ xóa chữ/watermark, giữ nguyên ảnh gốc"; kết quả vẫn là ảnh gốc nên mang cùng trạng thái bản quyền như ảnh dùng thẳng, thuộc quyết định chịu rủi ro của CEO (có khiếu nại thì gỡ/thay ngay); chủ thể riêng tư vẫn không được giữ nguyên mà dùng AI từ prompt minh họa chung chung.
- Điều chỉnh tối 29/10/2026 (lệnh CEO, lần 2, bãi bỏ ranh giới loại trừ cá nhân riêng tư giữ lại trước đó cùng buổi tối): ảnh của cá nhân riêng tư cũng giữ nguyên như mọi ảnh khác — chỉ xóa chữ/watermark nếu có; ảnh tìm được có tỷ lệ khác thì tự cắt về đúng tỷ lệ cần dùng (720x1280 dọc 9:16), khi cắt phải focus đúng chủ thể chính của cảnh, soi lại sau khi cắt; quy tắc chung chung chỉ còn áp dụng cho ảnh AI từ prompt, không áp dụng cho ảnh thật tìm được.
