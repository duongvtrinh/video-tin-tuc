# Cài bộ lịch mẫu (scheduled tasks) cho tài khoản Muse mới

Bộ lịch mẫu của công ty: 7 lịch chạy thật (xem bảng dưới). Scout chạy 2 ca/ngày: 04:00 và 13:00; COO chạy ca 03:00 hàng ngày (dời từ 06:00 theo quyết CEO 13/11/2026, DEC-262); Sản xuất (pipeline) chạy 2 ca/ngày: 05:00 và 14:00 (mỗi ca đăng ký ở Bước 0 rồi nhận ca ở Bước 4, lệch 5 phút — gộp chung 1 lịch/ca theo quyết CEO 13/11/2026, DEC-259/DEC-260/DEC-261); **giám sát TTS (tts-watchdog) chạy mỗi 30 phút (thêm 13/11/2026 — kiểm tra /health, tự cài lại unit + restart khi lỗi, chỉ báo chat chính khi đã restart hoặc vẫn không lên)**. File này + thư mục
`company-os/crons/daily/` là **bản mẫu dùng chung**, nằm trong repo để mọi chi nhánh
(tài khoản Muse) đều cài được cùng một chuẩn. Cấu hình lịch đang chạy là của từng
tài khoản, không tự sinh ra khi clone repo. Lưu ý: 7 file mẫu trong
`company-os/crons/daily/` (6 file ca ngày + `tts-watchdog.md`) nằm trên repo; ở
local chỉ có `tts-watchdog.md`, 6 file còn lại chỉ tồn tại trên repo. File mẫu đã
đồng bộ với lịch live ngày 14/11/2026 (diff body = 0 trừ frontmatter, xem
`company-os/crons/daily/`). Bản live (body lịch đang chạy) nằm ở
`goals/one-person-media-company/crons/daily/`
của từng tài khoản (riêng tts-watchdog nằm ở `crons/minutely/` vì là lịch interval);
đối chiếu mẫu với lịch đang chạy thì lấy mẫu từ repo, đối chiếu với bản live đó.

## Quy tắc cài đặt

- **Mặc định KHÔNG tạo lịch nào** khi clone repo xong (BOOTSTRAP Phần E4 + quy tắc 4 — chỉ tạo
  khi CEO duyệt riêng).
- CEO nói **"cài bộ lịch mẫu"** (một lần duyệt cho cả bộ, hoặc duyệt riêng từng
  lịch) thì agent của tài khoản mới tạo 7 lịch bằng `cron.add` theo đúng các
  file mẫu dưới đây. Không tự cài khi chưa có lệnh CEO.
- Sau khi cài, CEO đổi giờ chạy / tên lịch / nội dung qua chat chính, agent sửa
  bằng `cron.update` (ghi lại toàn bộ body đã sửa). **Sửa file `.md` trong
  `company-os/crons/` hay trong thư mục crons của tài khoản KHÔNG đổi được lịch
  đang chạy** — các file đó chỉ là bản sao/bản mẫu.
- **Quy tắc nhân bản ca sản xuất (lệnh CEO 13/11/2026, DEC-259 — thay DEC-258):** khi thêm ca sản xuất mới trong ngày, mỗi ca chỉ cần 1 lịch: prod-pipeline-HHMM chạy lúc T (Bước 0 đăng ký ca lúc T, Bước 4 nhận ca lúc T+5; lệch 5 phút giữ nguyên dưới dạng chờ bên trong lịch). **Không phân biệt ca chính/ca phụ — mọi ca dùng cùng một mẫu.** Ca hiện tại: 2 ca/ngày — prod-pipeline-0500 chạy 05:00 (Bước 0 đăng ký ca 05:00, Bước 4 nhận ca 05:05) + prod-pipeline-1400 chạy 14:00 (Bước 0 đăng ký ca 14:00, Bước 4 nhận ca 14:05). coo-scan (điểm danh + quét COO_TASKS) không tham gia đăng ký ca ở bất kỳ ca nào. Khi nhân bản, phải cập nhật luật khớp ca trong skill Production + body pipeline + spec SHIFT_CHECKIN (hạng/lô/ký nhận/đóng cửa tính theo dòng đăng ký CỦA CA ĐÓ — dòng đăng ký gần nhất trước giờ nhận ca, cột D còn trống; với 2 ca/ngày, khớp theo cửa sổ ca — REG_TIME < 12:00 cho ca sáng, ≥ 12:00 cho ca chiều; đóng cửa chỉ clear các dòng của ca đó) và ghi DEC.

## Bảng 7 lịch mẫu

| ID | Giờ chạy (+07) | Việc chính |
| --- | --- | --- |
| scout-scan-0600 | 04:00 hàng ngày | Scout quét chủ đề + chấm điểm ngay trong cùng lượt quét (ca sáng) |
| scout-scan-1300 | 13:00 hàng ngày | Scout quét chủ đề + chấm điểm ngay trong cùng lượt quét (ca chiều, nhân bản từ ca 04:00 theo lệnh CEO 13/11/2026) |
| prod-pipeline-0500 | 05:00 hàng ngày | Pipeline ca đầu ngày: đăng ký ca 05:00 (Bước 0) rồi nhận ca 05:05 (Bước 4), nhận lô tối đa 3 chủ đề READY theo thứ tự đăng ký ca (tab SHIFT_CHECKIN), sản xuất tuần tự Production → QA → Drive |
| prod-pipeline-1400 | 14:00 hàng ngày | Pipeline ca chiều: đăng ký ca 14:00 (Bước 0) rồi nhận ca 14:05 (Bước 4), nhận lô tối đa 3 chủ đề READY theo thứ tự đăng ký ca trong cửa sổ chiều (REG_TIME ≥ 12:00), sản xuất tuần tự Production → QA → Drive |
| bot-hoc-hoi-2000 | 20:00 hàng ngày | Học-hỏi: rút bài học từ lỗi lặp lại có bằng chứng, cải tiến template/skill/SOP (đổi chuẩn thì chỉ đề xuất để CEO quyết) |
| coo-scan-0300 | 03:00 hàng ngày | COO điểm danh tại tab COO_CHECKIN (Bước 0), rồi quét tab COO_TASKS, nhận dòng của chi nhánh mình, giao phòng, xác nhận E–G; không có dòng thì im lặng, không thông báo |
| tts-watchdog | mỗi 30 phút | Giám sát server TTS: kiểm tra /health (cổng 8000); lỗi thì cài lại unit systemd từ bản chuẩn + restart tối đa 2 lần (lần 2 dọn tiến trình chiếm cổng 8000); khỏe thì im lặng, chỉ báo chat chính khi đã phải restart hoặc vẫn không lên |

## Cài dịch vụ TTS để tự chạy lại khi Muse khởi động lại

Mục đích: server TTS phải luôn sẵn sàng trước mỗi ca sản xuất (pipeline kiểm tra
/health đầu ca, TTS chưa sẵn sàng thì ca đó không nhận lô — bot-sop). Cài TTS thành
dịch vụ systemd thì máy khởi động lại, tiến trình TTS cũ tự chạy tiếp: vừa tự khởi
động khi boot, vừa tự restart khi tiến trình chết — giống máy hiện tại.

**Điều kiện trước:** TTS đã cài theo BOOTSTRAP C2 (venv + model đã tải về cache
`~/.cache/huggingface` trong lần chạy đầu; các lần sau nạp từ cache, không cần mạng).

**Cài một lần cho mỗi tài khoản/máy mới** (file unit bản chuẩn nằm trong repo tại
`company-os/systemd/vieneu-tts.service`):

```bash
cp ~/workspace/company-os/systemd/vieneu-tts.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now vieneu-tts
```

Đường dẫn `~/workspace/company-os/` trong 3 lệnh trên hoạt động nhờ 3 symlink
đã tạo ở BOOTSTRAP C1 (nối layout clone `video-tin-tuc/` với đường dẫn vận hành).
Nếu symlink chưa có, tạo trước rồi mới chạy 3 lệnh này.

**Kiểm chứng ngay sau khi cài:**

```bash
systemctl is-enabled vieneu-tts   # phải ra: enabled
systemctl is-active vieneu-tts    # phải ra: active
curl -s http://127.0.0.1:8000/health   # phải có "status":"ok"
```

**Vì sao tự chạy lại được:**

- Unit chạy bằng **system manager** (không phải user): máy khách boot target tối thiểu
  `default.target`, không có user bus. `WantedBy=default.target` nên service tự khởi
  động khi boot; `Restart=always` + `RestartSec=10` nên tiến trình chết (kể cả
  `kill -9` MainPID) thì systemd restart lại — đã kiểm chứng trên máy hiện tại
  13/11/2026: kill -9 MainPID → tự khởi động lại, /health OK.
- Biến môi trường trong unit: `HOME=/home/hatch` (service chạy dưới HOME=/root nên phải
  ghi rõ), `HF_HOME=/home/hatch/.cache/huggingface`, `HF_HUB_OFFLINE=1` (nạp model từ
  cache, ~2,5 giây), `VIENEU_MODE=v3nano`; log service ghi vào
  `~/workspace/company-os/tts-service.log`. **Mật khẩu proxy KHÔNG được ghi vào unit.**
- **Sau khi thay máy, /etc bị xóa nên unit mất** (sự kiện thật 13/11/2026 18:41: unit
  mất khỏi /etc sau thay máy) — lịch `tts-watchdog` (mỗi 30 phút, trong bộ lịch chuẩn
  ở trên) tự cài lại unit từ bản chuẩn trong repo + restart khi /health lỗi, tối đa 2
  lần thử, nên không cần người can thiệp. Khôi phục thủ công khi cần thì chạy lại 3
  lệnh cài ở trên.
- **File unit trong repo cũng là bản chuẩn dùng chung:** khi sửa unit đang chạy (vd đổi
  biến môi trường, cổng), cập nhật luôn bản trong repo trong cùng lần sửa — watchdog
  cài lại unit từ bản này mỗi khi /etc mất, nên bản repo lỗi thời sẽ cài lại unit cũ.
- Phạm vi: mục này chỉ lo **tiến trình server TTS**. Builder (tiến trình dựng video)
  KHÔNG tự sống lại sau khi khởi động lại — builder dở dang thì resume bằng checkpoint
  trong TASKS.K + builder mới, pipeline kiểm tra BUILDING/REVIEW cũ đầu ca (DEC-105/106).

## Cách tạo từng lịch (agent làm)

Với mỗi file mẫu trong `company-os/crons/daily/<id>.md`:

0. Tạo goal bootstrap của tài khoản này trước (chỉ làm 1 lần): goal slug `vieneu-media-company-bootstrap`, tên "VieNeu Media Company Bootstrap" — goal này làm `owner` cho cả 7 lịch. Chưa có goal thì chưa tạo lịch.
1. Đọc frontmatter của file mẫu để lấy `id`, `title`, `schedule` (kind/timezone/
   time — hoặc `every` với lịch interval như tts-watchdog) và `timeout_secs` (nếu có).
2. Lấy phần body của file mẫu (sau dòng `---` thứ hai) làm body cho `cron.add`.
3. Gọi `cron.add` với: `enabled: true`, `mode: task`,
   `owner: goal:vieneu-media-company-bootstrap` (goal bootstrap của chính tài
   khoản này), `delivery` = chat COO của tài khoản mới (lấy ID qua `chat.list`, KHÔNG copy UUID {{CHAT_ID_COO}} của chi nhánh này) — **trừ tts-watchdog: `delivery` = chat chính của tài khoản mới** (lịch này báo CEO trực tiếp khi TTS sập, không qua COO).
4. Kiểm tra trước khi tạo xong: body đã thay hết các `{{...}}` chưa (grep `{{`
   phải = 0), còn UUID hay email lạ nào của chi nhánh khác không (grep UUID và
   `@vuachim` trong body phải = 0 — email khai báo của chính tài khoản này cũng
   không hardcode trong body, agent đọc từ MEMORY.md). Copy nguyên văn file mẫu
   mà chưa thay placeholder thì lịch sẽ gọi nhầm phòng của chi nhánh khác (hoặc
   gọi lỗi) — không được tạo khi còn placeholder.
5. Kiểm tra lại bằng `cron.view` (đọc lại body) và `cron.list` (đủ 7 lịch, đều
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
| `delivery` (chat COO) | Chat COO của tài khoản mới (lấy ID qua `chat.list`, KHÔNG copy UUID {{CHAT_ID_COO}} của chi nhánh này) |
| `delivery` của tts-watchdog (không nằm trong file mẫu — file mẫu bỏ delivery theo lệ chung) | ID chat chính của tài khoản mới (xem bằng `chat.list`); 6 lịch còn lại dùng chat COO |

**Không phải thay:** ID workbook "Video HQ — Tin Tức"
(`1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`) và thư mục Drive
"Video Muse" dùng chung cho mọi chi nhánh, giữ nguyên trong body. Email khai
báo của chi nhánh KHÔNG hardcode trong body nào (quyết CEO 07/11/2026, R4-17
phương án A) — agent đọc email khai báo trong MEMORY.md của chính tài khoản
mình; cấm đoán, cấm dùng email Drive/GitHub/Facebook thay thế. Body tts-watchdog
không có placeholder nào (không chứa ID chat hay email) — chỉ cần đặt đúng
`delivery` là chat chính.

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
  đang chạy (qua `cron.update`); lịch interval đổi chu kỳ thì sửa cả `every`.
- **File unit TTS (`company-os/systemd/vieneu-tts.service`) cũng là bản chuẩn dùng chung:** khi sửa unit đang chạy (vd đổi biến môi trường, cổng), cập nhật luôn bản trong repo trong cùng lần sửa — watchdog cài lại unit từ bản này mỗi khi /etc mất sau thay máy, nên bản repo lỗi thời sẽ cài lại unit cũ.

## Ghi chú

- File mẫu trong repo chỉ là chuẩn chung; mỗi tài khoản tự chịu trách nhiệm về
  lịch của mình (bật/tắt/sửa giờ) và chỉ cài khi CEO của tài khoản đó duyệt.
- Đẩy file mẫu lên GitHub theo lệ chung: gửi phân tích cho CEO đọc trước, chỉ
  push sau khi CEO duyệt riêng.
