import numpy as np, sys
name, thr, x0, x1 = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
y0, y1 = int(sys.argv[5]), int(sys.argv[6])
a = np.load(name + '_rgba.npy'); g = a[..., :3].mean(-1)
for y in range(y0, y1):
    r = g[y, x0:x1]; d = np.where(r < thr)[0]
    if len(d) == 0: print(y, '-'); continue
    # list dark runs
    runs = []; s = d[0]; p = d[0]
    for v in d[1:]:
        if v != p + 1: runs.append((s + x0, p + x0)); s = v
        p = v
    runs.append((s + x0, p + x0))
    print(y, 'L=%d R=%d W=%d' % (d[0] + x0, d[-1] + x0, d[-1] - d[0] + 1), runs[:3], '...', runs[-3:] if len(runs) > 3 else '')
