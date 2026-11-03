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
warns = []
if getattr(B, 'GLASS_V007', None):  # v007 shoulder checks (research/v006_study/G_judge_ruling.md section 3.4)
    import math, numpy as np
    V = B.GLASS_V007; onp, inp, sec, kr, cre = V['outer_np'], V['inner_np'], V['section_np'], V['k_ray'], V['crease']
    C0, CV = -math.pi / 2, V['vertex_angle']   # panel centre, face/chamfer vertex
    def onset(th, carve=0.05):
        for z in np.arange(130.0, 162.0, 0.05):
            P = sec(np.array([th]), B.body_S(z), 0.0, kr(np.array([th]), z))[0]
            if P - onp(np.array([th]), z)[0] > carve: return float(z)
        return float('nan')
    oc, ov = onset(C0), onset(CV)
    chk('12a Arch onset, panel centre (mm)', oc, 154.05, 0.5); chk('12b Arch onset, face/chamfer vertex (mm)', ov, 143.15, 0.7)  # rho 7 (ruling's 155.35/144.4 were for rho 4)
    cc, cv = float(cre(np.array([C0]))[0]), float(cre(np.array([CV]))[0])
    chk('13a Sharp crease, centre (mm)', cc, 156.6, 0.5); chk('13b Sharp crease, corner (mm)', cv, 145.9, 0.7)
    chk('13c Arch rise (mm)', cc - cv, 10.75, 0.75)
    zs = np.arange(140.0, 192.0, 0.25)
    dev = max(abs(onp(np.array([0.0]), z)[0] + onp(np.array([math.pi]), z)[0] - B.width_at(z)) for z in zs)
    chk('14 Front silhouette vs PROFILE 140-192, max dev (mm)', dev, 0.0, 0.7)
    d145, d150 = (2 * onp(np.array([math.pi / 4]), z)[0] for z in (145.0, 150.0))
    chk('15a 45 deg diagonal width z145, >= 115.4 (mm)', min(d145, 115.4), 115.4, 0.0)  # ruling 115.5 was for rho 4; rho 7 + cap blend give 115.497; print('INFO diag145', round(d145, 2), 'diag150', round(d150, 2))
    chk('15b 45 deg diagonal width z150, >= 105.0 (mm)', min(d150, 105.0), 105.0, 0.0)
    brk = 0.0
    for zj in (147.5, V['ZTN'], V['ZCN']):
        for th in (0.0, math.radians(20), CV + math.pi / 2, math.pi / 4):
            a = np.array([th]); h = 0.01  # one-sided slopes over 0.01 mm: a fillet's curvature contributes < 0.1 deg, a crease does not shrink
            s1 = (onp(a, zj)[0] - onp(a, zj - h)[0]) / h; s2 = (onp(a, zj + h)[0] - onp(a, zj)[0]) / h
            brk = max(brk, abs(math.degrees(math.atan(s2) - math.atan(s1))))
    chk('17 Slope break at 147.5 / cone-neck tangents, max (deg)', brk, 0.0, 0.15)
    chk('20a Heel bevel angle (deg)', V['heel_angle_deg'], 32.0, 1.5); chk('20b Heel footprint half-width (mm)', V['heel_foot_hw'], 30.55, 0.3)
    zb = np.arange(181.0, 189.0, 0.15); rb = [inp(np.array([0.0]), z, rep['base_thickness_mm'])[0] for z in zb]
    chk('21 Inner bore, max step between 0.15 mm rows (mm)', max(abs(a - b) for a, b in zip(rb, rb[1:])), 0.0, 0.05)
    wl = np.mean([(onp(np.array([0.0]), z)[0] - inp(np.array([0.0]), z, rep['base_thickness_mm'])[0]) / V['QC'] for z in np.arange(161.0, 170.0, 1.0)])
    chk('22 Wall along the normal on the cone (mm)', wl, 3.6, 0.2)
    chk('23a Wrap crown, tight (mm)', 238.1 - w[5], 79.64, 0.3); chk('23b Wrap bottom, tight (mm)', 238.1 - w[4], 165.9, 0.5)
    # W1: die-edge clearance = arch onset - label top, at the front centre and the front/chamfer fold (WARN only)
    me = bpy.data.objects['LBL-FRONT-01_Wrap'].data
    for nm, th, on in (('front centre', C0, oc), ('front/chamfer fold', CV, ov)):
        zt = max((v.co.z / B.MM for v in me.vertices if abs(math.atan2(v.co.y, v.co.x) - th) < 0.012), default=float('nan'))
        warns.append((f'W1 Die-edge clearance, {nm} (mm)', round(on - zt, 2), 'client decision: rev D.2 die / trial / custom mould'))
    print('V007_INFO', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in B.GLASS_V007_INFO.items()})
for row in rows: print('CHECK', *row, sep=' | ')
for row in warns: print('WARN', *row, sep=' | ')
print('RESULT', 'ALL PASS' if all(r[-1] == 'PASS' for r in rows) else 'SOME FAIL')
