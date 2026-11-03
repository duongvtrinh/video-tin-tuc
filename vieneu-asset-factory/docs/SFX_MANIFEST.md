# Hiệu ứng âm thanh (SFX) — manifest

8 file MP3 hiệu ứng KHÔNG nằm trong repo này (công cụ đẩy snapshot chỉ nhận
file UTF-8, không nhận file nhị phân). Bản khôi phục đã kiểm chứng:
thư mục Drive "sfx" (đủ 8 file, kiểm chứng 03/11/2026) — tải về vào
`vieneu-asset-factory/sfx/` trước khi render cần SFX. Tổng 292KB.

## Cách app dùng

Pipeline render (`bin/render_draft.py`) chèn SFX tại `part.startSec +
offsetSec` theo gợi ý SFX trong `broll-plan.json` của từng voice part
(kế hoạch B-roll do agent lập, đọc catalog template để gợi ý SFX phù hợp).
SFX không gắn cố định với template nào — mapping nằm trong từng plan.

## Danh sách 8 file

| File | Dung lượng | Vai trò |
|------|-----------|---------|
| `boom_sub_impact.mp3` | 20 KB | Tiếng nổ trầm, nhấn cao trào |
| `cinematic_riser.mp3` | 24 KB | Âm dâng, chuyển đoạn kịch tính |
| `heavy_thud_slam.mp3` | 8,6 KB | Tiếng đập mạnh, đóng sầm |
| `paper_rip.mp3` | 6,1 KB | Tiếng xé giấy |
| `punch_impact.mp3` | 5,2 KB | Tiếng đấm, va chạm |
| `radar_glitch.mp3` | 6,9 KB | Tiếng glitch, tín hiệu điện tử |
| `typing_fast.mp3` | 204 KB | Tiếng gõ phím nhanh, dài nhất |
| `whoosh_fast.mp3` | 4,6 KB | Tiếng vút nhanh, chuyển cảnh |

## Lưu ý

- File MP3 nhị phân nên không đi qua công cụ đẩy snapshot; lấy từ thư mục
  Drive "sfx" theo BOOTSTRAP §7 của monorepo (không phải từ repo này).
- Khi tái tạo: giữ nguyên tên file (pipeline và plan tham chiếu đúng tên
  này); thay file khác cùng tên vẫn chạy được nhưng đổi chất âm.
