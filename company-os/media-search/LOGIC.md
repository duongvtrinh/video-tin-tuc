# Logic tìm ảnh/video — từ khóa tiếng Việt khớp kịch bản, ảnh tự do dùng thẳng, ảnh có chữ/watermark xử lý bằng AI giữ nguyên ảnh gốc

## Bài học bắt buộc TOPIC-219 — 04/11/2026 (lệnh CEO, áp dụng cho mọi tài khoản Muse clone repo này)

Sai sót đã xảy ra, không được lặp lại: hai video TOPIC-219 (vụ VKS đề nghị tù chung thân cho Mr Pips và Mr Hunter, sáng 4/11/2026) đều không có ảnh thật. Bản A dùng 8 ảnh AI generic minh họa phòng xử án. Bản B chỉ dùng card chữ, không có ảnh nào. Cả hai đội sản xuất đều không quét bài báo gốc, không thử từ khóa, không soi ứng viên, mà nhảy thẳng sang AI/card.

Thực tế kiểm chứng sau đó: bài Tuổi Trẻ 4/11 về đúng vụ việc đã có ảnh thật các bị cáo tại phiên tòa (Ảnh: GIANG LONG, không logo/watermark/chữ) — đủ điều kiện dùng thẳng kèm ghi nguồn theo quyết định chịu rủi ro của CEO 29/10/2026. Sai sót không phải vì không có ảnh thật, mà vì không tìm.

Từ nay, tìm ảnh thật là cửa CHẶN trước render, không phải khuyến nghị:

1. Trước khi tạo bất kỳ ảnh nào, phải tìm ảnh thật cho từng cảnh bằng từ khóa TIẾNG VIỆT khớp kịch bản, ưu tiên bài báo về đúng vụ việc, rồi bài đăng mạng xã hội công khai, rồi tìm kiếm hình ảnh. Thử nhiều cụm từ khóa đồng nghĩa, không dừng ở cụm đầu tiên, không lấy mù top 1.
2. Ghi nhật ký tìm ảnh cho mỗi cảnh vào bàn giao và tab 10_Media_Sources: từ khóa đã thử, ứng viên tìm được (link + nguồn + tác giả nếu có), phân loại (dùng thẳng / AI xóa chữ giữ nguyên ảnh gốc / loại), và lý do loại nếu loại. Thiếu nhật ký này thì cảnh đó chưa đủ điều kiện render.
3. Chỉ khi đã thử hết mà hoàn toàn không có ứng viên phù hợp mới được tạo AI từ prompt, và phải ghi rõ: "AI từ prompt, không có ảnh tham chiếu, đã thử các từ khóa: ..." — cấm ghi chung chung "AI generic" để lấp hồ sơ.
4. Nền xanh rêu kẻ ô vuông (không chữ) KHÔNG thay thế ảnh. Nền này là nền chờ khi chưa có ảnh, không phải ảnh minh họa. Scene không có ảnh thật vẫn phải có ảnh nền (ảnh thật generic, ảnh gốc đã xử lý, hoặc AI từ prompt có ghi rõ lý do), không được render chỉ nền xanh rêu rồi gọi là "đã có ảnh".
5. QA chặn: nếu media table ghi AI generic / nền xanh rêu kẻ ô vuông (không chữ) mà không kèm nhật ký tìm ảnh thật, QA TRẢ LẠI, không duyệt im lặng, dù các cửa kỹ thuật và nội dung khác đạt.

Ghi chú chuyển đổi 05/11/2026 (lệnh CEO): logic card chữ cũ đã được thay bằng nền xanh rêu kẻ ô, không chữ, trong `bin/render_scene_card.py` — nền xanh rêu đậm #1C372A, kẻ ô vuông 80px, không kicker, không headline, không dòng nguồn, không template overlay. Nền này vẫn KHÔNG thay thế ảnh, giống như card chữ cũ: scene chỉ có nền này vẫn tính là thiếu ảnh ở tầng hồ sơ/QA.
6. Trình bày sai nguồn gốc là lỗi chặn: ảnh AI từ prompt mà bàn giao, caption hoặc plan ghi như ảnh thật (kể cả ghi mediaSource.source là tên một tờ báo/trang trong khi file thực chất là AI) thì QA TRẢ LẠI để ghi đúng "AI từ prompt, minh họa, không phải ảnh thật". Quyền trả lại này thuộc QA, không cần CEO quyết từng trường hợp.
7. Luật mới trong mục này (cửa chặn TOPIC-219, ranh giới AI cho nhân vật có tên ở mục dưới) chỉ áp cho video MỚI từ 05/11/2026. Video đã duyệt trước đó giữ nguyên trạng thái, KHÔNG hồi tố, không làm lại chỉ vì luật mới.

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
   - **AI XÓA CHỮ/WATERMARK (giữ nguyên ảnh gốc, lệnh CEO tối 29/10/2026):** ảnh có logo, watermark, chữ dính trên ảnh, hoặc có dấu hiệu agency, bất kể chủ thể là ai (kể cả cá nhân riêng tư). Dùng AI chỉnh sửa để xóa CHỈ logo/watermark/chữ khỏi ảnh gốc, giữ nguyên toàn bộ phần còn lại của ảnh gốc (bố cục, người, vật, bối cảnh). Cách làm đã chốt (lệnh CEO 05/11/2026): nếu chữ/watermark nằm ở vị trí mà cắt khung không giải quyết được thì dùng AI tạo lại ảnh với tham chiếu là chính ảnh gốc, prompt "Tạo ảnh giống ảnh tham chiếu, chỉ loại bỏ chữ hoặc watermark trên ảnh" (CEO viết "loại bỏ ảnh hoặc watermark" — đọc là "chữ", theo đúng ngữ cảnh chữ/watermark). Cấm tạo ảnh AI mới tương tự từ prompt thuần không có ảnh tham chiếu — chỉ được tạo lại từ ảnh tham chiếu như cách trên. Kết quả vẫn là ảnh gốc (đã xử lý), mang cùng trạng thái bản quyền như ảnh dùng thẳng, thuộc quyết định chịu rủi ro của CEO (có khiếu nại thì gỡ/thay ngay). Không có ứng viên dùng thẳng phù hợp thì tạo AI từ prompt kịch bản thuần (không có ảnh gốc để giữ).
4. **Ảnh gốc đã xóa chữ/watermark: kiểm tra đúng thứ, không sinh ảnh mới:** soi trực quan đối chiếu output với ảnh gốc — chữ/watermark/logo đã sạch, phần còn lại giữ nguyên (bố cục, người, vật, bối cảnh không đổi). Nếu AI làm biến dạng phần còn lại của ảnh thì loại và xử lý lại, không chuyển sang sinh ảnh tương tự. Bàn giao ghi rõ URL ảnh gốc + "ảnh gốc đã xóa chữ/watermark bằng AI, vẫn là ảnh gốc" + ghi chú quyết định chịu rủi ro của CEO.
   - **CÁCH LÀM AI-ERASE ĐÃ CHỐT (lệnh CEO 05/11/2026, thay ghi chú "chưa có implementation" ngày 05/11/2026):** khi chữ/watermark nằm ở vị trí mà cắt khung không giải quyết được, dùng AI tạo lại ảnh với tham chiếu là chính ảnh gốc, prompt "Tạo ảnh giống ảnh tham chiếu, chỉ loại bỏ chữ hoặc watermark trên ảnh". Ưu tiên cắt khung trước khi dùng AI, vì cắt khung cho output thật không qua AI. Production KHÔNG được ghi bàn giao là "đã xóa bằng AI" khi chưa có output đối chiếu thật; nếu output AI làm biến dạng phần còn lại của ảnh thì xử lý lại, vẫn biến dạng thì LOẠI ứng viên đó (chọn ứng viên khác hoặc leo thang COO/QA), không ghi khống là đã xử lý.
5. **Không bao giờ ghi minh họa là "tư liệu thật"** của một sự kiện cụ
   thể, dù là ảnh tự do hay ảnh AI từ prompt. Nhân vật/sự kiện thiếu tư
   liệu đã kiểm chứng: giữ quy tắc chung chung 28/10/2026 (góc rộng,
   sau lưng/bóng mờ, bàn tay (chỉ khi là vật chứng, ví dụ bàn tay đang ký giấy tờ — không cận cảnh bàn tay để nhận diện người), vật chứng, ngoại thất, ghế trống; không cận
   mặt, không tạo chân dung người thật cụ thể). Quy tắc chung chung này chỉ áp dụng cho ảnh AI từ prompt; ảnh thật tìm được thì giữ nguyên theo mục 3, không ép về dạng chung chung. (Xem mục "Ranh giới AI cho nhân vật có tên" ngay dưới đây: nhóm A — nhân vật công chúng có nhiều thông tin công khai đã kiểm chứng — được tạo chân dung AI nếu cần thiết; nhóm B — thiếu thông tin — chỉ dùng hình chung chung; không chắc thì xếp nhóm B — sửa 05/11/2026, lựa chọn A15.)

## Ranh giới AI cho nhân vật có tên (chỉ áp cho AI từ prompt — sửa ngày 05/11/2026 theo lệnh CEO)

Luật này là nơi chuẩn cho ranh giới AI; các skill chỉ trỏ tới đây, không chép lại với diễn đạt khác. Trước khi tạo ảnh, Production phải phân loại nhân vật vào đúng một trong hai nhóm dưới đây. Nếu không chắc nhân vật thuộc nhóm nào thì xếp vào nhóm B (thiếu thông tin) — không được tự nâng lên nhóm A.

- **Nhóm A — Nhân vật công chúng, có nhiều thông tin công khai đã kiểm chứng:** ví dụ tổng thống Mỹ, cầu thủ Messi, Chủ tịch nước Tô Lâm. Dấu hiệu nhận biết: giữ vai trò công chúng rõ ràng và có nhiều thông tin, ảnh công khai đã kiểm chứng được về người đó (không phải chỉ nổi tiếng trên mạng xã hội). Với nhóm này, **có thể tạo chân dung AI nếu cần thiết** — tức là đã tìm ảnh thật mà không có ứng viên phù hợp, cảnh đó thực sự cần hình nhân vật, và prompt chỉ dùng thông tin công khai đã xác thực (vai trò, trang phục, bối cảnh vụ việc). Chân dung AI này vẫn phải ghi rõ trong bàn giao là "ảnh AI minh họa, không phải ảnh thật" — không được trình bày như ảnh thật, không được ghi là "chân dung chính xác" của người đó, vì model không đảm bảo vẽ đúng người.
- **Nhóm B — Nhân vật thiếu thông tin:** không phải nhân vật công chúng, ít hoặc không có thông tin, ảnh công khai đã kiểm chứng, hoặc đang trong vụ việc pháp lý nhạy cảm. Với nhóm này, **chỉ được:** góc rộng, sau lưng, bóng mờ, bàn tay (chỉ khi là vật chứng, ví dụ bàn tay đang ký giấy tờ — không cận cảnh bàn tay để nhận diện người), vật chứng (tài liệu, điện thoại, hóa đơn, vật liên quan vụ việc), ngoại thất, ghế trống — hình chung chung, không focus vào nhân vật. **Cấm:** cận mặt, chân dung ở trung tâm khung hình, tái tạo khuôn mặt hay nhận diện của một người thật cụ thể. **Cấm dùng tên làm chỉ dẫn ngoại hình:** KHÔNG viết tên người đó vào prompt như một chỉ dẫn để model vẽ giống người đó (vai trò, trang phục, bối cảnh vụ việc đã xác thực thì được ghi; tên thì không). Viết tên vào prompt cũng không làm model vẽ đúng người đó, chỉ làm tăng nguy cơ người xem tưởng ảnh AI là tư liệu thật.
- **Ghi rõ trong bàn giao:** mọi ảnh AI cho nhân vật có tên đều phải ghi rõ là ảnh AI minh họa, không phải ảnh thật — trình bày như ảnh thật thì QA TRẢ LẠI (xem mục TOPIC-219, bullet 6). Với nhóm A, ghi thêm "chân dung AI minh họa [tên], nhóm công chúng"; với nhóm B, ghi thêm "minh họa chung chung, nhóm thiếu thông tin".
- **Phạm vi:** ranh giới này CHỈ áp cho ảnh AI từ prompt. Ảnh thật tìm được giữ nguyên theo mục 3 (kể cả ảnh nhân vật có tên trong bài báo về đúng vụ việc), không ép về dạng chung chung. Video đã duyệt trước 05/11/2026 không hồi tố theo ranh giới này.

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
  - Ảnh có logo/watermark/chữ, dấu hiệu agency → xử lý AI xóa chữ/watermark giữ nguyên ảnh gốc theo mục 4 (cắt khung trước nếu được; không cắt được thì AI tạo lại từ ảnh tham chiếu theo cách đã chốt ở mục 4), ghi URL ảnh gốc + ghi chú xử lý.
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
- Ảnh gốc đã xóa chữ/watermark bằng AI: URL ảnh gốc, prompt đã dùng ("Tạo ảnh giống ảnh tham chiếu, chỉ loại bỏ chữ hoặc watermark trên ảnh"), ghi chú "ảnh gốc đã xóa chữ/watermark bằng AI tạo lại từ ảnh tham chiếu" + ghi chú quyết định chịu rủi ro của CEO, kết quả soi (chữ/watermark đã sạch, phần còn lại giữ nguyên).
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
  mới bắt buộc phái sinh AI. [ĐÃ BÃI BỎ — phần "hoặc chủ thể riêng tư":
  vế "chủ thể riêng tư mới bắt buộc phái sinh AI" đã bị lần điều chỉnh
  thứ hai cùng tối 29/10/2026 (bullet cuối mục này) bãi bỏ — ảnh của cá
  nhân riêng tư cũng giữ nguyên như mọi ảnh khác, chỉ xóa chữ/watermark
  nếu có; không áp vế này cho video mới.]
- Các bài học cũ vẫn còn giá trị và đã được giữ lại trong logic mới:
  không lấy từ máy quay làm query, không lấy mù top 1, soi trực quan
  bắt buộc, video ưu tiên thời lượng gần voice part.
- Điều chỉnh tối 29/10/2026 (lệnh CEO, chất lượng tạo ảnh AI của Muse quá tệ): nhánh phái sinh đổi từ "tạo ảnh AI mới tương tự" sang "AI chỉ xóa chữ/watermark, giữ nguyên ảnh gốc"; kết quả vẫn là ảnh gốc nên mang cùng trạng thái bản quyền như ảnh dùng thẳng, thuộc quyết định chịu rủi ro của CEO (có khiếu nại thì gỡ/thay ngay). [ĐÃ BÃI BỎ — vế "chủ thể riêng tư vẫn không được giữ nguyên mà dùng AI từ prompt minh họa chung chung": vế này đã bị lần điều chỉnh thứ hai cùng tối 29/10/2026 (bullet cuối mục này) bãi bỏ; không áp cho video mới.]
- Điều chỉnh tối 29/10/2026 (lệnh CEO, lần 2, bãi bỏ ranh giới loại trừ cá nhân riêng tư giữ lại trước đó cùng buổi tối): ảnh của cá nhân riêng tư cũng giữ nguyên như mọi ảnh khác — chỉ xóa chữ/watermark nếu có; ảnh tìm được có tỷ lệ khác thì tự cắt về đúng tỷ lệ cần dùng (720x1280 dọc 9:16), khi cắt phải focus đúng chủ thể chính của cảnh, soi lại sau khi cắt; quy tắc chung chung chỉ còn áp dụng cho ảnh AI từ prompt, không áp dụng cho ảnh thật tìm được.
