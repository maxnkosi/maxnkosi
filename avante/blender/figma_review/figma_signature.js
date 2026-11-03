// Avante design review: per-layer signature of the editable artwork components.
// Paste into the Figma MCP tool `use_figma` (file JcxeRDhCrtgZUXhTWQn2hV). Read-only: it changes nothing.
// Output: { C05: { "0/15": {id, name, sig}, ... }, ... }. Paths are child indexes under the component,
// so they match between a baseline and a later run. Compare with diff_review.py.
const ART = {C01: '62:31', C05: '64:31', C06: '64:442', C07: '64:897', C10: '64:1388'};
const ONLY = null;   // e.g. ['C05'] to check one concept
function h(s) { let x = 2166136261; for (let i = 0; i < s.length; i++) { x ^= s.charCodeAt(i); x = Math.imul(x, 16777619) >>> 0; } return x.toString(16); }
function sig(n) {
  const p = {t: n.type, nm: n.name, v: n.visible, o: +((n.opacity ?? 1).toFixed(4))};
  if ('relativeTransform' in n) p.tf = n.relativeTransform.flat().map(v => +v.toFixed(3));
  if ('width' in n) { p.w = +n.width.toFixed(2); p.h = +n.height.toFixed(2); }
  for (const k of ['fills', 'strokes', 'effects']) if (k in n && n[k] !== figma.mixed) p[k] = h(JSON.stringify(n[k]));
  if ('strokeWeight' in n && n.strokeWeight !== figma.mixed) p.sw = n.strokeWeight;
  if ('blendMode' in n) p.bm = n.blendMode;
  if ('isMask' in n) p.mk = n.isMask;
  if (n.type === 'BOOLEAN_OPERATION') p.bo = n.booleanOperation;
  if ('vectorPaths' in n && n.type !== 'TEXT') p.vp = h(JSON.stringify(n.vectorPaths));
  if (n.type === 'TEXT') {
    p.ch = h(n.characters);
    p.st = h(JSON.stringify(n.getStyledTextSegments(['fontName', 'fontSize', 'letterSpacing', 'lineHeight', 'fills', 'textCase'])));
    p.al = n.textAlignHorizontal;
  }
  return h(JSON.stringify(p));
}
const out = {};
for (const [cid, id] of Object.entries(ART)) {
  if (ONLY && !ONLY.includes(cid)) continue;
  const comp = await figma.getNodeByIdAsync(id); const rows = {};
  const walk = (n, path) => { rows[path] = {id: n.id, name: n.name, sig: sig(n)}; if ('children' in n) n.children.forEach((c, i) => walk(c, path + '/' + i)); };
  comp.children.forEach((c, i) => walk(c, String(i)));
  out[cid] = rows;
}
return out;
