import sys, os, math
sys.argv = [sys.argv[0]]
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'b_shoulder_diag.py')).read().split('# ============================================================== analysis')[0])
def area(fn, n=720):
    a = 0.0
    for i in range(n):
        t0, t1 = 2*math.pi*i/n, 2*math.pi*(i+1)/n
        a += 0.5*fn(t0)*fn(t1)*math.sin(t1-t0)
    return a
WALL = g.WALL
v_old = v_new = 0.0; dz = 0.5
z = 120.0
while z < 185.0:
    zm = z + dz/2
    S = g.inner_width(zm, 20.0)
    a_old = area(lambda t: g.dome_cut(g.section_r(t, S, g.roundness(zm)), zm, WALL))
    a_new = area(lambda t: p1_r(t, zm, 3.0, inset=WALL), 360)
    v_old += a_old*dz; v_new += a_new*dz; z += dz
print('inner volume 120-185 v006 ml', round(v_old/1000, 2), 'P1', round(v_new/1000, 2), 'delta', round((v_new-v_old)/1000, 2))
S0 = g.inner_width(60, 20.0); A0 = area(lambda t: g.section_r(t, S0, 0.0))
print('inner section area at z60 mm2', round(A0), '-> base shift mm', round((v_new-v_old)/A0, 2))
# wall thickness normal on cone for v006 (radial inset) vs P1
m = 1.287; print('v006 normal wall on cone (radial 3.6):', round(3.6/math.sqrt(1+m*m), 2))
print('Z_HOLD kink: width slope at 152.5 =', round((g.width_at(152.75)-g.width_at(152.25))/0.5, 3), 'per mm; at 147.5 =', round((g.width_at(147.75)-g.width_at(147.25))/0.5, 3))
