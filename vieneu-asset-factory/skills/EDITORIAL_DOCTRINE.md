# HỌC THUYẾT DỰNG PHIM VST (Editorial Doctrine) — v3.1 NGỮ CẢNH LINH HOẠT & ĐIỆN ẢNH

> Tài liệu gốc duy nhất về triết lý dựng phim của VieNeu Studio.
> Mọi skill trong `.agents/skills/` chỉ được TRÍCH DẪN, không chép lại nội dung này.
> Sửa đổi học thuyết ở đây tự động có hiệu lực cho toàn bộ pipeline.

---

## 1. Triết lý Cốt lõi: Phù hợp Ngữ cảnh Kịch bản (Context-First Cinema Editing)

1. **Tỷ lệ chữ và tần suất hiển thị linh hoạt theo kịch bản:**
   - **Không khóa cứng điều kiện tỷ lệ chữ** hay hạn ngạch cứng nhắc. Tỷ lệ chữ hiển thị hoàn toàn dựa vào tính chất và bối cảnh của từng kịch bản.
   - **Không cấm các cảnh chữ liên tiếp** nếu mạch kịch bản thực sự cần (ví dụ chuỗi luận điểm dồn dập, so sánh đối đầu, hoặc các mốc lịch sử/số liệu liên tục). Khi kịch bản cần nhấn mạnh, hãy để template chữ xuất hiện tự nhiên.
   - Khi kịch bản mang tính mô tả cảnh quan, hành động hoặc đại cảnh, hãy ưu tiên Pure Visual Footage để hình ảnh điện ảnh lên tiếng.

2. **Bảo toàn tuyệt đối lời thoại (Lossless Audio Gate):**
   - Nối mọi `voiceText` phải ra đúng 100% kịch bản gốc: từng chữ, dấu câu, con số. Tuyệt đối không cắt gọt track âm thanh giọng đọc.

3. **Hình và Tiếng độc lập — Multi-Shot Visual Beats:**
   - Trong một câu thuyết minh dài (3s–10s), hình ảnh không được đứng yên một góc máy duy nhất.
   - Nhịp hình được bẻ thành các **Visual Beats (1.2s – 3.2s)** cắt nhanh theo từng danh từ / thực thể hành động (Action / Reaction / Insert Detail), trong khi track âm thanh tiếp tục phát liền mạch.

4. **Nội dung cụ thể, không viết chung chung — Chữ dùng đúng bối cảnh:**
   - Cho phép sử dụng mọi template chữ phù hợp với bối cảnh kịch bản: phân đoạn chương (`section-title`), mốc thời gian (`date-stamp`), luận điểm (`thesis-marker`), trích dẫn (`quote-card`), so sánh đối đầu (`versus-split`), từ khóa dồn dập (`keyword-burst`), số liệu thống kê (`stat-counter`), đặt vấn đề (`typewriter-reveal`)...
   - **Quy tắc nội dung cụ thể & Nhãn phụ (sublabel):**
     + Nội dung chính, nhãn chính, nhãn phụ phải phản ánh thông tin cụ thể, xác thực của phân đoạn kịch bản đó. Tuyệt đối không dùng cụm từ chung chung, sáo rỗng ("sự kiện quan trọng", "thay đổi vĩnh viễn", "thông tin chi tiết", "bối cảnh", "ghi chú"...).
     + **Không thêm nhãn phụ chung chung không có ý nghĩa:** Nhãn phụ (`sublabel`) chỉ được phép thêm nếu nó có ý nghĩa rõ ràng và thực sự bổ sung ý nghĩa cho nội dung chính (như số liệu, tỷ lệ %, mốc thời gian, địa danh, thuộc tính then chốt). Nếu không có thông tin bổ sung rõ ràng và có ý nghĩa thì **bắt buộc bỏ trống** (`""`), phần tử rỗng sẽ tự ẩn trên video.
   - Không chép lại nguyên cả câu thoại dài lên màn hình nếu không cần thiết; chữ xuất hiện để cô đọng ý chính, nhấn mạnh trực quan.

5. **(Đã bỏ — CEO 13/11/2026, DEC-267):** Luật "chữ tối đa 3,0 giây, tự ẩn sau 3 giây" đã bỏ
   vì không khớp thực tế: engine render mỗi part thành 1 ảnh tĩnh duy nhất, chữ ở suốt part,
   không có cơ chế tự ẩn giữa part. Logic tạo video hiện tại (chữ ở suốt part, part ngắn thì
   chữ ngắn) là đúng. Thời lượng chữ theo độ dài part (xem `docs/TEXT_DENSITY_RULES.md`); thời
   gian chờ sau part chia đoạn (vd `thesis-marker`) theo luật nghỉ nhấn CHỐT 04/11/2026
   (pauseAfterMs = 2000ms). Riêng hiệu ứng gõ chữ: chỉ nội dung chính của `typewriter-reveal`
   có hiệu ứng gõ chữ, nhãn chính/phụ dùng hiệu ứng khác phù hợp.

6. **CHIẾN LƯỢC 1: Chuỗi liệt kê dồn dập (Rapid-Fire Enumeration Montage) [ƯU TIÊN HÀNG ĐẦU]:**
   - Một video editor chuyên nghiệp **không bao giờ ngắt câu thuần túy ở dấu chấm câu**. Dấu chấm câu chỉ là quy ước ngữ pháp, còn nhịp dựng phim phụ thuộc vào **thực thể trực quan**, **mạch cảm xúc** và **nhịp thở hình ảnh**.
   - Khi câu văn chứa một chuỗi các danh từ, vũ khí, phương tiện, địa danh hoặc thực thể cụ thể nối tiếp nhau:
     *Ví dụ gốc:* `"Chiến tranh kéo dài buộc các bên phải bổ sung đạn dược, tên lửa, xe bọc thép và hệ thống phòng không."*
   - **Cách chia của Editor chuyên nghiệp:**
     1. **Đoạn dẫn nhập / ngữ cảnh nền**:
        + Lời thoại: `"Chiến tranh kéo dài buộc các bên phải bổ sung"`
        + B-roll: `useBroll: false` (giữ trọn vẹn cảnh nền chính / master shot).
        + Vai trò: Tạo **khoảng thở thị giác (Visual Breathing Room)**, chuẩn bị tâm thế cho người xem trước khi bước vào chuỗi hình ảnh dồn dập.
     2. **Chuỗi Montage từng thực thể (Rapid Cutaway Beats)**:
        Mỗi danh từ được tách thành một `voicePart` riêng biệt tương ứng đúng nhịp phát âm:
        + Đoạn 1: `"đạn dược,"` $\rightarrow$ `templateId: "cutaway-standard"`, `inputs: {}` (không chữ che màn hình), `sfx: {"id": "whoosh_fast", "offsetSec": 0.0, "volume": 0.7}`, `keywords: ["đạn dược quân sự", "kho đạn pháo"]`.
        + Đoạn 2: `"tên lửa,"` $\rightarrow$ `templateId: "cutaway-standard"`, `inputs: {}`, `sfx: {"id": "whoosh_fast", "offsetSec": 0.0, "volume": 0.7}`, `keywords: ["tên lửa hành trình", "phóng tên lửa"]`.
        + Đoạn 3: `"xe bọc thép"` $\rightarrow$ `templateId: "cutaway-standard"`, `inputs: {}`, `sfx: {"id": "whoosh_fast", "offsetSec": 0.0, "volume": 0.7}`, `keywords: ["xe bọc thép chiến đấu", "xe tăng thiết giáp"]`.
        + Đoạn 4: `"và hệ thống phòng không."` $\rightarrow$ `templateId: "cutaway-standard"`, `inputs: {}`, `sfx: {"id": "heavy_thud_slam", "offsetSec": 0.0, "volume": 0.35}`, `keywords: ["hệ thống phòng không", "radar phòng không"]`.
        *(Món cuối cùng dùng SFX nặng hơn như `heavy_thud_slam` để chốt hạ chuỗi liệt kê).*
   - **Hiệu quả thị giác**: Các B-roll xuất hiện liên tiếp chớp nhoáng theo nhịp đọc của phát thanh viên. Người xem nhìn thấy chuỗi hình ảnh/video tư liệu thật đổi liên tục, tạo cảm giác phim tài liệu cực kỳ đắt giá, chuyên nghiệp như BBC/Discovery.

---

## 2. Nhịp điệu và Động cơ Cắt cảnh (Pacing & Motion Choreography)

- **Thời lượng tối đa của một cú máy đơn (Single Shot Limit):**
  - Cảnh trầm lắng / triết lý / kết luận: tối đa 4.0s – 4.5s.
  - Cảnh phân tích / giải thích: 2.5s – 3.2s.
  - Cảnh cao trào / hành động / liệt kê: 1.2s – 2.0s.
- **Luân phiên góc máy (Focal Length & Shot Scale Variety):**
  - Luân phiên đa dạng các cự ly máy quay: **Extreme Wide (Toàn cảnh) $\rightarrow$ Medium Action (Trung cảnh) $\rightarrow$ Close-up / Macro (Cận cảnh & Cực cận)**.

---

## 3. Âm thanh và Ma trận SFX (Sound Design Matrix)

Mọi hiệu ứng thị giác và chuyển cảnh đều được đồng bộ với 8 file âm thanh chuẩn trong thư viện `data/sfx/`. Volume ghi theo **tuyến tính (0–1)**, không dùng dB. Quy ước: **1 SFX/part trong plan** — beat cần 2 tiếng (vd riser + thud ở section-title) thì tách thành 2 part (riser ở part trước, thud ở part này), không ghi 2 SFX vào cùng 1 part. SFX nặng (thud/slam/boom) mixer cắt về **0.4** bất kể plan khai cao hơn — ví dụ ghi **0.35**.

Bảng quy đổi dB → tuyến tính (để đọc tài liệu cũ): 0dB = 1.0 · −2dB ≈ 0.79 · −3dB ≈ 0.71 · −5dB ≈ 0.56 · −6dB ≈ 0.5 · −8dB ≈ 0.4.

1. **Chuyển chương (`section-title`):** `heavy_thud_slam.mp3` tại $t + 0.05s$ (0.35). (Riser `cinematic_riser.mp3` nếu cần thì đặt ở part trước, không gộp vào part này.)
2. **Câu hỏi mở đầu (`typewriter-reveal`):** `typing_fast.mp3` tại $t + 0.1s$ (0.56).
3. **Băng giấy luận điểm (`thesis-marker`, `quote-card`):** `paper_rip.mp3` tại thời điểm thẻ xuất hiện (0.71).
4. **Nhãn từ khóa dập nhanh (`keyword-burst`):** `punch_impact.mp3` (nếu có 2 tag: nhân đôi tại $t=0.05s$ và $t=0.38s$).
5. **HUD / Dữ liệu / Bản đồ (`tactical-banner`, `stat-counter`):** `radar_glitch.mp3` (0.56).
6. **Chuyển cảnh nhanh giữa 2 visual beats:** `whoosh_fast.mp3` (0.4).
7. **Cao trào / Cháy nổ / Đại cảnh chấn động:** `boom_sub_impact.mp3` (0.35 — SFX nặng, mixer cắt về 0.4).

---

## 4. Nhất quán Phong cách (Stylistic Discipline)

- **1 Video = 1 Genre Palette + 1 Color Grade + Tối đa 2 Accent Colors.**
- Không dùng SFX hoạt hình, tiếng chuông rẻ tiền. Chỉ dùng 8 âm thanh điện ảnh chuẩn trong thư viện studio.
- Đồ họa hiển thị rõ ràng, tương phản tốt, thẩm mỹ tinh tế và phục vụ cho nội dung kịch bản.
