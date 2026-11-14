# Logic tìm ảnh/video — từ khóa tiếng Việt khớp kịch bản, ảnh tự do dùng thẳng, ảnh có chữ/watermark xử lý bằng AI giữ nguyên ảnh gốc

## Thứ tự ưu tiên chọn ảnh/video (lệnh CEO 14/11/2026)

Thứ tự bắt buộc khi chọn ảnh/video cho từng cảnh/part, áp cho mọi video mới:

1. **Ảnh/video thật có nguồn rõ ràng:** báo chí, mạng xã hội công khai nói về đúng chủ đề/vụ việc — ưu tiên bài báo về đúng vụ việc trước, rồi bài đăng mạng xã hội công khai.
2. **Nếu không đủ thì tìm thêm bằng Google Images:** tìm kiếm hình ảnh Google bằng từ khóa tiếng Việt khớp kịch bản (xem mục 8 — mở rộng qua Google ảnh).
3. **Chỉ sau khi đã nỗ lực ở bước 1 và 2 mà vẫn không có ảnh/video phù hợp thì mới tạo ảnh/video AI.** Ảnh/video AI dùng tối thiểu — chỉ tạo khi không tìm được ảnh phù hợp sau các nỗ lực tìm ở các nguồn khác; AI không bao giờ là lựa chọn đầu tiên.

Chi tiết thi hành: cửa chặn TOPIC-219 dưới đây (nhật ký tìm ảnh bắt buộc, QA chặn khi AI không kèm nhật ký), mục "Nguyên tắc" 1–2 (từ khóa tiếng Việt, nguồn tìm công khai), mục 8 (mở rộng Google ảnh), trần AI ≤ thật theo scene (mục 6). Luật này củng cố luật đã có (cửa chặn TOPIC-219 04/11, mở rộng Google ảnh 10/11) thành một thứ tự duy nhất — không đổi nội dung các mục đó.

## Bài học bắt buộc TOPIC-219 — 04/11/2026 (lệnh CEO, áp dụng cho mọi tài khoản Muse clone repo này)

Sai sót đã xảy ra, không được lặp lại: hai video TOPIC-219 (vụ VKS đề nghị tù chung thân cho Mr Pips và Mr Hunter, sáng 4/11/2026) đều không có ảnh thật. Bản A dùng 8 ảnh AI generic minh họa phòng xử án. Bản B chỉ dùng card chữ, không có ảnh nào. Cả hai đội sản xuất đều không quét bài báo gốc, không thử từ khóa, không soi ứng viên, mà nhảy thẳng sang AI/card.

Thực tế kiểm chứng sau đó: bài Tuổi Trẻ 4/11 về đúng vụ việc đã có ảnh thật các bị cáo tại phiên tòa (Ảnh: GIANG LONG, không logo/watermark/chữ) — đủ điều kiện dùng thẳng kèm ghi nguồn theo quyết định chịu rủi ro của CEO 29/10/2026. Sai sót không phải vì không có ảnh thật, mà vì không tìm.

Từ nay, tìm ảnh thật là cửa CHẶN trước render, không phải khuyến nghị:

1. Trước khi tạo bất kỳ ảnh nào, phải tìm ảnh thật cho từng cảnh/part CẦN ảnh (cảnh mà mọi part đã có ảnh/video riêng thì không cần ảnh cảnh chung — mục 8 dưới; part s1p1 và ảnh cảnh chung luôn phải là ảnh/video thật, không bao giờ nền trung tính) bằng từ khóa TIẾNG VIỆT khớp kịch bản, ưu tiên bài báo về đúng vụ việc, rồi bài đăng mạng xã hội công khai, rồi tìm kiếm hình ảnh. Thử nhiều cụm từ khóa đồng nghĩa, không dừng ở cụm đầu tiên, không lấy mù top 1.
2. Ghi nhật ký tìm ảnh cho mỗi ảnh cảnh chung (khi cảnh cần, mục 8) và mỗi part có ảnh/video riêng vào bàn giao (broll-plan.json + media-log.json trong thư mục project): từ khóa đã thử, ứng viên tìm được (link + nguồn + tác giả nếu có), phân loại (dùng thẳng / AI xóa chữ giữ nguyên ảnh gốc / loại), và lý do loại nếu loại. Thiếu nhật ký này thì cảnh/part đó chưa đủ điều kiện render. Ngoài danh sách `scenes`, media-log.json có thêm danh sách `parts` — 1 dòng cho mỗi part có ảnh/video riêng (ghi `partId` thật, không để `partId` = `sceneId`); part dùng nền trung tính ghi `file` (file nền) + `classification` 'trung-tinh' + ghi chú 'nền trung tính cho template <tên>' + templateId (+ `chosen` ghi file + classification như các dòng part khác); part dùng nền không cần `keywordsTried`/`candidates` (file thư viện, không phải tìm) (quyết định CEO 09/11/2026, F7).
3. Chỉ khi đã thử hết mà hoàn toàn không có ứng viên phù hợp mới được tạo AI từ prompt, và phải ghi rõ: "AI từ prompt, không có ảnh tham chiếu, đã thử các từ khóa: ..." — cấm ghi chung chung "AI generic" để lấp hồ sơ.
4. Nền xanh rêu kẻ ô vuông (không chữ) KHÔNG thay thế ảnh. Nền này là nền chờ khi chưa có ảnh, không phải ảnh minh họa. Cảnh cần ảnh cảnh chung (mục 8) mà không có ảnh thật vẫn phải có ảnh nền (ảnh thật generic, ảnh gốc đã xử lý, hoặc AI từ prompt có ghi rõ lý do — KHÔNG BAO GIỜ nền trung tính, 12/11/2026), không được render chỉ nền xanh rêu rồi gọi là "đã có ảnh". Ngoại lệ duy nhất: scene khai `cardImage` trỏ tới file thật tồn tại trong project thì CÓ ảnh — render dùng chính ảnh đó làm nền (không chữ, in BG-IMAGE-OK), không tính là thiếu ảnh. File không tồn tại, nằm ngoài project, hoặc mở không được → render in CARDIMAGE-MISSING rồi rơi về nền rêu + cờ `isMossGrid` → tính là thiếu ảnh như thường. (R4-43, 08/11/2026, DEC-051, phương án B: giữ ngoại lệ, chưa quyết giữ hay bỏ.)
5. QA chặn: nếu media table ghi 'AI từ prompt' / nền xanh rêu kẻ ô vuông (không chữ) mà không kèm nhật ký tìm ảnh thật, QA TRẢ LẠI, không duyệt im lặng, dù các cửa kỹ thuật và nội dung khác đạt. Nhãn 'AI generic' bị cấm ghi dưới mọi hình thức (xem mục 3).

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
  chung chung, ghi nguồn + giấy phép, tắt tiếng, dọc 9:16. **Ngoại lệ
  (quy tắc CEO 10/11/2026): nếu ảnh/video ứng viên lấy từ bài báo
  Việt Nam — ảnh minh họa nước ngoài trong bài báo Việt thì coi như
  đã được kiểm chứng, cần giữ lại sử dụng.** Ảnh khác
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
6. **Luật kề nhau (quy tắc CEO 09/11/2026, DEC-242 — E2, trần theo scene; đính chính DEC-244):** 2 part liền kề không lặp ảnh/video (ngoại lệ: 2 part ở 2 scene khác nhau cùng dùng 1 file nền trung tính thì được chung file; trong cùng 1 scene tối đa 1 part dùng nền trung tính); pool visual theo scene; crop chi tiết (hạn chế, chỉ khi không tìm được nguồn thật VÀ AI cũng không tạo được visual dùng được; vùng cắt có cạnh ngắn nhất ≥ 720px; tối đa 1 chi tiết/ảnh gốc; crop phải cho thấy nội dung khác hẳn; không cộng vào vế 'thật' của trần); trần AI ≤ thật tính theo scene (nền trung tính được cho là ảnh thật, mỗi scene tối đa 1 file nền); ảnh fill-in KHÔNG cộng vào vế 'thật' của trần (chỉ visual khớp nội dung + nền trung tính + ảnh bằng chứng cắt từ PDF bài báo mới tính; fill-in đếm riêng) (quyết định CEO 09/11/2026, F5); fill-in đại diện — xem skill Production, mục 'Luật kề nhau'. Luật phân nhánh + cửa bối cảnh vẫn áp cho mọi ảnh riêng, crop chi tiết và ảnh đại diện như ảnh scene. Hệ quả của trần AI ≤ thật: scene có ảnh scene là AI thì bắt buộc phải có ít nhất 1 visual thật hoặc 1 nền trung tính trong scene (không thì AI > thật, vi phạm trần). **Luật trần xuất hiện (quy tắc CEO 09/11/2026, DEC-272):** mỗi file visual nội dung chỉ xuất hiện tối đa 2 lần trong 1 video (đếm theo nội dung dhash, Hamming ≤ 10 — chuyển từ md5 theo quyết CEO 13/11/2026 (L8); 1 lần = 1 part có visual đã resolve là file đó; ngoại lệ duy nhất là ảnh/video trung tính — không áp dụng; fill-in tính vào trần như visual nội dung; ảnh bằng chứng cắt từ PDF bài báo cũng tính 1 lần như visual nội dung; bookend tính là 2 lần; crop chi tiết là file khác với ảnh gốc nên có ngân sách 2 lần riêng); preflight chặn khi vi phạm — xem skill Production, mục 'Luật kề nhau'.
7. **Ảnh nền trung tính cho part template (quy tắc CEO 09/11/2026; đính chính DEC-244):** chỉ template không có input ảnh `img`/`img1`/`img2` mới được dùng nền trung tính — **ngoại lệ DEC-268 (CEO 13/11/2026): `cutaway-standard` (mode=cutaway) KHÔNG được dùng nền trung tính dù không có input ảnh, vì luôn phải có ảnh/video phù hợp với lời đọc; ngoại lệ DEC-274 (CEO 13/11/2026): `preview-banner` KHÔNG được dùng nền trung tính dù không có input ảnh — bắt buộc ảnh/video thật từ internet/báo chí/mạng xã hội/Google ảnh theo quy trình mục 1–3 và mục 8(d) (hết đường mới AI theo TOPIC-219 hoặc báo COO, không bao giờ rơi về nền trung tính);** **mỗi scene tối đa 1 part dùng nền trung tính** (thường là part đầu của scene, TRỪ s1p1, ảnh/video cảnh chung và part preview-banner — ba chỗ này không bao giờ dùng nền trung tính, mục 8) hoặc không có; nền phải trung tính thật sự (không người/địa danh/chữ/logo/dấu hiệu nước ngoài); **nền trung tính được cho là ảnh thật** (cộng vào vế thật của trần AI ≤ thật, tính theo scene); **cùng 1 file nền được dùng lại ở các scene khác nhau trong video** (trùng trong toàn bộ video, không trùng trong 1 scene); thư viện có file `neutral-bg.json` mô tả tường minh từng file (màu, họa tiết, mood, phù hợp template nào) để chọn đúng file phù hợp part; file nền từ thư viện đã duyệt (CEO duyệt từng file + mô tả) — xem skill Production, mục 'Luật kề nhau'. Nền do AI tạo vẫn ghi `classification` 'trung-tinh' (không ghi nhãn AI) và `promptRecord` vẫn lưu prompt đầy đủ — nền được cho là ảnh thật bất kể nguồn file.
8. **Mở rộng tìm kiếm qua Google ảnh khi ảnh thật quá ít (quy tắc CEO 10/11/2026 — bài học TOPIC-287):** sau khi tìm ở báo chí + mạng xã hội mà số ảnh/video thật quá ít để dùng không bị lặp lại, PHẢI mở rộng qua công cụ tìm kiếm ảnh của Google. Từ kịch bản xác định từ khóa điểm nhấn, chủ thể, nhân vật thực, đối tượng cụ thể — rồi PHÂN LOẠI trước khi tìm: **nhóm CỤ THỂ** (tên riêng, tổ chức thật, địa danh thật, đối tượng cụ thể — vd TEDI, Ban Quản lý dự án Thăng Long, ga Ngọc Hồi, ga Thủ Thiêm, Bộ Tài chính, Bộ Xây dựng) DÙNG để tìm Google ảnh (trả về nhiều ảnh thật); **nhóm CHUNG CHUNG** (khái niệm trừu tượng, quy trình, thuật ngữ chung — vd tư vấn quốc tế, báo cáo nghiên cứu khả thi, gói thầu bị hủy, giá dự toán, đánh giá năng lực) VẪN CÓ THỂ tìm, nhưng chủ yếu ra ảnh chụp văn bản, PDF — không phải ảnh thật cụ thể; TUY NHIÊN trong đó có một số ảnh Vector Illustration, Infographic, Concept Art DÙNG ĐƯỢC làm ảnh giải thích (làm rõ thông tin, tăng tính sinh động) — quan trọng là phải lọc đúng ảnh; ảnh giải thích là minh họa, không phải tư liệu thật — nhưng tính vào vế thật của trần AI ≤ thật (vì là file thật tìm trên web, không phải AI tạo — quyết định CEO 10/11/2026). Ảnh tìm được qua Google ảnh vẫn qua cửa bối cảnh + soi trực quan + phân loại như mọi ứng viên khác — xem skill Production.

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
  - Ảnh tìm được có tỷ lệ khác 9:16: ảnh ngang → cắt thành vuông focus chủ thể chính bằng `bin/square_crop.py` (crop vuông giữa khung; pipeline chưa có model saliency nên cửa sổ vuông lấy giữa), soi lại sau khi cắt để chắc chủ thể không bị cắt đầu/cắt người; ảnh dọc khác tỉ lệ (vd 4:5) → cắt về 9:16 (luật CEO 1/11/2026, thay luật cắt 9:16 cũ).
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
  cần cắt từ clip dài hơn. `mediaType` chỉ là gợi ý để AI tạo ảnh hay
  video; nếu ảnh/video lấy từ nguồn thực thì preflight/render bỏ qua
  `mediaType`, resolve theo file thật trên đĩa (quyết định CEO
  09/11/2026, F1).

## Ảnh bằng chứng từ PDF bài báo (quyết CEO 13/11/2026 — v1 thí điểm)

- **1 ảnh bằng chứng/video, cho đúng 1 part** (part luận chứng). Không bao giờ 2 ảnh bằng chứng/video.
- **Khi nào thêm — phải đủ cả 4:** (1) video có luận chứng trung tâm rõ ràng (1 con số / trích dẫn / kết luận) mà lời đọc nêu kèm nguồn; (2) có 1 bài báo uy tín chứa đúng luận chứng đó VÀ bài có ảnh hero/thân bài gần tựa đề (ảnh nội dung, không phải logo/quảng cáo/thumbnail tin khác); (3) lấy được PDF của bài; (4) có 1 part mà lời đọc nêu luận chứng đó, hiển thị được ≥ ~4s (giọng + pauseAfterMs). **Không thêm khi:** luận chứng là tổng hợp từ nhiều nguồn; bài là ý kiến/bình luận; PDF in lỗi/paywall che tựa đề; không có part nào nêu luận chứng kèm nguồn.
- **Bài báo phải CÓ ẢNH:** không có ảnh thì chọn nguồn báo chí khác (lệnh CEO 13/11) — thử tối đa 3 nguồn; hết 3 mà không có thì BỎ ảnh bằng chứng ở video đó (ghi lý do vào media-log), không chặn dựng, không dùng ảnh tin liên quan.
- **Thêm ở đâu:** ưu tiên 1 — part ĐI SÂU ĐẦU TIÊN nêu luận chứng kèm nguồn (thường S2P1/S3P1, ngay sau hook + preview); ưu tiên 2 — part ngay sau hook nếu hook đã nêu con số; ưu tiên 3 — part kết luận/chốt. Mặc định KHÔNG đặt ở s1p1 (hook cần ảnh/video sự kiện). Part đó dùng template dưới đáy (preview-banner/keyword-block) hoặc không template — KHÔNG dùng template toàn màn hình. Thời lượng hiển thị ≥ ~4s: ưu tiên part có câu luận chứng đủ dài; nếu giọng ngắn hơn thì tăng pauseAfterMs cho đủ 4s.
- **Lấy PDF:** headless `--print-to-pdf` trước (trang không chặn); bị chặn thì xin PDF từ trình duyệt thực — builder ghi yêu cầu (URL + TOPIC_ID) vào TASKS.K + nhắn COO; main chat in PDF, file về workspace, báo lại qua COO. Giới hạn 1 lần xin/video. **CHỈ CÒN ĐƯỜNG PDF — chụp ảnh màn hình đã loại khỏi logic (lệnh CEO 13/11: chỉ cho tỉ lệ 16:9, phương án tồi).** Không lấy được PDF thì bỏ ảnh bằng chứng (không chặn dựng).
- **Tỉ lệ trang — 3 trường hợp (lệnh CEO 13/11, sửa cùng ngày):** (1) trang có tỉ lệ rộng/cao trong khoảng **3:4 (0,75) đến 4:3 (1,33)** (trang Letter/A4 thường nằm trong khoảng này): render NGUYÊN TRANG bằng `bin/pdf_crop.py --whole-page` (200 DPI) → PNG giữ nguyên tỉ lệ trang, KHÔNG cắt, **KHÔNG cần cảnh báo lỗi gì**; (2) trang **DÀI HƠN 3:4** (tỉ lệ < 0,75): **GIỮ LẠI, cắt ảnh 3:4** bằng `bin/pdf_crop.py --full-page` (cửa sổ trên cùng, đầy chiều rộng — tựa đề/sapo ở đầu trang) → PNG 720×960; (3) trang **RỘNG HƠN 4:3** (tỉ lệ > 1,33, trang quá ngắn): **LOẠI NGUỒN NÀY, tìm nguồn báo khác** (tối đa 3 nguồn). **Chỉ bỏ trang quá ngắn.** Trang dùng làm bằng chứng phải là trang CỦA BÀI (tựa đề/sapo/thân bài) — trang nào lẫn mục tin liên quan/sidebar thì không dùng, chọn trang khác của cùng bài hoặc đổi nguồn (QA kiểm: dính tin khác thì TRẢ LẠI).
- **Ghi log (dòng part, `classification` = `chup-man-hinh`):** file + `link` (URL bài báo) + `source` (tên báo) + `articleDate` (ngày đăng) + `pdfPage` (số trang đã lấy) + `captureDate` (ngày lấy PDF). Part bằng chứng không cần `keywordsTried`/`candidates` (bài đã chọn từ danh sách nguồn của kịch bản, không tìm bằng từ khóa) — như part nền trung tính. `mediaSource.source` trong plan = tên báo.
- **Đếm:** ảnh bằng chứng tính vào vế **thật** của trần AI ≤ thật (mục 6) và tính **1 lần** vào trần DEC-272 như mọi visual nội dung. Preflight chặn khi: thiếu 1 trong 4 trường (link/source/articleDate/pdfPage), video có 2 part bằng chứng trở lên, file bằng chứng là cả trang dài chưa cắt (tỉ lệ < 0,75 — phải cắt 3:4), hoặc file rộng hơn 4:3 (trang quá ngắn — phải loại nguồn).

## Hồ sơ bàn giao cho QA (mỗi media, thiếu trường nào thì chưa đủ điều kiện render)

- Ảnh dùng thẳng: nguồn, link trang file, giấy phép đã kiểm chứng
  (với ảnh tự do) hoặc ghi nguồn báo/trang + ghi chú "dùng trực tiếp
  theo quyết định CEO 29/10/2026" (với ảnh báo/mạng xã hội không
  logo/watermark/chữ), tác giả (nếu giấy phép yêu cầu), ghi chú soi
  trực quan khớp kịch bản.
- Ảnh gốc đã xóa chữ/watermark bằng AI: URL ảnh gốc, prompt đã dùng ("Tạo ảnh giống ảnh tham chiếu, chỉ loại bỏ chữ hoặc watermark trên ảnh"), ghi chú "ảnh gốc đã xóa chữ/watermark bằng AI tạo lại từ ảnh tham chiếu" + ghi chú quyết định chịu rủi ro của CEO, kết quả soi (chữ/watermark đã sạch, phần còn lại giữ nguyên).
- Ảnh AI từ prompt: prompt + ghi chú "AI từ prompt, không có ảnh tham
  chiếu".
- Ảnh bằng chứng từ PDF bài báo: URL bài báo + tên báo + ngày đăng
  bài + số trang PDF đã lấy + ngày lấy PDF (xem mục Ảnh
  bằng chứng; preflight chặn khi thiếu URL/tên báo/ngày đăng/trang lấy
  hoặc file ngoài khoảng tỉ lệ 3:4–4:3).
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


## Nguồn credential cho API stock (quyết CEO 11/11/2026)

`search_media.py` lấy key Pixabay/Pexels theo thứ tự: (1) biến môi trường `PIXABAY_API_KEY` / `PEXELS_API_KEY` nếu có; (2) không có thì đi đường Secure Vault qua helper của connector `custom.pixabay` / `custom.pexels` (nguồn báo là `pixabay (vault)` / `pexels (vault)`). **Chuẩn vận hành chính thức của công ty là đường vault** — không đặt key qua biến môi trường trong vận hành thật; env chỉ dùng tạm khi gỡ lỗi và phải gỡ ngay sau đó, vì env thắng thầm lặng trước vault và làm mọi kiểm tra phía vault báo bình thường trong khi key thật đang dùng là key env.
8. **Ảnh/video cho cảnh chung, part s1p1 và part preview-banner (quy tắc CEO 12/11/2026; preview-banner bổ sung DEC-274, 13/11/2026):** (a) cảnh mà MỌI part đã có ảnh/video riêng (kể cả cảnh chỉ có 1 part đã có) thì KHÔNG tìm/tạo ảnh/video cho cảnh chung — nó bị file riêng của part che hết, chỉ tốn tài nguyên; (b) cảnh có cả part có và part không có ảnh/video riêng: lấy 1 ảnh/video của part đại diện nhất cho cả cảnh làm ảnh cảnh chung (video thì trích 1 khung hình), không tìm thêm; phải qua luật kề nhau và trần 2 lần/video, không qua thì xử lý như (c); (c) cảnh không part nào có ảnh/video riêng: BẮT BUỘC tìm ảnh/video cho cảnh chung, không để màn hình đen; (d) ảnh/video cảnh chung, part s1p1 và part dùng template preview-banner KHÔNG BAO GIỜ là ảnh/video trung tính (thư mục `neutral-bg/`) — phải là ảnh thật từ báo chí, mạng xã hội, Google ảnh, đúng nội dung chủ đề, theo đúng quy trình mục 1–3 (hết đường mới đến AI theo TOPIC-219, tuyệt đối không rơi về nền trung tính). Chi tiết và preflight: skill Production, mục 'Ảnh/video cho cảnh chung và part s1p1'.
