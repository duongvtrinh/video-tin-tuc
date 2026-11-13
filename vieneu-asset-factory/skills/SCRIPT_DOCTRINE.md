# HỌC THUYẾT VIẾT KỊCH BẢN (Script Doctrine) — v1.0

> Tài liệu gốc duy nhất về CÁCH VIẾT lời đọc cho video của VieNeu Studio.
> Cùng vai trò với `EDITORIAL_DOCTRINE.md` (cách dựng): skill, prompt và QA chỉ TRÍCH DẪN, không chép lại.
> Sửa ở đây thì prompt trong app (`script-prompt.ts`), 3 file `prompts/video_script_*.txt` và mục
> "Viết kịch bản" của skill `media-video-production` phải sửa theo.
> Kiểm tra cơ học đi kèm: `bin/script_lint.py` (chạy TRƯỚC TTS).

**Giữ nguyên mọi luật CEO đã chốt:** giọng người viết 29/10, luận điểm 30/10, ký hiệu đơn vị 30/10,
3 nhịp mở đầu 31/10, tìm đa nguồn + gợi ý độ dài 03/11, nghỉ nhấn 04/11, và **luật câu mở đầu 12/11** (mục 3.1, thay mọi chỗ cũ đòi câu đầu có con số/tên riêng). Tài liệu này không đổi luật nào,
chỉ nói rõ LÀM THẾ NÀO để tuân thủ mà vẫn nghe như người, và vá các chỗ các luật đó mâu thuẫn nhau (mục 9).

---

## 0. Một đoạn chẩn đoán

Kịch bản "mùi AI" không phải vì sai chính tả hay thiếu ý. Nó có mùi vì **không ai đang nói**: mọi câu đều
đúng, đều vừa vặn, đều dài bằng nhau, đều kết bằng một nhận định an toàn. Người kể thật thì chọn (bỏ bớt dữ
kiện), có thái độ (tò mò, nghi ngờ số liệu), nói thẳng chỗ chưa biết, và để thông tin nặng nhất rơi ở cuối câu.
Giữ chân người xem cũng đến từ đúng những thứ đó: **cụ thể, có nhịp, có điều chưa được trả lời**.

Cho nên mọi quy tắc dưới đây phục vụ ba việc: (1) cho người kể một giọng, (2) buộc người kể chọn, (3) viết cho
tai nghe chứ không viết cho mắt đọc.

---

## 1. Người kể (voice card)

Mỗi kịch bản có MỘT người kể, giữ nguyên từ câu đầu tới câu cuối.

**Mặc định của kênh:**
- Là ai: người làm nghề, đã đọc hết hồ sơ, kể lại cho một người bạn thông minh nhưng chưa biết chuyện. Hai
  phút, qua điện thoại, không có slide.
- Thái độ: điềm tĩnh, tò mò, hơi nghi con số. Không hô hào, không cảm thán, không dạy đời.
- Được phép (vì người thật hay làm vậy):
  - nhận xét ngắn có căn cứ ngay sau một con số: "Nghe thì nhỏ.", "Con số này chưa đo ở đâu."
  - tự sửa cho chính xác: "Nói đúng hơn là…"
  - **nói thẳng chỗ chưa biết**: "Hồ sơ không nói khoản này ai chịu." (chỉ khi dữ kiện thật sự không có)
- Xưng hô: không xưng "tôi". "Mình" tối đa 3 lần cả bài, dùng ở chỗ dẫn đường tự nhiên — nhưng KHÔNG dùng để liệt kê số luận điểm (cấm "Mình đi qua ba chuyện/luận điểm", xem §3.2).
  "Bạn" tối đa 2 lần. Cấm "các bạn", "quý vị", "hôm nay chúng ta", "bạn có biết".
- Tiểu từ khẩu ngữ (nhé, nhỉ, đấy, nha): cấm, trừ khi giọng riêng của kênh khai báo khác.

Kênh có thể khai báo giọng riêng trong brief; không khai báo thì dùng mặc định trên.

---

## 2. Trước khi viết: năm quyết định (không in ra)

1. **Câu chuyện một câu.** [Ai/cái gì] làm hoặc gặp [gì], vướng [gì], kết quả là [gì / chưa biết].
   Không viết nổi một câu như vậy thì chưa đủ hiểu chủ đề; quay lại dữ kiện.
2. **Chi tiết mạnh nhất** của dữ kiện: cái nhìn thấy hoặc đếm được, có xung đột hoặc quy mô. Nó làm câu thứ 2 của bài (ngay sau câu mở đầu — câu mở đầu không được dẫn số liệu, xem 3.1).
3. **Vì sao người xem bận tâm.** Đụng tới tiền, thời gian, an toàn hay sự công bằng của họ. Phải nằm trong dữ kiện.
4. **Cắt.** Lập hai danh sách: giữ / bỏ. Dữ kiện đúng nhưng không đẩy chuyện đi thì BỎ. Bản tin kể đủ;
   người kể chọn. Mỗi luận điểm giữ tối đa: 1 con số chính + 1 phép đối chiếu + 1 chi tiết đời thường.
5. **Chỗ chưa biết / nguồn lệch nhau.** Ghi ra. Nói thẳng trong kịch bản; đây vừa là sự thật vừa là thứ làm
   giọng kể có người.

Luật kiểm chứng không đổi: chỉ dùng sự kiện đã kiểm chứng; không bịa số, tên, ngày, phát biểu. Được phép
**tính toán suy ra từ dữ kiện** (14 − 10 = chậm 4 tháng; 2/4 = một nửa) và so sánh trước/sau; phép tính phải
đúng và con số gốc phải có trong dữ kiện.

---

## 3. Khung (giữ luật 31/10) và cách làm cho khung không lộ khung

Khung: **Đặt vấn đề → Giới thiệu sơ bộ → Đi sâu → Móc lại quanh 50% → Kết soi lại vấn đề.**

### 3.1 Câu mở đầu (luật CEO 12/11/2026) và hook
**Câu đầu tiên của bài luôn là MỘT trong 13 dạng sau**, để người xem muốn nghe tiếp cho tới cái kết. Dạng 1-5 là danh sách gốc của CEO; dạng 6-13 là biến thể thêm để chủ đề nào cũng có cách mở hợp (ví dụ lấy chuyện giả định "cầu X / sông Y"):

| # | Dạng | Ví dụ câu đầu | Hợp với |
|---|---|---|---|
| 1 | Tuyên bố gây sốc | "Cây cầu mới qua sông Y đã thông xe, và chuyện nó làm bớt kẹt xe chỉ mới là lời hứa." | Điều trái kỳ vọng đã xảy ra |
| 2 | Câu hỏi dẫn dắt câu chuyện | "Ai đã hứa cây cầu này làm bớt kẹt xe, và hứa dựa trên cái gì?" | Cả bài đi trả lời một câu hỏi |
| 3 | Câu hỏi đặt vấn đề | "Cầu xong rồi, vậy bến phà từng chở cả vùng giờ đi đâu?" | Có chỗ vướng chưa ai giải |
| 4 | Câu nói suy ngẫm (về CHÍNH chuyện này) | "Cầu qua sông Y xong rồi, và cái người ta mất mới bắt đầu hiện ra." | Có cái giá/ý nghĩa đáng ngẫm |
| 5 | Câu khẳng định mô tả cả nội dung | "Cầu qua sông Y đã xong, phà đã ngừng chạy, còn lời hứa bớt kẹt xe thì chưa ai đo." | Chủ đề mỏng, chưa rõ đặc điểm nổi bật |
| 6 | Nghịch lý bằng lời | "Cây cầu xây ra để chống kẹt xe, giờ lại thành chỗ kẹt nhất vùng." | Dự án, chính sách, kinh tế |
| 7 | Hình ảnh lạ (nhìn thấy được, không số) | "Bến phà quen thuộc sáng nay im ắng đến lạ." | Thiên tai, đời sống, sự việc vừa xảy ra |
| 8 | Lời nhân chứng (trích nguyên văn, có trong nguồn) | "Ông nói: tôi chỉ muốn biết tiền của mình đã đi đâu." | Vụ án, tranh chấp, người bị hại |
| 9 | Lời hứa bị phá (kết quả trước, nguyên nhân sau) | "Họ từng cam đoan chuyện này không bao giờ xảy ra, và nó vừa xảy ra." | Doanh nghiệp, quy định, an toàn |
| 10 | Điều ai cũng tưởng, rồi lật | "Ai cũng nghĩ lỗi nằm ở nhà thầu, nhưng hồ sơ chỉ ra một chỗ khác." | Vụ việc gây tranh cãi, bị hiểu sai |
| 11 | Người xem trong tình huống (giả định riêng của chủ đề) | "Nếu sáng mai bạn chuyển khoản mà tiền không về, ai chịu trách nhiệm?" | Tài chính, luật, tiêu dùng, công nghệ |
| 12 | Người trả giá ít ai nhắc | "Có một nhóm người không ai nhắc tới trong vụ này, và họ trả giá nhiều nhất." | Tác động xã hội, giải tỏa, sa thải |
| 13 | Đính chính tin đang lan | "Tin đang lan khắp mạng về vụ này sai một chỗ, và chỗ sai đó quan trọng hơn người ta nghĩ." | Tin giả, tin viral |

**Câu mở đầu TUYỆT ĐỐI không dẫn số liệu hay ngày tháng**, ở cả 13 dạng: không chữ số, không %, không "ngày 3/11", không số viết bằng chữ đi với đơn vị ("hai mươi tỷ", "ba nghìn người", "ba ngày"); lời trích ở dạng 8 cũng vậy. Mốc thời gian tương đối ("sáng nay") thì được. Lý do nghe được: câu đầu mà đọc một con số thì tai chưa có gì để níu — số chỉ có nghĩa khi người ta đã biết nó thuộc về chuyện gì. Con số, ngày tháng, quy mô dời xuống **câu thứ 2**, và đó mới là chỗ dùng "chi tiết mạnh nhất" (mục 2):
*"Cầu qua sông Y đã xong, phà đã ngừng chạy, còn lời hứa bớt kẹt xe thì chưa ai đo. **Từ 0 giờ ngày 3/11, phà qua sông Y ngừng chạy. Mỗi ngày nó chở khoảng 4.000 lượt xe máy.**"*

**Chọn dạng theo dữ kiện:** có lời nhân chứng mạnh → 8; có hai điều mâu thuẫn trong hồ sơ → 6 hoặc 10; có một nhóm người chịu thiệt → 12; chủ đề đụng túi tiền/quyền lợi người xem → 11; tin đang lan sai → 13; có điều đã xảy ra gây sốc → 1 hoặc 9; có điều chưa ai trả lời → 2 hoặc 3; có cảnh nhìn thấy được → 7; có cái giá đáng ngẫm → 4; chưa rõ đặc điểm nào → 5. **Xoay dạng giữa các video liên tiếp của một kênh:** mở bằng cùng một khuôn nhiều video liền là dấu hiệu "mùi AI" mới.

Ràng buộc đi kèm:
- Của RIÊNG câu chuyện này (qua bài kiểm tra "thay chủ đề", mục 8), nêu đúng chủ thể/sự việc, tối đa ~18 tiếng, đọc một hơi.
- **Lời hứa phải được trả trong video.** Dạng 12 mà video không chỉ ra nhóm người nào, dạng 13 mà không chỉ ra chỗ sai nào, dạng 10 mà không chỉ ra chỗ khác nào là giật tít lừa người xem (xem 3.3: chỉ treo thứ dữ kiện sẽ trả).
- Dạng 8: chỉ dùng lời có thật trong nguồn, không bịa trích dẫn. Dạng 7: chỉ mốc thời gian tương đối.
- Dạng 2, 3, 11 (và dạng 8 nếu lời trích là câu hỏi) là câu hỏi: đó là **câu hỏi duy nhất của cả bài** (Q1), phải được trả lời sớm, và bài vẫn không được kết bằng câu hỏi (Q2). Công thức "Câu hỏi đặt ra là…", "Vậy điều gì đã xảy ra?", "Bạn có biết…" vẫn cấm ở mọi vị trí; dạng 11 phải là tình huống giả định riêng của chủ đề, không phải "Bạn có biết".
- Dạng 6 và 10: đừng viết theo khuôn "Không phải… mà là…" (luật cấm đối lập sáo); nói thẳng như ví dụ.
- Vẫn cấm mở bằng: bối cảnh chung, định nghĩa, chào hỏi, giới thiệu kênh, "Trong thời đại…".
- `script_lint.py`: K3 (LỖI) nếu câu đầu có chữ số/%/ngày tháng/số chữ + đơn vị lớn; K4 (CẢNH BÁO) nếu số chữ + đơn vị thời gian/đếm. Lint không phân loại dạng; chọn dạng là việc của người viết.

### 3.2 Preview là lời hứa, không phải mục lục
1-2 câu, nói như lời hứa/dẫn vào vấn đề tự nhiên: *"Cầu 120 tỷ đã xong, phà đã ngừng chạy — nhưng tiền đó mua được gì, vì sao chậm 4 tháng, và con số giảm 30% ùn tắc là lời hứa của ai."* Mỗi ý là một mẩu tò mò có thật; không số liệu râu ria. CẤM liệt kê/đếm số luận điểm (CEO 14/11/2026): cấm "Mình đi qua ba chuyện/luận điểm", "Mình đi qua hai luận điểm", "Có ba điểm", "Chúng ta sẽ xem ba vấn đề", và mọi câu thông báo số luận điểm sẽ trình bày.
Không viết "Bài viết/video này sẽ…", "Chúng ta sẽ cùng…".

### 3.3 Vòng mở (open loop)
Người xem ở lại để biết điều chưa được trả lời. Cứ khoảng 20-25 giây có một mảnh nhỏ: hoặc **trả** một vòng đã
treo, hoặc **treo** một vòng mới. Cách treo hợp lệ là một **câu khẳng định có thông tin**, không phải câu hỏi,
không phải lời loan báo:
- Được: *"Còn một khoản nữa, và khoản này bằng cả hai khoản trên cộng lại."* (khi dữ kiện đúng thế)
- Cấm: *"Nhưng câu chuyện chưa dừng lại ở đó."*, *"Điều bất ngờ sắp tới…"* (trailer rỗng).
Quy tắc vàng: **chỉ treo thứ dữ kiện sẽ trả.** Treo mà không trả là lừa người xem, và QA sẽ trả lại.

### 3.4 Tiêu đề luận điểm (giữ luật 30/10)
Vẫn là dòng riêng, `1. IN HOA.` hoặc IN HOA kết thúc bằng dấu chấm. Nhưng nội dung phải là **mệnh đề cụ thể**
có số hoặc động từ, ≤ 8 tiếng; không phải nhãn chủ đề.
- Được: `1. 120 TỶ ĐỒNG CHO 840 MÉT.` · `2. CHẬM 4 THÁNG, MỘT NỬA LÀ DO ĐƯỜNG ỐNG.`
- Cấm: `1. TỔNG QUAN DỰ ÁN.` · `2. TÁC ĐỘNG.` · `3. KẾT LUẬN.`
Tiêu đề được TTS đọc lên, nên nó phải nghe như một câu người ta nói.

### 3.5 Móc lại ~50%
Là **thông tin mới làm đổi cách hiểu** (đảo chiều, con số trái kỳ vọng, chi tiết mâu thuẫn). Nói thẳng như tin,
không loan báo "bước ngoặt". *"Chậm 4 tháng. Nhưng 2 tháng trong đó, công trình đứng yên vì một đường ống nước
nằm đúng chỗ đóng trụ."*

### 3.6 Kết (giữ luật: soi lại vấn đề, không đạo lý, không câu hỏi mở)
- Quay lại vấn đề mà câu mở đầu đã đặt ra, và hình ảnh/con số ở câu thứ 2, bằng một **diễn biến hoặc bước tiếp theo cụ thể**.
- **Câu chốt** (QA yêu cầu "câu chốt đáng nhớ"): chi tiết cụ thể cuối cùng, ≤ 12 tiếng, đặt sau nhịp nghỉ.
  Không phải bài học, không phải khẩu hiệu. *"Phà đã ngừng chạy. Còn 30% kia, nhìn vào giờ cao điểm đầu tiên là biết."*
- Muốn kéo bình luận: đặt câu hỏi vào **caption bài đăng**, không đặt vào lời đọc.

---

## 4. Nghề câu: viết cho tai

Đơn vị đo là **tiếng** (âm tiết, đếm theo khoảng trắng, cùng cách đếm với hệ số 4,16 tiếng/giây).

1. **Một câu một ý.** Điển hình 8-18 tiếng. Trần 28. Quá 40 là lỗi.
2. **Nhịp thở.** Xen câu rất ngắn (2-7 tiếng) với câu 14-24. Ít nhất ~12% câu ≤ 7 tiếng. Không để 3 câu liền
   dài bằng nhau. Câu ngắn đặt ở chỗ nhấn: *"Làm hết 14."* *"Là thời gian."*
3. **Thông tin nặng nhất đặt cuối câu**, nơi giọng đọc rơi xuống. Con số chính cũng ở cuối.
4. **Tối đa 2-3 con số mỗi câu.** Nhiều hơn thì tách câu; tai không giữ nổi.
5. **Mở câu bằng chủ thể + hành động**, không bằng trạng ngữ dài. Đổi chủ ngữ giữa các câu liền nhau;
   không mở 3 câu liền bằng cùng một cụm ("Theo…", "Cầu…").
6. **Động từ thay danh hoá, chủ động thay bị động.** "Chủ đầu tư làm cầu để gỡ ùn tắc", không phải
   "Việc xây dựng cầu được chủ đầu tư tiến hành nhằm giải quyết tình trạng ùn tắc."
7. **Chi tiết thay tính từ** (luật 29/10 mục 4). Bảng đổi ở phụ lục A.
8. **Để sự thật tự gây cảm xúc.** Muốn nhấn thì nhấn bằng cấu trúc (câu ngắn, đặt cuối, nghỉ một nhịp), không bằng
   tính từ, trạng từ hay dấu chấm than. Người kể được phản ứng bằng một câu ngắn có căn cứ, không bằng "thật đáng tiếc".
9. **Cho con số trọng lượng bằng đối chiếu**, trong phạm vi dữ kiện: trước/sau ("chờ 25 phút → …"), kế hoạch/thực tế
   ("10 tháng → 14"), phần/tổng ("2 trong 4 tháng"). Đối chiếu với vật quen thuộc (sân bóng, bao nhiêu lần…)
   chỉ khi phép tính đúng và ghi rõ đó là phép tính.
10. **Từ nối: nói thường.** "Nhưng", "Còn", "Nên", "Mà". Cấm đầu đoạn "Tuy nhiên / Bên cạnh đó / Ngoài ra / Đồng thời / Hơn nữa".
    Bảng văn viết → văn nói ở phụ lục B.
11. **Không hoàn hảo một cách có chủ đích.** Được: câu bỏ chủ ngữ, câu cụt, bắt đầu bằng "Nhưng/Và/Còn", tự sửa giữa câu.
    Không được: sai sự thật.
12. **Trích nguồn không máy móc** (giữ luật): nêu một lần cho rõ, sau đó xen "ông nói", "cáo trạng ghi", hoặc đặt nguồn ở cuối câu.
    Khẳng định tương lai luôn ghi nguồn ngay trong câu ("theo chủ đầu tư", "dự kiến").
13. **Dấu câu cho TTS** (giữ luật 30/10): ký hiệu giữ nguyên (`10%`, `35°C`, `10 km`); `:` trước tên riêng đứng sau chức danh;
    không ngoặc đơn, không gạch dài, không chấm phẩy, không markdown, không chỉ đạo `[…]`.

---

## 5. Cấm theo LỚP chức năng

Danh sách cụm cấm cố định luôn bị mô hình lách bằng từ đồng nghĩa ("Điều đáng nói là" → "Điểm đáng chú ý là").
Vì vậy cấm theo **chức năng**: gặp biến thể không có trong danh sách mà làm cùng việc đó, vẫn cấm, và **không
thay bằng từ đồng nghĩa; viết lại câu từ một chi tiết cụ thể.** Lời trích nguyên văn của nhân vật được miễn.

| Lớp | Chức năng (cái bị cấm) | Ví dụ |
|---|---|---|
| C1 | Câu hỏi tu từ rỗng làm cầu nối, hoặc câu hỏi công thức ở bất kỳ vị trí nào (riêng CÂU MỞ ĐẦU được là câu hỏi riêng của câu chuyện — mục 3.1) | "Câu hỏi đặt ra là…", "Vậy điều gì đã xảy ra?", "Bạn có biết…", "Điều gì khiến…" giữa bài |
| C2 | Đối lập sáo | "Không chỉ… mà còn…", "Không phải… mà là…" |
| C3 | Mở đầu khái quát | "Trong thời đại…", "Khi nhắc đến…", "Từ trước đến nay…" |
| C4 | Cầu nối trailer | "Câu chuyện chưa dừng lại ở đó", "Điều đáng nói là", "Thú vị hơn nữa" |
| C5 | Tổng kết / đạo lý | "Bài học rút ra", "Qua đó có thể thấy", "Tóm lại", "Nhìn chung" |
| C6 | Cân bằng kiểu bài luận | "Một mặt… mặt khác…", "Vừa… vừa…" |
| C7 | Tính từ cảm xúc thay bằng chứng | "đáng kinh ngạc", "gây chấn động", "thật đau lòng" |
| **C8** | **"Nâng tầm" văn báo cáo** (mới) | "đóng vai trò", "mang lại", "đánh dấu bước ngoặt", "góp phần", "hành trình", "kỷ nguyên" |
| **C9** | **Chào hỏi / kêu gọi** (mới) | "Xin chào", "Hôm nay chúng ta cùng…", "Đừng quên theo dõi" |
| N3 | Câu chốt cách ngôn cuối đoạn (mới) | "Đó mới là điều quan trọng.", "Đây chính là…" |

Ngoài lớp: **bộ ba trừu tượng** ("A, B và C" toàn danh từ trừu tượng), **câu nào đoạn nào cũng kết bằng một nhận định**,
**mọi dữ kiện đều có trọng lượng bằng nhau** (không chọn) là ba dấu hiệu mạnh nhất; bước 2 và 4 ở mục 2 chặn chúng từ gốc.

---

## 6. Trước / Sau

(Dữ kiện giả định: cầu X qua sông Y. Chỉ để minh hoạ, không phải tin thật.)

| | Trước (mùi AI) | Sau |
|---|---|---|
| Câu mở đầu + câu 2 | Trong bối cảnh Hà Nội ngày càng phát triển, hạ tầng giao thông luôn đóng vai trò quan trọng. | Cầu qua sông Y đã xong, phà đã ngừng chạy, còn lời hứa bớt kẹt xe thì chưa ai đo. Từ 0 giờ ngày 3/11, phà qua sông Y ngừng chạy. Mỗi ngày nó chở khoảng 4.000 lượt xe máy. |
| Preview | Hãy cùng tìm hiểu về dự án, những khó khăn và tác động của nó. | Cầu 120 tỷ đã xong, phà đã ngừng chạy — nhưng tiền đó mua được gì, vì sao chậm 4 tháng, và con số 30% là lời hứa của ai. |
| Cầu nối | Nhưng câu chuyện chưa dừng lại ở đó. Điều đáng nói là tiến độ. | Kế hoạch là 10 tháng. Làm hết 14. |
| Tính từ → chi tiết | Việc chờ phà gây bất tiện rất lớn cho người dân. | Theo chủ đầu tư, mỗi lượt qua sông phải chờ trung bình khoảng 25 phút. |
| Văn viết → nói | Dự án được chủ đầu tư tiến hành nhằm giải quyết tình trạng ùn tắc. | Chủ đầu tư làm cầu để gỡ ùn tắc. |
| Tương lai | Cầu sẽ giúp giảm 30% ùn tắc. | Chủ đầu tư dự kiến ùn tắc giờ cao điểm giảm 30%. Họ chưa nói 30% này đo ở đoạn nào. |
| Móc 50% | Bên cạnh đó, việc dời đường ống cũng góp phần làm chậm tiến độ. | Trong 4 tháng chậm, 2 tháng công trình đứng yên. Không phải vì bê tông hay thép. Một đường ống nước nằm đúng chỗ đóng trụ. |
| Kết | Qua đó có thể thấy cầu X là biểu tượng của sự phát triển. | Phà đã ngừng chạy. Còn 30% kia, nhìn vào giờ cao điểm đầu tiên là biết. |

---

## 7. Quy trình

1. **Chọn** (mục 2): câu chuyện một câu, chi tiết hook, vì sao người xem bận tâm, giữ/bỏ, chỗ chưa biết.
2. **Dựng xương:** hook / preview / các luận điểm (mỗi cái 1 câu chủ ý + 1 con số chính) / chỗ móc 50% / diễn biến kết. Đánh dấu chỗ treo và chỗ trả mỗi vòng mở.
3. **Viết** một mạch theo giọng người kể, theo mục 3-4.
4. **Chạy `script_lint.py --facts <dữ kiện>`.** Còn LỖI thì viết lại câu đó (không thay từ đồng nghĩa) rồi chạy lại. CẢNH BÁO: đọc từng cái, sửa hoặc ghi lý do giữ.
   Lint kiểm cơ học: mẫu cấm (§5), xưng hô (§1: cấm "tôi"/"các bạn"/"quý vị", "mình" tối đa 3, "bạn" tối đa 2),
   có đoạn preview sau hook (§3.2), câu chốt cuối ≤ 12 tiếng (§3.6), số/ngày lệch dữ kiện. Lint KHÔNG kiểm:
   chất lượng lời hứa trong preview (có phải lời hứa thật hay chỉ là mục lục), nhịp treo/trả vòng mở (§3.3),
   xưng hô trong lời trích nguyên văn (được miễn). Ba thứ đó chỉ rà bằng tai (mục 8) và QA.
5. **Rà tai** (không thay được bằng lint): ba bài kiểm tra ở mục 8.
6. **Đối chiếu nguồn** (luật cũ, vẫn bắt buộc): từng ngày tháng, từng phát ngôn gắn tên người, từng "nhất". Sau đó mới chạy TTS.

---

## 8. Ba bài kiểm tra rà tai

1. **Thay chủ đề.** Đổi tên sự kiện thành sự kiện khác cùng loại; đoạn nào vẫn đọc được nguyên văn là đoạn chung chung. Viết lại bằng chi tiết chỉ thuộc về câu chuyện này.
2. **Xoá thử.** Với mỗi câu: xoá đi có mất thông tin hoặc mất nhịp không? Không mất thì xoá.
3. **Che số.** Che mọi con số; còn lại có còn dắt người nghe đi tiếp không? Nếu không, câu chuyện đang dựa hoàn toàn vào số liệu, thiếu hành động và con người.

---

## 9. Các chỗ luật đang mâu thuẫn, và cách hiểu thống nhất

| Mâu thuẫn trong tài liệu cũ | Cách hiểu thống nhất |
|---|---|
| Skill viết: cấm câu hỏi mở cho khán giả, cấm kết luận. QA: "kết có kết luận rõ ràng và một câu chốt đáng nhớ". | "Kết luận rõ" = soi lại vấn đề mở đầu bằng diễn biến cụ thể; "câu chốt" = chi tiết cụ thể cuối cùng (mục 3.6). Không phải bài học. |
| Skill, mục độ dài: mở rộng bằng "câu hỏi cho khán giả". Bài học 30/10: "kết bằng câu hỏi". | Cả hai trái luật kết hiện hành. Câu hỏi tương tác đặt ở caption, không ở lời đọc. |
| Luật hook cũ (31/10, 11/11): hook là cảnh cụ thể có con số/tên riêng, "không câu hỏi" — vs luật 12/11: câu mở đầu là 1 trong 5 dạng (kể cả câu hỏi) và tuyệt đối không số liệu/ngày tháng. | Luật 12/11 thay luật cũ ở câu ĐẦU TIÊN. Con số/cảnh cụ thể vẫn bắt buộc nhưng dời xuống câu thứ 2. Câu hỏi mở đầu là câu hỏi duy nhất của bài và vẫn không được kết bằng câu hỏi. |
| Preview "không kể chi tiết" vs luật "mỗi câu mang thông tin mới". | Preview là ngoại lệ có chủ ý; nhưng phải là lời hứa có mẩu tò mò (mục 3.2), không phải danh sách trung tính. |
| Gợi ý độ dài mặc định 240 giây (≈ 1.000 tiếng) vs khung đề xuất 2-3 phút (≈ 500-750 tiếng). | Mặc định app nên là 150-180 giây. Độ dài chỉ là gợi ý (luật 03/11), nhưng dữ kiện mỏng + mục tiêu dài là nguồn độn chữ lớn nhất, và độn chữ là mùi AI rõ nhất. |

---

## Phụ lục A — Tính từ → thứ nhìn thấy

| Thay vì… | Viết… |
|---|---|
| "tình hình rất căng thẳng" | tiếng súng, con số thương vong, giờ giấc, ai ra lệnh |
| "gây bất tiện lớn" | chờ bao nhiêu phút, mất bao nhiêu tiền, vòng thêm bao nhiêu km |
| "công trình khổng lồ" | dài bao nhiêu m, bao nhiêu người làm, bao nhiêu tháng |
| "tăng mạnh" | từ bao nhiêu lên bao nhiêu, trong bao lâu |
| "gây chấn động dư luận" | bao nhiêu lượt chia sẻ/bình luận, ai lên tiếng đầu tiên |
| "nhiều người cho rằng" | ai, bao nhiêu người, nói ở đâu |

## Phụ lục B — Văn viết → văn nói

| Văn viết | Văn nói |
|---|---|
| tiến hành / thực hiện | làm |
| nhằm / nhằm mục đích | để |
| cho biết | nói / cho hay (xen "ông nói") |
| sở hữu | có |
| diễn ra | xảy ra / có |
| hiện nay / hiện tại | giờ / bây giờ |
| đã được phê duyệt | được duyệt / Bộ duyệt |
| việc xây dựng cầu | xây cầu |
| Tuy nhiên, | Nhưng |
| Bên cạnh đó / Ngoài ra | (bỏ) hoặc "Còn" |
| Do đó / Vì vậy | Nên |
| đồng thời | (tách thành hai câu) |
