# Từ điển viết tắt cho VieNeu-TTS (abbr_dict) — hướng dẫn cho agent

## Vấn đề

Engine Vieneu chuẩn hoá bằng sea-g2p (nằm trong `vieneu-tts-api`, **không được
sửa**) vẫn đọc sai một số từ/cụm. Ví dụ thật ở project BIGBANG (xem
`build/norm_chunks.json` trước khi có từ điển):

| Trong kịch bản | sea-g2p đọc thành | Vấn đề |
|---|---|---|
| BIGBANG | bê i gờ bê a nờ gờ | tên nhóm bị đánh vần từng chữ cái |
| WORLD TOUR | vê kép ô rờ lờ đê tê ô u rờ | cụm tiếng Anh bị đánh vần |
| COSMOS | xê ô ét mờ ô ét | từ tiếng Anh bị đánh vần |
| mạng xã hội X | mạng xã hội mười | chữ X bị đọc thành số La Mã 10 |

Ngược lại, những thứ sau engine đã làm **đúng** nên đừng thêm vào từ điển:
số và ngày ("90.000" → "chín mươi nghìn"), tên bài hát tiếng Anh để nguyên
("Haru Haru", "Fantastic Baby" — viết thường/hoa đầu từ nên được giữ nguyên,
G2P đọc bằng âm tiếng Anh thật),
cách đọc từng chữ cái đã đúng ("GDP" → "g d p"), "VIP" → "víp", "XX" → "ích ích".

## Nguyên tắc độc lập với nguồn vieneu-tts-api

- **Không sửa bất kỳ file nào** trong `~/workspace/vieneu-tts-api/` (kể cả
  `.venv` của nó) và không sửa engine/sea-g2p.
- Mọi code mới/chỉnh đều nằm trong `~/workspace/asset-factory/`:
  `bin/abbr_expand.py` (mới), `bin/normalize_chunks.py`,
  `bin/tts_batch.py` (móc từ điển), file này, và một đoạn trong `PIPELINE.md`.
- Khi update nguồn vieneu-tts-api, lớp từ điển không bị ảnh hưởng vì nó chỉ
  đọc `abbr_dict.json` của từng project và chạy trước khi gọi engine.

## Thứ tự lớp chuẩn hoá (quan trọng, đừng đảo)

1. Engine chuẩn hoá bằng sea-g2p → `build/norm_chunks.json` (bản gốc).
2. **Agent rà soát** các cặp (câu gốc → câu chuẩn hoá) trong norm_chunks,
   tìm từ/cụm còn sót, ghi cách đọc đúng vào từ điển.
3. Pipeline áp từ điển **trước khi gọi engine** ở lần chạy sau:
   `speech_text = expand(voiceText)` rồi engine mới chuẩn hoá speech_text.
   Làm vậy để phần còn lại của câu (số, ngày, từ thường) vẫn được sea-g2p
   xử lý như cũ, và audio với timing karaoke dùng chung một bản speech_text.
4. `karaoke.py` không cần sửa: pairs vẫn giữ câu gốc để hiển thị, còn
   `align_words` đã chịu được nở 1→N (vd "BIGBANG" 1 chữ gốc → "bích beng"
   2 chữ chuẩn hoá).

## File từ điển

- Vị trí: `<project>/abbr_dict.json`, tức ngay trong thư mục dự án.
- Xuất kèm ZIP (từ 2026-10-25): `assemble_project.py` tự thêm file này vào
  ZIP ở `<pid>/abbr_dict.json`, cùng cấp với `project.json`, khi project có
  từ điển; project không có từ điển thì ZIP giữ nguyên như cũ. Sau khi bung
  ZIP vào `projects/` của VieNeu Studio local, file nằm ở
  `projects/<pid>/abbr_dict.json` để logic local đọc. Định dạng ổn định cho
  phía local: `{"version": 1, "entries": {term: cách đọc}}`, khớp
  case-sensitive, giá trị không chứa dấu kết câu; giá trị có thể chứa tag
  `<en>...</en>` (engine Vieneu đọc tag này bằng âm tiếng Anh).
- Dạng chuẩn (khuyên dùng):
  `{"version": 1, "entries": {"TERM": "cách đọc", ...}}`
- Dạng phẳng cũng được chấp nhận (toàn bộ key cấp cao là term); key bắt đầu
  bằng `_` được bỏ qua (dùng ghi chú).

## Quy tắc viết entry (xem `bin/abbr_expand.py`)

- Khớp **đúng chữ hoa/thường** như trong kịch bản (case-sensitive). Term
  "AI" sẽ không chạm vào từ "ai" trong câu. Nếu kịch bản dùng nhiều biến thể
  ("BIGBANG", "BigBang"), thêm đủ các biến thể.
- Cụm dài ưu tiên trước, thay một lượt duy nhất (không thay đệ quy).
- Dùng cụm dài để khóa ngữ cảnh khi một chữ cái đứng một mình dễ nhầm:
  viết `"mạng xã hội X": "mạng xã hội ích"` thay vì `"X": "ích"`.
- Cách đọc **không chứa dấu kết câu (. ! ?) hay xuống dòng** — entry vi phạm
  bị bỏ qua và báo `ABBR-WARN` (vì sẽ làm lệch chia câu của karaoke).
- Cách đọc có ba dạng, chọn theo bản chất của term (quy tắc này rút ra từ
  test thật 2026-10-25, xem thêm bên dưới):
  1. **Dạng tiếng Anh (ưu tiên cho cụm/tên tiếng Anh thật):** giá trị là
     chính dạng tiếng Anh viết thường, nên bọc trong tag
     `<en>...</en>`, vd `"WORLD TOUR": "<en>world tour</en>"`. Lý do:
     G2P đọc được từ tiếng Anh viết thường bằng âm tiếng Anh thật
     (`world tour` → `wˈɜːld tˈʊɹ`, `fantastic baby` → `fæntˈæstɪk bˈeɪbi`);
     chỉ dạng VIẾT HOA HẾT mới rơi vào nhánh đánh vần của normalizer.
     Tag `<en>` do mình đưa vào **sống sót qua normalize** (đã test:
     `chuyến <en>world tour</en> của...` → norm giữ nguyên tag), chunking
     coi `<en>...</en>` là một token không tách, và `karaoke.py` đã tự bóc
     tag trước khi căn timing (`strip_tags`, dòng 221) nên alignment an toàn.
  2. **Nghĩa tiếng Việt:** khi muốn khán giả hiểu nghĩa hơn là nghe tên
     gốc, vd `"WORLD TOUR": "lưu diễn thế giới"`.
  3. **Phiên âm Việt:** chỉ dùng khi tên gọi đã có cách đọc mượn quen thuộc
     trong tiếng Việt, vd `"BIGBANG": "bích beng"`. Đừng tự bịa phiên âm
     cho cụm tiếng Anh (vd "uôn tua" cho WORLD TOUR đã bị chứng minh là
     yếu: mất phụ âm cuối rld, nghe gần "won" hơn "world").
- **Số La Mã và ký hiệu chữ cái (X, XX, V, IV, ...): KHÔNG được coi là
  đúng mặc định.** Trước khi kết luận một cách đọc kiểu đánh vần là đúng,
  luôn đối chiếu ngữ cảnh trong câu: kỷ niệm bao nhiêu năm? lần thứ mấy?
  chương mấy? Vì cùng một ký hiệu, ngữ cảnh đổi thì nghĩa đổi hẳn: XX
  trong "tour kỷ niệm 20 năm ... [XX: COSMOS]" phải là "hai mươi", không
  phải "ích ích"; ngược lại X trong "mạng xã hội X" là tên chữ cái "ích",
  không phải số 10. Đây là việc chỉ agent làm được (engine không có ngữ
  cảnh), nên bỏ sót nó là lỗi của khâu rà soát, không phải của engine.
  Không được viết code tự đổi XX → 20 mù: ở chỗ khác XX có thể là nghĩa
  khác (vd ký hiệu, mã), nên quyết định luôn thuộc về agent theo từng câu.

## Quy trình cho mỗi project (agent làm)

1. Chạy `normalize_chunks.py` lần đầu (chưa có từ điển) để có norm_chunks gốc.
2. Đọc các cặp (câu gốc → câu chuẩn hoá), khoanh những chỗ engine đọc sai.
3. Ghi `<project>/abbr_dict.json` (chỉ những chỗ sai thật, đừng lạm dụng).
4. Chạy `bin/abbr_expand.py <project_id>` để xem báo cáo thay thế từng part.
5. Chạy lại `normalize_chunks.py` (norm mới theo speech_text) rồi `tts_batch.py`
   (part nào có từ điển mới hơn file WAV sẽ đọc lại kể cả không có `--force`,
   nhưng chạy `--force` cho chắc khi vừa sửa từ điển), rồi `karaoke.py`.
6. Kiểm chứng: pairs mới phải giữ nguyên câu gốc ở vế trái, vế phải chứa cách
   đọc mới; nghe/kiểm tra frame karaoke nếu cần; rồi mới render lại.

## Ví dụ từ điển project BIGBANG (đã áp dụng)

```json
{"version": 1,
 "entries": {"BIGBANG": "bích beng",
             "WORLD TOUR": "<en>world tour</en>",
             "COSMOS": "cốt mốt",
             "mạng xã hội X": "mạng xã hội ích",
             "XX": "hai mươi"}}
```

LỊCH SỬ 2026-10-25: entry WORLD TOUR ban đầu là "uôn tua", user chất vấn
và test chứng minh dạng tiếng Anh tốt hơn nên đã đổi sang
"<en>world tour</en>"; cùng ngày user chỉ ra XX trong tên tour chính là
số 20 (tour kỷ niệm 20 năm) nên thêm "XX": "hai mươi" — trước đó agent
từng bỏ sót XX vì xếp "ích ích" vào loại "đã đúng" mà không đối chiếu
ngữ cảnh (xem checklist số La Mã ở mục Quy tắc viết entry).

Ví dụ chung (chưa áp cho project cụ thể, chỉ để tham khảo):
`"SVĐ" → "sân vận động"`, `"TP.HCM" → "thành phố Hồ Chí Minh"`,
`"THPT" → "trung học phổ thông"`. Ngược lại, đừng thêm `"GDP"` (đọc từng chữ
cái đã đúng) hay tên bài hát tiếng Anh thông thường.

## Bảng tham chiếu viết tắt đã quyết (quy tắc CEO tối 30/10/2026)

Tra bảng này TRƯỚC khi ghi entry mới: term đã quyết thì project mới dùng
lại đúng cách đọc này, không học lại từ đầu; term mới quyết xong thì bổ
sung vào bảng. Phân loại theo luật đánh vần / đọc thành từ trong skill
Sản xuất (mục Lớp AI rà soát phát âm).

| Term | Loại | Cách đọc | Ghi chú |
| SJC | đánh vần | ét giây xê | sea-g2p đã đúng, không cần entry |
| GDP | đánh vần | g d p | sea-g2p đã đúng, không cần entry |
| DOJI | đọc thành từ | đô di | sea-g2p đọc sai thành "đê ô giây i" (đo 30/10/2026); biến thể "đô zi" chấp nhận theo giọng vùng, chọn một, không ghi cả hai |
| BIGBANG | đọc thành từ | bích beng | tên nhóm, không đánh vần |
| COSMOS | đọc thành từ | cốt mốt | |
| WORLD TOUR | tiếng Anh | <en>world tour</en> | phiên âm "uôn tua" đã bị bác 25/10/2026 vì yếu (mất phụ âm cuối, nghe gần "won") |
| Đ (đứng độc lập) | luật chung | đờ | sea-g2p để trơ thành token chết, audio mất tiếng (vụ 067); luật tự động trong abbr_expand.py, không cần entry từng project |
| Ă (đứng độc lập) | luật chung | á | như Đ: token chết, audio mất tiếng |
| Â (đứng độc lập) | luật chung | ớ | G2P đọc sang tiếng Anh ("a circumflex"); luật tự động trong abbr_expand.py |
