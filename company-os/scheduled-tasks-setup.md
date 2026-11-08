# Cài bộ lịch mẫu (scheduled tasks) cho tài khoản Muse mới

Bộ lịch mẫu của công ty: 10 lịch chạy thật (xem bảng dưới). File này + thư mục
`company-os/crons/daily/` là **bản mẫu dùng chung**, nằm trong repo để mọi chi nhánh
(tài khoản Muse) đều cài được cùng một chuẩn. Cấu hình lịch đang chạy là của từng
tài khoản, không tự sinh ra khi clone repo.

## Quy tắc cài đặt

- **Mặc định KHÔNG tạo lịch nào** khi clone repo xong (BOOTSTRAP §1.7 — chỉ tạo
  khi CEO duyệt riêng).
- CEO nói **"cài bộ lịch mẫu"** (một lần duyệt cho cả bộ, hoặc duyệt riêng từng
  lịch) thì agent của tài khoản mới tạo 10 lịch bằng `cron.add` theo đúng các
  file mẫu dưới đây. Không tự cài khi chưa có lệnh CEO.
- Sau khi cài, CEO đổi giờ chạy / tên lịch / nội dung qua chat chính, agent sửa
  bằng `cron.update` (ghi lại toàn bộ body đã sửa). **Sửa file `.md` trong
  `company-os/crons/` hay trong thư mục crons của tài khoản KHÔNG đổi được lịch
  đang chạy** — các file đó chỉ là bản sao/bản mẫu.

## Bảng 10 lịch mẫu

| ID | Giờ chạy (+07) | Việc chính |
| --- | --- | --- |
| scout-scan-0600 | 06:00 hàng ngày | Scout quét chủ đề + chấm điểm ngay trong cùng lượt quét |
| scout-scan-1000 | 10:00 hàng ngày | Scout quét chủ đề + chấm điểm |
| scout-scan-1400 | 14:00 hàng ngày | Scout quét chủ đề + chấm điểm |
| scout-scan-1800 | 18:00 hàng ngày | Scout quét chủ đề + chấm điểm |
| prod-pipeline-0600 | 06:00 hàng ngày | Pipeline nhận lô tối đa 3 chủ đề READY (tối đa 12 claim/ngày), sản xuất tuần tự Production → QA → Drive |
| prod-pipeline-1000 | 10:00 hàng ngày | Pipeline nhận lô tối đa 3 chủ đề READY, sản xuất tuần tự |
| prod-pipeline-1400 | 14:00 hàng ngày | Pipeline nhận lô tối đa 3 chủ đề READY, sản xuất tuần tự |
| prod-pipeline-1800 | 18:00 hàng ngày | Pipeline nhận lô tối đa 3 chủ đề READY, sản xuất tuần tự |
| bot-hoc-hoi-2000 | 20:00 hàng ngày | Học-hỏi: rút bài học từ lỗi lặp lại có bằng chứng, cải tiến template/skill/SOP (đổi chuẩn thì chỉ đề xuất để CEO quyết) |
| coo-scan-0600 | 06:00 hàng ngày | COO quét tab COO_TASKS, nhận dòng của chi nhánh mình, giao phòng, xác nhận E–G; không có dòng thì im lặng, không thông báo |

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
5. Kiểm tra lại bằng `cron.view` (đọc lại body) và `cron.list` (đủ 10 lịch, đều
   enabled).

## Những chỗ phải thay trước khi tạo (theo tài khoản mới)

Không bao giờ copy nguyên văn file mẫu — mọi giá trị động phải khớp với công
ty mới. File mẫu cố tình để placeholder `{{...}}` ở những chỗ dưới đây để copy
nguyên văn không chạy được: lịch tạo ra từ body còn placeholder sẽ gọi nhầm
phòng của chi nhánh khác (hoặc gọi lỗi).

| Trong file mẫu | Thay bằng gì ở tài khoản mới |
| --- | --- |
| Trong file mẫu là `{{CHAT_ID_SCOUT_BAO}}` và `{{CHAT_ID_SCOUT_GROUP}}` (4 file scout-scan-*) | ID chat Scout - Báo / Scout - Group của tài khoản mới (xem bằng `chat.list`) |
| Trong file mẫu là `{{CHAT_ID_SAN_XUAT}}` và `{{CHAT_ID_QA}}` (4 file prod-pipeline-*) | ID chat Sản xuất / Kỹ thuật QA của tài khoản mới (xem bằng `chat.list`) |
| `owner: goal:vieneu-media-company-bootstrap` | Goal bootstrap của chính tài khoản mới (cùng slug nếu tài khoản đó theo đúng chuẩn này) |
| `delivery` (chat COO) | Chat COO của tài khoản mới (lấy ID qua `chat.list`, KHÔNG copy UUID 2e9f544b-1dad-420a-a1b4-ed9463cc89d9 của chi nhánh này) |

**Không phải thay:** ID workbook "Video HQ — Trụ sở Muse"
(`1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`) và thư mục Drive
"Video Muse" dùng chung cho mọi chi nhánh, giữ nguyên trong body. Email khai
báo của chi nhánh KHÔNG hardcode trong body nào (quyết CEO 07/11/2026, R4-17
phương án A) — agent đọc email khai báo trong MEMORY.md của chính tài khoản
mình; cấm đoán, cấm dùng email Drive/GitHub/Facebook thay thế.

## Bảo trì bản mẫu (để khỏi lệch)

- **Body trong file mẫu phải giống hệt body của lịch đang chạy, trừ 4 placeholder
  ID chat phòng** (xem bảng trên): khi diff, chỉ các dòng chứa placeholder ở mỗi
  file scout-scan-*/prod-pipeline-* được phép khác; mọi dòng khác phải giống hệt.
  Frontmatter thì khác — bản mẫu bỏ `delivery` và `metadata` vốn là của riêng
  từng tài khoản.
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
