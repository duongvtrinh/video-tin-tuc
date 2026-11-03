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

_SYMLINK_FACTORY = Path.home() / "workspace" / "asset-factory"
# May goc giu symlink cu (khong doi hanh vi); ban clone monorepo
# khong co symlink thi resolve tu vi tri file script (bin/../).
FACTORY = _SYMLINK_FACTORY if _SYMLINK_FACTORY.exists() else Path(__file__).resolve().parent.parent
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
    return json.loads(cat.read_text(encoding="utf-8"))


def guess_mood(topic: str) -> str:
    t = topic.lower()
    for kws, mood in MOOD_KEYWORDS:
        if any(k in t for k in kws):
            return mood
    return "news"  # mặc định cho nội dung tin tức


def main() -> int:
    if "--list-moods" in sys.argv:
        catalog = load_catalog()
        moods = sorted({m for t in catalog for m in t.get("moods", [])})
        print("moods:", ", ".join(moods))
        return 0
    pid = sys.argv[1]
    catalog = load_catalog()
    proj = FACTORY / "projects" / pid
    plan = json.loads((proj / "broll-plan.json").read_text(encoding="utf-8"))
    inp = json.loads((proj / "input.json").read_text(encoding="utf-8"))

    if "--mood" in sys.argv:
        mood = sys.argv[sys.argv.index("--mood") + 1]
    else:
        mood = plan.get("mood") or guess_mood(inp.get("topic", ""))

    cands = [t for t in catalog if mood in t.get("moods", [])]
    if not cands:
        print(f"không có track nào mood '{mood}'", file=sys.stderr)
        return 1
    # chọn ngẫu nhiên theo seed project để ổn định
    track = random.Random(f"bgm-{pid}-{mood}").choice(cands)
    plan["bgm"] = {"id": track["id"], "mood": mood, "file": track["file"],
                   "title": track["title"], "artist": track["artist"],
                   "attribution": track.get("attribution", "")}
    (proj / "broll-plan.json").write_text(
        json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"BGM-OK mood={mood} track={track['title']} - {track['artist']}")
    if track.get("attribution"):
        print(f"  ghi công: {track['attribution']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
