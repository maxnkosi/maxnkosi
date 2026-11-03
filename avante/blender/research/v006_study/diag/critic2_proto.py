"""F critic prototype (study only). Combines B (cone + rolling-ball fillet), A (cone continued below 157.5),
D (crisp vertical edges, adaptive sampling, heel), C (label on panel planes + rev D.1 die) by MONKEYPATCHING
build_avante_master in memory. No project file is edited.

Run: Blender -b --factory-startup --python critic2_proto.py -- RHO LABEL SHOTS SAMPLES [TAG]
  RHO     shoulder rolling-ball radius (mm), e.g. 3 or 4;  'v006' = unpatched baseline
  LABEL   'plane' (C: panel planes, true length, rev D.1 die) | 'wrap' (rev D die, crown wraps over the
          fillet+cone by meridian arc length) | 'b49' (B: builder radial mapping, sin49 -> sin(atan(1/M)))
  SHOTS   comma list of: glass34, glasshero, full34, fullhero, shoulder, glassshoulder, neck, heel, none
  SAMPLES cycles samples
"""
import bpy, math, sys, os, json, time, importlib.util
import numpy as np
from mathutils import Vector

ROOT = '/Users/maxhlomendlini/Documents/Avante/avante/blender/'
OUT = ROOT + 'research/v006_study/diag/'
spec = importlib.util.spec_from_file_location('build_avante_master', ROOT + 'build_avante_master.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
RHO_ARG = argv[0] if argv else '4'
LABEL = argv[1] if len(argv) > 1 else 'plane'
SHOTS = (argv[2] if len(argv) > 2 else 'none').split(',')
SAMPLES = int(argv[3]) if len(argv) > 3 else 64
TAG = argv[4] if len(argv) > 4 else f'r{RHO_ARG}_{LABEL}'
BASELINE = RHO_ARG == 'v006'
MM = B.MM
T0 = time.time()
REP = {'tag': TAG, 'rho': RHO_ARG, 'label': LABEL}

if not BASELINE:
    RHO = float(RHO_ARG); RHO_IN = RHO + 1.0
    # ------------------------------------------------------------ D: crisp vertical edges (stable softmin)
    B.EDGE_SOFT = 0.07
    B.Z_HOLD = 147.5                                   # B: removes the 152.5 C1 kink (PROFILE slope 0 here)
    CH = B.CHAMFER

    def sq_np(th, S, k=None):
        k = B.EDGE_SOFT if k is None else k
        h, a = S / 2, CH * S
        c, s = np.abs(np.cos(th)), np.abs(np.sin(th))
        r1 = h / np.maximum(c, s); r2 = (S - a) / (c + s)
        m = np.minimum(r1, r2)
        return m - k * np.log(np.exp(-(r1 - m) / k) + np.exp(-(r2 - m) / k))

    def sq_radius(theta, S):
        return float(sq_np(np.array([theta]), S)[0])
    B.sq_radius = sq_radius

    def section_np(th, S, t):
        return (1 - t) * sq_np(th, S) + t * S / 2

    # ------------------------------------------------------------ B/A: cone generatrix + neck fillet
    zf = np.array([p[0] for p in B.PROFILE if 160 <= p[0] <= 172.5]); rf = np.array([p[1] / 2 for p in B.PROFILE if 160 <= p[0] <= 172.5])
    Afit = np.vstack([np.ones(len(zf)), zf - 160.0]).T
    coef = np.linalg.lstsq(Afit, rf, rcond=None)[0]; R0, M = float(coef[0]), float(-coef[1])
    RN, RHO_N = 34.1 / 2, 20.5
    # optional 'raised shoulder' variant (critic stress test): CRIT_R0, CRIT_M, CRIT_RHON env overrides
    R0 = float(os.environ.get('CRIT_R0', R0)); M = float(os.environ.get('CRIT_M', M)); RHO_N = float(os.environ.get('CRIT_RHON', RHO_N))
    QC = math.sqrt(1 + M * M)
    RCN = RN + RHO_N; ZCN = 160.0 + (RHO_N * QC - RCN + R0) / M; ZTN = ZCN - RHO_N * M / QC
    REP.update(cone_R0=R0, cone_M=M, cone_deg_from_horiz=math.degrees(math.atan(1 / M)), neck_tangent=(ZTN, ZCN))
    W190 = B.width_at(190.0) / 2

    def G_np(z):
        z = np.asarray(z, float)
        G = R0 - M * (z - 160.0); m = np.full_like(z, M)
        inf = (z > ZTN) & (z < ZCN)
        dz = z - ZCN; s = np.sqrt(np.maximum(RHO_N ** 2 - dz * dz, 1e-12))
        G = np.where(inf, RCN - s, G); m = np.where(inf, -dz / s, m)
        neck = z >= ZCN
        G = np.where(neck, RN, G); m = np.where(neck, 0.0, m)
        fin = z >= 190.0
        if np.any(fin):
            G = np.where(fin, np.vectorize(B.width_at)(np.where(fin, z, 200.0)) / 2, G); m = np.where(fin, 0.0, m)
        return G, m

    def ri_np(dA, dB, c, rho):
        a, b = dA + rho, dB + rho
        s = np.sqrt(np.maximum(1 - c * c, 1e-12))
        out = np.sqrt(np.maximum(a * a + b * b - 2 * a * b * c, 0.0)) / s - rho
        out = np.where(a - b * c <= 0, b - rho, out)
        out = np.where(b - a * c <= 0, a - rho, out)
        out = np.where((a <= 0) & (b <= 0), np.maximum(a, b) - rho, out)
        return out

    def shell_r(th, z, S, t, inset=0.0, rho=RHO):
        """radius on ray th at z: prism section(S,t) ROUND-INTERSECT cone, both offset inward by inset (normal)."""
        th = np.asarray(th, float); z = np.broadcast_to(np.asarray(z, float), th.shape)
        S = np.broadcast_to(np.asarray(S, float), th.shape); t = np.broadcast_to(np.asarray(t, float), th.shape)
        e = 1e-5
        P = section_np(th, S, t); dP = (section_np(th + e, S, t) - section_np(th - e, S, t)) / (2 * e)
        G, m = G_np(z); q = np.sqrt(1 + m * m)
        G = G - inset * q            # cone offset normally (true wall); prism inset already in S
        cp = P / np.sqrt(P * P + dP * dP); c = cp / q
        r = np.minimum(P, G)
        fastP = (G - P) >= q * rho * (1 - c) + 1e-9
        fastG = (P - G) * cp >= rho * (1 - c) + 1e-9
        need = ~(fastP | fastG)
        r = np.where(fastP, P, np.where(fastG, G, r))
        if np.any(need):
            Pn, Gn, cpn, qn, cn = P[need], G[need], cp[need], q[need], c[need]
            lo = np.zeros_like(Pn); hi = Pn + 0.01
            for _ in range(46):
                mid = 0.5 * (lo + hi)
                f = ri_np((mid - Pn) * cpn, (mid - Gn) / qn, cn, rho)
                hi = np.where(f > 0, mid, hi); lo = np.where(f > 0, lo, mid)
            r = r.copy(); r[need] = 0.5 * (lo + hi)
        return r

    def outer_np(th, z):
        z = np.asarray(z, float) * np.ones_like(np.asarray(th, float))
        S = np.vectorize(B.body_S)(z); t = np.vectorize(B.roundness)(z)
        return shell_r(th, z, S, t, 0.0, RHO)

    BORE_R = B.BORE / 2
    def inner_np(th, z, base_t, S=None, t=None):
        """inner wall: prism = inner_width square (heel included), cone inset WALL normal, rho_in, bore blend 181-189."""
        th = np.asarray(th, float); z = np.asarray(z, float) * np.ones_like(th)
        if S is None:
            S = np.vectorize(lambda zz: max(B.body_S(zz) - 2 * B.WALL, B.BORE) - heel_dw(zz, base_t))(z)
        if t is None: t = np.vectorize(B.roundness)(z)
        r = shell_r(th, z, S, t, B.WALL, RHO_IN)
        w = np.clip((z - 181.0) / 8.0, 0, 1); w = w * w * (3 - 2 * w)        # D: no step at 185
        return (1 - w) * r + w * BORE_R

    def heel_dw(z, base_t):
        dz = z - base_t
        if 0 <= dz < B.HEEL_R: return 2 * (B.HEEL_R - math.sqrt(max(B.HEEL_R ** 2 - (B.HEEL_R - dz) ** 2, 0.0)))
        return 0.0

    # scalar outer_r for capsule / wrap / anything else in the builder
    def outer_r(theta, z):
        return float(outer_np(np.array([theta]), z)[0])
    B.outer_r = outer_r
    _OR = {}
    def outer_r_cached(theta, z):
        k = (round(theta, 6), round(z, 4))
        if k not in _OR: _OR[k] = outer_r(theta, z)
        return _OR[k]

    # ------------------------------------------------------------ D: adaptive angular sampling
    tv = math.atan(1 - 2 * CH)
    TH = set(round(2 * math.pi * i / 384, 7) for i in range(384))
    for q4 in range(4):
        for va in (q4 * math.pi / 2 + tv, q4 * math.pi / 2 + math.pi / 2 - tv):
            for j in range(-24, 25): TH.add(round((va + j * 0.0018) % (2 * math.pi), 7))
    THETAS = np.array(sorted(TH)); NT = len(THETAS)
    REP['ring_verts'] = NT

    # ------------------------------------------------------------ B: arch-following rows
    SH = B.width_at(B.Z_HOLD)
    def crease(th, inset=0.0):
        P = sq_np(th, SH - 2 * inset)
        return 160.0 + ((R0 - inset * QC) - P) / M
    ZA_OUT = crease(THETAS); ZA0_OUT = float(crease(np.array([-math.pi / 2]))[0])
    ZA_IN = crease(THETAS, B.WALL); ZA0_IN = float(crease(np.array([-math.pi / 2]), B.WALL)[0])
    REP['crease_out_centre_corner'] = (ZA0_OUT, float(ZA_OUT.min())); REP['crease_in_centre_corner'] = (ZA0_IN, float(ZA_IN.min()))

    def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
    def wrow(v, za0):
        if v < za0 - 8: return sm((v - 118.0) / (za0 - 8 - 118.0))
        if v > za0 + 3: return 1 - sm((v - (za0 + 3)) / (186.0 - (za0 + 3)))
        return 1.0
    def row_z(v, ZA, za0): return v + wrow(v, za0) * (ZA - za0)

    def vsamp(z0, z1, za0):
        vs = set([round(z0, 3), round(z1, 3)]); v = z0
        while v < z1:
            vs.add(round(v, 3))
            if za0 - 6 <= v <= za0 + 5: v += 0.15
            elif 138 <= v <= 194: v += 0.3
            elif v < 14 or v > 212: v += 0.5
            else: v += 1.0
        return sorted(x for x in vs if z0 <= x <= z1)

    # ------------------------------------------------------------ D: heel (filleted polyline)
    def fillet_polyline(P, radii, step=0.08):
        out = [P[0]]
        for i in range(1, len(P) - 1):
            a, b, c = Vector(P[i - 1]), Vector(P[i]), Vector(P[i + 1])
            u, v = (a - b).normalized(), (c - b).normalized()
            ang = math.acos(max(-1, min(1, u.dot(v))))
            d = radii[i] / math.tan(ang / 2)
            p0, p1 = b + u * d, b + v * d
            bis = (u + v).normalized(); ctr = b + bis * (radii[i] / math.sin(ang / 2))
            a0 = math.atan2(*(p0 - ctr).yx); a1 = math.atan2(*(p1 - ctr).yx)
            da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            nseg = max(4, int(abs(da) * radii[i] / step))
            s0 = Vector(out[-1]); L = (p0 - s0).length
            for k in range(1, int(L / 0.5) + 1): out.append(tuple(s0 + (p0 - s0) * (k * 0.5 / L)))
            for k in range(nseg + 1):
                ak = a0 + da * k / nseg
                out.append((ctr.x + radii[i] * math.cos(ak), ctr.y + radii[i] * math.sin(ak)))
        end = Vector(P[-1]); s0 = Vector(out[-1]); L = (end - s0).length
        for k in range(1, int(L / 0.5) + 1): out.append(tuple(s0 + (end - s0) * (k * 0.5 / L)))
        out.append(P[-1]); return out
    Z_TOP = 14.0
    hw14 = B.width_at(Z_TOP) / 2
    side_slope = (B.width_at(20) - B.width_at(Z_TOP)) / 2 / (20 - Z_TOP)
    hwS = hw14 - side_slope * (Z_TOP - 7.5); hwF = hwS - 4.5
    HEEL = fillet_polyline([(hwF - 6, 0.0), (hwF, 0.0), (hwS, 7.5), (hw14, Z_TOP)], [None, 1.0, 1.0])

    def ring_pts(r, z):
        return list(zip((r * np.cos(THETAS) * MM).tolist(), (r * np.sin(THETAS) * MM).tolist(), (np.asarray(z) * np.ones(NT) * MM).tolist()))

    def outer_rows():
        rows = []
        for hw, z in HEEL[:-1]:
            rows.append(ring_pts(sq_np(THETAS, 2 * hw), z))
        for v in vsamp(Z_TOP, B.GLASS_H, ZA0_OUT):
            z = row_z(v, ZA_OUT, ZA0_OUT)
            rows.append(ring_pts(outer_np(THETAS, z), z))
        return rows

    def inner_rows(base_t, top, flat_top=None):
        """inner wall bottom-up: punt, heel fillet, then arch rows. flat_top: liquid (rows lerp to a flat fill plane)."""
        W0 = max(B.body_S(base_t) - 2 * B.WALL, B.BORE) - heel_dw(base_t, base_t); t0 = B.roundness(base_t); rows = []
        for i in range(1, 21):
            k = i / 20; z = base_t + B.PUNT_H * (1 - k * k)
            rows.append((sq_np(THETAS, W0 * k) if k > 0 else np.zeros(NT), np.full(NT, z)))
        for a in range(5, 91, 5):
            z = base_t + B.HEEL_R * (1 - math.cos(math.radians(a)))
            rows.append((inner_np(THETAS, z, base_t), np.full(NT, z)))
        v_end = top if flat_top is None else ZA0_IN + 1.0
        for v in vsamp(base_t + B.HEEL_R + 0.25, v_end, ZA0_IN):
            z = row_z(v, ZA_IN, ZA0_IN)
            rows.append((inner_np(THETAS, z, base_t), z))
        if flat_top is not None:  # liquid: blend the last arch row into the flat fill plane
            zl = rows[-1][1]
            for k in range(1, 31):
                z = zl + (flat_top - zl) * k / 30
                rows.append((inner_np(THETAS, z, base_t), z))
        return rows

    def build_glass(C, base_t):
        t = time.time()
        outer = outer_rows()
        inner = [ring_pts(r, z) for r, z in reversed(inner_rows(base_t, B.GLASS_H))]
        verts, faces = B.loft(outer + inner, close_bottom=(0, 0, 1.2 * MM), close_top=(0, 0, (base_t + B.PUNT_H) * MM))
        ob = B.mesh_from('GLS-01_Glass', verts, faces, C)
        B.recalc_normals(ob)
        for p in ob.data.polygons: p.use_smooth = True
        REP['glass_verts'] = len(verts); REP['glass_build_s'] = round(time.time() - t, 1)
        return ob
    B.build_glass = build_glass

    def build_liquid(C, base_t):
        OV = 0.05; rows = []
        for r, z in inner_rows(base_t, None, flat_top=B.FILL_Z):
            lift = OV if np.max(z) < base_t + B.HEEL_R else 0.0
            rows.append(ring_pts(r + OV, z - lift))
        rf = inner_np(THETAS, B.FILL_Z, base_t) + OV
        for dd, hh in ((0.0, 1.8), (0.1, 1.3), (0.3, 0.85), (0.6, 0.48), (1.0, 0.22), (1.6, 0.07), (2.5, 0.0)):
            rows.append(ring_pts(rf - dd, B.FILL_Z + hh))
        verts, faces = B.loft(rows, close_bottom=(0, 0, (base_t + B.PUNT_H - OV) * MM), close_top=(0, 0, B.FILL_Z * MM))
        ob = B.mesh_from('LIQ-01_Brandy', verts, faces, C)
        B.recalc_normals(ob)
        for p in ob.data.polygons: p.use_smooth = True
        REP['liquid_verts'] = len(verts)
        return ob
    B.build_liquid = build_liquid

    # ------------------------------------------------------------ volume on the new inner wall
    TH720 = np.linspace(0, 2 * math.pi, 721)[:-1]
    def area_of(r):
        return 0.5 * float(np.sum(r * np.roll(r, -1))) * math.sin(2 * math.pi / 720)
    _AB = {}
    def area_body(z):  # base-independent (above the heel)
        k = round(z, 3)
        if k not in _AB: _AB[k] = area_of(inner_np(TH720, z, -100.0))
        return _AB[k]
    def inner_volume(z0, z1, dz=0.25):
        v, z = 0.0, z0
        while z < z1:
            zz = min(z + dz, z1); zm = (z + zz) / 2
            if zm < z0 + B.HEEL_R:
                a = area_of(inner_np(TH720, zm, z0))
            else:  # fixed global grid so the base solve reuses the cache
                g = math.floor(zm / dz) * dz; f = (zm - g) / dz
                a = (1 - f) * area_body(g) + f * area_body(g + dz)
            v += a * (zz - z); z = zz
        W0 = max(B.body_S(z0) - 2 * B.WALL, B.BORE)
        return (v - 0.5 * B.PUNT_H * W0 * W0) / 1000.0
    B.inner_volume = inner_volume

    # ------------------------------------------------------------ C: label mapping
    SIN49 = math.sin(math.radians(49))
    if LABEL == 'plane':  # rev D.1 die: crown above the max-width line at true-length projection
        B.TRIM = [(x, y * SIN49 if y < 0 else y) for x, y in B.TRIM]

    _SEC = {}
    def section_table(z):
        """filleted prism section (no cone) at z, arc length from front centre (theta=-90 deg) toward +x."""
        S = round(B.body_S(z), 2); k = S
        if k in _SEC: return _SEC[k]
        th = np.linspace(-math.pi / 2, math.radians(55), 8001)
        r = sq_np(th, S); x, y = r * np.cos(th), r * np.sin(th)
        L = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
        h, a = S / 2, CH * S
        v1, v2, v3 = math.atan2(-h, h - a), math.atan2(-(h - a), h), math.atan2(h - a, h)
        Lv = [0.0] + [float(np.interp(v, th, L)) for v in (v1, v2, v3)]
        _SEC[k] = (th, L, Lv); return _SEC[k]

    def panel_theta(sE, z):
        th, L, Lv = section_table(z); s = abs(sE)
        if s <= B.HF_E: l = Lv[0] + (Lv[1] - Lv[0]) * s / B.HF_E
        elif s <= B.S1_E: l = Lv[1] + (Lv[2] - Lv[1]) * (s - B.HF_E) / (B.S1_E - B.HF_E)
        else: l = Lv[2] + (Lv[3] - Lv[2]) * (s - B.S1_E) / (B.S2_E - B.S1_E)
        t = float(np.interp(l, L, th))
        return t if sE >= 0 else -math.pi - t   # mirror about the y axis

    def plane_point(sE, z, off):
        th = panel_theta(sE, z); S = B.body_S(z)
        e = 1e-4
        p = lambda t: np.array([sq_np(np.array([t]), S)[0] * math.cos(t), sq_np(np.array([t]), S)[0] * math.sin(t)])
        p0 = p(th); tg = p(th + e) - p(th - e); n = np.array([tg[1], -tg[0]]); n /= np.linalg.norm(n)
        if n @ p0 < 0: n = -n
        q = p0 + n * off
        return (q[0] * MM, q[1] * MM, z * MM), th

    _COL = {}
    def column_z(th, arc):
        """height reached by walking 'arc' mm up the glass meridian on ray th from Z_EDGE."""
        k = round(th, 5)
        if k not in _COL:
            zs = np.arange(B.Z_EDGE, 166.0, 0.05)
            r = outer_np(np.full(len(zs), th), zs)
            L = np.concatenate([[0], np.cumsum(np.hypot(np.diff(r), np.diff(zs)))])
            _COL[k] = (zs, L)
        zs, L = _COL[k]
        return float(np.interp(arc, L, zs))

    def surf_xyz(sE, v, off):
        if LABEL == 'plane':
            return plane_point(sE, B.Z_EDGE - v, off)[0]
        if LABEL == 'wrap':
            z0 = B.Z_EDGE - v
            th = panel_theta(sE, max(z0, 0.0))
            z = z0 if v >= 0 else column_z(th, -v)
            r = outer_r_cached(th, z) + off
            return (r * math.cos(th) * MM, r * math.sin(th) * MM, z * MM)
        # 'b49': builder mapping, B's suggested slope
        z = B.Z_EDGE - v if v >= 0 else B.Z_EDGE + (-v) * math.sin(math.atan(1 / M))
        th = panel_theta(sE, z)
        r = outer_r_cached(th, z) + off
        return (r * math.cos(th) * MM, r * math.sin(th) * MM, z * MM)
    B.surf_xyz = surf_xyz

# ================================================================= build
t = time.time()
rep = B.main()
REP['build_s'] = round(time.time() - t, 1)
REP.update(rep)
print('CRITIC_REPORT_BUILD', REP, flush=True)

# ---------------------------------------------------------------- acceptance checks (same logic as check_avante_master.py)
def bb(name):
    me = bpy.data.objects[name].data
    co = np.array([v.co[:] for v in me.vertices]) / MM
    return co[:, 0].min(), co[:, 0].max(), co[:, 1].min(), co[:, 1].max(), co[:, 2].min(), co[:, 2].max()
rows = []
def chk(label, value, target, tol):
    rows.append((label, round(float(value), 2), target, tol, 'PASS' if abs(value - target) <= tol else 'FAIL'))
g = bb('GLS-01_Glass'); chk('Glass height', g[5], 226.9, 0.05); chk('Glass max width X', g[1] - g[0], 89.0, 0.5)
c = bb('SLV-CAP-01_Capsule'); chk('Overall height', c[5], 238.1, 0.05); chk('Capsule skirt from cap', 238.1 - c[4], 66.27, 0.05)
w = bb('LBL-FRONT-01_Wrap'); chk('Wrap crown from cap', 238.1 - w[5], 79.64, 0.6); chk('Wrap bottom from cap', 238.1 - w[4], 165.9, 3.5)
n = bb('LBL-NECK-01_Collar'); chk('Collar top', 238.1 - n[5], 23.66, 0.05); chk('Collar bottom', 238.1 - n[4], 37.64, 0.05)
r = bb('LBL-ROUNDEL-01_Roundel'); chk('Roundel centre', 238.1 - (r[4] + r[5]) / 2, 195.9, 0.05); chk('Roundel film dia', r[1] - r[0], 46.71, 0.1)
chk('Inner volume to fill (ml)', rep['inner_volume_to_fill_ml'], 750.0, 15.0)
REP['checks'] = rows; REP['checks_all_pass'] = all(x[-1] == 'PASS' for x in rows)
for x in rows: print('CHECK', *x, sep=' | ')

# ---------------------------------------------------------------- label stress test (dieline -> 3D strain, gap, arch clearance)
if not BASELINE:
    lab = bpy.data.objects['LBL-FRONT-01_Wrap'].data
    V = np.array([v.co[:] for v in lab.vertices]) / MM
    uvl = lab.uv_layers['UVMap'].data
    UV = np.zeros((len(V), 2))
    for p in lab.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): UV[vi] = uvl[li].uv[:]
    D2 = np.stack([UV[:, 0] * B.WRAP_ART['w'] + B.WRAP_ART['x'], (1 - UV[:, 1]) * B.WRAP_ART['h'] + B.WRAP_ART['y']], 1)
    lam1, lam2, zc_, area_ = [], [], [], []
    for p in lab.polygons:
        vs = list(p.vertices)
        for k in range(1, len(vs) - 1):
            i, j, l = vs[0], vs[k], vs[k + 1]
            e1, e2 = V[j] - V[i], V[l] - V[i]
            d1, d2 = D2[j] - D2[i], D2[l] - D2[i]
            A2 = np.array([d1, d2]).T
            if abs(np.linalg.det(A2)) < 1e-6: continue
            u = e1 / (np.linalg.norm(e1) + 1e-12); nrm = np.cross(e1, e2); nn = np.linalg.norm(nrm)
            if nn < 1e-10: continue
            wv = np.cross(nrm / nn, u)
            A3 = np.array([[e1 @ u, e2 @ u], [e1 @ wv, e2 @ wv]])
            F = A3 @ np.linalg.inv(A2)
            sv = np.linalg.svd(F, compute_uv=False)
            lam1.append(sv[0]); lam2.append(sv[1]); zc_.append((V[i, 2] + V[j, 2] + V[l, 2]) / 3); area_.append(abs(np.linalg.det(A2)) / 2)
    lam1, lam2, zc_ = np.array(lam1), np.array(lam2), np.array(zc_)
    strain = np.maximum(np.abs(lam1 - 1), np.abs(lam2 - 1))
    top = zc_ > B.Z_EDGE
    REP['strain'] = dict(all_p99=float(np.percentile(strain, 99)), all_max=float(strain.max()),
                         crown_p99=float(np.percentile(strain[top], 99)) if top.any() else None,
                         crown_max_stretch=float(lam1[top].max() - 1) if top.any() else None,
                         crown_max_compress=float(1 - lam2[top].min()) if top.any() else None,
                         frac_over_1pct=float((strain > 0.01).mean()), crown_frac_over_1pct=float((strain[top] > 0.01).mean()) if top.any() else None)
    bands = {}
    for lo_, hi_ in ((0, 100), (100, 130), (130, 145), (145, B.Z_EDGE), (B.Z_EDGE, 154), (154, 170)):
        sel = (zc_ >= lo_) & (zc_ < hi_)
        if sel.any(): bands[f'{lo_:.0f}-{hi_:.1f}'] = dict(n=int(sel.sum()), p99=round(float(np.percentile(strain[sel], 99)), 4), max=round(float(strain[sel].max()), 4),
                                                           max_stretch=round(float(lam1[sel].max() - 1), 4), max_comp=round(float(1 - lam2[sel].min()), 4))
    REP['strain_bands'] = bands
    # gap and arch clearance per vertex (glass side: the original faces before solidify)
    th = np.arctan2(V[:, 1], V[:, 0]); rl = np.hypot(V[:, 0], V[:, 1])
    rg = np.array([outer_r_cached(float(a), float(z)) for a, z in zip(th, V[:, 2])])
    Sg = np.array([B.body_S(float(z)) for z in V[:, 2]])
    rp = np.array([sq_np(np.array([a]), s)[0] for a, s in zip(th, Sg)])
    gap = rl - rg; carve = rp - rg
    REP['label_gap'] = dict(max=float(gap.max()), p99=float(np.percentile(gap, 99)), frac_gt_0p1=float((gap > 0.1).mean()), min=float(gap.min()))
    REP['label_on_carved_glass_frac'] = float((carve > 0.05).mean())
    # per column overshoot of label top edge above the arch onset (carve > 0.05)
    cols = {}
    for a, z, cv in zip(th, V[:, 2], carve):
        key = round(math.degrees(a)); cols.setdefault(key, []).append((z, cv))
    over = {}
    for key in sorted(cols):
        zs = sorted(cols[key]); ztop = zs[-1][0]
        a = math.radians(key); zz = np.arange(130.0, 175.0, 0.05)
        cz = sq_np(np.full(len(zz), a), np.vectorize(B.body_S)(zz)) - outer_np(np.full(len(zz), a), zz)
        onset = float(zz[np.argmax(cz > 0.05)]) if (cz > 0.05).any() else None
        over[key] = (round(ztop, 2), onset and round(onset, 2), onset and round(onset - ztop, 2))
    REP['clearance_by_theta_deg'] = {k: over[k] for k in sorted(over) if k % 5 == 0 or k in (-90,)}
    REP['clearance_min'] = min(v[2] for v in over.values() if v[2] is not None)
    print('CRITIC_LABEL', json.dumps({k: REP[k] for k in ('strain', 'label_gap', 'label_on_carved_glass_frac', 'clearance_min')}), flush=True)

json.dump(REP, open(OUT + f'critic2_{TAG}.json', 'w'), indent=1, default=str)

# ================================================================= renders
if SHOTS != ['none']:
    sc = bpy.context.scene
    cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = 'METAL'; cp.get_devices()
    for d in cp.devices: d.use = True
    sc.cycles.device = 'GPU'; sc.cycles.samples = SAMPLES
    def mkcam(name, yaw, el, tgt_mm, dist, lens):
        cd = bpy.data.cameras.new(name); cd.lens = lens
        co = bpy.data.objects.new(name, cd); bpy.data.collections['LGT_CAM_ENV'].objects.link(co)
        y, e = math.radians(yaw), math.radians(el); tg = Vector((0, 0, tgt_mm * MM))
        co.location = tg + dist * Vector((math.sin(y) * math.cos(e), -math.cos(y) * math.cos(e), math.sin(e)))
        B.look_at(co, tg); co['foil_aim_z'] = 0.137; return co
    cams = {'shoulder': mkcam('CAM_Crit_Shoulder', 28, 10, 150, 0.28, 100),
            'neck': mkcam('CAM_Crit_Neck', 15, 8, 185, 0.26, 100),
            'heel': mkcam('CAM_Crit_Heel', 30, 3, 10, 0.24, 100)}
    def glass_only(on):
        for nm in ('GEO_Labels', 'GEO_Capsule'):
            for ob in bpy.data.collections[nm].all_objects: ob.hide_render = on
        bpy.data.objects['LIQ-01_Brandy'].hide_render = on
    SPEC = {'glass34': ('CAM_ThreeQuarter', True, (600, 960)), 'glasshero': ('CAM_Hero', True, (600, 960)),
            'full34': ('CAM_ThreeQuarter', False, (600, 960)), 'fullhero': ('CAM_Hero', False, (600, 960)),
            'shoulder': ('CAM_Crit_Shoulder', False, (900, 720)), 'glassshoulder': ('CAM_Crit_Shoulder', True, (900, 720)),
            'neck': ('CAM_Crit_Neck', True, (800, 640)), 'heel': ('CAM_Crit_Heel', True, (800, 640))}
    times = {}
    for s in SHOTS:
        camn, go, res = SPEC[s]
        glass_only(go)
        B.aim_studio(bpy.data.objects[camn])
        sc.render.resolution_x, sc.render.resolution_y = res
        sc.render.filepath = OUT + f'critic2_{TAG}_{s}.png'
        t = time.time(); bpy.ops.render.render(write_still=True); times[s] = round(time.time() - t, 1)
        print('CRITIC_RENDER', s, times[s], flush=True)
    REP['render_s'] = times
    json.dump(REP, open(OUT + f'critic2_{TAG}.json', 'w'), indent=1, default=str)
REP['total_s'] = round(time.time() - T0, 1)
json.dump(REP, open(OUT + f'critic2_{TAG}.json', 'w'), indent=1, default=str)
print('CRITIC_DONE', REP['total_s'], flush=True)
