/* VieNeuRender — engine render frame DUY NHẤT dùng chung cho:
 *  (1) HTML preview player trong app VieNeu Asset Factory
 *  (2) trang render_page.html của pipeline frame-capture
 * Framework-free, không phụ thuộc React. Host chỉ cần:
 *   const stage = document.getElementById('stage');
 *   VieNeuRender.mount(stage, DATA);   // DATA: {W,H,parts:[...]}
 *   VieNeuRender.seekTo(t);            // render frame tại giây t
 *   VieNeuRender.getDuration();        // tổng thời lượng (giây)
 *   VieNeuRender.isReady();            // true khi ảnh đã preload xong
 *
 * Data contract cho mỗi part:
 *   { id, start, end, image, video?, videoW?, videoH?, templateId, tplHtml, tplCss, tplInputs,
 *     motion?,              // tên motion render sẽ dùng (xem dưới); vắng = hash(partId)
 *     tplStart?, tplEnd?,   // cửa sổ hiện template (giây tuyệt đối); vắng = cả part
 *     karaoke: { lines: [{start,end,words:[{text,start,end}]}], subsHidden } }
 *   - video: URL file b-roll video của part (nếu có). Engine vẽ <video>
 *     thật, tắt tiếng, lặp: khung dọc + video ngang/vuông -> nằm trong
 *     cửa sổ 3:4 cố định (cao bằng cửa sổ, hai bên cắt); video dọc
 *     9:16 -> đầy khung. Video không gắn motion Ken Burns (render
 *     cũng không).
 *   - Lớp 3:4 LUÔN CỐ ĐỊNH: fgWrap không di chuyển, không đổi kích
 *     thước; chỉ nội dung bên trong chuyển động và bị cắt bởi
 *     overflow:hidden, không để lộ nền mờ vào trong cửa sổ.
 *
 * Quy tắc render (KHÓA — đổi ở đây là đổi cả preview lẫn MP4):
 *  - Motion: 6 preset CSS keyframes. Khi part có `motion` (tên motion mà
 *    render_draft.py thật sự dùng cho part đó — chuỗi tuần tự
 *    random.Random("motion-<pid>") do host tính và gắn vào data), engine
 *    dùng ĐÚNG motion đó; chỉ khi vắng mới fallback về hash(partId) như
 *    trước. Trước khi có trường này, preview chọn motion bằng hash còn
 *    render chọn bằng RNG tuần tự nên hai bên lệch nhau (blurtest001
 *    part 4: render pan_down, preview zoom_in — user bắt lỗi 2026-11-01).
 *    Thứ tự preset khớp MOTIONS của render_draft.py:
 *    zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down; chiều pan
 *    của keyframes đã quy về cùng hệ "nội dung dịch chuyển" với zoompan
 *    (render dịch cửa sổ crop, preview dịch element — dấu đã khớp).
 *    Từ 29/10/2026 motion ảnh chạy bằng CSS animation
 *    trên compositor thay vì JS gán transform mỗi khung hình, để giảm tải
 *    cho trình phát: JS chỉ dựng animation (tên keyframes, duration bằng
 *    độ dài part, delay âm bằng vị trí trong part), còn nội suy transform
 *    do trình duyệt lo. Zoom tối đa 1.05 khớp ffmpeg render_draft.py,
 *    easing ease-in-out xấp xỉ smoothstep của ffmpeg.
 *  - seekTo(t) mặc định lái animation bằng delay âm + paused, nên khung
 *    hình luôn đúng dù host có gọi seekTo mỗi khung hình hay không
 *    (đường này dùng cho trang frame-capture). Host phát video gọi thêm
 *    VieNeuRender.setPlaying(true) để animation chạy thật trên
 *    compositor và seekTo không chạm vào animation khi còn cùng part;
 *    setPlaying(false) quay lại chế độ lái bằng delay.
 *  - Chuyển cảnh: 0.5s đầu part, crossfade 2 layer, ảnh cũ vẫn chuyển động.
 *  - Template: fill {{placeholder}} (escape HTML, **bold** -> <strong>),
 *    hiện trong [tplStart,tplEnd) nếu có, ngược lại cả part.
 *  - Host template theo ĐÚNG hợp đồng thiết kế (render_template.py):
 *    overlay là flex-center (template tĩnh được căn giữa khung; template
 *    position:absolute tự định vị theo stage), --broll-accent = #FBBF24,
 *    và CSS được chuẩn hoá theo KÍCH THƯỚC STAGE chứ không theo viewport
 *    của host: vmin/vw/vh -> px theo W/H, @media orientation/aspect-ratio
 *    xét theo tỉ lệ stage. Ở trang frame-capture viewport == stage nên
 *    các phép chuẩn hoá này là đồng nhất — khung hình MP4 không đổi;
 *    ở app (stage bị scale bằng transform, viewport là cửa sổ) chúng giữ
 *    template hiển thị đúng như bản render.
 *  - Karaoke: highlight từng từ #FBBF24 theo [start,end); part có
 *    template chữ thật (subsHidden) thì KHÔNG hiện phụ đề.
 *  - HẰNG SỐ ĐÃ CHỐT (Giai đoạn 4, 05/11/2026 — xem PIPELINE.md mục
 *    "Hằng số pipeline đã chốt"): khung mặc định 9:16 khi thiếu
 *    aspectRatio (host tính W/H, engine chỉ nhận W/H); phụ đề cách đáy
 *    20% chiều cao khi dọc, 7% khi ngang (khớp karaoke.ass MarginV —
 *    trước đây subsDiv ghim 7% cả hai chiều nên preview dọc lệch MP4);
 *    font phụ đề 40*(min(W,H)/480) khớp karaoke.py; zoom tối đa 1.05,
 *    chuyển cảnh 0.5s, accent theo bảng ACCENT_HEX của
 *    render_template.py (host phải gắn part.tplAccent = accent.default
 *    trong meta thì preview mới khớp MP4 — build_render_page.py đã gắn).
 *    PREVIEW CHỈ LÀ XẤP XỈ ở: pan blur-fill (xem COMP_KEYFRAMES),
 *    easing (cubic-bezier xấp xỉ smoothstep của ffmpeg), độ mờ nền
 *    (CSS blur 30px + scale 1.1 so với gblur sigma=25 của ffmpeg) và
 *    co chữ template (preview vẽ HTML đúng cỡ stage, MP4 vẽ PNG rồi
 *    co 92%W/80%H trừ full-stage) — xem PIPELINE.md liệt kê đầy đủ.
 *  - Phụ đề fallback: host tự xử lý khi không có karaoke (ngoài engine).
 *  - Font DUY NHẤT (CEO chốt 30/10/2026): Anton cho MỌI template và cho
 *    phụ đề karaoke — ở preview này và ở bản render ffmpeg (karaoke.py
 *    ghi Style Fontname Anton vào .ass). Stage ghim --vst-font-family
 *    về Anton để template nào dùng biến đó cũng không lệch font. Host
 *    phải nạp sẵn font Anton (app: Google Fonts trong theme.css; trang
 *    frame-capture: font Anton đã cài trên máy render qua fontconfig).
 */

(function (global) {
  'use strict';

  var TRANS = 0.5; // giây crossfade đầu mỗi part

  // Motion bằng CSS keyframes (29/10/2026, thay JS gán transform mỗi
  // khung hình): chỉ 6 rule dùng chung cho mọi part; animation của một
  // part chỉ khác duration (độ dài part) và delay âm (vị trí trong part).
  // Zoom tối đa 1.05 khớp ffmpeg; pan ±2% để ảnh scale 1.05 vẫn phủ kín
  // khung (lề mỗi bên 2.5%). Easing ease-in-out là xấp xỉ CSS gần nhất
  // của smoothstep s=t*t*(3-2*t) mà ffmpeg dùng — cả hai đều bắt đầu và
  // kết thúc chậm, khác biệt mắt thường khó thấy.
  var MOTION_KEYFRAMES = [
    ['vn-motion-0', 'from{transform:scale(1)}to{transform:scale(1.05)}'],
    ['vn-motion-1', 'from{transform:scale(1.05)}to{transform:scale(1)}'],
    ['vn-motion-2', 'from{transform:scale(1.05) translateX(0%)}to{transform:scale(1.05) translateX(2%)}'],
    ['vn-motion-3', 'from{transform:scale(1.05) translateX(0%)}to{transform:scale(1.05) translateX(-2%)}'],
    ['vn-motion-4', 'from{transform:scale(1.05) translateY(0%)}to{transform:scale(1.05) translateY(2%)}'],
    ['vn-motion-5', 'from{transform:scale(1.05) translateY(0%)}to{transform:scale(1.05) translateY(-2%)}']
  ];
  // Blur-fill 3:4 (CEO 2026-11-01): cùng 6 kiểu motion nhưng cho ảnh
  // nền trước (fg vuông 960x960 trong cửa sổ 720x960). CHIỀU PAN ĐÃ
  // ĐẢO DẤU 2026-11-01 cho khớp render: zoompan dịch CỬA SỔ (x/y là
  // mép crop) nên cửa sổ dịch trái thì NỘI DUNG dịch phải, ngược với
  // translate của preview (dịch cả element). SỐ PAN LÀ XẤP XỈ, KHÔNG
  // KHỚP RENDER (đo đợt D3, 01/11/2026): preview pan ngang 12% ≈ 121px
  // một chiều, render 240px một chiều; preview pan dọc 2% ≈ 20px,
  // render ≈ 46px. Preview không thể khớp render với fg 960 hiện tại
  // vì lề phủ chỉ 144px ngang / 24px dọc — muốn khớp phải phóng to fg
  // (xem TEMPLATE_POSITION_SPEC.md, mục D3) và kiểm chứng bằng mắt
  // trong tab Preview trước khi đổi. Đừng ghi "khớp render" ở đây cho
  // đến khi đo lại sau thay đổi đó.
  var COMP_KEYFRAMES = [
    ['vn-comp-0', 'from{transform:scale(1)}to{transform:scale(1.05)}'],
    ['vn-comp-1', 'from{transform:scale(1.05)}to{transform:scale(1)}'],
    ['vn-comp-2', 'from{transform:scale(1.05) translateX(0%)}to{transform:scale(1.05) translateX(12%)}'],
    ['vn-comp-3', 'from{transform:scale(1.05) translateX(0%)}to{transform:scale(1.05) translateX(-12%)}'],
    ['vn-comp-4', 'from{transform:scale(1.05) translateY(0%)}to{transform:scale(1.05) translateY(2%)}'],
    ['vn-comp-5', 'from{transform:scale(1.05) translateY(0%)}to{transform:scale(1.05) translateY(-2%)}']
  ];
  var MOTION_EASING = 'cubic-bezier(0.42,0,0.58,1)';

  function hashId(id) {
    var h = 0;
    for (var i = 0; i < id.length; i++) h = (h * 31 + id.charCodeAt(i)) >>> 0;
    return h;
  }

  function motionIndexFor(partId) {
    return hashId(String(partId)) % MOTION_KEYFRAMES.length;
  }

  // Thứ tự khớp MOTIONS trong bin/render_draft.py; index dùng chung cho
  // cả MOTION_KEYFRAMES lẫn COMP_KEYFRAMES (cùng một kiểu motion, hai bộ
  // keyframes cho ảnh full và ảnh blur-fill).
  var MOTION_ORDER = ['zoom_in', 'zoom_out', 'pan_left', 'pan_right', 'pan_up', 'pan_down'];

  // Motion của một part: ưu tiên tên motion render thật (part.motion do
  // host tính từ chuỗi RNG của render_draft.py); host cũ không gắn thì
  // fallback hash(partId) như trước, nhưng KÈM CẢNH BÁO (đợt C,
  // 01/11/2026) thay vì lặng như trước — fallback vẫn giữ tạm thời.
  var _motionWarned = {};
  function motionIndexForPart(part) {
    if (part && typeof part.motion === 'string') {
      var idx = MOTION_ORDER.indexOf(part.motion);
      if (idx >= 0) return idx;
    }
    var pid = part ? part.id : '';
    if (!_motionWarned[pid]) {
      _motionWarned[pid] = true;
      if (typeof console !== 'undefined' && console.warn) {
        console.warn('[vieneu] part thiếu motion render thật, đang fallback hash(partId): ' + (pid || '(không có id)') + ' — host cần gắn part.motion theo chuỗi RNG render_draft.py');
      }
    }
    return motionIndexFor(pid);
  }

  function esc(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function fillTpl(html, inputs) {
    return html.replace(/\{\{(\w+)\}\}/g, function (m, k) {
      var v = inputs[k];
      if (v === undefined || v === null) v = '';
      return esc(v).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    });
  }

  function clamp01(x) {
    return Math.min(Math.max(x, 0), 1);
  }

  // ---- Chuẩn hoá CSS template theo kích thước stage ----
  // CSS template viết cho trang đúng bằng stage (viewport == stage như
  // trang frame-capture / render_template.py). Host khác (app: stage bị
  // scale, viewport là cửa sổ) phải đổi đơn vị viewport về px theo stage
  // và xét @media theo stage, nếu không cỡ chữ/vị trí template lệch hẳn.

  function fmtPx(x) {
    return String(Math.round(x * 100) / 100) + 'px';
  }

  // Một feature trong @media xét theo stage: true/false, null = không
  // biết (giữ nguyên block, không suy đoán).
  function evalMediaFeature(f) {
    var m = /^\(\s*orientation\s*:\s*(portrait|landscape)\s*\)$/.exec(f);
    if (m) {
      var portrait = data.H >= data.W;
      return (m[1] === 'portrait') === portrait;
    }
    m = /^\(\s*(min|max)-aspect-ratio\s*:\s*(\d+(?:\.\d+)?)\s*\/\s*(\d+(?:\.\d+)?)\s*\)$/.exec(f);
    if (m) {
      var ratio = data.W / data.H;
      var target = parseFloat(m[2]) / parseFloat(m[3]);
      return m[1] === 'max' ? ratio <= target : ratio >= target;
    }
    m = /^\(\s*(min|max)-width\s*:\s*(\d+(?:\.\d+)?)px\s*\)$/.exec(f);
    if (m) return m[1] === 'max' ? data.W <= parseFloat(m[2]) : data.W >= parseFloat(m[2]);
    m = /^\(\s*(min|max)-height\s*:\s*(\d+(?:\.\d+)?)px\s*\)$/.exec(f);
    if (m) return m[1] === 'max' ? data.H <= parseFloat(m[2]) : data.H >= parseFloat(m[2]);
    return null;
  }

  // true = khớp stage, false = không khớp, null = có phần không đánh
  // giá được -> giữ nguyên block @media như CSS gốc.
  function evalMediaQuery(query) {
    var alternatives = query.split(',');
    var sawKnown = false;
    for (var a = 0; a < alternatives.length; a++) {
      var q = alternatives[a].trim();
      var feats = q.match(/\([^)]*\)/g);
      if (!feats) return null;
      var rest = q
        .replace(/\([^)]*\)/g, '')
        .replace(/\band\b/g, '')
        .replace(/\bonly\b/g, '')
        .replace(/\bscreen\b/g, '')
        .replace(/\ball\b/g, '')
        .trim();
      if (rest) return null;
      var ok = true;
      for (var i = 0; i < feats.length; i++) {
        var r = evalMediaFeature(feats[i]);
        if (r === null) return null;
        if (!r) ok = false;
      }
      sawKnown = true;
      if (ok) return true;
    }
    return sawKnown ? false : null;
  }

  function resolveMediaQueries(css) {
    var out = '';
    var i = 0;
    while (i < css.length) {
      var at = css.indexOf('@media', i);
      if (at < 0) { out += css.slice(i); break; }
      var brace = css.indexOf('{', at);
      if (brace < 0) { out += css.slice(i); break; }
      out += css.slice(i, at);
      var depth = 0;
      var j = brace;
      for (; j < css.length; j++) {
        if (css[j] === '{') depth++;
        else if (css[j] === '}') {
          depth--;
          if (depth === 0) break;
        }
      }
      if (j >= css.length) { out += css.slice(at); break; }
      var verdict = evalMediaQuery(css.slice(at + 6, brace).trim());
      if (verdict === null) out += css.slice(at, j + 1);
      else if (verdict) out += css.slice(brace + 1, j);
      i = j + 1;
    }
    return out;
  }

  var cssNormCache = {};
  function normalizeCss(css, templateId) {
    var key = String(templateId) + '|' + data.W + 'x' + data.H;
    var hit = cssNormCache[key];
    if (hit !== undefined) return hit;
    var out = resolveMediaQueries(css);
    var vminPx = Math.min(data.W, data.H) / 100;
    var vwPx = data.W / 100;
    var vhPx = data.H / 100;
    out = out
      .replace(/(-?\d+(?:\.\d+)?)vmin/g, function (mm, n) { return fmtPx(parseFloat(n) * vminPx); })
      .replace(/(-?\d+(?:\.\d+)?)vw/g, function (mm, n) { return fmtPx(parseFloat(n) * vwPx); })
      .replace(/(-?\d+(?:\.\d+)?)vh/g, function (mm, n) { return fmtPx(parseFloat(n) * vhPx); });
    cssNormCache[key] = out;
    return out;
  }

  // ---- state ----
  var stage = null, data = null, ready = false;
  var layerA = null, layerB = null, imgA = null, imgB = null;
  var layerObjA = null, layerObjB = null;
  var brollDiv = null, subsDiv = null;
  var fontPx = 36;

  function buildDom() {
    stage.innerHTML = '';
    stage.style.position = 'relative';
    stage.style.overflow = 'hidden';
    stage.style.background = '#000';
    stage.style.width = data.W + 'px';
    stage.style.height = data.H + 'px';
    // Màu nhấn mặc định của hệ template (render_template.py đặt trên
    // :root) — nhiều template dùng var(--broll-accent) không fallback.
    stage.style.setProperty('--broll-accent', '#FBBF24');
    // Font chung duy nhất Anton (CEO chốt 30/10/2026): ghim biến font mà
    // một số template tham chiếu về Anton, khớp khai báo Anton trực tiếp
    // trong CSS của mọi template còn lại.
    stage.style.setProperty('--vst-font-family', "'Anton', sans-serif");

    // Keyframes motion dùng chung: một <style> duy nhất, 12 rule.
    var ks = document.createElement('style');
    var kcss = '';
    var allKeys = MOTION_KEYFRAMES.concat(COMP_KEYFRAMES);
    for (var ki = 0; ki < allKeys.length; ki++) {
      kcss += '@keyframes ' + allKeys[ki][0] + '{' + allKeys[ki][1] + '}';
    }
    ks.textContent = kcss;
    stage.appendChild(ks);

    function mkLayer() {
      var l = document.createElement('div');
      l.style.cssText = 'position:absolute;inset:0;will-change:transform,opacity;';
      var im = document.createElement('img');
      im.style.cssText = 'width:100%;height:100%;object-fit:cover;will-change:transform;';
      l.appendChild(im);
      var vid = document.createElement('video');
      vid.style.cssText = 'width:100%;height:100%;object-fit:cover;display:none;';
      vid.muted = true; vid.loop = true; vid.playsInline = true; vid.preload = 'auto';
      l.appendChild(vid);
      // Blur-fill 3:4 (CEO 2026-11-01): nền mờ phủ kín khung + cửa sổ
      // nét 3:4 CỐ ĐỊNH căn giữa dọc (cao 75% khung, cách đều 12.5%
      // trên/dưới). Cửa sổ không bao giờ di chuyển hay đổi kích thước;
      // chỉ nội dung bên trong chuyển động và bị cắt bởi
      // overflow:hidden. Ảnh nền trước là vuông (object-fit cover tự
      // cắt vuông giữa với ảnh ngang), khớp render_draft.py. Video
      // nền trước đúng bằng cửa sổ (cao bằng cửa sổ, hai bên cắt).
      var bg = document.createElement('img');
      bg.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:blur(30px) brightness(0.92);transform:scale(1.1);display:none;';
      l.appendChild(bg);
      var bgVid = document.createElement('video');
      bgVid.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;filter:blur(30px) brightness(0.92);transform:scale(1.1);display:none;';
      bgVid.muted = true; bgVid.loop = true; bgVid.playsInline = true; bgVid.preload = 'auto';
      l.appendChild(bgVid);
      var winH = Math.round(data.H * 0.75), winTop = Math.round(data.H * 0.125);
      var fgWrap = document.createElement('div');
      fgWrap.style.cssText = 'position:absolute;left:0;right:0;top:' + winTop + 'px;height:' + winH + 'px;overflow:hidden;display:none;';
      var fg = document.createElement('img');
      fg.style.cssText = 'position:absolute;top:0;left:' + Math.round((data.W - winH) / 2) + 'px;width:' + winH + 'px;height:' + winH + 'px;object-fit:cover;will-change:transform;';
      fgWrap.appendChild(fg);
      var fgVid = document.createElement('video');
      fgVid.style.cssText = 'position:absolute;top:0;left:0;width:' + data.W + 'px;height:' + winH + 'px;object-fit:cover;display:none;';
      fgVid.muted = true; fgVid.loop = true; fgVid.playsInline = true; fgVid.preload = 'auto';
      fgWrap.appendChild(fgVid);
      l.appendChild(fgWrap);
      stage.appendChild(l);
      return { layer: l, img: im, vid: vid, bgImg: bg, bgVid: bgVid, fgWrap: fgWrap, fgImg: fg, fgVid: fgVid, composite: false, media: null, mediaW: 0, mediaH: 0 };
    }
    var a = mkLayer(), b = mkLayer();
    layerObjA = a; layerObjB = b;
    layerA = a.layer; imgA = a.img;
    layerB = b.layer; imgB = b.img;

    brollDiv = document.createElement('div');
    // Luật CEO 31/10/2026: vùng chữ template về bottom, đúng khoảng
    // cách phụ đề (20% chiều cao khi dọc, 7% khi ngang — khớp
    // render_draft.py); template position:absolute thoát khỏi flow và
    // tự định vị theo stage nên không chịu quy tắc này (brollDiv vẫn
    // phủ kín khung nên vẫn là containing block đúng).
    brollDiv.style.cssText = 'position:absolute;inset:0;pointer-events:none;' +
      'display:none;align-items:flex-end;justify-content:center;';
    brollDiv.style.paddingBottom = Math.round(data.H * (data.H > data.W ? 0.20 : 0.07)) + 'px';
    stage.appendChild(brollDiv);

    subsDiv = document.createElement('div');
    // Vị trí phụ đề: 20% chiều cao khi dọc, 7% khi ngang — khớp
    // karaoke.ass MarginV (karaoke.py) và render_draft.py. Trước đây
    // ghim 7% cả hai chiều nên preview video dọc đặt phụ đề thấp hơn
    // MP4 (MP4 cách đáy 20%H). CSS bottom % tính theo chiều cao stage
    // nên 20%/7% tương đương đúng MarginV theo px của .ass.
    subsDiv.style.cssText = 'position:absolute;left:0;right:0;bottom:' + (data.H > data.W ? '20%' : '7%') + ';text-align:center;pointer-events:none;';
    stage.appendChild(subsDiv);
    lastSubsHtml = null;

    fontPx = Math.round(40 * Math.min(data.W, data.H) / 480);
  }

  function findPart(t) {
    var parts = data.parts;
    for (var i = 0; i < parts.length; i++) {
      if (t >= parts[i].start && t < parts[i].end) return i;
    }
    if (parts.length && t >= parts[parts.length - 1].end) return parts.length - 1;
    return 0;
  }

  // HTML phụ đề của lần vẽ trước: seekTo chạy mỗi khung hình khi phát,
  // chỉ ghi lại DOM khi nội dung thật sự đổi (đổi dòng hoặc đổi từ đang
  // highlight) — ghi innerHTML 60 lần/giây là nguồn giật chính của player.
  var lastSubsHtml = null;

  function setSubsHtml(html) {
    if (html === lastSubsHtml) return;
    lastSubsHtml = html;
    subsDiv.innerHTML = html;
    // highlight từ đang đọc màu vàng (áp trực tiếp, không phụ thuộc stylesheet ngoài)
    var spans = subsDiv.querySelectorAll('.w.hl');
    for (var s = 0; s < spans.length; s++) spans[s].style.color = '#FBBF24';
  }

  function renderSubs(part, t) {
    var k = part.karaoke;
    if (!k || k.subsHidden || !k.lines || !k.lines.length) {
      setSubsHtml('');
      return;
    }
    var line = null;
    for (var i = 0; i < k.lines.length; i++) {
      if (t >= k.lines[i].start && t < k.lines[i].end) { line = k.lines[i]; break; }
    }
    if (!line) {
      // giữ line cuối trong khoảng trống giữa các line (không nhấp nháy):
      // line cuối cùng đã kết thúc nhưng line kế chưa bắt đầu
      for (var j = 0; j < k.lines.length; j++) {
        if (t >= k.lines[j].end && (j + 1 >= k.lines.length || t < k.lines[j + 1].start)) {
          line = k.lines[j];
          break;
        }
      }
      if (!line) { setSubsHtml(''); return; }
    }
    var html = '';
    for (var w = 0; w < line.words.length; w++) {
      var word = line.words[w];
      var hl = (t >= word.start && t < word.end) ? ' hl' : '';
      html += '<span class="w' + hl + '">' + esc(word.text) + '</span> ';
    }
    setSubsHtml('<div class="line" style="display:inline-block;background:rgba(0,0,0,.65);' +
      'padding:.3em .8em;border-radius:4px;font:600 ' + fontPx + 'px Anton,Arial,sans-serif;color:#fff;">' +
      html + '</div>');
  }

  function renderBroll(part, t) {
    if (part.templateId && part.tplHtml) {
      var ts = (part.tplStart !== undefined) ? part.tplStart : part.start;
      var te = (part.tplEnd !== undefined) ? part.tplEnd : part.end;
      if (t >= ts && t < te) {
        if (brollDiv.dataset.pid !== part.id) {
          brollDiv.innerHTML = '<style>' +
            normalizeCss(part.tplCss || '', part.templateId) + '</style>' +
            fillTpl(part.tplHtml, part.tplInputs || {});
          brollDiv.dataset.pid = part.id;
        }
        // clip-caption giữ thiết kế caption sát đáy 3% (lệnh CEO
        // 31/10/2026), giống render_draft; các part còn lại: part vẫn
        // hiện phụ đề (subsHidden false) thì thẻ sát đáy 3% dưới vùng
        // phụ đề, part ẩn phụ đề thì thẻ ở khoảng cách phụ đề như thường.
        // Đợt D1 (01/11/2026): paddingBottom KHÔNG có tác dụng với
        // template absolute (clip-caption root absolute bottom:0 — nó
        // định vị theo padding box của brollDiv, không bị padding đẩy
        // lên). Nên với clip-caption phải lùi chính đáy của brollDiv
        // lên 3% thì absolute bottom:0 mới rơi đúng y=H-h-3%H như render.
        // Với template flow thì paddingBottom vẫn là cơ chế đúng.
        // Đợt D2 (01/11/2026): subsHidden lấy từ karaoke làm chuẩn,
        // chỉ fallback về field của part khi karaoke không có.
        var _subsHidden = (part.karaoke && part.karaoke.subsHidden !== undefined)
          ? part.karaoke.subsHidden : part.subsHidden;
        // Đợt D4 (CEO quyết giữ accent, 01/11/2026): màu nhấn của part
        // lấy từ host (part.tplAccent, host đọc từ meta.json của
        // template) hoặc từ inputs.accent nếu host truyền tên màu; không
        // có thì vàng #FBBF24 như trước. Đặt lên brollDiv để CSS
        // var(--broll-accent) của template nhận đúng màu của part đó.
        var _accentMap = { gold: '#FBBF24', red: '#EF4444', cyan: '#22D3EE',
          green: '#22C55E', pink: '#F472B6', purple: '#A78BFA', orange: '#FB923C' };
        var _accentName = part.tplAccent || (part.tplInputs && part.tplInputs.accent);
        brollDiv.style.setProperty('--broll-accent',
          (_accentName && _accentMap[_accentName]) || '#FBBF24');
        var _isEdge3 = (part.templateId === 'clip-caption' || _subsHidden === false);
        brollDiv.style.paddingBottom = _isEdge3
          ? Math.round(data.H * 0.03) + 'px'
          : Math.round(data.H * (data.H > data.W ? 0.20 : 0.07)) + 'px';
        brollDiv.style.bottom = (part.templateId === 'clip-caption')
          ? Math.round(data.H * 0.03) + 'px' : '0px';
        brollDiv.style.display = 'flex';
        return;
      }
    }
    brollDiv.style.display = 'none';
    brollDiv.style.bottom = '0px';
    brollDiv.dataset.pid = '';
  }

  // Gán src chỉ khi ảnh của layer thật sự đổi — gán lại cùng một URL
  // mỗi khung hình buộc trình duyệt xử lý lại ảnh, thêm một nguồn giật.
  function setImgOnly(img, src) {
    if (img.dataset.cur !== src) {
      img.dataset.cur = src;
      img.src = src;
    }
  }

  // Blur-fill 3:4: media ngang/vuông trong khung dọc thì chuyển layer
  // sang composite (nền mờ + cửa sổ nét CỐ ĐỊNH), ngược lại giữ full
  // như cũ. Ảnh quyết định theo kích thước thật (naturalWidth/Height)
  // vì preview data không kèm tỉ lệ ảnh; video quyết định theo
  // videoW/H trong data nếu có, không thì theo metadata khi tải xong
  // (trước đó tạm coi là ngang khi khung dọc).
  function updateLayerMode(lo) {
    var isVideo = lo.media === 'video';
    var w = isVideo ? lo.mediaW : lo.img.naturalWidth;
    var h = isVideo ? lo.mediaH : lo.img.naturalHeight;
    var comp = false;
    if (data && data.H > data.W) {
      comp = (w > 0 && h > 0) ? (w >= h) : true;
    }
    if (comp !== lo.composite) {
      lo.composite = comp;
      lo.img.dataset.anim = '';
      lo.fgImg.dataset.anim = '';
    }
    var show = function (el, on) { el.style.display = on ? '' : 'none'; };
    if (isVideo) {
      show(lo.img, false); show(lo.bgImg, false); show(lo.fgImg, false);
      if (comp) {
        if (lo.vid.dataset.cur) setVideoSrc(lo, lo.vid.dataset.cur);
        show(lo.vid, false); show(lo.bgVid, true); show(lo.fgWrap, true); show(lo.fgVid, true);
      } else {
        show(lo.vid, true); show(lo.bgVid, false); show(lo.fgWrap, false); show(lo.fgVid, false);
      }
    } else {
      show(lo.vid, false); show(lo.bgVid, false); show(lo.fgVid, false);
      if (comp) {
        setImgOnly(lo.bgImg, lo.img.dataset.cur);
        setImgOnly(lo.fgImg, lo.img.dataset.cur);
        show(lo.img, false); show(lo.bgImg, true); show(lo.fgWrap, true); show(lo.fgImg, true);
      } else {
        show(lo.img, true); show(lo.bgImg, false); show(lo.fgWrap, false); show(lo.fgImg, false);
      }
    }
  }

  function setVideoSrc(lo, src) {
    var vids = [lo.vid, lo.bgVid, lo.fgVid];
    for (var i = 0; i < vids.length; i++) {
      if (vids[i].dataset.cur !== src) {
        vids[i].dataset.cur = src;
        vids[i].src = src;
      }
    }
  }

  function setMedia(lo, part) {
    if (part.video) {
      lo.media = 'video';
      lo.mediaW = part.videoW || 0;
      lo.mediaH = part.videoH || 0;
      setVideoSrc(lo, part.video);
      var onMeta = function () {
        if (lo.vid.videoWidth > 0) {
          lo.mediaW = lo.vid.videoWidth;
          lo.mediaH = lo.vid.videoHeight;
        }
        updateLayerMode(lo);
      };
      lo.vid.onloadedmetadata = onMeta;
      if (lo.vid.readyState >= 1) onMeta();
    } else {
      lo.media = 'image';
      lo.mediaW = 0; lo.mediaH = 0;
      var img = lo.img;
      var src = part.image || '';
      if (img.dataset.cur !== src) {
        img.dataset.cur = src;
        img.src = src;
        img.onload = function () { updateLayerMode(lo); };
      }
    }
    updateLayerMode(lo);
  }

  // ---- Motion CSS: JS chỉ dựng animation, trình duyệt nội suy ----
  // runningMode = false (mặc định): seekTo lái animation bằng delay âm
  // + paused — khung hình luôn đúng, tương thích host cũ và trang
  // frame-capture. runningMode = true (host gọi setPlaying(true) khi
  // phát): animation chạy thật trên compositor; seekTo cùng part không
  // chạm vào animation nữa, chỉ còn phụ đề/template/crossfade.
  var runningMode = false, lastT = 0, curPartId = null;

  function applyMotion(lo, part, elapsedSec, resync) {
    if (part.video) return; // video tự chạy, không gắn Ken Burns (render cũng không)
    var comp = lo.composite;
    var img = comp ? lo.fgImg : lo.img;
    var name = (comp ? COMP_KEYFRAMES : MOTION_KEYFRAMES)[motionIndexForPart(part)][0];
    var dur = Math.max(part.end - part.start, 0.01);
    var key = name + '|' + dur.toFixed(3);
    if (img.dataset.anim !== key) {
      img.dataset.anim = key;
      img.style.animationName = name;
      img.style.animationDuration = dur + 's';
      img.style.animationTimingFunction = MOTION_EASING;
      img.style.animationFillMode = 'both';
      img.style.animationIterationCount = '1';
      resync = true;
    }
    if (!resync) return;
    img.style.animationDelay = (-elapsedSec) + 's';
    img.style.animationPlayState = runningMode ? 'running' : 'paused';
  }

  function setOpacity(layer, v) {
    if (layer.style.opacity !== v) layer.style.opacity = v;
  }

  function pauseVideos(lo) {
    if (!lo) return;
    var vids = [lo.vid, lo.bgVid, lo.fgVid];
    for (var i = 0; i < vids.length; i++) {
      try { vids[i].pause(); } catch (e) {}
    }
  }

  // Đồng bộ video b-roll với mốc timeline: chỉ đặt lại currentTime khi
  // tua/nhảy part hoặc khi đang tạm dừng; khi đang phát thì để video
  // tự chạy (đặt lại mỗi khung hình sẽ giật). Video luôn tắt tiếng.
  function syncVideo(lo, part, t, resync) {
    if (!part.video || lo.media !== 'video') return;
    var vids = [lo.vid, lo.bgVid, lo.fgVid];
    var dur = lo.vid.duration;
    var target = t - part.start;
    if (isFinite(dur) && dur > 0) target = target % dur;
    if (target < 0) target = 0;
    for (var i = 0; i < vids.length; i++) {
      var v = vids[i];
      try {
        if (resync && Math.abs((v.currentTime || 0) - target) > 0.1) v.currentTime = target;
        if (runningMode) {
          var pr = v.play();
          if (pr && pr.catch) pr.catch(function () {});
        } else {
          v.pause();
        }
      } catch (e) {}
    }
  }

  function seekTo(t) {
    if (!data || !data.parts.length) return;
    var parts = data.parts;
    var idx = findPart(t);
    var part = parts[idx];
    var prev = idx > 0 ? parts[idx - 1] : null;
    var inTrans = prev && (t - part.start) < TRANS;
    var tp = inTrans ? (t - part.start) / TRANS : 1;
    // Nhảy timeline (tua ngược, nhảy part, hoặc bước thời gian lớn) thì
    // animation đang chạy cũng phải đồng bộ lại, kể cả cùng part.
    var jumped = (part.id !== curPartId) || (t < lastT - 0.01) || (t - lastT > 1.0);
    curPartId = part.id;
    lastT = t;

    if (inTrans) {
      setMedia(layerObjA, prev);
      setMedia(layerObjB, part);
      applyMotion(layerObjA, prev, t - prev.start, !runningMode || jumped);
      applyMotion(layerObjB, part, t - part.start, !runningMode || jumped);
      syncVideo(layerObjA, prev, t, false);
      syncVideo(layerObjB, part, t, !runningMode || jumped);
      setOpacity(layerA, String(1 - tp));
      setOpacity(layerB, String(tp));
    } else {
      setMedia(layerObjB, part);
      applyMotion(layerObjB, part, t - part.start, !runningMode || jumped);
      syncVideo(layerObjB, part, t, !runningMode || jumped);
      pauseVideos(layerObjA);
      setOpacity(layerA, '0');
      setOpacity(layerB, '1');
    }

    renderBroll(part, t);
    renderSubs(part, t);
  }

  function setPlaying(p) {
    runningMode = !!p;
    // Đồng bộ lại animation của layer đang hiện về đúng mốc lastT rồi
    // mới đổi trạng thái chạy/dừng, tránh ảnh nhảy khung khi bấm phát.
    if (layerObjB) {
      var idx = findPart(lastT);
      var part = data.parts[idx];
      applyMotion(layerObjB, part, lastT - part.start, true);
      syncVideo(layerObjB, part, lastT, true);
    }
  }

  function mount(stageEl, d) {
    stage = stageEl;
    data = d;
    ready = false;
    runningMode = false;
    lastT = 0;
    curPartId = null;
    buildDom();
    // preload ảnh
    var imgs = [];
    for (var i = 0; i < data.parts.length; i++) {
      if (data.parts[i].image && imgs.indexOf(data.parts[i].image) < 0) imgs.push(data.parts[i].image);
    }
    if (!imgs.length) { ready = true; return; }
    var loaded = 0;
    for (var j = 0; j < imgs.length; j++) {
      var im = new Image();
      im.onload = im.onerror = function () { if (++loaded >= imgs.length) ready = true; };
      im.src = imgs[j];
    }
  }

  global.VieNeuRender = {
    mount: mount,
    seekTo: seekTo,
    setPlaying: setPlaying,
    getDuration: function () {
      return (data && data.parts.length) ? data.parts[data.parts.length - 1].end : 0;
    },
    isReady: function () { return ready; }
  };
})(window);
