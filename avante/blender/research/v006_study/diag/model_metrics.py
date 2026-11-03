"""Blender headless: analytic metrology of build_avante_master (v006 as on disk, v005 pyramid reconstructed).
Run: Blender -b --factory-startup --python model_metrics.py   (imports the builder; main() is not run)."""
import sys, math, json
ROOT = '/Users/maxhlomendlini/Documents/Avante/avante/blender'
sys.path.insert(0, ROOT)
import build_avante_master as B
D = ROOT + '/research/v006_study/diag/'
d2r = math.radians

def r6(th, z): return B.outer_r(th, z)
def r5(th, z): return B.section_r(th, B.width_at(z), B.roundness(z))   # v005: pyramid = body square follows PROFILE
MODELS = {'v005': r5, 'v006': r6}
TH = [2 * math.pi * i / 2880 for i in range(2880)]

def sil(rf, z, view=0.0):  # full silhouette width seen along a horizontal direction rotated by `view` from a face normal
    return 2 * max(rf(t, z) * math.cos(t - view) for t in TH if abs(((t - view + math.pi) % (2 * math.pi)) - math.pi) < math.pi / 2)

out = {'profile_z': [p[0] for p in B.PROFILE], 'PROFILE': B.PROFILE}
for name, rf in MODELS.items():
    m = {}
    m['front'] = [(z, sil(rf, z, 0.0)) for z, _ in B.PROFILE]
    m['diag45'] = [(z, sil(rf, z, d2r(45))) for z, _ in B.PROFILE]
    m['face_centre_w'] = [(z, 2 * rf(0.0, z)) for z, _ in B.PROFILE]
    # fine front silhouette 120..200 for shape analysis
    m['front_fine'] = [(z / 4, sil(rf, z / 4, 0.0)) for z in range(480, 801)]
    # where carving starts: drop >= 0.2 mm below the plain held square body at given polar angle
    def carve_start(th, tol=0.2):
        for zz in range(1000, 1900):
            z = zz / 10
            S = B.width_at(min(z, B.Z_HOLD)) if name == 'v006' else B.width_at(z)
            base = B.sq_radius(th, B.width_at(min(z, 152.5)))  # reference: square held at its 152.5 size
            if rf(th, z) < base - tol: return z
        return None
    S0 = B.width_at(152.5); h = S0 / 2; a = B.CHAMFER * S0
    th_edge = math.atan2(h - a, h)                    # face/chamfer edge
    th_corner = d2r(45)
    m['carve_start'] = {'panel_centre': carve_start(0.0), 'face_mid(y=h/2)': carve_start(math.atan2(h / 2, h)),
                        'face_edge': carve_start(th_edge), 'chamfer_centre': carve_start(th_corner)}
    out[name] = m

# v006 specifics
S0 = B.width_at(152.5); h = S0 / 2; a = B.CHAMFER * S0
out['geom'] = dict(S_hold=S0, chamfer_leg=a, chamfer_facet_width=a * math.sqrt(2), face_flat_width=S0 - 2 * a,
                   chamfer_frac=B.CHAMFER, th_edge_deg=math.degrees(math.atan2(h - a, h)),
                   Z_HOLD=B.Z_HOLD, Z_ARCH_C=B.Z_ARCH_C, Z_ARCH_F=B.Z_ARCH_F, ARCH_K=B.ARCH_K, EDGE_SOFT=B.EDGE_SOFT,
                   shoulder_R=[(z / 2, B.shoulder_R(z / 2)) for z in range(240, 381)])

# curvature radii -------------------------------------------------------------------------
def section_min_radius(rf, z, th0, th1, n=4000):
    best = (1e9, None)
    dt = (th1 - th0) / n
    for i in range(1, n):
        t = th0 + i * dt
        r0, r1, r2 = rf(t - dt, z), rf(t, z), rf(t + dt, z)
        rp = (r2 - r0) / (2 * dt); rpp = (r2 - 2 * r1 + r0) / dt ** 2
        k = abs(r1 ** 2 + 2 * rp ** 2 - r1 * rpp) / (r1 ** 2 + rp ** 2) ** 1.5
        if 1 / k < best[0]: best = (1 / k, math.degrees(t))
    return best
def profile_radius(rf, th, z0, z1, dz=0.05):
    """min radius of curvature of the vertical profile curve (r(z), z) at polar angle th; returns (R, z, sign)."""
    best = (1e9, None, 0)
    z = z0 + dz
    while z < z1 - dz:
        x0, x1, x2 = rf(th, z - dz), rf(th, z), rf(th, z + dz)
        xp = (x2 - x0) / (2 * dz); xpp = (x2 - 2 * x1 + x0) / dz ** 2
        k = xpp / (1 + xp * xp) ** 1.5
        if abs(k) > 1e-9 and 1 / abs(k) < best[0]: best = (1 / abs(k), round(z, 2), 'convex' if k < 0 else 'concave')
        z += dz
    return best
radii = {}
for name, rf in MODELS.items():
    th_e = math.atan2(h - a, h)
    radii[name] = {
        'vertical_face_chamfer_edge_z100': section_min_radius(rf, 100.0, th_e - 0.15, th_e + 0.15),
        'vertical_edge_z140': section_min_radius(rf, 140.0, th_e - 0.15, th_e + 0.15),
        'face_to_shoulder_panel_centre': profile_radius(rf, 0.0, 140, 166),
        'face_to_shoulder_face_edge': profile_radius(rf, th_e, 125, 166),
        'chamfer_to_shoulder_corner': profile_radius(rf, d2r(45), 120, 166),
        'shoulder_to_neck_panel_centre': profile_radius(rf, 0.0, 168, 192),
        'shoulder_to_neck_corner': profile_radius(rf, d2r(45), 168, 192),
    }
out['radii'] = radii

# waviness: sign changes of d2r/dz along the profile at several angles (inflections = 'uneven surface')
def inflections(rf, th, z0=125, z1=190, dz=0.25):
    zs, prev, res = [], None, []
    z = z0 + dz
    while z < z1:
        k = rf(th, z + dz) - 2 * rf(th, z) + rf(th, z - dz)
        s = 1 if k > 1e-6 else (-1 if k < -1e-6 else 0)
        if s and prev and s != prev: res.append(round(z, 2))
        if s: prev = s
        z += dz
    return res
out['inflections'] = {name: {deg: inflections(rf, d2r(deg)) for deg in (0, 15, 30, 39, 45)} for name, rf in MODELS.items()}

# arch on the face plane (v006): for lateral offset y along the front face, the height where the dome has cut
# 0.2 mm into the plane. Also the visible 'edge' = where surface slope passes 20 deg off vertical.
def arch(rf, tol=0.2):
    rows = []
    for yy in [0, 5, 10, 15, 20, 25, 30, 35, h - a, h - a / 2, h]:
        th = math.atan2(yy, h)
        z_cut = None; z_slope = None
        for zz in range(1200, 1800):
            z = zz / 10
            base = B.sq_radius(th, S0)
            if z_cut is None and rf(th, z) < base - tol: z_cut = z
            dr = (rf(th, z + 0.05) - rf(th, z - 0.05)) / 0.1
            if z_slope is None and z > 120 and dr * math.cos(th) < -math.tan(d2r(20)): z_slope = z
        rows.append((round(yy, 2), round(math.degrees(th), 2), z_cut, z_slope))
    return rows
out['arch'] = {name: arch(rf) for name, rf in MODELS.items()}
json.dump(out, open(D + 'model_metrics.json', 'w'), indent=1)
print('MODEL_OK')
for k in ('geom',):
    print(k, {kk: v for kk, v in out[k].items() if kk != 'shoulder_R'})
for name in MODELS:
    print(name, 'carve', out[name]['carve_start'])
    print(name, 'arch', out['arch'][name])
    print(name, 'radii', radii[name])
    print(name, 'inflections', out['inflections'][name])
print('z  PROFILE  v005front v006front v006facec v005diag v006diag')
for i, (z, w) in enumerate(B.PROFILE):
    print('%6.1f %6.2f %7.2f %7.2f %7.2f %7.2f %7.2f' % (z, w, out['v005']['front'][i][1], out['v006']['front'][i][1],
          out['v006']['face_centre_w'][i][1], out['v005']['diag45'][i][1], out['v006']['diag45'][i][1]))
