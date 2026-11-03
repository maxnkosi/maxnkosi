# D study (edges/bevels): measure the effective edge radii the v006 build functions produce.
# Read-only: imports build_avante_master.py as a module (main() is __main__-guarded), builds nothing.
# Run: Blender -b --factory-startup -P d_edge_metrics.py
import sys, math, importlib.util
ROOT = '/Users/maxhlomendlini/Documents/Avante/avante/blender/'
spec = importlib.util.spec_from_file_location('bam', ROOT + 'build_avante_master.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

def curv2(pts):
    """discrete curvature radius at each interior point of a 2D polyline (circumradius of 3 points)."""
    out = []
    for i in range(1, len(pts) - 1):
        (x1, y1), (x2, y2), (x3, y3) = pts[i - 1], pts[i], pts[i + 1]
        a = math.dist(pts[i - 1], pts[i]); b = math.dist(pts[i], pts[i + 1]); c = math.dist(pts[i - 1], pts[i + 1])
        area2 = abs((x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1))
        out.append(float('inf') if area2 < 1e-15 else a * b * c / (2 * area2))
    return out

def arclen(pts):
    s = [0.0]
    for i in range(1, len(pts)): s.append(s[-1] + math.dist(pts[i - 1], pts[i]))
    return s

def edge_report(pts, label, thresh=25.0):
    """Find curvature peaks (edges): min radius, and the arc length over which R < thresh (the visible round)."""
    R = curv2(pts); s = arclen(pts)[1:-1]
    i = 0; found = []
    while i < len(R):
        if R[i] < thresh:
            j = i
            while j < len(R) and R[j] < thresh: j += 1
            k = min(range(i, j), key=lambda q: R[q])
            # turning angle over the zone
            def ang(p, q): return math.atan2(q[1] - p[1], q[0] - p[0])
            t0 = ang(pts[i], pts[i + 1]); t1 = ang(pts[j], pts[j + 1]) if j + 1 < len(pts) else t0
            turn = abs(math.degrees((t1 - t0 + math.pi) % (2 * math.pi) - math.pi))
            L = s[j - 1] - s[i]
            found.append((s[k], R[k], L, turn, L / max(math.radians(turn), 1e-9)))
            i = j
        else: i += 1
    print(f'--- {label}')
    for sk, rk, L, turn, req in found:
        print(f'   at s={sk:7.2f} mm  Rmin={rk:6.2f} mm  zone={L:5.2f} mm  turn={turn:5.1f} deg  equiv_R(zone/turn)={req:6.2f} mm')
    return found

# ---------- 1. horizontal section: face / chamfer / face, at three heights
print('PARAMS CHAMFER', B.CHAMFER, 'EDGE_SOFT', B.EDGE_SOFT, 'ARCH_K', B.ARCH_K, 'N_RING', B.N_RING)
for z in (40.0, 100.0, 140.0):
    S = B.body_S(z); a = B.CHAMFER * S
    print(f'\n=== section z={z}  S={S:.2f}  chamfer leg={a:.2f}  facet width={a*math.sqrt(2):.2f} mm')
    N = 40000
    pts = [(B.sq_radius(t, S) * math.cos(t), B.sq_radius(t, S) * math.sin(t))
           for t in [math.radians(-5 + 60 * i / N) for i in range(N + 1)]]
    found = edge_report(pts, f'z={z} section, theta -5..55 deg (face->chamfer->face)')
    # flat width actually left on the chamfer facet (between the two zones where R<200mm)
    R = curv2(pts); s = arclen(pts)[1:-1]
    flat = [s[i] for i in range(len(R)) if R[i] > 500]
    # sharp-corner pull-in
    rs = B.sq_radius(math.atan2(S / 2, S / 2 - a), S)  # angle of the sharp vertex face/chamfer
    th = math.atan2(S / 2 - a, S / 2)
    sharp = (S / 2) / math.cos(th)
    print(f'   vertex pull-in (sharp - soft) at face/chamfer vertex = {sharp - B.sq_radius(th, S):.3f} mm')
    # mesh: ring segment length and how many verts fall inside each softened zone
    dth = 2 * math.pi / B.N_RING
    print(f'   N_RING={B.N_RING}: segment ~{dth * S / 2:.2f}-{dth * sharp:.2f} mm; '
          f'verts per round zone ~{found[0][2] / (dth * sharp):.2f}')
    for n in (1024, 2048):
        print(f'   N_RING={n}: segment ~{2 * math.pi / n * sharp:.3f} mm, verts per zone ~{found[0][2] / (2 * math.pi / n * sharp):.1f}')

# ---------- 2. vertical profiles through the shoulder dome (r vs z) at fixed theta
print('\n=== shoulder dome, vertical profiles (outer_r), z 120..192')
for deg, name in ((0, 'face centre'), (15, 'face 2/3 out'), (None, 'face/chamfer edge'), (45, 'chamfer centre')):
    S = B.body_S(150)
    th = math.atan2(S / 2 - B.CHAMFER * S, S / 2) if deg is None else math.radians(deg)
    zs = [120 + 72 * i / 7200 for i in range(7201)]
    pts = [(z, B.outer_r(th, z)) for z in zs]
    # angle between held face and dome at the crossing: compare dR/dz of the dome where R==r_face
    rface = B.section_r(th, B.body_S(130), 0)
    zc = None
    for z in zs:
        if B.shoulder_R(z) < B.section_r(th, B.body_S(z), B.roundness(z)): zc = z; break
    if zc:
        dR = (B.shoulder_R(zc + 0.05) - B.shoulder_R(zc - 0.05)) / 0.1
        print(f'{name}: dome crosses face at z={zc:.2f}, dome slope dR/dz={dR:.3f} -> crease angle {math.degrees(math.atan(abs(dR))):.1f} deg')
        # blend half-width along z for softmin k: |r1-r2| < 3k  ->  dz ~ 3k/|slope|
        print(f'   softmin ARCH_K={B.ARCH_K}: 95% blend band ~ +-{3 * B.ARCH_K / max(abs(dR), 1e-6):.1f} mm in z; '
              f'pull-in at crossing {B.ARCH_K * math.log(2):.2f} mm')
    edge_report(pts, f'{name} (theta={math.degrees(th):.1f}) r(z) profile', thresh=40.0)

# ---------- 3. lathe profile edges (heel, neck, finish) from PROFILE via width_at
def prof(z0, z1, n=4000):
    return [(z0 + (z1 - z0) * i / n, B.width_at(z0 + (z1 - z0) * i / n) / 2) for i in range(n + 1)]
print('\n=== PROFILE half-width slopes, base 0..20 mm')
for z0, z1 in zip([0, 1, 2, 3.5, 5, 7.5, 10], [1, 2, 3.5, 5, 7.5, 10, 20]):
    print(f'   {z0:4}-{z1:4}: d(half-width)/dz = {(B.width_at(z1) - B.width_at(z0)) / 2 / (z1 - z0):.3f}')
edge_report(prof(0, 25), 'base heel half-width profile 0..25 (in the face plane)', thresh=60)
edge_report(prof(170, 195), 'shoulder-to-neck (lathe) 170..195', thresh=40)
edge_report(prof(212, 226.9), 'neck finish 212..226.9', thresh=20)
print('\nbase: z rows', [round(z, 2) for z in B.z_samples(0, 12)])
print('dome region rows 128..150 step:', [round(z, 1) for z in B.z_samples(128, 150)][:8], '...')
