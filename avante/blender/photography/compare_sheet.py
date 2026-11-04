"""Reference-vs-render comparison sheet (QC): each row = reference | render, scaled to the same height.

    blender -b --factory-startup --python photography/compare_sheet.py -- OUT.png ROW_H ref1.png render1.png [ref2 render2 ...]
"""
import bpy, sys, numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
out, H = argv[0], int(argv[1]); pairs = list(zip(argv[2::2], argv[3::2]))


def load(p):
    im = bpy.data.images.load(p); w, h = im.size
    a = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(a); a = a.reshape(h, w, 4)[::-1]
    bpy.data.images.remove(im); return a


def resize(a, w, h):
    Hh, W = a.shape[:2]
    ys = np.clip(((np.arange(h) + 0.5) * Hh / h).astype(int), 0, Hh - 1); xs = np.clip(((np.arange(w) + 0.5) * W / w).astype(int), 0, W - 1)
    return a[ys][:, xs]


rows = []
for r, p in pairs:
    ims = []
    for f in (r, p):
        a = load(f); h, w = a.shape[:2]; ims.append(resize(a, int(round(w * H / h)), H))
    gap = np.ones((H, 24, 4), np.float32) * 0.95
    rows.append(np.concatenate([ims[0], gap, ims[1]], 1))
Wm = max(r.shape[1] for r in rows)
rows = [np.concatenate([r, np.ones((H, Wm - r.shape[1], 4), np.float32) * 0.95], 1) for r in rows]
sep = np.ones((24, Wm, 4), np.float32) * 0.95
sheet = np.concatenate(sum([[r, sep] for r in rows], [])[:-1], 0); sheet[..., 3] = 1
h, w = sheet.shape[:2]
im = bpy.data.images.new('sheet', w, h, alpha=True); im.pixels.foreach_set(np.ascontiguousarray(sheet[::-1]).ravel())
im.filepath_raw = out; im.file_format = 'PNG'; im.save(); print('SHEET', out, w, h)
