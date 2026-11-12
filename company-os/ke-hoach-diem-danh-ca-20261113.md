# Kế hoạch: Tab điểm danh nhận ca — SHIFT_CHECKIN

- Ngày lập: 2026-11-13 03:05 (+07), theo lệnh CEO 03:04 13/11.
- Trạng thái: **ĐÃ DUYỆT + ĐÃ TRIỂN KHAI GĐ 1–3 (13/11 ~03:20). GĐ 4 (ca thật đầu tiên 06:00/06:05 13/11) đang chờ chạy; GĐ 5 (push repo) chờ CEO duyệt riêng.**
- **CEO duyệt 13/11 03:17 +07:** tên tab + cột tiếng Anh (SHIFT_CHECKIN; BRANCH_EMAIL / REG_DATE / REG_TIME / HANDOVER_SIGNOFF); còn lại thông qua, thực hiện. GĐ 1–3 ĐÃ XONG 13/11 ~03:20: tab SHIFT_CHECKIN + DEC-257, skill COO (bước 0b) + Production (nhận ca), lịch coo-scan-0600 (thêm bước 0b) + prod-pipeline-0600 (dời 06:00 → 06:05, bước 4 mới), spec + scheduled-tasks-setup + improvement-log IMP-20261113-<mã-chi-nhánh>-01; test trên tab SHIFT_CHECKIN_TEST (3 chi nhánh mô phỏng + dòng trùng + dòng ngày cũ) ĐẠT, tab test đã xóa. **Lưu ý: D8 vẫn chưa quyết; theo cổng hiện hành (READY) danh sách chia L = 0 nên ca đầu tiên ký EMPTY — không phải cơ chế hỏng.**
- Vấn đề gốc: L1 trong rà soát toàn bộ 12/11 (đua claim 06:00 không phân xử được — xem `~/workspace/company-os/ra-soat-toan-bo-20261112.md`).
- Cơ sở đã kiểm chứng trước khi viết: thân lịch `coo-scan-0600` và `prod-pipeline-0600` (đọc live 13/11), Sheet sống sau đợt xóa 12/11 ~20:20 (TOPICS 150 dòng: APPROVED 87 / READY 57 / DUPLICATE 5 / HOLD 1; TASKS 60 dòng: DELIVERED 58 / CANCELLED 1 / RETURNED 1).

---

## 1. Vấn đề đang giải

**Hiện tại (L1):** mọi chi nhánh cùng chạy pipeline lúc 06:00, cùng chọn 3 READY đầu Sheet, cùng đọc "chưa có dòng TASKS" rồi cùng ghi CLAIMED trong khoảng vài giây. Luật "2 dòng CLAIMED cùng TOPIC_ID thì dòng tạo sau dừng" không thực thi được vì TASKS chỉ có UPDATED_AT dạng ngày — không xác định được dòng nào tạo sau. Hậu quả: hai bên cùng dừng (mất chủ đề) hoặc cùng làm một video; luật "ghi sau thắng" (R4-10) hợp thức hóa va chạm thay vì ngăn nó.

**Cơ chế mới đề xuất (ý CEO):** thay "ai nhanh tay thì được" bằng **đăng ký theo thứ tự + chia lô theo thứ tự đăng ký**. Chi nhánh đăng ký sớm nhận các lô đầu của danh sách chủ đề đã duyệt; mỗi chi nhánh ký nhận lô của mình; người ký cuối cùng "đóng cửa" (xóa danh sách trong ngày). Đua claim biến mất vì lô của mỗi chi nhánh được xác định từ thứ tự đăng ký — không còn hai bên cùng chọn 3 READY đầu Sheet nữa.

**Phụ thuộc tiên quyết — D8:** cơ chế này chỉ CHIA chủ đề, không TẠO chủ đề. Danh sách chia (mục 4) hôm nay đang RỖNG: 57 READY đều đã có TASKS. Nếu D8 chưa quyết và CEO chưa flip APPROVED→READY thì ngày đầu tiên chạy, mọi chi nhánh đều ký "EMPTY — no topics left". D8 phải quyết TRƯỚC hoặc CÙNG lúc với kế hoạch này (xem GĐ 0).

---

## 2. Thiết kế tab SHIFT_CHECKIN

Tên tab đề xuất: **SHIFT_CHECKIN** (tên ngắn, đúng chức năng; chốt tên ở GĐ 0 nếu CEO muốn tên khác).

| Cột | Tên cột | Định dạng | Ai ghi | Ghi chú |
|-----|---------|-----------|--------|---------|
| A | BRANCH_EMAIL | email đầy đủ của chi nhánh, vd `branch@example.com` | COO (lúc đăng ký) | Chữ ký định danh, đúng luật email đầy đủ (quyết BBB 12/11). Không dùng mã rút gọn. |
| B | REG_DATE | `YYYY-MM-DD` (giờ Asia/Saigon) | COO | Ngày đăng ký ca. |
| C | REG_TIME | `HH:MM:SS` (giờ Asia/Saigon) | COO | Giờ COO ghi lúc append. Chỉ là bản ghi đọc được; **thứ tự đăng ký lấy theo THỨ TỰ DÒNG, không lấy theo cột này** (xem mục 7.1). |
| D | HANDOVER_SIGNOFF | chuỗi ký nhận (mục 5) hoặc trống | Sản xuất (lúc nhận ca) | Trống = chưa ký nhận. COO để trống khi đăng ký. |

- Dòng 1 là tiêu đề (không xóa bao giờ). Dữ liệu từ dòng 2. Frozen row 1.
- Mỗi chi nhánh đăng ký **đúng 1 dòng mỗi ngày**. Không dropdown, không công thức.
- Tab dùng chung đa chi nhánh như các tab khác: mỗi phòng chỉ ghi dòng của email mình (COO ghi cột A–C dòng của mình; Sản xuất ghi cột D dòng của mình). Không sửa dòng của chi nhánh khác.

---

## 3. Timeline trong ngày (giờ Asia/Saigon)

| Giờ | Ai | Việc |
|-----|----|------|
| 06:00 | COO (lịch `coo-scan-0600`, bước mới 0b) | Kiểm tra cửa chặn hạn mức (đã có ở bước 0: đọc COO_CHECKIN mới nhất). Nếu quá 95% → **không đăng ký** (chi nhánh hôm đó không nhận lô mới, Production vẫn làm video đang dở — xem mục 7.7). Nếu còn hạn mức → append 1 dòng đăng ký (A–C), D để trống. |
| 06:00–06:05 | — | Cửa sổ đăng ký. Các COO khác nhau đăng ký xong trong khoảng này. |
| 06:05 | Sản xuất (lịch `prod-pipeline-0600` dời 06:00 → 06:05) | Đọc tab SHIFT_CHECKIN + danh sách chủ đề (mục 4), tính hạng của mình, xác định lô, ký nhận vào cột D dòng của mình, rồi claim các TOPIC_ID trong lô vào TASKS (bước 5–7 cũ giữ nguyên làm chốt chặn cuối). Sau đó làm tiếp các bước pipeline cũ (giao Production, QA, báo cáo). |
| 06:05–06:30 | Sản xuất (từng chi nhánh) | Sau khi ký xong, tự kiểm tra có phải người ký cuối cùng không (mục 6). |
| 06:30 | — | **Hạn chót ký nhận.** Dòng hôm nay chưa ký sau 06:30 coi như "không nhận ca" (mục 7.4). |
| Ngày hôm sau 06:00 | COO đăng ký đầu tiên trong ngày | Dọn dòng tồn đọng của ngày cũ nếu còn (mục 7.4). |

**Lưu ý về giờ chạy thật của cron:** lịch 06:00 có thể được dispatch sớm tối đa ~5 phút (quy ước runtime). Vì vậy Production KHÔNG được đọc tab ngay khi job khởi động — bước đầu tiên của ca 06:05 phải chờ đến đúng 06:05 wall-clock (đọc giờ hệ thống, ngủ tới 06:05) rồi mới đọc tab đăng ký. Ngược lại COO đăng ký sớm (05:55–06:00) là vô hại. Nếu không có bước chờ này, khoảng cách 5 phút có thể co về 0 và cơ chế mất tác dụng.

---

## 4. Thuật toán chia lô

### 4.1. Danh sách chia (L)

L = các chủ đề thỏa CẢ 3 điều kiện, **theo thứ tự Sheet trong TOPICS** (giữ nguyên luật "theo thứ tự Sheet", không đổi sang xếp theo điểm):

1. STATUS = READY, TOPIC_ID đã có (không trống), chưa có dòng TASKS nào cho TOPIC_ID đó.
2. **Phụ thuộc D8:** nếu CEO chọn D8-B (đổi nghĩa READY, cổng sang APPROVED + chưa có TASKS) thì điều kiện 1 đổi thành STATUS = APPROVED. Kế hoạch này viết theo D8-A; nếu D8-B thì thay đúng một chữ này, còn lại không đổi.
3. L được đọc (snapshot) lúc 06:05. CEO flip READY sau 06:05 có hiệu lực từ ngày hôm sau.

**Số liệu thật hôm nay (13/11, sau đợt xóa):**
- Theo D8-A: L = **0 chủ đề** (57 READY đều đã có TASKS) → ngày đầu tiên mọi chi nhánh ký "HẾT" (xem mục 1).
- Theo D8-B: L = 87 APPROVED − 3 đã có TASKS (058/059/114) = **84 chủ đề → 28 lô**.

### 4.2. Hạng và lô

- Hạng `r` = vị trí dòng đăng ký của chi nhánh trong các dòng **ngày hôm nay**, tính từ trên xuống (dòng đầu tiên = hạng 1). Chỉ tính dòng đầu tiên của mỗi email trong ngày; dòng đăng ký trùng (mục 7.3) không tính hạng.
- Cỡ lô `B` = **3** (giữ trần nhận 3 chủ đề/ca, DEC-199 — không đổi).
- Lô của hạng `r` = L[3(r−1) : 3r] (cắt theo chỉ số 0-based: hạng 1 lấy L[0:3], hạng 2 lấy L[3:6], …).
- Nếu lát cắt rỗng → chi nhánh đó ký "EMPTY — no topics left" (mục 5).
- Nếu lát cắt còn 1–2 chủ đề (phần dư cuối danh sách) → lấy hết phần dư, ký rõ số lượng còn lại (mục 5).
- Các chủ đề không ai lấy (hạng vượt quá số lô, hoặc chi nhánh không đăng ký) **ở lại trong L ngày hôm sau** — danh sách được tính lại mỗi sáng, không mất chủ đề.

### 4.3. Ví dụ (giả sử D8-B, L = 84 chủ đề)

| Hạng (thứ tự đăng ký) | Lô nhận | Ký nhận |
|---|---|---|
| 1 — chi nhánh đăng ký đầu tiên | L[0:3] | `06:05:12 \| TOPIC-356, TOPIC-357, TOPIC-358` |
| 2 | L[3:6] | `06:05:20 \| TOPIC-359, TOPIC-360, TOPIC-361` |
| 3 | L[6:9] | `06:05:31 \| TOPIC-362, TOPIC-363, TOPIC-364` |
| … | … | … |
| 28 | L[81:84] | `06:06:02 \| TOPIC-440, TOPIC-441, TOPIC-442` |
| 29 trở đi | (rỗng) | `06:06:15 \| EMPTY — no topics left` |

Ví dụ phần dư: nếu L = 85 chủ đề thì hạng 29 lấy L[84:85] = 1 chủ đề, ký `06:06:15 | còn 1: TOPIC-443`.

---

## 5. Quy tắc ký nhận (cột D)

Sản xuất ghi vào cột D **dòng đăng ký của chính mình** (dòng đầu tiên có A = email mình, B = ngày hôm nay), đúng một lần, định dạng:

- Đủ lô: `HH:MM:SS | TOPIC-xxx, TOPIC-yyy, TOPIC-zzz` (giờ ký nhận + 3 TOPIC_ID, theo đúng thứ tự trong L).
- Phần dư: `HH:MM:SS | còn N: TOPIC-xxx, ...` (N = 1 hoặc 2).
- Hết chủ đề: `HH:MM:SS | EMPTY — no topics left`.
- Không được ghi gì khác vào cột D (không ghi chú dài, không ghi lý do — lý do thuộc về báo cáo ca pipeline).

Sau khi ký nhận, Sản xuất claim đúng các TOPIC_ID đã ký vào TASKS bằng bước claim-then-verify cũ (pipeline bước 5–7). **Cột D là cam kết phân lô; TASKS CLAIMED mới là khóa sản xuất.** Nếu hai bên tính ra cùng TOPIC_ID (do snapshot L lệch nhau — mục 7.5), luật bước 7 cũ vẫn áp dụng: dòng tạo sau dừng, ghi DUP_NOTE.

---

## 6. Quy tắc "đóng cửa" (người ký cuối cùng xóa danh sách)

Sau khi ký nhận xong, mỗi chi nhánh tự kiểm tra: **tất cả các dòng ngày hôm nay (mỗi email tính dòng đầu tiên) đã có cột D không trống chưa?**

- Chưa hết → không phải người cuối → không làm gì thêm.
- Đã hết → mình là người ký cuối cùng → có trách nhiệm **đóng cửa**: **xóa toàn bộ danh sách trong ngày** (mọi dòng dữ liệu, không xóa dòng tiêu đề).

**Cách xóa (quyết định kỹ thuật — cần CEO chốt, xem mục 11.5):**

- **Khuyến nghị: xóa nội dung bằng values.clear (A2:D đến dòng cuối), KHÔNG dùng deleteDimension.** Lý do: hai chi nhánh có thể cùng thấy "đã ký hết" trong cùng một giây (người ký áp chót đọc sau khi người cuối đã ký) và cùng đóng cửa. Clear là lũy đẳng — lần clear thứ hai trên vùng đã trống là no-op, vô hại. Ngược lại deleteDimension dịch chuyển dòng: lần xóa thứ hai trên cùng khoảng dòng sẽ xóa nhầm các dòng khác (vd dòng đăng ký mới của ngày hôm sau nếu đã có, hoặc dòng của ca khác).
- **Trước khi clear, người đóng cửa phải snapshot toàn bộ dòng trong ngày vào nhật ký ngày của mình** (`~/memory/YYYY-MM-DD.md`: email + giờ đăng ký + nội dung ký nhận từng chi nhánh). Tab bị xóa là mất dấu vết kiểm tra; snapshot là bằng chứng duy nhất còn lại về thứ tự đăng ký của ngày đó. Không snapshot thì không đóng cửa.
- Chỉ xóa sau khi đã xác minh: (a) mọi dòng hôm nay đã ký; (b) snapshot đã ghi xong. Nếu bước nào chưa đạt thì không đóng, để lại cho ngày hôm sau dọn (mục 7.4).

---

## 7. Phân tích logic — các trường hợp biên và cách xử lý

Đây là phần phân tích kỹ thuật của cơ chế. Mỗi trường hợp đều có cách xử lý đã chốt trong kế hoạch; trường hợp nào chưa có cách xử lý sẽ ghi rõ là "cần CEO quyết".

### 7.1. Thứ tự đăng ký lấy theo dòng hay theo giờ?

**Vấn đề:** cột C là giờ do COO tự ghi. Hai chi nhánh có thể ghi cùng giờ (cùng giây), ghi giờ lệch đồng hồ, hoặc ghi giờ sớm hơn thực tế. Không thể dùng cột C làm căn cứ phân xử.

**Cách xử lý:** thứ tự đăng ký = **thứ tự dòng trong tab** (dòng trên = đăng ký trước). Append qua Sheets API được serialize theo thứ tự xử lý — mỗi lần append là nguyên tử, dòng nào được ghi trước thì ở trên. Cột C chỉ là bản ghi đọc được cho người, không dùng để phân xử. Skill COO ghi rõ: "ghi giờ hệ thống lúc append, không ghi giờ khác; nếu hai dòng có giờ mâu thuẫn với thứ tự dòng thì thứ tự dòng thắng".

### 7.2. Hai COO append cùng lúc

Append đồng thời được API xếp hàng — dòng nào xử lý trước thì ở trên. Không có trạng thái "cùng dòng". Trường hợp xấu nhất là thứ tự giữa hai chi nhánh đến cùng giây là do API quyết định — chấp nhận được vì cả hai đều đăng ký đúng giờ; lô khác nhau nhưng đều có lô (trừ khi hết danh sách). Không cần khóa phân tán.

### 7.3. Một chi nhánh đăng ký 2 dòng (trùng)

**Vấn đề:** COO chạy lại (retry sau lỗi, hoặc cron chạy 2 lần) append dòng thứ hai cùng email cùng ngày. Dòng thứ hai trống cột D sẽ làm kẹt kiểm tra "đã ký hết chưa" (mục 6) — không ai đóng cửa được.

**Cách xử lý:** chỉ dòng ĐẦU TIÊN của mỗi email trong ngày được tính (hạng + kiểm tra đóng cửa). Dòng trùng bị bỏ qua hoàn toàn — Sản xuất ký vào dòng đầu tiên, không ký dòng trùng. Khi đóng cửa, clear toàn bộ dòng trong ngày (kể cả dòng trùng). Skill COO thêm: "append xong đọc lại tab; nếu đã có dòng của mình trong ngày thì không append nữa".

### 7.4. Chi nhánh đăng ký nhưng không ký nhận (Production lỗi / không chạy)

**Vấn đề:** cột D của dòng đó mãi trống → không ai đủ điều kiện "đã ký hết" → không ai đóng cửa → dòng tồn sang ngày hôm sau, và ngày hôm sau kiểm tra "dòng hôm nay đã ký hết chưa" sẽ thấy cả dòng cũ (nếu tính cả dòng cũ) — tab kẹt vĩnh viễn.

**Cách xử lý (3 lớp):**
1. **Hạn chót 06:30:** sau 06:30, dòng hôm nay chưa ký coi như "không nhận ca" — chi nhánh đó mất lô hôm nay, và dòng đó KHÔNG còn chặn việc đóng cửa (kiểm tra đóng cửa sau 06:30 tính dòng quá hạn là "đã xử lý xong").
2. **Kiểm tra đóng cửa chỉ tính dòng ngày hôm nay** (lọc B = ngày hôm nay). Dòng ngày cũ không bao giờ chặn đóng cửa.
3. **Dọn tồn đọng:** COO đăng ký đầu tiên của ngày mới, trước khi append dòng của mình, clear các dòng có B < ngày hôm nay nếu còn sót (đọc tab, thấy dòng cũ thì clear trước). Đây là lưới an toàn cuối cùng.

### 7.5. Hai chi nhánh tính ra cùng TOPIC_ID (snapshot L lệch nhau)

**Vấn đề:** mỗi chi nhánh đọc L độc lập lúc 06:05. Nếu L thay đổi giữa hai lần đọc (vd một chi nhánh khác vừa ghi TASKS CLAIMED, hoặc CEO flip READY đúng lúc đó), lát cắt có thể chồng nhau.

**Cách xử lý:** đây là rủi ro dư — cửa sổ chỉ vài giây và lô được chia theo hạng nên chồng nhau chỉ xảy ra khi L đổi trong lúc đọc. Chốt chặn cuối vẫn là bước claim-then-verify + bước 7 cũ (dòng CLAIMED trùng → dòng tạo sau dừng, ghi DUP_NOTE). Ngoài ra cột D ghi rõ lô mỗi bên đã ký nên chồng chéo nhìn thấy ngay trong tab. Không thêm khóa mới — giữ cơ chế đơn giản, dựa vào chốt chặn đã có.

### 7.6. Không có chi nhánh nào đăng ký / không có chủ đề

- Không có dòng đăng ký nào: Production 06:05 đọc tab thấy trống → không ký gì, không nhận lô, làm tiếp các bước pipeline cũ (video đang dở, kiểm tra BLOCKED…) và báo cáo ca ghi "không có chi nhánh nào đăng ký ca".
- Có đăng ký nhưng L rỗng (tình trạng hôm nay theo D8-A): mọi chi nhánh ký "EMPTY — no topics left", không claim gì, ca kết thúc phần nhận lô như luật cũ (pipeline bước 12: báo không có chủ đề READY).

### 7.7. Chi nhánh quá hạn mức 95%

COO kiểm tra cửa chặn ở bước 0 (đã có) TRƯỚC khi đăng ký. Quá 95% → **không đăng ký** → không có lô mới hôm đó. Production 06:05 vẫn chạy bình thường để hoàn thành video đang dở (bước 2 cũ) — chỉ không nhận lô mới. Không đăng ký "giữ chỗ" rồi bỏ lô: lô bị giữ mà không làm sẽ làm chi nhánh sau mất lượt oan (hạng của họ bị đẩy xuống nhưng lô đầu bị bỏ trống — thực ra không mất: lô bỏ trống ở lại L ngày hôm sau; nhưng ngày hôm đó lô đó không ai làm, lãng phí một ngày của chủ đề đó).

### 7.8. Đăng ký trễ (sau 06:05)

COO nào append sau 06:05 (cron trễ, lỗi mạng rồi retry) thì dòng đó **không được tính cho ca hôm nay**: Production đã đọc snapshot lúc 06:05 và không thấy dòng đó → chi nhánh trễ không có hạng, không có lô, không ký nhận. Dòng trễ vẫn nằm trong tab và sẽ bị clear lúc đóng cửa hoặc lúc dọn tồn đọng ngày hôm sau. Chi nhánh trễ hôm đó chỉ làm video đang dở. Không có cơ chế "đăng ký bù" trong ngày.

### 7.9. Đóng cửa hai lần (double-close)

Đã phân tích ở mục 6: hai chi nhánh cùng thấy "đã ký hết" và cùng đóng cửa. Dùng **values.clear** (lũy đẳng) thay vì deleteDimension thì lần thứ hai vô hại. Nếu CEO vẫn muốn deleteDimension (xóa hẳn dòng) thì bắt buộc thêm bước "đọc lại và đối chiếu nội dung dòng trước khi xóa" — và vẫn còn cửa sổ đua nhỏ. Khuyến nghị giữ values.clear.

### 7.10. Công bằng dài hạn

Chi nhánh có cron chạy đúng giờ nhất sẽ luôn đăng ký sớm và luôn nhận lô đầu (chủ đề đầu Sheet — thường là chủ đề mới nhất / điểm cao nhất). Đây là hệ quả trực tiếp của luật "đăng ký sớm nhận lô đầu" mà CEO đề ra (thưởng cho đúng giờ). Không coi là lỗi. Nếu sau này CEO muốn xoay vòng công bằng (vd hạng đảo theo ngày chẵn/lẻ), đó là thay đổi luật riêng — không làm trong đợt này.

### 7.11. Tab mới có ảnh hưởng gì tới các luật cũ?

- **R1–R10 / claim-then-verify / bước 7 trùng CLAIMED:** giữ nguyên làm chốt chặn cuối (mục 5, 7.5).
- **Trần 3 chủ đề/ca (DEC-199):** giữ nguyên — cỡ lô B = 3.
- **Cửa chặn hạn mức 95%:** giữ nguyên — COO không đăng ký khi quá hạn (mục 7.7); pipeline bước 1 vẫn đọc COO_CHECKIN.
- **Cổng sản xuất (READY + TOPIC_ID + chưa có TASKS):** giữ nguyên, chỉ thay cách CHỌN lô (từ "3 READY đầu Sheet" sang "lô theo hạng đăng ký").
- **D1/D2 (nguồn đọc hạn mức):** không chạm — cơ chế này không đọc hạn mức ở đâu khác.
- **L2 (coo-scan bước 8 đọc báo cáo pipeline "buổi sáng hôm nay"):** không chạm.
- **DEC-121 / REPORT_ID:** không chạm — tab mới không dùng REPORT_ID.

---

## 8. Thay đổi cần làm (khi CEO duyệt kế hoạch)

| # | Hạng mục | Nội dung |
|---|----------|----------|
| 1 | Tab mới | Tạo tab `SHIFT_CHECKIN` trong workbook `1neK…` (4 cột A–D như mục 2, frozen row 1). Ghi DEC mô tả tab + luật (DEC số tiếp theo sau DEC-247; lưu ý D7: DEC-248..256 đang chờ ghi X-01–X-08 + BBB — DEC của tab này lấy số sau đó). |
| 2 | Skill COO (`media-coo`) | Thêm bước 0b sau bước 0 (điểm danh COO_CHECKIN): kiểm tra hạn mức → append dòng đăng ký (A–C) → đọc lại tab xác nhận dòng của mình (chống đăng ký trùng, mục 7.3). Thêm quy tắc dọn dòng ngày cũ (mục 7.4.3). |
| 3 | Skill Production (`media-video-production`) | Thêm bước nhận ca đầu ca: chờ đến 06:05 → đọc tab + tính hạng + xác định lô → ký nhận cột D → claim TASKS theo lô (bước 5–7 cũ). Thêm quy tắc tự kiểm tra đóng cửa + snapshot + clear (mục 6). |
| 4 | Lịch `coo-scan-0600` | Thêm bước đăng ký vào thân lịch (bước 0b). Giờ giữ 06:00. |
| 5 | Lịch `prod-pipeline-0600` | Dời 06:00 → **06:05**; thay bước 4 (chọn 3 READY đầu Sheet) bằng bước nhận ca theo hạng đăng ký; các bước còn lại giữ nguyên. |
| 6 | Tài liệu repo | Cập nhật `google-sheet-spec.md` (thêm spec tab SHIFT_CHECKIN + luật chia lô) và `scheduled-tasks-setup.md` (giờ pipeline 06:05). Ghi improvement-log (IMP mới, mã chi nhánh đầy đủ). |
| 7 | Push GitHub | **Riêng, sau khi CEO duyệt riêng** (luật đẩy tối 12/11: luôn hỏi trước khi đẩy). Không đẩy cùng đợt triển khai local. |

---

## 9. Kế hoạch thực hiện

### GĐ 0 — Chốt tiên quyết (CEO, trước khi làm gì khác)
- Quyết D8 (A hay B) — vì danh sách L phụ thuộc vào nó (mục 1, 4.1).
- Chốt tên tab (`SHIFT_CHECKIN` hay tên khác).
- Chốt cách đóng cửa: values.clear (khuyến nghị) hay deleteDimension (mục 6, 7.9).
- Chốt đăng ký là bước trong `coo-scan-0600` (khuyến nghị — ít lịch hơn, dùng chung bước kiểm tra hạn mức ở bước 0) hay lịch riêng.
- Xác nhận cỡ lô B = 3 và hạn chót ký nhận 06:30.

### GĐ 1 — Tạo tab + ghi DEC (làm local, không động vào lịch cũ)
- Tạo tab SHIFT_CHECKIN (4 cột, frozen row 1) trên workbook `1neK…`.
- Ghi 1 dòng DEC mô tả tab + luật chia lô + luật đóng cửa (CEO ký F+G theo lệ).
- Cập nhật `google-sheet-spec.md` (spec tab mới) — local trước, push sau.

### GĐ 2 — Sửa skill + lịch (local)
- Sửa skill COO (bước 0b + dọn dòng cũ) và skill Production (bước nhận ca + đóng cửa).
- Sửa thân lịch: `coo-scan-0600` thêm bước đăng ký; `prod-pipeline-0600` dời 06:05 + thay bước 4.
- Đọc lại cả hai thân lịch xác nhận (đúng quy trình sửa cron: view → update thân đầy đủ → view lại).

### GĐ 3 — Kiểm thử (trước ca thật đầu tiên)
- Test trên tab test riêng (`SHIFT_CHECKIN_TEST`): mô phỏng 3 chi nhánh đăng ký (dùng email test, không dùng email chi nhánh thật), kiểm tra: thứ tự dòng = hạng; chia lô đúng công thức (đủ 3 / phần dư / hết); ký nhận đúng định dạng; người cuối đóng cửa bằng clear (clear 2 lần liên tiếp vẫn an toàn); dòng trùng bị bỏ qua; dòng ngày cũ không chặn đóng cửa.
- Xóa tab test sau kiểm thử.
- Kiểm chứng: đọc lại tab test sau mỗi bước, đối chiếu công thức bằng tay.

### GĐ 4 — Chạy thật ca đầu tiên (06:00 ngày hôm sau sau khi GĐ 0–3 xong)
- Agent chính giám sát ca 06:00 (đăng ký) và 06:05 (nhận ca): đọc tab live sau 06:05, đối chiếu hạng/lô/ký nhận với tính toán tay, xác nhận tab được đóng cửa (hoặc ghi rõ vì sao chưa đóng — vd có chi nhánh không ký).
- Báo cáo ca đầu tiên về chat COO (kèm snapshot thứ tự đăng ký của ngày).
- Nếu ca đầu tiên lỗi: dừng cơ chế, quay lại luật cũ (3 READY đầu Sheet) cho ca hôm sau, sửa rồi thử lại — không để lỗi kéo sang ngày thứ hai.

### GĐ 5 — Ghi chép + push (sau khi ca đầu tiên chạy đạt)
- Ghi improvement-log + nhật ký ngày.
- Push repo (skill COO/Production, spec, lịch): **chờ CEO duyệt riêng** theo luật đẩy.

---

## 10. Rủi ro còn lại (sau khi áp dụng đầy đủ mục 7)

1. **Snapshot L lệch nhau (mục 7.5):** cửa sổ vài giây, chốt chặn claim-then-verify đã có. Rủi ro dư thấp.
2. **Cron dispatch sớm:** đã xử lý bằng bước chờ đến 06:05 (mục 3). Nếu runtime đổi quy ước dispatch, cần xem lại.
3. **Một chi nhánh không bao giờ đăng ký** (COO lỗi kéo dài): chi nhánh đó đơn giản là không có lô — đúng thiết kế (opt-in mỗi ngày), nhưng CEO/COO cần phát hiện qua việc tab thiếu email đó nhiều ngày (báo cáo ca pipeline ghi "không có dòng đăng ký của chi nhánh X" — có thể thêm vào báo cáo ca nếu CEO muốn).
4. **Tab bị chi nhánh khác ghi sai** (vd ghi đè dòng người khác): luật "chỉ ghi dòng của email mình" đã có ở các tab khác; vi phạm thì thấy rõ trong tab (dòng sai email + giờ). Không có khóa kỹ thuật — dựa vào kỷ luật chung của mô hình repo.
5. **D8 chưa quyết:** ngày đầu tiên chạy mà L rỗng thì mọi chi nhánh ký "HẾT" — không phải lỗi cơ chế, mà là chưa có chủ đề để chia. Cần nói rõ với CEO trước ngày chạy đầu tiên để khỏi tưởng cơ chế hỏng.

## 11. Việc không làm trong đợt này

- Không đổi cỡ lô (giữ 3), không xoay vòng công bằng (mục 7.10).
- Không thêm cột thứ 5 (ghi chú) — nếu sau này cần, thêm riêng.
- Không đổi luật claim-then-verify, bước 7 trùng CLAIMED, cửa chặn 95%, hay cổng READY.
- Không sửa D1/D2, L1 theo hướng khác (cơ chế này THAY THẾ cách xử lý L1 bằng đăng ký có thứ tự; L1-A/L1-B trong báo cáo rà soát không cần thực hiện nữa nếu cơ chế này được duyệt).
- Không push GitHub trong đợt triển khai local.

---

## 12. Quyết định cần CEO chốt (để triển khai)

1. **D8 (A hay B)** — tiên quyết, vì danh sách L phụ thuộc vào nó.
2. **Duyệt kế hoạch này** (GĐ 0–5) hay sửa gì trước khi làm.
3. Tên tab: `SHIFT_CHECKIN` (đề xuất) hay tên khác.
4. Đăng ký là bước trong `coo-scan-0600` (đề xuất) hay lịch riêng.
5. Đóng cửa bằng values.clear (đề xuất) hay deleteDimension.
6. Xác nhận: cỡ lô 3, hạn chót ký nhận 06:30, đăng ký trễ sau 06:05 không được tính.

---

## Bổ sung 13/11 — Quy tắc nhân bản ca sản xuất (lệnh CEO 13/11/2026, DEC-258)

Khi thêm ca sản xuất mới trong ngày, LUÔN tạo đủ 2 lịch theo cặp, lệch nhau đúng 5 phút: (1) lịch đăng ký ca cho COO lúc T, (2) lịch nhận ca cho Sản xuất lúc T+5. Không tạo chỉ 1 trong 2, không để 2 lịch cùng giờ. Ca hiện tại: coo-scan-0600 (06:00, chứa bước đăng ký 0b) + prod-pipeline-0600 (06:05).

Checklist bắt buộc khi nhân bản (để tránh bỏ sót):
1. Lịch COO của ca phụ CHỈ chứa bước đăng ký (điểm danh COO_CHECKIN + đăng ký SHIFT_CHECKIN) — KHÔNG quét lại COO_TASKS (COO_TASKS chỉ đọc 1 lần/ngày lúc 06:00; quét lại có thể giao trùng việc đã giao).
2. Đổi luật khớp ca trong skill Production + body pipeline + spec SHIFT_CHECKIN: hạng/lô/ký nhận/đóng cửa tính theo dòng đăng ký CỦA CA ĐÓ (dòng đăng ký gần nhất trước giờ nhận ca, cột D còn trống) — KHÔNG lấy dòng đầu tiên của ngày (luật hiện tại chỉ đúng khi 1 ca/ngày).
3. Đóng cửa chỉ clear các dòng đăng ký của ca đó, không clear dòng của ca khác trong cùng ngày.
4. Ghi DEC + cập nhật bảng lịch trong scheduled-tasks-setup.md.

Quy tắc này đã ghi vào: skill COO (mục Bước 0b), skill Production (mục Nhận ca), google-sheet-spec.md (mục SHIFT_CHECKIN), scheduled-tasks-setup.md (mục Quy tắc cài đặt), DEC-258, MEMORY.md.

---

## Bổ sung 13/11 — Gộp đăng ký + nhận ca chung 1 lịch (lệnh CEO 13/11/2026, DEC-259 — thay DEC-258)

CEO chọn gộp chung 1 lịch thay vì 2 lịch theo cặp. Thực hiện 13/11:
- Xóa lịch coo-register-0600 (vừa tạo cùng ngày, chưa chạy lần nào).
- Pipeline prod-pipeline-0600 dời 06:05 → 06:00, thêm Bước 0 đăng ký ca (chờ đúng 06:00 wall-clock rồi đăng ký; kiểm tra hạn mức, dọn dòng ngày cũ, chống trùng, append A–C, D trống); Bước 4 nhận ca vẫn chờ đúng 06:05 wall-clock. Lệch 5 phút giữ nguyên dưới dạng chờ bên trong lịch — không được bỏ (nhận ca ngay sau đăng ký thì hạng tính trên dữ liệu thiếu dòng đăng ký của các chi nhánh khác).
- coo-scan-0600 chỉ còn điểm danh + quét COO_TASKS (Bước 0b đã gỡ); không tham gia đăng ký ca ở bất kỳ ca nào.
- Không phân biệt ca chính/ca phụ — mọi ca dùng cùng một mẫu: mỗi ca mới = 1 lịch prod-pipeline-HHMM chạy lúc T (Bước 0 đăng ký ca lúc T, Bước 4 nhận ca lúc T+5).
- Tên/giờ lịch đã sửa cho khớp: prod-pipeline-0600 chạy 06:00 (tiêu đề "Sản xuất video lúc 06:00 hàng ngày"); bảng lịch trong scheduled-tasks-setup.md, skill COO/Production, spec SHIFT_CHECKIN đều ghi đúng tên + giờ này.
- Checklist khi nhân bản (không đổi): hạng/lô/ký nhận/đóng cửa tính theo dòng đăng ký CỦA CA ĐÓ; đóng cửa chỉ clear dòng của ca đó; ghi DEC.

Mục "Quy tắc nhân bản ca" (DEC-258) ở trên đã hết hiệu lực, giữ lại làm hồ sơ lịch sử.

---

## Bổ sung 13/11 — Dời ca sáng 06:00 → 05:00 + thêm ca chiều 14:00 (lệnh CEO 13/11/2026, DEC-260/DEC-261)

- Ca sáng dời 06:00 → 05:00: xóa prod-pipeline-0600, tạo prod-pipeline-0500 chạy 05:00 (Bước 0 đăng ký ca 05:00, Bước 4 nhận ca 05:05). Cổng hạn mức chuyển sang kiểm tra trực tiếp (DEC-263): ca 05:00 đọc % tuần trực tiếp bằng lệnh subscription-status lúc bắt đầu ca, không đọc Sheet nữa (Sheet chỉ làm dự phòng khi lệnh lỗi).
- Thêm ca chiều prod-pipeline-1400 chạy 14:00 (Bước 0 đăng ký ca 14:00, Bước 4 nhận ca 14:05). Chi nhánh này giờ chạy 2 ca/ngày (05:00 + 14:00), tối đa 6 chủ đề/ngày; các chi nhánh khác vẫn 1 ca 06:00 trừ khi CEO mở rộng.
- Khớp ca theo cửa sổ REG_TIME (quy tắc mới cho 2 ca/ngày): ca sáng tính dòng REG_TIME < 12:00, ca chiều chỉ tính dòng REG_TIME ≥ 12:00 — áp dụng cho kiểm tra trùng đăng ký (Bước 0d), hạng (Bước 4b) và đóng cửa (Bước 4f). Ca chiều dọn luôn dòng tồn đọng của ca sáng (REG_TIME < 12:00) khi đăng ký; không clear dòng trong cửa sổ ca mình. Cứu lô cũ qua đêm (Bước 2h) chỉ ca sáng làm, 1 lần/ngày; ca chiều bỏ qua.
- Tên/giờ lịch đã sửa cho khớp: 5 lịch (scout 06:00, coo-scan 03:00, pipeline 05:00 + 14:00, học hỏi 20:00); bảng lịch trong scheduled-tasks-setup.md, skill COO/Production, spec SHIFT_CHECKIN đều ghi đúng tên + giờ.
- Cổng hạn mức chuyển sang kiểm tra trực tiếp (CEO 13/11, DEC-263): Scout/Pipeline/ca quét đọc % tuần trực tiếp bằng lệnh subscription-status lúc bắt đầu ca (≥95% thì dừng/claim 0); TASKS.L giữ làm bản ghi để CEO kiểm tra; dòng điểm danh COO_CHECKIN hàng ngày vẫn ghi (số trực tiếp) làm bản ghi, cổng không đọc nó nữa; nếu lệnh lỗi thì dùng số Sheet mới nhất làm dự phòng. Skill Scout/COO + spec + 4 body lịch đã sửa theo.
- Checklist khi nhân bản (không đổi, bổ sung cửa sổ ca): hạng/lô/ký nhận/đóng cửa tính theo dòng đăng ký CỦA CA ĐÓ (khớp theo cửa sổ REG_TIME); đóng cửa chỉ clear dòng của ca đó; ghi DEC.
