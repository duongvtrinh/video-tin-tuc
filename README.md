# vieneu-media-company

Monorepo hệ thống dựng video của công ty truyền thông một người.
Repo RIÊNG TƯ — chỉ Muse của cùng tài khoản mới có quyền đọc.

## Bắt đầu từ đâu

Đọc `BOOTSTRAP.md` trước, làm đúng thứ tự trong đó. Mỗi bước có kiểm
chứng; bước nào fail thì dừng và báo, không tự chế, không bỏ qua.
Chi nhánh mới clone repo về thì làm theo hướng dẫn từng bước ở
`BOOTSTRAP.md` §C1 (lấy repo về máy, layout clone + 3 symlink).

## Cấu trúc

- `vieneu-tts/` — giọng đọc VieNeu TTS (`tts_cli.py`, `server.py`,
  `start.sh`, `requirements.txt`).
- `vieneu-asset-factory/` — pipeline dựng video (`bin/` script,
  `lib/`, `templates/`, `skills/`, `prompts/`, `docs/`,
  `PIPELINE.md`, `ABBR_DICT.md`) + `sfx/` (8 file `.mp3`) + `bgm/` (24 track).
- `app-tao-video/` — source App Tạo Video (client/src: `App.tsx` + `lib.ts` + 11 component theo tab; server/src: `priv/` 9 module + `privileged.ts` + `actions.ts` + `schema.ts` + `script-prompt.ts` kèm test `bun:test`; migration drizzle 0001–0003). Khi chạy thật là artifact — tạo lại bằng artifact tools theo `BOOTSTRAP.md` §6; bản build `dist/` không nằm trong repo (build lại khi tạo artifact).
- `company-os/` — logic vận hành: 7 skill trong `skills/`
  (`media-coo`, `media-scout`, `media-video-production`,
  `media-video-tech-qa`, `thumbnail-xep-lop`,
  `template_render_assertion`, `measure_motion_on_lossless_frames`)
  + tài liệu
  (`media-search/LOGIC.md`, `google-sheet-spec.md`, checklist,
  `code-fix-20261029/REPORT.md`).

- Tài sản nhị phân ĐÃ nằm trong git từ 04/11/2026, clone là có:
  `vieneu-asset-factory/sfx/` 8 file `.mp3` + `bgm/` 24 track
  (+ `bgm_catalog.json`, `README.md`). Connector snapshot-push chỉ
  nhận UTF-8 nên không push được file nhị phân — mỗi lần đẩy kiểm tra
  lại cây `sfx/`/`bgm/` trên remote; bản dự phòng trên Drive chỉ dùng
  để khôi phục khi thiếu (BOOTSTRAP.md §7).

## Những gì KHÔNG có trong repo này (cố ý)

- State và dữ liệu: `projects/`, MP4, thư mục work, backup, log,
  dữ liệu Sheet/Drive, `MEMORY.md` và nhật ký (thông tin cá nhân).
- Bí mật: mật khẩu, token, API key — liên kết lại qua connector /
  Secure Vault, không bao giờ ghi vào git.
- App `app-tao-video`: là artifact, không phải repo git — tạo lại
  bằng artifact tools theo `BOOTSTRAP.md` §6.
