import { mountCurrencyStreamLogo } from './logo.js';

// Demo page: ?view=front|oblique or ?yaw=&pitch=
const q = new URLSearchParams(location.search);
const opts = q.has('yaw') ? { yaw: Number(q.get('yaw')), pitch: Number(q.get('pitch') ?? 0) } : { view: q.get('view') ?? 'front' };
const el = document.getElementById('logo');
mountCurrencyStreamLogo(el, opts).ready.then(() => { window.__logoReady = true; });
