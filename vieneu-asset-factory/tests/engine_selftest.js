// Self-test offline cho lib/render-engine.js (không cần trình duyệt/app).
// Mô phỏng DOM tối thiểu, mount engine với dữ liệu dạng previewtest001,
// seek qua các part rồi in hình học thật của từng lớp:
//  - fgWrap (cửa sổ 3:4) có cố định không, có bao giờ bị gắn animation không
//  - phần tử nào nhận animation (phải là ảnh bên trong, không phải cửa sổ)
//  - box ảnh dưới transform ở hai đầu keyframe có phủ kín cửa sổ không
//  - part video hiện <video> nào, box video ra sao
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const DIMS = {
  'img-land': [1200, 627],
  'img-sq': [627, 627],
  'img-port': [800, 1200],
  'vid-river': [1920, 1080],
};
const DUR = { 'vid-river': 15 };

function parseCssText(el, text) {
  text.split(';').forEach((pair) => {
    const i = pair.indexOf(':');
    if (i > 0) el._style[pair.slice(0, i).trim()] = pair.slice(i + 1).trim();
  });
}

class El {
  constructor(tag) {
    this.tag = tag;
    this.children = [];
    this._style = {};
    this.dataset = {};
    this.textContent = '';
    this._innerHTML = '';
    this._src = '';
    this.onload = null;
    this.onerror = null;
    this.onloadedmetadata = null;
    this.currentTime = 0;
    this.duration = NaN;
    this.readyState = 0;
    this.videoWidth = 0;
    this.videoHeight = 0;
    this.naturalWidth = 0;
    this.naturalHeight = 0;
    this.paused = true;
    this.muted = false;
    this.loop = false;
    this.playsInline = false;
    this.preload = '';
    const self = this;
    this.style = new Proxy(this._style, {
      set(t, k, v) { if (k === 'cssText') parseCssText(self, v); else t[k] = v; return true; },
      get(t, k) {
        if (k === 'cssText') return '';
        if (k === 'setProperty') return (kk, vv) => { t[kk] = vv; };
        return t[k];
      },
    });
    Object.defineProperty(this, 'innerHTML', {
      get() { return this._innerHTML; },
      set(v) { this._innerHTML = v; this.children = []; },
    });
    Object.defineProperty(this, 'src', {
      get() { return this._src; },
      set(v) {
        this._src = v;
        const d = DIMS[v];
        if (this.tag === 'img' && d) {
          this.naturalWidth = d[0]; this.naturalHeight = d[1];
          if (this.onload) this.onload();
        } else if (this.tag === 'video' && d) {
          this.videoWidth = d[0]; this.videoHeight = d[1];
          this.duration = DUR[v] || NaN;
          this.readyState = 4;
          if (this.onloadedmetadata) this.onloadedmetadata();
        }
      },
    });
  }
  appendChild(c) { this.children.push(c); c.parentNode = this; return c; }
  querySelectorAll() { return []; }
  play() { this.paused = false; return { catch() {} }; }
  pause() { this.paused = true; }
}

const stage = new El('div');
const sandbox = {
  window: {},
  document: { createElement: (tag) => new El(tag) },
  Image: class extends El { constructor() { super('img'); } },
  console,
};
sandbox.window = sandbox;
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '..', 'lib', 'render-engine.js'), 'utf8'), sandbox);
const R = sandbox.window.VieNeuRender;

const data = {
  W: 720, H: 1280,
  parts: [
    { id: 'scene1-part-1', start: 0, end: 3.24, image: 'img-land', motion: 'zoom_out', karaoke: { lines: [] } },
    { id: 'scene2-part-1', start: 3.24, end: 6.89, image: 'img-sq', motion: 'pan_up', karaoke: { lines: [] } },
    { id: 'scene3-part-1', start: 6.89, end: 10.04, image: '', video: 'vid-river', videoW: 1920, videoH: 1080, motion: 'pan_left', karaoke: { lines: [] } },
    { id: 'scene4-part-1', start: 10.04, end: 13.31, image: 'img-port', motion: 'pan_right', karaoke: { lines: [] } },
  ],
};
R.mount(stage, data);

function layerDivs() {
  return stage.children.filter((c) => c.tag === 'div' && c.children.some((k) => k.tag === 'img'));
}
function currentLayer() {
  const ls = layerDivs();
  return ls.find((l) => l.style.opacity === '1') || ls[ls.length - 1];
}
function kids(layer) {
  const o = {};
  for (const c of layer.children) {
    if (c.tag === 'img' && !o.img) o.img = c;
    else if (c.tag === 'video' && !o.vid) o.vid = c;
    else if (c.tag === 'img') o.bgImg = c;
    else if (c.tag === 'video') o.bgVid = c;
    else if (c.tag === 'div') o.fgWrap = c;
  }
  // phân biệt bg theo style position absolute + filter blur
  for (const c of layer.children) {
    if (c.tag === 'img' && c.style.filter) o.bgImg = c;
    if (c.tag === 'video' && c.style.filter) o.bgVid = c;
  }
  if (o.fgWrap) {
    for (const c of o.fgWrap.children) {
      if (c.tag === 'img') o.fgImg = c;
      if (c.tag === 'video') o.fgVid = c;
    }
  }
  return o;
}
function num(v) { const n = parseFloat(v); return isNaN(n) ? 0 : n; }

// Parse keyframes từ <style> engine tự chèn
const styleText = stage.children.find((c) => c.tag === 'style').textContent;
const KEYS = {};
styleText.replace(/@keyframes\s+(\S+)\{from\{transform:([^}]*)\}to\{transform:([^}]*)\}\}/g, (_, name, from, to) => {
  KEYS[name] = [from, to];
});
function parseTf(s) {
  const sc = /scale\(([\d.]+)\)/.exec(s);
  const tx = /translateX\((-?[\d.]+)%\)/.exec(s);
  const ty = /translateY\((-?[\d.]+)%\)/.exec(s);
  return { s: sc ? parseFloat(sc[1]) : 1, tx: tx ? parseFloat(tx[1]) : 0, ty: ty ? parseFloat(ty[1]) : 0 };
}
function coverage(box, tf, win) {
  // box: {left, top, w, h} trong tọa độ wrap; win: {x0,x1,y0,y1}
  const cx = box.left + box.w / 2, cy = box.top + box.h / 2;
  const sx = (tf.tx / 100) * box.w * tf.s, sy = (tf.ty / 100) * box.h * tf.s;
  const x0 = cx - (box.w * tf.s) / 2 + sx, x1 = cx + (box.w * tf.s) / 2 + sx;
  const y0 = cy - (box.h * tf.s) / 2 + sy, y1 = cy + (box.h * tf.s) / 2 + sy;
  return { x0: Math.round(x0), x1: Math.round(x1), y0: Math.round(y0), y1: Math.round(y1),
           covers: x0 <= win.x0 + 0.5 && x1 >= win.x1 - 0.5 && y0 <= win.y0 + 0.5 && y1 >= win.y1 - 0.5 };
}

for (const t of [0.5, 1.6, 3.5, 5.0, 7.5, 11.0]) {
  R.seekTo(t);
  const L = kids(currentLayer());
  const comp = L.fgWrap && L.fgWrap.style.display !== 'none';
  console.log(`\n=== seekTo ${t}s ===`);
  console.log(`  composite=${comp}`);
  if (L.fgWrap) {
    console.log(`  fgWrap: left=${L.fgWrap.style.left} right=${L.fgWrap.style.right} top=${L.fgWrap.style.top} height=${L.fgWrap.style.height} overflow=${L.fgWrap.style.overflow} display=${L.fgWrap.style.display} animationName=${L.fgWrap.style.animationName || '(none)'}`);
  }
  const animEl = [L.img, L.fgImg, L.vid, L.fgVid].find((e) => e && e.style.animationName);
  console.log(`  animated element: ${animEl ? animEl.tag + ' name=' + animEl.style.animationName : '(none)'}`);
  if (comp && L.fgImg && animEl === L.fgImg) {
    const box = { left: num(L.fgImg.style.left), top: num(L.fgImg.style.top), w: num(L.fgImg.style.width), h: num(L.fgImg.style.height) };
    const win = { x0: 0, x1: 720, y0: 0, y1: 960 };
    const [f, to] = KEYS[L.fgImg.style.animationName];
    console.log(`  fgImg box: left=${box.left} w=${box.w} h=${box.h}`);
    console.log(`  keyframe from: ${f} -> covers=${JSON.stringify(coverage(box, parseTf(f), win))}`);
    console.log(`  keyframe to:   ${to} -> covers=${JSON.stringify(coverage(box, parseTf(to), win))}`);
  }
  if (!comp && L.img && animEl === L.img) {
    const box = { left: 0, top: 0, w: 720, h: 1280 };
    const win = { x0: 0, x1: 720, y0: 0, y1: 1280 };
    const [f, to] = KEYS[L.img.style.animationName];
    console.log(`  img full box 720x1280`);
    console.log(`  keyframe from: ${f} -> covers=${JSON.stringify(coverage(box, parseTf(f), win))}`);
    console.log(`  keyframe to:   ${to} -> covers=${JSON.stringify(coverage(box, parseTf(to), win))}`);
  }
  if (L.vid) {
    console.log(`  video: vid display=${L.vid.style.display} fgVid display=${L.fgVid ? L.fgVid.style.display : 'n/a'} fgVid box=${L.fgVid ? `left=${L.fgVid.style.left} w=${L.fgVid.style.width} h=${L.fgVid.style.height}` : 'n/a'} img display=${L.img.style.display} paused=${L.vid.paused} currentTime=${L.vid.currentTime}`);
  }
}
