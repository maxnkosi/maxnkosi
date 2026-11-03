# D study: silhouette edge x per row (left/right) near the base of raw2 / raw1 to read the heel bevel
import bpy, numpy as np
R = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/references/bottle/'
for n, y0, y1 in (('raw2.png', 150, 372), ('raw1.png', 120, 392)):
    im = bpy.data.images.load(R + n); w, h = im.size
    a = np.array(im.pixels[:]).reshape(h, w, 4)[::-1]; L = 0.2126*a[...,0] + 0.7152*a[...,1] + 0.0722*a[...,2]
    print(n, w, h)
    for y in range(y0, y1, 3 if n == 'raw2.png' else 4):
        dark = np.where(L[y] < 0.9)[0]
        dark = dark[(dark > w*0.2) & (dark < w*0.8)]
        if len(dark): print(f'  y={y:3d}  left={dark.min():3d} right={dark.max():3d} width={dark.max()-dark.min():3d}')
        else: print(f'  y={y:3d}  -')
