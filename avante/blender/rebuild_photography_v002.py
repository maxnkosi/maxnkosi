"""Rebuild only the PHOTOGRAPHY scenes/rigs inside the v002 master (concept assemblies and studio untouched).

    blender -b avante_variants_master_v002.blend --python rebuild_photography_v002.py [-- PHOTO_C01_R25,...]
"""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
import photography_v002 as PH

for sc in [s for s in bpy.data.scenes if s.name.startswith('PHOTO_')]:
    w = sc.world; bpy.data.scenes.remove(sc)
    if w and w.users == 0: bpy.data.worlds.remove(w)
ph = bpy.data.collections.get('PHOTOGRAPHY')
if ph:
    def purge(c):
        for ch in list(c.children): purge(ch)
        for ob in list(c.objects):
            d = ob.data; bpy.data.objects.remove(ob)
            if d is not None and d.users == 0:
                for coll in (bpy.data.meshes, bpy.data.lights, bpy.data.cameras):
                    if d.name in coll and coll[d.name] == d: coll.remove(d); break
        if c is not ph: bpy.data.collections.remove(c)
    purge(ph)
for m in [m for m in bpy.data.materials if m.users == 0 and m.name.startswith('M_PHOTO_')]: bpy.data.materials.remove(m)
PH.build()
assert os.path.basename(bpy.data.filepath) == 'avante_variants_master_v002.blend'
bpy.ops.wm.save_mainfile()
print('PHOTO_REBUILT', bpy.data.filepath)
