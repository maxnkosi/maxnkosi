"""Avante variants master v001: Concepts 1, 5, 6, 7 and 10 in one shared studio.

    blender -b avante_master_v009.blend --python build_variants_master.py -- --save avante_variants_master_v001.blend [--only C01,C05]

Opens the approved v009 master (never re-saved), reorganises it into the variants hierarchy and adds the four
new concept assemblies. Concept 1 objects, materials, studio and cameras are v009 untouched (only renamed into
collections and parented to CONCEPT_01's root at the origin).
Glass, liquid and capsule meshes are linked duplicates (identical physical bottle); every label, emblem and
label material is a per-concept copy, so editing one concept cannot change another.
"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_avante_master as B
import variants_stage as VS

MM = 0.001
SPACING = 0.135     # lineup pitch (m): 89 mm bottles, 46 mm air
ORDER = ['C01', 'C05', 'C06', 'C07', 'C10']


def new_coll(name, parent):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in parent.children: parent.children.link(c)
    return c


def move(ob, dest):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    dest.objects.link(ob)


def concept_tree(top, cid):
    col = new_coll('CONCEPT_' + cid[1:], top)
    subs = {k: new_coll(f'{cid}_{k}', col) for k in ('Bottle_Glass', 'Liquid', 'Closure', 'Labels', 'Emblems', 'Materials')}
    r = bpy.data.objects.new(cid + '_ROOT', None); r.empty_display_type = 'PLAIN_AXES'; r.empty_display_size = 0.03
    col.objects.link(r)
    r['lineup_x'] = (ORDER.index(cid) - 2) * SPACING
    return col, subs, r


def parent(ob, r):
    ob.parent = r; ob.matrix_parent_inverse.identity()


def restructure():
    sc = bpy.context.scene
    top = new_coll('AVANTE_VARIANTS_MASTER', sc.collection)
    st = new_coll('STUDIO_SHARED', top)
    S = {k: new_coll('STUDIO_' + k, st) for k in ('Floor', 'Background', 'Softboxes', 'Reflectors', 'Flags')}
    cams = new_coll('CAMERAS', top)
    K = {k: new_coll('CAM_' + k, cams) for k in ('Lineup_Hero', 'Lineup_ThreeQuarter', 'Individual_Hero', 'Individual_ThreeQuarter', 'Material_Macros')}
    O = bpy.data.objects
    move(O['ENV_Sweep'], S['Floor'])
    for n in ('LGT_Key_Softbox', 'LGT_Rim_L_Strip', 'LGT_Rim_R_Strip', 'LGT_Top', 'LGT_Fill_Low'): move(O[n], S['Softboxes'])
    for n in ('RIG_BackCard', 'CRD_Brandy_Back', 'CRD_Foil_Strip', 'CRD_Foil_Strip_Roundel'): move(O[n], S['Reflectors'])
    for n in ('FLG_Black_L', 'FLG_Black_R'): move(O[n], S['Flags'])
    for n in ('CAM_Hero', 'CAM_Shoulder', 'RIG_Turntable', 'CAM_Turntable'): move(O[n], K['Individual_Hero'])
    for n in ('CAM_ThreeQuarter', 'CAM_Shoulder_34', 'CAM_Corner'): move(O[n], K['Individual_ThreeQuarter'])
    for n in ('CAM_Macro_Avante', 'CAM_Macro_Roundel', 'CAM_Macro_CollarFlag', 'CAM_Angle_Avante', 'CAM_Angle_Roundel', 'CAM_Angle_CollarFlag'):
        move(O[n], K['Material_Macros'])
    # the world (near-black) is the background; the sweep is floor and backdrop in one piece
    S['Background']['note'] = 'World background (near-black, v009) + ENV_Sweep backdrop in STUDIO_Floor'
    # Concept 1: v009 objects, renamed with the concept prefix, parented to CONCEPT_01's root at the origin
    col, subs, r = concept_tree(top, 'C01')
    for n, k in (('GLS-01_Glass', 'Bottle_Glass'), ('LIQ-01_Brandy', 'Liquid'), ('SLV-CAP-01_Capsule', 'Closure'),
                 ('LBL-FRONT-01_Wrap', 'Labels'), ('LBL-NECK-01_Collar', 'Labels'), ('LBL-ROUNDEL-01_Roundel', 'Emblems')):
        ob = O[n]; move(ob, subs[k]); parent(ob, r); ob.name = 'C01_' + n
    r['emblems'] = 'C01_LBL-ROUNDEL-01_Roundel'; r['foil_z'] = 0.137; r['emblem_z'] = 0.0422
    # foil receivers: the old GEO_Labels collection becomes a pure light-link set (not in the scene tree)
    gl = bpy.data.collections['GEO_Labels']
    if gl.name in sc.collection.children: sc.collection.children.unlink(gl)
    gl.name = 'LNK_Foil_Labels'
    for c in ('GEO_Labels', 'GEO_Glass_Liquid', 'GEO_Capsule', 'LGT_CAM_ENV'):
        cc = bpy.data.collections.get(c)
        if cc and cc.name in sc.collection.children: sc.collection.children.unlink(cc)
    for ob in list(gl.objects): gl.objects.unlink(ob)
    for n in ('C01_LBL-FRONT-01_Wrap', 'C01_LBL-NECK-01_Collar', 'C01_LBL-ROUNDEL-01_Roundel'): gl.objects.link(O[n])
    for c in ('GEO_Glass_Liquid', 'GEO_Capsule', 'LGT_CAM_ENV'):
        cc = bpy.data.collections.get(c)
        if cc and not cc.objects and not cc.children: bpy.data.collections.remove(cc)
    return top, S, K


def concept_shell(top, cid):
    """Linked-duplicate glass, liquid and capsule (one physical bottle) under a new concept root."""
    col, subs, r = concept_tree(top, cid)
    O = bpy.data.objects
    for n, k in (('GLS-01_Glass', 'Bottle_Glass'), ('LIQ-01_Brandy', 'Liquid'), ('SLV-CAP-01_Capsule', 'Closure')):
        src = O['C01_' + n]; ob = src.copy()  # shares mesh data and materials (identical bottle)
        ob.name = f'{cid}_{n}'; subs[k].objects.link(ob); parent(ob, r)
    return col, subs, r


def lineup_rig(S, K):
    """Lineup-only cards and the two lineup cameras. Hidden in single mode by variants_stage."""
    O = bpy.data.objects
    src_rig, src_card = O['RIG_BackCard'], O['CRD_Brandy_Back']
    for cid in ORDER:
        rig = bpy.data.objects.new('RIG_BackCard_' + cid, None); S['Reflectors'].objects.link(rig)
        rig.parent = O[cid + '_ROOT']
        tc = rig.constraints.new('LOCKED_TRACK'); tc.track_axis = 'TRACK_NEGATIVE_Y'; tc.lock_axis = 'LOCK_Z'
        card = src_card.copy(); card.name = 'CRD_Brandy_Back_' + cid; S['Reflectors'].objects.link(card)
        card.parent = rig; card.location = src_card.location.copy(); card.rotation_euler = src_card.rotation_euler.copy()
        card.hide_render = True; rig.hide_render = True
    ls = B.foil_card(S['Reflectors'], 'CRD_Foil_Strip_Lineup', 1.30, 0.28, 9.0, bpy.data.collections['LNK_Foil_Labels'])
    ls.hide_render = True
    # variants: a third strip for the gold prints on the glass (they sit far above the label copy)
    lp = bpy.data.collections.get('LNK_Prints') or bpy.data.collections.new('LNK_Prints')
    ps = B.foil_card(S['Reflectors'], 'CRD_Foil_Strip_Print', 0.30, 0.08, 4.5, lp); ps.hide_render = True
    # the lineup cameras stand further back than the v009 sweep's front edge (y -0.6): a matching apron
    # continues the floor toward them. Lineup only, so the single-bottle (v009) shots are unchanged.
    ap = B.mesh_from('ENV_Floor_Lineup_Apron', [(-1.6, -2.6, 0), (1.6, -2.6, 0), (1.6, -0.6, 0), (-1.6, -0.6, 0)], [(0, 1, 2, 3)], S['Floor'])
    ap.data.materials.append(bpy.data.materials['M_ENV_Sweep']); ap.hide_render = True
    # wider copy of the same sweep for the lineup (the 1.6 m v009 sweep ends inside the 3/4 lineup frame)
    sw = O['ENV_Sweep'].copy(); sw.data = O['ENV_Sweep'].data.copy(); sw.name = 'ENV_Sweep_Lineup'
    sw.scale = (3.0, 1.0, 1.0); S['Background'].objects.link(sw); sw.hide_render = True
    # lineup cameras: 85 mm like CAM_Hero, far enough to hold five bottles in 16:9
    for name, coll, loc, tgt, aimz in (('CAM_Lineup_Hero', 'Lineup_Hero', (0.0, -1.95, 0.135), (0, 0, 0.118), 0.11),
                                       ('CAM_Lineup_ThreeQuarter', 'Lineup_ThreeQuarter', (0.98, -1.70, 0.30), (0.02, 0, 0.112), 0.11)):
        cd = bpy.data.cameras.new(name); cd.lens = 85
        co = bpy.data.objects.new(name, cd); K[coll].objects.link(co); co.location = loc; VS._look_at(co, tgt)
        co['foil_aim_z'] = aimz; co['lineup'] = 1; co['res'] = (2400, 1350)


def concept_macros(K):
    """Per-concept macro cameras on the hero mark (same lenses and stops as the v009 macros):
    label copy (front, 100 mm f/16), emblem or glass print (front, 100 mm f/8), raking angle on the label
    (135 mm f/16, turned 20 deg and rolled, like CAM_Angle_Avante). Collar flags use the v009 collar cameras."""
    import math
    for cid in ORDER[1:]:
        r = bpy.data.objects[cid + '_ROOT']
        fz = r['foil_z']; ez = r.get('emblem_z', r.get('print_z'))
        shots = [('Macro_Label', fz, (0.0, -0.28), 100, 16, 0, None), ('Angle_Label', fz, None, 135, 16, 25, (20, 8))]
        if ez: shots.append(('Macro_Emblem', ez, (0.0, -0.28), 100, 8, 0, None))
        if r.get('print_z') and r.get('emblem_z'): shots.append(('Angle_Print', r['print_z'], None, 135, 11, -20, (-18, 6)))
        for nm, z, loc, lens, fs, roll, ang in shots:
            name = f'CAM_{cid}_{nm}'
            fy = VS.front_point(z)[0].y
            cd = bpy.data.cameras.new(name); cd.lens = lens; cd.dof.use_dof = True; cd.dof.aperture_fstop = fs
            tgt = (0.0, fy, z)
            if ang is None:
                l = (loc[0], loc[1], z); cd.dof.focus_distance = abs(loc[1] - fy)
            else:
                y_, e_ = math.radians(ang[0]), math.radians(ang[1]); fd = 0.30; cd.dof.focus_distance = fd
                l = tuple(t + fd * d for t, d in zip(tgt, (math.sin(y_) * math.cos(e_), -math.cos(y_) * math.cos(e_), math.sin(e_))))
            co = bpy.data.objects.new(name, cd); K['Material_Macros'].objects.link(co); co.location = l; VS._look_at(co, tgt)
            if roll:
                from mathutils import Quaternion
                co.rotation_euler = (co.rotation_euler.to_quaternion() @ Quaternion((0, 0, 1), math.radians(roll))).to_euler()
            co[f'foil_aim_z_{cid}'] = z; co['foil_aim_z'] = z; co['concept'] = cid
            if 'Emblem' in nm: co['foil_strength'] = 0.5


def main(only=None):
    top, S, K = restructure()
    import variants_concepts as VC
    for cid in ORDER[1:]:
        col, subs, r = concept_shell(top, cid)
        if only is None or cid in only:
            VC.BUILD[cid](subs, r)
    lineup_rig(S, K)
    if only is None: concept_macros(K)
    # store the staging module inside the file so the .blend is self-contained
    here = os.path.dirname(os.path.abspath(__file__))
    for fn in ('variants_stage.py',):
        t = bpy.data.texts.get(fn) or bpy.data.texts.new(fn); t.from_string(open(os.path.join(here, fn)).read())
    VS.stage('single', 'C01', bpy.data.objects['CAM_Hero'])


if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    only = argv[argv.index('--only') + 1].split(',') if '--only' in argv else None
    main(only)
    if '--save' in argv:
        out = os.path.abspath(argv[argv.index('--save') + 1])
        assert not out.endswith('avante_master_v009.blend'), 'v009 is the untouched checkpoint'
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print('VARIANTS_SAVED', out)
