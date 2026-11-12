# Quy tắc mật độ chữ cho B-roll (bổ sung cho Doctrine v3.1)

> Tài liệu này là **hướng dẫn bắt buộc** cho mọi agent/Muse dàn cảnh video từ repo này.
> Nó không thay thế `skills/EDITORIAL_DOCTRINE.md` (v3.1) và `skills/broll-director/SKILL.md` —
> nó siết chặt phần mà Doctrine cố tình để mở: Doctrine **không khóa cứng tỷ lệ chữ** và
> **không cấm các cảnh chữ liên tiếp**. Thực tế cho thấy nếu agent hiểu mọi part đều là
> "beat cần nhấn mạnh" thì video sẽ ra chữ ở gần như 100% part, và vì bản render giữ
> overlay suốt cửa sổ của part nên người xem thấy chữ gần như liên tục. Tài liệu này
> đảo mặc định lại: **mặc định là không chữ, chỉ gắn chữ khi có lý do cụ thể**.
>
> Agent dàn cảnh PHẢI đọc tài liệu này cùng với `skills/EDITORIAL_DOCTRINE.md` và
> `skills/broll-director/SKILL.md` trước khi viết `broll-plan.json`.

## 0. Nguyên tắc mặc định: không chữ trước, có chữ sau

- Một part **mặc định không gắn template** (trong `broll-plan.json` part đó không có
  `templateId`, chỉ còn ảnh nền + chuyển động, và phụ đề karaoke vẫn hiện bình thường).
- Chỉ gắn template chữ khi part đó thỏa **ít nhất một** điều kiện ở §1, đồng thời không
  phạm `notFor` của template đó trong `templates/<id>/meta.json`.
- Không có thông tin cụ thể thì để part không template. **Cấm bịa chữ** để lấp đầy
  template, cấm dùng chữ chung chung, sáo rỗng.

## 1. Khi nào ĐƯỢC gắn template chữ

Chỉ các beat nhấn mạnh sau đây (khớp với `whenToUse` của từng template):

| Beat | Template điển hình |
|---|---|
| Con số then chốt cần người xem nhớ (đúng một con số) | `stat-counter` |
| Mốc thời gian, sự kiện | `date-stamp`, `timeline-strip` |
| Trích dẫn nguyên văn | `quote-card` |
| Luận điểm khẳng định | `thesis-marker` |
| Đối đầu A vs B | `versus-split`, `compare-bars` |
| Tỉ số, bảng xếp hạng | `scoreboard`, `podium-rank` |
| Mở chương, mở video | `section-title`, `breaking-banner` |
| Câu hỏi mở đầu, đặt vấn đề | `typewriter-reveal` |
| Từ khóa dồn dập, thực thể nổi bật | `keyword-burst`, `keyword-block` |
| Thăm dò, bình luận viral | `poll-vote`, `social-comment` |
| Nguồn trích dẫn | `source-citation` |

Ma trận chọn theo chủ đề video nằm ở §7 của `skills/broll-director/SKILL.md`
(tin tức, chiến tranh, thể thao, tài chính, trending, lịch sử) — vẫn có hiệu lực,
nhưng chỉ áp dụng cho các part đã qua được §0 và §1.

## 2. Khi nào KHÔNG được gắn template chữ

- Part miêu tả bối cảnh, phong cảnh, hành động, cảm xúc tự nhiên.
- Part dẫn nhập / khoảng thở thị giác (`boundaryHint: "breath"`, hoặc đoạn dẫn trước
  chuỗi liệt kê dồn dập — giữ master shot với `useBroll: false`).
- Part liệt kê từng thực thể (enumeration): mỗi thực thể là một beat `cutaway-standard`
  với `inputs: {}` — **không điền `text` vào `cutaway-standard`**. `keywords` của part
  này chỉ dùng để tìm/tạo ảnh minh họa, không phải chữ hiển thị.
- Part không có thông tin cụ thể, xác thực nào để đưa lên màn hình.
- Part đã có một template chữ khác bao phủ cùng ý (tránh trùng ý bằng hai lớp chữ).

## 3. Kỷ luật nội dung chữ (áp dụng cho mọi template đã gắn)

- `label` (nhãn chính), `text` (nội dung chính), `value`/`unit` (số liệu) phải là thông
  tin cụ thể, xác thực của đúng part đó, lấy từ kịch bản — không viết chung chung.
- `sublabel` (nhãn phụ) chỉ được điền khi nó bổ sung ý nghĩa thật: con số, tỷ lệ %,
  mốc thời gian, địa danh, thuộc tính then chốt. Không có thì **bắt buộc để `""`** —
  phần tử rỗng sẽ tự ẩn. Cấm các nhãn phụ chung chung ("thông tin chi tiết",
  "ghi chú", "bổ sung", "bối cảnh", "giải thích"...).
- Tôn trọng `required` và `maxLength` của từng trường trong `meta.json` (cổng
  `PIPELINE.md` + `bin/preflight.py` sẽ chặn nếu vi phạm, nhưng agent phải tự đúng
  từ lúc viết plan).

## 4. Tương tác với phụ đề — lý do thứ hai để giữ chữ thưa

- Part có template chữ thật sẽ bị ẩn phụ đề karaoke (`subsHidden`) để tránh chen chữ.
  Từ 31/10/2026, mọi template đều khai `"hidesSubs": true` (42/42) — ngoại lệ
  `clip-caption`/`story-title` đã bỏ, không còn template nào giữ phụ đề khi có chữ.
- Hệ quả: gắn chữ tràn lan không chỉ làm màn hình rối mà còn làm mất phụ đề ở hầu
  hết video. Giữ chữ thưa cũng là giữ phụ đề.

## 5. Kiểm tra cuối trước khi render (bắt buộc)

Trước khi chạy render, rà lại `broll-plan.json` và trả lời 3 câu hỏi:

1. **Đếm:** có bao nhiêu part mang `templateId` trên tổng số part? Nếu gần như 100%
   part đều có template thì staging đã sai — quay lại §0 và gỡ template khỏi các
   part miêu tả/khoảng thở.
2. **Đối chiếu:** mỗi template đã gắn có chỉ ra được beat nào ở §1 không, và có phạm
   `notFor` trong `meta.json` của nó không? Template nào không chỉ ra được thì gỡ.
3. **Soi chữ:** mọi `sublabel` đều có ý nghĩa thật (số/%/ngày/địa danh) hay còn nhãn
   phụ chung chung? Mọi `text`/`label` đều có trong kịch bản hay đã bị bịa thêm?
   Còn chữ chung chung hoặc bịa thì sửa hoặc gỡ template.

Chỉ khi cả 3 câu đều đạt mới được render.
