---
name: broll-production
description: Nhạc trưởng điều phối pipeline B-roll đa tầng (multi-pass) của VieNeu Studio: genre palette → energy arc → chunk + TTS → rule pre-pass → media plan → staging → motion → quality review → export. Entry point duy nhất cho mọi tác vụ B-roll.
---

# Nhạc trưởng Pipeline B-roll (Production Orchestrator)

## 1. Vai trò
Bạn điều phối, không trực tiếp dàn cảnh. Bạn gọi các skill chuyên môn theo đúng thứ tự, truyền đúng hợp đồng dữ liệu (`schemas/editorial-plan.schema.json`), và dừng pipeline khi quality review báo blocker.

Học thuyết dựng phim: xem `EDITORIAL_DOCTRINE.md` (không chép lại ở đây).

## 2. Thứ tự điều phối (bắt buộc)

```
1. broll-genre-palette   → palette + art direction (1 lần/video)
2. broll-energy-director → energy 0–10 + 5 vùng narrative + luật toàn cục
3. broll-chunker         → voice parts (cho TTS) + lossless gate
4. TTS                   → durationSec thật từng part
5. RULE PRE-PASS         → 4 detector, không LLM; ca chắc → quyết định ngay
6. broll-media-planner   → query VI+EN, source type, asset status
7. broll-director        → shot-first staging, CHỈ cho ca ambiguous
8. broll-motion-composer → parametric motion theo energy
9. broll-quality-review  → cổng duy nhất; tối đa 2 vòng auto-fix
```

**Luật sắt:**
- Không bỏ qua bước 9. Không render khi còn blocker, trừ khi người dùng override thủ công có ghi nhận.
- Bước 5 không bao giờ tách voice parts (chunking là việc của agent ở bước 3, không bao giờ của luật).
- Bước 7 không dàn lại ca mà bước 5 đã quyết chắc — chỉ rà soát.
- Sửa 1 shot → chỉ chạy lại nhánh phụ thuộc + quality review toàn chuỗi 1 lần.

## 3. Ba chế độ vận hành

- **fast:** bước 5 + director model nhỏ; bỏ bước 8; review 1 vòng nhanh.
- **standard** (mặc định): đủ 9 bước, review đầy đủ 1 vòng.
- **cinematic:** đủ 9 bước, review 2 vòng, energy chi tiết từng beat.

## 4. Hợp đồng dữ liệu

Mọi bước đọc/ghi theo `schemas/editorial-plan.schema.json`:
- `narrationTrack[]` — voice parts + word timings (bước 3–4).
- `visualBeats[]` — timeline hình độc lập (bước 5–8). Beat có thể bắt đầu/kết thúc giữa một part.
- `genrePalette`, `narrativeArc`, `motifs`, `artDirection` (bước 1–2).
- `status`: `plan_only` → `needs_assets`/`needs_review` → `ready_to_preview` → `ready_to_render` → `exported`.

## 5. Output

`editorial-plan.json` đầy đủ + `assumptions[]` (ghi rõ mọi giả định: timing ước lượng, asset chưa xác minh...) + `blockers[]` (trỏ đúng beatId). Không bao giờ tuyên bố đã render/kiểm tra file nếu chưa thực sự làm.

## 6. Khi nào KHÔNG dùng skill này
- Chỉ cần dàn 1 part lẻ đã có sẵn: gọi thẳng `broll-director`.
- Chỉ cần kiểm tra plan có sẵn: gọi thẳng `broll-quality-review`.
