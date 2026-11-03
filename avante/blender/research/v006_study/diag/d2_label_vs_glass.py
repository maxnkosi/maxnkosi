"""v006 study C: wrap label vs glass, read-only, from the saved .blend meshes (pre-modifier data).
Usage: Blender -b --factory-startup avante_master_v00X.blend -P d2_label_vs_glass.py -- TAG OUTDIR
Writes OUTDIR/d2_TAG.json and prints a summary. Lengths in mm.
"""
import bpy, math, json, sys, os
import numpy as np

argv = sys.argv[sys.argv.index('--') + 1:]
TAG, OUT = argv[0], argv[1]
CAP_TOP, Z_EDGE = 238.1, 238.1 - 87.5
WRAP_ART = dict(x=-121.734, y=-12.414, w=243.469, h=101.258)
NR = 256

res = {'tag': TAG}
g = bpy.data.objects['GLS-01_Glass']
res['glass_mods'] = [(m.type, getattr(m, 'node_group', None) and m.node_group.name) for m in g.modifiers]
res['glass_matrix_identity'] = all(abs(g.matrix_world[i][j] - (1 if i == j else 0)) < 1e-9 for i in range(4) for j in range(4))
co = np.empty(len(g.data.vertices) * 3); g.data.vertices.foreach_get('co', co); co = co.reshape(-1, 3) * 1000.0
# outer rings come first (loft(outer + inner)), N_RING verts each, z increasing
nch = len(co) // NR
zc = co[:nch * NR, 2].reshape(nch, NR)
k = 1
while k < nch and np.all(np.abs(zc[k] - zc[k].mean()) < 1e-4) and zc[k].mean() > zc[k - 1].mean(): k += 1
X = co[:k * NR].reshape(k, NR, 3)
Z = X[:, 0, 2].copy()
TH = np.arange(NR) * 2 * math.pi / NR
R = np.hypot(X[..., 0], X[..., 1])
res['outer_rings'] = int(k); res['outer_z_range'] = [float(Z[0]), float(Z[-1])]

# differential geometry on the (theta, z) grid
dth = 2 * math.pi / NR
def dth_(A): return (np.roll(A, -1, axis=1) - np.roll(A, 1, axis=1)) / (2 * dth)
def dz_(A): return np.gradient(A, Z, axis=0)
Xt, Xz = dth_(X), dz_(X)
Xtt, Xtz, Xzz = dth_(Xt), dz_(Xt), dz_(Xz)
nrm = np.cross(Xt, Xz); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
# make outward
radial = np.stack([np.cos(TH), np.sin(TH), np.zeros(NR)], -1)[None]
sgn = np.sign(np.sum(nrm * radial, -1, keepdims=True)); nrm *= sgn
E, F, G = (Xt * Xt).sum(-1), (Xt * Xz).sum(-1), (Xz * Xz).sum(-1)
L, M, N = (Xtt * nrm).sum(-1), (Xtz * nrm).sum(-1), (Xzz * nrm).sum(-1)
den = E * G - F * F
K = (L * N - M * M) / den
H = (E * N - 2 * F * M + G * L) / (2 * den)
disc = np.sqrt(np.maximum(H * H - K, 0))
k1, k2 = H + disc, H - disc  # principal curvatures (1/mm); convex outward -> negative with outward normal
kmin_abs = np.minimum(np.abs(k1), np.abs(k2)); kmax_abs = np.maximum(np.abs(k1), np.abs(k2))
tilt = np.degrees(np.arcsin(np.clip(nrm[..., 2], -1, 1)))  # normal elevation; 0 = vertical wall

def sample(A, th, z):
    i = (th % (2 * math.pi)) / dth; i0 = int(math.floor(i)) % NR; i1 = (i0 + 1) % NR; ti = i - math.floor(i)
    j = int(np.clip(np.searchsorted(Z, z) - 1, 0, len(Z) - 2)); tj = (z - Z[j]) / (Z[j + 1] - Z[j])
    a = A[j, i0] * (1 - ti) + A[j, i1] * ti; b = A[j + 1, i0] * (1 - ti) + A[j + 1, i1] * ti
    return float(a * (1 - tj) + b * tj)

# --- label
w = bpy.data.objects['LBL-FRONT-01_Wrap']; me = w.data
lco = np.empty(len(me.vertices) * 3); me.vertices.foreach_get('co', lco); lco = lco.reshape(-1, 3) * 1000.0
uvl = me.uv_layers[0].data
dev = np.zeros((len(me.vertices), 2))
for p in me.polygons:
    for li, vi in zip(p.loop_indices, p.vertices):
        u, v = uvl[li].uv
        dev[vi] = (u * WRAP_ART['w'] + WRAP_ART['x'], (1 - v) * WRAP_ART['h'] + WRAP_ART['y'])

# per vertex glass relation
lth = np.arctan2(lco[:, 1], lco[:, 0]); lr = np.hypot(lco[:, 0], lco[:, 1]); lz = lco[:, 2]
gap = np.array([lr[i] - sample(R, lth[i], lz[i]) for i in range(len(lco))])
vK = np.array([sample(K, lth[i], lz[i]) for i in range(len(lco))])
vkmin = np.array([sample(kmin_abs, lth[i], lz[i]) for i in range(len(lco))])
vkmax = np.array([sample(kmax_abs, lth[i], lz[i]) for i in range(len(lco))])
vtilt = np.array([sample(tilt, lth[i], lz[i]) for i in range(len(lco))])

# strain: deformation gradient dieline -> 3D, per triangle (fan-triangulated polygons)
tris = []
for p in me.polygons:
    vs = list(p.vertices)
    for t in range(1, len(vs) - 1): tris.append((vs[0], vs[t], vs[t + 1]))
tris = np.array(tris)
P0, P1, P2 = dev[tris[:, 0]], dev[tris[:, 1]], dev[tris[:, 2]]
Q0, Q1, Q2 = lco[tris[:, 0]], lco[tris[:, 1]], lco[tris[:, 2]]
e1, e2 = Q1 - Q0, Q2 - Q0
ax = e1 / np.linalg.norm(e1, axis=1, keepdims=True)
nn = np.cross(e1, e2); nn /= np.linalg.norm(nn, axis=1, keepdims=True); ay = np.cross(nn, ax)
Qm = np.stack([np.stack([(e1 * ax).sum(1), (e2 * ax).sum(1)], 1), np.stack([(e1 * ay).sum(1), (e2 * ay).sum(1)], 1)], 1)  # 2x2 cols e1,e2
Pm = np.stack([np.stack([P1[:, 0] - P0[:, 0], P2[:, 0] - P0[:, 0]], 1), np.stack([P1[:, 1] - P0[:, 1], P2[:, 1] - P0[:, 1]], 1)], 1)
areaP = 0.5 * np.abs(np.linalg.det(Pm))
ok = areaP > 1e-4
Fm = np.einsum('nij,njk->nik', Qm[ok], np.linalg.inv(Pm[ok]))
sv = np.linalg.svd(Fm, compute_uv=False)
lam1, lam2 = sv[:, 0], sv[:, 1]
cz = ((Q0 + Q1 + Q2) / 3)[ok][:, 2]; cdev = ((P0 + P1 + P2) / 3)[ok]
# directional stretch along dieline x (around) and y (down)
Fx = np.linalg.norm(Fm[:, :, 0], axis=1); Fy = np.linalg.norm(Fm[:, :, 1], axis=1)
shear = np.degrees(np.arcsin(np.clip(np.abs((Fm[:, :, 0] * Fm[:, :, 1]).sum(1)) / (Fx * Fy), 0, 1)))
tri_area = areaP[ok]

def stats(mask, name):
    if not mask.any(): return {name: None}
    a = tri_area[mask]
    return {name: dict(area_mm2=float(a.sum()),
                       max_stretch_pct=float((lam1[mask].max() - 1) * 100), max_compress_pct=float((1 - lam2[mask].min()) * 100),
                       p95_abs_strain_pct=float(np.percentile(np.maximum(lam1[mask] - 1, 1 - lam2[mask]) * 100, 95)),
                       mean_x_strain_pct=float(np.average(Fx[mask] - 1, weights=a) * 100),
                       mean_y_strain_pct=float(np.average(Fy[mask] - 1, weights=a) * 100),
                       max_shear_deg=float(shear[mask].max()),
                       area_over_0p5pct=float(a[np.maximum(lam1[mask] - 1, 1 - lam2[mask]) > 0.005].sum()),
                       area_over_2pct=float(a[np.maximum(lam1[mask] - 1, 1 - lam2[mask]) > 0.02].sum()))}

s = {}
s.update(stats(np.ones_like(cz, bool), 'all'))
s.update(stats(cz < Z_EDGE - 1, 'below_Z_EDGE'))
s.update(stats(cz >= Z_EDGE - 1, 'above_Z_EDGE-1'))
s.update(stats((cz >= Z_EDGE - 1) & (np.abs(cdev[:, 0]) <= 37.78), 'above_front'))
s.update(stats((cz >= Z_EDGE - 15) & (np.abs(cdev[:, 0]) > 37.78) & (np.abs(cdev[:, 0]) <= 47.28), 'top15_chamfer'))
s.update(stats((cz >= Z_EDGE - 15) & (np.abs(cdev[:, 0]) > 47.28), 'top15_sides'))
res['strain'] = s

# glass under label: doubly curved area
Kthr = 1e-5  # 1/mm^2 (geometric-mean radius ~316 mm)
dbl = np.abs(vK) > Kthr
res['label_vertices'] = int(len(lco))
res['label_vertices_on_doubly_curved_glass'] = int(dbl.sum())
res['label_vertices_on_doubly_curved_glass_pct'] = float(dbl.mean() * 100)
res['gap_mm'] = dict(min=float(gap.min()), max=float(gap.max()), median=float(np.median(gap)))
res['label_z_max'] = float(lz.max()); res['label_z_min'] = float(lz.min())

# crown (top boundary)
from collections import Counter
ec = Counter()
for p in me.polygons:
    vs = list(p.vertices)
    for a, b in zip(vs, vs[1:] + vs[:1]): ec[tuple(sorted((a, b)))] += 1
bverts = sorted({v for e, c in ec.items() if c == 1 for v in e})
top = [v for v in bverts if dev[v, 1] < 15.5 and not (abs(dev[v, 0]) > 105 and dev[v, 1] > 14.0 and False)]
top = [v for v in top if lz[v] > 120]
top.sort(key=lambda v: dev[v, 0])
crown = []
for xq in [0, 10, 20, 30, 37.78, 42.5, 46.9, 55, 70, 90, 110, 119.4]:
    v = min(top, key=lambda v: abs(dev[v, 0] - xq))
    crown.append(dict(dev_x=round(float(dev[v, 0]), 2), dev_y=round(float(dev[v, 1]), 2), z=round(float(lz[v]), 2),
                      from_cap_top=round(CAP_TOP - float(lz[v]), 2), theta_deg=round(math.degrees(lth[v]), 1),
                      gap=round(float(gap[v]), 3), K=float(vK[v]), R_min_mm=round(1 / max(vkmax[v], 1e-9), 1),
                      R_other_mm=round(1 / max(vkmin[v], 1e-9), 1), normal_tilt_deg=round(float(vtilt[v]), 1)))
res['crown'] = crown

# where on the glass is it doubly curved: lowest z (above 120) per theta column, for crown thetas
def z_dbl(th):
    i = int(round((th % (2 * math.pi)) / dth)) % NR
    for j in range(len(Z)):
        if Z[j] > 120 and abs(K[j, i]) > Kthr and Z[j] < 185: return float(Z[j])
    return None
for c in crown:
    zd = z_dbl(math.radians(c['theta_deg'])); c['glass_doubly_curved_from_z'] = zd
    c['clearance_crown_to_doubly_curved_mm'] = None if zd is None else round(zd - c['z'], 2)

# glass profile along front centre and chamfer centre (theta)
prof = {}
for nm, thd in (('front_centre', -90.0), ('chamfer_centre', -45.0), ('front_x30', math.degrees(math.atan2(-44.45, 30)))):
    rows = []
    for zq in np.arange(130, 166.1, 2.0):
        th = math.radians(thd)
        rows.append(dict(z=float(zq), r=round(sample(R, th, zq), 2), tilt=round(sample(tilt, th, zq), 1), K=sample(K, th, zq),
                         R1=round(1 / max(sample(kmax_abs, th, zq), 1e-9), 1), R2=round(1 / max(sample(kmin_abs, th, zq), 1e-9), 1)))
    prof[nm] = rows
res['glass_profile'] = prof

# strain map summary in dieline bins (x every 10 mm, y every 4 mm) for the top region
bins = []
for yb in np.arange(-12, 20, 4.0):
    row = []
    for xb in np.arange(-120, 121, 10.0):
        m = (cdev[:, 0] >= xb) & (cdev[:, 0] < xb + 10) & (cdev[:, 1] >= yb) & (cdev[:, 1] < yb + 4)
        row.append(None if not m.any() else round(float(np.max(np.maximum(lam1[m] - 1, 1 - lam2[m])) * 100), 1))
    bins.append(dict(y=float(yb), max_abs_strain_pct_by_x=row))
res['strain_bins_top'] = bins
os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, f'd2_{TAG}.json'), 'w'), indent=1)
print('D2_DONE', TAG, json.dumps({k: res[k] for k in ('glass_mods', 'outer_rings', 'gap_mm', 'label_z_max', 'label_vertices_on_doubly_curved_glass_pct')}))
print('STRAIN', json.dumps(s, indent=0))
for c in crown: print('CROWN', c)
