import numpy as np, sys
name, thr, x0, x1 = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
y0, y1, st = int(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
a = np.load(name + '_rgba.npy'); g = a[..., :3].mean(-1)
for y in range(y0, y1, st):
    r = g[y, x0:x1]; d = np.where(r < thr)[0]
    if len(d) == 0: print(y, '-'); continue
    runs = []; s = d[0]; p = d[0]
    for v in d[1:]:
        if v != p + 1: runs.append((s + x0, p + x0)); s = v
        p = v
    runs.append((s + x0, p + x0))
    print('%d L=%d R=%d W=%d C=%.1f' % (y, d[0] + x0, d[-1] + x0, d[-1] - d[0] + 1, (d[0] + d[-1]) / 2 + x0),
          ' '.join('%d-%d' % rr for rr in runs[:3]), '|', ' '.join('%d-%d' % rr for rr in runs[-3:]))
