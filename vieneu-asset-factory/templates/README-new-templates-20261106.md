# Template mới 06/11/2026 — Gói chuyển sang tài khoản Muse khác

Ngày tạo gói: 06/11/2026. Nguồn cảm hứng: reel "Tại sao bang Texas chuyển xanh"
(trang Vietnam Business News, 05/11/2026) — toàn ảnh tĩnh + đồ họa tĩnh nền navy
sao + giọng đọc, số liệu được "diễn" bằng hình (đếm tăng, biểu đồ cột, gạch X,
mũi tên). Gói này tách 8 template + logic engine từ reel đó ra để dùng lại cho
video tin tức/giải thích. **Local only — không push GitHub nếu chưa có duyệt riêng.**

## 1. Cài đặt (4 bước)

1. **Templates:** copy toàn bộ thư mục `templates/` vào factory của tài khoản kia,
   giữ nguyên cấu trúc `templates/<id>/` (mỗi template đủ 3 file:
   `template.html` + `style.css` + `meta.json`). Nhớ copy cả
   `templates/_shared/transparent.png`.
2. **SFX:** copy 3 file `sfx/*.mp3` vào thư mục `sfx/` của factory bên kia
   (`whoosh_fast.mp3`, `heavy_thud_slam.mp3`, `boom_sub_impact.mp3`).
3. **Engine:** NẾU factory bên kia cùng base vieneu-asset-factory thì thay 3 file
   `bin/render_template.py`, `bin/render_draft.py`, `bin/preflight.py` bằng file
   trong `engine/` của gói. NẾU khác base thì KHÔNG ghi đè mù — merge theo danh
   sách hàm/khối mới ở mục 3 (Logic) bên dưới.
4. **Kiểm chứng:** dựng 1 project mẫu từ `examples/` (xem mục 4), chạy
   preflight → render_draft, mở file preview xem khung hình thật. Chỉ khi xem
   thấy hình đúng mới tính là xong (kiểm chứng dữ liệu + build không thay được
   kiểm chứng hiển thị).

## 2. Danh mục template

| Template | Ver | Mục đích | Inputs chính | SFX gợi ý |
|---|---|---|---|---|
| hook-title-card | 1.1.0 | Thẻ tiêu đề toàn màn hình cho beat hook 0–3s, nền xanh rêu kẻ ô vuông | line1 (req, ≤40), line2, line3, punch (req, ≤40) | whoosh_fast 0.6 |
| compare-bars | 1.1.0 | So sánh 2–4 đối tượng bằng thanh ngang, tỉ lệ theo giá trị | count (2/3/4, mặc định 2), title (req), label1–4, value1–4, w1–4 (0–100, dài nhất = 100), tone1–4, foot | heavy_thud_slam 0.35 |
| strike-verdict | 1.0.0 | Kỳ vọng cũ bị gạch đỏ + kết quả mới vàng lớn (beat "tưởng thế mà không phải thế") | struck (req, ≤40), result (req, ≤14), label (req, ≤40), sublabel | heavy_thud_slam 0.35 |
| photo-duo | 1.3.0 | 2 ảnh dọc khung vàng + số lớn + mũi tên (dòng chảy ảnh 1 → ảnh 2) | img1, img2 (req, ảnh), label1, label2 (req), big, stage 1–6 | heavy_thud_slam 0.35 |
| photo-hero | 1.2.0 | 1 ảnh lớn + 1 con số then chốt ("một người, một con số") | img (req, ảnh), big (req), label (req), sub, stage 1–4 | heavy_thud_slam 0.35 |
| photo-duo-h | 1.2.0 | 2 ảnh ngang + VS + kết luận vàng nghiêng (đối đầu trực diện) | img1, img2 (req, ảnh), title (req), label1, label2 (req), verdict, foot, stage 1–4 | boom_sub_impact 0.4 |
| photo-quote | 1.0.0 | Thẻ ảnh đa năng: 1 ảnh + kicker + headline + subline (cả trích dẫn: headline = câu trích, subline = tên nguồn) | img (req, ảnh), headline (req, ≤48), kicker, subline, stage 1–4 | whoosh_fast 0.6 |
| verdict-stamp | 1.0.0 | Con dấu đóng lên ảnh/video (dùng làm templateId trực tiếp hoặc lớp phủ `broll.stamps`) | text (req, ≤14, 1–3 từ), tone (green/red), tilt (-15/0/15) | heavy_thud_slam 0.35 |

Tên cũ (chỉ giữ trong ghi chú lịch sử): `compare-bars` trước là `duel-bars`;
`photo-quote` trước là `story-card`. Mọi template đều `hidesSubs: true`
(phụ đề karaoke ẩn trên part dùng template).

## 3. Logic tham khảo nhanh

### (a) Input ảnh — `render_template.py`

- `_image_uri(value, base_dir)`: đường dẫn tương đối resolve theo thư mục project
  (render_draft truyền qua argv 6); tuyệt đối hoặc `file://` giữ nguyên.
- `fill_placeholders`: thay `{{key}}` bằng giá trị input (escape HTML; riêng
  `items` thành `<li>`).
- `preflight.py` báo **lỗi** nếu file ảnh của input type `image` không tồn tại.
  Lưu ý: part chưa có TTS thì preflight bỏ qua toàn bộ kiểm template.
- Render bằng WeasyPrint 70.0 qua `write_pdf` + `pdftoppm -png -r 96`
  (WeasyPrint không có `write_png`); chạy bằng venv có WeasyPrint + PIL.

### (b) Video-slot (ảnh/video thay nhau trong khung) — `render_template.py` + `render_draft.py`

- Template photo nào có khung đều khai `videoSlots` trong meta (tọa độ ô trong
  không gian 720x1280) — nhưng đó chỉ là **fallback**.
- Input ảnh trỏ tới file video (.mp4/.mov/.webm/.mkv) thì `render_template.py`
  thay bằng `templates/_shared/transparent.png` (ảnh 1x1 trong suốt) để chừa lỗ.
- `render_draft.py` composite video **SAU** ảnh template, đè đúng ô trong của khung.
  Ô slot **đo trực tiếp từ khung viền vàng trên PNG template đã render**
  (`_gold_frame_rects`) vì bố cục flex dịch theo nội dung; meta chỉ là fallback.
- Thứ tự composite: nền → template PNG → slot video → dấu. Video tắt tiếng,
  lặp/cắt theo độ dài part. File video thiếu → `video-slot-thieu-bo-qua`
  (bỏ qua + ghi report); ô không trống (có ảnh thật) → `video-slot-khong-trong-bo-qua`.
- Template fullscreen opaque KHÔNG có lỗ alpha — video phải đè LÊN TRÊN template.

### (c) Reveal (các lớp hiện lần lượt) — `render_draft.py`

- `broll.reveal` = danh sách stage, vd `["1","2","3","4"]`; render từng stage
  thành PNG rồi nối bằng ffmpeg overlay `enable='gte(t,T)'`.
- Cắt cứng, **chia đều** thời lượng part; chỉ áp template full-stage
  (không full-stage thì bỏ qua + ghi report); stage render lỗi thì rơi về tĩnh 1 stage.
- Video trong ô slot chỉ hiện từ stage đầu tiên mà viền vàng của ô đã hiện.
- **Reveal KHÔNG khớp giọng đọc** (CEO 06/11/2026) — các lớp hiện lần lượt
  nối tiếp, độc lập với lời thoại.

### (d) Dấu — `render_draft.py` + `preflight.py` + template `verdict-stamp`

- `broll.stamps` = mảng, tối đa **3 dấu/part**; mỗi dấu
  `{text ≤14, tone green|red, tilt -15|0|15, on, at, sfx}`.
  `at` bắt buộc **> 0** và < thời lượng part; `sfx` riêng của dấu là
  `{"id": "heavy_thud_slam", "offsetSec": at, "volume": 0.35}`.
  `broll.stamp` đơn cũ vẫn chạy (`_normalize_stamps` coi là danh sách 1 phần tử).
- Dấu xoay bằng **CSS `transform: rotate()`** inline trong template
  verdict-stamp. WeasyPrint 70.0 **CÓ hỗ trợ CSS rotate 2D** (đã kiểm chứng
  bằng render thật) — KHÔNG dùng cơ chế PIL rotateInput (đã gỡ 06/11/2026).
- Dấu đóng vào **tâm ô ảnh** đo từ khung viền vàng trên PNG template đã render
  (`_gold_frame_centers` trong render_draft.py); hiện từ t=`at`
  (overlay `enable='gte(t,at)'`); composite **sau** cả video-slot.
- Dấu là lớp **độc lập** với lớp chữ: chữ thuộc template chính (render vào PNG
  template, hiện theo reveal stage); dấu là template riêng nền trong suốt
  composite lên trên. Template không có khung ảnh thì dấu rơi về giữa khung.
- Preflight kiểm từng dấu: text có + ≤14, tone/tilt hợp lệ, `on` phải là input
  ảnh của template, `at` ≥ giờ ảnh đó hiện (photo-duo img2 từ stage 5,
  photo-duo-h img2 từ stage 2, các ô còn lại từ stage 1), SFX dấu phải là
  heavy_thud_slam và offsetSec lệch `at` ≤ 0,15s. 2 dấu cùng một ô → cảnh báo.

### (e) SFX — `render_draft.py`

- Render chỉ đọc `part.broll.sfx` + SFX riêng từng dấu (dedup theo cặp
  id + mili-giây); KHÔNG đọc SFX trong meta template — Production copy SFX gợi
  ý của meta vào plan.
- **Part ID phải theo quy ước `...-scene<order>-part-<pi>`** thì SFX mới được thu:
  render thu SFX bằng cách tách hậu tố `-part-N` từ part ID
  (`part["id"].rsplit("-part-", 1)[1]`); ID ngắn kiểu `s1p1` thì SFX bị bỏ lặng lẽ.
- SFX nặng cap 0.4, limiter cuối 0.89; khung 3–7 SFX cho video 180–300s;
  beat hook/móc lại/kết luận phải có SFX; 0 SFX bị trả lại.
  Ngoại lệ: keyword-block và quote-card 1.5.0 không có SFX gợi ý theo thiết kế.

### (f) Phụ thuộc / quy ước chung

- **Font Anton** cho mọi template + karaoke (phụ đề 60px ở 720x1280, MarginV 256).
- Ảnh trong template **tĩnh hoàn toàn** (không Ken Burns) — Production cắt ảnh
  trước về đúng tỉ lệ khung: photo-duo 528x300, photo-hero 528x460,
  photo-duo-h 232x155 (3:2), photo-quote 528x380.
- Mọi `mediaSource` (cấp scene và cấp part) bắt buộc có chuỗi `source` không rỗng.
- CSS template: class tiền tố `broll-<id>`, thang vmin, màu vàng `#FBBF24`,
  không animation CSS; `radial-gradient` phải viết color-stop tường minh từng mốc
  (WeasyPrint rớt nền khi dùng color-stop 2 vị trí).
- **Bảng màu chuẩn (thống nhất toàn bộ template, 06/11/2026):** nền xanh rêu
  `#1C372A`, kẻ ô vuông `#2A4D3B` (ô 80px ở khung 720, kẻ dày 2px), vàng
  `#FBBF24`, chữ trắng `#fff`, chữ phụ xám `#cbd5e1`. Nền kẻ ô viết bằng 2
  `linear-gradient` + `background-size:80px 80px`, color-stop viết tường minh
  từng mốc như `radial-gradient` (WeasyPrint rớt nền khi dùng color-stop 2 vị trí).

## 4. Ví dụ plan ngắn

Lấy từ `examples/` (file đầy đủ, xem ngay cách dùng từng template).
File audio TTS KHÔNG kèm trong gói (nặng) — bên kia tự chạy TTS của họ.

### photo-duo 2 dấu (từ `newtpltest001-broll-plan.json`, scene 1 part 3)

```json
{
  "id": "xxx-scene1-part-3",
  "voiceText": "Musk thắng lớn, Paxton thua cuộc: hai dấu xanh đỏ đóng lên từng ảnh.",
  "broll": {
    "mediaType": "image",
    "templateId": "photo-duo",
    "inputs": {
      "img1": "build/media/images/musk.jpg",
      "img2": "build/media/images/paxton.jpg",
      "label1": "Elon Musk", "label2": "Ken Paxton",
      "big": "168 TRIỆU USD", "stage": "6"
    },
    "mediaSource": { "source": "Ảnh cắt từ reel Texas" },
    "stamps": [
      { "text": "CHIẾN THẮNG", "tone": "green", "tilt": "15",
        "on": "img1", "at": 1.2,
        "sfx": { "id": "heavy_thud_slam", "offsetSec": 1.2, "volume": 0.35 } },
      { "text": "THUA CUỘC", "tone": "red", "tilt": "-15",
        "on": "img2", "at": 2.2,
        "sfx": { "id": "heavy_thud_slam", "offsetSec": 2.2, "volume": 0.35 } }
    ]
  }
}
```

### compare-bars 4 bars (từ `newtpltest002-broll-plan.json`, scene 1 part 5)

```json
{
  "id": "xxx-scene1-part-5",
  "voiceText": "Bốn bang lớn nhất: California 54, Texas 40, Florida 30, New York 28 phiếu đại cử tri.",
  "broll": {
    "mediaType": "image",
    "templateId": "compare-bars",
    "inputs": {
      "count": "4", "title": "PHIẾU ĐẠI CỬ TRI",
      "label1": "CALIFORNIA", "value1": "54", "w1": "100", "tone1": "white",
      "label2": "TEXAS",      "value2": "40", "w2": "74",  "tone2": "gold",
      "label3": "FLORIDA",    "value3": "30", "w3": "56",  "tone3": "white",
      "label4": "NEW YORK",   "value4": "28", "w4": "52",  "tone4": "gold",
      "foot": "Bốn bang lớn nhất về phiếu đại cử tri"
    },
    "mediaSource": { "source": "Ảnh cắt từ reel Texas" },
    "sfx": { "id": "heavy_thud_slam", "offsetSec": 0, "volume": 0.35 }
  }
}
```

## 5. Nội dung gói

```
new-templates-20261106/
  README.md                         (file này)
  templates/                        (8 template, mỗi cái 3 file + _shared/transparent.png)
    hook-title-card/ compare-bars/ strike-verdict/
    photo-duo/ photo-hero/ photo-duo-h/ photo-quote/ verdict-stamp/
  engine/                           (file đầy đủ, không phải patch)
    render_template.py  render_draft.py  preflight.py
  sfx/                              (3 mp3)
    whoosh_fast.mp3  heavy_thud_slam.mp3  boom_sub_impact.mp3
  examples/                         (plan mẫu, không kèm audio TTS)
    newtpltest001-broll-plan.json  newtpltest001-input.json
    newtpltest002-broll-plan.json  newtpltest002-input.json
  tests/
    test_new_templates_all.py       (assert trên frame MP4 thật; cần 2 project
                                     test newtpltest001/002 mới chạy được)
```


- **ĐỔI NỀN 06/11/2026:** nền navy sao của 5 template fullscreen
  (hook-title-card, photo-duo, photo-hero, photo-duo-h, photo-quote) đã đổi
  thành xanh rêu kẻ ô vuông chuẩn (`#1C372A` + kẻ `#2A4D3B`, ô 80px, kẻ 2px);
  nền thẻ của 2 template overlay (compare-bars, strike-verdict) đổi từ
  `rgba(8,10,16,.82)` sang tông rêu `rgba(28,55,42,.85)`; verdict-stamp
  trong suốt nên giữ nguyên. Các template đã tăng minor version + ghi chú
  đổi trong `meta.json`.

## 6. Lưu ý

- Cụm "theo khung reel Vietnam Business News" trong description của meta là ghi
  chú nguồn gốc thiết kế, KHÔNG hiện trên màn hình — giữ nguyên, không scrub.
- hook-title-card 1.1.0 đã gỡ brand "VIETNAM BUSINESS NEWS" (06/11/2026):
  template không còn mang logo/tên kênh nào.
- Template photo-xxx phải ĐA NĂNG dùng cho nhiều kịch bản, không tạo nhiều
  template cấu trúc gần giống nhau (ưu tiên mở rộng template đã có).
- Cửa mở còn lại: ngoại lệ motion cho part photo-duo (tĩnh hoàn toàn 5–9s)
  chưa ghi vào skill QA; app chưa hỗ trợ nhập dấu/reveal (chỉ pipeline).
