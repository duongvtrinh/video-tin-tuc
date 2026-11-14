# Measure motion on lossless frames

> **TRẠNG THÁI: HẾT HIỆU LỰC từ 12/11/2026 (quyết định X-02 = B, CEO 12/11/2026).** QA không còn chấm motion (quyết định CEO 10/11/2026 22:46 trên repo chuẩn: xóa kiểm tra motion đo PNG 2fps/MAD <1,0/chuỗi >5s và bỏ luôn luật QA chấm motion bằng mắt; CEO tự kiểm tra video). Skill này được LƯU TRỮ, KHÔNG XÓA — giữ làm tài liệu tham khảo về cách đo (đo trên PNG lossless, không JPEG; sửa bằng video thật trước, tăng zoom sau). Không dùng skill này để trả lại video vì motion nữa.

## Extract lossless frames

- Extract consecutive frames from the final MP4 as PNG files at full resolution.

- Do not extract frames as JPEG files for a motion measurement.

- Do not downscale frames before you measure a static run.

- Keep the PNG frames for the part you measured until the verdict is recorded.

## Measure the static run inside one part

- Compare consecutive PNG frames inside one part and record the longest run that stays nearly unchanged.

- Do not measure across a cut or a template change, since a single large change at a cut is not motion inside a part.

- Read the static run threshold and the verdict rule in [media_video_tech_qa](/home/hatch/workspace/custom-skills/media-video-tech-qa/SKILL.md) before you decide whether a part passes or fails.

- Treat on screen typing as no motion when you measure a part, since each typed character changes only a few pixels and the frame difference stays low while typing.

## Resolve a disputed measurement

- Record both numbers with each extraction format and resolution when Production and QA disagree.

- Trust the PNG full resolution number when a JPEG or downscaled number disagrees with it.

- Do not ask for a re-render only to make two numbers match when both numbers fall on the same side of the threshold.

- Treat a disagreement that changes the pass or fail side as a real defect and re-measure on PNG frames before you decide.

## Report what you measured

- Report the extraction format, the resolution, the part, and the longest static run with its start and end times.

- Name the fix when a part fails, in this order of reliability: real video instead of a still image first, stronger zoom second. Do NOT name a brighter still image as a fix — a brighter background does not add motion. Counter-evidence (TOPIC-252, 06/11/2026): v1 failed motion at S11P1 (PNG 7.50/5.50/5.00s); v2 only swapped the background for a brighter, higher-contrast AI still (bright desk, open files, red seal, window light) and measured WORSE (PNG 11.0/8.0/7.5s), because the image was a soft gradient (blurred wall, soft sun-shadow edges) and the typewriter scrim compressed the gradient further, so slow zoom created almost no frame change; v3 swapped to real video (Pexels 7710488) and measured 1.5/1.5/1.5s and was APPROVED. Same class: TOPIC-243 v1, TOPIC-249 v1, TOPIC-251 v1, TOPIC-106 v1, TOPIC-186 v1 — all fixed by real video, never by another still.

- Keep the PNG frames and the measurement beside the verdict so a later reviewer can rerun the same check.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Use real video for a hook or important scene when a still image cannot hold motion, and measure the real video the same way.

- Check a dark low contrast background before you render, but do not trust brightness alone: a bright still image with soft gradients can measure worse than a darker one, because brightness without sharp detail creates almost no frame-to-frame change under slow zoom (TOPIC-252 v2, 06/11/2026: brighter high-contrast still measured 11.0/8.0/7.5s vs v1 7.50/5.50/5.00s). What keeps a typewriter part moving is high-frequency detail in the background plus a strong enough zoom — and the reliable fix when a part fails is real video, not another still image.
