"""
Avante Brandy — master scene builder (avante_master_v007)
==========================================================
v007 (research/v006_study, judge's ruling): reference-true Imperial glass from glass_v007.py — straight
52 deg cone cut by the chamfered square (arch at ~156.6 centre / ~146 corners), rho 4 rolling-ball fillet,
R 1 vertical edges, 32 deg heel bevel, flat floor; label kept as approved (rev D datums).
v005 (3 Nov 2026, research/v005_study): reference-led foil, emboss, paper and label pass.
Client decisions: dyed-through navy stock, 0.15 mm label, bird/spear graphic toned down,
angled macro cameras added, roundel keeps raised 0.04 mm foil. Run prep_v005_textures.py first.

Builds the Concept 1 rev D packaging on the 750 ml Imperial bottle:
  GLS-01 glass · LIQ-01 brandy · SLV-CAP-01 closed-top navy shrink capsule + gold pinline
  LBL-NECK-01 collar with radial flag · LBL-FRONT-01 wrap (front + bevels + sides)
  LBL-ROUNDEL-01 clear-film roundel · studio lights · cameras.

Run inside Blender (Scripting tab → Open → Run Script), or headless:
    blender -b -P build_avante_master.py -- --render preview.png
Textures are read from ./textures next to this script (exported from Figma
file JcxeRDhCrtgZUXhTWQn2hV, page 03 / page 01 § L).

All dimensions in millimetres in the code; the scene is real-size in metres
(1 BU = 1 m) so Cycles light falloff is physical. Values tagged P are
proposals from the Figma/Notion handoff and must be replaced by measurements.
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector, Quaternion

MM = 0.001  # mm → metres

# ---------------------------------------------------------------- data
# Outer width (flat-to-flat for the square body, diameter for the round neck)
# vs height above base, glass only — from the user's cap-off photo scaled to
# the supplier height 226.9 mm (V). ±0.7 mm.
PROFILE = [(0, 55.6), (1, 60.0), (2, 62.2), (3.5, 63.8), (5, 64.9), (7.5, 68.5), (10, 71.6),
           (20, 73.0), (40, 75.6), (60, 77.0), (80, 79.6), (100, 83.0), (120, 85.0), (140, 88.1),
           (145, 89.0), (150, 89.0), (152.5, 88.9), (155, 88.4), (157.5, 85.5), (160, 80.3),
           (162.5, 74.0), (165, 67.6), (167.5, 60.8), (170, 54.2), (172.5, 48.5), (175, 43.5),
           (177.5, 39.8), (180, 36.8), (182.5, 35.8), (185, 35.0), (188, 34.3), (190, 34.1),
           (215, 34.1), (216.5, 36.5), (218, 40.5), (220, 41.5), (223, 41.0), (224.5, 40.0),
           (225.7, 38.0), (226.5, 35.0), (226.9, 32.5)]
GLASS_H = 226.9          # V supplier
FILL_Z = GLASS_H - 66.0  # V supplier fill height (66 mm below glass top)
FILL_ML = 750.0          # V
CAP_TOP = 238.1          # P (glass + ≈11.2 mm bar-top)
WALL = 3.6               # A side wall; thinner so the heavier heel still holds 750 ml
BORE = 26.0              # P neck bore
CHAMFER = 0.0754         # P chamfer leg / side (W2124 ratio)
N_RING = 256
EDGE_SOFT = 0.125        # v007: soft-min width k; vertical edge R = 7.91 k = 1.0 mm (v006 0.7 was R 5.5)
GLASS_MODEL = 'v007'     # 'v007' = glass_v007.py (reference-true shoulder); 'legacy' = v006 dome below
LABEL_T = 0.15           # D v005 client: dyed-through navy felt stock incl. adhesive (mm)
LABEL_GAP = 0.005        # v005: adhesive-wetted contact, no air film (mm)
LABEL_BEVEL = 0.025      # v005: softened die-cut edge (mm)
EMB_H = 0.20             # P emboss height EMB-01 (mm)
ROUNDEL_RELIEF = 0.04    # A stamped-foil relief on film (mm); stays within approved foil on film
HEEL_R = 5.0             # v007 (judge, raw2): inner heel fillet radius (mm)
PUNT_H = 0.0             # v007 (raw2 shows a flat inner floor); was 3.5
BASE_T = 20.0            # solved in main()

# rev D label placement (mm, heights above base)
Z_EDGE = CAP_TOP - 87.5          # max-width line = wrap development origin
CAPSULE_BOTTOM = CAP_TOP - 66.27
PINLINE_TOP = CAP_TOP - 64.85
COLLAR_TOP, COLLAR_BOT = CAP_TOP - 23.66, CAP_TOP - 37.64
ROUNDEL_Z, ROUNDEL_X = CAP_TOP - 195.9, -0.43
ROUNDEL_FILM_R, ROUNDEL_PRINT_R, ROUNDEL_TEX = 46.706 / 2, 43.71 / 2, 47.706

# developed wrap (page 01 § L, frame 29:3) — polyhedral fan development
DEV_R = 3.825 * 89.0 / 0.4885
HF_E, S1_E, S2_E = 37.78, 47.28, 47.28 + 75.6
WRAP_ART = dict(x=-121.734, y=-12.414, w=243.469, h=101.258)
SHOULDER_STRETCH = 1.0 / math.sin(math.radians(49))
TRIM = [(-119.4, 14.429), (-46.9, 5.64), (-46.638, 5.527), (-45.867, 5.211), (-44.621, 4.712),
        (-42.94, 4.052), (-40.851, 3.249), (-38.389, 2.325), (-36.292, 1.434), (-34.057, 0.526),
        (-31.635, -0.555), (-29.051, -1.834), (-26.33, -3.112), (-23.5, -4.367), (-20.587, -5.57),
        (-17.617, -6.696), (-14.616, -7.721), (-11.607, -8.618), (-8.619, -9.362), (-5.679, -9.925),
        (-2.81, -10.286), (0.0, -10.414), (2.81, -10.286), (5.679, -9.925), (8.619, -9.362),
        (11.607, -8.618), (14.616, -7.721), (17.617, -6.696), (20.587, -5.57), (23.5, -4.367),
        (26.33, -3.112), (29.051, -1.834), (31.635, -0.555), (34.057, 0.526), (36.292, 1.434),
        (38.389, 2.325), (40.851, 3.249), (42.94, 4.052), (44.621, 4.712), (45.867, 5.211),
        (46.638, 5.527), (46.9, 5.64), (119.4, 14.429), (106.749, 86.63), (41.93, 78.772),
        (33.515, 78.258), (-33.515, 78.258), (-41.93, 78.772), (-106.749, 86.63)]

# collar (page 01 § L, frame 30:2)
NECK_D = 34.1
COLLAR_F = 1228 * 0.019356
COLLAR_C = math.pi * NECK_D
COLLAR_ART_W, COLLAR_ART_H, COLLAR_BLEED = 158.667, 17.975, 2.0

# ---------------------------------------------------------------- helpers
def lerp(a, b, t): return a + (b - a) * t

def _pchip():
    """Monotone cubic (Fritsch-Carlson) slopes: passes through every PROFILE point, no kinks, no overshoot."""
    x = [p[0] for p in PROFILE]; y = [p[1] for p in PROFILE]; n = len(x)
    h = [x[i + 1] - x[i] for i in range(n - 1)]; d = [(y[i + 1] - y[i]) / h[i] for i in range(n - 1)]
    m = [d[0]] + [0.0] * (n - 2) + [d[-1]]
    for i in range(1, n - 1):
        if d[i - 1] * d[i] > 0:
            w1, w2 = 2 * h[i] + h[i - 1], h[i] + 2 * h[i - 1]
            m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i])
    return x, y, h, m
_PX, _PY, _PH, _PM = _pchip()

def width_at(z):
    if z <= _PX[0]: return _PY[0]
    if z >= _PX[-1]: return _PY[-1]
    for i in range(len(_PX) - 1):
        if z <= _PX[i + 1]:
            t = (z - _PX[i]) / _PH[i]; t2, t3 = t * t, t * t * t
            return ((2 * t3 - 3 * t2 + 1) * _PY[i] + (t3 - 2 * t2 + t) * _PH[i] * _PM[i]
                    + (-2 * t3 + 3 * t2) * _PY[i + 1] + (t3 - t2) * _PH[i] * _PM[i + 1])

def roundness(z):  # 0 = chamfered square, 1 = round. v005b: only the neck finish; the dome rounds the shoulder
    t = min(max((z - 182.0) / 4.0, 0.0), 1.0)
    return t * t * (3 - 2 * t)

# v005b shoulder (client bottle refs, Figma 56:35): a revolved dome cutting the square body, so each flat
# face ends in an arch (high at the panel centre, carved down at the corners) instead of a straight crease.
# The body square is held above Z_HOLD; the dome follows the measured front silhouette above Z_ARCH_F and
# eases out to clear the corners by Z_ARCH_C. A: arch heights read from the refs and the rev D wrap crown.
Z_HOLD = 147.5  # v007: PROFILE slope is 0 here, so holding the square adds no break (v006 152.5 left a 1.9 deg ring)
Z_ARCH_C, Z_ARCH_F, ARCH_K = 131.0, 157.5, 1.2  # legacy v006 dome only (GLASS_MODEL = 'legacy')

def softmin(a, b, k):
    m = min(a, b)
    return m - k * math.log(math.exp(-(a - m) / k) + math.exp(-(b - m) / k))

_SR = {}
def shoulder_R(z):
    """Dome radius (mm) at height z: the front silhouette above Z_ARCH_F, a monotone Hermite ease below it
    that leaves the corners untouched (R = corner radius + 4k, zero slope) at Z_ARCH_C, growing below."""
    if not _SR:
        S = width_at(Z_HOLD); _SR['rc'] = max(sq_radius(math.radians(a / 10), S) for a in range(0, 901)) + 4 * ARCH_K
        _SR['rf'] = width_at(Z_ARCH_F) / 2; _SR['mf'] = (width_at(Z_ARCH_F + 0.25) - width_at(Z_ARCH_F - 0.25)) / 2 / 0.5
    if z >= Z_ARCH_F: return width_at(z) / 2
    if z <= Z_ARCH_C: return _SR['rc'] + 2.0 * (Z_ARCH_C - z)
    L = Z_ARCH_F - Z_ARCH_C; t = (z - Z_ARCH_C) / L; t2, t3 = t * t, t * t * t
    return (2 * t3 - 3 * t2 + 1) * _SR['rc'] + (-2 * t3 + 3 * t2) * _SR['rf'] + (t3 - t2) * L * _SR['mf']

def dome_cut(r, z, inset=0.0):
    """Section radius r cut by the shoulder dome, offset inward by inset (wall, liquid)."""
    return softmin(r, shoulder_R(z) - inset, ARCH_K) if z > Z_ARCH_C - 20 else r

def body_S(z):  # square body width; held above the shoulder line, where the dome takes over
    return width_at(min(z, Z_HOLD))

def outer_r(theta, z):
    return dome_cut(section_r(theta, body_S(z), roundness(z)), z)

def sq_radius(theta, S):
    h, a = S / 2, CHAMFER * S
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    r1 = h / max(c, s)
    r2 = (S - a) / (c + s)
    # v007: stable soft-min (the raw exp(-r/k) form underflows below k ~0.078); R = 7.91 k on these edges
    return softmin(r1, r2, EDGE_SOFT)

def section_r(theta, S, t):
    return (1 - t) * sq_radius(theta, S) + t * S / 2

def ring(z, S, t, n=N_RING, off=0.0, cut=None):
    """cut: None = plain section; a number = also cut by the shoulder dome, inset by that many mm."""
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = section_r(th, S, t)
        if cut is not None: r = dome_cut(r, z, cut)
        r += off
        pts.append(((r * math.cos(th)) * MM, (r * math.sin(th)) * MM, z * MM))
    return pts

def section_area(S, t, n=360, z=None, cut=None):
    a = 0.0
    def r(th):
        v = section_r(th, S, t)
        return dome_cut(v, z, cut) if cut is not None else v
    for i in range(n):
        th0, th1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        a += 0.5 * r(th0) * r(th1) * math.sin(th1 - th0)
    return a  # mm²

def inner_width(z, base_t=None):
    base_t = BASE_T if base_t is None else base_t
    w = BORE if z >= 185 else max(body_S(z) - 2 * WALL, BORE)  # v005b: held square, the dome cuts it
    dz = z - base_t
    if 0 <= dz < HEEL_R:  # v004: filleted inner heel, no hard 90 degree floor
        w -= 2 * (HEEL_R - math.sqrt(max(HEEL_R ** 2 - (HEEL_R - dz) ** 2, 0.0)))
    return w

def inner_volume(z0, z1, dz=0.25):
    v, z = 0.0, z0
    while z < z1:
        zz = min(z + dz, z1)
        zm = (z + zz) / 2
        v += section_area(inner_width(zm, z0), roundness(zm), z=zm, cut=(WALL if zm < 185 else None)) * (zz - z)
        z = zz
    W0 = inner_width(z0, z0)
    return (v - 0.5 * PUNT_H * W0 * W0) / 1000.0  # ml, less the punt dome

def solve_base_thickness():
    lo, hi = 2.0, 60.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if inner_volume(mid, FILL_Z) > FILL_ML: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def inner_stack(base_t, top):
    """Inner wall, bottom-up, from the punt centre through the heel fillet to z=top. Returns (z, S, t)."""
    W0 = inner_width(base_t, base_t); t0 = roundness(base_t); out = []
    for i in range(1, 21):
        k = i / 20
        out.append((base_t + PUNT_H * (1 - k * k), W0 * k, t0))
    for a in range(5, 91, 5):
        z = base_t + HEEL_R * (1 - math.cos(math.radians(a)))
        out.append((z, inner_width(z, base_t), roundness(z)))
    for z in z_samples(base_t + HEEL_R + 0.25, top):
        out.append((z, inner_width(z, base_t), roundness(z)))
    return out

def z_samples(z0, z1):
    zs = set([round(z0, 3), round(z1, 3)] + [round(p[0], 3) for p in PROFILE if z0 < p[0] < z1])
    z = z0
    while z < z1:  # v004: fine steps through the heel and shoulder
        zs.add(round(z, 3))
        z += 0.5 if (z < 12 or 148 < z < 192 or z > 212) else 1.0
    return sorted(zs)

def mesh_from(name, verts, faces, collection):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    collection.objects.link(ob)
    return ob

def loft(rings, close_bottom=None, close_top=None):
    """rings: list of vertex rings (equal length). close_*: centre point or None."""
    verts, faces = [], []
    n = len(rings[0])
    for r in rings: verts.extend(r)
    for k in range(len(rings) - 1):
        a, b = k * n, (k + 1) * n
        for i in range(n):
            j = (i + 1) % n
            faces.append((a + i, a + j, b + j, b + i))
    if close_bottom is not None:
        c = len(verts); verts.append(close_bottom)
        faces += [(c, (i + 1) % n, i) for i in range(n)]
    if close_top is not None:
        c = len(verts); verts.append(close_top)
        base = (len(rings) - 1) * n
        faces += [(c, base + i, base + (i + 1) % n) for i in range(n)]
    return verts, faces

def shade_smooth(ob, angle=35):
    for p in ob.data.polygons: p.use_smooth = True
    try:
        bpy.context.view_layer.objects.active = ob
        ob.select_set(True)
        bpy.ops.object.shade_auto_smooth(angle=math.radians(angle))
        ob.select_set(False)
    except Exception:
        pass

def recalc_normals(ob, inside=False):
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if inside: bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(ob.data); bm.free()

def coll(name):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(c)
    return c

def tex_dir():
    cands = []
    try: cands.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError: pass
    for t in bpy.data.texts:
        if t.filepath: cands.append(os.path.dirname(bpy.path.abspath(t.filepath)))
    if bpy.data.filepath: cands.append(os.path.dirname(bpy.data.filepath))
    cands.append(os.getcwd())
    for c in cands:
        if os.path.isdir(os.path.join(c, 'textures')): return os.path.join(c, 'textures')
    raise RuntimeError('textures/ folder not found next to the script')

# ---------------------------------------------------------------- materials
def node_mat(name):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (800, 0)
    return m, nt, out

def principled(nt, **kw):
    p = nt.nodes.new('ShaderNodeBsdfPrincipled')
    for k, v in kw.items():
        if k in p.inputs: p.inputs[k].default_value = v
    return p

def img(nt, path, non_color=False, loc=(-600, 0)):
    n = nt.nodes.new('ShaderNodeTexImage'); n.location = loc
    n.image = bpy.data.images.load(path, check_existing=True)
    if non_color: n.image.colorspace_settings.name = 'Non-Color'
    n.interpolation = 'Cubic'; n.extension = 'CLIP'
    return n

def srgb(c):  # hex → linear tuple
    c = c.lstrip('#'); v = [int(c[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4) for x in v) + (1.0,)

NAVY, GOLD = srgb('#003653'), srgb('#E7C187')
FOIL_F0 = (0.95, 0.69, 0.33, 1.0)  # FOIL-01 warm pale gold reflectance (P, match to foil swatch)

def mat_glass():
    m, nt, out = node_mat('M_GLS-01_Flint')
    p = principled(nt, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0, 'IOR': 1.52, 'Transmission Weight': 1.0})
    vol = nt.nodes.new('ShaderNodeVolumeAbsorption')
    vol.inputs['Color'].default_value = (0.90, 0.97, 0.93, 1); vol.inputs['Density'].default_value = 10.0  # faint iron green, shows at thick edges only
    # moulded glass is never optically flat: very low-frequency waviness
    tc = nt.nodes.new('ShaderNodeTexCoord'); no = nt.nodes.new('ShaderNodeTexNoise'); no.inputs['Scale'].default_value = 28.0; no.inputs['Detail'].default_value = 1.0
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = 1.0; bu.inputs['Distance'].default_value = 0.00012
    nt.links.new(tc.outputs['Object'], no.inputs['Vector']); nt.links.new(no.outputs[0], bu.inputs['Height']); nt.links.new(bu.outputs[0], p.inputs['Normal'])
    nt.links.new(p.outputs[0], out.inputs['Surface']); nt.links.new(vol.outputs[0], out.inputs['Volume'])
    return m

def mat_brandy():
    m, nt, out = node_mat('M_LIQ-01_Brandy')
    p = principled(nt, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0, 'IOR': 1.355, 'Transmission Weight': 1.0})
    vol = nt.nodes.new('ShaderNodeVolumeAbsorption')
    vol.inputs['Color'].default_value = (0.9, 0.7, 0.2, 1)  # P — target transmittance ≈(0.57,0.19,0.01) over 80 mm; calibrate to reference photography
    vol.inputs['Density'].default_value = 95.0                   # per metre
    nt.links.new(p.outputs[0], out.inputs['Surface']); nt.links.new(vol.outputs[0], out.inputs['Volume'])
    return m

def noise(nt, scale, detail=2.0, stretch=None):
    tc = nt.nodes.new('ShaderNodeTexCoord'); n = nt.nodes.new('ShaderNodeTexNoise')
    n.inputs['Scale'].default_value = scale; n.inputs['Detail'].default_value = detail
    if stretch:
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = stretch
        nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], n.inputs['Vector'])
    else:
        nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    return n

def uv_mm(nt, w, h):
    """UV scaled to millimetres of artwork, so texture sizes are real and follow the sheet (v005)."""
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (w, h, 1.0)
    nt.links.new(tc.outputs['UV'], mp.inputs['Vector']); return mp.outputs[0]

def noise_v(nt, vec, feature_mm, detail=2.0, stretch=None):
    """Noise over a mm vector; feature_mm is the blob size. stretch=(sx, sy) elongates (fibres)."""
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 1.0 / feature_mm
    n.inputs['Detail'].default_value = detail
    if stretch:
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (stretch[0], stretch[1], 1.0)
        nt.links.new(vec, mp.inputs['Vector']); vec = mp.outputs[0]
    nt.links.new(vec, n.inputs['Vector']); return n.outputs['Fac']

def map_range(nt, val, a, b, interp='SMOOTHSTEP'):
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.interpolation_type = interp
    mr.inputs['From Min'].default_value = a; mr.inputs['From Max'].default_value = b
    nt.links.new(val, mr.inputs['Value']); return mr.outputs[0]

def math_node(nt, op, a=None, b=None):
    m = nt.nodes.new('ShaderNodeMath'); m.operation = op
    for i, v in enumerate((a, b)):
        if v is None: continue
        if isinstance(v, (int, float)): m.inputs[i].default_value = v
        else: nt.links.new(v, m.inputs[i])
    return m.outputs[0]

def foil_bsdf(nt, vec, pits=None):
    """FOIL-01 hot foil, v005 (study A): a polished heated die leaves near-mirror tops. Paper texture
    survives only as rare shallow pits (<= 6 um) plus a fine 0.13 mm grain (2 um); no mm-scale term
    (that was the v004 'crumple'). Roughness 0.07 +- 0.015 at 0.12 mm. Colour stays FOIL_F0 (gold data)."""
    fb = principled(nt, **{'Base Color': FOIL_F0, 'Metallic': 1.0})
    fr = noise_v(nt, vec, 0.12, 2.0)
    nt.links.new(math_node(nt, 'ADD', 0.055, math_node(nt, 'MULTIPLY', fr, 0.03)), fb.inputs['Roughness'])
    grain = math_node(nt, 'MULTIPLY', noise_v(nt, vec, 0.13, 2.0), 2e-6)
    # pits only in the deepest felt marks (about 5-10 % of the area), 3 um: first test at 0.30-0.48 / 6 um
    # pitted nearly half of every letter, which mirror foil exaggerates into blotches
    h = grain if pits is None else math_node(nt, 'ADD', grain, math_node(nt, 'MULTIPLY', map_range(nt, pits, 0.25, 0.35, 'SMOOTHERSTEP'), 3e-6))
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Strength'].default_value = 1.0; bu.inputs['Distance'].default_value = 1.0
    nt.links.new(h, bu.inputs['Height']); nt.links.new(bu.outputs[0], fb.inputs['Normal'])
    return fb

def mat_label(name, color, foil, art_wh, emb=None, uv=None):
    """SUB-01 dyed-through navy felt paper, INK, VAR-01 (UV), FOIL-01, EMB-01. v005: all texture sizes
    are real mm in label UV space (fibres follow the machine direction on every panel)."""
    m, nt, out = node_mat(name)
    T = tex_dir()
    c = img(nt, os.path.join(T, color), loc=(-900, 300))
    f = img(nt, os.path.join(T, foil), True, loc=(-900, -300))
    vec = uv_mm(nt, *art_wh)
    # paper relief (metres), study C: felt pecks 0.6 mm at 30 um, body 1.2 mm at 10 um,
    # fibres 1.2 x 0.25 mm at 6 um along the sheet (U)
    vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 1 / 0.6
    nt.links.new(vec, vor.inputs['Vector'])
    peck = math_node(nt, 'MULTIPLY', map_range(nt, vor.outputs['Distance'], 0.0, 0.5), 30e-6)
    body = noise_v(nt, vec, 1.2, 3.0)
    fibre = noise_v(nt, vec, 1.0, 2.0, stretch=(1 / 1.2, 1 / 0.25))
    relief = math_node(nt, 'ADD', peck, math_node(nt, 'ADD', math_node(nt, 'MULTIPLY', body, 10e-6), math_node(nt, 'MULTIPLY', fibre, 6e-6)))
    # bare paper (cream knock-out) versus inked area, from artwork luminance
    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(c.outputs['Color'], bw.inputs[0])
    bare = map_range(nt, bw.outputs[0], 0.30, 0.60, 'LINEAR')
    # ink roughness 0.66 +- 0.04; cream ink 0.78
    ink_r = math_node(nt, 'ADD', 0.62, math_node(nt, 'MULTIPLY', noise_v(nt, vec, 0.4, 3.0), 0.08))
    rough = nt.nodes.new('ShaderNodeMix'); rough.data_type = 'FLOAT'
    nt.links.new(bare, rough.inputs['Factor']); nt.links.new(ink_r, rough.inputs['A']); rough.inputs['B'].default_value = 0.78
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 1.0; bump.inputs['Distance'].default_value = 1.0
    nt.links.new(relief, bump.inputs['Height'])
    # mottle: cloudy 6 mm, +-3 %, multiplicative (v004 was additive +-0.03, about +-30 % on navy)
    hsv = nt.nodes.new('ShaderNodeHueSaturation')
    nt.links.new(c.outputs['Color'], hsv.inputs['Color'])
    nt.links.new(math_node(nt, 'ADD', 0.97, math_node(nt, 'MULTIPLY', noise_v(nt, vec, 6.0, 2.0), 0.06)), hsv.inputs['Value'])
    paper = principled(nt, **{'Sheen Weight': 0.0, 'Specular IOR Level': 0.32})  # v005: no suede sheen
    nt.links.new(hsv.outputs[0], paper.inputs['Base Color']); nt.links.new(rough.outputs[0], paper.inputs['Roughness']); nt.links.new(bump.outputs[0], paper.inputs['Normal'])
    foilb = foil_bsdf(nt, vec, pits=body)
    mix = nt.nodes.new('ShaderNodeMixShader'); mix.location = (400, 0)
    nt.links.new(f.outputs['Color'], mix.inputs['Fac'])
    nt.links.new(paper.outputs[0], mix.inputs[1]); nt.links.new(foilb.outputs[0], mix.inputs[2])
    if uv:
        u = img(nt, os.path.join(T, uv), True, loc=(-900, -600))
        nt.links.new(u.outputs['Color'], paper.inputs['Coat Weight'])
        paper.inputs['Coat Roughness'].default_value = 0.08
    if emb:
        # v005: rounded 16-bit height (prep_v005_textures.py), 0.2 mm peak, foil edge at the foot
        e = img(nt, os.path.join(T, emb), True, loc=(-900, -900))
        dsp = nt.nodes.new('ShaderNodeDisplacement'); dsp.location = (500, -400); dsp.space = 'OBJECT'
        dsp.inputs['Midlevel'].default_value = 0.0; dsp.inputs['Scale'].default_value = EMB_H * MM
        nt.links.new(e.outputs['Color'], dsp.inputs['Height'])
        nt.links.new(dsp.outputs[0], out.inputs['Displacement'])
        m.displacement_method = 'BOTH'
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    return m

def mat_cut_edge():
    # v005 client: dyed-through navy, so the die-cut core is navy (slightly lifted by exposed fibre)
    return mat_simple('M_SUB-01_CutEdge_Navy', **{'Base Color': tuple(min(x * 1.25, 1) for x in NAVY[:3]) + (1,), 'Roughness': 0.9})

def mat_reverse():
    # v005: reverse of the dyed sheet against the glass, wetted by adhesive: darker, no own shine, no relief
    return mat_simple('M_SUB-01_Reverse_Wetted', **{'Base Color': tuple(x * 0.8 for x in NAVY[:3]) + (1,), 'Roughness': 0.85, 'Specular IOR Level': 0.2})

def mat_roundel():
    m, nt, out = node_mat('M_LBL-ROUNDEL-01_ClearFilm')
    T = tex_dir()
    c = img(nt, os.path.join(T, 'COLOR__LBL-ROUNDEL-01.png'), loc=(-900, 300))
    f = img(nt, os.path.join(T, 'MASK-FOIL-01__LBL-ROUNDEL-01.png'), True, loc=(-900, -100))
    ink = principled(nt, **{'Roughness': 0.5})
    nt.links.new(c.outputs['Color'], ink.inputs['Base Color'])
    foilb = foil_bsdf(nt, uv_mm(nt, ROUNDEL_TEX, ROUNDEL_TEX))  # on film: no paper pits
    mix = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(f.outputs['Color'], mix.inputs['Fac'])
    nt.links.new(ink.outputs[0], mix.inputs[1]); nt.links.new(foilb.outputs[0], mix.inputs[2])
    # SUB-02 clear film. v005 fix: Base Color white (v004 left the 0.8 default, which greyed the ring)
    film = principled(nt, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.04, 'IOR': 1.49, 'Transmission Weight': 1.0})
    uvn = nt.nodes.new('ShaderNodeTexCoord')
    sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0)
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = ROUNDEL_PRINT_R / ROUNDEL_TEX
    nt.links.new(uvn.outputs['UV'], sub.inputs[0]); nt.links.new(sub.outputs[0], ln.inputs[0]); nt.links.new(ln.outputs['Value'], lt.inputs[0])
    mix2 = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lt.outputs[0], mix2.inputs['Fac']); nt.links.new(film.outputs[0], mix2.inputs[1]); nt.links.new(mix.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs['Surface'])
    # v004: stamped-foil relief from the approved foil mask; no change of physical treatment
    dsp = nt.nodes.new('ShaderNodeDisplacement'); dsp.space = 'OBJECT'; dsp.inputs['Midlevel'].default_value = 0.0
    dsp.inputs['Scale'].default_value = ROUNDEL_RELIEF * MM
    nt.links.new(f.outputs['Color'], dsp.inputs['Height']); nt.links.new(dsp.outputs[0], out.inputs['Displacement'])
    m.displacement_method = 'BOTH'
    return m

def mat_simple(name, **kw):
    m, nt, out = node_mat(name)
    p = principled(nt, **kw); nt.links.new(p.outputs[0], out.inputs['Surface'])
    return m

# ---------------------------------------------------------------- build
def clear_scene():
    for ob in list(bpy.data.objects): bpy.data.objects.remove(ob, do_unlink=True)
    for c in list(bpy.data.collections): bpy.data.collections.remove(c)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for x in list(blk):
            if x.users == 0: blk.remove(x)

def build_glass(C, base_t):
    # v005b: held body square cut by the revolved shoulder dome (arched faces), inner wall inset by WALL
    outer = [ring(z, body_S(z), roundness(z), cut=0.0) for z in z_samples(0.0, GLASS_H)]
    inner = [ring(z, S, t, cut=(WALL if z < 185 else None)) for z, S, t in reversed(inner_stack(base_t, GLASS_H))]
    verts, faces = loft(outer + inner, close_bottom=(0, 0, 1.2 * MM), close_top=(0, 0, (base_t + PUNT_H) * MM))
    ob = mesh_from('GLS-01_Glass', verts, faces, C)
    recalc_normals(ob); shade_smooth(ob, 40)
    return ob

def build_liquid(C, base_t):
    # v004: the liquid overlaps the glass by 0.05 mm. No air film, so no false total internal reflection.
    OV = 0.05
    rings = []
    for z, S, t in inner_stack(base_t, FILL_Z):
        if z >= FILL_Z: continue
        lift = OV if z < base_t + HEEL_R else 0.0
        rings.append(ring(z - lift, S + 2 * OV, t, cut=WALL - OV))
    Wf, tf = inner_width(FILL_Z, base_t) + 2 * OV, roundness(FILL_Z)
    rings.append(ring(FILL_Z, Wf, tf, cut=WALL - OV))
    # meniscus for about 40% ABV: 1.8 mm climb, flat within 2.5 mm (derived estimate)
    for dd, hh in ((0.0, 1.8), (0.1, 1.3), (0.3, 0.85), (0.6, 0.48), (1.0, 0.22), (1.6, 0.07), (2.5, 0.0)):
        rings.append(ring(FILL_Z + hh, Wf - 2 * dd, tf, cut=WALL - OV + dd))
    verts, faces = loft(rings, close_bottom=(0, 0, (base_t + PUNT_H - OV) * MM), close_top=(0, 0, FILL_Z * MM))
    ob = mesh_from('LIQ-01_Brandy', verts, faces, C)
    recalc_normals(ob); shade_smooth(ob, 40)
    return ob

def capsule_raw(theta, z):
    r_glass = outer_r(theta, min(z, GLASS_H)) if z <= GLASS_H else 0
    r_clos = 20.9 if z >= CAP_TOP - 14.8 else (17.8 if z >= CAP_TOP - 23.0 else 0)  # P bar-top head/band
    return max(r_glass, r_clos) + 0.06

_CAP_TABLE = {}
def capsule_profile(z):
    """Film over the closure: shrink film bridges steps instead of tracing them (smoothed about +-3 mm)."""
    key = round(z * 4)
    if key not in _CAP_TABLE:
        w, tot, W = 3.0, 0.0, 0.0
        for k in range(-12, 13):
            zz = z + w * k / 12; g = math.cos(math.pi * k / 24) ** 2
            tot += g * capsule_raw(0.0, min(zz, CAP_TOP)); W += g
        r_glass = outer_r(0.0, min(z, GLASS_H)) + 0.06 if z <= GLASS_H else 0.0
        _CAP_TABLE[key] = max(tot / W, r_glass)  # film can never sit under the glass bead
    return _CAP_TABLE[key]

def capsule_r(theta, z):
    k = min(max((z - 186.0) / 4.0, 0.0), 1.0)
    r = (1 - k) * capsule_raw(theta, z) + k * capsule_profile(z) if k > 0 else capsule_raw(theta, z)
    # restrained shrink pleats: real geometry, strongest on the neck, gone at hem and head
    hem = min(max((z - CAPSULE_BOTTOM) / 10.0, 0.0), 1.0)
    head = min(max((CAP_TOP - 15.0 - z) / 6.0, 0.0), 1.0)
    pl = math.sin(34 * theta + 1.3 * math.sin(3 * theta)) + 0.5 * math.sin(57 * theta + 2 * math.cos(5 * theta + z / 9.0))
    r += 0.075 * hem * head * pl * (0.6 + 0.4 * math.sin(z / 7.0 + 2 * theta))
    # back seam: 2 mm overlap, raised 0.06 mm, on the far side
    d = abs(((theta - math.pi / 2 + math.pi) % (2 * math.pi)) - math.pi) * r
    if d < 1.4: r += 0.06 * min(max((1.4 - d) / 0.4, 0.0), 1.0)
    if z > CAP_TOP - 2.0:  # 2 mm top fillet
        dz = z - (CAP_TOP - 2.0)
        r -= 2.0 - math.sqrt(max(4.0 - dz * dz, 0.0))
    return r

def build_capsule(C):
    zs = sorted(set([CAPSULE_BOTTOM, PINLINE_TOP] + [z for z in z_samples(CAPSULE_BOTTOM, CAP_TOP)] +
                    [CAP_TOP - 0.25 * k for k in range(8, 120)] +
                    [CAP_TOP - 2.0 + 2.0 * math.sin(math.radians(a)) for a in range(0, 91, 10)]))
    rings = []
    for z in zs:
        rings.append([((capsule_r(th, z)) * math.cos(th) * MM, (capsule_r(th, z)) * math.sin(th) * MM, z * MM)
                      for th in [2 * math.pi * i / N_RING for i in range(N_RING)]])
    verts, faces = loft(rings, close_top=(0, 0, CAP_TOP * MM))
    ob = mesh_from('SLV-CAP-01_Capsule', verts, faces, C)
    recalc_normals(ob)
    navy = mat_simple('M_SUB-03_ShrinkFilm_INK-01-S', **{'Base Color': NAVY, 'Roughness': 0.34, 'Coat Weight': 0.2, 'Coat Roughness': 0.18})
    gold = mat_simple('M_MET-01_GoldInk', **{'Base Color': GOLD, 'Metallic': 0.85, 'Roughness': 0.28})
    ob.data.materials.append(navy); ob.data.materials.append(gold)
    for p in ob.data.polygons:
        zc = sum(ob.data.vertices[v].co.z for v in p.vertices) / len(p.vertices) / MM
        p.material_index = 1 if zc < PINLINE_TOP else 0
    sol = ob.modifiers.new('film', 'SOLIDIFY'); sol.thickness = 0.05 * MM; sol.offset = 1
    shade_smooth(ob, 40)
    return ob

# --- wrap label --------------------------------------------------------------
def dev_xy(sE, v):
    """developed (dieline) coordinates in mm for perimeter coord sE and depth v."""
    sgn = 1 if sE >= 0 else -1; s = abs(sE)
    Yc = DEV_R * math.cos(HF_E / DEV_R)
    def V(sb, vv):
        th = sb / DEV_R; r = DEV_R - vv
        return (r * math.sin(th), Yc - r * math.cos(th))
    if s <= HF_E:
        # v003: flat front panel in the polyhedral fan. Rows stay horizontal and meet the bevel
        # panel exactly on the fold ray (v002 had a 1.02 mm jump here and at v=0: the crown step).
        th = HF_E / DEV_R
        return (sE / HF_E * (DEV_R - max(v, 0.0)) * math.sin(th), v * math.cos(th))
    if s <= S1_E:
        u = (s - HF_E) / (S1_E - HF_E); a, b = V(HF_E, v), V(S1_E, v)
    else:
        u = (s - S1_E) / (S2_E - S1_E); a, b = V(S1_E, v), V(S2_E, v)
    return (sgn * lerp(a[0], b[0], u), lerp(a[1], b[1], u))

def surf_xyz(sE, v, off):
    z = Z_EDGE - v if v >= 0 else Z_EDGE + (-v) * math.sin(math.radians(49))
    S = body_S(z); a = CHAMFER * S; h = S / 2; hf3 = h - a  # v005b: held body square
    sgn = 1 if sE >= 0 else -1; s = abs(sE)
    if s <= HF_E:
        x, y = (s / HF_E) * hf3, -h
    elif s <= S1_E:
        u = (s - HF_E) / (S1_E - HF_E); x, y = lerp(hf3, h, u), lerp(-h, -h + a, u)
    else:
        u = (s - S1_E) / (S2_E - S1_E); x, y = h, lerp(-h + a, h - a, u)
    x *= sgn
    th = math.atan2(y, x)
    r = outer_r(th, z) + off  # v005b: the wrap follows the arched shoulder
    return (r * math.cos(th) * MM, r * math.sin(th) * MM, z * MM)

def inside(pt, poly):
    x, y = pt; c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1: c = not c
    return c

def poly_sdf(pt, poly):
    """signed distance (mm) of pt to polygon; negative inside."""
    x, y = pt; dmin = 1e9; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy or 1e-12
        t = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / L2))
        ex, ey = x - (x1 + t * dx), y - (y1 + t * dy)
        dmin = min(dmin, ex * ex + ey * ey)
    d = math.sqrt(dmin)
    return -d if inside(pt, poly) else d

def clipped_grid(us, vs, sdf, pos, uvf):
    """Build a mesh over param grid (us × vs), clipped to sdf ≤ 0 with edge-interpolated
    boundary (marching-squares style). pos(u,v)→xyz, uvf(u,v)→(U,V)."""
    nu = len(us); d = {}
    for j, v in enumerate(vs):
        for i, u in enumerate(us): d[(i, j)] = sdf(u, v)
    verts, uvs, faces, key = [], [], [], {}
    def vid(k, u, v):
        if k not in key:
            key[k] = len(verts); verts.append(pos(u, v)); uvs.append(uvf(u, v))
        return key[k]
    for j in range(len(vs) - 1):
        for i in range(nu - 1):
            c = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
            vals = [d[k] for k in c]
            if all(x > 0 for x in vals): continue
            poly = []
            for e in range(4):
                a, b = c[e], c[(e + 1) % 4]; da, db = d[a], d[b]
                if da <= 0: poly.append(vid(('v',) + a, us[a[0]], vs[a[1]]))
                if (da <= 0) != (db <= 0):
                    t = da / (da - db)
                    u = lerp(us[a[0]], us[b[0]], t); v = lerp(vs[a[1]], vs[b[1]], t)
                    poly.append(vid(('e',) + tuple(sorted((a, b))), u, v))
            if len(poly) >= 3: faces.append(tuple(poly))
    return verts, uvs, faces

def paper_shell(ob, mat, thickness=LABEL_T):
    """v005: solidify the sheet so the glass-side face (the original surface) gets the wetted reverse,
    the new outer shell gets the printed face and the rim gets the navy die-cut core, then soften the
    cut edge. The reverse has no displacement, so the emboss no longer pushes into the glass.
    Measured in 5.1: with offset +1 the new (outer) shell keeps the base index and the original
    (glass-side) faces take material_offset."""
    ob.data.materials.append(mat)                # 0: printed face (outer shell)
    ob.data.materials.append(mat_cut_edge())     # 1: rim
    ob.data.materials.append(mat_reverse())      # 2: reverse (original faces, glass side)
    sol = ob.modifiers.new('paper', 'SOLIDIFY'); sol.thickness = thickness * MM; sol.offset = 1.0
    sol.use_rim = True; sol.use_even_offset = True
    sol.material_offset = 2; sol.material_offset_rim = 1
    bev = ob.modifiers.new('cut_edge', 'BEVEL'); bev.width = LABEL_BEVEL * MM; bev.segments = 2
    bev.limit_method = 'ANGLE'; bev.angle_limit = math.radians(60)
    shade_smooth(ob, 30)

def finish_label(ob, uvs, mat, thickness=LABEL_T, outward_check=None):
    uvl = ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uvl.data[li].uv = uvs[vi]
    recalc_normals(ob)
    if outward_check and outward_check(ob): recalc_normals(ob, inside=True)
    paper_shell(ob, mat, thickness)

def build_wrap(C):
    s_vals = sorted(set([round(-122.5 + 0.5 * i, 3) for i in range(491)] + [-S1_E, -HF_E, HF_E, S1_E]))
    v_vals = [round(-12.5 + 0.5 * j, 3) for j in range(187)]
    verts, uvs, faces = clipped_grid(
        s_vals, v_vals,
        lambda u, v: poly_sdf(dev_xy(u, v), TRIM),
        lambda u, v: surf_xyz(u, v, LABEL_GAP),
        lambda u, v: ((dev_xy(u, v)[0] - WRAP_ART['x']) / WRAP_ART['w'], 1 - (dev_xy(u, v)[1] - WRAP_ART['y']) / WRAP_ART['h']))
    ob = mesh_from('LBL-FRONT-01_Wrap', verts, faces, C)
    mat = mat_label('M_LBL-FRONT-01_SUB-01_Paper', 'COLOR__LBL-FRONT-01_v005.png', 'MASK-FOIL-01__LBL-FRONT-01.png',
                    (WRAP_ART['w'], WRAP_ART['h']), 'HEIGHT-EMB-01__LBL-FRONT-01.exr', 'MASK-UV-01__LBL-FRONT-01.png')
    def facing_in(o):
        ps = [p for p in o.data.polygons if abs(p.center.x) < 0.01]
        return bool(ps) and sum(p.normal.y for p in ps) > 0
    finish_label(ob, uvs, mat, outward_check=facing_in)
    # v003: adaptive dicing for true emboss; SIMPLE keeps the die line exact. Render only.
    sub = ob.modifiers.new('emboss_dice', 'SUBSURF'); sub.subdivision_type = 'SIMPLE'
    sub.levels = 0; sub.render_levels = 1
    sub.use_adaptive_subdivision = True; sub.adaptive_space = 'PIXEL'; sub.adaptive_pixel_size = 1.0
    return ob

# --- collar --------------------------------------------------------------------
def capsule_outer_max(z0, z1):
    """Largest capsule outer radius (film included) over a height band, so labels sit on, not in, the film."""
    return max(capsule_r(2 * math.pi * i / N_RING, z0 + (z1 - z0) * k / 40)
               for i in range(N_RING) for k in range(41)) + 0.05

def build_collar(C):
    # v005 fix: v004 used a fixed 17.25 mm, under the pleated film (17.32-17.56 mm)
    rc = capsule_outer_max(COLLAR_BOT, COLLAR_TOP) + LABEL_GAP
    L = 2 * COLLAR_F + COLLAR_C
    def uv(s, z):
        return ((COLLAR_BLEED + s) / COLLAR_ART_W, 1 - (COLLAR_BLEED + (COLLAR_TOP - z)) / COLLAR_ART_H)
    verts, faces, uvs = [], [], []
    zs = [COLLAR_BOT + (COLLAR_TOP - COLLAR_BOT) * k / 8 for k in range(9)]
    # cylinder: s from F (root, +X) counter-clockwise to F+C
    nseg = 160
    for z in zs:
        for i in range(nseg + 1):
            s = COLLAR_F + COLLAR_C * i / nseg; phi = 2 * math.pi * i / nseg
            verts.append((rc * math.cos(phi) * MM, rc * math.sin(phi) * MM, z * MM)); uvs.append(uv(s, z))
    for j in range(len(zs) - 1):
        for i in range(nseg):
            a = j * (nseg + 1) + i; b = a + nseg + 1
            faces.append((a, a + 1, b + 1, b))
    # flag plies (radial, at +X), clipped to the stadium-shaped die (full-radius ends)
    L, Rr, zm = 2 * COLLAR_F + COLLAR_C, (COLLAR_TOP - COLLAR_BOT) / 2, (COLLAR_TOP + COLLAR_BOT) / 2
    def stadium_sdf(sv, z):
        x = min(max(sv, Rr), L - Rr)
        return math.hypot(sv - x, z - zm) - Rr
    zs_f = [COLLAR_BOT + (COLLAR_TOP - COLLAR_BOT) * k / 28 for k in range(29)]
    ds = [COLLAR_F * k / 48 for k in range(49)]
    # v005: plies glued back to back (0.01 mm), with a slight paper-memory curl of 0.6 mm at the tip
    curl = lambda d: -0.6 * (d / COLLAR_F) ** 2
    for ply, yoff, sfun in (('front', -0.01, lambda d: COLLAR_F + COLLAR_C + d), ('back', 0.01, lambda d: COLLAR_F - d)):
        fv, fu, ff = clipped_grid(ds, zs_f, lambda d, z: stadium_sdf(sfun(d), z),
                                  lambda d, z: ((rc + d) * MM, (yoff + curl(d)) * MM, z * MM), lambda d, z: uv(sfun(d), z))
        base = len(verts); verts += fv; uvs += fu
        # v005: each ply faces outward, so its solidify shell (printed face) grows away from the other ply.
        # (v004's inward faces were hidden because both shells shared one material; with the printed/reverse
        # split the back ply's art showed through the front ply mirrored.)
        for f in ff: faces.append(tuple(base + i for i in (reversed(f) if ply == 'back' else f)))
    ob = mesh_from('LBL-NECK-01_Collar', verts, faces, C)
    mat = mat_label('M_LBL-NECK-01_SUB-01_Paper', 'COLOR__LBL-NECK-01.png', 'MASK-FOIL-01__LBL-NECK-01.png', (COLLAR_ART_W, COLLAR_ART_H))
    uvl = ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uvl.data[li].uv = uvs[vi]
    paper_shell(ob, mat)
    return ob

# --- roundel ------------------------------------------------------------------
def build_roundel(C):
    # v004: concentric disc that conforms to the tapered face, with 0.05 mm film thickness
    def pos(x, z): return ((ROUNDEL_X + x) * MM, (-(width_at(ROUNDEL_Z + z) / 2) - 0.12) * MM, (ROUNDEL_Z + z) * MM)
    verts, uvs = [pos(0, 0)], [(0.5, 0.5)]; faces = []
    n, rings = 128, 24
    for j in range(1, rings + 1):
        rr = ROUNDEL_FILM_R * j / rings
        for i in range(n):
            a = 2 * math.pi * i / n; x, z = rr * math.cos(a), rr * math.sin(a)
            verts.append(pos(x, z)); uvs.append((0.5 + x / ROUNDEL_TEX, 0.5 + z / ROUNDEL_TEX))
    faces += [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    for j in range(rings - 1):
        a0, b0 = 1 + j * n, 1 + (j + 1) * n
        for i in range(n):
            k = (i + 1) % n
            faces.append((a0 + i, b0 + i, b0 + k, a0 + k))
    ob = mesh_from('LBL-ROUNDEL-01_Roundel', verts, faces, C)
    uvl = ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uvl.data[li].uv = uvs[vi]
    recalc_normals(ob)
    if ob.data.polygons[0].normal.y > 0: recalc_normals(ob, inside=True)
    ob.data.materials.append(mat_roundel())
    sol = ob.modifiers.new('film', 'SOLIDIFY'); sol.thickness = 0.05 * MM; sol.offset = 1.0; sol.use_rim = True
    shade_smooth(ob, 30)
    sub = ob.modifiers.new('relief_dice', 'SUBSURF'); sub.subdivision_type = 'SIMPLE'; sub.levels = 0; sub.render_levels = 1
    sub.use_adaptive_subdivision = True; sub.adaptive_space = 'PIXEL'; sub.adaptive_pixel_size = 1.0
    return ob

# --- studio -----------------------------------------------------------------
def look_at(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()

def area_light(C, name, loc, size, power, target, shape='RECTANGLE', size_y=None):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = shape; ld.size = size; ld.energy = power
    if size_y: ld.size_y = size_y
    ob = bpy.data.objects.new(name, ld); C.objects.link(ob); ob.location = loc; look_at(ob, target)
    return ob

def soft_card(C, name, loc, w, h, strength, target, colour=(1, 1, 1, 1), black=False):
    """Plane with a soft elliptical falloff, seen only in reflections/refractions."""
    hw, hh = w / 2, h / 2
    ob = mesh_from(name, [(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)], [(0, 1, 2, 3)], C)
    ob.location = loc; look_at(ob, target)
    ob.visible_camera = False
    ob.visible_diffuse = False
    if black:
        m = mat_simple('M_ENV_Flag_Black', **{'Base Color': (0.003, 0.003, 0.003, 1), 'Roughness': 0.9})
        ob.data.materials.append(m); return ob
    ob.visible_shadow = False
    m, nt, out = node_mat('M_' + name)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / hw, 1 / hh, 1)
    gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 0.55
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = colour
    mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = strength
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs[0], gr.inputs['Vector'])
    nt.links.new(gr.outputs['Fac'], pw.inputs[0]); nt.links.new(pw.outputs[0], mu.inputs[0])
    nt.links.new(mu.outputs[0], em.inputs['Strength']); nt.links.new(em.outputs[0], out.inputs['Surface'])
    ob.data.materials.append(m)
    return ob

def foil_card(C, name, w, h, strength, receivers):
    """v005 (studies A, D): narrow gradient strip that the foil mirrors. Bright band over the top of the
    letters, smooth fall-off to black below, soft ends; everything else the foil sees is the dark world,
    so off-angle foil and emboss shoulders go deep. Light-linked to the labels only."""
    hw, hh = w / 2, h / 2
    ob = mesh_from(name, [(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)], [(0, 1, 2, 3)], C)
    ob.visible_camera = False; ob.visible_diffuse = False; ob.visible_shadow = False
    m, nt, out = node_mat('M_' + name)
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs[0])
    fy = map_range(nt, sep.outputs['Y'], -0.4 * hh, 0.1 * hh, 'SMOOTHERSTEP')           # fall-off below the band
    ax = math_node(nt, 'ABSOLUTE', sep.outputs['X'])
    fx = math_node(nt, 'SUBTRACT', 1.0, map_range(nt, ax, 0.6 * hw, hw, 'SMOOTHSTEP'))   # soft ends
    em = nt.nodes.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (1.0, 0.98, 0.95, 1)
    s = math_node(nt, 'MULTIPLY', math_node(nt, 'MULTIPLY', fy, fx), strength); s.node.name = 'STRENGTH'
    nt.links.new(s, em.inputs['Strength'])
    nt.links.new(em.outputs[0], out.inputs['Surface']); ob.data.materials.append(m)
    ob['base_strength'] = strength
    try: ob.light_linking.receiver_collection = receivers
    except Exception as e: print('AVANTE_WARN light linking unavailable:', e)
    return ob

def aim_studio(cam=None):
    """Point the camera-dependent cards at the active camera:
    - CRD_Brandy_Back stays directly behind the bottle (constraint);
    - CRD_Foil_Strip sits where the foil mirrors the camera: card = p + 2(n.v)n - v, v = camera - p,
      with p on the front face at the camera's 'foil_aim_z' and n the face normal, which tilts down
      by the bottle taper (about 4 deg at the wordmark; a flat -Y mirror missed the strip)."""
    sc = bpy.context.scene
    cam = cam or sc.camera
    bpy.data.objects['RIG_BackCard'].constraints[0].target = cam
    sc.camera = cam
    def place(card, pz):
        pz /= MM
        p = Vector((0.0, -width_at(pz) / 2 * MM, pz * MM))
        dw = (width_at(pz + 0.5) - width_at(pz - 0.5)) / 2  # half-width change per mm
        n = Vector((0.0, -1.0, -dw)).normalized()
        v = cam.matrix_world.translation - p
        r = 2 * n.dot(v) * n - v
        if r.z < 0 and p.z + r.z < 0.02:  # mirror points into the floor: card stands on the table instead
            r *= (0.02 - p.z) / r.z
        card.location = p + r; look_at(card, p)
    card, card2 = bpy.data.objects.get('CRD_Foil_Strip'), bpy.data.objects.get('CRD_Foil_Strip_Roundel')
    if card:
        aim = cam.get('foil_aim_z', 0.137)
        place(card, aim)
        # per-camera strip level: the roundel shots clipped the foil to near-white at the full level
        card.active_material.node_tree.nodes['STRENGTH'].inputs[1].default_value = card['base_strength'] * cam.get('foil_strength', 1.0)
        if card2:  # second strip for the roundel in wide shots; off when the camera is about the roundel
            place(card2, ROUNDEL_Z * MM); card2.hide_render = abs(aim - ROUNDEL_Z * MM) < 0.01
        bpy.context.view_layer.update()

aim_back_card = aim_studio  # v004 name, kept for scripts

def build_studio(C):
    sc = bpy.context.scene
    # sweep backdrop + floor
    bm = bmesh.new()
    prof = [(-0.6, 0.0)] + [(0.25 + 0.25 * math.sin(math.radians(a)), 0.25 - 0.25 * math.cos(math.radians(a))) for a in range(0, 91, 5)] + [(0.5, 1.2)]
    w = 1.6
    rows = []
    for (yy, zz) in prof:
        rows.append([bm.verts.new((x, yy, zz)) for x in (-w / 2, w / 2)])
    for a, b in zip(rows, rows[1:]): bm.faces.new((a[0], a[1], b[1], b[0]))
    me = bpy.data.meshes.new('ENV_Sweep'); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('ENV_Sweep', me); C.objects.link(ob)
    m, nt, out = node_mat('M_ENV_Sweep')
    p = principled(nt, **{'Base Color': (0.016, 0.0155, 0.015, 1), 'Roughness': 0.62, 'Specular IOR Level': 0.3})  # v003: matte charcoal, no mirrored light sheets behind the liquid
    nt.links.new(p.outputs[0], out.inputs['Surface']); ob.data.materials.append(m)
    for pl in me.polygons: pl.use_smooth = True
    # world
    wd = sc.world or bpy.data.worlds.new('World'); sc.world = wd; wd.use_nodes = True
    bg = wd.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.003, 0.003, 0.0033, 1); bg.inputs[1].default_value = 1.0  # v005: near-black, so foil off-angle goes deep
    tgt = (0, 0, 0.12)
    # v003 product-photography rig
    area_light(C, 'LGT_Key_Softbox', (-0.72, -0.42, 0.42), 0.9, 10.5, tgt, size_y=1.2)   # large, off-axis: keeps the matte label from washing out
    area_light(C, 'LGT_Rim_L_Strip', (-0.30, 0.08, 0.13), 0.05, 3.2, tgt, size_y=0.8)   # glass edge lines
    area_light(C, 'LGT_Rim_R_Strip', (0.30, 0.08, 0.13), 0.05, 3.2, tgt, size_y=0.8)
    area_light(C, 'LGT_Top', (0.05, -0.05, 0.65), 0.6, 0.45, tgt, size_y=0.6)        # v005 fix: square, as intended
    area_light(C, 'LGT_Fill_Low', (0.55, -0.55, 0.08), 0.5, 0.5, tgt, size_y=0.5)
    # black flags: hold dark glass edges in reflection (not seen directly). Shadow visibility stays off:
    # a v005 test with shadows on threw a hard curved shadow edge across the backdrop in the 3/4 view
    for nm, x in (('FLG_Black_L', -0.16), ('FLG_Black_R', 0.16)):
        fl = soft_card(C, nm, (x, 0.27, 0.25), 0.38, 0.6, None, (0, 0.27, 0.25), black=True)
        fl.rotation_euler = (math.pi / 2, 0, math.pi / 2); fl.visible_shadow = False
    # cards keep to reflections and refractions only, so they never appear in frame
    rig = bpy.data.objects.new('RIG_BackCard', None); C.objects.link(rig)
    # v005: larger than the liquid seen through the flat faces, so its soft edge never lands in the
    # liquid (the v004 tonal step); weaker and less orange (the peachy top)
    back = soft_card(C, 'CRD_Brandy_Back', (0, 0.085, 0.095), 0.17, 0.24, 1.25, (0, -1, 0.095), colour=(1.0, 0.95, 0.88, 1))
    back.parent = rig   # always behind the bottle from the active camera (see aim_studio)
    tc = rig.constraints.new('LOCKED_TRACK'); tc.track_axis = 'TRACK_NEGATIVE_Y'; tc.lock_axis = 'LOCK_Z'
    # v005: CRD_Foil_Specular (1.1 x 0.42 m, flat, everywhere in the foil's mirror) is replaced by a
    # narrow gradient strip placed in the mirror direction of the active camera (aim_studio)
    foil_card(C, 'CRD_Foil_Strip', 0.30, 0.08, 9.0, bpy.data.collections['GEO_Labels'])
    # roundel strip: small and dimmer (it stands close, on the table) and linked to the roundel only, so it
    # neither washes the roundel's navy ink nor glints in the wrap's spot-UV varnish
    lnk = bpy.data.collections.get('LNK_Roundel') or bpy.data.collections.new('LNK_Roundel')
    lnk.objects.link(bpy.data.objects['LBL-ROUNDEL-01_Roundel'])
    foil_card(C, 'CRD_Foil_Strip_Roundel', 0.12, 0.04, 6.0, lnk)
    # cameras (macros: 2000x1600; focus distance measured to the label face). foil_aim_z = foil height
    # the camera is about. v005 angled cameras (study D): long lens, turned off square, rolled.
    for name, loc, lens, tgt2, focus, fstop, aimz, roll in (
            ('CAM_Hero', (0.0, -0.74, 0.13), 85, (0, 0, 0.119), None, None, 0.137, 0),
            ('CAM_ThreeQuarter', (0.42, -0.6, 0.16), 85, (0, 0, 0.119), None, None, 0.137, 0),
            ('CAM_Macro_Avante', (0.0, -0.28, 0.137), 100, (0, 0, 0.137), 0.235, 16, 0.137, 0),
            ('CAM_Macro_Roundel', (0.0, -0.28, 0.0422), 100, (0, 0, 0.0422), 0.242, 8, 0.0422, 0),
            ('CAM_Macro_CollarFlag', (0.06, -0.2, 0.216), 100, (0.027, 0, 0.2075), 0.205, 11, 0.2075, 0),
            ('CAM_Angle_Avante', None, 135, (0.0, -0.045, 0.139), 0.30, 16, 0.139, 25),
            ('CAM_Angle_Roundel', None, 135, (0.0, -0.038, 0.0422), 0.30, 11, 0.0422, -20),
            ('CAM_Angle_CollarFlag', None, 100, (0.03, 0.0, 0.2075), 0.26, 11, 0.2075, 15),
            # v007 review cameras level with the shoulder (the hero at z 130 looks up and makes it read lower)
            ('CAM_Shoulder', (0.0, -0.49, 0.155), 135, (0, 0, 0.155), None, None, 0.137, 0),
            ('CAM_Shoulder_34', (0.258, -0.369, 0.155), 135, (0, 0, 0.155), None, None, 0.137, 0)):
        cd = bpy.data.cameras.new(name); cd.lens = lens
        if focus:
            cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop; cd.dof.focus_distance = focus
        if loc is None:  # angled: yaw/elevation per shot, at the focus distance from the subject
            yaw, el = {'CAM_Angle_Avante': (20, 8), 'CAM_Angle_Roundel': (-18, 6), 'CAM_Angle_CollarFlag': (28, 16)}[name]
            y, e = math.radians(yaw), math.radians(el)
            loc = tuple(t + focus * d for t, d in zip(tgt2, (math.sin(y) * math.cos(e), -math.cos(y) * math.cos(e), math.sin(e))))
        co = bpy.data.objects.new(name, cd); C.objects.link(co); co.location = loc; look_at(co, tgt2)
        co['foil_aim_z'] = aimz
        if 'Roundel' in name: co['foil_strength'] = 0.5
        if roll:
            co.rotation_euler = (co.rotation_euler.to_quaternion() @ Quaternion((0, 0, 1), math.radians(roll))).to_euler()
    # turntable: 120 frames, one linear orbit
    tt = bpy.data.objects.new('RIG_Turntable', None); C.objects.link(tt); tt.location = (0, 0, 0.119)
    cd = bpy.data.cameras.new('CAM_Turntable'); cd.lens = 85
    co = bpy.data.objects.new('CAM_Turntable', cd); C.objects.link(co); co.parent = tt; co['foil_aim_z'] = 0.137
    co.location = (0, -0.8, 0.03); look_at(co, (0, 0, 0))
    tt.rotation_euler = (0, 0, 0); tt.keyframe_insert('rotation_euler', index=2, frame=1)
    tt.rotation_euler = (0, 0, 2 * math.pi); tt.keyframe_insert('rotation_euler', index=2, frame=121)
    ad = tt.animation_data
    for fc in ad.action.layers[0].strips[0].channelbag(ad.action_slot).fcurves:
        for kp in fc.keyframe_points: kp.interpolation = 'LINEAR'
    sc.frame_start, sc.frame_end = 1, 120
    sc.frame_set(1)
    aim_back_card(bpy.data.objects['CAM_Hero'])

def render_settings(samples=128, res=(1000, 1600)):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = samples; sc.cycles.use_denoising = True; sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    sc.cycles.max_bounces = 32; sc.cycles.transmission_bounces = 24; sc.cycles.glossy_bounces = 12
    sc.cycles.transparent_max_bounces = 24; sc.cycles.volume_bounces = 4
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 0.0; sc.cycles.adaptive_threshold = 0.005; sc.cycles.sample_clamp_indirect = 10.0  # v005: no glossy blur on mirror foil
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.unit_settings.system = 'METRIC'; sc.unit_settings.length_unit = 'MILLIMETERS'
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'None'  # v004: no look hue shift on amber and navy
    except Exception: pass

if GLASS_MODEL == 'v007':  # replaces glass, liquid, outer_r, inner_volume and the wrap mapping (see glass_v007.py)
    try: sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    except NameError: pass
    import glass_v007
    GLASS_V007_INFO = glass_v007.install(sys.modules[__name__])

def main():
    clear_scene()
    global BASE_T
    _CAP_TABLE.clear()
    BASE_T = base_t = solve_base_thickness()
    G, L, K, S = coll('GEO_Glass_Liquid'), coll('GEO_Labels'), coll('GEO_Capsule'), coll('LGT_CAM_ENV')
    glass = build_glass(G, base_t); glass.data.materials.append(mat_glass())
    liq = build_liquid(G, base_t); liq.data.materials.append(mat_brandy())
    build_capsule(K); build_collar(L); build_wrap(L); build_roundel(L)
    build_studio(S); render_settings()
    report = {
        'base_thickness_mm': round(base_t, 2),
        'inner_volume_to_fill_ml': round(inner_volume(base_t, FILL_Z), 1),
        'brimful_ml': round(inner_volume(base_t, GLASS_H), 1),
        'glass_height_mm': GLASS_H, 'overall_with_capsule_mm': CAP_TOP,
        'max_width_mm': max(w for _, w in PROFILE),
    }
    print('AVANTE_REPORT', report)
    return report

if __name__ == '__main__':
    rep = main()
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    if '--save' in argv:
        bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(argv[argv.index('--save') + 1]))
    if '--render' in argv:
        out = os.path.abspath(argv[argv.index('--render') + 1])
        if '--camera' in argv: aim_back_card(bpy.data.objects[argv[argv.index('--camera') + 1]])
        if '--gpu' in argv:
            cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = 'METAL'; cp.get_devices()
            for d in cp.devices: d.use = True
            bpy.context.scene.cycles.device = 'GPU'
        if '--samples' in argv: bpy.context.scene.cycles.samples = int(argv[argv.index('--samples') + 1])
        if '--res' in argv:
            w, h = argv[argv.index('--res') + 1].split('x'); bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = int(w), int(h)
        bpy.context.scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print('AVANTE_RENDER', out)
