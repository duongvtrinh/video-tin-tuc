# Thư viện nhạc nền (BGM) — VieNeu Asset Factory

24 track nhạc nền royalty-free, chia theo 8 mood để agent tự chọn theo nội dung video.
File MP3 256–320kbps, dài 1.5–5 phút — đủ làm nền cho video 3–5 phút (loop/cắt nếu cần).

## Nguồn & License

Toàn bộ track của **Kevin MacLeod**, tải trực tiếp từ **incompetech.com**
(kho nhạc miễn phí nổi tiếng nhất giới editor YouTube, không cần login).

- **License: Creative Commons Attribution 4.0 (CC BY 4.0)**
  https://creativecommons.org/licenses/by/4.0/
- Được dùng thương mại, được đăng YouTube/Facebook **có bật kiếm tiền**,
  với điều kiện duy nhất: **ghi công (attribution)**.

## Cách ghi công khi đăng video

Dán vào phần mô tả video (description), thay `<Tên track>` bằng track đã dùng:

```
<Tên track> by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0
```

Ví dụ:

```
Thinking Music by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0
```

Mỗi track trong `bgm_catalog.json` đã có sẵn trường `attribution` — agent/app
có thể copy nguyên văn vào mô tả khi xuất bản.

## Cấu trúc

```
bgm/
├── bgm_catalog.json      # metadata 24 track (id, title, moods, duration, license, attribution, file)
├── README.md             # file này
├── calm/                 # êm dịu, nhẹ nhàng
├── dramatic/             # kịch tính, cao trào
├── funny/                # hài hước, vui nhộn
├── news/                 # thời sự, bản tin (đều, không lấn giọng đọc)
├── inspirational/        # truyền cảm hứng, tích cực
├── suspense/             # hồi hộp, căng thẳng
└── sad/                  # buồn, trầm lắng
    upbeat/               # sôi động, năng lượng
```

## Gợi ý chọn mood cho video tin tức

| Loại nội dung                          | Mood gợi ý              |
|----------------------------------------|-------------------------|
| Bản tin thời sự thường ngày            | `news`                  |
| Phân tích địa chính trị, xung đột      | `dramatic`, `suspense`  |
| Tin vui, thành tựu, câu chuyện cảm động | `inspirational`, `calm` |
| Tin buồn, tưởng niệm                   | `sad`                   |
| Tin giải trí, chuyện lạ, hài           | `funny`, `upbeat`       |

Lưu ý kỹ thuật: nhạc nền nên phát ở mức **-20 đến -28 dB** dưới giọng đọc
(ducking), tránh track có đoạn cao trào đột ngột đè lên lời bình.
