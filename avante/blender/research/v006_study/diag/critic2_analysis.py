"""F critic: analytic checks on the prototype geometry (no build). Blender -b --factory-startup --python critic2_analysis.py
Silhouette vs PROFILE, arch onset, crown clearance, rev D.2 die requirement vs topmost artwork, wrap strain lower bound."""
import bpy, sys, os, math, json
import numpy as np
HERE = '/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
SRC = open(HERE + 'critic2_proto.py').read().split('# ================================================================= build')[0]
res = {}
for tag, rho, env in (('r3', '3', {}), ('r4', '4', {}), ('r4_high', '4', dict(CRIT_R0='47.38', CRIT_M='1.6', CRIT_RHON='18'))):
    for k in ('CRIT_R0', 'CRIT_M', 'CRIT_RHON'): os.environ.pop(k, None)
    os.environ.update(env)
    sys.argv = ['x', '--', rho, 'plane', 'none', '16', 'ana']
    NS = {'__name__': 'crit'}; exec(compile(SRC, 'proto', 'exec'), NS)
    B, outer_np, sq_np = NS['B'], NS['outer_np'], NS['sq_np']
    out = {}
    # front silhouette half-width vs PROFILE
    th = np.radians(np.arange(-134, -45.9, 0.25))
    dev = {}
    for z, w in B.PROFILE:
        if 140 <= z <= 192:
            r = outer_np(th, z); hw = float(np.max(r * np.abs(np.sin(th))))   # front view looks along y: width in x... use |y| for side view
            r2 = outer_np(th + math.pi / 2, z); hw2 = float(np.max(r2 * np.abs(np.cos(th + math.pi / 2))))
            dev[z] = round(max(hw, hw2) - w / 2, 2)
    out['silhouette_dev_vs_profile'] = dev
    out['silhouette_maxabs'] = max(abs(v) for v in dev.values())
    # diagonal (45 deg) silhouette width at 145/150 (A: ref ~116/~110 est., v006 109.2/99.3)
    for z in (145, 150, 155):
        thd = np.radians(np.arange(-90, 0.01, 0.1)); r = outer_np(thd, z)
        out[f'diag45_width_{z}'] = round(2 * float(np.max(r * np.cos(thd + math.pi / 4))), 1)
    # arch onset (0.05 mm carve) per theta
    zz = np.arange(125.0, 175.0, 0.05); S = np.vectorize(B.body_S)(zz)
    on = {}
    for d in (-90, -80, -70, -60, -55, -49.66, -45, -40.34, -35, -20, 0):
        a = math.radians(d); cz = sq_np(np.full(len(zz), a), S) - outer_np(np.full(len(zz), a), zz)
        on[d] = round(float(zz[np.argmax(cz > 0.05)]), 2)
    out['arch_onset'] = on
    out['arch_rise_onset'] = round(on[-90] - on[-49.66], 2)
    res[tag] = out
    print(tag, json.dumps(out))

# ---- rev D.2 die (top edge follows the cone arch with 2 mm clearance; true length on the panel planes)
B = NS['B']
r4 = res['r4']['arch_onset']
def onset_at_s(s):  # s along the front/chamfer (dieline x ~ s); interpolate onset by panel angle
    S = B.width_at(147.5); h, a = S / 2, B.CHAMFER * S
    if s <= B.HF_E: x, y = s / B.HF_E * (h - a), -h
    elif s <= B.S1_E: u = (s - B.HF_E) / (B.S1_E - B.HF_E); x, y = (h - a) + a * u, -h + a * u
    else: x, y = h, -h + a + (s - B.S1_E) / (B.S2_E - B.S1_E) * (2 * h - 2 * a)
    d = math.degrees(math.atan2(y, x))
    ks = sorted(r4); return float(np.interp(d, ks, [r4[k] for k in ks]))
SIN49 = math.sin(math.radians(49))
top = sorted([(p[0], p[1] / SIN49 if p[1] < 0 else p[1]) for p in B.TRIM if p[1] < 15 and p[0] >= 0])  # B.TRIM was D.1-patched by the proto exec: undo
def y_trim(x):
    for (x0, y0), (x1, y1) in zip(top, top[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return top[-1][1]
# topmost art per column from the foil mask and the colour art (C's d4 method)
T = '/Users/maxhlomendlini/Documents/Avante/avante/blender/textures'; A = B.WRAP_ART
masks = {}
for f in ('MASK-FOIL-01__LBL-FRONT-01.png', 'HEIGHT-EMB-01__LBL-FRONT-01.exr'):
    try:
        im = bpy.data.images.load(os.path.join(T, f)); w, h = im.size
        px = np.array(im.pixels[:]).reshape(h, w, 4)[::-1]; masks[f] = (px[..., 0] > (0.5 if 'MASK' in f else 0.02), w, h)
    except Exception as e: print('mask fail', f, e)
d2 = []
for s in (0, 5, 10, 15, 20, 25, 30, 35, 37.78, 40, 42.5, 45, 46.9, 47.28, 50, 55, 60):
    z_need = onset_at_s(s) - 2.0
    y_D = y_trim(s); y_D1 = y_D * math.sin(math.radians(49)) if y_D < 0 else y_D
    y_D2 = max(B.Z_EDGE - z_need, y_D1)  # dieline y of the new top edge (v ~ y on the near-flat fan)
    art = None
    for f, (m, w, h) in masks.items():
        c0 = int((s - 1.5 - A['x']) / A['w'] * w); c1 = int((s + 1.5 - A['x']) / A['w'] * w)
        rows = np.where(m[:, c0:c1].any(1))[0]; ys = A['y'] + rows / h * A['h']; ys = ys[ys > -9.9]
        if len(ys): art = min(art, float(ys.min())) if art is not None else float(ys.min())
    d2.append(dict(s=s, onset=round(onset_at_s(s), 2), revD_y=round(y_D, 2), revD1_y=round(y_D1, 2), revD2_y=round(y_D2, 2),
                   crown_z_D1=round(B.Z_EDGE - y_D1, 2), clear_D1=round(onset_at_s(s) - (B.Z_EDGE - y_D1), 2),
                   paper_removed_vs_D1=round(y_D2 - y_D1, 2), top_art_y=art and round(art, 2), art_clear_D2=art and round(art - y_D2, 2)))
res['revD2'] = d2
res['revD2_crown_from_cap'] = round(B.CAP_TOP - (onset_at_s(0) - 2.0), 2)
for r in d2: print('D2', r)

# ---- wrap strain lower bound: sheet rotated about a curved hinge (crease) by fold angle phi:
# hoop strain at distance d beyond the hinge ~ kappa_g * d * (1 - cos phi). crease z_c(x) = 160 + (R0 - sqrt(h^2+x^2))/M on the panel
R0, M = 40.1595, 1.28686; h = 44.5
lb = []
for x in (0, 10, 20, 30, 37):
    zc = lambda xx: 160 + (R0 - math.hypot(h, xx)) / M
    e = 0.01; z1 = (zc(x + e) - zc(x - e)) / (2 * e); z2 = (zc(x + e) - 2 * zc(x) + zc(x - e)) / e / e
    kappa = abs(z2) / (1 + z1 * z1) ** 1.5
    crown = {0: 158.47, 10: 157.42, 20: 154.98, 30: 151.64, 37: 148.9}[x]
    d = max(crown - zc(x), 0) / math.sqrt(1 + 0) ; phi = math.atan(M * h / math.hypot(h, x))  # cone normal vs panel normal
    phi = math.radians(90) - math.atan(1 / M) if x == 0 else phi
    lb.append(dict(x=x, crease_z=round(zc(x), 2), crown_z=crown, beyond_mm=round(d, 2), kappa=round(kappa, 4), strain_lb_pct=round(100 * kappa * d * (1 - math.cos(math.radians(52.15))), 2)))
res['wrap_strain_lower_bound'] = lb
for r in lb: print('LB', r)
json.dump(res, open(HERE + 'critic2_analysis.json', 'w'), indent=1)
