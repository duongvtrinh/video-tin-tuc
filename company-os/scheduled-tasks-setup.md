# Cài bộ lịch mẫu (scheduled tasks) cho tài khoản Muse mới

Bộ lịch mẫu của công ty: 6 lịch chạy thật (xem bảng dưới). Scout chạy 2 ca/ngày: 04:00 và 13:00; COO chạy ca 03:00 hàng ngày (dời từ 06:00 theo quyết CEO 13/11/2026, DEC-262); Sản xuất (pipeline) chạy 2 ca/ngày: 05:00 và 14:00 (mỗi ca đăng ký ở Bước 0 rồi nhận ca ở Bước 4, lệch 5 phút — gộp chung 1 lịch/ca theo quyết CEO 13/11/2026, DEC-259/DEC-260/DEC-261). File này + thư mục
`company-os/crons/daily/` là **bản mẫu dùng chung**, nằm trong repo để mọi chi nhánh
(tài khoản Muse) đều cài được cùng một chuẩn. Cấu hình lịch đang chạy là của từng
tài khoản, không tự sinh ra khi clone repo.

## Quy tắc cài đặt

- **Mặc định KHÔNG tạo lịch nào** khi clone repo xong (BOOTSTRAP §1.7 — chỉ tạo
  khi CEO duyệt riêng).
- CEO nói **"cài bộ lịch mẫu"** (một lần duyệt cho cả bộ, hoặc duyệt riêng từng
  lịch) thì agent của tài khoản mới tạo 6 lịch bằng `cron.add` theo đúng các
  file mẫu dưới đây. Không tự cài khi chưa có lệnh CEO.
- Sau khi cài, CEO đổi giờ chạy / tên lịch / nội dung qua chat chính, agent sửa
  bằng `cron.update` (ghi lại toàn bộ body đã sửa). **Sửa file `.md` trong
  `company-os/crons/` hay trong thư mục crons của tài khoản KHÔNG đổi được lịch
  đang chạy** — các file đó chỉ là bản sao/bản mẫu.
- **Quy tắc nhân bản ca sản xuất (lệnh CEO 13/11/2026, DEC-259 — thay DEC-258):** khi thêm ca sản xuất mới trong ngày, mỗi ca chỉ cần 1 lịch: prod-pipeline-HHMM chạy lúc T (Bước 0 đăng ký ca lúc T, Bước 4 nhận ca lúc T+5; lệch 5 phút giữ nguyên dưới dạng chờ bên trong lịch). **Không phân biệt ca chính/ca phụ — mọi ca dùng cùng một mẫu.** Ca hiện tại: 2 ca/ngày — prod-pipeline-0500 chạy 05:00 (Bước 0 đăng ký ca 05:00, Bước 4 nhận ca 05:05) + prod-pipeline-1400 chạy 14:00 (Bước 0 đăng ký ca 14:00, Bước 4 nhận ca 14:05). coo-scan (điểm danh + quét COO_TASKS) không tham gia đăng ký ca ở bất kỳ ca nào. Khi nhân bản, phải cập nhật luật khớp ca trong skill Production + body pipeline + spec SHIFT_CHECKIN (hạng/lô/ký nhận/đóng cửa tính theo dòng đăng ký CỦA CA ĐÓ — dòng đăng ký gần nhất trước giờ nhận ca, cột D còn trống; với 2 ca/ngày, khớp theo cửa sổ ca — REG_TIME < 12:00 cho ca sáng, ≥ 12:00 cho ca chiều; đóng cửa chỉ clear các dòng của ca đó) và ghi DEC.

## Bảng 6 lịch mẫu

| ID | Giờ chạy (+07) | Việc chính |
| --- | --- | --- |
| scout-scan-0600 | 04:00 hàng ngày | Scout quét chủ đề + chấm điểm ngay trong cùng lượt quét (ca sáng) |
| scout-scan-1300 | 13:00 hàng ngày | Scout quét chủ đề + chấm điểm ngay trong cùng lượt quét (ca chiều, nhân bản từ ca 04:00 theo lệnh CEO 13/11/2026) |
| prod-pipeline-0500 | 05:00 hàng ngày | Pipeline ca đầu ngày: đăng ký ca 05:00 (Bước 0) rồi nhận ca 05:05 (Bước 4), nhận lô tối đa 3 chủ đề READY theo thứ tự đăng ký ca (tab SHIFT_CHECKIN), sản xuất tuần tự Production → QA → Drive |
| prod-pipeline-1400 | 14:00 hàng ngày | Pipeline ca chiều: đăng ký ca 14:00 (Bước 0) rồi nhận ca 14:05 (Bước 4), nhận lô tối đa 3 chủ đề READY theo thứ tự đăng ký ca trong cửa sổ chiều (REG_TIME ≥ 12:00), sản xuất tuần tự Production → QA → Drive |
| bot-hoc-hoi-2000 | 20:00 hàng ngày | Học-hỏi: rút bài học từ lỗi lặp lại có bằng chứng, cải tiến template/skill/SOP (đổi chuẩn thì chỉ đề xuất để CEO quyết) |
| coo-scan-0300 | 03:00 hàng ngày | COO điểm danh tại tab COO_CHECKIN (Bước 0), rồi quét tab COO_TASKS, nhận dòng của chi nhánh mình, giao phòng, xác nhận E–G; không có dòng thì im lặng, không thông báo |

## Cách tạo từng lịch (agent làm)

Với mỗi file mẫu trong `company-os/crons/daily/<id>.md`:

1. Đọc frontmatter của file mẫu để lấy `id`, `title`, `schedule` (kind/timezone/
   time) và `timeout_secs` (nếu có).
2. Lấy phần body của file mẫu (sau dòng `---` thứ hai) làm body cho `cron.add`.
3. Gọi `cron.add` với: `enabled: true`, `mode: task`,
   `owner: goal:vieneu-media-company-bootstrap` (goal bootstrap của chính tài
   khoản này), `delivery` = chat COO của tài khoản mới (lấy ID qua `chat.list`, KHÔNG copy UUID 2e9f544b-1dad-420a-a1b4-ed9463cc89d9 của chi nhánh này).
4. Kiểm tra trước khi tạo xong: body đã thay hết các `{{...}}` chưa (grep `{{`
   phải = 0), còn UUID hay email lạ nào của chi nhánh khác không (grep UUID và
   `@vuachim` trong body phải = 0 — email khai báo của chính tài khoản này cũng
   không hardcode trong body, agent đọc từ MEMORY.md). Copy nguyên văn file mẫu
   mà chưa thay placeholder thì lịch sẽ gọi nhầm phòng của chi nhánh khác (hoặc
   gọi lỗi) — không được tạo khi còn placeholder.
5. Kiểm tra lại bằng `cron.view` (đọc lại body) và `cron.list` (đủ 6 lịch, đều
   enabled).

## Những chỗ phải thay trước khi tạo (theo tài khoản mới)

Không bao giờ copy nguyên văn file mẫu — mọi giá trị động phải khớp với công
ty mới. File mẫu cố tình để placeholder `{{...}}` ở những chỗ dưới đây để copy
nguyên văn không chạy được: lịch tạo ra từ body còn placeholder sẽ gọi nhầm
phòng của chi nhánh khác (hoặc gọi lỗi).

| Trong file mẫu | Thay bằng gì ở tài khoản mới |
| --- | --- |
| Trong file mẫu là `{{CHAT_ID_SCOUT_BAO}}` và `{{CHAT_ID_SCOUT_GROUP}}` (file scout-scan-0600 / scout-scan-1300) | ID chat Scout - Báo / Scout - Group của tài khoản mới (xem bằng `chat.list`) |
| Trong file mẫu là `{{CHAT_ID_SAN_XUAT}}`, `{{CHAT_ID_QA}}` và `{{CHAT_ID_COO}}` (file prod-pipeline-0500 / prod-pipeline-1400) | ID chat Sản xuất / Kỹ thuật QA / COO của tài khoản mới (xem bằng `chat.list`) |
| Trong file mẫu là `{{EMAIL_KHAI_BAO}}` (file coo-scan-0300, 2 chỗ — ví dụ REPORT_ID `RPT-YYYYMMDD-{{EMAIL_KHAI_BAO}}-NN`) | Email khai báo của tài khoản mới (xem MEMORY.md của tài khoản đó) |
| Trong file mẫu là `{{MA_CHI_NHANH}}` (file bot-hoc-hoi-2000, 1 chỗ — ví dụ ID mục `IMP-...-{{MA_CHI_NHANH}}-...`) | Mã chi nhánh = phần trước @ của email khai báo của tài khoản mới |
| `owner: goal:vieneu-media-company-bootstrap` | Goal bootstrap của chính tài khoản mới (cùng slug nếu tài khoản đó theo đúng chuẩn này) |
| `delivery` (chat COO) | Chat COO của tài khoản mới (lấy ID qua `chat.list`, KHÔNG copy UUID 2e9f544b-1dad-420a-a1b4-ed9463cc89d9 của chi nhánh này) |

**Không phải thay:** ID workbook "Video HQ — Tin Tức"
(`1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`) và thư mục Drive
"Video Muse" dùng chung cho mọi chi nhánh, giữ nguyên trong body. Email khai
báo của chi nhánh KHÔNG hardcode trong body nào (quyết CEO 07/11/2026, R4-17
phương án A) — agent đọc email khai báo trong MEMORY.md của chính tài khoản
mình; cấm đoán, cấm dùng email Drive/GitHub/Facebook thay thế.

## Bảo trì bản mẫu (để khỏi lệch)

- **Body trong file mẫu phải giống hệt body của lịch đang chạy, trừ 7 placeholder
  (5 ID chat phòng + email khai báo + mã chi nhánh)** (xem bảng trên): khi diff, chỉ các dòng chứa placeholder ở mỗi
  file được phép khác; mọi dòng khác phải giống hệt.
  Frontmatter thì khác — bản mẫu bỏ `delivery` và `metadata` vốn là của riêng
  từng tài khoản, và đổi `owner` thành `goal:vieneu-media-company-bootstrap`.
- Mỗi khi sửa body một lịch đang chạy bằng `cron.update` (vd các đợt L7/L10/L13
  ngày 08/11/2026), **cập nhật luôn file mẫu tương ứng trong repo trong cùng lần
  sửa**. Ngược lại, sửa file mẫu mà không sửa lịch đang chạy thì lịch vẫn chạy
  theo body cũ.
- Lịch nào đổi giờ chạy thì sửa cả `time` trong frontmatter file mẫu lẫn lịch
  đang chạy (qua `cron.update`).

## Ghi chú

- File mẫu trong repo chỉ là chuẩn chung; mỗi tài khoản tự chịu trách nhiệm về
  lịch của mình (bật/tắt/sửa giờ) và chỉ cài khi CEO của tài khoản đó duyệt.
- Đẩy file mẫu lên GitHub theo lệ chung: gửi phân tích cho CEO đọc trước, chỉ
  push sau khi CEO duyệt riêng.
