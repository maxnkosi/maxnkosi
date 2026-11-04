"""Render the reference-directed photography scenes of the variants master.

    blender -b avante_variants_master_v002.blend --python render_photography.py -- PASS [scenes|all] [res_pct] [spp]

PASS is A (composition), B (light/material), C (QC) or FINAL; output renders/photography/<PASS>/<scene>.png.
Each PHOTO_<cid>_<ref> scene links its concept's assembly and its own rig only; the concept is shown on the
hero mark (root at the origin), exactly as for the diagnostic renders.
"""
import bpy, sys, os
argv = sys.argv[sys.argv.index('--') + 1:]
PASS = argv[0]
names = None if len(argv) < 2 or argv[1] in ('', 'all') else argv[1].split(',')
pct = int(argv[2]) if len(argv) > 2 else 100
spp = int(argv[3]) if len(argv) > 3 else None
here = os.path.dirname(os.path.abspath(__file__))
cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = 'METAL'; cp.get_devices()
for d in cp.devices: d.use = True
for sc in [s for s in bpy.data.scenes if s.name.startswith('PHOTO_')]:
    if names and sc.name not in names: continue
    cid = sc['concept']
    col = bpy.data.collections['CONCEPT_' + cid[1:]]; col.hide_render = False
    bpy.data.objects[cid + '_ROOT'].location = (0, 0, 0)
    sc.cycles.device = 'GPU'
    sc.cycles.samples = spp or sc.get('final_spp', 512)
    sc.render.resolution_percentage = pct
    sc.render.filepath = os.path.join(here, 'renders', 'photography', PASS, sc.name + '.png')
    bpy.ops.render.render(write_still=True, scene=sc.name)
    print('PHOTO_DONE', sc.name, flush=True)
