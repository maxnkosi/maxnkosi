# D study: luminance row scans of reference photos (run: Blender -b --factory-startup -P d_rowscan.py)
import bpy, numpy as np, os
R = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/references/bottle/'
def load(n):
    im = bpy.data.images.load(R + n); w, h = im.size
    a = np.array(im.pixels[:]).reshape(h, w, 4)[::-1]  # top-down
    return (0.2126*a[...,0] + 0.7152*a[...,1] + 0.0722*a[...,2])
for n, rows, x0, x1 in (('raw7.png', (450, 550, 650), 225, 580), ('raw2.png', (200, 250), 190, 350), ('raw1.png', (250, 300), 90, 230), ('raw5.png', (450, 520), 115, 380)):
    L = load(n)
    for y in rows:
        seg = L[y, x0:x1]
        print(n, 'y', y, 'x0', x0)
        print(' '.join('%02d' % int(v * 99) for v in seg))
