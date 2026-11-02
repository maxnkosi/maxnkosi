"""Bake the assembled Currency Stream logo (frame 226) to a static GLB.

Usage (bpy module or `blender -b -P`):
    python tools/export_static_logo.py <source.blend> <out.glb>

The source .blend is never saved; everything happens on the in-memory copy.
"""
import os
import sys
from pathlib import Path

argv = sys.argv[-2:]
sys.argv = sys.argv[:1]
import bpy  # noqa: E402
import numpy as np  # noqa: E402
from mathutils import Matrix  # noqa: E402

SRC, OUT = argv
PIECES = ["Central S", "Left arc", "Right arc"]
ASSEMBLED_FRAME = 226
# Slab thickness multiplier (env THICKNESS_FACTOR). Bevel profiles keep their
# radius: the front half moves +Z, the back half -Z, which lengthens only the
# straight side wall between the two rounded edges.
THICKNESS_FACTOR = float(os.environ.get("THICKNESS_FACTOR", "2"))

bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene

# 1. Evaluate the assembled pose BEFORE touching any animation.
scene.frame_set(ASSEMBLED_FRAME)
deps = bpy.context.evaluated_depsgraph_get()
pose = {n: bpy.data.objects[n].evaluated_get(deps).matrix_world.copy() for n in PIECES}
for n, m in pose.items():
    print(f"frame {ASSEMBLED_FRAME} world[{n}] =", [[round(v, 5) for v in r] for r in m])

# 2. Strip animation, unparent keeping the captured world transforms.
for ob in bpy.data.objects:
    ob.animation_data_clear()
    if ob.data is not None and getattr(ob.data, "animation_data", None):
        ob.data.animation_data_clear()
for act in list(bpy.data.actions):
    bpy.data.actions.remove(act)
for mk in list(scene.timeline_markers):
    scene.timeline_markers.remove(mk)
for n in PIECES:
    ob = bpy.data.objects[n]
    ob.parent = None
    ob.matrix_world = pose[n]
bpy.context.view_layer.update()

# 2b. Thicken without distorting the bevels.
if THICKNESS_FACTOR != 1.0:
    for n in PIECES:
        me = bpy.data.objects[n].data
        co = np.empty(len(me.vertices) * 3); me.vertices.foreach_get("co", co); co = co.reshape(-1, 3)
        half = np.abs(co[:, 2]).max()
        co[:, 2] += np.where(co[:, 2] >= 0, 1.0, -1.0) * half * (THICKNESS_FACTOR - 1.0)
        me.vertices.foreach_set("co", co.ravel()); me.update()
        print(f"{n}: thickness {2*half:.3f} -> {2*np.abs(co[:,2]).max():.3f}")

# 3. Drop pivots, cameras, lights, everything that is not one of the pieces.
for ob in list(bpy.data.objects):
    if ob.name not in PIECES:
        bpy.data.objects.remove(ob, do_unlink=True)

# 4. One named root. Rotated +90deg about X so that, after the exporter's
#    Z-up -> Y-up conversion, the logo faces +Z in glTF (three.js front view).
root = bpy.data.objects.new("Currency Stream Logo", None)
scene.collection.objects.link(root)
root.rotation_euler = (1.5707963267948966, 0, 0)
bpy.context.view_layer.update()
for n in PIECES:
    ob = bpy.data.objects[n]
    ob.parent = root  # identity parent-inverse: pieces rotate with the root

bpy.ops.object.select_all(action="DESELECT")
for n in PIECES + ["Currency Stream Logo"]:
    bpy.data.objects[n].select_set(True)

Path(OUT).parent.mkdir(parents=True, exist_ok=True)
bpy.ops.export_scene.gltf(
    filepath=OUT, export_format="GLB", use_selection=True,
    export_animations=False, export_cameras=False, export_lights=False,
    export_apply=False, export_normals=True, export_texcoords=True,
    export_tangents=False, export_yup=True, export_materials="EXPORT",
    export_image_format="JPEG", export_extras=False,
)
print("wrote", OUT)
