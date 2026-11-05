#!/usr/bin/env python3
"""Chọn nhạc nền (BGM) cho project theo mood/chủ đề.

    python3 select_bgm.py <project_id> [--mood <mood>] [--list-moods]

- Không có --mood: agent suy mood từ topic (tin tức/địa chính trị -> news,
  ...), in gợi ý; --mood ép mood cụ thể.
- Ghi lựa chọn vào broll-plan.json -> {"bgm": {...}} để render_draft mix.

Mood hợp lệ = thư mục trong bgm/ (xem bgm_catalog.json).
"""
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from filename import atomic_write_text  # noqa: E402  (Giai đoạn 5)

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
if FACTORY == _SYMLINK_FACTORY:
    # B46 (06/11/2026, lệnh CEO, lựa chọn A): dấu vết khi dùng nhầm
    # root cũ — đường symlink ~/workspace/asset-factory đã lỗi thời,
    # factory chuẩn là layout repo (bin/../).
    print(f"  warn: FACTORY resolve qua symlink cu {_SYMLINK_FACTORY} — kiem tra lai duong factory", file=sys.stderr)

BGM_DIR = FACTORY / "bgm"

# từ khóa topic -> mood
MOOD_KEYWORDS = [
    (("chiến tranh", "xung đột", "địa chính trị", "quân sự", "tấn công",
      "khủng hoảng", "tranh chấp", "bầu cử", "chính trị"), "news"),
    (("hài", "cười", "vui nhộn", "tấu hài", "meme"), "funny"),
    (("thư giãn", "êm dịu", "thiền", "ngủ", "chill", "thiên nhiên"), "calm"),
    (("kịch tính", "gay cấn", "hành động", "bom tấn"), "dramatic"),
    (("truyền cảm hứng", "động lực", "thành công", "vượt khó"), "inspirational"),
    (("kinh dị", "hồi hộp", "bí ẩn", "điều tra"), "suspense"),
    (("buồn", "chia tay", "mất mát", "tưởng niệm"), "sad"),
    (("tươi vui", "năng động", "du lịch", "ẩm thực", "lễ hội"), "upbeat"),
]


def load_catalog():
    cat = BGM_DIR / "bgm_catalog.json"
    if not cat.exists():
        print("chưa có bgm/bgm_catalog.json", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(cat.read_text(encoding="utf-8"))
    except Exception as exc:
        # Giai đoạn 5: catalog hỏng -> báo rõ, không crash trần.
        print(f"bgm_catalog.json hỏng: {exc}", file=sys.stderr)
        sys.exit(1)


def guess_mood(topic: str) -> str:
    t = topic.lower()
    for kws, mood in MOOD_KEYWORDS:
        if any(k in t for k in kws):
            return mood
    return "news"  # mặc định cho nội dung tin tức


def main() -> int:
    if "--list-moods" in sys.argv:
        catalog = load_catalog()
        if not isinstance(catalog, list):
            print("bgm_catalog.json hỏng: cấp cao phải là list", file=sys.stderr)
            return 1
        moods = sorted({m for t in catalog if isinstance(t, dict) for m in t.get("moods", [])})
        print("moods:", ", ".join(moods))
        return 0
    if len(sys.argv) < 2:
        print("usage: select_bgm.py <project_id> [--mood <mood>] [--list-moods]",
              file=sys.stderr)
        return 2
    pid = sys.argv[1]
    catalog = load_catalog()
    if not isinstance(catalog, list):
        print("bgm_catalog.json hỏng: cấp cao phải là list", file=sys.stderr)
        return 1
    proj = FACTORY / "projects" / pid
    try:
        plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
        inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"không đọc được plan/input của {pid}: {exc}", file=sys.stderr)
        return 1
    if not isinstance(plan, dict) or not isinstance(inp, dict):
        print(f"plan/input của {pid} hỏng: phải là dict", file=sys.stderr)
        return 1

    if "--mood" in sys.argv:
        try:
            mood = sys.argv[sys.argv.index("--mood") + 1]
        except IndexError:
            print("--mood thiếu giá trị", file=sys.stderr)
            return 2
    else:
        mood = plan.get("mood") or guess_mood(inp.get("topic", ""))

    cands = [t for t in catalog if isinstance(t, dict) and mood in t.get("moods", [])]
    if not cands:
        print(f"không có track nào mood '{mood}'", file=sys.stderr)
        return 1
    # chọn ngẫu nhiên theo seed project để ổn định
    track = random.Random(f"bgm-{pid}-{mood}").choice(cands)
    # Giai đoạn 5: track thiếu key bắt buộc -> lỗi rõ, không crash trần
    # KeyError và không ghi plan.bgm dở.
    _missing = [k for k in ("id", "file", "title", "artist") if k not in track]
    if _missing:
        print(f"track BGM mood '{mood}' thiếu key: {', '.join(_missing)} "
              f"(track={track}) — sửa bgm_catalog.json rồi chạy lại",
              file=sys.stderr)
        return 1
    # B30 (06/11/2026, lệnh CEO, lựa chọn A): track trong catalog nhưng
    # file nhạc không có trên đĩa thì LỖI, không ghi plan — trước đây
    # vẫn in BGM-OK và lỗi chỉ lộ ở preflight/render/assemble sau đó.
    _bgm_file = BGM_DIR / track["file"]
    if not _bgm_file.is_file():
        print(f"track BGM '{track['id']}' thiếu file nhạc trên đĩa: {_bgm_file} "
              f"— copy file vào bgm/ hoặc sửa bgm_catalog.json rồi chạy lại",
              file=sys.stderr)
        return 1
    plan["bgm"] = {"id": track["id"], "mood": mood, "file": track["file"],
                   "title": track["title"], "artist": track["artist"],
                   "attribution": track.get("attribution", "")}
    # Giai đoạn 5: ghi plan tạm rồi rename — crash giữa chừng không để
    # lại broll-plan.json bị cắt (plan là gốc sự thật của cả pipeline).
    atomic_write_text(proj / "broll-plan.json",
                      json.dumps(plan, ensure_ascii=False, indent=1))
    print(f"BGM-OK mood={mood} track={track['title']} - {track['artist']}")
    if track.get("attribution"):
        print(f"  ghi công: {track['attribution']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
