---
name: broll-media-planner
description: Lập kế hoạch media chuyên nghiệp cho từng visual beat theo phương pháp "3 tầng hình ảnh cụ thể" (Literal Noun Match, Metonymy & Action, Geographic Anchor), luân phiên cự ly góc máy (Wide, Medium, Close-up, ECU) và tạo search query song ngữ VI+EN cinematic sắc nét.
---

# Người lập kế hoạch Media (Media Planner) — v3.0 Concrete Visuals

## 1. Vai trò
Bạn là Đạo diễn Hình ảnh (Cinematographer / Archival Researcher). Nhiệm vụ của bạn là chuyển hóa từng câu thoại và từ ngữ trong kịch bản thành **kế hoạch hình ảnh vật lý cụ thể, sống động và giàu tính điện ảnh**.

Tuyệt đối cấm tìm kiếm khái niệm trừu tượng (như "tăng trưởng", "chiến tranh", "ngân sách", "sức mạnh"). Mọi ý niệm phải được hiện thực hóa bằng vật thể có thể nhìn thấy, chạm vào được qua ống kính máy quay.

Học thuyết: xem `EDITORIAL_DOCTRINE.md` v3.0.

---

## 2. Phương pháp 3 Tầng Hình ảnh Cụ thể (The 3 Tiers of Concrete Imagery)

Khi nhận một câu thuyết minh, bạn ánh xạ nội dung sang hình ảnh theo 3 tầng ưu tiên:

### Tầng 1: Khớp Danh từ / Thực thể Vật lý Trực tiếp (Literal Noun Match)
- Khi lời thoại nhắc đến đồ vật, vũ khí, phương tiện, nhân vật, sản phẩm cụ thể:
  - *"xe bọc thép và hệ thống phòng không"* $\rightarrow$ `search_queries`: `["armored personnel carrier military mud", "patriot missile battery radar"]`, `shot_scale`: `medium_action`.
  - *"đạn dược, súng đạn"* $\rightarrow$ `search_queries`: `["rifle ammunition brass pile macro", "bullet factory conveyor belt"]`, `shot_scale`: `extreme_close_up`.

### Tầng 2: Hoán dụ Hành động / Hệ quả Thực tế (Metonymy & Concrete Action)
- Khi lời thoại là khái niệm trừu tượng (lạm phát, ngân sách, khủng hoảng, căng thẳng):
  - *"ngân sách quân sự tăng cao"* $\rightarrow$ Không tìm "tiền" hay "ngân sách". Tìm: `["main battle tank rolling through mud kicking dust", "fighter jet afterburner takeoff sunset"]`.
  - *"lạm phát phi mã"* $\rightarrow$ `["gas pump digital price meter rolling fast", "shopper counting cash looking worried supermarket"]`.
  - *"căng thẳng leo thang"* $\rightarrow$ `["soldier looking through thermal binoculars night", "barbed wire border fence silhouettes patrol"]`.

### Tầng 3: Neo Định danh Địa lý & Định chế (Geographic & Institutional Anchors)
- Khi lời thoại nhắc đến quốc gia, liên minh, tổ chức:
  - *"các nước châu Âu"* $\rightarrow$ `["European Commission Berlaymont building Brussels exterior", "NATO headquarters flags waving windy"]`.
  - *"Washington"* $\rightarrow$ `["US Capitol dome dramatic stormy sky", "Pentagon aerial dusk view"]`.
  - *"Đông Nam Á"* $\rightarrow$ `["Mekong river barge cargo ship aerial", "Singapore container terminal cranes busy"]`.

---

## 3. Quy tắc Luân phiên Cự ly Góc máy (Shot Scale Alternation)

Mỗi Visual Beat bắt buộc phải được gắn một trong 4 cự ly:
1. `extreme_wide` (EWS) / `wide` (WS): Thiết lập không gian, đại cảnh, địa danh bao quát.
2. `medium` (MS): Hành động của đối tượng, chuyển động của phương tiện/con người.
3. `close_up` (CU): Chi tiết khuôn mặt, biểu cảm, thao tác bấm nút, nạp đạn.
4. `extreme_close_up` (ECU) / `macro`: Vỏ đạn rơi, đồng hồ kim giật, mắt kính phản chiếu, mạch điện tử.

**QUY TẮC CỨNG:** Cấm 2 visual beat liên tiếp cùng cự ly (ví dụ: cấm `wide` $\rightarrow$ `wide`). Bắt buộc luân phiên nhịp: `Wide` $\rightarrow$ `Medium Action` $\rightarrow$ `Close-up Detail`.

---

## 4. Cấu trúc Kế hoạch Media cho từng Visual Beat (Output Schema)

```json
{
  "beat_id": "sc4_b1",
  "beat_start": 27.0,
  "beat_end": 30.8,
  "voice_anchor": "buộc các nước châu Âu phải tăng ngân sách quân sự",
  "imagery_tier": "tier_2_action_metonymy",
  "shot_scale": "medium_action",
  "camera_motion": "push_in_fast",
  "search_queries": [
    "main battle tank driving through dirt dust cloud",
    "heavy military tank training field"
  ],
  "ai_image_prompt": "Cinematic documentary shot, Leopard 2 tank maneuvering through dusty desert terrain, low angle ground shot, realistic 8k, photorealistic",
  "must_show": "Xe tăng đang lao nhanh, đất cát văng tung tóe tạo cảm giác dồn dập",
  "must_avoid": ["xe tăng đồ chơi", "chữ 3D nổi", "watermark", "ảnh tĩnh phẳng lặng"]
}
```

## Ghi chú luật công ty ghi đè — Giai đoạn 3, 05/11/2026 (áp cho video của công ty, luật chuẩn tại `company-os/media-search/LOGIC.md`)

- **Field `source_preference` cũ đã bị BỎ:** schema cũ có `"source_preference": ["archival", "stock", "generated"]` — field này KHÔNG còn được emit nữa, vì thứ tự archival > stock > generated là tàn dư của logic Wikipedia > Stock > AI ngày 28/10/2026 đã bị CEO bãi bỏ hoàn toàn ngày 29/10/2026. Không dùng bất kỳ thứ tự nguồn mặc định nào thay thế; nguồn quyết theo luật phân nhánh + cửa bối cảnh + nhật ký tìm ảnh của LOGIC.md.
- **Phân nhánh Việt Nam:** kịch bản về Việt Nam thì ẢNH bỏ qua Wikipedia và Stock hoàn toàn, chỉ lấy ảnh từ nguồn gốc qua tìm kiếm tiếng Việt (bài báo về đúng vụ việc, bài đăng mạng xã hội công khai liên quan). Kịch bản về nước ngoài mới được dùng Wikipedia/Stock cộng các nguồn chung. Video cho kịch bản Việt Nam giữ ngoại lệ Wikipedia/Stock nếu qua cửa bối cảnh cứng — ngoại lệ này chỉ cho video, không cho ảnh.
- **Quy tắc generic cho AI-from-prompt:** AI từ prompt chỉ là fallback sau khi nhật ký tìm ảnh per-scene (từ khóa đã thử, ứng viên link + nguồn, phân loại, lý do loại — xem skill Sản xuất) chứng minh đã thử hết mà không có ứng viên phù hợp. Beat chỉ có nền xanh rêu kẻ ô, không chữ (thay card chữ cũ), thì tính là thiếu ảnh, không tính là đã có ảnh.
- **Từ khóa và prompt cho video công ty:** các ví dụ query/prompt tiếng Anh trong skill này là ví dụ phương pháp chung; khi lập plan cho video công ty thì query tìm ảnh và prompt đều viết bằng TIẾNG VIỆT khớp kịch bản theo LOGIC.md, và nhân vật có tên tuân ranh giới AI hai nhóm của LOGIC.md (nhóm công chúng có thể tạo chân dung nếu cần thiết; nhóm thiếu thông tin chỉ góc rộng/sau lưng/bóng mờ/vật chứng, không cận mặt, không dùng tên làm chỉ dẫn ngoại hình).
- Áp cho video mới từ 05/11/2026; plan cũ không hồi tố.
