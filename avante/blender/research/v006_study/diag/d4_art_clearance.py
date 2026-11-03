"""Topmost artwork (foil + emboss masks) near the crown, in dieline mm. Read-only.
Usage: Blender -b --factory-startup -P d4_art_clearance.py"""
import bpy, numpy as np, os
T = '/Users/maxhlomendlini/Documents/Avante/avante/blender/textures'
A = dict(x=-121.734, y=-12.414, w=243.469, h=101.258)
for f in ('MASK-FOIL-01__LBL-FRONT-01.png', 'COLOR__LBL-FRONT-01_v005.png'):
    im = bpy.data.images.load(os.path.join(T, f)); w, h = im.size
    px = np.array(im.pixels[:]).reshape(h, w, 4)[::-1]  # row 0 = top
    if 'MASK' in f: m = px[..., 0] > 0.5
    else:
        lum = px[..., :3].mean(-1); bg = np.median(lum[int(h * 0.3):int(h * 0.5), int(w * 0.45):int(w * 0.55)])
        m = np.abs(lum - bg) > 0.08
    for x0, x1 in ((-10, 10), (-31.6, 31.6), (-47.3, 47.3)):
        c0, c1 = int((x0 - A['x']) / A['w'] * w), int((x1 - A['x']) / A['w'] * w)
        rows = np.where(m[:, c0:c1].any(1))[0]
        # skip the bleed above the trim: first art row below dieline y = -10.414 + 0.5
        ys = A['y'] + rows / h * A['h']; ys = ys[ys > -9.9]
        print('ART', f, (x0, x1), 'size', (w, h), 'topmost art dieline y =', round(float(ys.min()), 2) if len(ys) else None)
