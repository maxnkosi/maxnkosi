"""Final stills from the variants master, one shared studio and one exposure/colour pipeline for every shot.
    blender -b avante_variants_master_v001.blend --python render_variants.py -- PREFIX [only,names] [samples_scale]
Writes renders/<PREFIX>_<shot>.png. Single-bottle shots stage that concept on the v009 hero mark with the
other four hidden from render (no stray shadows or reflections); lineup shots stand all five on their marks."""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import variants_stage as VS

argv = sys.argv[sys.argv.index('--') + 1:]
prefix = argv[0]
only = argv[1].split(',') if len(argv) > 1 and argv[1] not in ('', 'all') else None
scale = float(argv[2]) if len(argv) > 2 else 1.0

SHOTS = [('lineup_hero', 'lineup', None, 'CAM_Lineup_Hero', (2400, 1350), 512),
         ('lineup_threequarter', 'lineup', None, 'CAM_Lineup_ThreeQuarter', (2400, 1350), 512)]
for cid in ('C01', 'C05', 'C06', 'C07', 'C10'):
    SHOTS += [(f'{cid}_hero', 'single', cid, 'CAM_Hero', (1000, 1600), 512),
              (f'{cid}_threequarter', 'single', cid, 'CAM_ThreeQuarter', (1000, 1600), 512)]
for cid in ('C05', 'C06', 'C07', 'C10'):
    for nm in ('Macro_Label', 'Angle_Label', 'Macro_Emblem', 'Angle_Print'):
        if f'CAM_{cid}_{nm}' in bpy.data.objects:
            SHOTS.append((f'{cid}_{nm.lower()}', 'single', cid, f'CAM_{cid}_{nm}', (2000, 1600), 384))
SHOTS.append(('C06_collarflag_macro', 'single', 'C06', 'CAM_Macro_CollarFlag', (2000, 1600), 384))

sc = bpy.context.scene
cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = 'METAL'; cp.get_devices()
for d in cp.devices: d.use = True
sc.cycles.device = 'GPU'
here = os.path.dirname(os.path.abspath(__file__))
for name, mode, cid, cam, res, spp in SHOTS:
    if only and name not in only: continue
    VS.stage(mode, cid, cam)
    sc.cycles.samples = max(16, int(spp * scale))
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(here, 'renders', f'{prefix}_{name}.png')
    bpy.ops.render.render(write_still=True)
    print('VARIANT_DONE', name, flush=True)
