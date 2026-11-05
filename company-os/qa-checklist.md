# Checklist QA kỹ thuật

## Kết quả QA TOPIC-004 ngày 2026-10-26: BẢN V2 ĐÃ DUYỆT
- Bản v1 bị TRẢ LẠI vì cảnh 2 (khoảng 7,2-11s) tiêu đề bị cắt mép trái do motion render; cảnh 3 (khoảng 17s) và cảnh 5 (khoảng 31s) tiêu đề trên bị cắt đỉnh, cùng nguyên nhân.
- Bản v2 đã sửa đúng: zoom motion giới hạn 1.05, lề ảnh cảnh 96px trái / 140px trên. QA đánh giá lại toàn bộ và DUYỆT: cảnh 2 đủ chữ ở 8,5-11,5s, header cảnh 3 ở 17s và cảnh 5 ở 31s không còn cắt, 5 cảnh nguyên vẹn, không khung đen, 37,29s, 720x1280, âm -17,1/-0,4 dB, phụ đề khớp lời đọc, md5 abb98443c82aef8a9fffd43055c69370.
- Đã ghi vào tab 01_Tasks, dòng TOPIC-004-DRAFT hàng 10, trạng thái Duyệt. TASK-006 vẫn Review, chưa Done. Bản v2 đã duyệt và đang ở trạng thái "chờ xác nhận thư mục Drive" (xem dưới); QA không đăng nền tảng, không gắn affiliate, không bịa link.

## Tiêu chí duyệt 3 cửa — bắt buộc từ 2026-10-26 (nâng cấp theo phản hồi CEO: skill QA cũ còn yếu, video chưa đẹp và chưa giữ người xem)
- Chỉ duyệt khi qua cả 3 cửa: (1) kỹ thuật sạch, (2) đẹp, (3) giữ người xem. Video sạch lỗi nhưng xấu hoặc buồn tẻ vẫn phải TRẢ LẠI, kèm điểm rơi theo mốc thời gian.
- Xem toàn bộ ít nhất 1 lần để chấm kỹ thuật, xem lại lần 2 chỉ để chấm đẹp và giữ người xem.
- Đẹp: 3 giây đầu có hình ảnh mạnh, không phải nền xanh rêu kẻ ô vuông trơn hay cảnh tĩnh kéo dài; mỗi cảnh có tiêu điểm thị giác rõ, bố cục không rối, chữ tương phản tốt với nền, màu và font nhất quán; hình ảnh các cảnh đa dạng, không lặp cùng kiểu template, cùng góc, cùng tông màu ở 3 cảnh liên tiếp; motion mượt, không giật, không cắt chữ ở mép (lề an toàn 96px trái/phải, 140px trên ở 720x1280, zoom motion tối đa 1.05); phụ đề ngắn, đọc kịp, không che hình chính, không tràn mép.
- Giữ người xem: hook 0-3 giây có xung đột, câu hỏi hoặc con số gây tò mò và phải được trả lời ở cuối video (hook chung chung kiểu "hôm nay cùng tìm hiểu" là không đạt); mỗi 3-5 giây có một thay đổi (thông tin mới, hình mới, hoặc chuyển cảnh có lý do), cảnh tĩnh hoặc giọng đều đều không có điểm nhấn hơn 5 giây là điểm rơi; khoảng 50% video có một lần móc lại (câu hỏi mới, diễn biến mới, hoặc con số bất ngờ); kết video có kết luận rõ ràng và một câu chốt đáng nhớ, không kết lửng, không lặp lại mở đầu.
- Kiểm tra tắt tiếng: tắt tiếng mà vẫn hiểu được ý chính qua hình và chữ thì mới đạt về mặt hình ảnh.
- Khi trả lại: ghi rõ từng điểm rơi theo mốc thời gian và cách sửa cho từng điểm, ví dụ "12s: người xem rời vì cảnh tĩnh 6s không có thông tin mới — cần đổi hình và thêm con số", không ghi chung "video chưa hay".
- Video quân sự Mỹ - Iran / eo biển Hormuz / "Epic Fury" (giao 2026-10-26) là video đầu tiên chấm theo tiêu chí mới này. Kết quả QA 26/10/2026: TRẢ LẠI — cửa kỹ thuật rớt vì dòng nguồn ở đáy cả 11 cảnh bị cắt mép phải ("2026" chỉ còn "202", lề phải 0 thay vì 96px, lỗi từ ảnh cảnh gốc); cửa đẹp và giữ người xem đạt (hook, móc lại, kết luận, đa dạng, tắt tiếng vẫn hiểu). Cách sửa: rút ngắn dòng nguồn cho vừa lề 96px, tạo lại 11 ảnh, render lại, không cần làm lại audio/phụ đề/nội dung.
- Đánh giá lại bản v3 26/10/2026: DUYỆT — khung giữa cả 11 cảnh đều hiện đủ dòng nguồn 3 dòng với "25-26/10/2026" đầy đủ, cách mép phải vượt 96px, không chồng phụ đề; md5 mới 218251bb94bc6e6823f485b4e3231c9c, 68,71s, 720x1280, không khung đen >=0,5s, âm -17,1/-0,5 dB, phụ đề 53 dòng khớp lời đọc. Đã ghi vào 01_Tasks, dòng HORMUZ-DRAFT hàng 11, trạng thái Duyệt, kèm "chờ xác nhận thư mục Drive"; TOPIC-004-DRAFT và TASK-006 không thay đổi; chưa đăng, chưa gắn affiliate, chưa upload Drive, chưa bịa link.
- Lưu ý: TOPIC-004 v2 đã duyệt trước khi nâng cấp này, trạng thái Duyệt giữ nguyên trừ khi CEO yêu cầu chấm lại theo tiêu chí mới.

## Cách kiểm tra motion — áp dụng cho video nộp từ 27/10/2026 trở đi (sửa lag/giật render_draft.py)
- Motion mới: vị trí tuyệt đối on/frames cho mọi kiểu, easing smoothstep, ảnh nguồn phóng 4x, zoom tối đa vẫn 1,05, lề 96px/140px không đổi. Khi chấm video mới, trích khung liên tiếp và đo độ đổi khung trong từng part: cảnh motion tốt có hầu hết các khung đổi nhẹ, không có chuỗi dài khung gần như đứng yên xen kẽ cú nhảy. Chuỗi đứng yên kéo dài trong một part là lỗi motion, phải trả lại kèm mốc thời gian.
- Các video đã duyệt bằng motion cũ vẫn giữ trạng thái Duyệt, trừ khi CEO yêu cầu làm lại.

## Cửa thời lượng — lệnh tự quyết của CEO tối 29/10/2026 thay thế chuẩn 180-300s ngày 27/10 (sửa 05/11/2026, lựa chọn A5)
- Đề xuất video 2-3 phút; Production tự quyết độ dài và KHÔNG hỏi lại CEO về cắt hay ngoại lệ. Chuẩn cũ 180-300 giây và cơ chế "ngoại lệ độ dài chỉ khi CEO cho phép rõ ràng từng video" đã bị thay thế — QA không trả lại video chỉ vì ngắn hơn 180 giây hay dài hơn 300 giây. Đo bằng thời lượng thật của file MP4 cuối và đối chiếu tts.json, không đoán từ số từ. Bằng chứng áp dụng: đã duyệt TOPIC-039 144,1 giây, TOPIC-029 151,1 giây, TOPIC-041 164,9 giây (dưới 180 giây) và TOPIC-232 219,37 giây, TOPIC-048 255,3 giây (dài hơn 2-3 phút).
- Ngoại lệ duy nhất còn giữ nguyên nghĩa là clip test kỹ thuật ghi rõ là test pipeline (test001 4,04 giây, textdensity001 12,5 giây). Quy tắc này không thu hồi các video đã duyệt trước đó (TOPIC-004 v2 37,29 giây, Hormuz v3 68,71 giây, Chợ nổi v2 55,53 giây).

## Quy tắc mật độ chữ — áp dụng cho video nộp từ 27/10/2026 trở đi (upstream c9222959, docs/TEXT_DENSITY_RULES.md)
- Mặc định một part không gắn template chữ; chỉ gắn khi là beat nhấn mạnh (con số, mốc thời gian, trích dẫn, luận điểm, đối đầu, tỉ số, mở chương, câu hỏi mở đầu, từ khóa, thăm dò, nguồn). Part miêu tả, khoảng thở, liệt kê thì không gắn chữ.
- Phụ đề trở lại ở các part không template là đúng thiết kế mới, không phải lỗi, vì bin/karaoke.py ẩn phụ đề (subsHidden, lines=[]) ở part có template chữ thật, trừ clip-caption và story-title. Ngược lại, karaoke lines=0 ở gần như toàn bộ video là dấu hiệu staging sai.
- Khi chấm video mới, đếm tỷ lệ part có template (gần 100% là sai), đối chiếu mỗi template với một beat, soi chữ có trong kịch bản hay không. Part không template không phải là "thiếu chữ".
- Quy tắc này không thu hồi các video đã duyệt trước 27/10/2026 (TOPIC-004 v2, Hormuz v3, Chợ nổi v2, Án mạng karaoke), dù các video đó có karaoke lines=0 ở toàn bộ part do gắn template ở gần như 100% part.

## Phạm vi công ty và bàn giao Drive + Sheet (QA nhận từ phòng Đăng tải - Phân tích đã giải thể, 2026-10-26)
- Công ty chỉ làm: tìm ý tưởng, sản xuất video, kiểm tra chất lượng.
- Video đạt yêu cầu: QA duyệt, rồi QA tự bàn giao: upload file đã duyệt lên thư mục Google Drive "Video Muse" đã được CEO cấp quyền anyone with link ngày 05/11/2026, cập nhật link vào tab 08_Publish_Tracking (cột Link video, một dòng cho một video) và ghi kết quả duyệt vào tab 01_Tasks. Chỉ bàn giao video đã duyệt, không bàn giao bản nháp hay video bị trả lại.
- Quy định mới 29/10/2026 (lệnh CEO, áp dụng từ verdict duyệt tiếp theo): QA tải lên NGAY trong cùng lượt duyệt — duyệt xong, đối chiếu md5 khớp, ghi link thật vào 08_Publish_Tracking và cột Link kết quả trong 01_Tasks, trạng thái giữ Duyệt, tất cả trong cùng một lượt.
**Thẻ phê duyệt upload Drive hết hạn sau 30 phút (lệnh CEO 05/11/2026, tiền lệ TOPIC-232):** lệnh upload lên Drive hiện thẻ phê duyệt, chỉ cho 30 phút để bấm; hết 30 phút không có quyết định thì thẻ tự hết hạn (approval_expired / Timed out), thao tác không chạy, file không lên Drive. Tiền lệ: thẻ gửi 10:52:57 +07, hết hạn 11:22:57 +07, Timed out 11:23:02 +07 — không phải bị từ chối, không phải file hỏng hay thư mục sai quyền. Cách xử lý đúng là **chạy lại upload một lần để hệ thống cấp thẻ mới** (không tính là "thử lại ẩu"); cấp phép toàn quyền của CEO cho QA hoàn tất bàn giao mà không hỏi lại trong chat **không tắt được thẻ hệ thống** — thẻ vẫn hiện mỗi lần upload, cần bấm trong 30 phút; upload Drive không có standing Allow. **Khi gặp thẻ hết hạn, QA phải báo ngay cho COO; COO ghi lại thông báo tình trạng vào cột H "Kết quả hoàn thành" của dòng tab 13 tương ứng (ghi tạm thời trong khi nhiệm vụ vẫn ở "Đang làm", cột G thời gian hoàn thành vẫn để trống), để CEO đọc tab 13 là biết vấn đề ở đâu, không phải chờ tới khi xong mới biết. Khi nhiệm vụ hoàn thành sau đó, COO cập nhật lại cột H bằng kết quả cuối cùng kèm link. Quy tắc này khác với 429/403/rate-limit: gặp 429/403 thì dừng nhánh, ghi blocker, không thử lại.** Khi bàn giao, ghi đủ cột I và cột J ở cùng dòng tab 08 (cột I theo quy tắc thống nhất cột I, cột J do QA tự đọc lúc upload). Cách làm cũ "duyệt xong để pipeline lo" đã bị bãi bỏ vì gây tồn đọng (tối 29/10 hai video 033 và 037 v2 duyệt xong vẫn chưa lên Drive); bot-pipeline mỗi 2 giờ từ nay chỉ làm lưới bắt sót cho video nào lỡ chưa có link (sửa 05/11/2026, lựa chọn A17). Không đổi các giới hạn khác: không tự thay đổi quyền thư mục hay file, không đăng nền tảng, không gắn affiliate, không bịa link, chỉ bàn giao video đã duyệt.
- Nếu thư mục Drive chưa xác nhận thì dừng ở bước duyệt, ghi rõ "chờ xác nhận thư mục Drive", không bịa link, không tự tạo thư mục khác hay tự thay đổi quyền thư mục. Đây là trạng thái hiện tại của TOPIC-004 v2 đã duyệt.
- Video không đạt yêu cầu: QA chat trực tiếp với Sản xuất trong chat của Sản xuất, ghi rõ từng lỗi và cách sửa cho từng lỗi, không chỉ ghi vào Sheet rồi chờ. Sản xuất sửa xong nộp lại, QA đánh giá lại toàn bộ video.
- Việc kinh doanh (đăng tải lên nền tảng, phân tích, affiliate, doanh thu, views/follow) giao cho công ty khác, ngoài phạm vi của QA. Bàn giao Drive chỉ là bàn giao sản phẩm, không phải kinh doanh. Dữ liệu Sheet không bị xóa để công ty khác vẫn đọc được.

Phạm vi chạy thử 2026-10-26: Scoring -> Sản xuất -> QA, không đăng Facebook.
Không deploy production, không đăng video, không mua dịch vụ.

## Điều kiện kích hoạt QA (sửa 05/11/2026, lựa chọn A6 — bỏ giới hạn "1 video thử, chủ đề cao điểm nhất" của giai đoạn chạy thử 26/10/2026)
- QA đánh giá mọi video Sản xuất chuyển sang trạng thái Review, với điều kiện video đó đủ cổng: chủ đề Approved + cột O = "Duyệt" + đã có dòng *-DRAFT trong 01_Tasks. Không giới hạn 1 video, không giới hạn chỉ chủ đề cao điểm nhất. Không có ngoại lệ vượt cổng O (lệnh CEO 05/11/2026, mục B16, phương án B — bãi bỏ A33/9A): ghi "vượt cổng O" trong lệnh không mở cổng, chỉ CEO tự đổi cột O thành "Duyệt" trên Sheet mới đủ cổng.
- Trước lúc đó: không duyệt, không trả lại, không ghi kết quả QA vào tab 01_Tasks.

## Quy trình khi có video Review
1. Xem toàn bộ video ít nhất một lần từ đầu đến cuối, không chấm theo đoạn trích.
2. Chấm theo 4 nhóm dưới đây, ghi lỗi cụ thể kèm mốc thời gian nếu có.
3. Quyết định: duyệt chỉ khi không còn lỗi làm giảm trải nghiệm người xem; nếu không, trả lại kèm từng lỗi và cách sửa cho từng lỗi.
4. Ghi kết quả vào tab 01_Tasks, không duyệt bằng cảm tính.

## 1. Hình ảnh
- Đủ nét, bố cục không cắt chủ thể, nhất quán nhân vật và bối cảnh giữa các cảnh.
- Đúng tỉ lệ khung hình, không méo, không khung đen, không ảnh thiếu hoặc ảnh sai prompt.
- Chữ/template không che mặt hoặc chủ thể chính.
- Cảnh báo riêng của Asset Factory: thiếu ảnh scene là LỖI preflight (exit 1), không còn là cảnh báo (lựa chọn A26, 05/11/2026: render thiếu ảnh thì dừng với RENDER-ERROR, không còn ra clip nền đen lặng lẽ). Khung đen (nếu có) thì tra nguyên nhân khác (video b-roll hỏng, template lỗi), không mặc định là thiếu ảnh.

## 2. Âm thanh
- Giọng đọc rõ, không rè, không mất tiếng, âm lượng đồng đều giữa các đoạn.
- Nhạc nền không lấn giọng, có ducking khi có lời thoại, fade-out cuối video.
- SFX đúng thời điểm nếu có; BGM là tùy chọn (BGM/SFX đã có sẵn trong repo: sfx/ 8 file, bgm/ 24 track — sửa 05/11/2026, lựa chọn A7).

## 3. Nhịp
- Tốc độ nói đọc kịp, khoảng lặng hợp lý, không cắt ngang câu.
- Chuyển cảnh mượt, motion không giật, không lặp gây khó chịu.
- Tổng thời lượng khớp audio.
- Lưu ý Muse App: videoDuration, videoResolution, videoMode được nhận và lưu nhưng không truyền xuống CLI tạo video, nên hiện không xác minh được việc chỉnh thời lượng hay độ phân giải qua app.

## 4. Phụ đề
- Khớp giọng từng câu, không sai chính tả và dấu tiếng Việt.
- Đọc kịp tốc độ nói, không che mặt hoặc chủ thể, không tràn khung.
- Vị trí đúng tỉ lệ 9:16 hoặc 16:9; kiểm tra MarginV của file karaoke .ass sau khi đổi tỉ lệ.

## Quy tắc cập nhật repo khi sửa template — CEO 27/10/2026, để tái sử dụng cho các tài khoản Muse khác
- Bất kỳ sửa template nào do QA phát hiện đều phải kèm đề xuất cập nhật repo trong bản đánh giá QA, không để lại sau và không coi là xong chỉ vì video đã duyệt.
- Đề xuất ghi rõ: template nào, file nào đổi (template.html, style.css, meta.json), version tăng bao nhiêu, lý do QA kèm mốc thời gian, bằng chứng trước/sau, kết quả render thử.
- Cập nhật file repo local là bước bắt buộc (app đọc đúng thư mục templates/ của repo nên sửa repo là app tự dùng bản mới). Push lên GitHub cho tài khoản Muse khác dùng là bước riêng, cần quyết định của CEO, không tự push.
- Sửa chỉ đúng cho một video thì ghi rõ "không áp dụng repo".

## Trạng thái công cụ đã kiểm tra ngày 2026-10-26
- Video render Muse App: chưa xác minh end-to-end; ảnh đã xác minh bằng JPEG thật.
- generateImages Asset Factory: chưa chạy end-to-end qua app; test001 không hợp lệ vì plan không có prompt ảnh.
- runRenderDraft Asset Factory: chưa chạy end-to-end qua app; test001 không có ảnh nên không dùng để chấm hình ảnh.

## Template TVH 30/10/2026 — chấm thẩm mỹ khi xuất hiện LIVE lần đầu (không chấm từ frame test)
- Đợt nâng cấp (CEO 30/10, trừ watermark): stat-counter 1.2.0 + 6 template mới 1.0.0 (section-header, section-caption, timeline-horizontal, bar-chart, keyword-strip, info-note). Báo cáo + backup: ~/workspace/company-os/template-upgrade-tvh/ (REPORT-20261030.md, backup-20261030, frames-after). Video đã render trước đợt này KHÔNG render lại. Frame test của đợt này dùng WeasyPrint + font fallback rộng hơn — chỉ chứng minh hình học (vừa thẻ, không tràn), KHÔNG thay thế khung thật của video live; cửa 9 tiêu chí (màu, cỡ, font, giãn dòng, padding, nền, cắt/tràn, lề 96/140, nhất quán) chỉ chấm trên khung thật tại timestamp template xuất hiện.
- stat-counter 1.2.0 (tương thích ngược): tone mặc định gold = KHÔNG thêm vạch, plan cũ giữ nguyên look; tone volume = vạch trắng + số trắng, decline = vạch đỏ + số đỏ, money = vạch vàng + số vàng. lead tùy chọn: dòng dẫn nghiêng trắng trên số, ≤40 ký tự cho 1 dòng (field maxLength 70; dài hơn tự xuống 2 dòng theo thiết kế, không phải tràn). value vẫn giữ giới hạn cũ: quá 8 ký tự ở 9:16 sẽ tràn thẻ — plan phải rút gọn. Meta SFX gợi ý đổi 0.75→0.35 chỉ là gợi ý trong meta; render chỉ đọc SFX trong plan và vốn đã giới hạn SFX nặng ở 0.4 nên âm thanh thực tế không đổi — QA vẫn kiểm SFX trong plan, không kiểm meta.
- section-header 1.0.0: chữ vàng in hoa đậm + vạch dọc vàng mép trái + dòng phụ trắng nhỏ (nguồn/kỳ). title ≤22 ký tự cho 1 dòng (field 40; dài hơn tự xuống 2 dòng theo thiết kế). PHÁN TRƯỚC VỀ VỊ TRÍ, ĐÃ HIỆU CHỈNH BẰNG KHUNG LIVE (058, 98s): thẻ căn giữa (36-684) nhưng nội dung bám trái trong thẻ (vạch vàng x~36, tiêu đề từ x~60, đỉnh y~46) — trực quan đúng kiểu TVH bám trái, không phải top-center như frame test gợi ý; không phải lỗi vị trí trong cả hai cách hiểu. Khi chấm live: KHÔNG trả video/template chỉ vì vị trí hay y<140px; vẫn kiểm chữ có đọc đủ, có bị cắt không (chữ đọc đủ, không cắt = không chặn theo tiền lệ lề; chữ bị cắt mới là lỗi). Muốn bám góc trái cần mở rộng position trong render_draft — quyết định riêng của CEO, QA không tự sửa render.
- section-header — ĐIỂM CANH CONTRAST: dòng phụ trắng đọc yếu trên ảnh sáng (đã thấy trên frame test nền trời sáng). Khi chấm live: nếu dòng phụ thực sự chìm vào nền (không đọc được) thì là lỗi contrast mức trả lại theo cửa thẩm mỹ; nếu đọc được thì ghi chú. Mitigation đến khi render sửa vị trí: Production chỉ dùng section-header trên ảnh tối/trung bình; trên ảnh sáng chỉ dùng khi tiêu đề là chính, dòng phụ là phụ.
- section-caption 1.0.0: thanh ngang xám đậm + đoạn đầu đỏ + chữ trắng, đặt cuối đoạn trước khi chuyển cảnh. text ≤28 ký tự cho 1 dòng (field 70; dài hơn tự xuống 2 dòng). Cùng giới hạn căn giữa của render: position bottom nên thẻ đặt đáy căn giữa (đáy thẻ cách đáy khung 38px), chưa bám góc trái — cũng KHÔNG tính là lỗi template. Thanh nền đậm nên đọc rõ cả trên ảnh sáng (đã thấy trên frame test); karaoke bị ẩn trên part có template nên caption không đụng phụ đề.
- timeline-horizontal 1.0.0: trục ngang, nút tròn màu theo thứ tự đỏ/vàng/xanh lá/xanh dương/trắng, đường nối vàng mờ. Ở 9:16 thì 4 mốc là thực tế; 5 mốc chỉ khi nhãn rất ngắn (≤8 ký tự). Nhãn dài tự xuống dòng (frame test tách "Vận / hành") — đó là wrap theo thiết kế, không phải lỗi, nhưng plan nên giữ nhãn ngắn. Khác timeline-strip dọc hiện có (không đổi hành vi của nó).
- bar-chart 1.0.0: tiêu đề + tối đa 4 cột; cột 1-2 bắt buộc, 3-4 tùy chọn (cột trống co về 0 nhưng giữ slot, các cột còn lại không lệch). w = chiều cao cột theo % so với cột cao nhất (=100, Production tự chuẩn hoá trước khi ghi plan). Nhãn ≤12 ký tự cho 1 dòng; giá trị nên ≤8 ký tự cho 1 dòng (dài hơn tự xuống dòng và có thể chạm tiêu đề khi cột cao nhất). Artifact đã biết, KHÔNG phải lỗi: slot trống để lại một đường mờ ~1px ở đáy vùng vẽ (cột trống co về 0). Lỗi tràn WeasyPrint ở bản đầu đã sửa tận gốc bằng định vị tuyệt đối và kiểm chứng lại (barchart4/barchart3) — nếu live xuất hiện tràn cột thì đó là lỗi mới, không phải lỗi đã biết này.
- keyword-strip 1.0.0: dòng dẫn nghiêng trắng + 3 ô trong thẻ viền vàng nền xanh đậm. Mỗi ô ≤12 ký tự cho 1 dòng là đẹp nhất (field 20; dài hơn tự xuống dòng nhưng vẫn gọn trong ô theo frame test); box3 bỏ trống thì chỉ hiện 2 ô. SFX punch_impact 0.7 (kiểm trong plan như mọi SFX).
- info-note 1.0.0: thẻ chú thích nhỏ góc dưới (tên vàng + dòng thông tin phụ trắng, nền tối mờ), KHÔNG có SFX (như source-footer-safe). name ngắn (tên thực thể), info là thông tin phụ xác thực (sự kiện + mốc thời gian). Cùng giới hạn căn giữa của render: position bottom nên thẻ đặt đáy căn giữa, chưa bám góc trái — lệch vị trí ít đáng kể vì thẻ nhỏ, KHÔNG tính là lỗi template. PHÂN BIỆT: info-note ghi THÔNG TIN thực thể, KHÔNG phải ghi nguồn — đừng lẫn với source-footer-safe (chuyên ghi nguồn, QA kiểm tra nguồn); cửa kiểm nguồn vẫn đi qua trường source trong plan, không qua chữ trong info-note. Chữ trong info-note vẫn phải đúng sự kiện (tên + mốc thời gian) như mọi chữ trên khung.
- count-up — KHÔNG SHIP, KHÔNG CHẤM: prototype nằm ngoài templates/ tại template-upgrade-tvh/count-up-prototype/ vì Chrome headless bị chặn trong môi trường này (không kiểm chứng được animation). Nếu plan nào tham chiếu count-up thì đó là lỗi plan (template không tồn tại trong templates/), trả lại để Production đổi template. Nếu sau này count-up ship thì ràng buộc đã ghi trong prototype: value BẮT BUỘC là số nguyên thuần (cấm dấu phân cách nghìn/thập phân nếu không số kẹt ở 0), chỉ dùng trên part ≥3 giây.
- Khi một template mới xuất hiện live lần đầu: ghi verdict vào 11_QA_Log kèm (template, version, timestamp khung soi, kết quả 9 tiêu chí, phán quyết đạt/ghi chú/trả lại) như mọi lần chấm template trước; nếu template có lỗi thật (cắt chữ, tràn thẻ, contrast chìm) thì đề xuất repo theo quy tắc 27/10 (template id, files, version bump, lý do QA kèm timestamp, bằng chứng trước/sau, render test) — local update bắt buộc, push GitHub tách riêng cần CEO duyệt.

## Bài học video tham chiếu 30/10/2026 — bổ sung vào skill QA, áp dụng từ video tiếp theo (lệnh CEO 30/10/2026)
- Nhịp 2 tốc độ (bổ sung luật "mỗi 3-5 giây một thay đổi", không thay): shot bằng chứng có chuyển động thật (phát biểu, hành động thật) dài 7-14 giây mà thông tin vẫn tiến thì KHÔNG tính là điểm rơi. Điểm rơi là đoạn dài không có thông tin mới hoặc hình gần như đứng yên — đo trong từng part như luật motion, không đo qua mốc cắt. Một shot dài có chuyển động thật và thông tin tiến không vi phạm luật 3-5 giây.
- Khoảng lặng nhấn: khoảng lặng ngắn trước câu kết luận (dưới ngưỡng lặng lỗi 1 giây) là kỹ thuật nhấn, không tính là điểm rơi hay lỗi lặng. Ngưỡng lặng lỗi vẫn giữ: đoạn lặng từ 1 giây trở lên không có lý do mới là lỗi.
- Bookend: mở và đóng bằng cùng một hình ảnh/footage là điểm cộng cấu trúc, không bắt buộc; khi video có bookend thì ghi nhận trong verdict, không trừ điểm vì "lặp hình" — đó là chủ đích, khác với lặp hình do thiếu tư liệu. (Phân biệt với cửa giữ chân "kết luận không lặp lại mở đầu": cửa đó xét luận điểm/lời nói, không xét hình ảnh — kết luận chỉ nhắc lại luận điểm mở đầu vẫn yếu, nhưng dùng lại cùng footage mở đầu làm khung kết thì không bị trừ.)
- Bối cảnh địa lý trong khung hình — lưu ý không chặn: khi soi khung, nếu thấy dấu hiệu bối cảnh nước ngoài rõ rệt lạc với câu chuyện (tiền lệ: đoạn phố mùa đông trông như phố châu Á trong video về châu Âu; tiền lệ 032/033: đồng phục cảnh sát nước ngoài, tòa nhà chính phủ Tokyo, phòng họp phương Tây) thì ghi LƯU Ý KHÔNG CHẶN trong verdict. Không tự áp thành cửa TRẢ LẠI — cửa ngữ nghĩa vẫn thuộc Production cho đến khi CEO quyết chuyển sang QA (quyết định 28/10/2026 giữ nguyên: QA không có cửa ngữ nghĩa image-vs-script).
- Thẻ mục số thứ tự: khi video dùng section-header đánh số #1/#2/#3 mở từng luận điểm, chấm nhất quán trong cửa thẩm mỹ — cùng kiểu thẻ, số thứ tự đúng thứ tự, mỗi thẻ mở một luận điểm riêng; thẻ mục không cần SFX lớn riêng, SFX gợi ý của template (whoosh_fast 0.6) là đủ, không trừ điểm vì "thẻ không có tiếng boom" (đo thật video tham chiếu không có spike âm lượng tại các thẻ mục). Điểm này không gỡ luật SFX ở beat hook/móc lại/kết luận — các beat đó vẫn cần SFX của chúng; nó chỉ có nghĩa các thẻ mục đánh số trong thân video không cần mỗi thẻ một SFX lớn riêng.
- Áp dụng từ video tiếp theo, không hồi tố: các video đã duyệt trước đó không chấm lại theo 3 điểm này.

## Luật biển/chữ trên ảnh AI — siết 03/11/2026 (áp cho video mới, không truy hồi video đã duyệt)
- Biển/bảng đọc được là chủ thể hoặc điểm nhấn của ảnh, hoặc chữ nhòe/vô nghĩa → TRẢ LẠI (tạo lại tối đa 3 lần hoặc đổi góc thành nền mờ).
- Chỉ giữ kèm ghi chú khi chữ là nền mờ thật sự không đọc được và không phải chủ thể.
- Tiền lệ giữ kèm ghi chú trước 03/11 (107 S10P2, 106 S6, 114 S2/S11) là luật cũ, không áp cho video mới.
- Gương cùng luật trong skill Sản xuất (vòng tạo lại + cửa kiểm tra thực tế 4 điểm: chữ/biển, mặt/tay, bối cảnh, đúng câu thoại).

## Luật nghỉ nhấn CHỐT 04/11/2026 (CEO, áp cho mọi video sản xuất từ nay, không còn là TEST)
- Part mang template chia đoạn (section-header, thesis-marker, section-title, section-caption): pauseAfterMs = 2000 ở chính part đó, part liền trước = 1000 (trước cũng là part chia đoạn thì giữ 2000, không cộng dồn; part chia đoạn đầu video không có part trước; các part còn lại mặc định 180; part cuối video không silence cuối). Thay luật 500ms cũ và trạng thái TEST tối 03/11.
- QA kiểm từ video tới theo chuẩn 1000 trước + 2000 sau (đọc plan part-level pauseAfterMs); video mới vẫn mang 500ms ở part chia đoạn thì TRẢ LẠI để sửa plan. Chuẩn cũ 4 lần 0,50 giây chỉ còn đúng cho các video đã duyệt trước ngày chốt (203, 197, 196, 200).
- Hệ quả cửa lặng: mix cuối có slot lặng có chủ đích ~1,0s trước mốc và 2,00s sau mốc chia đoạn — ngưỡng lặng lỗi ≥1s chỉ áp cho lặng ngoài các mốc đã lên kế hoạch (đối chiếu tts.json/plan).
- Video đã duyệt trước ngày chốt giữ nguyên nhịp cũ, không làm lại trừ khi CEO ra lệnh riêng. Skill QA đã cập nhật cùng nội dung; MEMORY.md dòng luật nghỉ nhấn CHỐT đã có từ chat chính.
