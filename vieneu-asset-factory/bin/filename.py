#!/usr/bin/env python3
"""Single source of truth cho quy tắc đặt tên file media.

Dùng chung cho các script factory: assemble_project.py, tts_batch.py,
render_draft.py, preflight.py, thumbnail.py. App (server/src/privileged.ts)
ĐÃ dùng hợp đồng này từ đợt C1 (01/11/2026): mọi tên media app tạo mới
và duplicateProject đều theo đúng rand6() này, nên render_draft tìm
thấy đúng file (hết clip đen/sai hình do lệch tên).
    python3 filename.py <project_id> img <order>            -> seg_1_483920.jpg
    python3 filename.py <project_id> broll <order> <partIdx> -> broll_seg_1_part_2_771122.jpg
    python3 filename.py <project_id> voice <order>           -> voice_seg_1_483920.wav
    python3 filename.py <project_id> partwav <order> <partIdx> -> parts/part_1_2_771122.wav
"""
import hashlib
import sys


def rand6(*parts: str) -> str:
    h = hashlib.md5("|".join(parts).encode("utf-8")).hexdigest()
    return "".join(c for c in h if c.isdigit())[:6].ljust(6, "0")


def main() -> int:
    pid, kind = sys.argv[1], sys.argv[2]
    if kind == "img":
        o = sys.argv[3]
        print(f"seg_{o}_{rand6(pid, 'img', o)}.jpg")
    elif kind == "broll":
        o, p = sys.argv[3], sys.argv[4]
        print(f"broll_seg_{o}_part_{p}_{rand6(pid, 'broll', o, p)}.jpg")
    elif kind == "voice":
        o = sys.argv[3]
        print(f"voice_seg_{o}_{rand6(pid, 'seg', o)}.wav")
    elif kind == "partwav":
        o, p = sys.argv[3], sys.argv[4]
        print(f"parts/part_{o}_{p}_{rand6(pid, 'part', o, p)}.wav")
    else:
        print(f"unknown kind: {kind}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
