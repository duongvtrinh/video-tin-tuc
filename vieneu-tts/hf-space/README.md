---
title: VieNeu TTS API
emoji: 🔊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# VieNeu TTS API trên HuggingFace Spaces

API tổng hợp giọng nói tiếng Việt (VieNeu-TTS v3 Nano, ONNX CPU, 24kHz).
Chạy miễn phí trên HuggingFace Spaces, gọi được từ bất cứ đâu qua HTTPS.

## Cách deploy (5 phút)

1. Tạo tài khoản miễn phí tại https://huggingface.co (nếu chưa có).
2. Vào https://huggingface.co/new-space :
   - **Space name:** `vieneu-tts-api` (hoặc tên tùy ý)
   - **SDK:** chọn **Docker**
   - Bấm **Create Space**.
3. Upload 3 file trong thư mục này lên Space: `Dockerfile`, `requirements.txt`,
   `server.py` (kéo-thả trực tiếp trên trang Files của Space, hoặc git push).
4. (Khuyến nghị) Vào **Settings → Variables and secrets → New secret**,
   thêm secret tên `TTS_API_KEY` với giá trị là mật khẩu tự đặt.
   Khi đó mọi request phải kèm header `X-API-Key` hoặc `?api_key=`.
5. Chờ Space build xong (tab Logs hiện "Running on...", khoảng 5-10 phút
   cho lần đầu vì phải tải model ~270MB vào image).

## Gọi API

URL public của Space có dạng:

```
https://<ten-tai-khoan>-vieneu-tts-api.hf.space
```

Kiểm tra:
```bash
curl https://<ten-tai-khoan>-vieneu-tts-api.hf.space/health
```

Tổng hợp giọng nói (trả về trực tiếp file WAV):
```bash
curl -X POST https://<ten-tai-khoan>-vieneu-tts-api.hf.space/speak \
  -H "Content-Type: application/json" \
  -H "X-API-Key: mat-khau-da-dat" \
  -d '{"text":"Xin chào, đây là VieNeu TTS API.","voice":"Minh Quân","speed":1.0}' \
  --output speech.wav
```

Danh sách giọng: `GET /voices` → 11 giọng (Adam, Ái Hân, Mỹ Duyên, Đức Trí,
Hữu Quân, Xuân Tiên, Mai Anh, Trúc Ly, Anh Khôi, Minh Quân, Mạnh Dũng).

## Lưu ý

- Gói miễn phí: Space sẽ "ngủ" sau một thời gian không dùng; request đầu tiên
  khi vừa thức dậy mất thêm ~30-60 giây (wake + load model), các request sau
  nhanh bình thường.
- Muốn luôn thức: nâng cấp gói PRO của HuggingFace (tùy chọn).
- Muốn chất lượng cao hơn (48kHz): sửa `Dockerfile`, đổi `Vieneu(mode='v3nano')`
  thành `Vieneu()` (bản Turbo, image nặng hơn ~2GB), rồi rebuild.
