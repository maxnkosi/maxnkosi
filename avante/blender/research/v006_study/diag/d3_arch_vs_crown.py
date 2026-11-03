"""v006 study C: analytic arch edge (v006 code) vs rev D crown, and the arch the glass needs.
Imports build_avante_master.py as a module (main() is not run). Read-only.
Usage: Blender -b --factory-startup -P d3_arch_vs_crown.py -- OUTDIR
"""
import sys, os, math, json, importlib.util
argv = sys.argv[sys.argv.index('--') + 1:]; OUT = argv[0]
ROOT = '/Users/maxhlomendlini/Documents/Avante/avante/blender'
spec = importlib.util.spec_from_file_location('bam', os.path.join(ROOT, 'build_avante_master.py'))
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

res = {}
CAP = b.CAP_TOP
# 1. dieline crown y(x) along the top edge of TRIM (front half, x >= 0)
top = [p for p in b.TRIM if p[1] < 15 and p[0] >= 0]
top.sort()
def y_trim(x):
    for (x0, y0), (x1, y1) in zip(top, top[1:]):
        if x0 <= x <= x1: return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return top[-1][1]
res['crown_drop_dieline_centre_to_kink'] = round(y_trim(46.9) - y_trim(0), 3)
res['crown_drop_dieline_centre_to_fold_HF_E'] = round(y_trim(b.HF_E) - y_trim(0), 3)

# 2. vertical placement of the crown: current code (sin49 above Z_EDGE) vs isometric on a vertical panel
def v_of(s, y):  # invert dev_xy y for perimeter coordinate s (bisection on v)
    lo, hi = -40.0, 100.0
    for _ in range(80):
        m = (lo + hi) / 2
        if b.dev_xy(s, m)[1] < y: lo = m
        else: hi = m
    return (lo + hi) / 2
bottom_y_centre = 78.258
v_bot = v_of(0.0, bottom_y_centre); v_top = v_of(0.0, y_trim(0))
res['dieline_height_centre_true_mm'] = round(v_bot - v_top, 3)
res['datum_span_mm'] = round(165.9 - 79.64, 3)
res['code_crown_z'] = round(b.Z_EDGE + (-v_top) * math.sin(math.radians(49)), 3)
res['iso_crown_z_if_bottom_held'] = round(b.Z_EDGE - v_top, 3)
res['iso_crown_from_cap_if_bottom_held'] = round(CAP - (b.Z_EDGE - v_top), 3)
res['iso_bottom_from_cap_if_crown_held'] = round(79.64 + (v_bot - v_top), 3)
res['roundel_top_from_cap'] = round(CAP - b.ROUNDEL_Z - b.ROUNDEL_FILM_R, 3)

# 3. v006 arch edge on the glass: lowest z where outer_r departs from the held body section by > tol
h = b.width_at(b.Z_HOLD) / 2
def panel_point(s):  # perimeter coordinate on the held square (front = -y), returns (x, y)
    S = b.width_at(b.Z_HOLD); a = b.CHAMFER * S; hh = S / 2; hf3 = hh - a
    if s <= b.HF_E: return (s / b.HF_E * hf3, -hh)
    if s <= b.S1_E:
        u = (s - b.HF_E) / (b.S1_E - b.HF_E); return (hf3 + (hh - hf3) * u, -hh + a * u)
    u = (s - b.S1_E) / (b.S2_E - b.S1_E); return (hh, -hh + a + (2 * hh - 2 * a) * u)
def arch_z(s, tol=0.05):
    x, y = panel_point(s); th = math.atan2(y, x)
    z = 120.0
    while z < 185:
        body = b.section_r(th, b.body_S(z), b.roundness(z))
        if body - b.outer_r(th, z) > tol: return z
        z += 0.05
    return None
def crown_z_code(s):
    y = y_trim(s if s <= 46.9 else s)  # dieline x ~ s on the front/chamfer within 0.1 mm (fan development)
    v = v_of(s, y)
    return b.Z_EDGE - v if v >= 0 else b.Z_EDGE + (-v) * math.sin(math.radians(49)), v
rows = []
for s in [0, 5, 10, 15, 20, 25, 30, 33, 35, 37.78, 40, 42.5, 45, 47.28, 55, 70, 90, 110, 119]:
    zc, v = crown_z_code(s) if s <= 119.4 else (None, None)
    za = arch_z(s); x, y = panel_point(s)
    rows.append(dict(s=s, x=round(x, 2), y=round(y, 2), r_axis=round(math.hypot(x, y), 2),
                     crown_z_code=round(zc, 2), crown_from_cap_code=round(CAP - zc, 2),
                     crown_z_iso_bottom_held=round(b.Z_EDGE - v, 2), crown_z_iso_crown_held=round(b.Z_EDGE - v - (b.Z_EDGE - v_top - res['code_crown_z']), 2),
                     arch_edge_z_v006=None if za is None else round(za, 2),
                     clearance_v006_mm=None if za is None else round(za - zc, 2)))
res['arch_vs_crown'] = rows

# 4. required dome radius R(z) for arch = crown + c, on the held 88.9 square (front + chamfer), crown held at 79.64
def req(c, mode):
    out = []
    for r in rows:
        if r['s'] > b.S1_E: continue
        zc = r['crown_z_iso_crown_held'] if mode == 'crown_held' else (r['crown_z_iso_bottom_held'] if mode == 'bottom_held' else r['crown_z_code'])
        # fillet: softmin(r_body, R, k) ~ R when R << r_body; at the edge R_req = r_axis + small margin, use r_axis
        out.append(dict(s=r['s'], z_arch=round(zc + c, 2), R_req=r['r_axis'], R_v006_at_z=round(b.shoulder_R(zc + c), 2)))
    return out
res['required_arch'] = {f'{mode}_c{c}': req(c, mode) for mode in ('crown_held', 'bottom_held') for c in (1.0, 2.0, 3.0)}

# 5. v006 shoulder_R and silhouette
res['shoulder_R_table'] = [dict(z=z, R_v006=round(b.shoulder_R(z), 2), half_width_profile=round(b.width_at(z) / 2, 2))
                           for z in [131, 135, 138, 140, 142, 144, 146, 148, 150, 152, 152.5, 154, 156, 157.5, 158.5, 160, 162]]
res['panel_half_width_h'] = round(h, 3)
res['silhouette_panel_apex_z'] = next(z / 10 for z in range(1400, 1700) if b.width_at(z / 10) / 2 < h - 0.05)

os.makedirs(OUT, exist_ok=True)
json.dump(res, open(os.path.join(OUT, 'd3_arch_vs_crown.json'), 'w'), indent=1)
print('D3', json.dumps({k: v for k, v in res.items() if not isinstance(v, (list, dict))}))
for r in rows: print('ROW', r)
for z in res['shoulder_R_table']: print('SR', z)
for k, v in res['required_arch'].items(): print('REQ', k, v)
