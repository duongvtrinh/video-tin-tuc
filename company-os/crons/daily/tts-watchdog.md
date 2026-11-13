---
id: tts-watchdog
title: Watchdog TTS mỗi 30 phút
enabled: true
mode: task
schedule:
  kind: interval
  timezone: Asia/Ho_Chi_Minh
  every: 30m
owner: goal:vieneu-media-company-bootstrap
---
Watchdog TTS (DEC-273 recovery, CEO 13/11/2026): mỗi lần chạy, thực thi script ~/workspace/company-os/tts-watchdog.sh (bash, không tham số). Script tự kiểm tra http://127.0.0.1:8000/health: khỏe thì im lặng exit 0; lỗi thì cài lại unit systemd từ bản chuẩn trong ~/workspace/company-os/systemd/vieneu-tts.service (khi /etc mất sau thay máy) rồi restart service, tối đa 2 lần thử. Chỉ báo về chat chính khi: script exit 1 (TTS vẫn không lên sau 2 lần thử — ghi rõ giờ + dòng cuối của ~/workspace/company-os/tts-watchdog.log) hoặc khi script đã phải khởi động lại TTS (ghi rõ giờ khôi phục). Khi khỏe thì không nhắn gì. Không chạm việc khác, không sửa MEMORY.md; ghi chú ca chạy vào nhật ký ngày ~/memory/YYYY-MM-DD.md chỉ khi có hành động khôi phục hoặc lỗi.
