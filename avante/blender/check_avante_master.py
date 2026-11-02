"""Acceptance checks for avante_master (page 03 § C.7). Run: python check_avante_master.py"""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_avante_master as B
rep = B.main()
def bb(name):
    ob = bpy.data.objects[name]; me = ob.data
    xs = [v.co.x / B.MM for v in me.vertices]; ys = [v.co.y / B.MM for v in me.vertices]; zs = [v.co.z / B.MM for v in me.vertices]
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)
rows = []
def chk(label, value, target, tol):
    ok = abs(value - target) <= tol; rows.append((label, round(value, 2), target, tol, 'PASS' if ok else 'FAIL')); return ok
g = bb('GLS-01_Glass'); chk('Glass height (mm)', g[5], 226.9, 0.05)
chk('Glass max width X (mm)', g[1] - g[0], 89.0, 0.5)
c = bb('SLV-CAP-01_Capsule'); chk('Overall height with capsule (mm)', c[5], 238.1, 0.05)
chk('Capsule skirt bottom, from cap top (mm)', 238.1 - c[4], 66.27, 0.05)
w = bb('LBL-FRONT-01_Wrap'); chk('Wrap crown, from cap top (mm)', 238.1 - w[5], 79.64, 0.6)
chk('Wrap bottom (front), from cap top (mm)', 238.1 - w[4], 165.9, 3.5)
n = bb('LBL-NECK-01_Collar'); chk('Collar top, from cap top (mm)', 238.1 - n[5], 23.66, 0.05); chk('Collar bottom, from cap top (mm)', 238.1 - n[4], 37.64, 0.05)
r = bb('LBL-ROUNDEL-01_Roundel'); chk('Roundel centre, from cap top (mm)', 238.1 - (r[4] + r[5]) / 2, 195.9, 0.05); chk('Roundel film Ø (mm)', r[1] - r[0], 46.71, 0.1)
chk('Inner volume to fill line (ml)', rep['inner_volume_to_fill_ml'], 750.0, 15.0)
for row in rows: print('CHECK', *row, sep=' | ')
print('RESULT', 'ALL PASS' if all(r[-1] == 'PASS' for r in rows) else 'SOME FAIL')
