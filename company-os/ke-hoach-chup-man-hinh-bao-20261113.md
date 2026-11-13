# Kế hoạch: Ảnh chụp màn hình bài báo làm tư liệu video

- Ngày: 13/11/2026. Đề xuất của CEO (chat chính).
- Trạng thái: **PHÂN TÍCH + KẾ HOẠCH — chưa triển khai, chờ CEO quyết.**
- Mã DEC: chưa có (nếu duyệt sẽ lấy số tiếp theo, sau DEC-274).

## 1. Ý tưởng (tóm tắt)

Khi quét nguồn dữ liệu, Production chọn ra **1 bài viết nói về chủ đề đầy đủ thông tin nhất**, từ một trang lớn, uy tín. Mở URL trên trình duyệt, **chụp lại ảnh màn hình của trang** (PNG tốt nhất; PDF/JPG cũng được). Ảnh này đưa vào video làm **tư liệu trực quan — bằng chứng thuyết phục** cho luận chứng trong video.

## 2. Vì sao hay

- **Bằng chứng thật, kiểm chứng được.** Ảnh chụp một bài báo thật từ một tờ báo thật mạnh hơn hẳn ảnh minh hoạ chung chung hay ảnh AI: người xem thấy được nguồn, tựa đề, ngày đăng — đúng văn hoá "mỗi con số có nguồn" của công ty.
- **Giải quyết bài toán thiếu ảnh thật.** Nhiều chủ đề không có ảnh thật của sự kiện, nhưng bài báo đầy đủ nhất thì luôn có — và Production đã phải tìm nó để viết kịch bản (luật kịch bản đa nguồn). Ảnh chụp là dạng hình ảnh của nguồn đã có, chi phí tìm thêm gần bằng 0.
- **Khớp luật actual-first.** Đây là tư liệu thật từ báo chí, không phải minh hoạ bịa — cùng họ với ảnh báo chí đã dùng, chỉ khác hình thức (chụp màn hình thay vì tải ảnh).

## 3. Phân tích kỹ thuật (đã kiểm chứng bằng code thật)

### 3.1 Khổ ảnh: 16:9 không hợp video 9:16 — cần chụp kiểu mobile

Video là 720x1280 (9:16). `render_draft.py` xử lý ảnh ngang/vuông bằng **blur-fill 3:4**: ảnh hiển thị trong cửa sổ 720x960, nền mờ lấp đầy (tiền lệ AGENTS.md: crop cửa sổ 3:4 chỉ giữ ~39% chiều rộng cho ảnh ngang; QA rule 4 xác nhận blur-fill 3:4 là thiết kế đúng, không phải lỗi).

Hệ quả: một ảnh chụp 16:9 (1280x720) sẽ hiển thị thành 720x405 ở giữa khung — chữ tựa đề nhỏ, khung lãng phí, bằng chứng yếu đi. **Đề xuất: chụp ở viewport mobile 720px** (trang báo render thành cột hẹp) rồi **cắt cửa sổ 9:16 từ đầu trang** (masthead + tựa đề + ảnh hero + đoạn mở đầu) → full-frame 720x1280, chữ đọc được, không blur. Phương án 16:9 của CEO giữ làm **fallback** cho bài có infographic/biểu đồ ngang quan trọng.

### 3.2 Công cụ chụp: chưa có sẵn, phải dựng mới

Đã kiểm trên máy: **không có Chromium headless, không có Playwright** (`which` trống, import lỗi). Có sẵn: PIL 10.2.0, ffmpeg. Factory chưa có tool chụp màn hình nào.

Hai đường:

| Đường | Ưu | Nhược |
|---|---|---|
| (a) **Headless Chromium + script `bin/screenshot_article.py`** (khuyến nghị làm chính) | Tự động, xác định, không cần người; chạy trong pipeline như mọi bước khác | Phải cài một lần (apt/Playwright); sau thay máy phải cài lại — ghi vào runbook |
| (b) **Browser task trực tiếp** (dự phòng) | Xử lý tốt banner cookie/paywall nhờ phiên đăng nhập sẵn | Builder ở chat Sản xuất không tự mở trình duyệt được — phải qua main chat/COO; mỗi video tốn một lần điều phối |

### 3.3 Chỉ chụp đầu trang, không chụp toàn bài

Chỉ lấy **1 viewport đầu trang** (masthead + tựa đề + hero + đoạn mở đầu). Không chụp toàn bộ thân bài vì: dài, chữ không đọc được ở 720px, và nặng vấn đề bản quyền (sao chép nhiều chữ). Phần đầu trang là đủ để chứng minh "bài này, báo này, nói điều này".

### 3.4 Phân loại media mới

Thêm classification **`chup-man-hinh`** vào media-log:

- Tính là **ảnh thật** (vế thật của trần AI ≤ thật) — vì là ảnh chụp thật của một trang thật, không phải AI tạo.
- Chịu **trần 2 lần/video (DEC-272, dhash)** như mọi visual nội dung — thực tế chỉ dùng 1 lần/video.
- **Không phải nền trung tính** — không chịu trần 1 nền/scene, không nằm trong thư viện `neutral-bg/`.
- Log bắt buộc: **URL bài + tên báo + ngày đăng + ngày chụp** (thay cho `keywordsTried` — vì đây không phải ảnh tìm bằng từ khoá mà là bài đã chọn).
- Preflight kiểm: file tồn tại + log đủ URL/tên báo/ngày đăng; **cảnh báo** (không lỗi) nếu file không phải 9:16.

### 3.5 Khớp luật hiện hành — hai điểm cần ghi rõ

- **§8(d)/Luật 4:** ảnh chụp màn hình báo chí được tính là **"ảnh thật từ báo chí"** → dùng được cho s1p1/ảnh cảnh chung. Ghi rõ vào luật để không nhập nhằng. V1 khuyến nghị chỉ dùng cho 1 part luận chứng (không bắt buộc s1p1).
- **Cửa ngữ nghĩa của QA (rule 5, CEO 28/10):** QA hiện KHÔNG chấm ảnh có đúng ý kịch bản không. Kiểm "ảnh chụp khớp với luận chứng trong lời đọc" được đặt dưới dạng **kiểm provenance** (URL trong log = bài trong ảnh; tựa đề/con số thấy được khớp con số lời đọc nói) — thuộc cửa hồ sơ rule 6 mà QA đã thi hành, **không cần mở cửa ngữ nghĩa**. Nếu CEO muốn QA chấm "ảnh này có chứng minh được luận điểm không" thì đó là quyết định riêng (xem §9).

## 4. Quy trình mới (v1)

1. **Chọn bài** (Production, lúc nghiên cứu kịch bản): từ danh sách nguồn của kịch bản, chọn 1 bài đầy đủ nhất theo tiêu chí §5.
2. **Chụp** (headless): viewport mobile 720x1280, chờ load + chờ ổn định, tắt banner cookie best-effort, chụp viewport đầu trang → PNG.
3. **Cắt** (PIL): cửa sổ 9:16 từ đầu trang → file 720x1280, đặt tên theo quy ước b-roll (`broll_seg_<order>_part_<idx>_<rand6>.png`).
4. **Gán**: làm b-roll cho **part luận chứng** (part nói con số/kết luận trung tâm). `mediaSource.source` = tên báo; classification `chup-man-hinh`; media-log ghi URL + tên báo + ngày đăng + ngày chụp.
5. **Preflight** kiểm theo §3.4 rồi mới render.
6. **QA kiểm** theo §7 rồi mới duyệt.
7. **Thất bại chụp** (bot wall, paywall che tựa đề, banner không tắt được): thử lại tối đa 3 lần → live browser → **bỏ qua, video dựng tiếp bằng thang visual thường**. Không bao giờ chặn dựng video vì ảnh chụp.

## 5. Tiêu chí chọn bài (cụ thể, để Production không phải đoán)

1. Báo lớn, uy tín; chủ đề Việt Nam ưu tiên báo Việt (VnExpress, Tuổi Trẻ, Thanh Niên, Dân Trí, VTV, VietnamPlus, Zing, Lao Động...); chủ đề quốc tế: hãng lớn (Reuters/AP/BBC...) + báo Việt nếu có bài tương đương.
2. Bài chứa **luận chứng trung tâm của video** (con số/trích dẫn/ngày quan trọng nhất).
3. Có masthead + tựa đề + ngày đăng **nhìn thấy được**; có ảnh hero càng tốt.
4. Không phải bài ý kiến, không phải re-post của aggregator, không phải thông cáo báo chí copy nguyên.
5. Không paywall chặn đầu trang.
6. Bài **đã nằm trong danh sách nguồn của kịch bản** — không thêm nguồn mới chỉ để chụp.

## 6. Thay đổi cần làm (v1)

| File | Thay đổi |
|---|---|
| `bin/screenshot_article.py` (mới) | Chụp headless (URL + viewport mobile 720x1280) → cắt 9:16 (PIL) → lưu PNG theo quy ước b-roll. Thử lại tối đa 3 lần. |
| Cài đặt + runbook | Cài headless Chromium một lần; ghi lệnh cài lại vào runbook (mất sau thay máy). |
| `bin/preflight.py` | Nhận classification `chup-man-hinh` (tính thật); bắt buộc log có URL + tên báo + ngày đăng; cảnh báo nếu file không 9:16. |
| `company-os/media-search/LOGIC.md` | Mục mới: định nghĩa, tiêu chí chọn bài (§5), quy trình chụp, log, cách đếm; §8(d) ghi rõ ảnh chụp được tính là ảnh thật từ báo chí. |
| Production skill (`tim-anh-media-luat-ke-nhau.md`) | Mục "Ảnh chụp màn hình bài báo (bằng chứng)": khi dùng (1/video, part luận chứng), cách chụp, schema log. Thang visual (1)–(4) không đổi — ảnh chụp là visual đặc biệt cho part luận chứng, không thay thang chung. |
| QA skill (`danh-gia-va-tieu-chi.md`) | Mục kiểm mới (§7): đọc được ở full-frame; masthead thấy được; không overlay/banner che tựa đề; khớp luận chứng (provenance); dùng tối đa 1 lần. |
| COO skill | **Không đổi v1** (đây là việc Production/QA, không phải cổng COO). |
| Template mới | **Không v1** — chỉ làm ở v2 nếu duyệt (xem §8). |

## 7. QA kiểm gì (v1)

1. Tựa đề đọc được ở full-frame 720x1280 (không phải vệt chữ mờ).
2. Masthead/tên báo thấy được (chứng minh nguồn ngay trong ảnh).
3. Không có banner cookie, popup, quảng cáo hay paywall che tựa đề.
4. Khớp luận chứng: URL trong log = bài trong ảnh; tựa đề/con số thấy được khớp con số lời đọc nói ở part đó.
5. Chỉ dùng 1 lần trong video.
6. Lời đọc ở part đó có ghi nguồn ("theo VnExpress...") — luật ghi nguồn vốn đã có, ảnh chụp không thay thế lời ghi nguồn.

## 8. Thí điểm, đánh giá, và v2

- **Thí điểm:** 2–3 video, mỗi video 1 ảnh chụp cho 1 part luận chứng. Production làm theo §4; QA chấm theo §7.
- **Đánh giá sau thí điểm** (QA + CEO soi mắt): tựa đề có đọc được không? Có thuyết phục hơn không? Chụp có chặn dựng không? Người xem có nhầm ảnh chụp là claim của video không?
- **Quyết sau thí điểm:** giữ v1 / làm **v2 (template bằng chứng riêng** — khung trình duyệt: thanh URL + tên báo + vùng ảnh chụp đo sẵn như photo templates) / bỏ.
- V2 tốn thêm ~1 phiên (dựng template + kiểm render + CEO soi mắt). Không làm v2 trước khi v1 chứng minh được giá trị.

## 9. Rủi ro + giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Bot wall / paywall / banner cookie che tựa đề | Thử lại tối đa 3 lần → live browser → bỏ qua (không chặn dựng) |
| Mất cài đặt Chromium sau thay máy | Ghi lệnh cài lại vào runbook; cài lại là một lệnh |
| Chữ quá nhỏ, không đọc được | Chụp mobile 9:16 (§3.1); QA kiểm đọc được (§7.1); không đạt thì bỏ ảnh chụp ở video đó |
| Bản quyền | Chỉ chụp đầu trang (tựa đề + mở đầu), không chụp thân bài; masthead hiện rõ trong ảnh (ghi nguồn ngay trong hình); log URL + ngày. Cùng tư thế như ảnh báo chí đã dùng. Rủi ro tồn dư — không phải tư vấn pháp lý. |
| Người xem nhầm ảnh chụp là claim của video | Masthead + tên báo trong ảnh; lời đọc ghi nguồn theo luật vốn có |
| Bài đổi tựa đề sau khi chụp | Ảnh chụp là bản đông cứng tại ngày chụp; log ghi ngày chụp |
| Ảnh chụp thay thế ảnh thật của sự kiện | Không: ảnh chụp chỉ dùng cho part luận chứng (con số/kết luận), không dùng cho part tả cảnh/sự kiện — chỗ đó vẫn ưu tiên ảnh thật của sự kiện |

## 10. Chi phí / nỗ lực (ước tính)

- **v1:** ~2 phiên làm việc của agent (tool chụp + luật + preflight + kiểm chứng trên 3–5 bài thật) + thí điểm 2–3 video. Không dịch vụ trả phí mới (Chromium miễn phí). Không chặn pipeline khi chụp lỗi.
- **v2 (template, nếu duyệt):** +1 phiên.
- Chi phí chạy: 1 ảnh PNG 720x1280 (~0,5–2MB)/video — không đáng kể.

## 11. Quyết định cần CEO

1. **Hướng chính:** (A) duyệt **v1 thí điểm** (chụp headless, mobile 9:16, 1 ảnh/video cho part luận chứng, không template mới) → làm xong thí điểm rồi báo cáo lại; (B) duyệt **v1 + làm luôn template v2**; (C) **để sau**, chưa làm.
2. **Phụ (quyết cùng lúc hoặc để sau):**
   - (1) Khổ ảnh: 9:16 mobile (khuyến nghị) vs 16:9 (đề xuất gốc — xem §3.1 vì sao 9:16 hơn).
   - (2) Có cho dùng ảnh chụp ở **s1p1** không? (Khuyến nghị v1: được, nhưng không bắt buộc — để thí điểm trả lời.)
   - (3) Chụp: headless làm chính + live browser dự phòng (khuyến nghị) vs chỉ live browser.
   - (4) QA: chỉ kiểm provenance (§7.4, trong rule 6 sẵn có) vs mở cửa ngữ nghĩa hẹp cho cặp ảnh–luận chứng (quyết định riêng, xem §3.5).

## 12. Kết quả kiểm chứng tool (13/11, trước khi áp dụng)

**Tool chọn: Google Chrome headless stock** (google-chrome 157.0.8103.78, cài từ .deb chính thức, ~17s) — 1 lệnh duy nhất, không server, không driver. Khởi động ~1s, chụp xong trong 4–14s.

**Loại trừ:** binary Chrome của Muse (`/opt/meta-chromium/chrome`) KHÔNG dùng được — đòi policy file WebGL domain (file + SHA-256, "contract" có chữ ký): thử ~14 định dạng đều lỗi `invalid WebGL domain policy contract`; các switch `--hatch-webgl-allowed-domains(-v1)`/`all-origins` chỉ qua được `--version`, không qua được lần chạy thật. Playwright nặng hơn (pip + tải browser riêng) nên không chọn.

**Mạng VM (2 yêu cầu riêng, đã kiểm chứng):** egress qua proxy `hatch-egress-proxy:3128` có auth (env `https_proxy`) + MITM TLS (CA "Hatch Sandbox Egress CA", bundle `/run/hatch/egress-tls/ca-bundle.pem`).
- (a) Cần **mini CONNECT proxy local** (127.0.0.1:8899, ~90 dòng Python, đọc auth từ env, không ghi mật khẩu ra file/log): Chrome không ăn auth trong `--proxy-server` (lỗi `ERR_NO_SUPPORTED_PROXIES`, mật khẩu đã kiểm là ký tự an toàn — không phải do ký tự lạ) và không đọc userinfo từ env (tunnel failed). Direct cũng không đi được (TLS bị MITM chặn).
- (b) Cần **`--ignore-certificate-errors`**: Chrome 157 dùng Chrome Root Store (không tin CA Hatch). CA đã có trong `/etc/ssl/certs` và `~/.pki/nssdb` (fingerprint khớp với CA đang phát hành) nhưng Chrome vẫn từ chối; thử policy `ChromeRootStoreEnabled=false` không có tác dụng trong headless. Điểm cần quyết cho v1: giữ cờ này (rủi ro thấp trong sandbox này vì mọi TLS đều đã qua MITM của Hatch; tool chỉ tải trang công khai, không đăng nhập) hay đầu tư sửa trust đúng cách.

**Kết quả chụp (viewport 720x1280, đã soi mắt từng ảnh):**
- VNBizNews, bài Nvidia tiếng Việt: 3,9s → PNG 720x1280, 6,5KB — trang trả **"Forbidden" (403)**. Tool chạy đúng, site chặn.
- Reuters DE, bài Nvidia: 13,7s → PNG 720x1280, 17KB — trang hiện **tường kiểm bot "Verifying the device..."**. Tool chạy đúng, site chặn.
- Blog Nvidia JP: treo >4 phút (nghi `--virtual-time-budget` kẹt với JS chạy liên tục) — đã kill. Bài học: không dùng `--virtual-time-budget` cho trang JS nặng; dùng timeout thời gian thực.

**Kết luận: TOOL HOẠT ĐỘNG** (render + chụp đúng 720x1280). Chưa có ảnh bài báo thật nào vì cả 2 báo thử đều chặn bot từ egress này. Hệ quả cho v1: đường chụp headless cần thêm fallback live-browser cho trang có tường bot (đã có trong kế hoạch §4); và cần timeout thực thay vì virtual-time-budget.

**Chứng cứ:** `company-os/anh-chup-thu/reuters-nvidia-20261113.png`, `vnbiznews-nvidia-20261113.png`. Script thử (tạm, ở `/tmp/shot-test/mini_proxy.py` — bản v1 viết lại thành `bin/screenshot_article.py` nếu duyệt).

**Đường trình duyệt thực của Muse (19:22 13/11, bổ sung sau khi CEO yêu cầu thử):** mở đúng bài VNBizNews trên — KHÔNG bị 403, KHÔNG tường bot, không banner cookie, không yêu cầu đăng nhập. Tựa đề đọc rất rõ trong ảnh chụp; logo VNBIZ News + sapo + hộp "Ý CHÍNH" thấy rõ. Ảnh chụp 1919×998 (viewport desktop — không chỉnh được 720×1280). Bài này vốn KHÔNG có ảnh hero (sau sapo là hộp Ý CHÍNH rồi thân bài) — không phải lỗi tải. Hạn chế còn lại: (a) chưa lấy được file PNG về workspace (ảnh chỉ nằm trong báo cáo của trình duyệt, tôi chưa cầm được file để đính kèm); (b) viewport desktop — muốn 9:16 phải crop sau (mất 2 bên) hoặc chụp lại kiểu mobile; (c) chưa rõ cơ chế giao file cho pipeline — cần thử lưu file ở v1. Kết luận: trình duyệt thực đọc được báo mà headless bị chặn — là đường dự phòng đúng cho trang có tường bot.

## 13. Hướng PDF toàn trang (đề xuất mới, 13/11 — CEO yêu cầu nghiên cứu vì headless bị chặn bot)

### 13.1 Vì sao PDF

Headless screenshot bị chặn bot ở chính các báo lớn (VNBizNews 403, Reuters tường kiểm bot). PDF in từ trình duyệt thực đọc được báo bị chặn; chữ trong PDF là vector (sắc nét ở mọi mức zoom); bản in thường sạch (không quảng cáo/banner); và quan trọng nhất — **file PDF giao được về workspace** (đã chứng minh, xem 13.2), giải quyết đúng chỗ tắc của hướng chụp ảnh (ảnh chụp chưa lấy được file về).

### 13.2 Đã kiểm chứng bằng file thật (13/11)

- **PDF VNBizNews** (bài Nvidia, trình duyệt thực in toàn trang): **17 trang, khổ Letter (612×792 pt), 6,9 MB**, tạo lúc 19:28, tiêu đề đúng. File về tới workspace (`company-os/anh-chup-thu/vnbiznews-nvidia-20261113.pdf`).
- **PDF blog Nvidia** (headless `--print-to-pdf`): 1,5 MB, 35s — headless in PDF được ở trang không chặn (khác với chụp ảnh treo ở `--virtual-time-budget`).
- **Tool cắt có sẵn:** `pdftoppm`, `pdfinfo`, `pdfimages`, PIL — không cần cài thêm.
- **Cắt thử 3:4 trang 1 → 720×960 (đã soi mắt): tựa đề to đậm đọc rõ, sapo đậm đọc rõ, hộp Ý CHÍNH đọc được, thân bài nhỏ nhưng vẫn đọc được phần lớn.** Đây là bằng chứng thuyết phục ở đúng cỡ hiển thị trong video.
- **Cắt thử 3:4 trang 3 (để chứng minh cái sai):** hiện ảnh nhà máy VinFast, 2 bài Nvidia KHÁC (kèm ảnh Jensen Huang), tin NSND Công Lý, tin lãi tiết kiệm — toàn tin khác, không phải bài được trích. Dùng crop này làm bằng chứng sẽ gây hiểu lầm.

### 13.3 Quy tắc cắt 3:4 (đề xuất)

- **Khổ cắt 3:4** vì khớp đúng cửa sổ hiển thị của engine (720×960, blur-fill 3:4) — ảnh cắt vừa khít cửa sổ, không viền mờ, không lãng phí. Trang Letter có tỉ lệ 0,773 ≈ 3:4 nên cắt toàn trang gần như vừa khít.
- **Neo ở ảnh CỦA BÀI:** cắt ở đoạn có ảnh hero/ảnh thân bài đầu tiên của chính bài được trích, sao cho một cửa sổ 3:4 chứa được cả tựa đề + ảnh (với bài báo thường — tựa đề, sapo, ảnh hero liền nhau ở trang 1–2 — điều này làm được).
- **Không có ảnh thì cắt tựa đề + sapo (trang 1)** — như bài VNBizNews này (không có ảnh hero, vẫn đủ bằng chứng).
- **TUYỆT ĐỐI KHÔNG cắt mục tin liên quan / sidebar / "các tin khác":** ảnh và tựa đề ở đó là của bài khác (đã chứng minh bằng crop trang 3). Đây là luật cứng, QA kiểm.
- **Muốn chữ to hơn:** in từ viewport hẹp (kiểu mobile) để cột chữ hẹp lại — để v2 (trình duyệt thực hiện chưa chỉnh được viewport).

### 13.4 Quy trình v1 (đề xuất)

1. Chọn bài (như §5). 2. Lấy PDF: headless `--print-to-pdf` trước; bị chặn thì trình duyệt thực in PDF (file về workspace — đã chứng minh). 3. Render trang bằng `pdftoppm` 150dpi. 4. Builder xem các trang, chọn vùng cắt 3:4 (neo ảnh của bài hoặc tựa đề+sapo; không chạm tin liên quan). 5. Cắt bằng PIL → PNG 720×960 làm b-roll cho part luận chứng (classification `chup-man-hinh`; log ghi URL + tên báo + ngày đăng + số trang/vùng cắt). 6. Preflight → render → QA kiểm (đọc được; đúng bài được trích; không dính tin khác; dùng 1 lần).

### 13.5 Thay đổi cần làm (v1)

| File | Thay đổi |
|---|---|
| `bin/pdf_crop.py` (mới) | Render trang (`pdftoppm`) + cắt 3:4 theo trang/vùng (PIL) → PNG 720×960. |
| `bin/preflight.py` | Nhận crop từ PDF (tính thật); bắt log có URL + tên báo + ngày đăng + trang cắt. |
| `company-os/media-search/LOGIC.md` | Mục cắt PDF + luật không cắt tin liên quan. |
| Production + QA skill | Mục "Ảnh chụp từ PDF bài báo": cách lấy PDF, cách chọn vùng cắt, QA kiểm (đúng bài, không tin khác). |
| Luồng xin PDF | Khi headless bị chặn, builder xin PDF từ trình duyệt thực qua COO/main chat — cần định rõ luồng này khi làm v1. |

### 13.6 So sánh PDF vs chụp ảnh màn hình

| | PDF toàn trang | Chụp ảnh màn hình |
|---|---|---|
| Chặn bot | Trình duyệt thực in được báo bị chặn | Headless bị chặn; trình duyệt thực đọc được nhưng chưa giao được file |
| Độ sắc | Chữ vector, sắc ở mọi zoom | Raster theo viewport |
| Giao file về workspace | **Đã chứng minh** (PDF 6,9 MB về tới nơi) | Chưa chứng minh (ảnh chỉ nằm trong báo cáo) |
| Khổ | Cắt 3:4 khớp cửa sổ engine | Mobile 9:16 full-frame (đẹp hơn nếu chụp được) |
| Việc thêm | Phải cắt (builder xem trang, chọn vùng) | Chụp xong dùng ngay |
| Rủi ro chính | Cắt nhầm sang tin khác (luật + QA chặn) | Trang chặn bot (cần đường dự phòng) |

### 13.7 Rủi ro

Layout in khác nhau theo báo (QA kiểm từng crop); PDF dài (17 trang cho 1 bài — chỉ cần trang 1–2, còn lại là tin liên quan); in từ trình duyệt thực là bước thủ công (builder phải chờ file); một số báo chặn in/paywall bản in; crop sai vùng = bằng chứng sai (luật không cắt tin liên quan + QA kiểm là 2 lớp chặn).

### 13.8 Chi phí

~2 phiên làm việc (tool cắt + luật + preflight + kiểm chứng) + thí điểm 2–3 video. Không phí dịch vụ mới.

### 13.9 Quyết định cần CEO

(A) **Duyệt hướng PDF làm chính** (thay hướng chụp ảnh) → làm v1 thí điểm; (B) **Giữ hướng chụp ảnh**, PDF chỉ là dự phòng khi chụp bị chặn; (C) **Để sau**, chưa làm.

**Quyết 19:37 13/11:** CEO duyệt phương án tích hợp (§14) — trong đó PDF là đường chính (§14.1) — nên hướng PDF làm chính (phương án A) được chốt cùng lúc. **Sửa 13/11 (~19:51, lệnh CEO): chụp ảnh màn hình LOẠI KHỎI LOGIC (chỉ cho tỉ lệ 16:9, phương án tồi) — chỉ còn đường PDF; các lựa chọn B/C ở trên không còn ý nghĩa.** v1 đã làm xong (xem §14.9).

## 14. Phương án tích hợp (đề xuất, 13/11 — CEO yêu cầu sau khi chốt hướng PDF)

### 14.1 Nguyên tắc

- **1 ảnh bằng chứng/video, cho đúng 1 part** (part luận chứng). Không bao giờ 2 ảnh bằng chứng/video (tránh loãng + tránh trần DEC-272).
- Ảnh bằng chứng là **nguyên trang PDF render thành ảnh** (hướng §13) — **CHỈ CÒN ĐƯỜNG PDF**; chụp ảnh màn hình đã loại khỏi logic (lệnh CEO 13/11: chỉ cho tỉ lệ 16:9, phương án tồi).
- **Bài báo làm bằng chứng phải CÓ ẢNH** (hero/ảnh thân bài gần tựa đề). Không có ảnh → **chọn nguồn báo chí khác** (lệnh CEO 13/11). Thử tối đa 3 nguồn; hết 3 mà không có → **BỎ ảnh bằng chứng ở video đó** (ghi lý do vào log; không chặn dựng video; không dùng ảnh tin liên quan).
- Ảnh bằng chứng không thay thang visual (1)–(4): các part khác vẫn theo thang (ảnh thật → AI → crop → fill-in). Nó chỉ thay visual của đúng 1 part luận chứng.

### 14.2 Khi nào thêm (điều kiện — phải đủ cả 4)

1. Video có **luận chứng trung tâm rõ ràng** (1 con số / 1 trích dẫn / 1 kết luận) mà lời đọc nêu **kèm nguồn** ("theo VnExpress...").
2. Có **1 bài báo uy tín chứa đúng luận chứng đó** (từ danh sách nguồn của kịch bản) **VÀ bài có ảnh** hero/thân bài gần tựa đề (ảnh nội dung ≥ ~400px trong PDF, không phải logo/quảng cáo/thumbnail tin khác).
3. **Lấy được PDF** của bài (headless hoặc trình duyệt thực).
4. Có **1 part mà lời đọc nêu luận chứng đó**, với thời lượng hiển thị ≥ ~4s (giọng + pauseAfterMs).

**KHÔNG thêm khi:** luận chứng là tổng hợp từ nhiều nguồn (không có 1 bài nào đứng tên nó — tránh gán sai nguồn); bài là ý kiến/bình luận (không phải tin tức); PDF in lỗi/paywall che tựa đề; không có part nào nêu luận chứng kèm nguồn; hết 3 nguồn mà không có ảnh.

### 14.3 Thêm ở đâu (chọn part)

- **Ưu tiên 1:** part **ĐI SÂU ĐẦU TIÊN nêu luận chứng trung tâm kèm nguồn** (thường S2P1/S3P1, ngay sau hook + preview). Người xem vừa nghe con số vừa thấy bằng chứng — thuyết phục nhất.
- **Ưu tiên 2** (nếu hook đã nêu con số): part ngay sau hook/preview nêu lại luận chứng kèm nguồn.
- **Ưu tiên 3:** part **kết luận/chốt** (nêu lại kết quả chính kèm nguồn).
- **Mặc định KHÔNG đặt ở s1p1:** hook cần ảnh/video sự kiện để giữ người xem 0–3s; ảnh bằng chứng nhiều chữ, ít cảm xúc. Chỉ đặt ở s1p1 khi hook chính là con số và không có ảnh sự kiện nào.
- **Chỉ 1 part.** Part đó dùng **template dưới đáy** (preview-banner/keyword-block) hoặc **không template** — KHÔNG dùng template toàn màn hình (che mất ảnh cắt). Phụ đề karaoke: kiểm tra khung render, không để phụ đề che tựa đề trong ảnh cắt.
- **Thời lượng hiển thị ≥ ~4s:** ưu tiên chọn part có câu luận chứng đủ dài; nếu giọng ngắn hơn thì tăng pauseAfterMs cho đủ 4s (ghi rõ trong plan).

### 14.4 Luồng tích hợp vào pipeline (v1)

| Bước | Ai | Làm gì |
|---|---|---|
| 1. Xác định luận chứng + part | Builder (Production) | Sau khi kịch bản duyệt: xác định luận chứng trung tâm + bài báo nguồn (từ danh sách nguồn) + part luận chứng (theo 14.3). |
| 2. Kiểm bài có ảnh không | Builder | Xem PDF/screenshot hoặc ảnh hero trong nguồn. Không có → đổi nguồn khác (tối đa 3). Hết 3 → bỏ, ghi lý do vào media-log. |
| 3. Lấy PDF | Builder + COO/main chat | Headless `--print-to-pdf` trước; bị chặn → builder ghi yêu cầu vào TASKS.K + nhắn COO; main chat in PDF bằng trình duyệt thực, file về workspace, báo lại qua COO. |
| 4. Trang nguyên | Builder | Tỉ lệ trang — 3 trường hợp: (1) trong khoảng 3:4–4:3 thì render NGUYÊN TRANG (`bin/pdf_crop.py --whole-page`, 200 DPI) → PNG giữ nguyên tỉ lệ trang, không cắt, không cảnh báo gì; (2) trang DÀI HƠN 3:4 (tỉ lệ < 0,75) thì GIỮ LẠI, cắt ảnh 3:4 (`bin/pdf_crop.py --full-page`, cửa sổ trên cùng, đầy chiều rộng) → PNG 720×960; (3) trang RỘNG HƠN 4:3 (tỉ lệ > 1,33, trang quá ngắn) thì LOẠI NGUỒN, tìm nguồn khác (tối đa 3 nguồn). Chỉ bỏ trang quá ngắn. Trang phải là trang CỦA BÀI (tựa đề/sapo/thân bài). |
| 5. Gán vào part | Builder | Làm b-roll part luận chứng: `mediaSource.source` = tên báo; classification `chup-man-hinh`; media-log ghi URL + tên báo + ngày đăng + ngày lấy PDF + trang đã lấy (+ lý do nếu bỏ). |
| 6. Preflight | Preflight | Kiểm: file tồn tại; log đủ URL/tên báo/ngày/trang; chặn file là cả trang dài chưa cắt (tỉ lệ < 0,75 — phải cắt 3:4) hoặc file rộng hơn 4:3 (trang quá ngắn — phải loại nguồn); tính thật cho trần AI. |
| 7. Render + QA | QA | Kiểm: đọc được ở 720×960; đúng bài được trích; không dính tin khác; giọng ghi nguồn; dùng 1 lần; phụ đề không che tựa đề. |
| 8. Bàn giao | QA | Như thường (upload Drive + ghi TASKS/QA_LOG). |

### 14.5 Thay đổi cần làm (v1)

| File | Thay đổi |
|---|---|
| `bin/pdf_crop.py` (mới) | Render trang (`pdftoppm`) + cắt 3:4 theo trang/vùng (PIL) → PNG 720×960. |
| `bin/preflight.py` | Nhận crop từ PDF (tính thật); bắt log có URL + tên báo + ngày đăng + trang cắt. |
| `company-os/media-search/LOGIC.md` | Mục ảnh bằng chứng: luật chọn nguồn có ảnh (§14.2), luật chọn part (§14.3), luật không cắt tin liên quan (§13.3). |
| Production skill (`tim-anh-media-luat-ke-nhau.md`) | Mục "Ảnh bằng chứng": khi nào thêm, thêm ở đâu, luồng lấy PDF, cách cắt. |
| QA skill (`danh-gia-va-tieu-chi.md`) | Mục kiểm ảnh bằng chứng (§14.4 bước 7). |
| COO skill | Luồng xin PDF (bước 3) — 1 dòng + tham chiếu. |
| media-log schema | Classification `chup-man-hinh` + các trường bắt buộc (URL, tên báo, ngày đăng, ngày lấy PDF, trang/vùng cắt). |

Không đổi: thang visual (1)–(4), luật nền trung tính, DEC-272, cửa QA 3 cổng, template.

### 14.6 Thí điểm + đánh giá

2–3 video (chọn video có luận chứng rõ + bài có ảnh hero). Đánh giá: tựa đề đọc được không? Có thuyết phục hơn không (CEO soi mắt)? Lấy PDF + cắt có làm chậm ca dựng không? Có nhầm nguồn không? Sau thí điểm: giữ / chỉnh (đổi part, đổi số nguồn thử) / bỏ.

### 14.7 Rủi ro + giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Nguồn tốt nhất không có ảnh | Đổi nguồn (tối đa 3) rồi bỏ nếu hết — không chặn dựng |
| Luận chứng tổng hợp nhiều nguồn | Không thêm (tránh gán sai nguồn) |
| PDF in lỗi / paywall | Đổi nguồn hoặc bỏ |
| Builder chọn sai part (đặt ở hook hoặc part không nêu nguồn) | Luật chọn part 14.3 + QA kiểm |
| Chờ PDF từ trình duyệt thực làm chậm ca | Headless trước (nhanh khi được); chỉ xin trình duyệt thực khi headless bị chặn; giới hạn 1 lần xin/video |
| Crop dính tin khác | Luật không cắt tin liên quan + QA kiểm (2 lớp) |

### 14.8 Quyết định cần CEO

(A) **Duyệt phương án tích hợp này** → làm v1 thí điểm (2–3 video). (B) **Chỉnh phương án** (nói rõ chỗ chỉnh: part mặc định, số nguồn thử, có cho s1p1 không...). (C) **Để sau**, chưa làm.

**Quyết 19:37 13/11: CEO chọn (A) — duyệt phương án, làm v1 thí điểm.**

### 14.9 v1 đã làm xong (13/11, sau khi CEO duyệt)

| Hạng mục | Trạng thái |
|---|---|
| `bin/pdf_crop.py` (mới) | Xong — render trang (`pdftoppm`) + cắt 3:4 → PNG 720×960; tự ép đúng tỉ lệ 3:4 khi box lệch; thử trên PDF VNBizNews thật: `--full-page` trang 1 ra đúng 720×960, dhash cách crop tay 2 (cùng nội dung), soi mắt đọc rõ tựa đề/sapo/Ý CHÍNH. |
| `bin/preflight.py` | Xong — classification `chup-man-hinh` tính vào vế thật của trần AI ≤ thật (nhánh rõ, trước đây fallback cũng cho là thật); chặn khi log thiếu 1 trong 4 trường (link/source/articleDate/pdfPage) hoặc video có 2 part bằng chứng trở lên; cảnh báo khi thiếu cropBox hoặc file lệch tỉ lệ 3:4. |
| `LOGIC.md` | Xong — mục Ảnh bằng chứng (khi nào/thêm ở đâu/lấy PDF/cắt 3:4/log/đếm) + mục 6 (trần AI/DEC-272) + mục Hồ sơ bàn giao. |
| Skill Production | Xong — từ vựng classification + nhật ký theo part + mục Ảnh bằng chứng + đếm. |
| Skill QA | Xong — mục kiểm (7) + trần AI + cửa hồ sơ (thiếu URL/tên báo/ngày đăng/trang cắt → TRẢ LẠI). |
| Skill COO | Xong — quy tắc 14: luồng xin PDF (Production nhắn → COO chuyển chat chính → main chat in PDF → báo lại). |
| media-log schema | Xong — classification `chup-man-hinh` + 4 trường bắt buộc (link/source/articleDate/pdfPage) + cropBox/captureDate. |

**Kiểm chứng (project thử `evidence001`, fixture có README, không phải video thật):** trường hợp ĐỦ (part 1 AI + part 2 bằng chứng) → preflight ĐẠT ✓, trần AI ≤ thật qua (AI 1 ≤ thật 1); thiếu articleDate + pdfPage → chặn đúng 2 trường, CHƯA ĐẠT; 2 part bằng chứng → chặn "tối đa 1 ảnh bằng chứng/video", CHƯA ĐẠT; crop lệch tỉ lệ 3:4 → cảnh báo, vẫn ĐẠT (QA soi khung quyết). Hồi quy topic357001 không đổi (chỉ lỗi DEC-274 S2P1 đã biết).

**Sửa v1.1 (13/11, lệnh CEO — chụp ảnh chỉ cho 16:9, phương án tồi; trang PDF theo khoảng tỉ lệ):** (1) chụp ảnh màn hình LOẠI KHỎI LOGIC — chỉ còn đường PDF; (2) ảnh bằng chứng đổi từ cắt 3:4 sang NGUYÊN TRANG (`bin/pdf_crop.py --whole-page`, 200 DPI); (3) chỉ dùng trang có tỉ lệ rộng/cao trong khoảng 3:4 (0,75)–4:3 (1,33), ngoài khoảng thì loại nguồn, tìm nguồn khác; trang trong khoảng thì dùng nguyên trang, không cảnh báo gì; (4) preflight bỏ cảnh báo 3:4 + cropBox, chặn file ngoài khoảng tỉ lệ; (5) LOGIC.md + skill Production/QA/COO + kế hoạch + MEMORY.md + AGENTS.md đã sửa theo. Kiểm chứng lại trên fixture `evidence001` (part 2 đổi sang file trang nguyên 1700×2200): đủ → ĐẠT, không cảnh báo; thiếu trường/2 part → chặn; file ngoài khoảng (tỉ lệ 0,56) → chặn. Hồi quy topic357001 không đổi.

**Sửa v1.2 (13/11, lệnh CEO — 2 lần sửa liên tiếp: "Trang tỷ lệ dài hơn 3:4 thì giữ lại và cắt ảnh 3:4" + "Tôi chỉ bỏ trang quá ngắn"):** v1.1 đã hiểu sai — bỏ cả 2 phía ngoài khoảng. Luật đúng là 3 trường hợp: (1) trang trong khoảng 3:4–4:3 → nguyên trang (`--whole-page`), không cảnh báo; (2) trang DÀI HƠN 3:4 (tỉ lệ < 0,75) → GIỮ LẠI, cắt ảnh 3:4 (`--full-page`, cửa sổ trên cùng, đầy chiều rộng) → PNG 720×960; (3) trang RỘNG HƠN 4:3 (tỉ lệ > 1,33, trang quá ngắn) → LOẠI NGUỒN, tìm nguồn báo khác. **Chỉ bỏ trang quá ngắn.** Sửa: `bin/pdf_crop.py` — `--full-page` xử lý trang dài (trước đây chỉ cắt 2 bên theo chiều cao, lỗi với trang dài vì box vượt trang); `--whole-page` báo 2 lỗi riêng (dài → cắt 3:4, rộng → loại nguồn); `bin/preflight.py` — 2 lỗi riêng tương ứng (tỉ lệ < 0,75 → báo cắt 3:4; tỉ lệ > 1,33 → báo loại nguồn); LOGIC.md + skill Production/QA + kế hoạch + MEMORY.md + AGENTS.md sửa theo. Kiểm chứng: xem §14.9 (tiếp).

**Kiểm chứng v1.2 (fixture `evidence001`, part 2 đổi file):** đủ (trang nguyên VNBizNews 1700×2200, tỉ lệ 0,77) → ĐẠT ✓; file trang dài chưa cắt (720×1280, tỉ lệ 0,56) → chặn "giữ lại trang này, cắt ảnh 3:4 bằng bin/pdf_crop.py --full-page rồi chạy lại preflight" ✓; file trang rộng (1280×720, tỉ lệ 1,78) → chặn "rộng hơn 4:3, trang quá ngắn — loại nguồn này, tìm nguồn báo khác" ✓; ảnh cắt 3:4 từ trang dài (720×960) → ĐẠT ✓; khôi phục file gốc → ĐẠT ✓. Tool: `--whole-page` trang dài (0,5) → thoát 1 "giữ lại, cắt 3:4"; `--whole-page` trang rộng (2,0) → thoát 1 "trang quá ngắn — loại nguồn"; `--full-page` trang dài (600×1200) → cửa sổ trên cùng 720×960 ✓ (v1.1 cũ bị lỗi box vượt trang); `--full-page` trang 1 VNBizNews → cửa sổ giữa 720×960 ✓. Hồi quy topic357001 không đổi (chỉ lỗi DEC-274 S2P1 đã biết).

**Thí điểm:** 2–3 video có luận chứng rõ + bài có ảnh hero. Ca 05:00 và 14:00 ngày 14/11 đều claim 0 chủ đề mới (hạn mức tuần 100%, reset 02:59 16/11 theo DEC-263) nên thí điểm chạy trên các video dựng tiếp theo sau reset (hoặc trên TOPIC-359 nếu CEO quyết làm) — v1 đã sẵn, không cần thêm việc.
