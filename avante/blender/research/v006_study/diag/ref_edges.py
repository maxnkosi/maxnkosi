# Blender headless: per-row silhouette edges of reference images (dark-on-light or colour-on-white).
import bpy, numpy as np, sys, json, os
R = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/references/bottle/'
OUT = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
res = {}
for name in ['raw1', 'raw2', 'raw7', 'raw5']:
    im = bpy.data.images.load(R + name + '.png')
    w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1]  # top row first
    np.save(OUT + name + '_rgba.npy', a)
    res[name] = (w, h)
print(json.dumps(res))
