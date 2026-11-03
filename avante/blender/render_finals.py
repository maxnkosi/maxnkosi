"""Final stills from a saved master. blender -b avante_master_v005.blend --python render_finals.py -- PREFIX SAMPLES
Aims the camera-dependent cards (back card, foil strips) for each camera before rendering."""
import bpy, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_avante_master as B
argv = sys.argv[sys.argv.index('--') + 1:]
prefix, samples = argv[0], int(argv[1])
only = argv[2].split(',') if len(argv) > 2 else None
SHOTS = [('hero', 'CAM_Hero', (1000, 1600)), ('threequarter', 'CAM_ThreeQuarter', (1000, 1600)),
         ('foil_macro', 'CAM_Macro_Avante', (2000, 1600)), ('roundel_macro', 'CAM_Macro_Roundel', (2000, 1600)),
         ('collarflag_macro', 'CAM_Macro_CollarFlag', (2000, 1600)), ('angle_avante', 'CAM_Angle_Avante', (2000, 1600)),
         ('angle_roundel', 'CAM_Angle_Roundel', (2000, 1600)), ('angle_collarflag', 'CAM_Angle_CollarFlag', (2000, 1600)),
         ('shoulder', 'CAM_Shoulder', (2000, 1500)), ('shoulder34', 'CAM_Shoulder_34', (2000, 1500))]
sc = bpy.context.scene
cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = 'METAL'; cp.get_devices()
for d in cp.devices: d.use = True
sc.cycles.device = 'GPU'; sc.cycles.samples = samples
here = os.path.dirname(os.path.abspath(__file__))
for name, cam, res in SHOTS:
    if only and name not in only: continue
    B.aim_studio(bpy.data.objects[cam])
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(here, 'renders', f'{prefix}_{name}.png')
    bpy.ops.render.render(write_still=True)
    print('FINAL_DONE', name, flush=True)
