"""Reference silhouette metrology (run with Blender's python3.13 + numpy). Sub-pixel outer edges per row."""
import numpy as np, json, sys
D = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
PROFILE_Z = [0, 1, 2, 3.5, 5, 7.5, 10, 20, 40, 60, 80, 100, 120, 140, 145, 150, 152.5, 155, 157.5, 160, 162.5, 165,
             167.5, 170, 172.5, 175, 177.5, 180, 182.5, 185, 188, 190, 215, 216.5, 218, 220, 223, 224.5, 225.7, 226.5, 226.9]
def edges(name, thr, x0, x1, mode='gray'):
    a = np.load(D + name + '_rgba.npy'); rgb = a[..., :3]
    g = rgb.mean(-1) if mode == 'gray' else rgb.min(-1)
    out = {}
    for y in range(g.shape[0]):
        r = g[y, x0:x1]; d = np.where(r < thr)[0]
        if len(d) == 0: continue
        i, j = d[0], d[-1]
        fl = (r[i - 1] - thr) / max(r[i - 1] - r[i], 1e-6) if i > 0 else 0
        fr = (r[j + 1] - thr) / max(r[j + 1] - r[j], 1e-6) if j + 1 < len(r) else 0
        xl, xr = x0 + i - fl, x0 + j + fr
        out[y] = (xl, xr)
    return out
cfg = {  # name: thr, x-window, mode, y_top (glass top edge row), y_base (bottom edge row), plateau rows to skip
    'raw2': (0.9, 150, 400, 'gray', 25.5, 363.5),   # lip top outline first dark row 26; bottom outline last full row 363
    'raw1': (0.9, 60, 260, 'gray', 85.5, 385.5),    # glass top = underside of black bar-top head (row 85/86); base = last row 384/385
    'raw7': (0.85, 200, 600, 'min', None, 797.5),   # 48Gin: top hidden by closure -> scaled by max width only
}
res = {}
for name, (thr, x0, x1, mode, yt, yb) in cfg.items():
    E = edges(name, thr, x0, x1, mode)
    ys = sorted(y for y in E if (yt is None or y >= yt) and y <= yb)
    W = {y: E[y][1] - E[y][0] for y in ys}
    # body max width = median of the 9 widest rows below the neck
    body = [W[y] for y in ys if y > (ys[0] + ys[-1]) / 2 - 0.3 * (ys[-1] - ys[0])]
    wmax = float(np.median(sorted(body)[-9:]))
    if yt is not None: s = 226.9 / (yb - yt)          # mm per px from glass height
    else: s = 89.3 / wmax                             # raw7: scale by raw2 max width
    zw = sorted(((yb - y) * s, W[y] * s, W[y] / wmax) for y in ys)
    Z = np.array([p[0] for p in zw]); Wm = np.array([p[1] for p in zw]); Wr = np.array([p[2] for p in zw])
    # smooth 3-row
    Wm_s = np.convolve(Wm, np.ones(3) / 3, 'same'); Wm_s[0], Wm_s[-1] = Wm[0], Wm[-1]
    table = [(z, float(np.interp(z, Z, Wm_s)), float(np.interp(z, Z, Wm_s)) / (wmax * s)) for z in PROFILE_Z if z <= Z[-1]]
    res[name] = dict(mm_per_px=s, wmax_px=wmax, wmax_mm=wmax * s, height_px=(yb - yt) if yt else None,
                     table=table, Z=Z.tolist(), W=Wm_s.tolist())
    print('==', name, 'mm/px %.4f  wmax %.1f px = %.2f mm  H_px %s' % (s, wmax, wmax * s, (yb - yt) if yt else '-'))
    for z, w, r in table: print('  z %6.1f  W %6.2f  W/Wmax %.3f' % (z, w, r))
json.dump(res, open(D + 'ref_profiles.json', 'w'))
