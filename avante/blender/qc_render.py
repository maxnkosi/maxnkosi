"""Fixed QC cameras for like-for-like comparison. Open a .blend, then:
blender -b file.blend --python qc_render.py -- OUT_DIR PREFIX [SAMPLES] [cam,cam]"""
import bpy, sys, os, math
from mathutils import Vector
argv = sys.argv[sys.argv.index('--') + 1:]
outdir, prefix = argv[0], argv[1]
samples = int(argv[2]) if len(argv) > 2 else 128
only = argv[3].split(',') if len(argv) > 3 else None
# name: location, lens, target, focus distance, f-stop, resolution
QC = {
 'hero':       ((0.0, -0.74, 0.13), 85, (0, 0, 0.119), None, None, (1000, 1600)),
 'threequarter': ((0.42, -0.6, 0.16), 85, (0, 0, 0.119), None, None, (1000, 1600)),
 'base':       ((0.05, -0.30, 0.035), 100, (0, -0.02, 0.018), 0.285, 11, (1200, 960)),
 'paper':      ((0.0, -0.21, 0.095), 100, (0, 0, 0.095), 0.168, 11, (1200, 960)),
 'neck':       ((0.03, -0.28, 0.195), 100, (0.008, 0, 0.195), 0.262, 11, (1200, 960)),
 'roundel':    ((0.0, -0.28, 0.0422), 100, (0, 0, 0.0422), 0.242, 11, (1200, 960)),
 'liquid':     ((0.0, -0.22, 0.164), 100, (0.02, 0, 0.16), 0.185, 11, (1200, 960)),
}
sc = bpy.context.scene
sc.cycles.samples = samples; sc.cycles.use_denoising = True
cp = bpy.context.preferences.addons['cycles'].preferences; cp.compute_device_type = 'METAL'; cp.get_devices()
for d in cp.devices: d.use = True
sc.cycles.device = 'GPU'
for name, (loc, lens, tgt, focus, fs, res) in QC.items():
    if only and name not in only: continue
    cd = bpy.data.cameras.new('QC_' + name); cd.lens = lens
    if focus: cd.dof.use_dof = True; cd.dof.focus_distance = focus; cd.dof.aperture_fstop = fs
    co = bpy.data.objects.new('QC_' + name, cd); sc.collection.objects.link(co); co.location = loc
    co.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = co
    if bpy.data.objects.get('CRD_Foil_Strip'):  # v005 scene: back card + foil strip follow the camera
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import build_avante_master as B
        co['foil_aim_z'] = {'roundel': 0.0422, 'neck': 0.2075, 'base': 0.0422}.get(name, 0.137)
        B.aim_studio(co)
    else:  # v004 and earlier
        rig = bpy.data.objects.get('RIG_BackCard')
        if rig and rig.constraints: rig.constraints[0].target = co
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.filepath = os.path.join(outdir, f'{prefix}_{name}.png')
    bpy.ops.render.render(write_still=True)
    print('QC_DONE', name)
