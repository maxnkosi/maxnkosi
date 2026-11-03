"""List objects / texts in a .blend (read-only). Usage: blender -b --factory-startup FILE -P d1_inspect.py"""
import bpy
print('FILE', bpy.data.filepath)
for t in bpy.data.texts: print('TEXT', t.name, len(t.as_string()))
for o in bpy.data.objects:
    print('OBJ', o.name, o.type, len(o.data.vertices) if o.type == 'MESH' else '', [m.type for m in o.modifiers])
