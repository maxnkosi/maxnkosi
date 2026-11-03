"""Write A_profiles.svg: shoulder half-width overlays + arch heights (no matplotlib; hand SVG)."""
import json, numpy as np
D = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
ref = json.load(open(D + 'ref_profiles.json')); mod = json.load(open(D + 'model_metrics.json'))
W, H = 1100, 560
def panel(x0, y0, w, h, xr, yr):
    X = lambda v: x0 + (v - xr[0]) / (xr[1] - xr[0]) * w
    Y = lambda v: y0 + h - (v - yr[0]) / (yr[1] - yr[0]) * h
    return X, Y
out = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" font-family="Helvetica" font-size="12">' % (W, H),
       '<rect width="100%" height="100%" fill="white"/>']
# panel A: z (vertical) vs half-width (horizontal), z 125..195
X, Y = panel(60, 30, 420, 480, (15, 48), (125, 195))
for v in range(15, 49, 5): out.append('<line x1="%.1f" y1="30" x2="%.1f" y2="510" stroke="#eee"/><text x="%.1f" y="525" text-anchor="middle">%d</text>' % (X(v), X(v), X(v), v))
for v in range(125, 196, 10): out.append('<line x1="60" y1="%.1f" x2="480" y2="%.1f" stroke="#eee"/><text x="55" y="%.1f" text-anchor="end">%d</text>' % (Y(v), Y(v), Y(v) + 4, v))
out.append('<text x="270" y="545" text-anchor="middle">front half-width (mm)   |   z above base (mm)</text>')
def poly(pts, col, dash=''):
    return '<polyline fill="none" stroke="%s" stroke-width="1.6" %s points="%s"/>' % (col, ('stroke-dasharray="%s"' % dash) if dash else '', ' '.join('%.1f,%.1f' % (X(r), Y(z)) for z, r in pts))
cols = {'raw2': '#000', 'raw1': '#888', 'raw7': '#1a9e8f'}
for k, c in cols.items():
    Z, Wd = ref[k]['Z'], ref[k]['W']; pts = [(z, w / 2) for z, w in zip(Z, Wd) if 125 <= z <= 195]
    out.append(poly(pts, c))
out.append(poly([(z, w / 2) for z, w in mod['v005']['front_fine'] if 125 <= z <= 195], '#d62728', '6,3'))
out.append(poly([(z, w / 2) for z, w in mod['v006']['front_fine'] if 125 <= z <= 195], '#1f5bd6', '2,2'))
leg = [('raw2 (Imperial, primary)', '#000', ''), ('raw1 (Imperial, cork)', '#888', ''), ('raw7 (48Gin, width-scaled)', '#1a9e8f', ''),
       ('v005 front silhouette', '#d62728', '6,3'), ('v006 front silhouette', '#1f5bd6', '2,2')]
for i, (t, c, d) in enumerate(leg):
    out.append('<line x1="80" y1="%d" x2="110" y2="%d" stroke="%s" stroke-width="2" %s/><text x="116" y="%d">%s</text>' % (50 + 16 * i, 50 + 16 * i, c, ('stroke-dasharray="%s"' % d) if d else '', 54 + 16 * i, t))
out.append('<text x="60" y="20" font-weight="bold">A. Shoulder silhouette (front view)</text>')
# panel B: arch height on the front face vs lateral offset y from the panel centre
X, Y = panel(600, 30, 440, 480, (0, 46), (136, 160))
for v in range(0, 47, 5): out.append('<line x1="%.1f" y1="30" x2="%.1f" y2="510" stroke="#eee"/><text x="%.1f" y="525" text-anchor="middle">%d</text>' % (X(v), X(v), X(v), v))
for v in range(136, 161, 2): out.append('<line x1="600" y1="%.1f" x2="1040" y2="%.1f" stroke="#eee"/><text x="595" y="%.1f" text-anchor="end">%d</text>' % (Y(v), Y(v), Y(v) + 4, v))
out.append('<text x="820" y="545" text-anchor="middle">lateral offset from panel centre (mm; face/chamfer edge at 37.8)</text>')
out.append('<line x1="%.1f" y1="30" x2="%.1f" y2="510" stroke="#999" stroke-dasharray="4,3"/>' % (X(37.75), X(37.75)))
raw7 = [(0.4, 153.0), (2.5, 153.0), (6.0, 153.0), (9.5, 152.7), (13.0, 151.5), (16.5, 151.2), (20.0, 150.6), (23.5, 149.5), (27.0, 148.3), (30.5, 146.5), (34.0, 144.8), (35.8, 143.9), (37.5, 142.5)]
arch6 = [(r[0], r[3]) for r in mod['arch']['v006']]
cut6 = [(0, 153.3), (h2 := 22.2, 147.9), (37.75, 140.1), (41.1, 139.7)]
def p2(pts, col, dash='', mk=False):
    s = '<polyline fill="none" stroke="%s" stroke-width="1.8" %s points="%s"/>' % (col, ('stroke-dasharray="%s"' % dash) if dash else '', ' '.join('%.1f,%.1f' % (X(a), Y(b)) for a, b in pts))
    if mk: s += ''.join('<circle cx="%.1f" cy="%.1f" r="2.5" fill="%s"/>' % (X(a), Y(b), col) for a, b in pts)
    return s
out.append(p2(raw7, '#1a9e8f', '', True))
out.append(p2([(a, b + 2.2) for a, b in raw7], '#1a9e8f', '5,3'))
out.append(p2(arch6, '#1f5bd6', '', True))
out.append(p2(cut6, '#1f5bd6', '2,2'))
out.append(p2([(0, 155.5), (45, 155.5)], '#d62728', '6,3'))
out.append('<circle cx="%.1f" cy="%.1f" r="5" fill="none" stroke="#000" stroke-width="2"/>' % (X(37.75), Y(147.3)))
leg = [('raw7 edge highlight (measured, lit half)', '#1a9e8f', ''), ('raw7 shifted +2.2 mm to raw2 shoulder height', '#1a9e8f', '5,3'),
       ('v006 visible edge (surface 20 deg off vertical)', '#1f5bd6', ''), ('v006 carving onset (0.2 mm cut)', '#1f5bd6', '2,2'),
       ('v005 straight crease', '#d62728', '6,3')]
for i, (t, c, d) in enumerate(leg):
    out.append('<line x1="620" y1="%d" x2="650" y2="%d" stroke="%s" stroke-width="2" %s/><text x="656" y="%d">%s</text>' % (420 + 16 * i, 420 + 16 * i, c, ('stroke-dasharray="%s"' % d) if d else '', 424 + 16 * i, t))
out.append('<circle cx="626" cy="500" r="5" fill="none" stroke="#000" stroke-width="2"/><text x="656" y="504">raw2: top of face/chamfer edge line (z 147.3)</text>')
out.append('<text x="600" y="20" font-weight="bold">B. Arch: height of the face-to-shoulder edge across the front face</text>')
out.append('</svg>')
open(D + 'A_profiles.svg', 'w').write('\n'.join(out)); print('ok')
