# Thư viện nhạc nền (BGM) — manifest

24 track Kevin MacLeod, CC-BY 4.0, chia 8 mood (mỗi mood 3 track). File MP3 đã nằm trong repo (`vieneu-asset-factory/bgm/`, đẩy 04/11/2026 qua giao diện web sau khi CEO duyệt); Drive chỉ còn là bản backup. Nếu chưa có file, select_bgm.py exit 2 và preflight báo "BGM không tồn tại" (không crash mù, không lặng lẽ). Tổng ~170MB, mỗi file 3,8–12MB.

## License & ghi công

Toàn bộ track của **Kevin MacLeod** (incompetech.com), **CC BY 4.0** (https://creativecommons.org/licenses/by/4.0/). Được dùng thương mại, được đăng YouTube/Facebook có bật kiếm tiền, với điều kiện duy nhất là **ghi công**. Mỗi track có sẵn trường `attribution` — copy nguyên văn vào mô tả video khi xuất bản, ví dụ: `Thinking Music by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0`.

## Cách app dùng thư viện này

- Agent tự đoán mood theo chủ đề video → ghi vào `broll-plan.json` (xem `bin/select_bgm.py`).
- Khi render: BGM lặp (loop), âm lượng 0.12, sidechain ducking theo giọng đọc, fade-out 2 giây cuối video. Ghi công tự động vào README của ZIP export.
- File MP3 256–320kbps, dài 1,5–5 phút — đủ làm nền cho video 3–5 phút (loop/cắt nếu cần).

## Danh sách 24 track

| # | Track | Mood | Thời lượng | File | Attribution |
|---|-------|------|-----------|------|-------------|
| 1 | Deliberate Thought | calm | 2:58 | `calm/deliberate_thought.mp3` | Deliberate Thought by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 2 | Meditation Impromptu 01 | calm | 3:33 | `calm/meditation_impromptu_01.mp3` | Meditation Impromptu 01 by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 3 | Meditation Impromptu 02 | calm | 4:09 | `calm/meditation_impromptu_02.mp3` | Meditation Impromptu 02 by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 4 | Hitman | dramatic | 3:21 | `dramatic/hitman.mp3` | Hitman by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 5 | Devastation and Revenge | dramatic | 3:05 | `dramatic/devastation_and_revenge.mp3` | Devastation and Revenge by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 6 | Five Armies | dramatic | 2:36 | `dramatic/five_armies.mp3` | Five Armies by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 7 | Sneaky Snitch | funny | 2:17 | `funny/sneaky_snitch.mp3` | Sneaky Snitch by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 8 | Monkeys Spinning Monkeys | funny | 2:05 | `funny/monkeys_spinning_monkeys.mp3` | Monkeys Spinning Monkeys by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 9 | Merry Go - Distressed | funny | 2:00 | `funny/merry_go_distressed.mp3` | Merry Go - Distressed by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 10 | Thinking Music | news | 3:16 | `news/thinking_music.mp3` | Thinking Music by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 11 | Local Forecast - Elevator | news | 3:09 | `news/local_forecast_elevator.mp3` | Local Forecast - Elevator by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 12 | Airport Lounge | news | 5:08 | `news/airport_lounge.mp3` | Airport Lounge by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 13 | Inspired | inspirational | 4:46 | `inspirational/inspired.mp3` | Inspired by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 14 | Heart of Nowhere | inspirational | 2:52 | `inspirational/heart_of_nowhere.mp3` | Heart of Nowhere by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 15 | Montauk Point | inspirational | 3:40 | `inspirational/montauk_point.mp3` | Montauk Point by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 16 | Oppressive Gloom | suspense | 3:19 | `suspense/oppressive_gloom.mp3` | Oppressive Gloom by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 17 | Volatile Reaction | suspense | 2:45 | `suspense/volatile_reaction.mp3` | Volatile Reaction by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 18 | Darkest Child | suspense | 3:59 | `suspense/darkest_child.mp3` | Darkest Child by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 19 | Heartbreaking | sad | 1:36 | `sad/heartbreaking.mp3` | Heartbreaking by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 20 | Long Road Ahead | sad | 2:26 | `sad/long_road_ahead.mp3` | Long Road Ahead by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 21 | Sad Trio | sad | 4:12 | `sad/sad_trio.mp3` | Sad Trio by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 22 | Carefree | upbeat | 3:25 | `upbeat/carefree.mp3` | Carefree by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 23 | Wallpaper | upbeat | 3:40 | `upbeat/wallpaper.mp3` | Wallpaper by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |
| 24 | Who Likes to Party | upbeat | 4:18 | `upbeat/who_likes_to_party.mp3` | Who Likes to Party by Kevin MacLeod (incompetech.com) — Licensed under CC BY 4.0 |

## Nguồn tải lại (nếu cần khôi phục file)

Mỗi track có `source_url` trỏ thẳng file MP3 gốc trên incompetech.com (xem `bgm_catalog.json`,
đi kèm thư mục bgm/). Tải lại từ đó sẽ được đúng file gốc — nhưng nếu chưa có bgm/ thì
chưa có catalog để đọc URL; lúc đó lấy catalog từ Muse cũ cùng với file nhạc.
