# D study: calibrate soft-min k -> effective fillet radius for the vertical chamfer edges (EDGE_SOFT)
# and the shoulder arch edge (ARCH_K). Read-only; monkeypatches the imported module in memory only.
import math, importlib.util
spec = importlib.util.spec_from_file_location('bam', '/Users/maxhlomendlini/Documents/Avante/avante/blender/build_avante_master.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

def sq_radius_stable(theta, S):  # same maths as B.sq_radius, but no exp underflow for small k
    h, a = S / 2, B.CHAMFER * S
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    return B.softmin(h / max(c, s), (S - a) / (c + s), B.EDGE_SOFT)
B.sq_radius = sq_radius_stable

def R3(p0, p1, p2):
    a, b, c = math.dist(p0, p1), math.dist(p1, p2), math.dist(p0, p2)
    ar = abs((p1[0]-p0[0])*(p2[1]-p0[1]) - (p1[1]-p0[1])*(p2[0]-p0[0]))
    return a*b*c/(2*ar) if ar > 1e-14 else 1e9

def zone(pts, thresh):
    Rs = [R3(pts[i-1], pts[i], pts[i+1]) for i in range(1, len(pts)-1)]
    rmin = min(Rs); i = Rs.index(rmin)
    lo = i
    while lo > 0 and Rs[lo] < thresh: lo -= 1
    hi = i
    while hi < len(Rs)-1 and Rs[hi] < thresh: hi += 1
    L = sum(math.dist(pts[q], pts[q+1]) for q in range(lo+1, hi+1))
    def ang(p, q): return math.atan2(q[1]-p[1], q[0]-p[0])
    turn = abs((ang(pts[hi+1], pts[hi+2]) - ang(pts[lo], pts[lo+1]) + math.pi) % (2*math.pi) - math.pi)
    return rmin, L, math.degrees(turn), L / max(turn, 1e-9)

print('EDGE_SOFT calibration (section z=100, face->chamfer edge; 45 deg turn)')
S = B.body_S(100.0); th_v = math.atan2(S/2 - B.CHAMFER*S, S/2)
for k in (0.7, 0.4, 0.3, 0.2, 0.15, 0.1, 0.08, 0.05):
    B.EDGE_SOFT = k
    N = 60000
    pts = [(B.sq_radius(t, S)*math.cos(t), B.sq_radius(t, S)*math.sin(t)) for t in
           [th_v + math.radians(-8 + 16*i/N) for i in range(N+1)]]
    rmin, L, turn, req = zone(pts, 30.0)
    print(f'  k={k:4.2f}: Rmin={rmin:5.2f}  95%-turn zone={L:5.2f} mm  turn={turn:4.1f}  equivR={req:5.2f} mm  pull-in={k*math.log(2):.3f} mm')

print('ARCH_K calibration (r(z) profiles through the arch crossing)')
B.EDGE_SOFT = 0.1
for k in (1.2, 0.8, 0.5, 0.35, 0.25, 0.2, 0.15, 0.1):
    B.ARCH_K = k; B._SR.clear()
    row = []
    for deg, z0, z1 in ((0, 148, 158), (45, 134, 150)):
        th = math.radians(deg)
        zs = [z0 + (z1 - z0)*i/20000 for i in range(20001)]
        pts = [(z, B.outer_r(th, z)) for z in zs]
        rmin, L, turn, req = zone(pts, 30.0)
        row.append(f'{"face" if deg == 0 else "corner"} Rmin={rmin:5.2f} zone={L:5.2f} turn={turn:4.1f} equivR={req:5.2f}')
    print(f'  k={k:4.2f}: ' + ' | '.join(row))
