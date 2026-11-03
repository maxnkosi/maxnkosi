import numpy as np, sys
name = sys.argv[1]; y0, y1, st = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
a = np.load(name + '_rgba.npy'); rgb = a[..., :3]
# non-background = clearly not white: min channel < 0.85
m = rgb.min(-1) < float(sys.argv[5]) if len(sys.argv) > 5 else rgb.min(-1) < 0.85
for y in range(y0, y1, st):
    d = np.where(m[y])[0]
    if len(d) == 0: print(y, '-'); continue
    print(y, d[0], d[-1], d[-1] - d[0] + 1)
