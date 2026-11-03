import sys, math
ROOT = '/Users/maxhlomendlini/Documents/Avante/avante/blender'; sys.path.insert(0, ROOT)
import build_avante_master as B
d2r = math.radians
r6 = B.outer_r
def r5(th, z): return B.section_r(th, B.width_at(z), B.roundness(z))
S0 = B.width_at(152.5); h = S0 / 2; a = B.CHAMFER * S0; th_e = math.atan2(h - a, h)
def sec_curv(rf, z, th, dt=2e-4):
    r0, r1, r2 = rf(th - dt, z), rf(th, z), rf(th + dt, z)
    rp = (r2 - r0) / (2 * dt); rpp = (r2 - 2 * r1 + r0) / dt ** 2
    return abs(r1 ** 2 + 2 * rp ** 2 - r1 * rpp) / (r1 ** 2 + rp ** 2) ** 1.5
for z in (60.0, 100.0, 140.0):
    best = min((1 / max(sec_curv(r5, z, th_e + d2r(i / 100)), 1e-9), i / 100) for i in range(-400, 400))
    # equivalent arc: angle 45deg turn; tangent-length-based radius: distance of softened curve from sharp corner
    S = B.width_at(z); hh = S / 2; aa = B.CHAMFER * S
    cx, cy = hh, hh - aa  # sharp face/chamfer corner
    th = math.atan2(cy, cx); r_sharp = math.hypot(cx, cy); gap = r_sharp - r5(th, z)
    Req = gap / (1 / math.cos(d2r(45) / 2) - 1)
    print('z %.0f vertical face/chamfer edge: min curvature radius %.2f mm (at %+.2f deg from edge); corner gap %.3f mm -> equivalent fillet R %.2f mm' % (z, best[0], best[1], gap, Req))
def prof(rf, th, z0, z1, dz=0.05):
    out = []
    z = z0
    while z <= z1:
        x0, x1, x2 = rf(th, z - dz), rf(th, z), rf(th, z + dz)
        xp = (x2 - x0) / (2 * dz); xpp = (x2 - 2 * x1 + x0) / dz ** 2
        k = xpp / (1 + xp * xp) ** 1.5
        out.append((round(z, 2), round(x1, 3), round(math.degrees(math.atan(-xp)), 1), round(1 / k, 1) if abs(k) > 1e-6 else None))
        z += 0.5
    return out
for name, rf in (('v005', r5), ('v006', r6)):
    for lab, th in (('panel centre', 0.0), ('face edge', th_e), ('corner 45', d2r(45))):
        print(name, lab, 'z, r, slope deg from vertical, curvature radius (neg=convex)')
        print('   ', prof(rf, th, 136, 162))
# kink at Z_HOLD
s_below = (B.width_at(152.5) - B.width_at(152.4)) / 0.1 / 2
print('Z_HOLD kink: dr/dz just below 152.5 = %.4f -> crease angle %.2f deg' % (s_below, math.degrees(math.atan(-s_below))))
# label crown: TRIM top centre & ends -> z on glass
Zc = B.Z_EDGE + 10.414 * math.sin(math.radians(49)); Ze = B.Z_EDGE - 5.64
print('Z_EDGE %.2f; label crown z: centre %.1f, at s=46.9 (corner end) %.1f, rise %.1f' % (B.Z_EDGE, Zc, Ze, Zc - Ze))
print('v006 at label crown centre: surface r(0,%.1f) = %.2f vs v005 %.2f' % (Zc, r6(0, Zc), r5(0, Zc)))
for z in (140, 142.5, 145, 147.5, 150, 152.5, 155):
    print(' z %.1f: inset v006-v005 at face edge %.2f mm, at corner %.2f mm, at panel centre %.2f, at y=30 %.2f' % (z, r6(th_e, z) - r5(th_e, z), r6(d2r(45), z) - r5(d2r(45), z), r6(0, z) - r5(0, z), r6(math.atan2(30, h), z) - r5(math.atan2(30, h), z)))
