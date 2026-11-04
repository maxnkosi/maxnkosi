"""Avante variants master v002: v001 structure, with the user's 3 Nov 2026 Figma edits and comments.

    blender -b avante_master_v009.blend --python build_variants_master_v002.py -- --save avante_variants_master_v002.blend

Same build as v001 (build_variants_master.py: v009 opened, never re-saved; one file, one shared studio), with
- Concepts 5, 6, 7, 10 from variants_concepts_v002 (edited vectors, frozen v001 registration, domed emboss,
  0.60 mm solid-metal coin);
- Concept 1: v009 objects as before, plus the domed emboss requested in two Figma comments: the AVANTE wordmark
  (spearman keeps the flat EMB-01 die) and the clear-film roundel (film domed, stamped-foil relief kept).
v001 and v009 are not touched; the save refuses either name.
"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import build_avante_master as B
import build_variants_master as BV
import variants_stage as VS
import variants_kit as K
import variants_concepts_v002 as VC2

HERE = os.path.dirname(os.path.abspath(__file__))
AVANTE_SPLIT = 0.29        # C01 emboss mask: rows below this fraction of the height are the AVANTE wordmark
ROUNDEL_DOME_H = 0.45      # P (mm) domed film roundel, centre rise


def c01_domed_wordmark():
    """Rebuild HEIGHT-EMB-01 for C01: AVANTE domed (pillow, 0.25 mm), spearman flat EMB-01 (0.20 mm)."""
    T = B.tex_dir()
    mask = K.load_rgba(os.path.join(T, 'MASK-EMB-01__LBL-FRONT-01.png'))[..., 0]
    H, W = mask.shape
    word = mask.copy(); word[:int(H * AVANTE_SPLIT)] = 0
    spear = mask - word
    dome = VC2.dome_profile(word) * (VC2.DOME_H / B.EMB_H)                 # in EMB_H units (displacement scale)
    flat = K.round_emboss(spear)
    h = np.maximum(dome, flat).astype(np.float32)
    # the v005 height map is 2x the mask resolution: upsample to match it
    old = bpy.data.images.load(os.path.join(T, 'HEIGHT-EMB-01__LBL-FRONT-01.exr'), check_existing=True)
    ow, oh = old.size
    h2 = VC2.V1.resize(h[..., None], ow, oh)[..., 0]
    out = bpy.data.images.new('HEIGHT-EMB-02__LBL-FRONT-01_C01_domed', ow, oh, alpha=False, float_buffer=True)
    out.colorspace_settings.name = 'Non-Color'
    px = np.dstack([h2, h2, h2, np.ones_like(h2)])[::-1]
    out.pixels.foreach_set(np.ascontiguousarray(px, np.float32).ravel())
    fn = os.path.join(HERE, 'textures', 'variants_v002', 'HEIGHT-EMB-02__LBL-FRONT-01_C01_domed.exr')
    os.makedirs(os.path.dirname(fn), exist_ok=True)
    # lossless ZIP float EXR: ~2 MB instead of ~470 MB uncompressed (GitHub's 100 MB file limit)
    s = bpy.context.scene.render.image_settings
    s.file_format = 'OPEN_EXR'; s.color_depth = '32'; s.exr_codec = 'ZIP'; s.color_mode = 'RGB'
    out.save_render(fn, scene=bpy.context.scene)
    out.source = 'FILE'; out.filepath = fn; out.reload()
    n = 0
    for m in bpy.data.materials:
        if not m.node_tree: continue
        for nd in m.node_tree.nodes:
            if nd.bl_idname == 'ShaderNodeTexImage' and nd.image and nd.image.name.startswith('HEIGHT-EMB-01__LBL-FRONT-01'):
                nd.image = out; n += 1
    print('AVANTE_V2 C01 domed wordmark: height map swapped in', n, 'node(s); max', round(float(h.max()) * B.EMB_H, 3), 'mm')
    return n


def c01_domed_roundel():
    """Clear-film roundel domed: height (mm) = dome cap over the film disc + the v004 stamped-foil relief."""
    m = bpy.data.materials['M_LBL-ROUNDEL-01_ClearFilm']; nt = m.node_tree
    dsp = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeDisplacement'][0]
    foil = dsp.inputs['Height'].links[0].from_socket
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0)
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    nt.links.new(tc.outputs['UV'], sub.inputs[0]); nt.links.new(sub.outputs[0], ln.inputs[0])
    r_uv = B.ROUNDEL_FILM_R / B.ROUNDEL_TEX
    rr = B.math_node(nt, 'DIVIDE', ln.outputs['Value'], r_uv)
    cap = B.math_node(nt, 'MAXIMUM', B.math_node(nt, 'SUBTRACT', 1.0, B.math_node(nt, 'MULTIPLY', rr, rr)), 0.0)
    h = B.math_node(nt, 'ADD', B.math_node(nt, 'MULTIPLY', cap, ROUNDEL_DOME_H), B.math_node(nt, 'MULTIPLY', foil, B.ROUNDEL_RELIEF))
    nt.links.new(h, dsp.inputs['Height']); dsp.inputs['Scale'].default_value = B.MM    # height already in mm
    ob = bpy.data.objects['C01_LBL-ROUNDEL-01_Roundel']
    if not any(md.type == 'SUBSURF' for md in ob.modifiers): K.dice(ob)
    m['v002'] = 'domed film roundel %.2f mm + stamped foil' % ROUNDEL_DOME_H
    print('AVANTE_V2 C01 domed roundel', ROUNDEL_DOME_H, 'mm')


def main():
    top, S, KC = BV.restructure()
    for cid in BV.ORDER[1:]:
        col, subs, r = BV.concept_shell(top, cid)
        VC2.BUILD[cid](subs, r)
    BV.lineup_rig(S, KC)
    BV.concept_macros(KC)
    c01_domed_wordmark(); c01_domed_roundel()
    import photography_v002 as PH
    PH.build()
    bpy.data.objects['C01_ROOT']['v002'] = 'domed AVANTE + roundel (Figma comments 1992886743, 1992886314)'
    for fn in ('variants_stage.py',):
        t = bpy.data.texts.get(fn) or bpy.data.texts.new(fn); t.from_string(open(os.path.join(HERE, fn)).read())
    VS.stage('single', 'C01', bpy.data.objects['CAM_Hero'])


if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    main()
    if '--save' in argv:
        out = os.path.abspath(argv[argv.index('--save') + 1])
        assert not out.endswith(('avante_master_v009.blend', 'avante_variants_master_v001.blend')), 'protected checkpoint'
        bpy.ops.file.make_paths_relative()
        bpy.ops.wm.save_as_mainfile(filepath=out)
        print('VARIANTS_SAVED', out)
