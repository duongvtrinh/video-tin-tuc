# Phân tích skill viết kịch bản — vì sao ra văn "mùi AI" và cách sửa

> **Cập nhật 12/11/2026 (lệnh CEO) — đọc trước.** Câu mở đầu kịch bản nay phải là 1 trong 5 dạng (tuyên bố sốc / câu hỏi dẫn dắt / câu hỏi đặt vấn đề / câu suy ngẫm / câu khẳng định mô tả cả nội dung) và **tuyệt đối không dẫn số liệu hay ngày tháng**; con số và cảnh cụ thể dời xuống câu thứ 2. Mọi chỗ trong báo cáo này khuyến nghị "hook phải có con số/tên riêng cụ thể", "hook là cảnh cụ thể" hoặc "không mở bằng câu hỏi" đã LỖI THỜI ở **câu đầu tiên** (vẫn đúng cho câu thứ 2). Chi tiết: `SCRIPT_DOCTRINE.md` mục 3.1. Cùng đợt có thêm luật chọn ảnh/video cho cảnh chung và s1p1 (không thuộc phạm vi báo cáo này).


Ngày: 11/11/2026 · Phạm vi: `vieneu-media-company-main`. Đã đọc: các mục kịch bản, cấu trúc mở đầu, luận điểm, độ dài, ký hiệu và bài học tham chiếu của skill sản xuất; mục "giữ người xem" của QA; prompt và test của app; 6 file `prompts/`. Không đọc phần dựng hình, SFX, template, và chỉ lướt phần còn lại của skill sản xuất (185 KB).

## 1. Kết luận ngắn

1. **Skill viết đúng hướng nhưng chỉ có tác dụng ở một trong ba đường sinh kịch bản.** Skill `media-video-production` (mục "Viết kịch bản như người viết", luật CEO 29/10) mô tả khá đúng bệnh và có luật giọng văn. Nhưng nút **Tạo kịch bản của app** và 3 prompt **Video Studio** không mang luật giọng văn đó theo.
2. **Lỗi gốc mà skill tự chẩn đoán ngày 29/10 đang lặp lại trong code.** Skill viết: *"skill cũ chỉ quy định cấu trúc… mà không quy định giọng văn, nên người viết AI lấp cấu trúc bằng các mẫu câu nối sẵn"*. `script-prompt.ts` hiện đúng là như vậy: có cấu trúc 3 nhịp, không có một dòng nào về giọng người kể, nhịp câu hay văn nói.
3. **Ba nguyên nhân khiến vẫn ra văn AI dù có luật cấm:** cấm bằng danh sách cụm cố định (mô hình né bằng đồng nghĩa); không buộc người viết **chọn/cắt** dữ kiện (nên kể đủ mọi thứ với trọng lượng bằng nhau); không ai kiểm tra bằng máy trước khi chạy TTS (bước "đọc to" mô hình không làm được).
4. **Giữ chân người xem đang dựa vào 3 mốc (hook, ~50%, kết), khoảng giữa trống.** Chưa có cơ chế "vòng mở" ở cấp lời đọc.
5. **Các tài liệu mâu thuẫn nhau về cách kết video**, dễ khiến Production viết đúng luật rồi bị QA trả lại.

Đã làm: học thuyết viết kịch bản mới (một nguồn duy nhất), prompt app viết lại, 3 prompt Video Studio viết lại, script kiểm tra `script_lint.py`, vá skill. Chưa đo được chất lượng văn trên mô hình thật, xem mục 6.

## 2. Skill kịch bản nằm ở đâu, và đi qua đường nào

| Đường sinh kịch bản | Ai/cái gì viết | Văn bản chỉ dẫn thực tế | Có luật giọng văn không |
|---|---|---|---|
| A. Production (Muse) viết trong pipeline chính | Agent Production (Muse) | `company-os/skills/media-video-production/SKILL.md`, mục "Viết kịch bản như người viết", "Cấu trúc mở đầu", "Cấu trúc luận điểm" | **Có** (7 lớp cấm + 6 quy tắc giọng + kiểm tra cuối) |
| B. Nút "Tạo kịch bản" trong app Tạo Video | 1 lời gọi `ctx.inference.complete` | `app-tao-video/server/src/script-prompt.ts` | **Không** (chỉ 4 mẫu cấm, không có quy tắc giọng) |
| C. Nút Tạo dàn ý / Tạo kịch bản / Tối ưu trong Video Studio | 1 lời gọi mô hình | `vieneu-asset-factory/prompts/video_script_{outline,generate,optimize}.txt` | **Không**, và còn kéo ngược |

Ngoài ra QA (`media-video-tech-qa`, `qa-checklist.md`) chấm "giữ người xem" sau khi đã dựng xong video.

## 3. Điểm mạnh nên giữ (không đổi)

- Chẩn đoán đúng nguyên nhân gốc giọng máy (29/10) và cấm các mẫu câu cụ thể có ví dụ.
- Khóa dữ kiện: chỉ dùng sự kiện đã kiểm chứng, tìm đa nguồn trước khi viết, "nhất" phải có bảng xếp hạng.
- Kết bằng diễn biến cụ thể, cấm đạo lý; tối đa 1 câu hỏi thật.
- Nêu nguồn một lần rồi xen kẽ thay vì "Theo…" đầu mọi câu.
- Giữ ký hiệu đơn vị, dấu `:` trước tên riêng, độ dài chỉ là gợi ý (đo thật 4,16 tiếng/giây).
- Test hóa prompt (`script-prompt.test.ts`): mỗi luật có một assert. Tôi giữ cách làm này.

## 4. Phát hiện, theo mức ảnh hưởng

### P1. Prompt của app bỏ rơi luật giọng văn (ảnh hưởng cao nhất)
`script-prompt.ts` (bản cũ) mang sang từ skill: 3 nhịp, tiêu đề đánh số, một câu cấm gộp 4 mẫu, ký hiệu số, gợi ý độ dài. **Không mang sang:** "một giọng kể xuyên suốt", "câu ngắn dài xen kẽ", "mỗi câu đưa thông tin mới", "chi tiết cụ thể thay tính từ", "để sự thật tự gây cảm xúc", "nêu nguồn không máy móc". Skill có 7 lớp cấm, mỗi lớp kèm ví dụ cụ thể; prompt chỉ có 4 mẫu, không ví dụ, và gộp "cầu nối trailer" vào "mở đầu chung chung". Không có "cân bằng kiểu bài luận" ("Một mặt… mặt khác…"); kết luận đạo lý chỉ bị cấm ở dòng Kết, không có ví dụ như "Tóm lại", "Qua đó có thể thấy". Vai trò của người viết chỉ là "biên kịch video tin tức… cho kênh **phân tích** sự kiện", tức là giọng bài phân tích.

### P2. Ba prompt Video Studio kéo văn về phía AI
Trích nguyên văn bản cũ:
- `video_script_generate.txt`: *"Lời thoại tự nhiên, **giàu cảm xúc**… câu từ **chuẩn xác** cho giọng đọc AI."* Giàu cảm xúc không kèm bằng chứng là cơ chế sinh ra tính từ cảm xúc rỗng. Không có danh sách cấm, không có yêu cầu cụ thể.
- `video_script_outline.txt`: khung "Mở đầu cuốn hút / Triển khai nội dung cốt lõi / Điểm nhấn / **Kêu gọi hành động**". Khung chung này cho ra dàn ý giống hệt nhau với mọi chủ đề, và "kêu gọi hành động" trái luật kết 31/10.
- `video_script_optimize.txt`: *"Sửa câu từ cho trôi chảy, tự nhiên, chuẩn xác… Loại bỏ lỗi ngữ pháp hoặc diễn đạt lủng củng."* Một lượt "đánh bóng" như vậy làm câu đều và mượt hơn, tức là **thêm** mùi AI; prompt không có mẫu cấm nào để lượt đánh bóng không đưa "Tuy nhiên", "Bên cạnh đó" quay lại. Luật bảo toàn nội dung của nó thì tốt và tôi giữ.

### P3. Cấm bằng danh sách cụm cố định
Danh sách cấm dài khoảng 25 cụm. Mô hình né bằng cách đổi từ ("Điều đáng nói là" → "Điểm đáng chú ý là"). Văn bản cũ cũng không đưa **mẫu đúng** để thay. Cách sửa: cấm theo *chức năng* (11 lớp, mục 5 của học thuyết), nói rõ "đừng thay bằng từ đồng nghĩa, viết lại từ chi tiết cụ thể", kèm bảng Trước/Sau.

### P4. Không có bước chọn/cắt, không có người kể
Prompt chỉ nói "chỉ được dùng đúng các sự kiện này". Điều đó chặn bịa nhưng không dạy chọn, nên mô hình rải đều mọi dữ kiện với trọng lượng bằng nhau. Dấu hiệu "văn AI" mạnh nhất không nằm ở từ mà ở chỗ **không có ai quyết định điều gì quan trọng hơn**. Cách sửa: 5 quyết định trước khi viết (câu chuyện một câu, chi tiết hook, vì sao người xem bận tâm, giữ/bỏ, chỗ chưa biết), và "voice card" cho người kể.

### P5. Khung cố định bị áp máy móc nên lộ khung
Khung hook → preview → luận điểm → móc 50% → kết là luật CEO, tôi giữ. Nhưng thực thi theo chữ thì ra: preview là mục lục trung tính, tiêu đề luận điểm là nhãn ("TỔNG QUAN", "TÁC ĐỘNG") đọc lên nghe như giáo trình, móc 50% là câu loan báo "bước ngoặt". Cách sửa: giữ khung, thêm cách làm cho từng phần (học thuyết mục 3): preview là lời hứa có mẩu tò mò, tiêu đề là mệnh đề cụ thể có số hoặc động từ, móc 50% là thông tin mới nói thẳng.

### P6. Giữ chân chỉ có 3 mốc
Hook, ~50%, kết. QA có luật "mỗi 3-5 giây có thay đổi" nhưng đó là luật về **hình**. Ở cấp lời đọc không có gì buộc khoảng giữa phải có điều chưa được trả lời. Cách sửa: **vòng mở** — cứ 20-25 giây hoặc trả một vòng đã treo, hoặc treo vòng mới bằng câu khẳng định có thông tin; cấm treo thứ dữ kiện không trả (đó là lừa người xem và QA sẽ trả lại vì hook không được trả lời ở cuối).

### P7. Tài liệu mâu thuẫn nhau
| Chỗ | Mâu thuẫn |
|---|---|
| Skill, mục "Viết kịch bản" vs QA, "Giữ người xem" | Skill: cấm kết luận đạo lý, cấm câu hỏi mở. QA: *"kết có kết luận rõ ràng và một câu chốt đáng nhớ"*. Production viết đúng luật vẫn có thể bị trả lại. |
| Skill, mục "Độ dài", danh sách mở rộng | Gợi ý thêm **"câu hỏi cho khán giả"** vào lời đọc. Trái luật kết. |
| Skill, "Bài học cụ thể 30/10" | Cấu trúc tham chiếu "kết bằng câu hỏi" và "hook bản đồ + câu hỏi lớn". Trái luật kết và luật hook 31/10. |
| `video_script_outline.txt` | "Kêu gọi hành động" ở phần kết. |
Cách xử lý: học thuyết mục 9 nêu cách hiểu thống nhất (câu chốt = chi tiết cụ thể cuối cùng; câu hỏi tương tác đặt vào caption, ngoài lời đọc). Đã vá trong skill sản xuất hai chỗ của dòng 2 và 3 (mục độ dài, bài học 30/10). **Chỗ skill vs QA chưa sửa** vì thuộc skill khác (mục 7).

### P8. Kiểm tra cuối không thực thi được
Bước "đọc to toàn bộ kịch bản" mô hình không làm được. Các bước còn lại ("tìm mẫu câu cấm", "đếm câu hỏi") là việc cơ học mà người/mô hình hay sót. Lỗi bị phát hiện ở QA tức là sau khi đã chạy TTS, tạo ảnh và render. Cách sửa: `bin/script_lint.py` chạy trước TTS, thoát mã 1 khi còn LỖI.

### P9. Độ dài mặc định đang mời độn chữ
`ScriptTab.tsx:17` và `actions.ts:175` đặt mặc định 240 giây (≈ 1.000 tiếng), trong khi khung đề xuất của skill là 2-3 phút (≈ 500-750 tiếng). Dữ kiện tối đa 20.000 ký tự nhưng thường mỏng; mục tiêu dài cộng dữ kiện mỏng là nguồn lặp ý và độn chữ chính, mà độn chữ là dấu hiệu rõ nhất của văn máy. Độ dài chỉ là gợi ý theo luật 03/11 nên tôi **không đổi code**, chỉ thêm câu "Dữ kiện mỏng thì viết ngắn" vào prompt. Khuyến nghị đổi mặc định về 150-180 giây.

## 5. Đã thay đổi gì

| File | Thay đổi |
|---|---|
| `vieneu-asset-factory/skills/SCRIPT_DOCTRINE.md` | **Mới.** Nguồn duy nhất về cách viết: voice card, 5 quyết định trước khi viết, khung + cách làm cho khung không lộ, vòng mở, nghề câu cho tai nghe, 11 lớp cấm, bảng Trước/Sau, quy trình, 3 bài rà tai, bảng thống nhất mâu thuẫn, 2 phụ lục. Cùng vai trò với `EDITORIAL_DOCTRINE.md`. |
| `app-tao-video/server/src/script-prompt.ts` | Viết lại. Giữ nguyên mọi luật cũ và mọi chuỗi đã có test. Thêm người kể, bước chọn/cắt, hook cụ thể, vòng mở, luật viết cho tai, cấm theo chức năng (9 nhóm), "ví dụ chỉ minh họa hình thức, không chép nội dung", tự kiểm. |
| `app-tao-video/server/src/script-prompt.test.ts` | Cập nhật test cho các luật mới của prompt. |
| `vieneu-asset-factory/prompts/video_script_generate.txt` | Viết lại theo học thuyết (bỏ "giàu cảm xúc"). |
| `…/video_script_outline.txt` | Dàn ý bám khung có "câu chuyện một câu"; bỏ "kêu gọi hành động". |
| `…/video_script_optimize.txt` | Vẫn bảo toàn nội dung; thêm đổi văn viết sang văn nói, sửa nhịp, xử lý mẫu mùi AI (chỉ xóa câu rỗng không mang thông tin). |
| `vieneu-asset-factory/bin/script_lint.py` | **Mới.** Chỉ dùng thư viện chuẩn. Bắt mẫu cấm, nhịp câu, từ văn viết, câu hỏi, câu mở đầu, số/ngày không có trong dữ kiện (`--facts`); không đụng phần chuẩn hoá đọc của VieNeu-TTS. Ước tính thời lượng chỉ để tham khảo. |
| `company-os/skills/media-video-production/SKILL.md` | Vá 5 chỗ: con trỏ tới học thuyết; thêm lớp cấm (8) (9) và nguyên tắc cấm theo chức năng; thêm bước 3b chạy lint; sửa 2 chỗ mâu thuẫn ("câu hỏi cho khán giả", "kết bằng câu hỏi"). Không xóa luật CEO nào. |
| `PIPELINE.md` | Ghi bước lint. |

Chạy lint trên một kịch bản: `python3 bin/script_lint.py <kich_ban.txt> --facts <du_kien.txt>`; test prompt app: `cd app-tao-video && bun test server/src/script-prompt.test.ts`.

## 6. Giới hạn, nói thẳng

- **Chưa chạy prompt mới qua mô hình thật của app**, nên chưa biết văn thật ra sao. Tôi không gọi được `ctx.inference` của app. Bản `script_human.txt` do tôi viết tay theo học thuyết; bản `script_ai.txt` là văn mô phỏng do tôi viết để thử công cụ, **không phải đầu ra thật của prompt cũ**.
- **Ngưỡng nhịp câu** (độ lệch/trung bình ≥ 0.45, câu ngắn ≥ 12%) hiệu chỉnh từ đúng 2 fixture, chỉ là heuristic. Cần chạy lint lên vài kịch bản thật đã QA duyệt để chỉnh lại.
- **Lint không đo "hay".** Một kịch bản qua lint vẫn có thể nhạt; một kịch bản bị cảnh báo vẫn có thể ổn. Lint chặn lỗi cơ học và nhắc, còn rà tai và đối chiếu nguồn vẫn là việc của người viết.
- **Prompt dài hơn khoảng 3 lần.** Có rủi ro mô hình chép ví dụ trong prompt (ví dụ cầu X); tôi đã thêm dòng cấm chép, nhưng cần quan sát vài lần chạy đầu.
- Bộ quy tắc từ vựng viết cho tiếng Việt; với `{language}` khác, các prompt Video Studio chỉ giữ phần tinh thần.
- Đo "giữ chân" thật phải bằng dữ liệu nền tảng, không bằng lint.

## 7. Việc nên làm tiếp (theo thứ tự)

1. **Chạy thử A/B trên 3-5 chủ đề thật:** cùng dữ kiện, một bản prompt cũ, một bản mới; chạy lint cả hai; đưa cả hai vào QA mù. Sau khi đăng, so tỷ lệ còn xem ở giây 3, giây 15 và thời gian xem trung bình. Đây là cách duy nhất biết "giữ chân" có tốt hơn không.
2. **Sửa một câu trong skill QA** (`media-video-tech-qa/SKILL.md` và `qa-checklist.md`): thay *"Kết video phải có kết luận rõ ràng và một câu chốt đáng nhớ, không kết lửng, không lặp lại mở đầu"* bằng *"Kết video phải soi lại vấn đề mở đầu bằng một diễn biến hoặc kết quả cụ thể và có một câu chốt cụ thể, ngắn; không kết lửng, không rút bài học, không lặp nguyên văn mở đầu."* Hiện còn mâu thuẫn với luật viết.
3. **Đổi mặc định độ dài** trong `ScriptTab.tsx` từ 240 xuống 150-180 giây.
4. **Tùy chọn:** trong `generateScriptAI`, sau khi sinh nháp thì chạy lint (cổng TS tương đương) và, nếu còn LỖI, gọi thêm đúng một lượt "viết lại các câu này" kèm danh sách lỗi. Chưa làm vì cần sửa `actions.ts` và chưa có cách test lời gọi inference ở đây.
5. **Voice card theo kênh:** nếu có nhiều kênh, khai báo giọng (xưng hô, mức hoài nghi, có dùng "mình" hay không) trong brief thay vì dùng mặc định.
