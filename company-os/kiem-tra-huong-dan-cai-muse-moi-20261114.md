# Kiểm tra hướng dẫn cài Muse mới trên repo GitHub

Ngày kiểm tra: 14/11/2026 (00:05–00:30). Người kiểm tra: Muse (chat chính).
Đối tượng: `BOOTSTRAP.md` (304 dòng) + `company-os/scheduled-tasks-setup.md` (153 dòng) trên repo `duongvtrinh/video-tin-tuc`, HEAD `2a20b90b` (đợt đẩy toàn bộ 13/11/2026 23:41).
Phương pháp: đọc toàn bộ 2 tài liệu; đối chiếu từng bước với máy local và với nội dung thật trên repo (đọc lại file từ repo, diff file mẫu lịch với lịch đang chạy, chạy kiểm chứng lệnh trong venv).

## Kết luận chung: CHƯA ĐẠT — bản cài mới theo đúng hướng dẫn sẽ KHÔNG làm việc đầy đủ

Một tài khoản Muse mới làm đúng từng bước trong hướng dẫn sẽ cài được phần lớn (repo, skill, factory, TTS, app mở được), nhưng sẽ **gãy ở 6 điểm chặn**:

1. Dịch vụ TTS systemd không cài được (file unit không có trên repo).
2. Lịch watchdog TTS không chạy được (script không có trên repo, body lịch gọi đường dẫn local).
3. App Tạo Video không tìm thấy factory (core.ts chỉ nhận 2 đường dẫn local, không nhận đường clone).
4. Preflight dhash lỗi (thiếu imagehash trong requirements.txt).
5. Tải video Facebook lỗi (yt-dlp không có ở đâu cả — requirements.txt không có, venv không có, PATH không có; lỗi này đã gãy cả trên máy local hiện tại).
6. 6/6 file mẫu lịch ngày trên repo đã cũ so với lịch đang chạy (thiếu cổng v3.0, thiếu luật L7, sai tên workbook cũ).

Chi tiết từng điểm ở mục 2. Những phần đã đúng ở mục 3. Đề xuất sửa và điểm cần CEO quyết ở mục 4–5.

## 1. Bức tranh toàn cảnh: layout local khác layout clone

Đây là gốc của phần lớn lỗi. Máy local đặt mọi thứ trực tiếp dưới `~/workspace/`:

- Factory: `~/workspace/vieneu-asset-factory/` (symlink `~/workspace/asset-factory/`)
- Company-os: `~/workspace/company-os/`
- TTS: `~/workspace/vieneu-tts-api/`
- Skill: `~/workspace/custom-skills/`

Hướng dẫn (BOOTSTRAP C1) lại clone repo vào **`~/workspace/video-tin-tuc/`**, mọi thứ nằm trong đó:

- Factory: `~/workspace/video-tin-tuc/vieneu-asset-factory/`
- Company-os: `~/workspace/video-tin-tuc/company-os/`
- TTS: `~/workspace/video-tin-tuc/vieneu-tts/`

Bản thân việc clone vào thư mục con là hợp lý. Vấn đề là **nhiều file vận hành trong repo vẫn viết theo đường dẫn local cũ** (unit systemd, script watchdog, body lịch watchdog, app core.ts), và hướng dẫn không có bước nào nối 2 layout này lại với nhau. Kết quả: file thì có trên repo, nhưng đường dẫn trong file trỏ vào chỗ không tồn tại trên máy clone.

## 2. Các lỗi chặn (theo thứ tự nghiêm trọng)

### Lỗi 1 — File unit systemd TTS không có trên repo (CHẶN dịch vụ TTS)

- `scheduled-tasks-setup.md` viết: "file unit bản chuẩn nằm trong repo tại `company-os/systemd/vieneu-tts.service`" và hướng dẫn chạy `cp ~/workspace/company-os/systemd/vieneu-tts.service /etc/systemd/system/`.
- Kiểm chứng: quét toàn bộ cây repo (373 file, HEAD trước đợt đẩy) + grep đợt đẩy `2a20b90b` (99 file) — **không có file nào tên systemd hay vieneu-tts.service**. Thư mục `company-os/systemd/` chỉ tồn tại ở local.
- Hệ quả: bước "Cài dịch vụ TTS để tự chạy lại khi Muse khởi động lại" không thực hiện được trên máy mới. TTS chỉ chạy bằng nohup/start.sh, chết sau khi thay máy thì không tự sống lại. Watchdog cũng không thể "cài lại unit từ bản chuẩn trong repo" như tài liệu viết.

### Lỗi 2 — Script watchdog TTS không có trên repo (CHẶN lịch watchdog)

- Body lịch `tts-watchdog.md` trên repo gọi `~/workspace/company-os/tts-watchdog.sh`.
- Kiểm chứng: file `company-os/tts-watchdog.sh` chỉ tồn tại ở local (1.629 byte), không có trên repo, không có trong đợt đẩy `2a20b90b`.
- Hệ quả: lịch watchdog tạo xong sẽ gọi script không tồn tại, mỗi 30 phút đều lỗi, TTS sập không ai cứu.

### Lỗi 3 — Unit + script watchdog + body lịch đều hardcode đường dẫn local (CHẶN ngay cả khi đã đẩy file lên repo)

Ngay cả khi đẩy 2 file ở Lỗi 1–2 lên repo nguyên văn, chúng vẫn không chạy trên máy clone vì đường dẫn trong file là đường dẫn local:

- Unit `vieneu-tts.service` (local): `WorkingDirectory=/home/hatch/workspace/vieneu-tts-api`, `ExecStart=/home/hatch/workspace/vieneu-tts-api/.venv/bin/uvicorn ...`, log ra `~/workspace/company-os/tts-service.log`. Máy clone có TTS ở `~/workspace/video-tin-tuc/vieneu-tts/`, không có thư mục `vieneu-tts-api`. Service sẽ fail ngay khi start.
- Script `tts-watchdog.sh` (local): `UNIT_SRC="$HOME/workspace/company-os/systemd/vieneu-tts.service"`, `LOG="$HOME/workspace/company-os/tts-watchdog.log"`. Máy clone không có `~/workspace/company-os/`.
- Body lịch `tts-watchdog.md` (trên repo): gọi `~/workspace/company-os/tts-watchdog.sh` và đọc log `~/workspace/company-os/tts-watchdog.log`. Cùng vấn đề.
- Kết luận: 3 file này phải được viết lại theo đường clone, hoặc hướng dẫn phải thêm bước tạo symlink nối 2 layout. Hiện tại không có bên nào làm việc đó.

### Lỗi 4 — App Tạo Video không tìm thấy factory trên máy clone (CHẶN app)

- `app-tao-video/server/src/priv/core.ts` dòng 18–20:

```
export const FACTORY = existsSync(join(HOME, "workspace/asset-factory"))
  ? join(HOME, "workspace/asset-factory")
  : join(HOME, "workspace/vieneu-asset-factory");
```

- App chỉ nhận 2 đường dẫn local, không nhận đường clone `~/workspace/video-tin-tuc/vieneu-asset-factory/`. Mọi đường dẫn phái sinh (`PROJECTS`, `BIN`, `VENV_PY`) đều trỏ sai trên máy clone.
- BOOTSTRAP Bảng B mục 11 viết "Đường dẫn factory: Đã ghi sẵn trong repo (core.ts tự phân giải) — tài khoản mới không sửa đường dẫn". Câu này sai với máy clone: core.ts không phân giải được đường clone.
- Hệ quả: bước kiểm chứng C5 (tạo project thử → đọc lại → xóa) sẽ gãy vì app không thấy thư mục `projects/` và không thấy Python venv của factory. App mở được giao diện nhưng không làm việc được.
- Lưu ý: script của factory thì không bị lỗi này — chúng tự phân giải (`FACTORY = symlink nếu có, không thì thư mục chứa script`). Chỉ app là hardcode 2 đường dẫn.

### Lỗi 5 — requirements.txt thiếu yt-dlp và imagehash (CHẶN preflight + tải video Facebook)

- `vieneu-asset-factory/requirements.txt` (local và repo giống hệt nhau) chỉ có 5 gói: Pillow, numpy, weasyprint, underthesea, websocket-client. Không có yt-dlp, không có imagehash.
- BOOTSTRAP C3.1 viết: "yt-dlp đã nằm trong requirements.txt của factory (chốt yt-dlp==2026.10.26)" và yêu cầu kiểm chứng `.venv/bin/yt-dlp --version`. Cả hai đều sai:
  - `which yt-dlp` trên máy local: không có (rc=1).
  - `.venv/bin/yt-dlp`: không tồn tại.
  - `import yt_dlp` trong venv factory: ModuleNotFoundError.
  - Tức là yt-dlp hiện không có ở bất kỳ đâu trên máy local. Script `dl_facebook_video.py` (tìm yt-dlp bằng `shutil.which`) sẽ báo "yt-dlp chưa cài" — chức năng tải video Facebook đang gãy cả trên máy local, không chỉ trên máy mới.
- imagehash: có trong venv local (4.3.2, import được, `preflight.py` dòng 1286 dùng cho dhash theo L8) nhưng không có trong requirements.txt. Máy mới cài đúng `pip install -r requirements.txt` sẽ thiếu imagehash → preflight phần dhash lỗi ImportError khi chạy.
- Nguyên nhân có thể: venv local từng được dựng lại từ requirements.txt (sau thay máy) nên yt-dlp rơi mất; imagehash được cài tay sau đó (13/11) mà không ghi lại vào requirements.txt.

### Lỗi 6 — 6/6 file mẫu lịch ngày trên repo đã cũ so với lịch đang chạy (lịch mới cài sẽ chạy luật cũ)

Đối chiếu body file mẫu trên repo với body lịch đang chạy trên máy local (đã chuẩn hoá placeholder UUID/email/mã chi nhánh về dạng `{{...}}` trước khi diff):

| File mẫu | So với lịch đang chạy | Nội dung cũ cụ thể |
|---|---|---|
| bot-hoc-hoi-2000.md | KHÁC | Còn tên workbook cũ "Video HQ — Trụ sở Muse" (đã đổi thành "Video HQ — Tin Tức" ngày 13/11) |
| coo-scan-0300.md | KHÁC, thiếu cả bước | Thiếu toàn bộ Bước 9 (kiểm 5 cổng v3.0 "Kịch bản như người", quyết CEO 12/11); Bước 7/8 còn wording cũ |
| prod-pipeline-0500.md | KHÁC | Thiếu luật đọc lại L7 (13/11, phương án B); bước 7 còn wording cũ |
| prod-pipeline-1400.md | KHÁC | Giống 0500: thiếu L7, bước 7 cũ |
| scout-scan-0600.md | KHÁC | Lệch wording ở bước 0/2/3/6 so với bản đang chạy |
| scout-scan-1300.md | KHÁC | Lệch wording ở bước 0/2/3/6 (đã có tên workbook mới, nhưng vẫn lệch các bước) |
| tts-watchdog.md | KHỚP | Đúng 759 ký tự, khớp hoàn toàn |

- Vi phạm đúng quy tắc bảo trì trong chính `scheduled-tasks-setup.md`: "Body trong file mẫu phải giống hệt body của lịch đang chạy, trừ 7 placeholder" và "mỗi khi sửa body một lịch đang chạy bằng cron.update thì cập nhật luôn file mẫu tương ứng trong repo trong cùng lần sửa".
- Hệ quả: máy mới cài bộ lịch từ file mẫu sẽ chạy luật cũ — sai tên workbook, thiếu cổng kiểm v3.0, thiếu luật đọc lại L7. Đây là lỗi âm thầm: lịch vẫn chạy, không báo lỗi, nhưng chạy sai luật hiện hành.
- Lưu ý: 6 file mẫu có placeholder đúng ({{CHAT_ID_...}}, {{EMAIL_KHAI_BAO}}, {{MA_CHI_NHANH}}), 0 giá trị riêng chi nhánh, 0 UUID hardcode — phần này đúng. Chỉ nội dung luật là cũ.

## 3. Những lỗi nhỏ hơn (không chặn, nhưng hướng dẫn viết không đủ để làm theo)

### 3.1. File manifest của app không tồn tại — bước C5 không làm được như viết

- BOOTSTRAP C5 yêu cầu "đối chiếu theo manifest" và ghi chú "(đề xuất file manifest trong repo — ĐỀ XUẤT chờ duyệt)". Trên repo chỉ có 2 manifest khác (`vieneu-asset-factory/docs/BGM_MANIFEST.md`, `SFX_MANIFEST.md`), không có manifest của app.
- Hệ quả: máy mới không có danh sách chuẩn để đối chiếu file nguồn app. Bước kiểm chứng C5 chỉ còn lại phần thử bằng tay (mở app, tạo/xóa project thử).

### 3.2. Script check-prereqs.sh không tồn tại — bước C0 chỉ làm được bằng tay

- BOOTSTRAP C0 đề xuất script `check-prereqs.sh` trong repo và ghi rõ "ĐỀ XUẤT chờ duyệt, chưa có trong repo". Các lệnh kiểm tra tay (ffmpeg, python3, bun, libsndfile, df, mạng HuggingFace) thì có liệt kê đủ trong mục, nên C0 vẫn làm được — chỉ mất công làm tay từng lệnh.

### 3.3. Script install.sh của TTS không tồn tại — bước C2 chỉ có start.sh

- BOOTSTRAP C2 đề xuất script chỉ-cài-đặt `install.sh` ("ĐỀ XUẤT chờ duyệt, chưa có trong repo"). Hiện chỉ có `start.sh` (gộp cài + chạy). `start.sh` đã kiểm chứng là tốt: dùng đường tương đối (`cd "$(dirname "$0")"`), tự tạo venv, cài requirements, kiểm tra libsndfile rồi mới chạy server — chạy đúng trên mọi đường clone. Chỉ thiếu đúng tính năng tách riêng bước cài đặt mà hướng dẫn mong muốn.

### 3.4. Font Anton: hướng dẫn không cho URL hay lệnh cụ thể

- BOOTSTRAP C3 chỉ viết "cài font Anton từ Google Fonts vào ~/.fonts và chạy fc-cache", không có URL tải hay lệnh cụ thể. File font không có trong repo. Máy local có font tại `~/.fonts/google-artistic/Anton-Regular.ttf`.
- Máy mới vẫn làm được (tìm Anton trên Google Fonts rồi tải), nhưng hướng dẫn không dẫn tới đúng 1 kết quả duy nhất.

### 3.5. Không có bước tạo goal bootstrap

- E4 và `scheduled-tasks-setup.md` yêu cầu mọi lịch có owner `goal:vieneu-media-company-bootstrap`, nhưng không có bước nào trong hướng dẫn bảo tài khoản mới tạo goal đó (hay tạo bằng cách nào). Agent mới phải tự suy ra.

## 4. Những phần đã đúng (kiểm chứng đạt)

- **Repo đủ 4 thành phần + README + BOOTSTRAP** (C1): app-tao-video, company-os, vieneu-asset-factory, vieneu-tts đều có trên repo, đúng nhánh main, private.
- **5 skill đúng**: media-coo, media-scout, media-video-production, media-video-tech-qa, thumbnail-xep-lop đều có trên repo (company-os/skills/), media-topic-scoring đã đóng không copy — đúng C4.
- **Factory đầy đủ**: bin, templates, docs, sfx đủ 8 file mp3, bgm đủ 24 track + README + bgm_catalog.json, neutral-bg image/video — đều có trên repo, khớp máy local.
- **TTS cài được**: requirements.txt của vieneu-tts đầy đủ (vieneu, onnxruntime, fastapi, uvicorn, numpy, scipy, soundfile, python-multipart, pydantic); start.sh chạy đúng trên mọi đường clone.
- **Script factory tự phân giải đường dẫn**: mọi script bin/*.py đều có fallback `FACTORY = symlink nếu có, không thì thư mục chứa script` — chạy đúng trên máy clone. Chỉ app là ngoại lệ (Lỗi 4).
- **File mẫu lịch sạch placeholder**: 6 file ngày có đúng placeholder, 0 email chi nhánh, 0 UUID hardcode; tts-watchdog.md không có placeholder (đúng như tài liệu).
- **Kết nối D1–D6**: hướng dẫn chi tiết, có bước kiểm chứng thật từng kết nối (GitHub, Drive, Sheets, Pixabay/Pexels qua vault với đúng placement/hosts, Facebook, Gmail). Phần này đã chạy thật ngày 11/11 và viết đúng.
- **E2/E5**: tạo 5 chat nhân viên và kiểm chứng 7 điểm trước ca COO_TASKS đầu tiên đều có đủ, rõ ràng.
- **E5 điểm 5 (tài sản nhị phân)**: sfx 8 + bgm 24 đã nằm trong git, clone là có — kiểm chứng đúng.

## 5. Đề xuất sửa (CEO quyết từng nhóm)

### Nhóm A — Sửa để bản cài mới chạy được (bắt buộc trước khi hướng dẫn được dùng)

1. **Đẩy `company-os/systemd/vieneu-tts.service` + `company-os/tts-watchdog.sh` lên repo** (2 file hiện chỉ có ở local).
2. **Viết lại 3 file theo đường clone** (hoặc theo đường tương đối/không hardcode): unit đổi `vieneu-tts-api` thành `video-tin-tuc/vieneu-tts` và log thành `video-tin-tuc/company-os/tts-service.log`; script watchdog đổi `UNIT_SRC`/`LOG` sang đường clone; body `tts-watchdog.md` đổi đường gọi script sang đường clone. Lưu ý: đổi xong thì máy local hiện tại (đang dùng đường local) phải được cập nhật theo, hoặc giữ 2 bản — cần quyết.
3. **App**: hoặc thêm 1 bước tạo symlink vào C3/C5 (`ln -s ~/workspace/video-tin-tuc/vieneu-asset-factory ~/workspace/asset-factory`), hoặc sửa `core.ts` để nhận thêm đường clone. Symlink là sửa ít nhất (1 dòng hướng dẫn), sửa core.ts là sạch nhất về lâu dài (app tự nhận cả 2 layout).
4. **requirements.txt của factory**: thêm `yt-dlp==2026.10.26` và `imagehash==4.3.2 --no-deps` (đúng phiên bản đã chốt). Đồng thời cài lại yt-dlp vào venv local (hiện đang thiếu cả trên máy local).
5. **Đồng bộ 6 file mẫu lịch ngày trên repo với lịch đang chạy** (copy body live đã chuẩn hoá placeholder về file mẫu), rồi kiểm chứng lại bằng diff.

### Nhóm B — Sửa để hướng dẫn đầy đủ (nên làm cùng đợt)

6. Thêm bước tạo goal `vieneu-media-company-bootstrap` trước E4.
7. Thêm URL/lệnh cụ thể để tải font Anton vào C3.
8. Tạo file manifest của app (hoặc sửa C5 bỏ yêu cầu đối chiếu manifest, chỉ giữ kiểm chứng bằng tay).
9. Tạo `check-prereqs.sh` và `install.sh` cho TTS (2 đề xuất đang treo), hoặc sửa hướng dẫn bỏ phần đề xuất và ghi rõ làm tay.

### Nhóm C — Quyết về layout (quyết 1 lần, ảnh hưởng mọi chi nhánh)

10. **Chuẩn layout**: giữ nguyên clone vào `~/workspace/video-tin-tuc/` + sửa file theo đường clone (Nhóm A), hay đổi hướng dẫn sang 1 chuẩn khác? Lưu ý: mọi chi nhánh khác đang dùng hướng dẫn này sẽ chịu cùng các lỗi trên nếu họ clone theo đúng hướng dẫn — đây không phải lỗi riêng của chi nhánh này.

## 6. Điểm CEO cần quyết

1. Nhóm A (5 mục bắt buộc): có duyệt sửa và đẩy lên repo không? (Có / Không — nếu có, tôi sửa local rồi trình duyệt đẩy riêng theo luật GitHub)
2. Nhóm B (4 mục nên làm): làm cùng đợt A hay để sau?
3. Nhóm C: chọn hướng nào — sửa file theo đường clone, hay thêm bước symlink, hay sửa core.ts?
4. yt-dlp thiếu trên máy local: có cài lại ngay vào venv factory không? (Có / Để sau — lưu ý chức năng tải video Facebook đang gãy)
