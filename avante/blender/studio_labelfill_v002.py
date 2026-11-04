"""v002 refinement (4 Nov): soft frontal fill in the shared studio, light-linked to the C07 and C10 front labels only,
so their cream paper reads cream (not AgX mid-grey) in the lineup and single-bottle renders. Idempotent; artwork,
materials, glass and the other concepts are untouched.

    blender -b avante_variants_master_v002.blend --python studio_labelfill_v002.py [-- C07=25,C10=45]
"""
import bpy, sys, os
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import photography_v002 as PH

argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ENERGY = {'C07': 25.0, 'C10': 45.0}          # watts (studio key LGT_Key_Softbox = 10.5 W)
for a in argv[0].split(',') if argv else []:
    k, v = a.split('='); ENERGY[k] = float(v)

main = [s for s in bpy.data.scenes if not s.name.startswith('PHOTO_')][0]
coll = bpy.data.collections.get('STUDIO_LABEL_FILL') or bpy.data.collections.new('STUDIO_LABEL_FILL')
if coll.name not in main.collection.children: main.collection.children.link(coll)
for cid, e in ENERGY.items():
    name = f'LGT_LabelFill_{cid}'
    ob = bpy.data.objects.get(name)
    if ob is None:
        ld = bpy.data.lights.new(name, 'AREA'); ob = bpy.data.objects.new(name, ld); coll.objects.link(ob)
    ld = ob.data; ld.shape = 'RECTANGLE'; ld.size, ld.size_y = 1.6, 0.5; ld.energy = e; ld.color = PH.kelvin_rgb(5200)
    ob.location = (0, -1.6, 0.35); PH.look_at(ob, (0, 0, 0.11)); ob.visible_glossy = False; ob.visible_camera = False
    ob.light_linking.receiver_collection = PH.label_receivers(cid)
    print('LABEL_FILL', name, e, len(ob.light_linking.receiver_collection.objects))
assert os.path.basename(bpy.data.filepath) == 'avante_variants_master_v002.blend'
bpy.ops.wm.save_mainfile(); print('STUDIO_LABELFILL_SAVED')
