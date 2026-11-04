"""Reference-directed photography for the variants master (v002): 15 independent setups.

Each setup is its own Blender scene PHOTO_<cid>_<ref> that LINKS the concept's assembly (CONCEPT_xx, never
copied) and its own rig collection PHOTO_<cid>_<ref>_RIG (camera, lights, cards, backdrop, props). Rigs are
built per placement from the reference recipe, so adjusting one photograph cannot change another, and the
shared studio (STUDIO_SHARED, CAMERAS, the main scene) is untouched. The rig collections also live under
PHOTOGRAPHY/<cid>/ in the main scene, excluded from its view layer.

Recipes are estimates from the reference images (photography/REFERENCE_BREAKDOWN.md); values refined in the
Pass A/B previews are written back here and stored on each scene as custom properties.

    import photography_v002 as PH; PH.build()          # called by build_variants_master_v002.py
    blender -b avante_variants_master_v002.blend -S PHOTO_C01_R25 --python render_photography.py -- PASS
"""
import bpy, math
from mathutils import Vector, Matrix

MM = 0.001
LIGHT_SCALE = 0.042    # Pass A: recipes were ~25x too bright; v009 studio key = 10.5 W
GLOW_SCALE = 0.20      # v009 brandy back card emission = 1.0

def hexlin(h, a=1.0):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (a,)

BRONZE, CREAM_BG, NAVY_BG, NAVY_BLACK, CHARCOAL, PLINTH = '#4E3B29', '#EFE6D6', '#0E2233', '#0A1520', '#1C1A19', '#1B2B4B'

# placement -> (reference recipe, backdrop colour)
PLACEMENTS = [
    ('C01', 'R25', BRONZE), ('C01', 'R19', NAVY_BG), ('C01', 'R23', CREAM_BG),
    ('C05', 'R25', BRONZE), ('C05', 'R23', CREAM_BG), ('C05', 'R24', CHARCOAL),
    ('C06', 'R25', CREAM_BG), ('C06', 'R20', NAVY_BLACK), ('C06', 'R21', NAVY_BG),
    ('C07', 'R25', BRONZE), ('C07', 'R24', CHARCOAL), ('C07', 'R22', CHARCOAL),
    ('C10', 'R25', NAVY_BG), ('C10', 'R21', NAVY_BG), ('C10', 'R23', CREAM_BG),
]
FIGMA_REF = {'R25': 'image 25 (hash 5ee68e)', 'R23': 'image 23 (473e3c)', 'R19': 'image 19 (eec2b0)', 'R24': 'image 24 (4fede0)',
             'R20': 'image 20 (172ed6)', 'R21': 'image 21 (5c6fd0)', 'R22': 'image 22 (15973c)'}


# ----------------------------------------------------------------- helpers
def look_at(ob, target, roll_deg=0.0):
    d = Vector(target) - ob.location
    q = d.to_track_quat('-Z', 'Y')
    if roll_deg: q = q @ Matrix.Rotation(math.radians(roll_deg), 4, 'Z').to_quaternion()
    ob.rotation_euler = q.to_euler()


def orbit(target, dist, az_deg, el_deg):
    """camera position at distance from target; az 0 = straight in front (-Y), positive = to the right (+X)."""
    a, e = math.radians(az_deg), math.radians(el_deg)
    t = Vector(target)
    return t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist


def mat_diffuse(name, hexcol, rough=0.85):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = hexlin(hexcol)
    b.inputs['Roughness'].default_value = rough
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = 0.25
    return m


def mat_emit(name, rgb, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes): nt.nodes.remove(n)
    e = nt.nodes.new('ShaderNodeEmission'); o = nt.nodes.new('ShaderNodeOutputMaterial')
    e.inputs['Color'].default_value = rgb; e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], o.inputs[0]); return m


def plane(name, coll, size, loc, mat, facing=None, camera_visible=True):
    me = bpy.data.meshes.new(name); w, h = size
    me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob); ob.location = loc
    me.materials.append(mat)
    if facing is not None: look_at_plane(ob, facing)
    ob.visible_camera = camera_visible
    return ob


def look_at_plane(ob, target):
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()


def sweep(name, coll, colour, width=3.0, depth=1.6, back=0.6, height=1.4, radius=0.35, y_front=-1.4):
    """seamless: floor from y_front to the back wall at +back with a rounded roll of the given radius."""
    pts = [(y_front, 0.0)]
    steps = 16
    for i in range(steps + 1):
        a = math.pi / 2 * i / steps
        pts.append((back - radius + math.sin(a) * radius, radius - math.cos(a) * radius))
    pts.append((back, height))
    verts, faces = [], []
    for x in (-width / 2, width / 2):
        for y, z in pts: verts.append((x, y, z))
    n = len(pts)
    for i in range(n - 1): faces.append((i, i + 1, n + i + 1, n + i))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); coll.objects.link(ob)
    me.materials.append(mat_diffuse('M_' + name, colour)); return ob


def area(name, coll, loc, target, size, energy, kelvin=5200, shape='RECTANGLE', spread=180, visible_glossy=True):
    ld = bpy.data.lights.new(name, 'AREA'); ld.shape = shape
    if shape in ('RECTANGLE', 'ELLIPSE'): ld.size, ld.size_y = size
    else: ld.size = size[0]
    ld.energy = energy * LIGHT_SCALE; ld.spread = math.radians(spread)
    ld.use_nodes = False; ld.color = kelvin_rgb(kelvin)
    ob = bpy.data.objects.new(name, ld); coll.objects.link(ob); ob.location = loc; look_at(ob, target)
    ob.visible_glossy = visible_glossy
    return ob


def spot(name, coll, loc, target, energy, angle_deg, radius=0.005, kelvin=5600, blend=0.15):
    ld = bpy.data.lights.new(name, 'SPOT'); ld.energy = energy * LIGHT_SCALE; ld.spot_size = math.radians(angle_deg)
    ld.spot_blend = blend; ld.shadow_soft_size = radius; ld.color = kelvin_rgb(kelvin)
    ob = bpy.data.objects.new(name, ld); coll.objects.link(ob); ob.location = loc; look_at(ob, target)
    return ob


def kelvin_rgb(k):
    """approximate black-body colour (linear), normalised."""
    t = k / 100.0
    r = 255 if t <= 66 else 329.698727446 * ((t - 60) ** -0.1332047592)
    g = 99.4708025861 * math.log(t) - 161.1195681661 if t <= 66 else 288.1221695283 * ((t - 60) ** -0.0755148492)
    b = 255 if t >= 66 else (0 if t <= 19 else 138.5177312231 * math.log(t - 10) - 305.0447927307)
    c = [max(0, min(255, x)) / 255 for x in (r, g, b)]
    c = [(x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    m = max(c); return tuple(x / m for x in c)


def camera(name, coll, loc, target, lens, roll=0.0, fstop=None, focus=None, shift=(0, 0)):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.sensor_fit = 'AUTO'
    cd.shift_x, cd.shift_y = shift
    if fstop:
        cd.dof.use_dof = True; cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus if focus else (Vector(target) - Vector(loc)).length
    ob = bpy.data.objects.new(name, cd); coll.objects.link(ob); ob.location = loc; look_at(ob, target, roll)
    return ob


def back_glow(coll, name, colour='#FF9A3C', strength=6.0, loc=(0, 0.11, 0.08), size=(0.10, 0.12), target=(0, 0, 0.08)):
    """warm card behind the bottle, invisible to the camera: lights the brandy from behind (v009 practice)."""
    return plane(name, coll, size, loc, mat_emit('M_' + name, hexlin(colour), strength * GLOW_SCALE), facing=target, camera_visible=False)


def foil_card(coll, name, cam, z, strength=3.0, size=(0.6, 0.12)):
    """camera-invisible card where the label face mirrors the camera, so hot foil reads gold (v009 practice)."""
    import variants_stage as VS
    ob = plane(name, coll, size, (0, 0, 0), mat_emit('M_' + name, (1.0, 0.92, 0.8, 1), strength), camera_visible=False)
    VS.mirror_card(ob, cam, z)
    ob.rotation_euler = (ob.location - VS.front_point(z)[0]).to_track_quat('-Z', 'Y').to_euler()
    look_at_plane(ob, VS.front_point(z)[0])
    return ob


# ----------------------------------------------------------------- label fill (v002 refinement, 4 Nov)
# Cream labels (C07, C10) read grey: their paper is lit far less than the glass highlights, so AgX lands the
# cream at mid-grey. A soft frontal fill, light-linked to the front-label objects only, lifts the paper without
# touching artwork, materials, glass or backdrop. Energy is per concept and per setup (W-units, x LIGHT_SCALE).
LABEL_FILL = {('C07', '*'): 55, ('C10', '*'): 100, ('C05', 'R24'): 50}


def label_receivers(cid):
    name = 'LBLFILL_RX_' + cid
    rx = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    for ob in bpy.data.objects:
        if ob.name.startswith(cid + '_LBL-FRONT') and ob.type == 'MESH' and ob.name not in rx.objects:
            rx.objects.link(ob)
    return rx


def label_fill(coll, cid, cam, energy, name):
    fz, ez = heights(cid)
    tgt = Vector((0, -0.04, 0.5 * (fz + ez)))
    d = (Vector(cam.location) - tgt).normalized()
    loc = tgt + d * 0.55 + Vector((0, 0, 0.10))
    ob = area(name, coll, tuple(loc), tuple(tgt), (0.45, 0.30), energy, 5200, visible_glossy=False)
    ob.light_linking.receiver_collection = label_receivers(cid)
    return ob


# ----------------------------------------------------------------- recipes
def heights(cid):
    r = bpy.data.objects[cid + '_ROOT']
    fz = r.get('foil_z', 0.137); ez = r.get('emblem_z', r.get('print_z', 0.12))
    return fz, ez


def rig_R25(c, cid, bg):
    """warm seamless, whole bottle, small and left of centre, 5:4."""
    sweep(f'{c.name}_Sweep', c, bg, back=0.7, radius=0.45, height=1.6)
    cam = camera(f'{c.name}_CAM', c, (0.024, -1.14, 0.122), (0.024, 0, 0.115), 85)
    area(f'{c.name}_Key', c, (-0.95, -0.55, 0.50), (0, 0, 0.11), (0.9, 0.7), 300, 4600)
    area(f'{c.name}_Rim_R', c, (0.42, 0.30, 0.22), (0, 0, 0.11), (0.10, 0.90), 55, 4800)
    area(f'{c.name}_Sweep_Wash', c, (0.25, -0.1, 1.0), (0.2, 0.7, 0.35), (0.9, 0.7), 45, 4200, spread=50, visible_glossy=False)
    back_glow(c, f'{c.name}_BackGlow', strength=5.0)
    fz, ez = heights(cid); foil_card(c, f'{c.name}_FoilCard', cam, fz, 2.5)
    return cam, (2000, 1600), dict(lens=85, dist=1.05, cam_h=0.122, notes='key soft front-left high, shadow right-back, rim right, back glow')


def rig_R23(c, cid, bg):
    """bottle on a navy plinth corner, low angle, warm cream gradient, 4:5."""
    wall = plane(f'{c.name}_Wall', c, (3.0, 2.0), (0, 0.85, 0.4), mat_diffuse(f'M_{c.name}_Wall', bg, 0.9), facing=(0, -1, 0.4))
    me = bpy.data.meshes.new(f'{c.name}_Plinth')
    w, d, h = 0.60, 0.50, 0.40
    v = [(x, y, z) for x in (-w / 2, w / 2) for y in (-0.12, -0.12 + d) for z in (-h, 0.0)]
    me.from_pydata(v, [], [(0, 1, 3, 2), (4, 6, 7, 5), (0, 2, 6, 4), (1, 5, 7, 3), (2, 3, 7, 6), (0, 4, 5, 1)])
    pl = bpy.data.objects.new(f'{c.name}_Plinth', me); c.objects.link(pl); pl.location = (0.10, 0.02, 0); pl.rotation_euler = (0, 0, math.radians(-24))
    me.materials.append(mat_diffuse(f'M_{c.name}_Plinth', PLINTH, 0.7))
    cam = camera(f'{c.name}_CAM', c, (-0.03, -0.56, -0.055), (0.0, 0, 0.13), 70)
    area(f'{c.name}_Wall_Glow', c, (0.0, 0.45, 0.02), (0.0, 0.85, 0.12), (0.7, 0.4), 900, 3700, spread=100, visible_glossy=False)
    area(f'{c.name}_Fill', c, (-0.55, -0.70, 0.25), (0, 0, 0.12), (1.0, 1.0), 90, 5000)
    area(f'{c.name}_Kick', c, (0.35, -0.35, 0.45), (0, 0, 0.15), (0.06, 0.06), 15, 5200)
    back_glow(c, f'{c.name}_BackGlow', strength=14.0)
    fz, ez = heights(cid); foil_card(c, f'{c.name}_FoilCard', cam, fz, 2.0)
    return cam, (1600, 2000), dict(lens=80, dist=0.66, cam_h=-0.02, notes='below plinth top looking up; warm wall gradient; strong back glow')


def rig_R19(c, cid, bg):
    """label macro, 1:1, shallow depth of field, bottle turned ~35 deg."""
    fz, ez = heights(cid)
    tgt = (0.0, -0.046, ez if cid == 'C01' else fz)
    world_card = plane(f'{c.name}_Back', c, (2.0, 2.0), (0, 1.0, 0.3), mat_diffuse(f'M_{c.name}_Back', bg, 0.9), facing=(0, 0, 0.3))
    pos = orbit(tgt, 0.31, 35, 12)
    aim = (tgt[0], tgt[1], tgt[2] - 0.022)
    cam = camera(f'{c.name}_CAM', c, tuple(pos), aim, 100, roll=-22, fstop=3.2, focus=(Vector(tgt) - pos).length)
    area(f'{c.name}_Top_Soft', c, (-0.30, -0.35, 0.55), tgt, (0.8, 0.8), 70, 5000)
    area(f'{c.name}_Edge', c, (0.45, 0.25, 0.30), tgt, (0.08, 0.8), 30, 5000)
    back_glow(c, f'{c.name}_BackGlow', strength=3.0)
    foil_card(c, f'{c.name}_FoilCard', cam, tgt[2], 2.0, size=(0.3, 0.2))
    return cam, (2000, 2000), dict(lens=100, fstop=3.2, dist=0.26, notes='macro on roundel + AVANTE; top-left soft source')


def rig_R24(c, cid, bg):
    """hard raking beam on a pale floor, high camera, 2:3."""
    floor = plane(f'{c.name}_Floor', c, (4, 4), (0, 0.4, 0), mat_diffuse(f'M_{c.name}_Floor', '#B9B2A6', 0.75))
    wall = plane(f'{c.name}_Wall', c, (4, 2.0), (0, 1.2, 1.0), mat_diffuse(f'M_{c.name}_Wall', bg, 0.9), facing=(0, -1, 1.0))
    floor.cycles.is_caustics_receiver = True
    tgt = (0, 0, 0.10)
    cam = camera(f'{c.name}_CAM', c, tuple(orbit(tgt, 0.70, 0, 25)), tgt, 70)
    beam = spot(f'{c.name}_Beam', c, (1.1, 0.55, 0.26), (0, 0, 0.08), 3500, 22, radius=0.004, kelvin=5600, blend=0.25)
    beam.data.cycles.is_caustics_light = True
    for n in ('GLS-01_Glass', 'LIQ-01_Brandy'):
        g = bpy.data.objects.get(f'{cid}_{n}')
        if g: g.cycles.is_caustics_caster = True
    area(f'{c.name}_Fill', c, (-0.6, -0.8, 0.6), tgt, (0.6, 0.6), 6, 6000)
    back_glow(c, f'{c.name}_BackGlow', strength=7.0, loc=(-0.02, 0.065, 0.09), size=(0.07, 0.10))
    fz, ez = heights(cid); foil_card(c, f'{c.name}_FoilCard', cam, fz, 1.5)
    return cam, (1600, 2400), dict(lens=70, dist=0.70, el=25, notes='hard spot back-right, long shadow + caustics toward front-left')


def rig_R20(c, cid, bg):
    """black void, emblem side lit, bottle turned 30 deg, slightly low camera."""
    tgt = (0, 0, 0.12)
    cam = camera(f'{c.name}_CAM', c, tuple(orbit(tgt, 0.68, -30, -3)), (0, 0, 0.118), 90, roll=-6)
    area(f'{c.name}_Side_L', c, (-0.70, 0.05, 0.20), tgt, (0.5, 1.2), 260, 4000)
    area(f'{c.name}_Rim_L', c, (-0.35, 0.40, 0.15), tgt, (0.06, 1.0), 40, 5200)
    area(f'{c.name}_Rim_R', c, (0.40, 0.35, 0.15), tgt, (0.06, 1.0), 30, 5200)
    back_glow(c, f'{c.name}_BackGlow', strength=16.0, loc=(0.04, 0.11, 0.09))
    fz, ez = heights(cid); foil_card(c, f'{c.name}_FoilCard', cam, ez, 2.0)
    return cam, (1550, 2400), dict(lens=90, dist=0.95, az=-30, notes='void; big soft side light left; double rim')


def rig_R21(c, cid, bg):
    """floating, tilted ~30 deg (top left), close crop, strip lights along both edges."""
    tgt = (0, 0, 0.115)
    cam = camera(f'{c.name}_CAM', c, tuple(orbit(tgt, 0.52, 8, 14)), tgt, 85, roll=-32)
    area(f'{c.name}_Strip_L', c, (-0.40, -0.10, 0.12), tgt, (0.08, 1.2), 70, 5200)
    area(f'{c.name}_Strip_R', c, (0.40, -0.05, 0.12), tgt, (0.08, 1.2), 60, 5200)
    area(f'{c.name}_Front_Fill', c, (0.05, -0.80, 0.35), tgt, (0.9, 0.6), 25, 5400)
    back_glow(c, f'{c.name}_BackGlow', strength=7.0)
    fz, ez = heights(cid); foil_card(c, f'{c.name}_FoilCard', cam, fz, 2.0)
    return cam, (1300, 2000), dict(lens=85, dist=0.62, roll=-30, notes='tilt by camera roll; long strips both sides')


def rig_R22(c, cid, bg):
    """dark label macro, tilted ~20 deg, foil glowing, warm bokeh behind, 2:3."""
    fz, ez = heights(cid)
    tgt = (0.0, -0.046, fz)
    plane(f'{c.name}_Back', c, (2.0, 2.0), (0, 1.2, 0.3), mat_diffuse(f'M_{c.name}_Back', bg, 0.9), facing=(0, 0, 0.3))
    bk = bpy.data.meshes.new(f'{c.name}_Bokeh')
    import bmesh; bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=0.05); bm.to_mesh(bk); bm.free()
    b = bpy.data.objects.new(f'{c.name}_Bokeh', bk); c.objects.link(b); b.location = (-0.22, 0.65, fz + 0.10)
    bk.materials.append(mat_emit(f'M_{c.name}_Bokeh', hexlin('#C98A3A'), 1.6))
    cam = camera(f'{c.name}_CAM', c, tuple(orbit(tgt, 0.30, 15, 10)), tgt, 100, roll=20, fstop=4.0)
    area(f'{c.name}_Top_Soft', c, (-0.30, -0.30, fz + 0.45), tgt, (0.9, 0.7), 60, 4600)
    back_glow(c, f'{c.name}_BackGlow', strength=4.0)
    foil_card(c, f'{c.name}_FoilCard', cam, fz, 3.0, size=(0.4, 0.2))
    return cam, (1600, 2400), dict(lens=100, fstop=4.0, dist=0.30, roll=20, notes='macro on AVANTE + label; warm bokeh behind')


RECIPES = {'R25': rig_R25, 'R23': rig_R23, 'R19': rig_R19, 'R24': rig_R24, 'R20': rig_R20, 'R21': rig_R21, 'R22': rig_R22}


# ----------------------------------------------------------------- scenes
def copy_settings(src, dst):
    dst.render.engine = src.render.engine
    for block in ('cycles', 'view_settings', 'display_settings'):
        a, b = getattr(src, block, None), getattr(dst, block, None)
        if a is None or b is None: continue
        for p in a.bl_rna.properties:
            if p.is_readonly or p.identifier in ('rna_type', 'curve_mapping'): continue
            try: setattr(b, p.identifier, getattr(a, p.identifier))
            except Exception: pass
    dst.render.film_transparent = False
    dst.render.image_settings.file_format = 'PNG'; dst.render.image_settings.color_depth = '8'


def build():
    main = bpy.data.scenes[0]
    top = bpy.data.collections.get('AVANTE_VARIANTS_MASTER')
    ph = bpy.data.collections.get('PHOTOGRAPHY') or bpy.data.collections.new('PHOTOGRAPHY')
    if ph.name not in top.children: top.children.link(ph)
    made = []
    for cid, ref, bg in PLACEMENTS:
        cc = bpy.data.collections.get('PHOTO_' + cid) or bpy.data.collections.new('PHOTO_' + cid)
        if cc.name not in ph.children: ph.children.link(cc)
        name = f'PHOTO_{cid}_{ref}'
        rig = bpy.data.collections.new(name + '_RIG'); cc.children.link(rig)
        sc = bpy.data.scenes.new(name); copy_settings(main, sc)
        w = bpy.data.worlds.new('W_' + name); w.use_nodes = True
        w.node_tree.nodes['Background'].inputs['Color'].default_value = tuple(x * 0.08 for x in hexlin(bg)[:3]) + (1,)
        w.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0
        sc.world = w
        sc.collection.children.link(bpy.data.collections['CONCEPT_' + cid[1:]])
        sc.collection.children.link(rig)
        cam, res, meta = RECIPES[ref](rig, cid, bg)
        e = LABEL_FILL.get((cid, ref), LABEL_FILL.get((cid, '*')))
        if e: label_fill(rig, cid, cam, e, f'{name}_LabelFill')
        sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 100
        sc['concept'] = cid; sc['reference'] = ref; sc['figma_reference'] = FIGMA_REF[ref]; sc['backdrop'] = bg
        for k, v in meta.items(): sc['est_' + k] = v
        sc['final_spp'] = 512
        made.append(name)
    # keep the rigs out of the shared studio's own renders
    def exclude(lc):
        for ch in lc.children:
            if ch.collection.name == 'PHOTOGRAPHY': ch.exclude = True
            else: exclude(ch)
    for vl in main.view_layers: exclude(vl.layer_collection)
    print('AVANTE_PHOTO scenes', len(made), made)
    return made
