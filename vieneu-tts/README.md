# VieNeu TTS API (standalone)

API server độc lập cho **VieNeu-TTS** — tổng hợp giọng nói tiếng Việt từ văn bản,
gọi được từ xa qua HTTP. Không cần cài toàn bộ VieNeu Studio.

- Engine mặc định: **v3 Nano** (ONNX, CPU, 24kHz) — nhẹ, chạy được trên máy yếu,
  11 giọng preset, không cần GPU.
- Có thể chuyển sang **v3 Turbo** (48kHz, chất lượng cao hơn, có voice cloning
  qua package `vieneu`) bằng biến môi trường.

## 1. Cài đặt & chạy

**Windows:** nhấp đúp `start.bat` (tự tạo venv, cài thư viện, chạy server).

**Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Điều kiện tiên quyết (Linux):** gói hệ thống `libsndfile1` (thư viện
`soundfile` cần để ghi WAV — thiếu thì server vẫn lên nhưng request `/speak`
đầu tiên sẽ lỗi; `start.sh` kiểm tra và báo ngay) và gói `python3-venv`
nếu dùng Debian/Ubuntu tối giản.

Lần chạy đầu tiên sẽ tự tải model từ HuggingFace (~vài trăm MB, cần mạng).
Sau đó mở: http://localhost:8000/health

Để chạy nền trên Linux (giữ server sau khi tắt terminal):
```bash
nohup ./start.sh > tts.log 2>&1 &
```

## 2. Cấu hình (biến môi trường)

| Biến | Mặc định | Ý nghĩa |
|---|---|---|
| `VIENEU_MODE` | `v3nano` | `v3nano` (nhẹ) hoặc `turbo` (48kHz, hay hơn) |
| `VIENEU_PRECISION` | `int8` | `int8` (nhanh, nhẹ) hoặc `fp32` (chuẩn nhất, chỉ cho turbo) |
| `VIENEU_VOICE` | `Hữu Quân` | Giọng mặc định khi request không chỉ định (code ưu tiên Hữu Quân rồi mới fallback giọng đầu tiên) |
| `TTS_API_KEY` | _(trống = không cần)_ | Nếu đặt, client phải gửi `X-API-Key` hoặc `?api_key=` |
| `TTS_MAX_CHARS` | `5000` | Giới hạn ký tự mỗi request |
| `PORT` | _(không đọc)_ | Không có tác dụng — server hardcode cổng 8000; muốn đổi cổng thì chạy tay `uvicorn server:app --host 0.0.0.0 --port 9000` thay cho start.sh |

Ví dụ chạy Turbo chất lượng cao:
```bat
set VIENEU_MODE=turbo
set VIENEU_PRECISION=int8
.venv\Scripts\uvicorn server:app --host 0.0.0.0 --port 8000
```

## 3. API

### GET /health
Kiểm tra server + model đã load chưa.
```bash
curl http://localhost:8000/health
```
```json
{"status":"ok","mode":"v3nano","sample_rate":24000,"voices":11,"error":null}
```

### GET /voices
Danh sách giọng đọc có sẵn.
```bash
curl http://localhost:8000/voices
```
```json
{"voices":[{"label":"Minh Quân","id":"Minh Quân"}, ...],"default":"Hữu Quân"}
```

### POST /speak
Tổng hợp giọng nói. **Trả về trực tiếp file WAV** (đồng bộ, không cần polling).

```bash
curl -X POST http://localhost:8000/speak \
  -H "Content-Type: application/json" \
  -d '{"text":"Xin chào, đây là VieNeu TTS API.","voice":"Minh Quân","speed":1.0}' \
  --output speech.wav
```

Python:
```python
# cần pip install requests (không có trong requirements.txt)
import requests
r = requests.post("http://SERVER_IP:8000/speak",
                  json={"text": "Xin chào cả nhà!", "voice": "Minh Quân", "speed": 1.0},
                  headers={"X-API-Key": "mat-khau-neu-co-dat"})
open("speech.wav", "wb").write(r.content)
```

Tham số:
| Trường | Kiểu | Mặc định | Ghi chú |
|---|---|---|---|
| `text` | string | _(bắt buộc)_ | Văn bản tiếng Việt (tối đa `TTS_MAX_CHARS` ký tự) |
| `voice` | string | giọng mặc định | Tên/id giọng trong `/voices` |
| `speed` | float | `1.0` | Tốc độ 0.5 – 2.0 |

Response header có thêm `X-Audio-Seconds` (độ dài audio) và `X-Voice`.

## 4. Gọi từ xa (mở cho máy khác gọi vào)

Server mặc định bind `0.0.0.0` nên máy khác trong cùng mạng gọi được qua
`http://IP_CUA_MAY_CHAY_SERVER:8000/speak`.

Muốn gọi qua Internet:
- Cách dễ nhất: dùng **Tailscale** (cài trên cả 2 máy, gọi qua IP 100.x của tailnet,
  không cần mở port router).
- Hoặc mở port 8000 trên router/firewall + đặt `TTS_API_KEY` để bảo vệ.
- Hoặc reverse proxy (nginx/Caddy) + HTTPS nếu dùng lâu dài.

## 5. Yêu cầu hệ thống

- Python 3.10+
- RAM: ~1GB cho Nano, ~2-4GB cho Turbo
- Disk: ~500MB (Nano) / ~2GB (Turbo) cho model + thư viện
- Không cần GPU.

## 6. Clone về Muse khác — hướng dẫn chi tiết

Repo này chỉ chứa **mã nguồn lõi** của VieNeu TTS. Sang Muse khác làm theo
các bước sau:

1. **Clone repo:**
   - Trên Muse mới, đăng nhập GitHub bằng tài khoản có quyền vào repo
     private này (repo này thuộc tài khoản `duongvtrinh`).
   - Clone repo về máy Muse mới (ví dụ vào `~/workspace/vieneu-tts-api/`).
2. **Cài đặt:**
   - Chạy `./start.sh` (Linux) hoặc `start.bat` (Windows): script tự tạo
     venv, cài thư viện trong `requirements.txt`, rồi chạy server.
   - Lần chạy đầu tiên sẽ tự tải model từ HuggingFace (cần mạng, vài
     trăm MB với bản Nano). Model cache **không** nằm trong repo nên máy
     mới phải tải lại một lần.
3. **Dùng trực tiếp trong chat (không qua server):**
   - VieNeu TTS chạy thẳng trên máy Muse bằng `tts_cli.py` với venv của
     chính nó, ví dụ:
     ```bash
     .venv/bin/python tts_cli.py --text "Xin chào cả nhà!" --voice "Minh Quân" --speed 1.0 --out out.wav
     ```
   - 11 giọng preset: Minh Quân, Hữu Quân, Ái Hân, Mỹ Duyên, Đức Trí,
     Xuân Tiên, Mai Anh, Trúc Ly, Anh Khôi, Mạnh Dũng, Adam.
   - Giới hạn 5000 ký tự/request. Lần đầu load model từ cache mất ~7 giây,
     RAM ~450MB.
   - **Lưu ý cho VieNeu Asset Factory:** các script `tts_batch.py` và
     `normalize_chunks.py` của factory **phải** chạy bằng venv của TTS
     này (không dùng venv của factory), vì bộ chuẩn hóa giọng đọc
     (sea-g2p) nằm trong venv TTS.
4. **Dùng dạng API server:**
   - Sau `./start.sh`, server chạy ở `http://localhost:8000` với các
     endpoint `/health`, `/voices`, `/speak` như mô tả ở mục 3–4 bên trên.
   - Muốn máy khác gọi vào thì dùng Tailscale hoặc mở port + đặt
     `TTS_API_KEY` như mục 4.

## KHÔNG có trong repo này

- `.venv/` (~896MB) — tạo lại bằng `start.sh` / `start.bat`.
- Model cache — tải lại từ HuggingFace ở lần chạy đầu.
- `briefings/` — file output mẫu (script + WAV), không phải mã nguồn.
- `__pycache__/` — sinh lại khi chạy.
