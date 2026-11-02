import glbUrl from '../public/models/currency-stream-logo.glb?inline';
import { mountCurrencyStreamLogo } from './logo.js';

const b64 = glbUrl.split(',')[1];
const bin = atob(b64);
const buf = new Uint8Array(bin.length);
for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i);

const el = document.getElementById('logo');
const logo = mountCurrencyStreamLogo(el, { modelData: buf.buffer, view: 'front', material: import.meta.env.VITE_MATERIAL ?? 'branded', background: '#ffffff' });
logo.ready.then(() => { window.__logoReady = true; });
document.querySelectorAll('[data-view]').forEach((b) => b.addEventListener('click', () => {
  logo.setView(b.dataset.view);
  document.querySelectorAll('[data-view]').forEach((x) => x.setAttribute('aria-pressed', String(x === b)));
}));
