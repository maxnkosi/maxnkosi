"""Fillet radii and cone straightness from front silhouettes (reference images and model), same method for both."""
import json, numpy as np
D = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
ref = json.load(open(D + 'ref_profiles.json')); mod = json.load(open(D + 'model_metrics.json'))
curves = {k: (np.array(v['Z']), np.array(v['W']) / 2) for k, v in ref.items()}
for k in ('v005', 'v006'):
    a = np.array(mod[k]['front_fine']); curves[k] = (a[:, 0], a[:, 1] / 2)
def fit(Z, R, z0, z1):
    m = (Z >= z0) & (Z <= z1); p = np.polyfit(Z[m], R[m], 1)
    res = R[m] - np.polyval(p, Z[m]); return p, float(np.abs(res).max()), float(res.std())
def vertex(p, q):  # r = p0 z + p1
    z = (q[1] - p[1]) / (p[0] - q[0]); return z, p[0] * z + p[1]
def fillet(Z, R, p, q):
    zv, rv = vertex(p, q)
    d = np.min(np.hypot(Z - zv, R - rv))
    a1, a2 = np.arctan(p[0]), np.arctan(q[0]); phi = abs(a1 - a2)
    return zv, rv, d, np.degrees(phi), d / (1 / np.cos(phi / 2) - 1)
for k, (Z, R) in curves.items():
    o = np.argsort(Z); Z, R = Z[o], R[o]
    body, _, _ = fit(Z, R, 130, 150)
    cone, cmax, cstd = fit(Z, R, 159, 170)
    neck, _, _ = fit(Z, R, 190, 212) if Z.max() > 212 else fit(Z, R, 188, 200)
    zk, rk, dk, phik, Rk = fillet(Z, R, body, cone)
    zn, rn, dn, phin, Rn = fillet(Z, R, cone, neck)
    ang = np.degrees(np.arctan(-cone[0]))  # from vertical: dr/dz
    # shoulder start: first z (going up) where R falls 0.5 mm below the body line
    zs = next(z for z, r in zip(Z, R) if z > 140 and r < np.polyval(body, z) - 0.5)
    print('%-5s cone %5.1f deg from vertical (%4.1f from horiz) straightness max %.2f sd %.2f mm | knuckle vertex z %.1f r %.1f gap %.2f turn %.0f -> R %.1f mm | neck vertex z %.1f gap %.2f turn %.0f -> R %.1f mm | shoulder start z %.1f'
          % (k, 90 - (90 - ang) if False else np.degrees(np.arctan(-cone[0])), 90 - np.degrees(np.arctan(-cone[0])), cmax, cstd, zk, rk, dk, phik, Rk, zn, dn, phin, Rn, zs))
