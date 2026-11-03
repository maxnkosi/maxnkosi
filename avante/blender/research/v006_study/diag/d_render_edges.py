# D study (edges/bevels): glass-only close-up renders, current v006 edges (A) vs proposed crisp edges (B).
# Read-only towards the project: imports build_avante_master.py and monkeypatches it IN MEMORY only.
# Run:  Blender -b --factory-startup -P d_render_edges.py -- A|B [samples]
import bpy, math, sys, os, importlib.util
from mathutils import Vector
ROOT = '/Users/maxhlomendlini/Documents/Avante/avante/blender/'
OUT = ROOT + 'research/v006_study/diag/'
spec = importlib.util.spec_from_file_location('bam', ROOT + 'build_avante_master.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else ['A']
VAR = argv[0]; SAMPLES = int(argv[1]) if len(argv) > 1 else 96
MM = B.MM

# ------------------------------------------------------------------ variant B patches (in memory)
if VAR.startswith('B'):
    B.EDGE_SOFT = 0.07   # soft-min k -> ~1.1 mm effective fillet on the 45 deg chamfer edges (d_calibrate.txt)
    B.ARCH_K = 0.30      # -> ~3 mm at the corners, crisp arch line across the faces
    B._SR.clear()

    def sq_radius_stable(theta, S):  # identical maths, no exp underflow for small k
        h, a = S / 2, B.CHAMFER * S
        c, s = abs(math.cos(theta)), abs(math.sin(theta))
        return B.softmin(h / max(c, s), (S - a) / (c + s), B.EDGE_SOFT)
    B.sq_radius = sq_radius_stable

    # adaptive angular sampling: coarse on the flats, ~0.08 mm steps across each fillet.
    # The face/chamfer vertex angles are independent of S: atan(1 - 2*CHAMFER).
    tv = math.atan(1 - 2 * B.CHAMFER)
    vert_angles = []
    for q in range(4):
        base = q * math.pi / 2
        vert_angles += [base + tv, base + math.pi / 2 - tv]
    TH = set(round(2 * math.pi * i / 384, 7) for i in range(384))
    for va in vert_angles:
        for j in range(-24, 25):  # +-24 steps of 0.0018 rad (~0.085 mm at r~47 mm) = +-2 mm
            TH.add(round((va + j * 0.0018) % (2 * math.pi), 7))
    THETAS = sorted(TH)
    print('B ring verts:', len(THETAS))

    def ring_adaptive(z, S, t, n=None, off=0.0, cut=None):
        pts = []
        for th in THETAS:
            r = B.section_r(th, S, t)
            if cut is not None: r = B.dome_cut(r, z, cut)
            r += off
            pts.append(((r * math.cos(th)) * MM, (r * math.sin(th)) * MM, z * MM))
        return pts
    B.ring = ring_adaptive

    _zs_orig = B.z_samples
    def z_samples_fine(z0, z1):
        zs = set(_zs_orig(z0, z1))
        z = z0
        while z < z1:  # 0.2 mm through the arch band and the shoulder knuckle
            if 128 <= z <= 162 or 178 <= z <= 192: zs.add(round(z, 3))
            z += 0.2
        return sorted(zs)
    B.z_samples = z_samples_fine

    # heel: straight 33 deg bevel, 7 mm tall x 4.5 mm in, R1.0 at the bevel top and R1.0 at the footprint
    def fillet_polyline(P, radii, step=0.08):
        """P: list of (hw, z) vertices; radii[i] for interior vertex i (1..n-2). Returns sampled points."""
        out = [P[0]]
        for i in range(1, len(P) - 1):
            a, b, c = Vector(P[i - 1]), Vector(P[i]), Vector(P[i + 1])
            u, v = (a - b).normalized(), (c - b).normalized()
            ang = math.acos(max(-1, min(1, u.dot(v))))
            d = radii[i] / math.tan(ang / 2)
            p0, p1 = b + u * d, b + v * d
            bis = (u + v).normalized(); ctr = b + bis * (radii[i] / math.sin(ang / 2))
            a0 = math.atan2(*(p0 - ctr).yx); a1 = math.atan2(*(p1 - ctr).yx)
            da = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            nseg = max(4, int(abs(da) * radii[i] / step))
            seg_start = Vector(out[-1]); L = (p0 - seg_start).length
            for k in range(1, int(L / 0.5) + 1): out.append(tuple(seg_start + (p0 - seg_start) * (k * 0.5 / L)))
            for k in range(nseg + 1):
                ak = a0 + da * k / nseg
                out.append((ctr.x + radii[i] * math.cos(ak), ctr.y + radii[i] * math.sin(ak)))
        end = Vector(P[-1]); s = Vector(out[-1]); L = (end - s).length
        for k in range(1, int(L / 0.5) + 1): out.append(tuple(s + (end - s) * (k * 0.5 / L)))
        out.append(P[-1])
        return out
    Z_TOP = 14.0
    hw14 = B.width_at(Z_TOP) / 2
    side_slope = (B.width_at(20) - B.width_at(Z_TOP)) / 2 / (20 - Z_TOP)
    hwS = hw14 - side_slope * (Z_TOP - 7.5)
    hwF = hwS - 4.5
    base_poly = fillet_polyline([(hwF - 6, 0.0), (hwF, 0.0), (hwS, 7.5), (hw14, Z_TOP)], [None, 1.0, 1.0])
    print('B heel: footprint hw %.2f, bevel top hw %.2f, side hw14 %.2f' % (hwF, hwS, hw14))

    def build_glass_B(C, base_t):
        outer = [B.ring(z, 2 * hw, 0.0, cut=0.0) for hw, z in base_poly[:-1]]
        outer += [B.ring(z, B.body_S(z), B.roundness(z), cut=0.0) for z in B.z_samples(Z_TOP, B.GLASS_H)]
        inner = [B.ring(z, S, t, cut=(B.WALL if z < 185 else None)) for z, S, t in reversed(B.inner_stack(base_t, B.GLASS_H))]
        verts, faces = B.loft(outer + inner, close_bottom=(0, 0, 1.2 * MM), close_top=(0, 0, (base_t + B.PUNT_H) * MM))
        ob = B.mesh_from('GLS-01_Glass', verts, faces, C)
        B.recalc_normals(ob)
        for p in ob.data.polygons: p.use_smooth = True   # plain smooth: dense true fillets carry the edge
        return ob
    builder = build_glass_B
else:
    builder = B.build_glass

# ------------------------------------------------------------------ scene
B.clear_scene()
base_t = B.solve_base_thickness(); B.BASE_T = base_t
C = B.coll('GEO_Glass')
glass = builder(C, base_t); gm = B.mat_glass(); glass.data.materials.append(gm)
if VAR.endswith('nobump'):
    for n in gm.node_tree.nodes:
        if n.type == 'BUMP': n.inputs['Strength'].default_value = 0.0
print('glass verts', len(glass.data.vertices), 'base_t', round(base_t, 2))
S = B.coll('ENV')
sc = bpy.context.scene
wd = bpy.data.worlds.new('W'); sc.world = wd; wd.use_nodes = True
wd.node_tree.nodes['Background'].inputs[0].default_value = (0.82, 0.82, 0.82, 1)   # white packshot, like the refs
# white floor
fl = B.mesh_from('ENV_Floor', [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)], [(0, 1, 2, 3)], S)
fl.data.materials.append(B.mat_simple('M_floor', **{'Base Color': (0.8, 0.8, 0.8, 1), 'Roughness': 0.4}))
# black side flags (seen only through/in the glass): they draw the edge lines, as in a packshot studio
def flag(name, loc, w, h, tgt):
    ob = B.mesh_from(name, [(-w/2, -h/2, 0), (w/2, -h/2, 0), (w/2, h/2, 0), (-w/2, h/2, 0)], [(0, 1, 2, 3)], S)
    ob.location = loc; B.look_at(ob, tgt); ob.visible_camera = False; ob.visible_shadow = False
    ob.data.materials.append(B.mat_simple('M_black', **{'Base Color': (0.0, 0.0, 0.0, 1), 'Roughness': 1.0, 'Specular IOR Level': 0.0}))
for nm, x in (('FLG_L', -0.22), ('FLG_R', 0.22)):
    flag(nm, (x, 0.06, 0.12), 0.12, 0.5, (0, 0.06, 0.12))
flag('FLG_Back_Strip', (0, 0.30, 0.12), 0.04, 0.5, (0, 0, 0.12))
B.area_light(S, 'LGT_Key', (-0.5, -0.5, 0.45), 0.6, 30.0, (0, 0, 0.12))
B.render_settings(samples=SAMPLES, res=(900, 900))
try:
    cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = 'METAL'; cp.get_devices()
    for d in cp.devices: d.use = True
    sc.cycles.device = 'GPU'
except Exception as e: print('GPU unavailable', e)

def cam(name, yaw_deg, elev_deg, tgt_mm, dist, lens, res=(900, 900)):
    cd = bpy.data.cameras.new(name); cd.lens = lens
    co = bpy.data.objects.new(name, cd); S.objects.link(co)
    y, e = math.radians(yaw_deg), math.radians(elev_deg)
    t = Vector((0, 0, tgt_mm * MM))
    co.location = t + dist * Vector((math.sin(y) * math.cos(e), -math.cos(y) * math.cos(e), math.sin(e)))
    B.look_at(co, t)
    return co, res
shots = [cam('corner_z100', 28, 4, 100, 0.20, 100),       # face -> chamfer -> side, transmitted + reflected
         cam('shoulder_arch', 20, 12, 146, 0.26, 100),     # arch edge across the face and over the corner
         cam('base_heel', 30, 3, 10, 0.22, 100),           # heel bevel, footprint corners
         cam('neck_root', 15, 8, 190, 0.24, 100),          # shoulder-to-neck and finish
         cam('full_34', 30, 6, 113, 0.70, 85, (700, 1000))]
if VAR.endswith('nobump'): shots = [shots[1], shots[3], shots[4]]
for co, res in shots:
    sc.camera = co; sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = OUT + f'r_{VAR}_{co.name}.png'
    bpy.ops.render.render(write_still=True)
    print('D_RENDER', sc.render.filepath)
