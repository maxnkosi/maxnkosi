"""raw7 (48Gin, matte, front): track the face-to-shoulder edge highlight per column -> arch height profile."""
import numpy as np
a = np.load('raw7_rgba.npy'); L = a[..., :3].mean(-1)
yb, s = 797.5, 89.3 / 305.6; xc = (246 + 551) / 2
k = np.ones(5) / 5
Y0, Y1 = 255, 318
for x in list(range(258, 400, 6)) + list(range(400, 546, 6)):
    col = L[Y0:Y1, x - 2:x + 3].mean(1); cs = np.convolve(col, k, 'same'); cs[:2] = cs[2]; cs[-2:] = cs[-3]
    inside = np.where(cs < 0.85)[0]
    if len(inside) == 0: continue
    i0 = inside[0] + 5
    if i0 >= len(cs) - 3: continue
    seg = cs[i0:]; ip = i0 + int(np.argmax(seg))
    print('x %+6.1f mm  peak y %3d  z %6.1f  L %3d' % ((x - xc) * s, Y0 + ip, (yb - Y0 - ip) * s, int(cs[ip] * 255)))
