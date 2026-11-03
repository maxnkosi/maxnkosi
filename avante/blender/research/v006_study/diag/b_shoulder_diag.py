"""B shoulder study — diagnostics (study only, does not modify the project).
Run:  Blender -b --factory-startup --python b_shoulder_diag.py -- [--render]
Loads the geometry functions of build_avante_master.py (everything above the materials section),
compares the v006 shoulder (softmin of held square and Hermite dome) with a proposed construction
(extruded chamfered square  ROUND-INTERSECT  revolved cone generatrix, constant-radius rolling-ball fillet),
writes CSV/SVG plots, a curvature map, and optional zebra / facing renders into this folder.
"""
import bpy, math, os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = open(os.path.join(ROOT, 'build_avante_master.py')).read()
cut = SRC.index('# ---------------------------------------------------------------- materials')
NS = {'__name__': 'avante_geo'}
exec(compile(SRC[:cut], 'build_avante_master_geo', 'exec'), NS)
g = type('G', (), NS)  # attribute access
RENDER = '--render' in sys.argv

# ============================================================== proposal (P1)
# 1. cone generatrix fitted to the straight part of the measured front silhouette (z 160..172.5)
zs_fit = [p[0] for p in g.PROFILE if 160 <= p[0] <= 172.5]
rs_fit = [p[1] / 2 for p in g.PROFILE if 160 <= p[0] <= 172.5]
A = np.vstack([np.ones(len(zs_fit)), np.array(zs_fit) - 160.0]).T
coef, *_ = np.linalg.lstsq(A, np.array(rs_fit), rcond=None)
R0, M = float(coef[0]), float(-coef[1])        # R = R0 - M (z - 160)
R_NECK = 34.1 / 2

def neck_fillet(rho_n):
    q = math.sqrt(1 + M * M)
    rc = R_NECK + rho_n
    zc = 160.0 + (rho_n * q - rc + R0) / M
    zt = zc - rho_n * M / q
    return rc, zc, zt

def fit_rho_n():
    best = None
    for rho_n in np.arange(4.0, 30.01, 0.25):
        rc, zc, zt = neck_fillet(rho_n)
        if zc > 190.0: continue
        err = 0.0
        for z, w in g.PROFILE:
            if 172.5 <= z <= 190: err += (G_of(z, rho_n)[0] - w / 2) ** 2
        if best is None or err < best[1]: best = (float(rho_n), err)
    return best

def G_of(z, rho_n):
    """revolved generatrix radius and slope magnitude m = -dG/dz (>= 0)."""
    if z >= 190.0:
        return g.width_at(z) / 2, 0.0
    rc, zc, zt = neck_fillet(rho_n)
    if z <= zt: return R0 - M * (z - 160.0), M
    if z >= zc: return R_NECK, 0.0
    dz = z - zc; s = math.sqrt(max(rho_n ** 2 - dz * dz, 1e-12))
    return rc - s, -dz / s  # dG/dz = dz/s (dz<0 -> negative) ; m = -dG/dz

RHO_N, _ = fit_rho_n()

def prism(theta, z):
    S = g.body_S(z)
    P = g.sq_radius(theta, S)
    e = 1e-4
    dP = (g.sq_radius(theta + e, S) - g.sq_radius(theta - e, S)) / (2 * e)
    return P, dP

def round_intersect(dA, dB, c, rho):
    """exact rolling-ball (radius rho) intersection of two half-spaces with unit normals at cos angle c.
    dA, dB: signed distances (positive outside). Returns signed distance of the filleted solid."""
    a, b = dA + rho, dB + rho
    if a <= 0 and b <= 0: return max(a, b) - rho
    if b - a * c <= 0: return a - rho
    if a - b * c <= 0: return b - rho
    s = math.sqrt(max(1 - c * c, 1e-12))
    return math.sqrt(max(a * a + b * b - 2 * a * b * c, 0.0)) / s - rho

def p1_r(theta, z, rho=3.0, inset=0.0):
    """proposal outer (inset=0) / inner (inset=WALL) radius on the ray theta at height z."""
    P, dP = prism(theta, z)
    P -= inset * math.sqrt(P * P + dP * dP) / P          # normal offset of the prism
    G, m = G_of(z, RHO_N)
    q = math.sqrt(1 + m * m)
    G -= inset * q                                       # normal offset of the cone (wall measured normal)
    cp = P / math.sqrt(P * P + dP * dP)                  # cos(radial, prism normal)
    c = cp / q                                           # cos(prism normal, cone normal)
    r_rho = max(rho - inset, 0.6) if inset else rho
    lo, hi = 0.0, P + 0.01
    if round_intersect((hi - P) * cp, (hi - G) / q, c, r_rho) < 0: return hi
    for _ in range(48):
        mid = 0.5 * (lo + hi)
        if round_intersect((mid - P) * cp, (mid - G) / q, c, r_rho) > 0: hi = mid
        else: lo = mid
    return 0.5 * (lo + hi)

def crease_z(theta):
    """sharp intersection height of prism and cone line on the ray theta (no fillet)."""
    P, _ = prism(theta, 152.5)
    return 160.0 + (R0 - P) / M

# ============================================================== analysis
v006 = lambda th, z: g.outer_r(th, z)
deg = math.radians
TH_PANEL_EDGE = math.atan2(g.width_at(152.5) / 2 - g.CHAMFER * g.width_at(152.5), g.width_at(152.5) / 2)
rows = {}
out = {'cone_R0_at160': R0, 'cone_slope_m': M, 'cone_angle_from_horizontal_deg': math.degrees(math.atan(1 / M)),
       'neck_fillet_rho': RHO_N, 'neck_fillet_zt_zc': neck_fillet(RHO_N)[1:][::-1],
       'theta_panel_edge_deg': math.degrees(TH_PANEL_EDGE)}

def carve_height(fun, theta, tol=0.10):
    """lowest z (scan down from 175) where the surface is still carved by > tol below the body prism."""
    z = 175.0; last = None
    while z > 100:
        P, _ = prism(theta, z)
        if P - fun(theta, z) > tol: last = z
        else: break
        z -= 0.1
    return last

for name, fun in (('v006', v006), ('P1_rho3', lambda t, z: p1_r(t, z, 3.0)), ('P1_rho2', lambda t, z: p1_r(t, z, 2.0))):
    ths = [0, 10, 20, 30, 35, 40, math.degrees(TH_PANEL_EDGE), 42.5, 45]
    out['carve_start_' + name] = {round(t, 1): carve_height(fun, deg(t)) for t in ths}
out['sharp_crease_P1'] = {round(t, 1): round(crease_z(deg(t)), 2) for t in [0, 10, 20, 30, 35, 40, math.degrees(TH_PANEL_EDGE), 42.5, 45]}

# meridians r(z) and curvature along theta = 0 (panel centre), panel edge, 45 (chamfer centre)
Z = np.arange(120.0, 195.0, 0.05)
def meridian(fun, th):
    r = np.array([fun(th, z) for z in Z])
    r1 = np.gradient(r, Z); r2 = np.gradient(r1, Z)
    k = r2 / (1 + r1 ** 2) ** 1.5
    return r, r1, k
MER = {}
for name, fun in (('v006', v006), ('P1', lambda t, z: p1_r(t, z, 3.0))):
    for tn, th in (('panel', 0.0), ('edge', TH_PANEL_EDGE), ('chamfer', math.pi / 4)):
        MER[(name, tn)] = meridian(fun, th)

# front silhouette half-width (max over theta of r cos theta) vs PROFILE
def silhouette(fun, z):
    return max(fun(deg(t), z) * math.cos(deg(t)) for t in np.arange(-44, 44.01, 0.5))
SIL = {'z': [], 'profile': [], 'v006': [], 'P1_rho3': [], 'P1_rho2': []}
for z, w in g.PROFILE:
    if 140 <= z <= 192:
        SIL['z'].append(z); SIL['profile'].append(w / 2)
        SIL['v006'].append(silhouette(v006, z))
        SIL['P1_rho3'].append(silhouette(lambda t, zz: p1_r(t, zz, 3.0), z))
        SIL['P1_rho2'].append(silhouette(lambda t, zz: p1_r(t, zz, 2.0), z))
out['silhouette_halfwidth'] = {k: [round(x, 2) for x in v] for k, v in SIL.items()}
out['silhouette_maxdev'] = {k: round(max(abs(a - b) for a, b in zip(SIL[k], SIL['profile'])), 2) for k in ('v006', 'P1_rho3', 'P1_rho2')}

# softmin pull-in on flat panel centre below the arch (v006): radial loss vs held square
out['v006_panel_centre_pullin_mm'] = {z: round(g.sq_radius(0, g.body_S(z)) - v006(0, z), 3) for z in (140, 145, 148, 150, 152, 154, 156)}
out['v006_corner_pullin_mm'] = {z: round(g.sq_radius(TH_PANEL_EDGE, g.body_S(z)) - v006(TH_PANEL_EDGE, z), 3) for z in (128, 131, 134, 137, 140, 143, 146)}
out['v006_shoulderR'] = {z: round(g.shoulder_R(z), 2) for z in (125, 131, 135, 140, 145, 150, 152.5, 155, 157.5, 160)}
out['v006_dR_dz'] = {z: round((g.shoulder_R(z + 0.01) - g.shoulder_R(z - 0.01)) / 0.02, 3) for z in (131.5, 135, 140, 145, 150, 155, 157.4, 157.6, 160, 165, 170, 175)}
# 2nd derivative of the revolved generatrix (curvature of the dome meridian) — jumps and noise
d2 = {}
for z in np.arange(150.0, 186.0, 1.25):
    h = 0.2
    d2[round(float(z), 2)] = round((g.shoulder_R(z + h) - 2 * g.shoulder_R(z) + g.shoulder_R(z - h)) / h / h, 4)
out['v006_d2R_dz2'] = d2

# crease sharpness vs grid: arch line slope dz/ds on the panel, and grid spacing
out['ring_spacing_mm_at_r58'] = 2 * math.pi * 58 / g.N_RING
json.dump(out, open(os.path.join(HERE, 'b_metrics.json'), 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))

# ============================================================== plots (SVG -> PNG via qlmanage)
def svg_plot(fname, series, xlab, ylab, title, xr=None, yr=None, W=900, H=520, vlines=()):
    L, R_, T, B = 70, 20, 40, 50
    xs = [x for s in series for x in s[1]]; ys = [y for s in series for y in s[2]]
    x0, x1 = xr or (min(xs), max(xs)); y0, y1 = yr or (min(ys), max(ys))
    X = lambda x: L + (x - x0) / (x1 - x0) * (W - L - R_)
    Y = lambda y: H - B - (y - y0) / (y1 - y0) * (H - T - B)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="Helvetica" font-size="13">',
         f'<rect width="{W}" height="{H}" fill="white"/>', f'<text x="{L}" y="24" font-size="16">{title}</text>']
    for i in range(6):
        xv = x0 + (x1 - x0) * i / 5; yv = y0 + (y1 - y0) * i / 5
        o.append(f'<line x1="{X(xv)}" y1="{T}" x2="{X(xv)}" y2="{H-B}" stroke="#ddd"/><text x="{X(xv)-12}" y="{H-B+18}">{xv:.4g}</text>')
        o.append(f'<line x1="{L}" y1="{Y(yv)}" x2="{W-R_}" y2="{Y(yv)}" stroke="#ddd"/><text x="5" y="{Y(yv)+4}">{yv:.4g}</text>')
    for xv, lab in vlines:
        o.append(f'<line x1="{X(xv)}" y1="{T}" x2="{X(xv)}" y2="{H-B}" stroke="#999" stroke-dasharray="4,3"/><text x="{X(xv)+3}" y="{T+12}" fill="#666">{lab}</text>')
    o.append(f'<text x="{W/2}" y="{H-12}">{xlab}</text><text x="5" y="{T-6}">{ylab}</text>')
    for k, (lab, sx, sy, col, dash) in enumerate(series):
        pts = ' '.join(f'{X(a):.1f},{Y(min(max(b, y0), y1)):.1f}' for a, b in zip(sx, sy))
        da = 'stroke-dasharray="5,4"' if dash else ''
        o.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="1.8" {da}/>')
        o.append(f'<line x1="{W-360}" y1="{T+14+k*18}" x2="{W-330}" y2="{T+14+k*18}" stroke="{col}" stroke-width="2.5"/><text x="{W-325}" y="{T+18+k*18}">{lab}</text>')
    o.append('</svg>')
    p = os.path.join(HERE, fname + '.svg'); open(p, 'w').write('\n'.join(o))
    os.system(f'cd "{HERE}" && qlmanage -t -s {W} -o . "{fname}.svg" >/dev/null 2>&1 && mv -f "{fname}.svg.png" "{fname}.png"')

# (a) arch: carve depth below the prism, panel-centre-to-chamfer, as height of carving start
TH = np.arange(0, 45.01, 0.5)
def arch_line(fun, tol=0.1): return [carve_height(fun, deg(t), tol) or float('nan') for t in TH]
svg_plot('b1_arch_height', [
    ('v006 carve starts (0.1 mm)', TH, arch_line(v006), '#c0392b', False),
    ('P1 rho3 carve starts (0.1 mm)', TH, arch_line(lambda t, z: p1_r(t, z, 3.0)), '#1f6fb2', False),
    ('P1 sharp crease (cone x prism)', TH, [crease_z(deg(t)) for t in TH], '#1f6fb2', True)],
    'theta from panel centre (deg)', 'z (mm)', 'Where the shoulder starts cutting the body: v006 vs cone proposal',
    yr=(125, 162), vlines=((math.degrees(TH_PANEL_EDGE), 'panel/chamfer edge'), (45, 'chamfer centre')))

# (b) meridian curvature along panel centre / panel edge
svg_plot('b2_meridian_curvature', [
    ('v006 panel centre', Z, MER[('v006', 'panel')][2], '#c0392b', False),
    ('v006 panel edge', Z, MER[('v006', 'edge')][2], '#e67e22', False),
    ('P1 panel centre', Z, MER[('P1', 'panel')][2], '#1f6fb2', False),
    ('P1 panel edge', Z, MER[('P1', 'edge')][2], '#16a085', False)],
    'z (mm)', 'meridian curvature 1/mm (neg = convex)', 'Meridian curvature: v006 ripples/jumps vs P1 (line + fillets)',
    xr=(125, 192), yr=(-0.45, 0.25), vlines=((g.Z_ARCH_C, 'Z_ARCH_C'), (g.Z_HOLD, 'Z_HOLD'), (g.Z_ARCH_F, 'Z_ARCH_F'), (182, 'roundness')))
svg_plot('b2b_meridian_slope', [
    ('v006 panel centre', Z, MER[('v006', 'panel')][1], '#c0392b', False),
    ('v006 panel edge', Z, MER[('v006', 'edge')][1], '#e67e22', False),
    ('v006 chamfer centre', Z, MER[('v006', 'chamfer')][1], '#8e44ad', False),
    ('P1 panel centre', Z, MER[('P1', 'panel')][1], '#1f6fb2', False),
    ('P1 panel edge', Z, MER[('P1', 'edge')][1], '#16a085', False)],
    'z (mm)', 'dr/dz', 'Meridian slope: v006 dome is near-vertical where it grazes the corners',
    xr=(125, 192), yr=(-1.6, 0.2), vlines=((g.Z_ARCH_C, 'Z_ARCH_C'), (g.Z_ARCH_F, 'Z_ARCH_F')))
# (c) silhouette deviation from PROFILE
svg_plot('b3_silhouette', [
    ('PROFILE/2 (measured)', SIL['z'], SIL['profile'], '#000', False),
    ('v006', SIL['z'], SIL['v006'], '#c0392b', False),
    ('P1 rho 3', SIL['z'], SIL['P1_rho3'], '#1f6fb2', False),
    ('P1 rho 2', SIL['z'], SIL['P1_rho2'], '#16a085', True)],
    'z (mm)', 'half width (mm)', 'Front silhouette half-width vs measured PROFILE', xr=(140, 192), yr=(15, 46))
# (d) v006 outer_r over theta at several heights, minus held square (carve depth)
ser = []
cols = ['#2c3e50', '#8e44ad', '#c0392b', '#e67e22', '#f1c40f', '#27ae60', '#1f6fb2']
for k, z in enumerate((134, 138, 142, 146, 150, 154, 158)):
    ser.append((f'v006 z={z}', TH, [g.sq_radius(deg(t), g.body_S(z)) - v006(deg(t), z) for t in TH], cols[k], False))
svg_plot('b4_v006_carve_depth_theta', ser, 'theta (deg)', 'carve depth below prism (mm)',
         'v006: depth the dome cuts into the held square, by height', yr=(0, 12), vlines=((math.degrees(TH_PANEL_EDGE), 'panel edge'),))
ser = []
for k, z in enumerate((140, 144, 148, 152, 154, 156, 158)):
    ser.append((f'P1 z={z}', TH, [g.sq_radius(deg(t), g.body_S(z)) - p1_r(deg(t), z, 3.0) for t in TH], cols[k], False))
svg_plot('b4b_P1_carve_depth_theta', ser, 'theta (deg)', 'carve depth below prism (mm)',
         'P1: depth the cone cuts into the held square, by height', yr=(0, 12), vlines=((math.degrees(TH_PANEL_EDGE), 'panel edge'),))

# (e) curvature heat map (theta x z): Gaussian-free proxy = meridional curvature at fixed theta
def heat(fun, n_th=180, z0=125.0, z1=190.0, dz=0.1):
    zz = np.arange(z0, z1, dz); tt = np.linspace(0, math.pi / 4, n_th)
    img = np.zeros((len(zz), n_th))
    for j, th in enumerate(tt):
        r = np.array([fun(th, z) for z in zz]); r1 = np.gradient(r, zz); r2 = np.gradient(r1, zz)
        img[:, j] = r2 / (1 + r1 ** 2) ** 1.5
    return img
def save_heat(fname, imgs, lim=0.25):
    pad = np.full((imgs[0].shape[0], 6), np.nan)
    a = np.hstack(sum([[im, pad] for im in imgs], [])[:-1])
    a = np.repeat(np.repeat(a, 3, axis=1), 1, axis=0)
    v = np.clip(a / lim, -1, 1)
    rgb = np.ones(a.shape + (4,))
    neg = v < 0; pos = v > 0
    rgb[..., 0] = np.where(neg, 1 + v, 1.0); rgb[..., 1] = 1 - np.abs(v); rgb[..., 2] = np.where(pos, 1 - v, 1.0)
    rgb[np.isnan(a)] = (0.2, 0.2, 0.2, 1)
    h, w = a.shape
    im = bpy.data.images.new(fname, w, h, alpha=True)
    im.pixels = rgb.astype(np.float32).ravel()  # row 0 = bottom = z0
    im.filepath_raw = os.path.join(HERE, fname + '.png'); im.file_format = 'PNG'; im.save()
save_heat('b5_curvature_map_v006_vs_P1', [heat(v006), heat(lambda t, z: p1_r(t, z, 3.0))])

# ============================================================== renders
def mesh_rows(rows_xyz, name):
    verts, faces = g.loft(rows_xyz)
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    for p in me.polygons: p.use_smooth = True
    return ob

def rings_flat(fun, n, zs):
    rows = []
    for z in zs:
        rows.append([(fun(2 * math.pi * i / n, z) * math.cos(2 * math.pi * i / n) * g.MM,
                      fun(2 * math.pi * i / n, z) * math.sin(2 * math.pi * i / n) * g.MM, z * g.MM) for i in range(n)])
    return rows

def smooth01(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
ZA0 = crease_z(0.0)
def row_z(theta, v):
    """arch-conforming rows: v is the row height at the panel centre; rows dip with the arch near corners."""
    w = smooth01((v - 118.0) / (ZA0 - 8 - 118.0)) if v < ZA0 - 8 else (1 - smooth01((v - (ZA0 + 3)) / (186.0 - (ZA0 + 3))) if v > ZA0 + 3 else 1.0)
    return v + w * (crease_z(theta) - ZA0)

def rings_arch(fun, n, vs):
    rows = []
    for v in vs:
        row = []
        for i in range(n):
            th = 2 * math.pi * i / n; z = row_z(th, v); r = fun(th, z)
            row.append((r * math.cos(th) * g.MM, r * math.sin(th) * g.MM, z * g.MM))
        rows.append(row)
    return rows

def vsamples():
    vs = set(); v = 110.0
    while v <= 200.0:
        vs.add(round(v, 3))
        v += 0.15 if (ZA0 - 5 <= v <= ZA0 + 4) else (0.4 if 130 < v < 192 else 1.0)
    return sorted(vs)

def zebra_mat(kind):
    m = bpy.data.materials.new('Z_' + kind); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputMaterial'); em = nt.nodes.new('ShaderNodeEmission')
    nt.links.new(em.outputs[0], o.inputs['Surface'])
    geo = nt.nodes.new('ShaderNodeNewGeometry')
    if kind == 'facing':
        lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.35
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0
        nt.links.new(lw.outputs['Facing'], inv.inputs[1]); nt.links.new(inv.outputs[0], em.inputs['Strength'])
        return m
    neg = nt.nodes.new('ShaderNodeVectorMath'); neg.operation = 'SCALE'; neg.inputs['Scale'].default_value = -1
    nt.links.new(geo.outputs['Incoming'], neg.inputs[0])
    rf = nt.nodes.new('ShaderNodeVectorMath'); rf.operation = 'REFLECT'
    nt.links.new(neg.outputs[0], rf.inputs[0]); nt.links.new(geo.outputs['Normal'], rf.inputs[1])
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(rf.outputs[0], sep.inputs[0])
    asn = nt.nodes.new('ShaderNodeMath'); asn.operation = 'ARCSINE'; nt.links.new(sep.outputs['Z'], asn.inputs[0])
    mul = nt.nodes.new('ShaderNodeMath'); mul.operation = 'MULTIPLY'; mul.inputs[1].default_value = 22.0
    nt.links.new(asn.outputs[0], mul.inputs[0])
    sn = nt.nodes.new('ShaderNodeMath'); sn.operation = 'SINE'; nt.links.new(mul.outputs[0], sn.inputs[0])
    gt = nt.nodes.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = 0.0
    nt.links.new(sn.outputs[0], gt.inputs[0]); nt.links.new(gt.outputs[0], em.inputs['Strength'])
    return m

if RENDER:
    sc = bpy.context.scene
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob, do_unlink=True)
    sc.render.engine = 'CYCLES'; sc.cycles.samples = 16; sc.cycles.device = 'CPU'
    sc.render.resolution_x = sc.render.resolution_y = 1000
    sc.world = bpy.data.worlds.new('W'); sc.world.color = (0.05, 0.05, 0.05)
    sc.view_settings.view_transform = 'Standard'
    cam_d = bpy.data.cameras.new('C'); cam_d.type = 'ORTHO'; cam_d.ortho_scale = 0.105
    cam = bpy.data.objects.new('C', cam_d); sc.collection.objects.link(cam); sc.camera = cam
    variants = {
        'v006': rings_flat(v006, g.N_RING, [z for z in g.z_samples(110.0, 200.0)]),
        'P1_flatrings256': rings_flat(lambda t, z: p1_r(t, z, 3.0), g.N_RING, [z for z in g.z_samples(110.0, 200.0)]),
        'P1_archrows512': rings_arch(lambda t, z: p1_r(t, z, 3.0), 512, vsamples()),
    }
    mats = {k: zebra_mat(k) for k in ('zebra', 'facing')}
    views = {'tq': (-60.0, 14.0), 'corner': (-45.0, 8.0)}
    for vname, rows_xyz in variants.items():
        ob = mesh_rows(rows_xyz, vname)
        for mk, mat in mats.items():
            ob.data.materials.clear(); ob.data.materials.append(mat)
            for view, (az, el) in views.items():
                d = 0.5; a, e = math.radians(az), math.radians(el)
                cam.location = (d * math.cos(e) * math.cos(a), d * math.cos(e) * math.sin(a), 0.157 + d * math.sin(e))
                from mathutils import Vector
                dirv = Vector((0, 0, 0.157)) - cam.location
                cam.rotation_euler = dirv.to_track_quat('-Z', 'Y').to_euler()
                sc.render.filepath = os.path.join(HERE, f'b6_{vname}_{mk}_{view}.png')
                bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(ob, do_unlink=True)
print('done')
