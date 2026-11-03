import sys, os, math
sys.argv = [sys.argv[0]]  # analysis only
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'b_shoulder_diag.py')).read().split('# ============================================================== analysis')[0])
deg = math.radians
def sil(rho, z): return max(p1_r(deg(t), z, rho) * math.cos(deg(t)) for t in np.arange(-44, 44.01, 0.5))
zs = [150, 152.5, 155, 157.5, 160, 162.5]
print('PROFILE', [round(g.width_at(z)/2, 2) for z in zs])
for rho in (2, 3, 4, 6, 8, 10):
    s = [round(sil(rho, z), 2) for z in zs]
    print('rho', rho, s, 'maxdev', round(max(abs(a - g.width_at(z)/2) for a, z in zip(s, zs)), 2),
          'corner carve', next(z for z in np.arange(140, 160, 0.1) if prism(deg(40.3), z)[0] - p1_r(deg(40.3), z, rho) > 0.1))
