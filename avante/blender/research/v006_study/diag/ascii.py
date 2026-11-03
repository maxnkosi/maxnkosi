import numpy as np, sys
a = np.load(sys.argv[1] + '_rgba.npy'); thr = float(sys.argv[2]); step = int(sys.argv[3])
g = a[..., :3].mean(-1)
h, w = g.shape
for y in range(0, h, step):
    row = g[y, ::max(1, step//2)]
    print('%4d ' % y + ''.join('#' if v < thr*0.6 else ('+' if v < thr else '.') for v in row))
