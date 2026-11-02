import { mountCurrencyStreamLogo } from './logo.js';

// Demo page: ?view=front|oblique or ?yaw=&pitch=
const q = new URLSearchParams(location.search);
const opts = q.has('yaw') ? { yaw: Number(q.get('yaw')), pitch: Number(q.get('pitch') ?? 0) } : { view: q.get('view') ?? 'front' };
opts.material = q.get('material') ?? 'branded'; // ?material=clear
opts.panel = q.get('panel') !== '0';           // ?panel=0 hides the settings panel
if (q.has('bg')) opts.background = '#' + q.get('bg');
const el = document.getElementById('logo');
const logo = mountCurrencyStreamLogo(el, opts);
window.__logo = logo; // handy for debugging: __logo.settings, __logo.update()
logo.ready.then(() => { window.__logoReady = true; });
