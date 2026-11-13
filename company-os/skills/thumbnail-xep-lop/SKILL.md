# Thumbnail xếp lớp

Tạo ảnh thumbnail tin tức kiểu lớp ảnh xếp chồng. Ảnh mặc định tỉ lệ 9:16, nhân vật lệch sang một bên, 1/4 phía dưới là nền trơn để chèn tiêu đề sau.

## Khi nào dùng

- Dùng khi user yêu cầu tạo thumbnail, ảnh bìa hoặc ảnh minh họa cho một tin hay một video.

- Dùng khi user gửi ảnh mẫu kèm nội dung và nói làm ảnh tương tự.

- Dùng khi user chỉnh sửa một thumbnail đã tạo, như đổi tỉ lệ, bỏ chữ, dời nhân vật hay đổi nền.

- Không dùng cho ảnh chân dung đơn, ảnh sản phẩm, logo hay ảnh minh họa trừu tượng.

## Đầu vào cần có

- Lấy nội dung chủ đề từ user, gồm một câu hoặc một đoạn ngắn.

- Suy ra nhân vật chính từ nội dung, hoặc lấy tên user nêu. Nhân vật công chúng chỉ cần tên, không cần ảnh.

- Tự phán đoán nhân vật chính từ nội dung, không bao giờ hỏi user. Chọn nhân vật công chúng gắn nhất với chủ đề, thường là người đứng đầu chính phủ, người đứng đầu tổ chức trong tin, hoặc người được nhắc tới trong tin. Chủ đề kinh tế Việt Nam thì mặc định là Thủ tướng. Không có nhân vật nào nổi bật thì chọn người đứng đầu quốc gia hay tổ chức chính trong chủ đề. Không tự đoán mặt người thường, và không tạo khi người thường chưa có ảnh user gửi.

- Lấy tỉ lệ từ user, mặc định là 9:16 cho TikTok, Reels và Shorts. Dùng 16:9 khi user nói rõ hoặc ảnh dùng cho Facebook hay YouTube ngang.

- Mặc định ảnh không có chữ. Chỉ thêm tiêu đề hay logo khi user yêu cầu rõ.

- Lấy ảnh mẫu phong cách khi user gửi kèm, và truyền làm ảnh reference đầu tiên trong lệnh tạo ảnh.

## Công thức ảnh chuẩn

- Xếp ảnh thành 3 lớp theo kiểu thumbnail tin tức drama.

- Lớp nền sau là bối cảnh chủ đề, như nhà máy, công trường, thành phố, cảng hay đồng ruộng. Thêm cờ hay quốc kỳ khi chủ đề liên quan tới quốc gia.

- Lớp giữa là vật thể chủ đề lớn và rõ ràng, như đoàn tàu, nhà máy, sản phẩm, xe hay biểu đồ.

- Lớp trước là nhân vật nổi tiếng cắt rời, kích thước cố định theo chuẩn ảnh Iran 13/11: chiếm khoảng 70% chiều rộng khung hình và khoảng 55% chiều cao khung hình, đỉnh đầu ở khoảng 1/3 chiều cao ảnh. Nhân vật luôn là lớp trên cùng, không có chi tiết nào phủ lên trên người nhân vật. Nhân vật luôn lệch sang cạnh trái hoặc cạnh phải, không bao giờ đặt chính giữa.

- Nhân vật lệch sang trái hoặc phải ngẫu nhiên, không mặc định một bên. Phông nền cố định ở bên phải. Nhân vật nằm bên trái thì mặt hướng về phải hoặc trực diện. Nhân vật nằm bên phải thì mặt hướng về trái hoặc trực diện.

- Nhiều nhân vật thì tất cả đứng cạnh nhau thành một nhóm ở lớp trước. Cả nhóm lệch sang trái hoặc phải, không đặt nhóm chính giữa, người nào cũng rõ mặt và không bị vật khác che mặt.

- Dùng ánh sáng drama, tương phản cao và màu sắc rực rỡ như thumbnail tin tức.

- Cấm chữ, logo và chữ trên vật thể trong ảnh. AI hay vẽ sai chính tả chữ nhỏ, như chữ trên thân tàu, nên cấm cả chữ nhỏ trên vật thể chứ không chỉ tiêu đề lớn. Ngoại lệ duy nhất: được thêm tên thương hiệu hay tổ chức ngắn gọn ở nền để chú thích rõ ngữ cảnh, khi cần.

## Quy tắc bố cục

- Nhân vật luôn lệch sang cạnh trái hoặc cạnh phải, không bao giờ đặt chính giữa. Bên trái hay phải là ngẫu nhiên, không mặc định một bên. Quy tắc này áp dụng cho cả ảnh một người và ảnh nhiều người.

- Phông nền cố định ở bên phải khung hình.

- Nền trải full toàn bộ khung hình, không có dải nền riêng ở phía dưới. Đáy nhân vật ở khoảng 3/4 chiều cao ảnh, thân dưới hoà trộn dần vào nền bằng hiệu ứng mờ dần, không cắt thẳng ngang ở lề dưới ảnh. 1/4 phía dưới giữ nền tối, trơn, không có vật thể hay chữ, để tiêu đề chèn sau vẫn đọc được.

- Ảnh 16:9 thì nhân vật hoặc nhóm nhân vật ở 1/3 trái hoặc 1/3 phải khung hình, các lớp nền trải ngang phía sau.

- Nhân vật luôn là lớp trước cùng và lớp trên cùng, mặt rõ, không bị bất kỳ chi tiết nào phủ lên trên.

- Kích thước nhân vật chính cố định theo chuẩn ảnh Iran 13/11: chiếm khoảng 70% chiều rộng khung hình và khoảng 55% chiều cao khung hình, đỉnh đầu ở khoảng 1/3 chiều cao ảnh.

## Các bước thực hiện

- Đọc nội dung rồi xác định nhân vật chính với tên đầy đủ từng người, 2 tới 3 yếu tố nền theo chủ đề, tỉ lệ và có chữ hay không.

- Gọi `media.generate_image` một lần cho một ảnh. Truyền ảnh mẫu của user, nếu có, làm entry image đầu tiên, rồi truyền entry text gồm nội dung user giữ nguyên ý cộng khối công thức phong cách.

- Viết khối công thức phong cách như sau: thumbnail tin tức kiểu lớp ảnh xếp chồng, lớp nền cố định ở bên phải và trải full toàn bộ khung hình, vật thể giữa, nhân vật tên cắt rời ở phía trước, luôn là lớp trên cùng, không có chi tiết nào phủ lên trên người nhân vật, lệch sang trái hoặc phải ngẫu nhiên, không đặt chính giữa, mặt hướng vào giữa khung hình hoặc trực diện, kích thước cố định chiếm khoảng 70% chiều rộng và 55% chiều cao khung hình, thân dưới hoà trộn dần vào nền, không cắt thẳng ngang ở lề dưới ảnh, tỉ lệ 9:16 hoặc 16:9, không có chữ, không logo, không chữ trên vật thể, được thêm tên thương hiệu hay tổ chức ngắn gọn ở nền khi cần chú thích ngữ cảnh. Nhiều nhân vật thì viết các nhân vật tên 1, tên 2 đứng cạnh nhau ở phía trước, cả nhóm lệch sang trái hoặc phải ngẫu nhiên.

- Đặt `output_format` là `jpg` và `name` theo chủ đề dạng slug, ví dụ `hoa-phat-thumbnail`.

- Đọc lại ảnh vừa tạo bằng `muse.read` để kiểm tra trước khi giao. Kiểm tra đúng tỉ lệ, nhân vật có lệch trái hoặc phải, nhiều nhân vật có đứng cạnh nhau, đáy nhân vật cách lề dưới 1/4 nếu là 9:16, còn chữ sót không kể cả chữ nhỏ trên vật thể, và nhân vật có đúng người với mặt không bị lỗi.

- Chỉnh sửa thì resume từ ảnh gần nhất, không tạo lại từ đầu. Truyền `snapshot_id` của ảnh gần nhất vào `resume_from_snapshot_id` và chỉ mô tả điểm cần đổi.

- Nếu một yêu cầu chỉnh sửa không được áp dụng thì thử lại một lần với câu lệnh tường minh có số đo cụ thể. Ví dụ phần dưới cùng của người kết thúc ở khoảng 3/4 chiều cao ảnh, chừa 1/4 phía dưới là nền xanh đậm trơn. Vẫn không được thì dừng và báo user, không thử lần 3.

- Giao ảnh bằng cách đính kèm file ảnh trong cùng tin nhắn trả lời. Nói rõ điểm chưa hoàn hảo còn sót, nếu có, và hỏi có cần sửa không.

## Quy tắc cần tuân thủ

- Không tự thêm chữ, tiêu đề hay logo khi user đã nói không cần chữ.

- Không bịa tên nhân vật. Không dùng ảnh người thường khi chưa có ảnh user gửi.

- Không bao giờ hỏi user về nhân vật. Tự phán đoán nhân vật từ nội dung, chọn nhân vật công chúng gắn nhất với chủ đề.

- Không tạo lại từ đầu khi user chỉ chỉnh một chi tiết. Luôn resume từ `snapshot_id` gần nhất.

- Tối đa 4 lần gọi `media.generate_image` cho một yêu cầu, kể cả thử lại. Quá thì dừng và hỏi user.

- Ảnh tạo ra là ảnh AI. Khuôn mặt nhân vật nổi tiếng chỉ gần giống, không phải ảnh thật, nên nói rõ với user khi giao nếu họ dùng làm thumbnail tin tức.

## Kết quả trả về

- Trả về một file ảnh JPG trong `~/workspace/imagine_media/`, đính kèm trong tin nhắn trả lời.

- Ghi chú ngắn gồm tỉ lệ, có hay không có chữ, và điểm chưa hoàn hảo nếu có.

## Ví dụ đã làm

- Ngày 13/11/2026, chủ đề Hòa Phát sẽ là nhà cung cấp thép cho đường sắt cao tốc Bắc Nam. Nhân vật là Trần Đình Long, chủ tịch Hòa Phát. Nền gồm nhà máy thép, cuộn thép, cờ Việt Nam và đoàn tàu cao tốc đỏ trắng.

- Bản 1 làm 16:9 có tiêu đề vàng và logo Hòa Phát, rồi user đổi sang 9:16 không chữ. Bản 2 là 9:16 không chữ nhưng còn sót chữ VIETNAM RAIÁY sai chính tả trên thân tàu.

- Bản 3 là user yêu cầu đưa nhân vật lên cách lề dưới 1/4. Lần 1 dùng câu ngắn thì ảnh gần như không đổi, lần 2 dùng câu tường minh là đáy người ở 3/4 chiều cao và 1/4 dưới là nền trơn thì thành công.

- Nhiều nhân vật đứng cạnh nhau đã thử thành công lần đầu ngày 13/11/2026, với chủ đề Nga Ukraine hòa bình. Putin và Zelenskyy đứng cạnh nhau, cả nhóm lệch phải, hai mặt đều rõ và không che nhau, đáy nhóm ở khoảng 3/4 chiều cao. Nếu nhóm bị đặt giữa hoặc đứng chồng lên nhau thì thử lại một lần bằng câu tường minh là đứng cạnh nhau thành một hàng, cả nhóm lệch sang phải.

- Quy tắc nhân vật luôn lệch trái hoặc phải, không đặt chính giữa, được user chốt sau khi xem các ảnh đã làm. Các ảnh thử trước đó có ảnh nhân vật đứng gần giữa, từ giờ không làm vậy nữa.

- Ba ảnh test luật mới ngày 13/11/2026 (U23 v2, Nvidia v2, Iran) đều đạt: nền full toàn bộ, thân dưới nhân vật hoà trộn vào nền, nhân vật lớp trên cùng không bị che, mặt hướng vào giữa khung hình, chữ thương hiệu ngắn ở nền khi cần (NVIDIA trên tòa nhà). Ảnh Iran là chuẩn kích thước nhân vật: đo thật chiếm khoảng 70% chiều rộng và 55% chiều cao khung hình, đỉnh đầu ở khoảng 1/3 chiều cao, rất cân đối.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Xin ảnh mẫu phong cách từ user khi muốn bám sát một kiểu thumbnail đã có, rồi truyền làm entry image đầu tiên.

- Hỏi rõ tên nhân vật khi nội dung có thể chỉ tới nhiều người, thay vì đoán một người rồi tạo sai.
