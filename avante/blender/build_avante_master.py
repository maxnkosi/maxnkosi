"""
Avante Brandy — master scene builder (avante_master_v001)
==========================================================

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
from mathutils import Vector

MM = 0.001  # mm → metres

# ---------------------------------------------------------------- data
# Outer width (flat-to-flat for the square body, diameter for the round neck)
# vs height above base, glass only — from the user's cap-off photo scaled to
# the supplier height 226.9 mm (V). ±0.7 mm.
PROFILE = [(0, 55.6), (1, 60.0), (2, 62.2), (3.5, 63.8), (5, 64.9), (7.5, 68.5), (10, 71.6),
           (20, 73.0), (40, 75.6), (60, 77.0), (80, 79.6), (100, 83.0), (120, 85.0), (140, 87.7),
           (145, 89.0), (150, 89.0), (152.5, 88.9), (155, 88.4), (157.5, 85.5), (160, 80.3),
           (162.5, 74.0), (165, 67.6), (167.5, 60.8), (170, 54.2), (172.5, 48.5), (175, 43.5),
           (177.5, 39.8), (180, 36.8), (182.5, 35.8), (185, 35.0), (188, 34.3), (190, 34.1),
           (215, 34.1), (216.5, 36.5), (218, 40.5), (220, 41.5), (223, 41.0), (224.5, 40.0),
           (225.7, 38.0), (226.5, 35.0), (226.9, 32.5)]
GLASS_H = 226.9          # V supplier
FILL_Z = GLASS_H - 66.0  # V supplier fill height (66 mm below glass top)
FILL_ML = 750.0          # V
CAP_TOP = 238.1          # P (glass + ≈11.2 mm bar-top)
WALL = 4.5               # P side wall
BORE = 26.0              # P neck bore
CHAMFER = 0.0754         # P chamfer leg / side (W2124 ratio)
N_RING = 256
EDGE_SOFT = 0.5          # P vertical-edge softening (mm)
LABEL_T = 0.10           # P paper thickness SUB-01 (mm)

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

def width_at(z):
    if z <= PROFILE[0][0]: return PROFILE[0][1]
    for (z0, w0), (z1, w1) in zip(PROFILE, PROFILE[1:]):
        if z <= z1: return lerp(w0, w1, (z - z0) / (z1 - z0))
    return PROFILE[-1][1]

def roundness(z):  # 0 = chamfered square body, 1 = round neck
    t = min(max((z - 150.0) / 32.0, 0.0), 1.0)
    return t * t * (3 - 2 * t)

def sq_radius(theta, S):
    h, a = S / 2, CHAMFER * S
    c, s = abs(math.cos(theta)), abs(math.sin(theta))
    r1 = h / max(c, s)
    r2 = (S - a) / (c + s)
    k = EDGE_SOFT  # soft-min ≈ R1–2 mm fillets on the chamfer edges (P)
    return -k * math.log(math.exp(-r1 / k) + math.exp(-r2 / k))

def section_r(theta, S, t):
    return (1 - t) * sq_radius(theta, S) + t * S / 2

def ring(z, S, t, n=N_RING, off=0.0):
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        r = section_r(th, S, t) + off
        pts.append(((r * math.cos(th)) * MM, (r * math.sin(th)) * MM, z * MM))
    return pts

def section_area(S, t, n=360):
    a = 0.0
    for i in range(n):
        th0, th1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        r0, r1 = section_r(th0, S, t), section_r(th1, S, t)
        a += 0.5 * r0 * r1 * math.sin(th1 - th0)
    return a  # mm²

def inner_width(z):
    if z >= 185: return BORE
    return max(width_at(z) - 2 * WALL, BORE)

def inner_volume(z0, z1, dz=0.25):
    v, z = 0.0, z0
    while z < z1:
        zz = min(z + dz, z1)
        zm = (z + zz) / 2
        v += section_area(inner_width(zm), roundness(zm)) * (zz - z)
        z = zz
    return v / 1000.0  # ml

def solve_base_thickness():
    lo, hi = 2.0, 60.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if inner_volume(mid, FILL_Z) > FILL_ML: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def z_samples(z0, z1):
    zs = sorted(set([round(z, 3) for z in
        [z0, z1] + [p[0] for p in PROFILE if z0 < p[0] < z1] +
        [z0 + i * 1.0 for i in range(int(z1 - z0) + 1) if z0 + i < z1]]))
    return zs

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
FOIL_F0 = (0.95, 0.68, 0.30, 1.0)  # FOIL-01 warm pale gold reflectance (P, match to foil swatch)

def mat_glass():
    m, nt, out = node_mat('M_GLS-01_Flint')
    p = principled(nt, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0, 'IOR': 1.52, 'Transmission Weight': 1.0})
    vol = nt.nodes.new('ShaderNodeVolumeAbsorption')
    vol.inputs['Color'].default_value = (0.93, 0.98, 0.95, 1); vol.inputs['Density'].default_value = 1.5
    nt.links.new(p.outputs[0], out.inputs['Surface']); nt.links.new(vol.outputs[0], out.inputs['Volume'])
    return m

def mat_brandy():
    m, nt, out = node_mat('M_LIQ-01_Brandy')
    p = principled(nt, **{'Base Color': (1, 1, 1, 1), 'Roughness': 0.0, 'IOR': 1.36, 'Transmission Weight': 1.0})
    vol = nt.nodes.new('ShaderNodeVolumeAbsorption')
    vol.inputs['Color'].default_value = (0.9, 0.7, 0.2, 1)  # P — target transmittance ≈(0.57,0.19,0.01) over 80 mm; calibrate to reference photography
    vol.inputs['Density'].default_value = 95.0                   # per metre
    nt.links.new(p.outputs[0], out.inputs['Surface']); nt.links.new(vol.outputs[0], out.inputs['Volume'])
    return m

def mat_label(name, color, alpha, foil, emb=None, uv=None):
    """SUB-01 paper + INK (colour texture) + FOIL-01 + EMB-01 + UV-01 + VAR-01, alpha = die."""
    m, nt, out = node_mat(name)
    T = tex_dir()
    c = img(nt, os.path.join(T, color), loc=(-900, 300))
    a = img(nt, os.path.join(T, alpha), True, loc=(-900, 0)) if alpha else None
    f = img(nt, os.path.join(T, foil), True, loc=(-900, -300))
    paper = principled(nt, **{'Roughness': 0.68, 'Sheen Weight': 0.25})   # VAR-01 matte over SUB-01
    nt.links.new(c.outputs['Color'], paper.inputs['Base Color'])
    foilb = principled(nt, **{'Base Color': FOIL_F0, 'Metallic': 1.0, 'Roughness': 0.18, 'Anisotropic': 0.3})
    mix = nt.nodes.new('ShaderNodeMixShader'); mix.location = (400, 0)
    nt.links.new(f.outputs['Color'], mix.inputs['Fac'])
    nt.links.new(paper.outputs[0], mix.inputs[1]); nt.links.new(foilb.outputs[0], mix.inputs[2])
    if uv:
        u = img(nt, os.path.join(T, uv), True, loc=(-900, -600))
        nt.links.new(u.outputs['Color'], paper.inputs['Coat Weight'])
        paper.inputs['Coat Roughness'].default_value = 0.04
    if emb:
        e = img(nt, os.path.join(T, emb), True, loc=(-900, -900))
        bump = nt.nodes.new('ShaderNodeBump'); bump.location = (-300, -700)
        bump.inputs['Strength'].default_value = 0.6; bump.inputs['Distance'].default_value = 0.2 * MM  # EMB-01 ≈0.2 mm (P)
        nt.links.new(e.outputs['Color'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], paper.inputs['Normal']); nt.links.new(bump.outputs['Normal'], foilb.inputs['Normal'])
    if a is None:
        nt.links.new(mix.outputs[0], out.inputs['Surface']); return m
    transp = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix2 = nt.nodes.new('ShaderNodeMixShader'); mix2.location = (600, 0)
    nt.links.new(a.outputs['Color'], mix2.inputs['Fac'])
    nt.links.new(transp.outputs[0], mix2.inputs[1]); nt.links.new(mix.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs['Surface'])
    return m

def mat_roundel():
    m, nt, out = node_mat('M_LBL-ROUNDEL-01_ClearFilm')
    T = tex_dir()
    c = img(nt, os.path.join(T, 'COLOR__LBL-ROUNDEL-01.png'), loc=(-900, 300))
    f = img(nt, os.path.join(T, 'MASK-FOIL-01__LBL-ROUNDEL-01.png'), True, loc=(-900, -100))
    ink = principled(nt, **{'Roughness': 0.45})
    nt.links.new(c.outputs['Color'], ink.inputs['Base Color'])
    foilb = principled(nt, **{'Base Color': FOIL_F0, 'Metallic': 1.0, 'Roughness': 0.18})
    mix = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(f.outputs['Color'], mix.inputs['Fac'])
    nt.links.new(ink.outputs[0], mix.inputs[1]); nt.links.new(foilb.outputs[0], mix.inputs[2])
    film = principled(nt, **{'Roughness': 0.04, 'IOR': 1.49, 'Transmission Weight': 1.0})  # SUB-02 clear film
    # print mask from UV distance (printed disc Ø43.71 inside the Ø46.71 film die)
    uvn = nt.nodes.new('ShaderNodeTexCoord')
    sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0)
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = ROUNDEL_PRINT_R / ROUNDEL_TEX
    nt.links.new(uvn.outputs['UV'], sub.inputs[0]); nt.links.new(sub.outputs[0], ln.inputs[0]); nt.links.new(ln.outputs['Value'], lt.inputs[0])
    mix2 = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lt.outputs[0], mix2.inputs['Fac']); nt.links.new(film.outputs[0], mix2.inputs[1]); nt.links.new(mix.outputs[0], mix2.inputs[2])
    nt.links.new(mix2.outputs[0], out.inputs['Surface'])
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
    zs = z_samples(0.0, GLASS_H)
    outer = [ring(z, width_at(z), roundness(z)) for z in zs]
    zi = [z for z in z_samples(base_t, GLASS_H)]
    inner = [ring(z, inner_width(z), roundness(z)) for z in reversed(zi)]
    verts, faces = loft(outer + inner, close_bottom=(0, 0, 1.2 * MM), close_top=(0, 0, base_t * MM))
    ob = mesh_from('GLS-01_Glass', verts, faces, C)
    recalc_normals(ob); shade_smooth(ob, 40)
    return ob

def build_liquid(C, base_t):
    zs = z_samples(base_t + 0.05, FILL_Z)
    rings = [ring(z, inner_width(z) - 0.1, roundness(z)) for z in zs]
    # meniscus: liquid climbs ≈1.3 mm up the glass wall (P), falls to flat within ≈3.5 mm
    Wf, tf = inner_width(FILL_Z) - 0.1, roundness(FILL_Z)
    for dd, hh in ((0.0, 1.3), (0.15, 0.95), (0.4, 0.62), (0.8, 0.36), (1.4, 0.17), (2.3, 0.06), (3.5, 0.0)):
        rings.append(ring(FILL_Z + hh, Wf - 2 * dd, tf))
    verts, faces = loft(rings, close_bottom=(0, 0, (base_t + 0.05) * MM), close_top=(0, 0, FILL_Z * MM))
    ob = mesh_from('LIQ-01_Brandy', verts, faces, C)
    recalc_normals(ob); shade_smooth(ob, 40)
    return ob

def capsule_r(theta, z):
    r_glass = section_r(theta, width_at(min(z, GLASS_H)), roundness(z)) if z <= GLASS_H else 0
    r_clos = 20.9 if z >= CAP_TOP - 14.8 else (17.8 if z >= CAP_TOP - 23.0 else 0)  # P bar-top head/band
    r = max(r_glass, r_clos) + 0.06
    if z > CAP_TOP - 2.0:  # 2 mm top fillet
        dz = z - (CAP_TOP - 2.0)
        r -= 2.0 - math.sqrt(max(4.0 - dz * dz, 0.0))
    return r

def build_capsule(C):
    zs = sorted(set([CAPSULE_BOTTOM, PINLINE_TOP] + [z for z in z_samples(CAPSULE_BOTTOM, CAP_TOP)] +
                    [CAP_TOP - 2.0 + 2.0 * math.sin(math.radians(a)) for a in range(0, 91, 10)]))
    rings = []
    for z in zs:
        rings.append([((capsule_r(th, z)) * math.cos(th) * MM, (capsule_r(th, z)) * math.sin(th) * MM, z * MM)
                      for th in [2 * math.pi * i / N_RING for i in range(N_RING)]])
    verts, faces = loft(rings, close_top=(0, 0, CAP_TOP * MM))
    ob = mesh_from('SLV-CAP-01_Capsule', verts, faces, C)
    recalc_normals(ob)
    navy = mat_simple('M_SUB-03_ShrinkFilm_INK-01-S', **{'Base Color': NAVY, 'Roughness': 0.14, 'Coat Weight': 0.6, 'Coat Roughness': 0.08})
    gold = mat_simple('M_MET-01_GoldInk', **{'Base Color': GOLD, 'Metallic': 0.85, 'Roughness': 0.35})
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
        q = (DEV_R - v) / DEV_R if v >= 0 else 1.0
        return (sE * q, v if v < 0 else V(0, v)[1])
    if s <= S1_E:
        u = (s - HF_E) / (S1_E - HF_E); a, b = V(HF_E, v), V(S1_E, v)
    else:
        u = (s - S1_E) / (S2_E - S1_E); a, b = V(S1_E, v), V(S2_E, v)
    return (sgn * lerp(a[0], b[0], u), lerp(a[1], b[1], u))

def surf_xyz(sE, v, off):
    z = Z_EDGE - v if v >= 0 else Z_EDGE + (-v) * math.sin(math.radians(49))
    S = width_at(z); a = CHAMFER * S; h = S / 2; hf3 = h - a
    sgn = 1 if sE >= 0 else -1; s = abs(sE)
    if s <= HF_E:
        x, y = (s / HF_E) * hf3, -h
    elif s <= S1_E:
        u = (s - HF_E) / (S1_E - HF_E); x, y = lerp(hf3, h, u), lerp(-h, -h + a, u)
    else:
        u = (s - S1_E) / (S2_E - S1_E); x, y = h, lerp(-h + a, h - a, u)
    x *= sgn
    th = math.atan2(y, x)
    r = section_r(th, S, roundness(z)) + off
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

def finish_label(ob, uvs, mat, thickness=LABEL_T, outward_check=None):
    uvl = ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uvl.data[li].uv = uvs[vi]
    recalc_normals(ob)
    if outward_check and outward_check(ob): recalc_normals(ob, inside=True)
    ob.data.materials.append(mat)
    sol = ob.modifiers.new('paper', 'SOLIDIFY'); sol.thickness = thickness * MM; sol.offset = 1.0
    sol.use_rim = True; sol.use_even_offset = True
    shade_smooth(ob, 30)

def build_wrap(C):
    s_vals = sorted(set([round(-122.5 + 0.5 * i, 3) for i in range(491)] + [-S1_E, -HF_E, HF_E, S1_E]))
    v_vals = [round(-12.5 + 0.5 * j, 3) for j in range(187)]
    verts, uvs, faces = clipped_grid(
        s_vals, v_vals,
        lambda u, v: poly_sdf(dev_xy(u, v), TRIM),
        lambda u, v: surf_xyz(u, v, 0.03),
        lambda u, v: ((dev_xy(u, v)[0] - WRAP_ART['x']) / WRAP_ART['w'], 1 - (dev_xy(u, v)[1] - WRAP_ART['y']) / WRAP_ART['h']))
    ob = mesh_from('LBL-FRONT-01_Wrap', verts, faces, C)
    mat = mat_label('M_LBL-FRONT-01_SUB-01_Paper', 'COLOR__LBL-FRONT-01.png', None,
                    'MASK-FOIL-01__LBL-FRONT-01.png', 'MASK-EMB-01__LBL-FRONT-01.png', 'MASK-UV-01__LBL-FRONT-01.png')
    def facing_in(o):
        ps = [p for p in o.data.polygons if abs(p.center.x) < 0.01]
        return bool(ps) and sum(p.normal.y for p in ps) > 0
    finish_label(ob, uvs, mat, outward_check=facing_in)
    return ob

# --- collar --------------------------------------------------------------------
def build_collar(C):
    rc = NECK_D / 2 + 0.06 + 0.03
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
    for ply, yoff, sfun in (('front', -0.12, lambda d: COLLAR_F + COLLAR_C + d), ('back', 0.12, lambda d: COLLAR_F - d)):
        fv, fu, ff = clipped_grid(ds, zs_f, lambda d, z: stadium_sdf(sfun(d), z),
                                  lambda d, z: ((rc + d) * MM, yoff * MM, z * MM), lambda d, z: uv(sfun(d), z))
        base = len(verts); verts += fv; uvs += fu
        for f in ff: faces.append(tuple(base + i for i in (f if ply == 'back' else reversed(f))))
    ob = mesh_from('LBL-NECK-01_Collar', verts, faces, C)
    mat = mat_label('M_LBL-NECK-01_SUB-01_Paper', 'COLOR__LBL-NECK-01.png', None, 'MASK-FOIL-01__LBL-NECK-01.png')
    uvl = ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uvl.data[li].uv = uvs[vi]
    ob.data.materials.append(mat)
    sol = ob.modifiers.new('paper', 'SOLIDIFY'); sol.thickness = LABEL_T * MM; sol.offset = 1.0; sol.use_rim = True
    shade_smooth(ob, 30)
    return ob

# --- roundel ------------------------------------------------------------------
def build_roundel(C):
    S = width_at(ROUNDEL_Z); y = -(S / 2) - 0.12
    verts, faces, uvs = [(ROUNDEL_X * MM, y * MM, ROUNDEL_Z * MM)], [], [(0.5, 0.5)]
    n = 128
    for i in range(n):
        a = 2 * math.pi * i / n
        x, z = ROUNDEL_FILM_R * math.cos(a), ROUNDEL_FILM_R * math.sin(a)
        verts.append(((ROUNDEL_X + x) * MM, y * MM, (ROUNDEL_Z + z) * MM))
        uvs.append((0.5 + x / ROUNDEL_TEX, 0.5 + z / ROUNDEL_TEX))
    faces = [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    ob = mesh_from('LBL-ROUNDEL-01_Roundel', verts, faces, C)
    uvl = ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uvl.data[li].uv = uvs[vi]
    recalc_normals(ob)
    if ob.data.polygons[0].normal.y > 0: recalc_normals(ob, inside=True)
    ob.data.materials.append(mat_roundel())
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
    p = principled(nt, **{'Base Color': (0.07, 0.068, 0.066, 1), 'Roughness': 0.25, 'Coat Weight': 0.3})
    nt.links.new(p.outputs[0], out.inputs['Surface']); ob.data.materials.append(m)
    for pl in me.polygons: pl.use_smooth = True
    # world
    wd = sc.world or bpy.data.worlds.new('World'); sc.world = wd; wd.use_nodes = True
    bg = wd.node_tree.nodes.get('Background'); bg.inputs[0].default_value = (0.02, 0.02, 0.022, 1); bg.inputs[1].default_value = 1.0
    tgt = (0, 0, 0.12)
    area_light(C, 'LGT_Key_Softbox', (-0.5, -0.45, 0.4), 0.6, 7, tgt)
    area_light(C, 'LGT_Rim_L_Strip', (-0.32, 0.18, 0.15), 0.06, 6, tgt, size_y=0.7)
    area_light(C, 'LGT_Rim_R_Strip', (0.32, 0.18, 0.15), 0.06, 6, tgt, size_y=0.7)
    area_light(C, 'LGT_Back_Glow', (0.0, 0.35, 0.1), 0.25, 4, (0, 0, 0.09))
    area_light(C, 'LGT_Top', (0.05, -0.05, 0.65), 0.5, 1.2, tgt)
    area_light(C, 'LGT_Foil_Card', (0.10, -0.5, 0.33), 0.30, 2.2, (0, 0, 0.13), size_y=0.06)  # specular card for FOIL-01
    area_light(C, 'LGT_Fill_Low', (0.35, -0.5, 0.05), 0.4, 0.5, tgt)
    # cameras
    for name, loc, lens, tgt2 in (('CAM_Hero', (0.0, -0.74, 0.13), 85, (0, 0, 0.119)),
                                  ('CAM_ThreeQuarter', (0.42, -0.6, 0.16), 85, (0, 0, 0.119)),
                                  ('CAM_Macro_Avante', (0.0, -0.28, 0.137), 100, (0, 0, 0.137))):
        cd = bpy.data.cameras.new(name); cd.lens = lens
        if 'Macro' in name:
            cd.dof.use_dof = True; cd.dof.aperture_fstop = 8; cd.dof.focus_distance = 0.235
        co = bpy.data.objects.new(name, cd); C.objects.link(co); co.location = loc; look_at(co, tgt2)
    sc.camera = bpy.data.objects['CAM_Hero']

def render_settings(samples=128, res=(1000, 1600)):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.samples = samples; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 32; sc.cycles.transmission_bounces = 24; sc.cycles.glossy_bounces = 12
    sc.cycles.transparent_max_bounces = 24; sc.cycles.volume_bounces = 4
    sc.cycles.caustics_reflective = False; sc.cycles.caustics_refractive = False
    sc.cycles.blur_glossy = 0.5
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.unit_settings.system = 'METRIC'; sc.unit_settings.length_unit = 'MILLIMETERS'
    try:
        sc.view_settings.view_transform = 'AgX'
        sc.view_settings.look = 'AgX - Punchy'
    except Exception: pass

def main():
    clear_scene()
    base_t = solve_base_thickness()
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
        if '--camera' in argv: bpy.context.scene.camera = bpy.data.objects[argv[argv.index('--camera') + 1]]
        if '--samples' in argv: bpy.context.scene.cycles.samples = int(argv[argv.index('--samples') + 1])
        if '--res' in argv:
            w, h = argv[argv.index('--res') + 1].split('x'); bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y = int(w), int(h)
        bpy.context.scene.render.filepath = out
        bpy.ops.render.render(write_still=True)
        print('AVANTE_RENDER', out)
