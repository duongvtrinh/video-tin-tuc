#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tìm ảnh/video có sẵn theo thứ tự ưu tiên đã chốt 28/10/2026:
  1. Wikipedia / Wikimedia Commons (tiếng Việt, không cần API key)
  2. Stock: Pixabay / Pexels (từ khóa TIẾNG ANH, cần API key qua biến môi trường)
  3. Tạo bằng AI (chỉ khi 2 lớp trên không có ứng viên đạt ngưỡng)

Logic chặt chẽ (xem LOGIC.md cùng thư mục):
  - Lọc bằng metadata trước, chỉ soi trực quan ứng viên đầu bảng.
  - Ảnh: khớp từ khóa + hướng dọc 9:16 + độ phân giải đủ cắt 720x1280 + giấy phép trắng.
  - Video: khớp từ khóa + thời lượng GẦN NHẤT với thời lượng voice part + hướng dọc + giấy phép trắng.
  - Không bao giờ ghi một file stock/Wikipedia là "tư liệu thật" của một sự kiện cụ thể;
    với nhân vật/sự kiện thiếu tư liệu, kết quả chỉ là minh họa chung chung.

Cách dùng:
  python3 search_media.py wikimedia --summary "phòng xử án" --media-type image
  python3 search_media.py wikimedia --summary "phòng xử án" --media-type video --duration 8.6
  python3 search_media.py stock --en-keywords "courtroom" --media-type video --duration 8.6
    (không có PIXABAY_API_KEY / PEXELS_API_KEY thì lớp stock báo SKIPPED, không bịa kết quả)

API key KHÔNG được ghi trong file, không in ra log. Chỉ đọc từ biến môi trường.
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path
import urllib.parse
import urllib.request

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "Muse-Media-Search/1.0 (one-person-media-company; test 2026-10-28)"

# Giấy phép được chấp nhận trên Wikimedia Commons cho video bàn giao.
# Loại: NC (cấm thương mại), ND (cấm phái sinh), GFDL-only (ràng buộc nặng, tránh).
LICENSE_ALLOW = ("CC0", "CC BY", "CC-BY", "PUBLIC DOMAIN", "PD-")
LICENSE_DENY = ("NC", "ND", "GFDL", "FAIR USE", "NON-FREE", "COPYRIGHTED")

# Stopword tiếng Việt tối thiểu, chỉ để tách từ khóa, không dùng để suy diễn nội dung.
# Thêm nhóm từ máy quay / dàn cảnh (góc, rộng, lia...) vì chúng không phải khái niệm cần tìm.
VI_STOPWORDS = {
    "và", "của", "là", "một", "các", "những", "đã", "đang", "sẽ", "cho", "với",
    "tại", "trong", "theo", "khi", "đến", "từ", "cả", "này", "đó", "thì", "mà",
    "không", "có", "được", "về", "như", "để", "ra", "lên", "xuống", "qua", "bị",
    "do", "hay", "nếu", "rất", "cũng", "chỉ", "nên", "vì", "sau", "trước",
    "ngày", "thứ", "ba", "xin", "dùng", "nào", "gì", "làm", "thành", "ở",
    "góc", "rộng", "phía", "xa", "cận", "toàn", "cảnh", "lia", "chậm", "quay",
    "máy", "khung", "dọc", "hình", "ảnh", "video", "minh", "họa",
}

# Cụm khái niệm linh hoạt (sửa 28/10/2026 theo lệnh CEO: tìm kiếm cần linh hoạt).
# BÀI HỌC GỐC 28/10/2026: metadata của Wikimedia Commons phần lớn là tiếng Anh,
# tìm đúng cụm tiếng Việt "phòng xử án" trả về 0 kết quả, "cân công lý" trả về ảnh
# không liên quan, trong khi "courtroom" và "gold bars" trả về đúng khái niệm.
# BÀI HỌC MỚI 28/10/2026 (Vinspeed): tóm tắt "Đoàn tàu cao tốc chạy trên cầu cạn"
# trả về 0 ứng viên, không phải vì không có ảnh tàu, mà vì bảng khái niệm cũ
# không có khái niệm tàu, và script chỉ thử một khái niệm đầu tiên rồi dừng.
# Trong khi đó Commons có ảnh tàu tốc độ cao dưới các cụm "high speed train",
# "high-speed railway", còn cụm Việt "đường sắt tốc độ cao" trả về 0 file,
# "tàu cao tốc" trả về 20 file nhưng đầu bảng lẫn tàu, bản đồ, tàu thủy.
# Vì vậy mỗi ý đồ hình ảnh là một CỤM gồm nhiều cụm Việt đồng nghĩa +
# nhiều cụm Anh tương đương, và script phải thử HẾT các cụm trong nhóm,
# gộp kết quả, chấm theo bất kỳ cụm nào trong nhóm, rồi mới kết luận
# lớp đó không có file. Một cụm không ra không có nghĩa là nhóm đó không có.
# Tên riêng / tên dự án / tên tàu (VinSpeed, Velaro Novo...) KHÔNG tự động
# gắn vào cụm chung: chúng chỉ được thử khi Production đưa vào
# --extra-keywords, vì "VinSpeed" không phải đồng nghĩa của "tàu cao tốc"
# nói chung, và Commons hiện tại tìm "VinSpeed" cũng trả về 0 file ảnh.
CONCEPT_CLUSTERS = [
    {"id": "courtroom", "vi": ["phòng xử án", "bục thẩm phán", "khu vực bị cáo"],
     "en": ["courtroom"]},
    {"id": "courthouse", "vi": ["tòa án"],
     "en": ["courthouse", "court building"]},
    {"id": "gold", "vi": ["vàng", "thỏi vàng", "két vàng"],
     "en": ["gold bars", "gold ingots", "gold vault"]},
    {"id": "scales_of_justice", "vi": ["cân công lý"],
     "en": ["scales of justice", "Lady Justice", "justice statue"]},
    {"id": "living_room", "vi": ["phòng khách"],
     "en": ["living room"]},
    {"id": "bills", "vi": ["hóa đơn"],
     "en": ["bills documents", "bills", "invoices"]},
    {"id": "smartphone", "vi": ["điện thoại"],
     "en": ["smartphone", "mobile phone"]},
    {"id": "empty_chair", "vi": ["ghế trống"],
     "en": ["empty chair"]},
    # Nhóm đường sắt tốc độ cao, thêm 28/10/2026 sau vụ Vinspeed.
    {"id": "high_speed_train", "vi": ["tàu cao tốc", "đường sắt tốc độ cao",
                               "tàu tốc độ cao", "đường sắt cao tốc"],
     "en": ["high speed train", "high-speed train", "high speed railway",
            "high-speed railway", "bullet train"]},
    {"id": "railway", "vi": ["đường sắt", "tuyến đường sắt"],
     "en": ["railway", "railroad", "railway line"]},
    {"id": "train_station", "vi": ["nhà ga", "ga đường sắt", "ga tàu"],
     "en": ["train station", "railway station"]},
    {"id": "viaduct", "vi": ["cầu cạn", "cầu vượt", "cầu đường sắt"],
     "en": ["viaduct", "elevated railway", "railway bridge"]},
    {"id": "construction", "vi": ["công trường", "thi công", "đang xây"],
     "en": ["construction site", "construction"]},
    {"id": "bridge_girder", "vi": ["dầm cầu", "dầm bê tông"],
     "en": ["bridge girder", "concrete girder"]},
    # Nhóm chiến sự Ukraine, thêm 29/10/2026 cho video Pokrovsk.
    {"id": "military_convoy", "vi": ["xe quân sự", "đoàn xe quân sự", "quân đội"],
     "en": ["military convoy", "military vehicles", "army vehicles"]},
    {"id": "battlefield_smoke", "vi": ["khói chiến trường", "mù khói", "cột khói", "khói"],
     "en": ["battlefield smoke", "war smoke", "smoke battlefield"]},
    {"id": "riverside_town", "vi": ["thị trấn ven sông", "thị trấn bên sông"],
     "en": ["riverside town", "river town"]},
    {"id": "meeting_room", "vi": ["phòng họp", "bàn họp", "phòng họp báo"],
     "en": ["conference room", "meeting room", "press conference"]},
    {"id": "government_building", "vi": ["tòa nhà chính phủ", "điện Kremlin", "Kremlin"],
     "en": ["government building", "Kremlin"]},
    {"id": "winter_city", "vi": ["chung cư mùa đông", "tuyết", "mùa đông"],
     "en": ["winter apartment building", "snow city", "winter city"]},
    {"id": "dirt_road", "vi": ["đường đất", "dấu xích xe"],
     "en": ["dirt road", "country road"]},
    {"id": "conference_hall", "vi": ["trung tâm hội nghị", "hành lang hội nghị"],
     "en": ["conference center", "convention center"]},
    {"id": "sunrise_field", "vi": ["bình minh trên cánh đồng", "cánh đồng"],
     "en": ["sunrise field", "sunrise countryside"]},
]

def concept_clusters(summary):
    """Trả về DANH SÁCH cụm phát hiện trong tóm tắt, theo thứ tự cụm đã chốt,
    không chỉ một cụm đầu tiên. Một cảnh có thể chứa 2 ý đồ hình ảnh
    (vd "tàu cao tốc chạy trên cầu cạn" vừa là tàu vừa là cầu cạn), và cả hai
    đều phải được thử, vì ảnh phù hợp có thể nằm ở cụm thứ hai."""
    low = summary.lower()
    found = []
    for cluster in CONCEPT_CLUSTERS:
        if any(phrase in low for phrase in cluster["vi"]):
            found.append(cluster)
    return found


def parse_extra_keywords(extra):
    """Tách --extra-keywords 'VinSpeed, Velaro Novo' thành danh sách cụm,
    giữ nguyên thứ tự, bỏ trùng, bỏ rỗng. Tên riêng giữ nguyên hoa/thường
    khi gọi API, nhưng chấm điểm không phân biệt hoa/thường."""
    if not extra:
        return []
    seen, out = set(), []
    for part in str(extra).split(","):
        q = part.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            out.append(q)
    return out


def cluster_phrases(summary, extra_keywords=None):
    """Mọi cụm được phép chấm điểm cho một cảnh: tất cả cụm Việt + Anh của
    mọi cụm phát hiện, cộng thêm từ khóa bổ sung (tên riêng/dự án/địa điểm).
    Một ứng viên khớp BẤT KỲ cụm nào trong danh sách này đều được tính điểm,
    không bắt buộc khớp đúng cụm đầu tiên."""
    phrases = []
    for cluster in concept_clusters(summary):
        phrases.extend(cluster["vi"])
        phrases.extend(cluster["en"])
    phrases.extend(parse_extra_keywords(extra_keywords))
    seen, out = set(), []
    for p in phrases:
        if p.lower() not in seen:
            seen.add(p.lower())
            out.append(p)
    return out


def build_queries(summary, limit_queries=12, extra_keywords=None):
    """Tạo truy vấn linh hoạt theo cụm, không theo từ đầu câu.
    Thứ tự: từ khóa bổ sung TRƯỚC (tên riêng/dự án là cụ thể nhất, nếu có
    file đúng dự án thì đó là lựa chọn tốt nhất, còn không thì rơi xuống
    cụm chung), rồi cụm Việt của mọi cụm phát hiện, rồi cụm Anh tương đương.
    Không còn lấy 3 từ đầu / 6 từ đầu của câu làm query, vì 3 từ đầu thường
    là "góc rộng phòng..." và đã cho ra ảnh cây, bản đồ không liên quan
    trong test cũ. Nếu không phát hiện cụm nào và không có từ khóa bổ sung,
    trả về danh sách rỗng để lớp đó báo NO_CLUSTER rõ ràng, thay vì chạy
    query nhiễu rồi trả về 0 một cách khó hiểu."""
    queries = []
    queries.extend(parse_extra_keywords(extra_keywords))
    for cluster in concept_clusters(summary):
        queries.extend(cluster["vi"])
        queries.extend(cluster["en"])
    seen, out = set(), []
    for q in queries:
        if q and q.lower() not in seen:
            seen.add(q.lower())
            out.append(q)
    return out[:limit_queries]


def _verdict(total, media_type, aspect, duration, full_match):
    """Cổng ACCEPT chung (sửa 29/10/2026, code-fix, audit D-M1/D-M2):
    điểm chỉ là một phần — ACCEPT còn đòi hỏi:
    - khớp ĐỦ cụm khái niệm (khớp nửa cụm 0.6 hoặc 1 token 0.3 thì tối đa
      CONSIDER, dù cộng điểm đủ 70 — tiền lệ: "gold vault" ACCEPT 76.2
      nhưng là họa tiết vàng trên mặt tiền tòa nhà, không phải két vàng);
    - ảnh ngang rõ ràng (aspect > 1.0) thì tối đa CONSIDER — trước đây
      cổng này chỉ có cho video, ảnh ngang 4000x3000 vẫn ACCEPT 86.4;
    - video ngang rõ ràng hoặc không biết thời lượng: tối đa CONSIDER
      (cổng cũ, giữ nguyên).
    full_match=True chỉ khi keyword_score == 1.0 (khớp nguyên cụm)."""
    blocked = (not full_match)
    if aspect and aspect > 1.0:
        blocked = True
    if media_type == "video" and duration is None:
        blocked = True
    if total >= 70 and not blocked:
        return "ACCEPT"
    return "CONSIDER" if total >= 50 else "REJECT"


def _slug_only_match(phrase, matched, url_text, other_text):
    """True khi mọi bằng chứng khớp đều chỉ nằm trong slug URL, không nằm
    trong metadata mô tả khác. Pexels video API không trả title/tags/
    description, nên slug là bằng chứng yếu — ứng viên chỉ khớp nhờ slug
    thì tối đa CONSIDER, phải soi khung thật rồi mới dùng."""
    url_text = (url_text or "").lower()
    other_text = (other_text or "").lower()
    if not matched:
        return False
    if any(m.lower() in other_text for m in matched):
        return False
    return all(m.lower() in url_text for m in matched)


def keyword_score_phrase(summary, haystack, extra_keywords=None):
    """Chấm khớp khái niệm bằng CỤM, không bằng từ đơn rời rạc, và chấm theo
    BẤT KỲ cụm nào trong nhóm, không chỉ cụm đầu tiên.
    - 1.0 nếu một cụm Việt, cụm Anh hoặc từ khóa bổ sung xuất hiện nguyên cụm
      trong tiêu đề/mô tả/danh mục.
    - 0.6 nếu không có cụm nguyên vẹn nhưng có >=50% token của MỘT cụm
      (vd "gold" + "ingot" cho "gold ingots", chấp nhận số ít/số nhiều).
      Token của các cụm khác nhau KHÔNG cộng dồn: "gold" từ cụm vàng +
      "train" từ cụm tàu không được tính là khớp một khái niệm.
    - 0.3 nếu chỉ có 1 token của một cụm.
    - 0.0 nếu không có gì: loại ngay, dù ảnh dọc và nét đến đâu."""
    phrases = cluster_phrases(summary, extra_keywords)
    for phrase in phrases:
        if phrase and phrase.lower() in haystack:
            return 1.0, [phrase]
    # Token fallback theo từng cụm riêng, lấy cụm khớp tốt nhất.
    best_ratio, best_matched = 0.0, []
    for phrase in phrases:
        tokens = sorted(set(phrase.lower().split()))
        if not tokens:
            continue
        words = set(re.findall(r"[a-zÀ-ỹ]+", haystack))
        words_norm = {w.rstrip("s") for w in words} | words
        matched = [t for t in tokens if t.rstrip("s") in words_norm
                   or t in words]
        ratio = len(matched) / len(tokens) if tokens else 0.0
        if ratio > best_ratio:
            best_ratio, best_matched = ratio, matched
    if best_ratio >= 0.5:
        return 0.6, best_matched
    if best_matched:
        return 0.3, best_matched
    return 0.0, []


def license_ok(license_name):
    if not license_name:
        return False, "unknown"
    name = license_name.upper()
    if any(d in name for d in LICENSE_DENY):
        return False, license_name
    if any(a in name for a in LICENSE_ALLOW):
        return True, license_name
    return False, license_name


def commons_search(query, media_type, per_query=20):
    """Gọi Wikimedia Commons API. Trả về danh sách file thô (chưa chấm điểm)."""
    filetype = "video" if media_type == "video" else "bitmap|drawing"
    params = {
        "action": "query",
        "format": "json",
        "formatversion": "2",
        "generator": "search",
        "gsrsearch": f"filetype:{filetype} {query}",
        "gsrnamespace": "6",
        "gsrlimit": str(per_query),
        "prop": "imageinfo|categories",
        "iiprop": "url|size|mime|extmetadata|metadata",
        "cllimit": "20",
    }
    url = COMMONS_API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    pages = (data.get("query") or {}).get("pages") or []
    return pages


def extract_duration(page):
    """Lấy thời lượng video (giây) từ metadata của Commons, nếu có."""
    info = (page.get("imageinfo") or [{}])[0]
    for item in info.get("metadata") or []:
        if item.get("name") in ("duration", "length"):
            try:
                return float(item.get("value"))
            except (TypeError, ValueError):
                pass
    # Một số file video ghi duration trong extmetadata dạng chuỗi.
    ext = info.get("extmetadata") or {}
    for key in ("Duration", "Length"):
        val = (ext.get(key) or {}).get("value")
        if val:
            m = re.search(r"([\d.]+)", str(val))
            if m:
                return float(m.group(1))
    return None


def score_candidate(page, media_type, target_duration, summary_text="",
                    extra_keywords=None):
    info = (page.get("imageinfo") or [{}])[0]
    title = page.get("title", "")
    desc = ""
    ext = info.get("extmetadata") or {}
    desc = re.sub(r"<[^>]+>", " ", (ext.get("ImageDescription") or {}).get("value", ""))
    cats = " ".join(c.get("title", "") for c in page.get("categories") or [])
    haystack = f"{title} {desc} {cats}".lower()

    # Phủ định trong tiêu đề: "No scales of justice" chứa cụm nhưng ảnh KHÔNG phải
    # cân công lý. Loại ngay nếu tiêu đề bắt đầu bằng no/not + bất kỳ cụm nào
    # trong nhóm, không chỉ cụm đầu tiên.
    if summary_text:
        for _phrase in cluster_phrases(summary_text, extra_keywords):
            if _phrase and (f"no {_phrase.lower()}" in title.lower()
                            or f"not {_phrase.lower()}" in title.lower()):
                return None
    # Chấm bằng cụm khái niệm (keyword_score_phrase), không chấm từ đơn rời.
    keyword_score, matched = keyword_score_phrase(
        summary_text, haystack, extra_keywords) if summary_text else (0.0, [])
    if keyword_score <= 0:
        return None  # không khớp khái niệm nào -> loại ngay, dù dọc và nét đến đâu.

    width = info.get("width") or 0
    height = info.get("height") or 0
    aspect = (width / height) if height else 0.0
    target_aspect = 9 / 16  # 0.5625, khung dọc 720x1280
    # Điểm hướng dọc: càng gần 9:16 càng cao; ảnh ngang bị trừ nặng vì cắt dọc mất nhiều.
    aspect_score = max(0.0, 1.0 - abs(aspect - target_aspect) / 1.0) if aspect else 0.0
    if aspect > 1.0:  # ngang rõ ràng
        aspect_score *= 0.4
    # Điểm độ phân giải: đủ cắt 720x1280 (chiều cao >= 1280 khi cắt dọc, hoặc chiều rộng >= 720).
    if media_type == "image":
        res_score = 1.0 if (height >= 1280 and width >= 720) else (0.6 if (height >= 720 and width >= 480) else 0.2)
    else:
        res_score = 1.0 if (height >= 720 and width >= 400) else 0.5

    lic_name = (ext.get("LicenseShortName") or {}).get("value", "")
    ok, lic = license_ok(lic_name)
    if not ok:
        return None  # giấy phép không trắng -> loại ngay, không chấm điểm nữa.

    duration = extract_duration(page) if media_type == "video" else None
    if media_type == "video":
        if target_duration and duration:
            # Ưu tiên thời lượng GẦN NHẤT với voice part, không thiên vị dài hơn.
            dur_score = max(0.0, 1.0 - abs(duration - target_duration) / max(duration, target_duration))
        else:
            dur_score = 0.5  # không có duration -> không cho điểm cao, phải kiểm tra tay.
        total = round(keyword_score * 45 + dur_score * 35 + aspect_score * 10 + res_score * 10, 1)
        breakdown = {
            "keyword": round(keyword_score * 45, 1),
            "duration_closeness": round(dur_score * 35, 1),
            "portrait_9_16": round(aspect_score * 10, 1),
            "resolution": round(res_score * 10, 1),
        }
    else:
        # Trọng số mới: ảnh dọc + nét tối đa chỉ 40 điểm, nên ảnh không khớp khái niệm
        # không thể lên CONSIDER như test đầu (ảnh cây 60 điểm chỉ vì dọc và nét).
        total = round(keyword_score * 60 + aspect_score * 15 + res_score * 15 + 10, 1)
        breakdown = {
            "keyword": round(keyword_score * 60, 1),
            "portrait_9_16": round(aspect_score * 15, 1),
            "resolution": round(res_score * 15, 1),
            "license_pass": 10,
        }

    return {
        "title": title,
        "page_url": f"https://commons.wikimedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}",
        "file_url": info.get("url"),
        "mime": info.get("mime"),
        "width": width,
        "height": height,
        "duration_sec": duration,
        "license": lic,
        "author": (ext.get("Artist") or {}).get("value", ""),
        "matched_tokens": matched,
        "score": total,
        "breakdown": breakdown,
        # Cổng ACCEPT chung (xem _verdict): điểm cao nhưng khớp nửa cụm
        # hoặc ảnh/video ngang thì tối đa CONSIDER, phải soi tay rồi mới dùng.
        "verdict": _verdict(total, media_type, aspect, duration,
                            full_match=(keyword_score >= 1.0)),
    }


def search_wikimedia(summary, media_type, target_duration, extra_keywords=None):
    """Thử HẾT các cụm trong nhóm, không dừng ở ACCEPT đầu tiên.
    Lý do 28/10/2026: ACCEPT đầu tiên có thể chỉ là khớp yếu ở cụm hẹp
    (vd ảnh tàu thủy lẫn trong "tàu cao tốc"), trong khi cụm Anh tương đương
    có ứng viên khớp mạnh hơn nhiều. Chỉ dừng sớm khi đã có ACCEPT >= 95,
    tức khớp gần như hoàn hảo, để tiết kiệm thời gian gọi API.
    Nếu không phát hiện cụm nào và không có từ khóa bổ sung, báo NO_CLUSTER
    rõ ràng thay vì trả về 0 khó hiểu: Production phải bổ sung cụm vào
    CONCEPT_CLUSTERS hoặc đưa --extra-keywords, rồi chạy lại."""
    queries = build_queries(summary, extra_keywords=extra_keywords)
    if not queries:
        return {
            "layer": "wikipedia_wikimedia_commons",
            "language": "vi",
            "queries_tried": [],
            "candidates": [],
            "decision": "NO_CLUSTER",
            "note": ("Không phát hiện cụm khái niệm nào trong tóm tắt và không "
                     "có từ khóa bổ sung. Bổ sung cụm vào CONCEPT_CLUSTERS hoặc "
                     "chạy lại với --extra-keywords, rồi mới kết luận không có file."),
        }
    best = {}
    tried = []
    for q in queries:
        tried.append(q)
        try:
            pages = commons_search(q, media_type)
        except Exception as exc:  # noqa: BLE001 - API ngoài, ghi lỗi thay vì crash cả pipeline.
            tried.append(f"ERROR: {exc}")
            continue
        for page in pages:
            cand = score_candidate(page, media_type, target_duration,
                                   summary_text=summary, extra_keywords=extra_keywords)
            if cand is None:
                continue
            key = cand["file_url"]
            if key not in best or cand["score"] > best[key]["score"]:
                cand["query_used"] = q
                cand["cluster"] = [c["id"] for c in concept_clusters(summary)]
                best[key] = cand
        if best and max(c["score"] for c in best.values()) >= 95:
            break
    ranked = sorted(best.values(), key=lambda c: c["score"], reverse=True)
    return {
        "layer": "wikipedia_wikimedia_commons",
        "language": "vi",
        "queries_tried": tried,
        "candidates": ranked[:10],
        "decision": "ACCEPT_TOP" if ranked and ranked[0]["verdict"] == "ACCEPT" else (
            "CONSIDER_TOP" if ranked and ranked[0]["score"] >= 50 else "FALLBACK_NEXT_LAYER"),
    }


def _http_json(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def _stock_score(phrase, haystack, width, height, media_type, duration, target_duration):
    """Chấm điểm stock bằng cùng công thức như lớp Wikipedia. Trả None nếu không khớp."""
    phrase_low = phrase.lower()
    if phrase_low in haystack:
        keyword_score = 1.0
        matched = [phrase]
    else:
        tokens = phrase_low.split()
        words = set(re.findall(r"[a-z]+", haystack))
        matched = [t for t in tokens if t in words or t.rstrip("s") in {w.rstrip("s") for w in words}]
        if matched and len(matched) / len(tokens) >= 0.5:
            keyword_score = 0.6
        elif matched:
            keyword_score = 0.3
        else:
            return None
    aspect = (width / height) if height else 0.0
    aspect_score = max(0.0, 1.0 - abs(aspect - 9 / 16)) if aspect else 0.0
    if aspect > 1.0:
        aspect_score *= 0.4
    if media_type == "image":
        res_score = 1.0 if (height >= 1280 and width >= 720) else (0.6 if (height >= 720 and width >= 480) else 0.2)
        total = round(keyword_score * 60 + aspect_score * 15 + res_score * 15 + 10, 1)
        breakdown = {"keyword": round(keyword_score * 60, 1),
                     "portrait_9_16": round(aspect_score * 15, 1),
                     "resolution": round(res_score * 15, 1), "license_pass": 10}
    else:
        res_score = 1.0 if (height >= 720 and width >= 400) else 0.5
        if target_duration and duration:
            dur_score = max(0.0, 1.0 - abs(duration - target_duration) / max(duration, target_duration))
        else:
            dur_score = 0.5
        total = round(keyword_score * 45 + dur_score * 35 + aspect_score * 10 + res_score * 10, 1)
        breakdown = {"keyword": round(keyword_score * 45, 1),
                     "duration_closeness": round(dur_score * 35, 1),
                     "portrait_9_16": round(aspect_score * 10, 1),
                     "resolution": round(res_score * 10, 1)}
    # Cổng ACCEPT chung (xem _verdict): khớp nửa cụm hoặc ảnh/video ngang
    # hoặc video không rõ thời lượng thì tối đa CONSIDER.
    verdict = _verdict(total, media_type, aspect, duration,
                       full_match=(keyword_score >= 1.0))
    return total, breakdown, verdict, matched


def _pixabay_candidates(key, phrase, media_type, target_duration):
    out = []
    q = urllib.parse.quote(phrase)
    if media_type == "image":
        url = (f"https://pixabay.com/api/?key={key}&q={q}&image_type=photo"
               f"&orientation=vertical&per_page=20&safesearch=true")
        data = _http_json(url)
        for hit in data.get("hits", []):
            hay = f"{hit.get('tags', '')} {hit.get('type', '')}".lower()
            scored = _stock_score(phrase, hay, hit.get("imageWidth") or 0,
                                  hit.get("imageHeight") or 0, media_type, None, None)
            if scored is None:
                continue
            total, breakdown, verdict, matched = scored
            out.append({"source": "pixabay", "title": hit.get("tags", ""),
                        "page_url": hit.get("pageURL"),
                        "file_url": hit.get("largeImageURL"),
                        "mime": "image/jpeg",
                        "width": hit.get("imageWidth"), "height": hit.get("imageHeight"),
                        "duration_sec": None, "license": "Pixabay License",
                        "matched_tokens": matched, "score": total,
                        "breakdown": breakdown, "verdict": verdict})
    else:
        url = f"https://pixabay.com/api/videos/?key={key}&q={q}&per_page=20&safesearch=true"
        data = _http_json(url)
        for hit in data.get("hits", []):
            hay = f"{hit.get('tags', '')}".lower()
            files = (hit.get("videos") or {})
            # Chọn file: ưu tiên chiều cao >= 720 trước, rồi mới đến gần 9:16.
            # Bài học test stock 28/10: xếp chỉ theo gần 9:16 thì toàn file nhỏ
            # 360x640 được chọn dù có file 720x1280/1080x1920 cùng tỉ lệ.
            best_file = None
            for _name, f in files.items():
                if not isinstance(f, dict) or not f.get("url"):
                    continue
                w, h = f.get("width") or 0, f.get("height") or 0
                if not h:
                    continue
                closeness = abs((w / h) - 9 / 16)
                # Đổi tên biến: trước đây dùng tên `key` trùng với tham số
                # API key của hàm (shadow) — URL đã build trước nên chưa vỡ,
                # nhưng lần sửa sau thêm phân trang/retry sẽ dùng nhầm tuple.
                rank_key = (0 if h >= 720 else 1, closeness, -h)
                if best_file is None or rank_key < best_file[0]:
                    best_file = (rank_key, f)
            if best_file is None:
                continue
            f = best_file[1]
            scored = _stock_score(phrase, hay, f.get("width") or 0, f.get("height") or 0,
                                  media_type, hit.get("duration"), target_duration)
            if scored is None:
                continue
            total, breakdown, verdict, matched = scored
            out.append({"source": "pixabay", "title": hit.get("tags", ""),
                        "page_url": hit.get("pageURL"),
                        "file_url": f.get("url"),
                        "mime": "video/mp4",
                        "width": f.get("width"), "height": f.get("height"),
                        "duration_sec": hit.get("duration"), "license": "Pixabay License",
                        "matched_tokens": matched, "score": total,
                        "breakdown": breakdown, "verdict": verdict})
    return out


def _pexels_candidates(key, phrase, media_type, target_duration):
    out = []
    headers = {"Authorization": key, "User-Agent": USER_AGENT}
    q = urllib.parse.quote(phrase)
    if media_type == "image":
        url = f"https://api.pexels.com/v1/search?query={q}&orientation=portrait&per_page=20&size=large"
        data = _http_json(url, headers)
        for photo in data.get("photos", []):
            hay = f"{photo.get('alt', '')}".lower()
            src = photo.get("src") or {}
            scored = _stock_score(phrase, hay, photo.get("width") or 0,
                                  photo.get("height") or 0, media_type, None, None)
            if scored is None:
                continue
            total, breakdown, verdict, matched = scored
            out.append({"source": "pexels", "title": photo.get("alt", ""),
                        "page_url": photo.get("url"),
                        "file_url": src.get("portrait") or src.get("large"),
                        "mime": "image/jpeg",
                        "width": photo.get("width"), "height": photo.get("height"),
                        "duration_sec": None, "license": "Pexels License",
                        "matched_tokens": matched, "score": total,
                        "breakdown": breakdown, "verdict": verdict})
    else:
        url = f"https://api.pexels.com/videos/search?query={q}&orientation=portrait&per_page=20"
        data = _http_json(url, headers)
        for video in data.get("videos", []):
            # Sửa 29/10/2026 (code-fix, audit D-M4): trước đây chỉ chấm trên
            # slug URL — video đúng vẫn bị loại nếu slug chung chung, video
            # sai vẫn được điểm nếu slug tình cờ chứa cụm (ACCEPT S2
            # courtroom 9s trước đây là may mắn theo slug). Pexels video API
            # không trả title/tags/description, nên haystack dùng mọi trường
            # mô tả thật còn lại: slug URL + tên uploader; và ứng viên chỉ
            # khớp nhờ slug thì tối đa CONSIDER, phải soi khung thật.
            user_name = (video.get("user") or {}).get("name", "")
            hay = f"{video.get('url', '')} {user_name}".lower()
            files = [f for f in video.get("video_files", [])
                     if f.get("file_type") == "video/mp4" and f.get("link")]
            if not files:
                continue
            # Chọn file mp4: ưu tiên chiều cao >= 720 trước, rồi mới đến gần 9:16.
            # (Xem ghi chú ở _pixabay_candidates về lỗi chọn file 360x640.)
            def _key(f):
                w, h = f.get("width") or 0, f.get("height") or 0
                return (0 if h >= 720 else 1,
                        abs((w / h) - 9 / 16) if h else 99, -h)
            f = sorted(files, key=_key)[0]
            scored = _stock_score(phrase, hay, f.get("width") or 0, f.get("height") or 0,
                                  media_type, video.get("duration"), target_duration)
            if scored is None:
                continue
            total, breakdown, verdict, matched = scored
            if verdict == "ACCEPT" and _slug_only_match(
                    phrase, matched, video.get("url", ""), user_name):
                verdict = "CONSIDER"  # chỉ khớp nhờ slug URL, chưa đủ ACCEPT
            out.append({"source": "pexels", "title": video.get("url", ""),
                        "page_url": video.get("url"),
                        "file_url": f.get("link"),
                        "mime": "video/mp4",
                        "width": f.get("width"), "height": f.get("height"),
                        "duration_sec": video.get("duration"), "license": "Pexels License",
                        "matched_tokens": matched, "score": total,
                        "breakdown": breakdown, "verdict": verdict})
    return out


def search_stock(en_keywords, media_type, target_duration):
    """
    Lớp stock: Pixabay / Pexels, chỉ tìm bằng từ khóa TIẾNG ANH đã chốt khái niệm.
    Key đọc từ biến môi trường, không bao giờ in ra, không đưa vào output hay
    thông báo lỗi (URL của Pixabay chứa key trong query string nên lỗi chỉ ghi
    chung chung, không kèm URL).
    """
    # Linh hoạt 28/10/2026: --en-keywords có thể là danh sách cách nhau bằng
    # dấu phẩy, vd "high speed train, high-speed railway, bullet train".
    # Mỗi cụm được chạy riêng và gộp kết quả, vì ảnh phù hợp có thể chỉ
    # gắn thẻ với một trong các cụm, không phải cụm đầu tiên.
    _phrases = parse_extra_keywords(en_keywords)
    if len(_phrases) > 1:
        merged, tried_all = [], []
        for _phrase in _phrases:
            _res = search_stock(_phrase, media_type, target_duration)
            merged.extend(_res.get("candidates", []))
            tried_all.extend(_res.get("sources_tried", []))
            tried_all.append(f"phrase:{_phrase}")
        _best = {}
        for _c in merged:
            _k = _c.get("file_url")
            if _k not in _best or _c["score"] > _best[_k]["score"]:
                _best[_k] = _c
        _ranked = sorted(_best.values(), key=lambda c: c["score"], reverse=True)
        return {"layer": "stock_pixabay_pexels", "language": "en",
                "en_keywords": en_keywords, "phrases_tried": _phrases,
                "sources_tried": tried_all,
                "candidates": _ranked[:10],
                "decision": "ACCEPT_TOP" if _ranked and _ranked[0]["verdict"] == "ACCEPT" else (
                    "CONSIDER_TOP" if _ranked and _ranked[0]["score"] >= 50 else "FALLBACK_AI")}
    if _phrases:
        en_keywords = _phrases[0]

    import os

    pixabay_key = os.environ.get("PIXABAY_API_KEY", "")
    pexels_key = os.environ.get("PEXELS_API_KEY", "")
    if not en_keywords:
        return {"layer": "stock_pixabay_pexels", "language": "en",
                "status": "SKIPPED_NO_EN_KEYWORDS",
                "note": "Stock cần từ khóa Anh đã chốt khái niệm, không dịch máy cả câu."}
    # Không trả về SKIPPED ngay khi thiếu key môi trường, vì đường vault
    # (custom.pixabay) có thể vẫn dùng được. Chỉ kết luận thiếu key ở cuối,
    # khi cả đường môi trường và đường vault đều không cho ứng viên nào.
    candidates, tried = [], []
    if pixabay_key:
        tried.append("pixabay")
        try:
            candidates.extend(_pixabay_candidates(pixabay_key, en_keywords, media_type, target_duration))
        except Exception:  # noqa: BLE001 - không kèm URL/key trong lỗi.
            tried.append("pixabay: API_ERROR")
    else:
        # Không có key trong môi trường thì thử đường vault đã lưu
        # (connector custom.pixabay, helper pixabay_search.py). Đường này
        # không cần key trong biến môi trường và không in key ra ngoài.
        tried.append("pixabay (vault)")
        try:
            import subprocess
            helper = (Path.home() / "workspace/custom-connectors/custom.pixabay"
                      / "bin/pixabay_search.py")
            if helper.exists():
                proc = subprocess.run(
                    [sys.executable, str(helper), "--query", en_keywords,
                     "--media-type", media_type],
                    capture_output=True, text=True, timeout=60)
                data = json.loads(proc.stdout) if proc.returncode == 0 else {}
                for h in data.get("hits", []):
                    # Sửa 29/10/2026 (code-fix, audit D-M5 — đã đối chiếu
                    # helper thật): helper vault dùng chung tên trường
                    # largeImageURL làm "URL file đã chọn" — với video, giá
                    # trị là URL file video thật (helper tự chọn file video
                    # tốt nhất), không phải URL ảnh; nhãn video/mp4 vì thế
                    # là đúng khi file tồn tại. Lỗi thật là trường hợp
                    # helper không chọn được file nào (largeImageURL None)
                    # mà code cũ vẫn đưa ứng viên không-file vào danh sách
                    # — bỏ qua các hit đó.
                    if not h.get("largeImageURL"):
                        continue
                    hay = f"{h.get('tags', '')}".lower()
                    scored = _stock_score(
                        en_keywords, hay, h.get("imageWidth") or 0,
                        h.get("imageHeight") or 0, media_type,
                        h.get("duration"), target_duration)
                    if scored is None:
                        continue
                    total, breakdown, verdict, matched = scored
                    candidates.append({
                        "source": "pixabay (vault)", "title": h.get("tags", ""),
                        "page_url": h.get("pageURL"),
                        "file_url": h.get("largeImageURL"),
                        "mime": "video/mp4" if media_type == "video" else "image/jpeg",
                        "width": h.get("imageWidth"), "height": h.get("imageHeight"),
                        "duration_sec": h.get("duration"),
                        "license": "Pixabay License",
                        "matched_tokens": matched, "score": total,
                        "breakdown": breakdown, "verdict": verdict})
        except Exception:  # noqa: BLE001 - vault chưa kết nối thì bỏ qua đường này.
            tried.append("pixabay (vault): UNAVAILABLE")
    if pexels_key:
        tried.append("pexels")
        try:
            candidates.extend(_pexels_candidates(pexels_key, en_keywords, media_type, target_duration))
        except Exception:  # noqa: BLE001 - không kèm key trong lỗi.
            tried.append("pexels: API_ERROR")
    else:
        # Đường vault Pexels, tương tự Pixabay: connector custom.pexels,
        # helper pexels_search.py, key qua header Authorization bằng surrogate.
        tried.append("pexels (vault)")
        try:
            import subprocess
            helper = (Path.home() / "workspace/custom-connectors/custom.pexels"
                      / "bin/pexels_search.py")
            if helper.exists():
                proc = subprocess.run(
                    [sys.executable, str(helper), "--query", en_keywords,
                     "--media-type", media_type],
                    capture_output=True, text=True, timeout=60)
                data = json.loads(proc.stdout) if proc.returncode == 0 else {}
                for h in data.get("hits", []):
                    # Như nhánh Pixabay: bỏ hit không có file thật. Với
                    # video, helper vault chỉ trả pageURL (slug) mà không
                    # trả metadata mô tả khác, nên khớp ở đây là khớp nhờ
                    # slug theo định nghĩa — tối đa CONSIDER, không ACCEPT.
                    # (largeImageURL ở đây là URL file video thật do helper
                    # chọn, như nhánh Pixabay, không phải URL ảnh.)
                    if not h.get("largeImageURL"):
                        continue
                    hay = f"{h.get('tags', '')} {h.get('pageURL', '')}".lower()
                    scored = _stock_score(
                        en_keywords, hay, h.get("imageWidth") or 0,
                        h.get("imageHeight") or 0, media_type,
                        h.get("duration"), target_duration)
                    if scored is None:
                        continue
                    total, breakdown, verdict, matched = scored
                    if media_type == "video" and verdict == "ACCEPT":
                        verdict = "CONSIDER"  # vault chỉ còn slug để chấm
                    candidates.append({
                        "source": "pexels (vault)",
                        "title": h.get("tags", "") or h.get("pageURL", ""),
                        "page_url": h.get("pageURL"),
                        "file_url": h.get("largeImageURL"),
                        "mime": "video/mp4" if media_type == "video" else "image/jpeg",
                        "width": h.get("imageWidth"), "height": h.get("imageHeight"),
                        "duration_sec": h.get("duration"),
                        "license": "Pexels License",
                        "matched_tokens": matched, "score": total,
                        "breakdown": breakdown, "verdict": verdict})
        except Exception:  # noqa: BLE001 - vault chưa kết nối thì bỏ qua đường này.
            tried.append("pexels (vault): UNAVAILABLE")
    ranked = sorted(candidates, key=lambda c: c["score"], reverse=True)
    return {"layer": "stock_pixabay_pexels", "language": "en",
            "en_keywords": en_keywords, "sources_tried": tried,
            "candidates": ranked[:10],
            "decision": "ACCEPT_TOP" if ranked and ranked[0]["verdict"] == "ACCEPT" else (
                "CONSIDER_TOP" if ranked and ranked[0]["score"] >= 50 else "FALLBACK_AI")}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tìm ảnh/video có sẵn theo thứ tự Wikipedia > Stock > AI")
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("wikimedia")
    w.add_argument("--summary", required=True, help="Tóm tắt kịch bản tiếng Việt của cảnh/part")
    w.add_argument("--media-type", choices=["image", "video"], required=True)
    w.add_argument("--duration", type=float, default=0.0, help="Thời lượng voice part (giây), cho video")
    w.add_argument("--extra-keywords", default="",
                   help="Từ khóa bổ sung cách nhau bằng dấu phẩy: tên riêng, tên dự án, "
                        "địa điểm, vd 'VinSpeed, Velaro Novo'. Chỉ dùng khi cần, "
                        "không tự gắn tên riêng vào cụm chung.")
    s = sub.add_parser("stock")
    s.add_argument("--en-keywords", default="",
                   help="Từ khóa tiếng Anh, một cụm hoặc danh sách cách nhau bằng dấu phẩy, "
                        "vd 'high speed train, high-speed railway, bullet train'")
    s.add_argument("--media-type", choices=["image", "video"], required=True)
    s.add_argument("--duration", type=float, default=0.0)
    args = ap.parse_args(argv)

    if args.cmd == "wikimedia":
        result = search_wikimedia(args.summary, args.media_type, args.duration or None,
                                  extra_keywords=args.extra_keywords)
    else:
        result = search_stock(args.en_keywords, args.media_type, args.duration or None)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
