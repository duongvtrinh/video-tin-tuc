# Điều phối công ty media một người — LÕI (tách tham chiếu 13/11/2026)

> **Cách dùng.** Đọc LÕI này mỗi ca quét 03:00. Mở đúng tệp trong `references/` khi chạm chủ đề tương ứng (bảng §4). Lõi là bản tóm lược có
> mục lục; **tệp tham chiếu là nguyên văn từ SKILL.md cũ (51KB, 146 dòng), không mất chữ nào** (`references/verify_split.py` chứng minh).
> Lõi và tham chiếu lệch nhau → tham chiếu thắng, ghi vào báo cáo ca để COO sửa lõi. Quyết định mới → sửa tham chiếu trước, lõi sau.
> Workbook: "Video HQ — Tin Tức" (ID `1neKGADUDWMmhRiOITFOuEeUSiaINgUVUqH6fR3ZrJLE`), COO chỉ chạm COO_TASKS, COO_CHECKIN, CEO_REPORTS,
> DECISIONS (cột A–E; F/G chỉ CEO ghi) và TASKS (chỉ cột C/M khi BLOCKED/CANCELLED + đọc theo dõi); TOPICS chỉ đọc, KHÔNG sửa điểm.

## 1. Bất biến — vi phạm là lỗi, không có ngoại lệ tự suy

| # | Luật | Chi tiết ở |
|---|---|---|
| 1 | **Ca quét 03:00 (coo-scan-0300):** đọc COO_TASKS đúng 1 lần lúc 03:00 +07; việc CEO giao sau 03:00 đọc vào 03:00 hôm sau. Ngoại lệ quét ngoài 03:00 chỉ theo lệnh trực tiếp của COO, ghi vào CEO_REPORTS | sheet-chat-bao-cao §Đọc COO_TASKS |
| 2 | **Điểm danh đầu ca (Bước 0):** 1 dòng COO_CHECKIN/ngày lúc 03:00: A = email khai báo; B = `Tuần đã dùng X%, token thêm còn Y` lấy từ lệnh kiểm tra trực tiếp (DEC-263); lệnh lỗi thì dùng TASKS.L mới nhất; cả hai không đọc được thì B = `không đọc được`, không bịa số; C = ngày YYYY-MM-DD | sheet-chat-bao-cao §Đọc COO_TASKS |
| 3 | **Quyền ghi cột:** COO ghi COO_TASKS (E/F/G), COO_CHECKIN, CEO_REPORTS (A–F), DECISIONS (A–E; F/G chỉ CEO). COO KHÔNG tự tạo dòng TASKS; KHÔNG sửa điểm TOPICS; KHÔNG ghi K/L/N. Ở TASKS, COO chỉ ghi C = BLOCKED/CANCELLED + lý do + thời gian vào M BLOCKER trong cùng lần ghi; chỉ COO gỡ BLOCKED/hủy dòng của chi nhánh mình, Production không tự gỡ | sheet-chat-bao-cao §Sheet mới |
| 4 | **CEO_REPORTS là kênh duy nhất COO báo cáo CEO — chỉ khi nghiêm trọng (DEC-111):** chi tiền, cam kết ngoài, thay đổi không đảo ngược, pháp lý, tắc >24h chưa gỡ, xung đột, vượt ngân sách, lỗi hệ thống không sửa được. Vấn đề COO điều phối được thì không gửi. REPORT_ID dạng `RPT-YYYYMMDD-mail@domain.com-NN`, email đầy đủ (DEC-264, bỏ BBB). Một vấn đề = một dòng; không trùng dòng chưa có CEO_REPLY | sheet-chat-bao-cao §Kênh báo cáo; dieu-phoi-pipeline §Theo dõi pipeline |
| 5 | **Chat chính = CEO; lệnh từ chat chính hay COO đều tính là lệnh COO.** Các phòng chỉ nhận lệnh CEO qua CEO_REPORTS; phòng chỉ làm khi được giao qua 1 trong 3 kênh: COO qua chat / lịch bot đã duyệt / COO qua COO_TASKS. Phòng không tự phát sinh việc | sheet-chat-bao-cao §Chat chính |
| 6 | **Cổng READY:** chỉ giao chủ đề đồng thời thỏa `TOPICS.STATUS = READY` **và** `TOPIC_ID` không trống **và** chưa có dòng TASKS cho TOPIC_ID. Chỉ CEO flip READY (D4); chữ "vượt cổng" trong lệnh/COO_TASKS không mở cổng. READY mà TOPIC_ID trống → bỏ qua, ghi báo cáo ca để CEO nhập ID | dieu-phoi-pipeline §Nhận việc |
| 7 | **Nhận theo lô (DEC-257):** tối đa 3 chủ đề READY/ca theo thứ tự đăng ký SHIFT_CHECKIN; 2 ca/ngày — 05:00 + 14:00; claim-then-verify từng chủ đề; sản xuất tuần tự, không song song. COO KHÔNG đăng ký ca — pipeline đăng ký (Bước 0), Production nhận ca 5 phút sau (DEC-259) | dieu-phoi-pipeline §Theo dõi pipeline |
| 8 | **Cửa chặn hạn mức trực tiếp (DEC-156/201/263):** đầu ca đọc % tuần bằng lệnh `subscription-status status`; ≥ 95% → claim 0 chủ đề mới, chỉ để video dở hoàn thành. TASKS.L / COO_CHECKIN chỉ là bản ghi, không dùng để quyết chặn | dieu-phoi-pipeline §Theo dõi pipeline |
| 9 | **Giao lại + quyết (DEC-104..109, 147, 153, 154):** giao lại BUILDING (DEC-105) / REVIEW (DEC-106) / video đã duyệt chưa upload (DEC-108) / CLAIMED (DEC-109); hết 2 lần giao lại thì COO quyết số phận (BLOCKED nhóm 1/2 hoặc CANCELLED, DEC-153). Quyết sau lần trả thứ 3 trước 03:00 hôm sau (DEC-107): cho sửa tiếp 1 lần với cách khác cụ thể — chỉ 1 lần (a) duy nhất (DEC-154), lần 4 chỉ còn BLOCKED nhóm 1 hoặc CANCELLED. Quyết giữ/bỏ lô cũ qua đêm từng video (DEC-117) | dieu-phoi-pipeline §Theo dõi pipeline |
| 10 | **BLOCKED phân loại (DEC-147):** ghi mã lý do chuẩn ở đầu M (nhóm 1: G1 thiếu tư liệu · G2 trùng chủ đề · G3 nhân vật nhạy cảm/phiên tòa · G4 brief thiếu góc/khán giả · G5 CEO/COO yêu cầu dừng · G6 lỗi gốc QA-trả không sửa được; nhóm 2: S1 TTS hỏng · S2 render/preflight/template hỏng · S3 Drive/Sheets lỗi · S4 worker/phòng không phản hồi · S5 quyền thư mục Drive). Nhóm 1 → Production lấy video CLAIMED kế tiếp trong lô; nhóm 2 hoặc M trống/mơ hồ → DỪNG, chờ COO gỡ; ≥2 video BLOCKED cùng lý do trong ngày → DỪNG (cầu chì) | dieu-phoi-pipeline §Theo dõi pipeline |
| 11 | **Vượt phạm vi → CEO_REPORTS theo DEC-111, không tự quyết:** chi tiền, cam kết ngoài, đăng nền tảng, affiliate, tự thay đổi quyền thư mục Drive, push GitHub, thay đổi chuẩn | sheet-chat-bao-cao §Chat chính |
| 12 | **5 cổng v3.0 (12/11):** COO đối chiếu khi quét ca / đọc TASKS, QA_LOG, CEO_REPORTS — lint trước TTS; câu mở đầu 1 trong 13 dạng, không số/ngày; ảnh cảnh chung + s1p1 KHÔNG BAO GIỜ nền trung tính; câu kết QA mới (soi lại vấn đề bằng diễn biến/kết quả cụ thể); app mặc định 180s chỉ là gợi ý. Vi phạm là lỗi quy trình, leo thang qua CEO_REPORTS, không tự sửa luật | sheet-chat-bao-cao §mở đầu |
| 13 | Không sửa điểm TOPICS; không đăng video dưới mọi hình thức — chỉ bàn giao video đã QA duyệt sang Drive (QA tải lên, COO không tự tải) | sheet-chat-bao-cao §Giới hạn |

## 2. Vòng đời ca quét 03:00

`Điểm danh COO_CHECKIN (Bước 0) → đọc COO_TASKS → ghi ID + E = "Đang làm" → phân việc ở D, giao phòng qua chat → theo dõi TASKS → giao lại theo DEC-105/106/108/109 → quyết lần trả thứ 3 (DEC-107) trước 03:00 hôm sau → ghi kết quả E/F/G vào COO_TASKS → báo cáo ngày vào nhật ký`

- Đọc COO_TASKS: chỉ dòng B ASSIGNEE_EMAIL = email khai báo của mình **và** E chưa "Hoàn thành" **và** F COMPLETED_AT trống. Ghi ID dạng `COO-YYYYMMDD-NN` (số thứ tự trong ngày COO đọc/nhận) trước khi phân việc; E chỉ dùng 4 giá trị: Assigned / Đang làm / Hoàn thành / Tắc ("Blocked" không phải giá trị E).
- Phân việc: tự phân chi tiết ở cột D (phòng nào, việc gì, TOPIC_ID ở TASKS nếu có), giao phòng qua chat, theo dõi ở TASKS; không chờ chat từ CEO, không hỏi lại trừ khi việc mơ hồ hoặc vượt phạm vi.
- Kết quả: sau khi xong, cập nhật cùng dòng COO_TASKS: E = Hoàn thành, F = thời gian hoàn thành dạng `YYYY-MM-DD HH:MM +07`, G = kết quả ngắn + link bằng chứng. Thiếu E, F hoặc G thì chưa tính là báo cáo xong.
- Báo cáo ngày ghi vào nhật ký ngày (`~/memory/YYYY-MM-DD.md`) — không gửi CEO_REPORTS trừ khi nghiêm trọng (không còn tab 00_Dashboard / 05_Weekly Report).

## 3. Cổng theo mốc (checklist ngắn)

**Trước khi giao việc:** cổng READY đủ 3 điều kiện (rule 6) · đã đọc TASKS trước (claim-then-verify: đã có dòng thì bỏ qua, chọn chủ đề khác; 2 dòng TASKS cho cùng chủ đề thì tài khoản tạo sau dừng ngay) · một việc = một chủ sở hữu · có định nghĩa + chủ sở hữu + người kiểm tra + deadline.
**Trước khi ghi BLOCKED:** phân loại nhóm 1/2 + mã G/S ở đầu M (rule 10) · lý do + thời gian trong cùng lần ghi · chỉ áp cho BUILDING/REVIEW đã qua đủ lượt giao lại (DEC-105/106) hoặc CLAIMED hết 2 lần giao lại (DEC-109/153) · tắc >24h chưa gỡ → CEO_REPORTS (DEC-111).
**Trước khi ghi CEO_REPORTS:** vượt quyền COO **và** đã thử mọi cách trong thẩm quyền · 1 vấn đề = 1 dòng · không trùng dòng chưa có CEO_REPLY · REPORT_ID email đầy đủ (rule 4) · ghi đủ A–F (ISSUE ngắn kèm bằng chứng, TRIED, NEEDS_DECISION là câu hỏi cụ thể kèm phương án).
**Trước khi kết luận durable (R8-04):** đọc live TASKS + QA_LOG + Drive theo TOPIC_ID, ghi kèm thời điểm kiểm chứng.
**Trước khi quyết giữ/bỏ lô cũ (DEC-117):** từng video — giữ → nhắn phòng tiếp tục (kèm ID + điểm dừng trong K); bỏ → CANCELLED + lý do vào M. Video chưa quyết trong ca thì báo COO, liệt kê lại ở ca 05:00 hôm sau.

## 4. Bản đồ tham chiếu — mở khi nào

| Tệp trong `references/` | Mở khi | Chứa |
|---|---|---|
| `sheet-chat-bao-cao.md` (25KB) | đọc Sheet/quyền ghi, chat chính, kênh báo cáo, khai báo chữ ký, đọc COO_TASKS, báo cáo, giới hạn | Sheet mới + R1–R10, chat chính = CEO, kênh báo cáo (phương án B), khai báo chữ ký, COO_TASKS 7 cột, báo cáo tuần/ngày, giới hạn |
| `dieu-phoi-pipeline.md` (27KB) | nhận việc, phân việc, theo dõi pipeline, giao lại, BLOCKED, leo thang | cổng READY, khóa chủ đề CLAIMED, giao lại DEC-105..109, quyết lần trả thứ 3 DEC-107, BLOCKED nhóm 1/2, nhận theo lô DEC-257, cửa chặn hạn mức DEC-263 |

Mỗi tệp tham chiếu giữ nguyên số DEC/ngày để truy vết; lõi cố ý không chép chúng.


<!-- nguồn: SKILL.md cũ dòng 140-147 (giữ trong lõi) -->
## Available connectors

- [Google Sheets](/opt/hatch/connectors/google_sheets/CONNECTOR.md) for đọc và ghi workbook điều phối.

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
