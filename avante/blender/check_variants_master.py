"""Verification of the variants master.
    blender -b avante_variants_master_v001.blend --python check_variants_master.py -- SIG_OUT.json
Concept 1 data signature is compared against v009 by compare_c01_v009 (README)."""
import bpy, sys, os, hashlib
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
OK = []
def check(name, cond, info=''):
    OK.append(bool(cond)); print(('PASS ' if cond else 'FAIL ') + name, info)

def mesh_hash(me):
    a = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', a)
    return hashlib.md5(np.round(a, 7).tobytes()).hexdigest()

def mat_sig(m):
    if not m or not m.node_tree: return str(m and m.name)
    return m.name + ':' + ','.join(sorted(f'{n.bl_idname}' for n in m.node_tree.nodes))

def signature(names):
    out = {}
    for n in names:
        o = bpy.data.objects[n]
        out[n.replace('C01_', '')] = (mesh_hash(o.data), tuple(round(x, 7) for x in o.matrix_world.translation),
                                      tuple(mat_sig(s.material) for s in o.material_slots), tuple(m.type for m in o.modifiers))
    return out

D = bpy.data
C = ['C01', 'C05', 'C06', 'C07', 'C10']
check('one file, one scene', len(D.scenes) == 1)
for cid in C:
    col = D.collections.get('CONCEPT_' + cid[1:])
    check(f'{cid} assembly present', col is not None)
    for sub in ('Bottle_Glass', 'Liquid', 'Closure', 'Labels'):
        check(f'{cid} {sub} populated', len(D.collections[f'{cid}_{sub}'].objects) > 0)
    obs = [o for o in col.all_objects if o.type == 'MESH']
    check(f'{cid} parented to its root', all(o.parent and o.parent.name == cid + '_ROOT' for o in obs))
# same physical bottle
g = [D.objects[f'{c}_GLS-01_Glass'] for c in C]
check('identical glass (shared mesh)', len({o.data.name for o in g}) == 1)
check('identical liquid (shared mesh)', len({D.objects[f'{c}_LIQ-01_Brandy'].data.name for c in C}) == 1)
check('identical capsule geometry', len({D.objects[f'{c}_SLV-CAP-01_Capsule'].data.name for c in C}) == 1)
# label/material independence between concepts
owners = {}
for cid in C:
    for sub in ('Labels', 'Emblems'):
        for o in D.collections[f'{cid}_{sub}'].objects:
            for s in o.material_slots:
                if s.material and ('LBL' in s.material.name or 'PRT' in s.material.name or 'MED' in s.material.name):
                    owners.setdefault(s.material.name, set()).add(cid)
            owners.setdefault('MESH:' + o.data.name, set()).add(cid)
shared = {k: v for k, v in owners.items() if len(v) > 1}
check('labels, emblems and their materials are per-concept', not shared, shared)
# shared studio and cameras
for n in ('STUDIO_SHARED', 'CAMERAS'):
    check(f'{n} present', n in D.collections)
for n in ('CAM_Lineup_Hero', 'CAM_Lineup_ThreeQuarter', 'CAM_Hero', 'CAM_ThreeQuarter'):
    check(f'camera {n}', n in D.objects)
# dependencies
miss = [i.filepath for i in D.images if i.source == 'FILE' and not os.path.exists(bpy.path.abspath(i.filepath))]
check('no missing textures', not miss, miss)
badlib = [l.filepath for l in D.libraries if not os.path.exists(bpy.path.abspath(l.filepath))]
check('every linked library resolves (only Blender bundled Smooth by Angle, as v009)', not badlib, badlib)
# staging
import variants_stage as VS
for cid in C:
    VS.stage('single', cid, 'CAM_Hero')
    vis = [c for c in C if not D.collections['CONCEPT_' + c[1:]].hide_render]
    check(f'single {cid} renders alone on the hero mark', vis == [cid] and tuple(D.objects[cid + '_ROOT'].location) == (0, 0, 0))
VS.stage('lineup', None, 'CAM_Lineup_Hero')
xs = [round(D.objects[c + '_ROOT'].location.x, 4) for c in C]
check('lineup: all five on their marks', all(not D.collections['CONCEPT_' + c[1:]].hide_render for c in C) and len(set(xs)) == 5, xs)
VS.stage('single', 'C01', 'CAM_Hero')
# Concept 1 identical to v009
names = ['C01_GLS-01_Glass', 'C01_LIQ-01_Brandy', 'C01_SLV-CAP-01_Capsule', 'C01_LBL-FRONT-01_Wrap', 'C01_LBL-NECK-01_Collar', 'C01_LBL-ROUNDEL-01_Roundel']
sig = signature(names)
if argv:
    import json
    tmp = argv[0]
    json.dump({k: [v[0], list(v[1]), list(v[2]), list(v[3])] for k, v in sig.items()}, open(tmp, 'w'))
    print('C01_SIG_WRITTEN', tmp)
print('RESULT', 'ALL PASS' if all(OK) else 'FAILURES', f'({sum(OK)}/{len(OK)})')
