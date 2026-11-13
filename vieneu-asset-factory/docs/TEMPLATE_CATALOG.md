# TEMPLATE_CATALOG (TỰ SINH — KHÔNG SỬA TAY)

> Sinh bởi `bin/gen_catalog.py` từ `templates/*/meta.json`. Sửa meta rồi chạy lại; `gen_catalog.py --check` báo lỗi thời. Đây là NGUỒN DUY NHẤT cho 'template nào tồn tại, dùng khi nào' — skill và doctrine trỏ về đây, không tự liệt kê tên.

**45 template active** · 5 theme · chuẩn schema `specVersion 2` (xem `docs/TEMPLATE_SPEC.md`).

## 1. Theo chủ đề (theme)

Chọn theme theo thể loại video (`broll-genre-palette`), rồi chọn template trong hàng đó. 'general' = dùng được cho mọi video nên không liệt kê lại ở đây.

| Theme | Thể loại (genre) | Accent mặc định | Template (id) |
|---|---|---|---|
| `history` Lịch sử | — | gold | `date-stamp`, `map-route`, `quote-card`, `section-title`, `source-citation`, `thesis-marker`, `timeline-horizontal`, `timeline-strip`, `typewriter-reveal` |
| `war` Chiến tranh | — | red | `breaking-banner`, `map-route`, `section-title`, `stat-counter`, `tactical-banner`, `thesis-marker`, `versus-split` |
| `sports` Thể thao | — | cyan | `bar-chart`, `compare-bars`, `dual-stat`, `keyword-burst`, `podium-rank`, `poll-vote`, `scoreboard`, `stat-counter`, `versus-split` |
| `economy` Kinh tế | — | green | `bar-chart`, `checklist`, `comment-frame`, `compare-bars`, `dual-stat`, `info-note`, `market-ticker`, `section-caption`, `section-header`, `section-title`, `share-bar`, `stat-counter`, `tactical-banner`, `thesis-marker`, `timeline-horizontal`, `trend-badge` |

## 2. Theo vai trò (category) và vị trí

`placement`: `subtitle-bottom` (mặc định, trên vùng phụ đề) · `flush-bottom` (sát đáy) · `edge-bottom` (sát mép) · `full-stage` (phủ khung hình) · `none` (cutaway, không lớp chữ).

| Category | Template | placement | nền | SFX gợi ý (id vol) |
|---|---|---|---|---|
| alert | `breaking-banner` v1.6.0 | subtitle-bottom | transparent | whoosh_fast 0.6 |
| alert | `tactical-banner` v1.4.0 | subtitle-bottom | transparent | radar_glitch 0.7 |
| banner | `preview-banner` v1.2.0 | flush-bottom | transparent | whoosh_fast 0.6 |
| clip | `clip-caption` v1.6.0 | edge-bottom | transparent | — |
| cutaway | `cutaway-standard` v1.6.0 | none | opaque | whoosh_fast 0.5 |
| hook | `hook-title-card` v1.2.0 | full-stage | opaque | whoosh_fast 0.6 |
| interactive | `poll-vote` v1.6.0 | subtitle-bottom | transparent | — |
| keyword | `keyword-block` v1.3.0 | flush-bottom | transparent | — |
| keyword | `keyword-burst` v1.3.0 | subtitle-bottom | transparent | punch_impact 0.8 |
| keyword | `keyword-strip` v1.10.0 | subtitle-bottom | transparent | punch_impact 0.7 |
| keyword | `typewriter-reveal` v1.9.0 | subtitle-bottom | transparent | typing_fast 0.75 |
| list | `checklist` v1.5.0 | subtitle-bottom | transparent | whoosh_fast 0.7 |
| list | `map-route` v1.6.0 | subtitle-bottom | transparent | cinematic_riser 0.55 |
| list | `podium-rank` v1.8.0 | subtitle-bottom | transparent | cinematic_riser 0.6 |
| list | `step-flow` v1.1.0 | subtitle-bottom | transparent | whoosh_fast 0.5 |
| list | `timeline-horizontal` v1.6.0 | subtitle-bottom | transparent | whoosh_fast 0.6 |
| list | `timeline-strip` v1.5.0 | subtitle-bottom | transparent | whoosh_fast 0.6 |
| lower-third | `lower-third-pro` v1.6.0 | subtitle-bottom | transparent | whoosh_fast 0.6 |
| photo | `photo-duo` v1.4.0 | full-stage | opaque | heavy_thud_slam 0.35 |
| photo | `photo-duo-h` v1.3.0 | full-stage | opaque | boom_sub_impact 0.4 |
| photo | `photo-hero` v1.3.0 | full-stage | opaque | heavy_thud_slam 0.35 |
| photo | `photo-quote` v1.1.0 | full-stage | opaque | whoosh_fast 0.6 |
| quote | `quote-card` v1.6.0 | subtitle-bottom | transparent | — |
| quote | `source-citation` v1.6.0 | subtitle-bottom | transparent | paper_rip 0.6 |
| social | `comment-frame` v1.6.0 | subtitle-bottom | transparent | — |
| social | `social-comment` v1.6.0 | subtitle-bottom | transparent | — |
| source | `info-note` v1.5.0 | subtitle-bottom | transparent | — |
| source | `source-footer-safe` v1.5.0 | subtitle-bottom | transparent | — |
| stat | `bar-chart` v1.6.0 | subtitle-bottom | transparent | heavy_thud_slam 0.35 |
| stat | `compare-bars` v1.6.0 | subtitle-bottom | transparent | heavy_thud_slam 0.35 |
| stat | `date-stamp` v1.7.0 | subtitle-bottom | transparent | heavy_thud_slam 0.4 |
| stat | `dual-stat` v1.7.0 | subtitle-bottom | transparent | heavy_thud_slam 0.35 |
| stat | `market-ticker` v1.6.0 | subtitle-bottom | transparent | — |
| stat | `scoreboard` v1.6.0 | subtitle-bottom | transparent | whoosh_fast 0.7 |
| stat | `section-caption` v1.6.0 | subtitle-bottom | transparent | whoosh_fast 0.6 |
| stat | `section-header` v1.6.0 | subtitle-bottom | transparent | whoosh_fast 0.6 |
| stat | `share-bar` v1.1.0 | subtitle-bottom | transparent | heavy_thud_slam 0.35 |
| stat | `stat-counter` v1.10.0 | subtitle-bottom | transparent | heavy_thud_slam 0.35 |
| stat | `strike-verdict` v1.5.0 | subtitle-bottom | transparent | heavy_thud_slam 0.35 |
| stat | `trend-badge` v1.1.0 | subtitle-bottom | transparent | punch_impact 0.55 |
| story | `story-title` v1.6.0 | subtitle-bottom | transparent | — |
| text | `verdict-stamp` v1.0.0 | subtitle-bottom | transparent | heavy_thud_slam 0.35 |
| title | `section-title` v1.8.0 | full-stage | opaque | cinematic_riser 0.6 |
| title | `thesis-marker` v1.6.0 | full-stage | opaque | heavy_thud_slam 0.4 |
| transition | `versus-split` v1.5.0 | full-stage | opaque | boom_sub_impact 0.4 |

## 3. Chi tiết từng template

### `bar-chart` — Biểu đồ cột / Bar chart  (v1.6.0, overlay, stat)
- **Input** (* bắt buộc): `foot` ≤60; `label1`* ≤16; `label2`* ≤16; `label3` ≤16; `label4` ≤16; `title`* ≤40; `tone1` ∈{money|volume|decline|mild}; `tone2` ∈{money|volume|decline|mild}; `tone3` ∈{money|volume|decline|mild}; `tone4` ∈{money|volume|decline|mild}; `value1`* ≤14; `value2`* ≤14; `value3` ≤14; `value4` ≤14; `w1`* ≤3; `w2`* ≤3; `w3` ≤3; `w4` ≤3
- **Dùng khi**: So sánh mức tăng/giảm của 2-4 đối tượng (chỉ số, thị trường, doanh thu) · Cần người xem thấy chênh lệch bằng mắt, không chỉ đọc số
- **KHÔNG dùng khi**: Chỉ một con số (dùng stat-counter) · Hai số đối chiếu (dùng dual-stat) · Quá 4 cột (chia thành nhiều cảnh)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.86) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `breaking-banner` — Banner tin nóng  (v1.6.0, overlay, alert)
- **Input** (* bắt buộc): `label` ≤20; `text`* ≤90
- **Dùng khi**: Tin vừa xảy ra, cần gây chú ý ngay · Tuyên bố khẩn cấp
- **KHÔNG dùng khi**: Tin không khẩn cấp · Text quá dài
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Bỏ viền đỏ: xóa border 2px accent ở thẻ ngoài (CEO 13/11/2026); chip TIN NÓNG nền đỏ giữ nguyên.

### `checklist` — Danh sách ý chính / Checklist  (v1.5.0, overlay, list)
- **Input** (* bắt buộc): `label` ≤40; `items`* ≤5 mục×56; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Liệt kê nguyên nhân, kết quả, điều kiện · Tóm tắt ý chính sau một đoạn dài
- **KHÔNG dùng khi**: Một ý duy nhất · Ý quá dài (hơn 60 ký tự mỗi dòng)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.5.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.84) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `clip-caption` — Tiêu đề clip tranh cãi  (v1.6.0, overlay, clip)
- **Input** (* bắt buộc): `summary`* ≤200; `title`* ≤40
- **Dùng khi**: Dựng lại clip gây tranh cãi: thêm tiêu đề vàng + khối tóm tắt hồng ở cuối khung, giữ nguyên credit gốc · Cần lớp chữ cố định xuyên suốt clip thay vì phụ đề karaoke
- **KHÔNG dùng khi**: Tiêu đề dài quá 40 ký tự · Tóm tắt dài quá 200 ký tự · Che mất credit/watermark gốc của clip
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `comment-frame` — Khung bình luận tâm sự  (v1.6.0, overlay, social)
- **Input** (* bắt buộc): `avatar` ≤2; `brand`* ≤20; `comments` ≤20; `likes` ≤20; `source` ≤40; `text`* ≤300; `title`* ≤70; `user`* ≤30
- **Dùng khi**: Video kể chuyện bằng bình luận mạng xã hội, mỗi thẻ hiển thị lâu và được đọc thành tiếng · Cần khung thương hiệu trên/dưới xuyên suốt kiểu reel tâm sự
- **KHÔNG dùng khi**: Bình luận dài quá 300 ký tự · Nội dung chưa kiểm chứng hoặc nhạy cảm · Gán lời giả cho người thật cụ thể
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `compare-bars` — Thanh so sánh / Compare Bars  (v1.6.0, overlay, stat)
- **Input** (* bắt buộc): `count` ∈{2|3|4}; `foot` ≤60; `label1`* ≤16; `label2`* ≤16; `label3` ≤16; `label4` ≤16; `title`* ≤40; `tone1` ∈{gold|white|decline}; `tone2` ∈{gold|white|decline}; `tone3` ∈{gold|white|decline}; `tone4` ∈{gold|white|decline}; `value1`* ≤14; `value2`* ≤14; `value3` ≤14; `value4` ≤14; `w1`* ≤3; `w2`* ≤3; `w3` ≤3; `w4` ≤3
- **Dùng khi**: So sánh 2-4 đối tượng bằng mắt: các thanh dài theo tỉ lệ giá trị, dài ngắn thấy ngay · Cần người xem thấy chênh lệch ngay không cần đọc kỹ số
- **KHÔNG dùng khi**: Chỉ một con số (dùng stat-counter) · So sánh 3-4 đối tượng dạng cột dọc (dùng bar-chart) · Hai bên đối đầu toàn màn hình (dùng versus-split)
- **Ràng buộc**: bắt buộc thêm theo count
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.3.0 (2026-11-13): I8-A (CEO 13/11/2026): thẻ rêu đủ cho overlay (X-01); nền thẻ đổi từ rgba(28,55,42,.85) sang nền rêu chuẩn đặc #1C372A + kẻ ô #2A4D3B 80px như hook-title-card.; v1.4.0 (2026-11-13): Sửa theo ý CEO 13/11/2026: nền thẻ về mực trong rgba(8,10,16,.82) như các template overlay khác (stat-counter, dual-stat); bỏ nền rêu đặc + kẻ ô vừa thêm ở v1.3.0.; v1.5.0 (2026-11-13): Tăng độ trong suốt: nền thẻ rgba(8,10,16,.82) → rgba(8,10,16,.75) theo ý CEO 13/11/2026.; v1.6.0 (2026-11-13): Tăng độ trong suốt thêm: nền thẻ rgba(8,10,16,.75) → rgba(8,10,16,.68) theo ý CEO 13/11/2026.

### `cutaway-standard` — B-roll toàn khung  (v1.6.0, cutaway, cutaway)
- **Input** (* bắt buộc): `text` ≤80
- **Dùng khi**: Có hình ảnh minh họa cụ thể cho lời đọc · Cần đổi nhịp hình ảnh trong một đoạn dài
- **KHÔNG dùng khi**: Không có media phụ phù hợp · Chủ thể chính cần được giữ liên tục trên màn hình
- Ảnh nội dung: CÓ (không dùng nền trung tính)

### `date-stamp` — Mốc thời gian / Date stamp  (v1.7.0, overlay, stat)
- **Input** (* bắt buộc): `value`* ≤14; `text` ≤60; `label` ≤24; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Chuyển mốc thời gian trong câu chuyện · Nhấn mạnh năm của một sự kiện
- **KHÔNG dùng khi**: Không có mốc thời gian cụ thể
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.7.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.8) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `dual-stat` — Hai số đối chiếu / Dual stat  (v1.7.0, overlay, stat)
- **Input** (* bắt buộc): `labelA`* ≤24; `labelB`* ≤24; `sublabel` ≤70; `valueA`* ≤10; `valueB`* ≤10
- **Dùng khi**: Beat đối chiếu đúng hai con số (tăng vs giảm, thiệt hại vs hưởng lợi, kế hoạch vs thực tế) · Cần người xem nhớ cả hai số cùng lúc, không chỉ một số chính
- **KHÔNG dùng khi**: Beat chỉ có một con số (dùng stat-counter) · Nhiều hơn hai con số trong cùng beat · Câu không có số liệu · Text dài giải thích (dùng section-title hoặc quote-card)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Ngoại lệ X-01 (CEO 12/11/2026): thẻ overlay giữ nền navy #080A10, không đổi rêu.; v1.7.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.85) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `hook-title-card` — Thẻ tiêu đề hook / Hook Title Card  (v1.2.0, fullscreen, hook)
- **Input** (* bắt buộc): `line1`* ≤40; `line2` ≤40; `line3` ≤40; `punch`* ≤40
- **Dùng khi**: Beat hook 0-3s: cần thẻ tiêu đề toàn màn hình mang chính câu hook (so sánh bất ngờ + sự kiện cụ thể) · Video tin tức/giải thích mở bằng một khẳng định gây sốc cần nhớ ngay
- **KHÔNG dùng khi**: Beat phân tích giữa video (dùng keyword-block) · Tiêu đề 2 dòng cố định xuyên suốt video (dùng story-title) · Mỗi dòng quá 40 ký tự
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `info-note` — Thẻ chú thích nhỏ / Info note  (v1.5.0, overlay, source)
- **Input** (* bắt buộc): `info`* ≤70; `name`* ≤30
- **Dùng khi**: Giới thiệu nhanh một thực thể khi nhắc tên lần đầu (công ty, tổ chức, nhân vật) kèm một dòng thông tin phụ · Chú thích nhỏ không đáng một thẻ số liệu riêng
- **KHÔNG dùng khi**: Ghi nguồn (dùng source-footer-safe) · Thông tin dài giải thích (dùng quote-card hoặc section-title)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.5.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.72) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `keyword-block` — Khối từ khóa / Keyword Block  (v1.3.0, overlay, keyword)
- **Input** (* bắt buộc): `accent` ∈{gold|red|cyan|green|pink|purple…}; `keyword`* ≤30; `line1` ≤60; `line3` ≤60
- **Dùng khi**: Beat phân tích chi tiết: mỗi beat một con số/từ khóa then chốt kèm ngữ cảnh · Dùng cho nhiều beat liên tiếp, mỗi beat một khối
- **KHÔNG dùng khi**: Liệt kê nhiều ý trong một thẻ (mỗi khối chỉ một từ khóa) · Từ khóa dài quá 30 ký tự
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `keyword-burst` — Từ khóa lớn / Keyword burst  (v1.3.0, overlay, keyword)
- **Input** (* bắt buộc): `text`* ≤36; `sublabel` ≤50; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Chốt ý bằng một từ/cụm từ · Nhịp nhấn mạnh trong câu kể nhanh
- **KHÔNG dùng khi**: Câu dài · Nhiều hơn 4 từ
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `keyword-strip` — Dải từ khóa / Keyword strip  (v1.10.0, overlay, keyword)
- **Input** (* bắt buộc): `box1`* ≤20; `box2`* ≤20; `box3` ≤20; `head` ≤50
- **Dùng khi**: Liệt kê 2-3 từ khóa song song trong một beat (lĩnh vực, đối tượng, hệ quả) · Cần người xem nhớ một nhóm khái niệm cùng lúc
- **KHÔNG dùng khi**: Một từ khóa duy nhất (dùng keyword-burst) · Từ khóa cực lớn chốt ý (dùng keyword-burst) · Quá 3 từ khóa (chia thành nhiều cảnh)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.9.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.8) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.; v1.10.0 (2026-11-13): Bỏ viền: xóa border vàng rgba(251,191,36,.55) ở các ô từ khóa (CEO 13/11/2026).

### `lower-third-pro` — Nhãn tên nâng cao / Lower third Pro  (v1.6.0, overlay, lower-third)
- **Input** (* bắt buộc): `label` ≤30; `text`* ≤56; `sublabel` ≤70; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Giới thiệu nhân vật kèm chức danh và năm · Định danh địa điểm kèm mô tả ngắn
- **KHÔNG dùng khi**: Thông tin dài · Vùng phụ đề đang chiếm chỗ
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `map-route` — Lộ trình hành quân / Route  (v1.6.0, overlay, list)
- **Input** (* bắt buộc): `label` ≤40; `items`* ≤6 mục×24; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Diễn biến hành quân, di chuyển của quân đội/nhân vật qua nhiều địa danh · Hành trình theo thứ tự địa điểm
- **KHÔNG dùng khi**: Chỉ 1 địa danh (dùng date-stamp hoặc lower-third) · Quá 6 điểm dừng
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.84) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `market-ticker` — Bảng thị trường  (v1.6.0, overlay, stat)
- **Input** (* bắt buộc): `change1`* ≤10; `change2` ≤10; `change3` ≤10; `dir1` ∈{up|down}; `dir2` ∈{up|down}; `dir3` ∈{up|down}; `label`* ≤40; `name1`* ≤20; `name2` ≤20; `name3` ≤20; `value1`* ≤14; `value2` ≤14; `value3` ≤14
- **Dùng khi**: Chỉ số VN-Index, HNX, giá vàng, dầu, tỷ giá · So sánh tăng/giảm trong ngày
- **KHÔNG dùng khi**: Quá 3 chỉ số · Số liệu không chắc chắn
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.92) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `photo-duo` — Hai ảnh + dòng chảy / Photo Duo  (v1.4.0, fullscreen, photo)
- **Input** (* bắt buộc): `big` ≤20; `img1`*; `img2`*; `label1`* ≤30; `label2`* ≤30; `stage` ∈{1|2|3|4|5|6}
- **Dùng khi**: Beat cần cho xem 2 nhân vật/đối tượng cùng lúc với mối quan hệ dòng chảy (tiền, ủng hộ, chuyển giao) giữa họ · Beat so sánh A -> B mà một ảnh nền duy nhất không kể được câu chuyện
- **KHÔNG dùng khi**: Chỉ một ảnh (dùng ảnh nền b-roll + template chữ thường) · 3 ảnh trở lên (chờ biến thể photo-trio) · Hai ảnh xếp ngang (chờ biến thể photo-duo-h)
- Ảnh nội dung: CÓ (không dùng nền trung tính)

### `photo-duo-h` — Hai ảnh đối đầu ngang / Photo Duo Horizontal  (v1.3.0, fullscreen, photo)
- **Input** (* bắt buộc): `foot` ≤60; `img1`*; `img2`*; `label1`* ≤20; `label2`* ≤20; `stage` ∈{1|2|3|4}; `title`* ≤40; `verdict` ≤40
- **Dùng khi**: Beat đối đầu trực diện 2 bên: ai thắng, ai thua, ai mạnh hơn · Cần người xem so sánh 2 gương mặt/cái tên trong một khung hình
- **KHÔNG dùng khi**: Hai ảnh xếp dọc theo dòng chảy (dùng photo-duo) · Một nhân vật duy nhất (dùng photo-hero) · So sánh bằng số liệu thuần không cần ảnh (dùng compare-bars hoặc versus-split)
- Ảnh nội dung: CÓ (không dùng nền trung tính)

### `photo-hero` — Ảnh lớn + số liệu / Photo Hero  (v1.3.0, fullscreen, photo)
- **Input** (* bắt buộc): `big`* ≤20; `img`*; `label`* ≤40; `stage` ∈{1|2|3|4}; `sub` ≤70
- **Dùng khi**: Beat 'một người, một con số': nhân vật cụ thể gắn với con số then chốt của câu chuyện · Cần người xem nhớ mặt nhân vật cùng lúc với số liệu
- **KHÔNG dùng khi**: Hai nhân vật trở lên (dùng photo-duo hoặc photo-duo-h) · Số liệu không gắn với nhân vật cụ thể (dùng stat-counter) · Trích dẫn lời nói (dùng photo-quote: headline = câu trích nguyên văn, subline = tên nguồn)
- Ảnh nội dung: CÓ (không dùng nền trung tính)

### `photo-quote` — Thẻ ảnh đa năng / Photo Quote  (v1.1.0, fullscreen, photo)
- **Input** (* bắt buộc): `img`*; `kicker` ≤20; `headline`* ≤48; `subline` ≤80; `stage` ∈{1|2|3|4}
- **Dùng khi**: Beat tin tức chung: một ảnh + một tiêu đề + một dòng phụ — dùng được cho mọi chủ đề · Trích dẫn lời nói: headline = câu trích nguyên văn, subline = tên nguồn, kicker tuỳ chọn
- **KHÔNG dùng khi**: Một người gắn với một con số then chốt (dùng photo-hero) · Hai ảnh đối đầu (dùng photo-duo-h)
- Ảnh nội dung: CÓ (không dùng nền trung tính)

### `podium-rank` — Bảng xếp hạng / Ranking  (v1.8.0, overlay, list)
- **Input** (* bắt buộc): `label` ≤40; `items`* ≤5 mục×40; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Bảng xếp hạng, top thành tích, kết quả nhiều vận động viên/đội · Liệt kê có thứ tự ưu tiên
- **KHÔNG dùng khi**: Chỉ 2 đối thủ (dùng scoreboard hoặc versus-split) · Danh sách không cần thứ hạng (dùng checklist)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.88) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.; v1.7.0 (2026-11-13): Đổi nền trong hạng 1: xanh trong rgba(34,211,238,.1) → rgba(255,255,255,.07), giống nền trong của poll-vote (CEO 13/11/2026).; v1.8.0 (2026-11-13): Bỏ viền xanh: xóa border rgba(34,211,238,.35) ở thẻ ngoài (CEO 13/11/2026).

### `poll-vote` — Thăm dò ý kiến  (v1.6.0, overlay, interactive)
- **Input** (* bắt buộc): `opt1`* ≤30; `opt2`* ≤30; `pct1`* ≤5 (có %); `pct2`* ≤5 (có %); `question`* ≤80
- **Dùng khi**: Kết quả khảo sát, thăm dò dư luận · So sánh 2 luồng ý kiến
- **KHÔNG dùng khi**: Quá 2 phương án · Không có số liệu %
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.92) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `preview-banner` — Banner preview / Preview Banner  (v1.2.0, overlay, banner)
- **Input** (* bắt buộc): `text`* ≤160
- **Dùng khi**: Beat preview sau hook: nêu vấn đề + nội dung chính trước khi đi sâu
- **KHÔNG dùng khi**: Liệt kê nhiều ý (mỗi beat phân tích dùng keyword-block riêng) · Câu quá dài quá 160 ký tự
- Ảnh nội dung: CÓ (không dùng nền trung tính)

### `quote-card` — Trích dẫn / Quote  (v1.6.0, overlay, quote)
- **Input** (* bắt buộc): `text`* ≤140; `label` ≤40; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Trích lời nhân vật, văn bản, hịch, thơ · Một câu nói mang tính biểu tượng
- **KHÔNG dùng khi**: Đoạn dài hơn hai câu · Không rõ nguồn trích dẫn
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.78) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `scoreboard` — Bảng tỷ số / Scoreboard  (v1.6.0, overlay, stat)
- **Input** (* bắt buộc): `label` ≤32; `text`* ≤60; `value`* ≤12; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Công bố tỷ số trận đấu, kết quả đối đầu · So sánh điểm số 2 bên
- **KHÔNG dùng khi**: Xếp hạng nhiều hơn 2 (dùng podium-rank) · Không có tỷ số cụ thể
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.9) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `section-caption` — Caption kết đoạn / Section caption  (v1.6.0, overlay, stat)
- **Input** (* bắt buộc): `text`* ≤70
- **Dùng khi**: Chốt một đoạn bằng một câu kết luận ngắn trước khi chuyển cảnh · Tóm tắt hệ quả của cụm số liệu vừa nêu
- **KHÔNG dùng khi**: Câu dài giải thích (dùng section-title hoặc quote-card) · Chữ nguồn (dùng source-footer-safe)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.92) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `section-header` — Tiêu đề cụm số liệu / Section header  (v1.6.0, overlay, stat)
- **Input** (* bắt buộc): `subline` ≤70; `title`* ≤40
- **Dùng khi**: Mở đầu một cụm số liệu trước khi thả các con số · Chuyển sang một nhóm số liệu mới trong cùng video
- **KHÔNG dùng khi**: Tiêu đề toàn cảnh (dùng section-title) · Beat chỉ có một con số (dùng stat-counter)
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `section-title` — Tiêu đề phần toàn khung  (v1.8.0, fullscreen, title)
- **Input** (* bắt buộc): `text`* ≤72; `label` ≤24
- **Dùng khi**: Mở đầu một chương hoặc phần mới, khi ảnh nền vẫn phải thấy được qua lớp phủ dưới 50% · Cần nhấn một tuyên bố rất ngắn bằng một nhịp toàn khung, không che kín ảnh
- **KHÔNG dùng khi**: Mọi phân cảnh thông thường · Đoạn đang cần quan sát hành động · Nhiều dòng giải thích hoặc số liệu · Cảnh ảnh đẹp cần giữ nguyên ảnh gốc — dùng lower-third/headline thay vì phủ tối toàn khung
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `share-bar` — Thanh cơ cấu / Share Bar  (v1.1.0, overlay, stat)
- **Input** (* bắt buộc): `title`* ≤40; `count` ∈{2|3|4}; `label1`* ≤22; `pct1`* ≤3; `label2`* ≤22; `pct2`* ≤3; `label3` ≤22; `pct3` ≤3; `label4` ≤22; `pct4` ≤3; `foot` ≤48; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Cơ cấu/thị phần/tỷ lệ các phần của MỘT tổng thể: 60% – 30% – 10% · Phân bổ ngân sách, nguồn gốc, thành phần, phiếu thuận/chống/trắng
- **KHÔNG dùng khi**: So sánh giá trị tuyệt đối giữa các đối tượng (dùng compare-bars) · Kết quả bình chọn hai phương án (dùng poll-vote) · Một con số tỷ lệ duy nhất (dùng stat-counter)
- **Ràng buộc**: bắt buộc thêm theo count; tổng = 100
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.0.0 (2026-11-12): Tạo mới.; v1.1.0 (2026-11-13): Đổi nền thẻ: rêu trong rgba(28,55,42,.85) → mực trong rgba(8,10,16,.68), chung mức chuẩn với nhóm mực trong (CEO 13/11/2026).

### `social-comment` — Bình luận viral  (v1.6.0, overlay, social)
- **Input** (* bắt buộc): `likes` ≤30; `platform` ≤20; `text`* ≤140; `user`* ≤30
- **Dùng khi**: Trích bình luận viral liên quan chủ đề · Thể hiện dư luận mạng xã hội
- **KHÔNG dùng khi**: Bình luận quá dài · Nội dung nhạy cảm chưa kiểm chứng
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.94) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `source-citation` — Trích nguồn tư liệu / Source  (v1.6.0, overlay, quote)
- **Input** (* bắt buộc): `text`* ≤60; `label` ≤24; `sublabel` ≤80; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Trích dẫn chính sử, văn bia, thần phả, hồi ký · Cần tăng độ tin cậy cho thông tin lịch sử
- **KHÔNG dùng khi**: Trích lời nhân vật (dùng quote-card) · Nguồn không xác định rõ
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.9) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `source-footer-safe` — Dòng nguồn an toàn lề phải  (v1.5.0, overlay, source)
- **Input** (* bắt buộc): `text`* ≤80; `label` ≤24; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Ghi nguồn cuối mỗi cảnh video tin tức dọc 720x1280 · Nguồn dài gồm nhiều báo, ngày tháng
- **KHÔNG dùng khi**: Dòng nguồn một dòng dài không ngắt · Chữ nguồn vượt 528px ở cỡ chữ đã chọn
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.5.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.65) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `stat-counter` — Số liệu lớn / Stat  (v1.10.0, overlay, stat)
- **Input** (* bắt buộc): `value`* ≤10; `unit` ≤12; `label` ≤40; `sublabel` ≤70; `tone` ∈{gold|volume|decline|money}; `lead` ≤70; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Có một con số then chốt cần người xem nhớ · So sánh quy mô, tỷ lệ, thời gian
- **KHÔNG dùng khi**: Câu không có số liệu · Nhiều hơn một con số trong cùng câu
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.10.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.82) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `step-flow` — Quy trình từng bước / Step Flow  (v1.1.0, overlay, list)
- **Input** (* bắt buộc): `title`* ≤36; `count` ∈{3|4}; `step1`* ≤34; `step2`* ≤34; `step3`* ≤34; `step4` ≤34; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Giải thích quy trình/cơ chế có THỨ TỰ: xin cấp phép, cách hoạt động, các giai đoạn xử lý · Câu có 'đầu tiên… sau đó… cuối cùng' hoặc các bước đánh số
- **KHÔNG dùng khi**: Danh sách ý song song không có thứ tự (dùng checklist) · Các mốc theo năm/ngày (dùng timeline-strip hoặc timeline-horizontal) · Tuyến đường địa lý (dùng map-route)
- **Ràng buộc**: bắt buộc thêm theo count
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.0.0 (2026-11-12): Tạo mới.; v1.1.0 (2026-11-13): Đổi nền thẻ: rêu trong rgba(28,55,42,.85) → mực trong rgba(8,10,16,.68), chung mức chuẩn với nhóm mực trong (CEO 13/11/2026).

### `story-title` — Tiêu đề truyện kể  (v1.6.0, overlay, story)
- **Input** (* bắt buộc): `line1`* ≤40; `line2`* ≤40
- **Dùng khi**: Video kể chuyện/bình luận xã hội bằng chuỗi ảnh minh họa truyện tranh, mỗi ảnh theo một câu thuyết minh · Cần tiêu đề 2 dòng cố định phía trên xuyên suốt video
- **KHÔNG dùng khi**: Tiêu đề dài quá 40 ký tự mỗi dòng · Nền quá rối khiến dòng đỏ khó đọc ở bản render tĩnh
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `strike-verdict` — Gạch bỏ + kết quả / Strike Verdict  (v1.5.0, overlay, stat)
- **Input** (* bắt buộc): `label`* ≤40; `result`* ≤14; `struck`* ≤40; `sublabel` ≤70
- **Dùng khi**: Beat kết quả lật ngược kỳ vọng: điều ai cũng tưởng đúng đã sai · Cần người xem nhớ kết quả mới, và nhớ luôn cái cũ đã bị gạch bỏ
- **KHÔNG dùng khi**: Số liệu thuần không có kỳ vọng bị phá vỡ (dùng stat-counter) · So sánh 2-4 đối tượng bằng thanh ngang (dùng compare-bars) hoặc đối đầu toàn màn hình (dùng versus-split)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.2.0 (2026-11-13): I8-A (CEO 13/11/2026): thẻ rêu đủ cho overlay (X-01); nền thẻ đổi từ rgba(28,55,42,.85) sang nền rêu chuẩn đặc #1C372A + kẻ ô #2A4D3B 80px như hook-title-card.; v1.3.0 (2026-11-13): Sửa theo ý CEO 13/11/2026: nền thẻ về mực trong rgba(8,10,16,.82) như các template overlay khác (stat-counter, dual-stat); bỏ nền rêu đặc + kẻ ô vừa thêm ở v1.2.0.; v1.4.0 (2026-11-13): Tăng độ trong suốt: nền thẻ rgba(8,10,16,.82) → rgba(8,10,16,.75) theo ý CEO 13/11/2026.; v1.5.0 (2026-11-13): Tăng độ trong suốt thêm: nền thẻ rgba(8,10,16,.75) → rgba(8,10,16,.68) theo ý CEO 13/11/2026.

### `tactical-banner` — Dải báo động chiến thuật / Alert  (v1.4.0, overlay, alert)
- **Input** (* bắt buộc): `text`* ≤80; `label` ≤24; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Tình huống khẩn cấp, bước ngoặt trận đánh · Lệnh tác chiến, cảnh báo
- **KHÔNG dùng khi**: Thông tin thường nhật · Đã dùng alert-flash ở cảnh kề trước
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `thesis-marker` — Luận điểm chính / Thesis Marker  (v1.6.0, fullscreen, title)
- **Input** (* bắt buộc): `value`* ≤10; `text`* ≤60; `label` ≤30; `sublabel` ≤70; `accent` ∈{gold|red|cyan|green|violet|white…}
- **Dùng khi**: Mở đầu một luận điểm then chốt (vd: 'Điểm đầu tiên...', 'Nguyên nhân thứ hai...') · Chuyển sang ý phân tích mới trong video tài liệu, kinh tế, chính luận · Tạo nhịp ngắt trang trọng phân tầng nội dung
- **KHÔNG dùng khi**: Các câu kể lể thông thường · Đoạn có nhiều chi tiết vụn vặt không phải luận điểm chính · Nhiều dòng văn bản dài dòng
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Giảm nền (CEO 13/11/2026): gradient mực rgba(8,10,16,.98/.97) → rgba(8,10,16,.90).

### `timeline-horizontal` — Trục thời gian ngang / Timeline horizontal  (v1.6.0, overlay, list)
- **Input** (* bắt buộc): `items`* ≤5 mục×36; `label` ≤40
- **Dùng khi**: Diễn biến theo thời gian với 2-5 mốc ngắn (tiến độ dự án, lộ trình, lịch trình) · Cần người xem thấy trình tự ngang thay vì liệt kê dọc
- **KHÔNG dùng khi**: Chỉ có 1 mốc (dùng date-stamp) · Quá 5 mốc (chia thành nhiều cảnh) · Diễn biến dài nhiều năm cần liệt kê dọc (dùng timeline-strip)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.6.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.86) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `timeline-strip` — Dải niên đại / Timeline  (v1.5.0, overlay, list)
- **Input** (* bắt buộc): `label` ≤40; `items`* ≤5 mục×64; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: Liệt kê các mốc thời gian, triều đại, sự kiện theo trình tự · Tóm tắt diễn biến nhiều năm trong một cảnh
- **KHÔNG dùng khi**: Chỉ có 1 mốc thời gian duy nhất (dùng date-stamp) · Quá 5 mốc (chia thành nhiều cảnh)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.5.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,.86) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `trend-badge` — Huy hiệu xu hướng / Trend Badge  (v1.1.0, overlay, stat)
- **Input** (* bắt buộc): `label`* ≤28; `value`* ≤8; `dir` ∈{up|down|flat}; `sub` ≤44
- **Dùng khi**: Một con số CHỈ SỰ THAY ĐỔI có hướng rõ: tăng/giảm %, lên/xuống điểm, lãi/lỗ · Câu có động từ tăng, giảm, lao dốc, bứt phá kèm số cụ thể
- **KHÔNG dùng khi**: Con số tĩnh không có chiều thay đổi (dùng stat-counter) · Nhiều chỉ số cùng lúc (dùng market-ticker) · So sánh hai giá trị đối đầu (dùng dual-stat)
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.0.0 (2026-11-12): Tạo mới.; v1.1.0 (2026-11-13): Đổi nền thẻ: rêu trong rgba(28,55,42,.85) → mực trong rgba(8,10,16,.68), chung mức chuẩn với nhóm mực trong (CEO 13/11/2026).

### `typewriter-reveal` — Gõ máy chữ / Typewriter Reveal  (v1.9.0, overlay, keyword)
- **Input** (* bắt buộc): `text`* ≤80; `label` ≤30; `sublabel` ≤60; `accent` ∈{cyan|gold|red|green|violet|white…}
- **Dùng khi**: Trích xuất hồ sơ, tài liệu giải mật, chỉ dụ hoặc văn kiện · Ghi chú tình báo, dòng suy ngẫm, mật mã hoặc câu hỏi điều tra · Tạo nhịp gõ chữ kịch tính, hé lộ dần thông điệp
- **KHÔNG dùng khi**: Các câu dài quá 80 ký tự · Đoạn có nhiều số liệu cần đọc nhanh · Cảnh có chủ thể ở vị trí overlay che khuất
- Ảnh nội dung: không → đủ điều kiện nền trung tính
- **Lịch sử**: v1.9.0 (2026-11-13): Chuẩn nền thẻ mực trong (CEO 13/11/2026): nền thẻ rgba(8,10,16,0.70) → rgba(8,10,16,.68), chung mức với compare-bars/strike-verdict.

### `verdict-stamp` — Con dấu phán quyết / Verdict Stamp  (v1.0.0, overlay, text)
- **Input** (* bắt buộc): `text`* ≤14; `tilt` ∈{-15|0|15}; `tone` ∈{green|red}
- **Dùng khi**: Beat cần đóng dấu kết quả lên ảnh/video: thắng/thua, cấm/cho phép, hết hàng/còn hàng, mức án
- **KHÔNG dùng khi**: Chữ dài hơn 3 từ (dùng keyword-block) · Cần nền đục sau chữ (dùng strike-verdict hoặc compare-bars)
- Ảnh nội dung: không → đủ điều kiện nền trung tính

### `versus-split` — Đối đầu / Versus  (v1.5.0, fullscreen, transition)
- **Input** (* bắt buộc): `text`* ≤30; `label`* ≤30; `sublabel` ≤60; `accent` ∈{gold|red|cyan|green|pink|purple…}
- **Dùng khi**: So sánh hai bên giao tranh · Đối lập hai quan điểm hoặc hai lựa chọn
- **KHÔNG dùng khi**: Chỉ có một đối tượng · Câu không mang tính so sánh
- Ảnh nội dung: không → đủ điều kiện nền trung tính
