# TEMPLATE_SPEC — đặc tả meta.json (specVersion 2) và bộ kiểm tra

Nguồn chuẩn: `templates/_tokens.json` (màu, thang cỡ chữ, SFX), `templates/_themes.json` (chủ đề + token nền),
`bin/meta_check.py` (kiểm giá trị input), `bin/validate_templates.py` (kiểm toàn catalog).
Danh sách template: `docs/TEMPLATE_CATALOG.md` (tự sinh).

## 1. Cấu trúc thư mục
`templates/<id>/{template.html, style.css, meta.json}`. Thư mục/tệp bắt đầu bằng `_` là hạ tầng, loader bỏ qua
(KHÔNG tạo thư mục con rỗng-meta như `_shared/`: `check_templates.py` và app từng duyệt mọi thư mục con).
Ảnh trong suốt cho ô video: `assets/transparent.png`, engine tự sinh.

## 2. Khóa meta.json
| Khóa | Bắt buộc | Ý nghĩa |
|---|---|---|
| `id`, `name`, `version`(semver), `status`(active/draft/retired) | ✔ | `id` = tên thư mục |
| `schemaVersion` (=1), `specVersion` (=2) | ✔ | specVersion 2 = có `placement`, `neutralBgEligible`, input có `values/min/max/pattern` |
| `mode` overlay/fullscreen/cutaway · `background` transparent/opaque | ✔ | |
| `placement` | v2 | `subtitle-bottom` mặc định · `flush-bottom` · `edge-bottom` · `full-stage` (bắt buộc cho mode fullscreen) · `none` (cutaway). Thay các tập ID hardcode trong `render_draft.py` |
| `neutralBgEligible` | v2 | `true` ⇔ template không có input ảnh, trừ template bị loại trừ (cutaway-standard DEC-268, preview-banner DEC-274 — luôn cần ảnh/video thật). |
| `category`, `capability`, `description`, `whenToUse`, `notFor` | ✔ | `notFor` trỏ template khác dạng `(dùng <id>)` — id phải tồn tại (M09) |
| `themes` | ✔ | tập con id trong `_themes.json`; `general` = dùng được cho mọi video |
| `supportedAspectRatios`, `hidesSubs`(bool), `maxStage` | ✔ | `hidesSubs` luôn `true` trên thực tế (karaoke.py ẩn phụ đề mọi template từ 31/10/2026) |
| `inputs` / `exampleInputs` / `exampleVariants` | ✔ | xem §3 |
| `constraints` | | xem §4 |
| `sfx` | | object `{id, offsetSec≥0, volume∈(0,1]}`; id thuộc 8 file chuẩn; nặng ≤ 0.4 |
| `accent` | | `{type:"enum", default}`; giá trị: `gold red cyan green pink purple orange white` (+ alias `violet`) |
| `videoSlots` | | khóa trỏ tới input `type:image` |
| `changelog` | | mảng `{version,date,note}` — lịch sử đặt ở đây, KHÔNG trong `description` |

## 3. Khóa của một input
`type` (`string`/`enum`/`image`) · `required` · `maxLength` (input danh sách: **mỗi mục**) · `maxItems` · `values` (enum) · `default` ·
`min`,`max`,`integer` (số) · `pattern`,`patternHint` (vd `poll-vote`: `68%` vì `{{pct}}` vừa là chữ vừa là `width:`) ·
`noEffect:true` (khai nhưng engine không đọc: `position`, `animation`).

## 4. constraints
- `{"type":"requiredWhen","countKey":"count","keysByCount":{"3":["label3",…]}}` — `count=N` thì các khóa liệt kê phải có.
- `{"type":"sum","countKey":"count","keysByCount":{…},"equals":100,"tolerance":1}` — tổng phải bằng.
Preflight và validator cùng gọi `meta_check.check_constraints` — một nguồn logic.

## 5. Theme
`plan.theme` (hoặc `inputs.theme` của part) ∈ `_themes.json`. Engine thêm `--broll-bg`, `--broll-grid` vào `:root`; thiếu/không biết → `general` (nền rêu cũ, hình không đổi). Template toàn màn hình dùng `var(--broll-bg,#1C372A)`.
Preview JS: host truyền `part.tplVars` để cùng hiệu ứng.

## 6. SFX
Chuẩn trong `_tokens.json`. Nặng = tên chứa `thud|slam|boom`, trần 0.4 (mixer cắt thầm lặng). `offsetSec` âm bị engine kẹp về 0 (trước đây `adelay` âm làm ffmpeg lỗi ở part đầu video).

## 7. Mã kiểm tra `bin/validate_templates.py`
| Mã | Kiểm |
|---|---|
| M01/M02 | khóa bắt buộc, id=thư mục, enum status/mode/background, semver, tỉ lệ khung, hidesSubs bool |
| M03 | themes thuộc registry |
| M04 | sfx là object, id chuẩn, volume, cap nặng, offset |
| M05/M06 | kiểu input, maxLength, enum có values, default ∈ values, accent hợp lệ, input số có min/max/pattern |
| M07 | exampleInputs: đủ bắt buộc, đúng giới hạn, đúng ràng buộc; exampleVariants |
| M08 | placeholder HTML ⇔ inputs; input chết |
| M09 | notFor trỏ template tồn tại |
| M10 | tiền tố class `broll-` |
| M11 | màu ngoài `_tokens`, cỡ chữ ngoài thang, animation, radial-gradient 2 vị trí, font Anton |
| M12 | placement / neutralBgEligible nhất quán |
| M13 | description quá dài/chứa ngày |
| M14/M15 | constraints, videoSlots hợp lệ |
| M16 | độ phủ theme (< 4 template/theme → cảnh báo) |
| M17 | tệp hạ tầng |
| M18 | tên template trong tài liệu (kể cả ô bảng) phải tồn tại |

Chạy: `python3 bin/validate_templates.py [--strict] [--json] [--only a,b] [--no-docs]`. Exit 1 nếu có ERROR.
