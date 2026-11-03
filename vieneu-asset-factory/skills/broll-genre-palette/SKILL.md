---
name: broll-genre-palette
description: Nhận diện thể loại video và khóa ngôn ngữ thị giác toàn video cho VieNeu Studio theo 6 nhóm chủ đề chuyên sâu (Địa chính trị/Quân sự, Kinh tế/Tài chính, Lịch sử, Công nghệ/AI, Khoa học/Tự nhiên, Tội phạm/Đời sống). Khóa bảng màu, SFX palette và phong cách quay chụp tư liệu phù hợp bối cảnh.
---

# Bảng màu Thể loại (Genre Palette) — v3.1 Multi-Genre Cinema

## 1. Vai trò
Bạn phân tích kịch bản và **khóa ngôn ngữ điện ảnh (Visual & Audio Language) cho toàn bộ video trong một lượt đọc duy nhất**.
Mọi tầng tiếp theo (Planner, Director, Motion Composer, Quality Gate) tuân thủ Palette được khóa ở đây.

Nguyên tắc: Xem `EDITORIAL_DOCTRINE.md` v3.1.
- **Tỷ lệ chữ và template hiển thị linh hoạt phù hợp với bối cảnh kịch bản**, không khóa cứng hạn ngạch.
- Cho phép xuất hiện các cảnh có chữ liên tiếp nếu phục vụ mục tiêu diễn đạt nội dung.

---

## 2. Sáu Nhóm Thể loại Chuyên sâu (The 6 Core Genres)

### 1. Địa chính trị / Quân sự (Geopolitics & Military)
- **Visual Tone:** Gritty documentary, desaturated military grade, khói bụi, tương phản cao, góc máy UAV hoặc kính ngắm vệ tinh.
- **Palette & Accents:** Primary: `red` (#c81e1e), Secondary: `steel-blue` (#2563eb), Neutral: `charcoal-black` (#090b10).
- **Template Thường Dùng:** `section-title` (bumper đỏ), `tactical-banner` (tọa độ/vị trí), `keyword-burst` (thực thể/vũ khí), `versus-split`.
- **SFX Core:** `heavy_thud_slam.mp3`, `cinematic_riser.mp3`, `punch_impact.mp3`, `radar_glitch.mp3`, `whoosh_fast.mp3`, `boom_sub_impact.mp3`.

### 2. Kinh tế / Tài chính / Vĩ mô (Finance & Economics)
- **Visual Tone:** Sleek corporate, sàn giao dịch hiện đại, cảng biển logistics, đồ thị phân tích vi mô, ánh sáng kính phản chiếu.
- **Palette & Accents:** Primary: `gold` (#f59e0b), Positive: `green` (#10b981), Negative: `crimson` (#ef4444), Neutral: `deep-navy` (#0a0f1d).
- **Template Thường Dùng:** `stat-counter` (con số % tăng trưởng), `tactical-banner` (chỉ số kinh tế), `section-title`, `thesis-marker`.
- **SFX Core:** `radar_glitch.mp3`, `typing_fast.mp3`, `heavy_thud_slam.mp3`, `whoosh_fast.mp3`.

### 3. Lịch sử / Nhân vật / Cổ trang (History & Biography)
- **Visual Tone:** Warm sepia / Thủy mặc tối, tông vàng đồng / gỗ mun, chân dung tư liệu lưu trữ, tranh khắc gỗ, bản đồ cổ có nếp gấp.
- **Palette & Accents:** Primary: `amber-gold` (#d97706), Accent: `burgundy` (#831843), Neutral: `parchment` (#1c1917).
- **Template Thường Dùng:** `typewriter-reveal` (câu nói nhân vật / mở đầu), `date-stamp` (mốc năm cụ thể), `quote-card`, `thesis-marker`.
- **SFX Core:** `paper_rip.mp3`, `typing_fast.mp3`, `cinematic_riser.mp3`, `heavy_thud_slam.mp3`.

### 4. Công nghệ / AI / Không gian (Tech, Cyber & Space)
- **Visual Tone:** Cyberpunk / Clean sci-fi, phòng thí nghiệm vi mạch, server room, render hạt 3D, neon xanh lam / cyan sắc nét.
- **Palette & Accents:** Primary: `cyan` (#06b6d4), Accent: `electric-purple` (#8b5cf6), Neutral: `space-black` (#030712).
- **Template Thường Dùng:** `tactical-banner` (HUD thông số chip/AI), `stat-counter`, `keyword-burst`, `section-title`.
- **SFX Core:** `radar_glitch.mp3`, `whoosh_fast.mp3`, `cinematic_riser.mp3`, `punch_impact.mp3`.

### 5. Khoa học / Tự nhiên / Môi trường (Science & Nature)
- **Visual Tone:** National Geographic style, đại cảnh thiên nhiên hoang sơ, macro cực cận sinh vật biển/rừng rậm, chuyển động timelapse mượt mà.
- **Palette & Accents:** Primary: `emerald` (#059669), Accent: `sunburst` (#eab308), Neutral: `earth-dark` (#111827).
- **Template Thường Dùng:** `section-title` phân đoạn, `stat-counter` đo lường diện tích/loài, `typewriter-reveal`.
- **SFX Core:** `whoosh_fast.mp3`, `boom_sub_impact.mp3`, `cinematic_riser.mp3`.

### 6. Đời sống / Tội phạm / Phá án (True Crime & Society)
- **Visual Tone:** Film Noir, ánh sáng tương phản gắt (Chiaroscuro), đèn neon phản chiếu mặt đường ướt đêm, hồ sơ chứng cứ, camera an ninh CCTV.
- **Palette & Accents:** Primary: `blood-red` (#dc2626), Warning: `amber` (#f59e0b), Neutral: `asphalt` (#020617).
- **Template Thường Dùng:** `typewriter-reveal` (thời khắc vụ án), `keyword-burst` (đầu mối điều tra), `date-stamp`, `quote-card`.
- **SFX Core:** `heavy_thud_slam.mp3`, `paper_rip.mp3`, `typing_fast.mp3`, `cinematic_riser.mp3`.

---

## 3. Cấu trúc Output JSON Duy nhất

```json
{
  "primary": "geopolitics_military",
  "secondary": "technology",
  "accents": {
    "primary": "red",
    "secondary": "steel-blue",
    "neutral": "charcoal-black"
  },
  "sfx_palette": [
    "heavy_thud_slam.mp3",
    "cinematic_riser.mp3",
    "punch_impact.mp3",
    "whoosh_fast.mp3"
  ],
  "motionBias": "fast-cut-camera-push",
  "artDirection": {
    "styleLock": "Gritty cinematic documentary, high-contrast, dust kicking up, realistic military lighting",
    "forbidden": ["watermark", "cartoonish faces", "ai-glitch extra limbs", "low-res textures"],
    "shotList": ["Drone wide aerial view", "Close-up tank treads dirt track", "Tactical map overlays"]
  }
}
```
