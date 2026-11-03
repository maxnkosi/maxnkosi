"""Shared toolkit for the Avante variant concepts (5, 6, 7, 10).

Placement rule (rev D, as Concept 1): one uniform artwork scale, 1 Figma unit = 0.019356 mm (concept bottle
width 4598 u = 89.0 mm), and the concept's shoulder-corner line (frame-relative y 3851) on the max-width line
Z_EDGE. Label artwork is composited 1:1 from the Figma layer exports (0.75 px/u = 38.7 px/mm), never redrawn.

Label coordinates are the v008 true-length wrap: s = arc length round the glass section from the front centre
(mm), v = depth below the wrap origin (mm). surf_xyz(s, v) is the approved glass mapping, so every label
lies exactly on the v009 glass with the adhesive gap.
"""
import bpy, os, math, json
import numpy as np
from mathutils import Vector
import build_avante_master as B

MM = 0.001
U = 0.019356             # mm per Figma unit (rev D)
PXU = 0.75               # export pixels per Figma unit
SHOULDER_REL = 3851.0    # concept shoulder-corner line, frame-relative Figma y
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'textures', 'variants_src')
OUT = os.path.join(HERE, 'textures', 'variants')

NAVY_HEX, GOLD_HEX, CREAM_HEX = '#003653', '#E7C187', '#EDE3D2'


# ----------------------------------------------------------------- mapping
def z_rule(rel_y):
    """Figma frame-relative y → height above the base (mm), rev D rule."""
    return B.Z_EDGE - (rel_y - SHOULDER_REL) * U


def zv(z):
    """height (mm) → wrap depth v used by surf_xyz (inverse of its z mapping, incl. LABEL_DROP)."""
    return B.Z_EDGE - getattr(B, 'LABEL_DROP', 0.0) - z


_ARC = {}
def back_corner_arc(z):
    """arc length (mm) from the front centre to the back corner (theta 45 deg) at height z."""
    k = round(z, 1)
    if k not in _ARC:
        th = np.linspace(-math.pi / 2, math.pi / 4, 1201)
        r = np.array([B.outer_r(float(t), z) for t in th])
        x, y = r * np.cos(th), r * np.sin(th)
        _ARC[k] = float(np.sum(np.hypot(np.diff(x), np.diff(y))))
    return _ARC[k]


def front_y(z):
    """front face plane (mm, negative Y) at height z."""
    return -B.outer_r(-math.pi / 2, z)


# ----------------------------------------------------------------- images (numpy, sRGB-encoded floats)
def load_rgba(path):
    im = bpy.data.images.load(path, check_existing=False)
    w, h = im.size
    a = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1].copy()   # top-down


def save_png(arr, path, mode='RGBA', depth='8'):
    h, w = arr.shape[:2]
    if arr.ndim == 2: arr = np.dstack([arr, arr, arr, np.ones_like(arr)])
    elif arr.shape[2] == 3: arr = np.dstack([arr, np.ones((h, w), np.float32)])
    im = bpy.data.images.new(os.path.basename(path), w, h, alpha=True, float_buffer=(depth == '16'))
    if depth == '16': im.colorspace_settings.name = 'Non-Color'
    im.pixels.foreach_set(np.ascontiguousarray(arr[::-1], np.float32).ravel())
    im.filepath_raw = path; im.file_format = 'PNG'
    st = bpy.context.scene.render.image_settings
    keep = (st.file_format, st.color_mode, st.color_depth)
    st.file_format = 'PNG'; st.color_mode = mode; st.color_depth = depth
    im.save_render(path, scene=bpy.context.scene)
    st.file_format, st.color_mode, st.color_depth = keep   # never leave the render output changed
    bpy.data.images.remove(im)
    return path


def hexrgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


class Concept:
    def __init__(self, cid):
        self.cid = cid
        self.dir = os.path.join(SRC, cid.lower())
        man = json.load(open(os.path.join(self.dir, 'manifest.json')))
        self.frame = man['frame']
        self.nodes = {c['id']: c for c in man['children']}
        os.makedirs(OUT, exist_ok=True)

    def rel(self, n):
        """node box in frame-relative Figma units (x, y, w, h)."""
        c = self.nodes[n]; return (c['x'] - self.frame['x'], c['y'] - self.frame['y'], c['width'], c['height'])

    def png(self, n):
        """Node export as straight RGBA. The Figma exports come flattened on white, so alpha is recovered per
        layer from its single ink colour: a = (white - p).(white - c) / |white - c|^2, colour = c (flat)."""
        if n in getattr(self, 'overrides', {}): return self.overrides[n]
        c = self.nodes[n]
        p = load_rgba(os.path.join(self.dir, c['file']))
        if p[..., 3].min() < 0.99: return p           # a real alpha export
        ink = self.ink(n, p)
        d = 1.0 - p[..., :3]; dc = 1.0 - ink
        a = np.clip((d @ dc) / max(float(dc @ dc), 1e-6), 0, 1).astype(np.float32)
        out = np.empty(p.shape, np.float32); out[..., :3] = ink; out[..., 3] = a
        return out

    def ink(self, n, p=None):
        if n in getattr(self, 'inks', {}): return hexrgb(self.inks[n])
        if p is None: p = load_rgba(os.path.join(self.dir, self.nodes[n]['file']))
        d = (1.0 - p[..., :3]).sum(-1)
        if d.max() < 0.02: return np.ones(3, np.float32)
        sel = p[..., :3][d >= 0.9 * d.max()]
        return np.median(sel, 0).astype(np.float32)

    def composite(self, box, layers, name):
        """Paste node exports 1:1 into a canvas covering `box` (frame-relative units x0, y0, x1, y1).
        layers: list of (node_id, role) with role 'ink' or 'foil' (foil also goes to the foil mask) or
        'emboss' (foil + emboss height). Returns file names (art RGBA, foil mask, emboss height) and the
        canvas size in mm."""
        x0, y0, x1, y1 = box
        W, H = int(round((x1 - x0) * PXU)), int(round((y1 - y0) * PXU))
        art = np.zeros((H, W, 4), np.float32); foil = np.zeros((H, W), np.float32); emb = np.zeros((H, W), np.float32)
        for n, role in layers:
            p = self.png(n); rx, ry, rw, rh = self.rel(n)
            ox, oy = int(round((rx - x0) * PXU)), int(round((ry - y0) * PXU))
            ph, pw = p.shape[:2]
            sx0, sy0 = max(0, -ox), max(0, -oy); dx0, dy0 = max(0, ox), max(0, oy)
            cw, ch = min(pw - sx0, W - dx0), min(ph - sy0, H - dy0)
            if cw <= 0 or ch <= 0: continue
            src = p[sy0:sy0 + ch, sx0:sx0 + cw]; a = src[..., 3:4]
            dst = art[dy0:dy0 + ch, dx0:dx0 + cw]
            out_a = a + dst[..., 3:4] * (1 - a)
            rgb = (src[..., :3] * a + dst[..., :3] * dst[..., 3:4] * (1 - a)) / np.maximum(out_a, 1e-6)
            art[dy0:dy0 + ch, dx0:dx0 + cw] = np.concatenate([rgb, out_a], -1)
            f = foil[dy0:dy0 + ch, dx0:dx0 + cw]
            if role in ('foil', 'emboss'):
                foil[dy0:dy0 + ch, dx0:dx0 + cw] = a[..., 0] + f * (1 - a[..., 0])
            else:  # an ink layer printed over foil knocks the foil out
                foil[dy0:dy0 + ch, dx0:dx0 + cw] = f * (1 - a[..., 0])
            if role == 'emboss':
                e = emb[dy0:dy0 + ch, dx0:dx0 + cw]; emb[dy0:dy0 + ch, dx0:dx0 + cw] = np.maximum(e, a[..., 0])
        files = {'art': f'COLOR__{name}.png', 'foil': f'MASK-FOIL__{name}.png'}
        save_png(art, os.path.join(OUT, files['art']))
        save_png(foil, os.path.join(OUT, files['foil']), 'BW')
        if emb.max() > 0:
            files['emb'] = f'HEIGHT-EMB__{name}.png'
            save_png(round_emboss(emb), os.path.join(OUT, files['emb']), 'BW', '16')
        return files, ((x1 - x0) * U, (y1 - y0) * U)


def blur(a, px):
    """separable box blur ×3 ≈ gaussian, radius px."""
    r = max(1, int(px))
    for _ in range(3):
        for ax in (0, 1):
            c = np.cumsum(np.pad(a, [(r + 1, r) if i == ax else (0, 0) for i in range(2)], mode='edge'), axis=ax)
            a = (np.take(c, range(2 * r + 1, c.shape[ax]), axis=ax) - np.take(c, range(0, c.shape[ax] - 2 * r - 1), axis=ax)) / (2 * r + 1)
    return a


def round_emboss(mask):
    """rounded die shoulder: 0.12 mm blur of the mask, reshaped so tops stay flat (as prep_v005_textures)."""
    h = blur(mask, 0.12 / U * PXU / 2)
    return np.clip((h - 0.15) / 0.7, 0, 1) ** 0.8


# ----------------------------------------------------------------- geometry
def _rr_sdf(u, v, uc, vc, hw, hh, r):
    qx, qy = abs(u - uc) - (hw - r), abs(v - vc) - (hh - r)
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r


def band(name, coll, z_top, z_bot, s_end, art_box_mm, off=B.LABEL_GAP, corner=1.0, ds=0.5, dv=0.5, s_end_hi=None):
    """Wrap band with level top/bottom edges between z_top and z_bot (mm), from -s_end to +s_end of true-length arc.
    art_box_mm = (s0, v0, w, h): artwork rectangle in label (s, v) mm; 'UVMap' maps it to 0..1.
    'BandUV' = (s across the label 0..1, v down the label 0..1) for the level colour bands."""
    v0, v1 = zv(z_top), zv(z_bot); vc, hh = (v0 + v1) / 2, (v1 - v0) / 2
    s_hi = s_end_hi if s_end_hi is not None else s_end
    sc_, hw = (s_hi - s_end) / 2, (s_hi + s_end) / 2
    us = sorted(set([round(x, 3) for x in np.arange(-s_end - ds, s_hi + ds + 1e-9, ds)]))
    vs = sorted(set([round(x, 3) for x in np.arange(v0 - dv, v1 + dv + 1e-9, dv)]))
    s0, a0, aw, ah = art_box_mm
    verts, uvs, faces = B.clipped_grid(us, vs, lambda u, v: _rr_sdf(u, v, sc_, vc, hw, hh, corner),
                                       lambda u, v: B.surf_xyz(u, v, off), lambda u, v: (u, v))
    ob = B.mesh_from(name, verts, faces, coll)
    l1 = ob.data.uv_layers.new(name='UVMap'); l2 = ob.data.uv_layers.new(name='BandUV')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices):
            u, v = uvs[vi]
            l1.data[li].uv = ((u - s0) / aw, 1 - (v - a0) / ah)
            l2.data[li].uv = ((u + s_end) / (s_end + s_hi), 1 - (v - v0) / (v1 - v0))
    B.recalc_normals(ob)
    ps = [p for p in ob.data.polygons if abs(p.center.x) < 0.01]
    if ps and sum(p.normal.y for p in ps) > 0: B.recalc_normals(ob, inside=True)
    return ob


def disc(name, coll, x_mm, z_mm, R, tex_mm, off, n=128, rings=32):
    """flat disc on the front face (follows the face's taper), UV = tex_mm square centred on the disc."""
    def pos(x, z): return ((x_mm + x) * MM, (front_y(z_mm + z) - off) * MM, (z_mm + z) * MM)
    verts, uvs, faces = [pos(0, 0)], [(0.5, 0.5)], []
    for j in range(1, rings + 1):
        rr = R * j / rings
        for i in range(n):
            a = 2 * math.pi * i / n; x, z = rr * math.cos(a), rr * math.sin(a)
            verts.append(pos(x, z)); uvs.append((0.5 + x / tex_mm, 0.5 + z / tex_mm))
    faces += [(0, 1 + i, 1 + (i + 1) % n) for i in range(n)]
    for j in range(rings - 1):
        a0, b0 = 1 + j * n, 1 + (j + 1) * n
        for i in range(n):
            k = (i + 1) % n; faces.append((a0 + i, b0 + i, b0 + k, a0 + k))
    ob = B.mesh_from(name, verts, faces, coll)
    uvl = ob.data.uv_layers.new(name='UVMap')
    for p in ob.data.polygons:
        for li, vi in zip(p.loop_indices, p.vertices): uvl.data[li].uv = uvs[vi]
    B.recalc_normals(ob)
    if ob.data.polygons[0].normal.y > 0: B.recalc_normals(ob, inside=True)
    return ob


def dice(ob, name='emboss_dice'):
    sub = ob.modifiers.new(name, 'SUBSURF'); sub.subdivision_type = 'SIMPLE'; sub.levels = 0; sub.render_levels = 1
    sub.use_adaptive_subdivision = True; sub.adaptive_space = 'PIXEL'; sub.adaptive_pixel_size = 1.0


# ----------------------------------------------------------------- materials
def tex(nt, fn, non_color=False, uv='UVMap', loc=(-900, 0), ext='CLIP'):
    n = nt.nodes.new('ShaderNodeTexImage'); n.location = loc
    n.image = bpy.data.images.load(os.path.join(OUT, fn), check_existing=True)
    if non_color: n.image.colorspace_settings.name = 'Non-Color'
    n.interpolation = 'Cubic'; n.extension = ext
    if uv != 'UVMap':
        m = nt.nodes.new('ShaderNodeUVMap'); m.uv_map = uv; nt.links.new(m.outputs[0], n.inputs['Vector'])
    return n


def band_image(name, stops, h_px=2048):
    """1 x h_px colour column for the level bands: stops = [(v_frac0, v_frac1, hex)], top to bottom."""
    col = np.zeros((h_px, 4, 4), np.float32); col[..., 3] = 1
    for f0, f1, hx in stops:
        col[int(round(f0 * h_px)):int(round(f1 * h_px)), :, :3] = hexrgb(hx)
    fn = f'BAND__{name}.png'; save_png(col, os.path.join(OUT, fn)); return fn


def mat_paper(name, band_fn, files, art_wh, stock='navy', emb_h=B.EMB_H, varnish=None):
    """Variant paper label: SUB-01 felt stock (dyed-through navy, or natural cream), offset ink, FOIL-01 hot foil,
    optional EMB-01 emboss. Same paper relief, ink, foil and mottle as the approved Concept 1 label (mat_label);
    the substrate colour comes from the level bands, the printed art is laid over it 1:1."""
    m, nt, out = B.node_mat(name)
    band = tex(nt, band_fn, uv='BandUV', loc=(-1200, 500), ext='EXTEND')
    art = tex(nt, files['art'], loc=(-1200, 200))
    f = tex(nt, files['foil'], True, loc=(-1200, -200))
    vec = B.uv_mm(nt, *art_wh)
    vor = nt.nodes.new('ShaderNodeTexVoronoi'); vor.inputs['Scale'].default_value = 1 / 0.6
    nt.links.new(vec, vor.inputs['Vector'])
    peck = B.math_node(nt, 'MULTIPLY', B.map_range(nt, vor.outputs['Distance'], 0.0, 0.5), 30e-6)
    body = B.noise_v(nt, vec, 1.2, 3.0)
    fibre = B.noise_v(nt, vec, 1.0, 2.0, stretch=(1 / 1.2, 1 / 0.25))
    relief = B.math_node(nt, 'ADD', peck, B.math_node(nt, 'ADD', B.math_node(nt, 'MULTIPLY', body, 10e-6), B.math_node(nt, 'MULTIPLY', fibre, 6e-6)))
    if stock == 'cream':   # natural felt is livelier than the dyed sheet: deeper felt marks
        relief = B.math_node(nt, 'MULTIPLY', relief, 1.25)
    colour = nt.nodes.new('ShaderNodeMix'); colour.data_type = 'RGBA'
    nt.links.new(art.outputs['Alpha'], colour.inputs['Factor'])
    nt.links.new(band.outputs['Color'], colour.inputs['A']); nt.links.new(art.outputs['Color'], colour.inputs['B'])
    bw = nt.nodes.new('ShaderNodeRGBToBW'); nt.links.new(colour.outputs['Result'], bw.inputs[0])
    bare = B.map_range(nt, bw.outputs[0], 0.30, 0.60, 'LINEAR')     # light areas: cream ink or bare cream stock
    ink_r = B.math_node(nt, 'ADD', 0.62, B.math_node(nt, 'MULTIPLY', B.noise_v(nt, vec, 0.4, 3.0), 0.08))
    rough = nt.nodes.new('ShaderNodeMix'); rough.data_type = 'FLOAT'
    nt.links.new(bare, rough.inputs['Factor']); nt.links.new(ink_r, rough.inputs['A']); rough.inputs['B'].default_value = 0.78
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Distance'].default_value = 1.0
    nt.links.new(relief, bump.inputs['Height'])
    hsv = nt.nodes.new('ShaderNodeHueSaturation'); nt.links.new(colour.outputs['Result'], hsv.inputs['Color'])
    nt.links.new(B.math_node(nt, 'ADD', 0.97, B.math_node(nt, 'MULTIPLY', B.noise_v(nt, vec, 6.0, 2.0), 0.06)), hsv.inputs['Value'])
    paper = B.principled(nt, **{'Sheen Weight': 0.0, 'Specular IOR Level': 0.32})
    nt.links.new(hsv.outputs[0], paper.inputs['Base Color']); nt.links.new(rough.outputs[0], paper.inputs['Roughness'])
    nt.links.new(bump.outputs[0], paper.inputs['Normal'])
    foilb = B.foil_bsdf(nt, vec, pits=body)
    mix = nt.nodes.new('ShaderNodeMixShader'); mix.location = (400, 0)
    nt.links.new(f.outputs['Color'], mix.inputs['Fac'])
    nt.links.new(paper.outputs[0], mix.inputs[1]); nt.links.new(foilb.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    if 'emb' in files:
        e = tex(nt, files['emb'], True, loc=(-1200, -600))
        dsp = nt.nodes.new('ShaderNodeDisplacement'); dsp.space = 'OBJECT'
        dsp.inputs['Midlevel'].default_value = 0.0; dsp.inputs['Scale'].default_value = emb_h * MM
        nt.links.new(e.outputs['Color'], dsp.inputs['Height']); nt.links.new(dsp.outputs[0], out.inputs['Displacement'])
        m.displacement_method = 'BOTH'
    return m


def mat_edges(cid, stock):
    """die-cut core and wetted reverse for the stock colour (navy: the v009 materials; cream: natural felt)."""
    if stock == 'navy': return B.mat_cut_edge(), B.mat_reverse()
    cr = tuple(hexrgb(CREAM_HEX) ** 2.2) + (1.0,)
    e = B.mat_simple(f'M_{cid}_SUB-04_CutEdge_Cream', **{'Base Color': cr, 'Roughness': 0.92})
    r = B.mat_simple(f'M_{cid}_SUB-04_Reverse_Wetted', **{'Base Color': tuple(x * 0.7 for x in cr[:3]) + (1,), 'Roughness': 0.85, 'Specular IOR Level': 0.2})
    return e, r


def paper_shell(ob, mat, cid, stock, thickness=B.LABEL_T):
    edge, rev = mat_edges(cid, stock)
    ob.data.materials.append(mat); ob.data.materials.append(edge); ob.data.materials.append(rev)
    sol = ob.modifiers.new('paper', 'SOLIDIFY'); sol.thickness = thickness * MM; sol.offset = 1.0
    sol.use_rim = True; sol.use_even_offset = True; sol.material_offset = 2; sol.material_offset_rim = 1
    bev = ob.modifiers.new('cut_edge', 'BEVEL'); bev.width = B.LABEL_BEVEL * MM; bev.segments = 2
    bev.limit_method = 'ANGLE'; bev.angle_limit = math.radians(60)
    B.shade_smooth(ob, 30)


def mat_glass_print(name, files, art_wh):
    """PRT-01 precious-metal (bright gold) screen print fired on the glass: a thin, near-mirror gold film
    (roughness 0.10-0.16), very slightly raised at the ink edge, transparent wherever there is no print."""
    m, nt, out = B.node_mat(name)
    art = tex(nt, files['art'], loc=(-900, 200))
    vec = B.uv_mm(nt, *art_wh)
    a = B.map_range(nt, art.outputs['Alpha'], 0.25, 0.65, 'SMOOTHSTEP')   # ink is either there or not
    gold = B.principled(nt, **{'Base Color': (0.93, 0.66, 0.30, 1.0), 'Metallic': 1.0})
    nt.links.new(B.math_node(nt, 'ADD', 0.10, B.math_node(nt, 'MULTIPLY', B.noise_v(nt, vec, 0.25, 2.0), 0.06)), gold.inputs['Roughness'])
    # screen-mesh texture: a 0.06 mm weave of 1.5 um, only visible in macros
    wv = B.math_node(nt, 'MULTIPLY', B.noise_v(nt, vec, 0.06, 1.0), 1.5e-6)
    edge = B.math_node(nt, 'MULTIPLY', B.map_range(nt, art.outputs['Alpha'], 0.0, 1.0), 4e-6)
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Distance'].default_value = 1.0
    nt.links.new(B.math_node(nt, 'ADD', wv, edge), bu.inputs['Height']); nt.links.new(bu.outputs[0], gold.inputs['Normal'])
    tr = nt.nodes.new('ShaderNodeBsdfTransparent')
    mix = nt.nodes.new('ShaderNodeMixShader'); nt.links.new(a, mix.inputs['Fac'])
    nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(gold.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    m.blend_method = 'HASHED' if hasattr(m, 'blend_method') else None
    return m


def mat_metal_medallion(name, files, tex_mm, relief_mm=0.25):
    """MED-01 die-struck metal medallion (0.3 mm brass-tone anodised aluminium seal, self-adhesive):
    satin field with a fine lathe-turned ring texture, polished raised monogram and ring type, relief from the
    artwork. Colour stays the FOIL-01 gold family so it sits with the hot foil."""
    m, nt, out = B.node_mat(name)
    art = tex(nt, files['art'], loc=(-1200, 300))
    h = tex(nt, files['emb'], True, loc=(-1200, -300)) if 'emb' in files else None
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sub = nt.nodes.new('ShaderNodeVectorMath'); sub.operation = 'SUBTRACT'; sub.inputs[1].default_value = (0.5, 0.5, 0)
    ln = nt.nodes.new('ShaderNodeVectorMath'); ln.operation = 'LENGTH'
    nt.links.new(tc.outputs['UV'], sub.inputs[0]); nt.links.new(sub.outputs[0], ln.inputs[0])
    rmm = B.math_node(nt, 'MULTIPLY', ln.outputs['Value'], tex_mm)
    rings = B.math_node(nt, 'SINE', B.math_node(nt, 'MULTIPLY', rmm, 2 * math.pi / 0.035))   # 35 um turning pitch
    hraw = h.outputs['Color'] if h else B.math_node(nt, 'MULTIPLY', 0.0, 0.0)
    rough = B.math_node(nt, 'ADD', 0.30, B.math_node(nt, 'MULTIPLY', hraw, -0.20))           # satin field 0.30, polished tops 0.10
    gold = B.principled(nt, **{'Metallic': 1.0, 'Anisotropic': 0.6})
    # base colour: FOIL gold, recesses a touch deeper (oxide/lacquer pooling)
    cmix = nt.nodes.new('ShaderNodeMix'); cmix.data_type = 'RGBA'
    nt.links.new(hraw, cmix.inputs['Factor'])
    cmix.inputs['A'].default_value = (0.42, 0.26, 0.09, 1); cmix.inputs['B'].default_value = (0.80, 0.55, 0.24, 1)  # Figma coin #825F2B bronze-gold
    nt.links.new(cmix.outputs['Result'], gold.inputs['Base Color']); nt.links.new(rough, gold.inputs['Roughness'])
    # tangent round the centre for the radial anisotropy
    tg = nt.nodes.new('ShaderNodeTangent'); tg.direction_type = 'RADIAL'; tg.axis = 'Y'
    nt.links.new(tg.outputs[0], gold.inputs['Tangent'])
    bu = nt.nodes.new('ShaderNodeBump'); bu.inputs['Distance'].default_value = 1.0
    nt.links.new(B.math_node(nt, 'MULTIPLY', rings, 0.4e-6), bu.inputs['Height']); nt.links.new(bu.outputs[0], gold.inputs['Normal'])
    # outside the struck blank: transparent (the disc mesh is the blank's outline already)
    nt.links.new(gold.outputs[0], out.inputs['Surface'])
    if h:
        dsp = nt.nodes.new('ShaderNodeDisplacement'); dsp.space = 'OBJECT'
        dsp.inputs['Midlevel'].default_value = 0.0; dsp.inputs['Scale'].default_value = relief_mm * MM
        nt.links.new(h.outputs['Color'], dsp.inputs['Height']); nt.links.new(dsp.outputs[0], out.inputs['Displacement'])
        m.displacement_method = 'BOTH'
    return m


def copy_collar(cid, coll, r):
    """Concept 1 neck collar (LBL-NECK-01, same artwork in Concepts 6, 7 and 10) as an independent copy."""
    src = bpy.data.objects['C01_LBL-NECK-01_Collar']
    ob = src.copy(); ob.data = src.data.copy(); ob.name = f'{cid}_LBL-NECK-01_Collar'
    coll.objects.link(ob); ob.parent = r; ob.matrix_parent_inverse.identity()
    for i, s in enumerate(ob.material_slots):
        if s.material and s.material.name.startswith('M_LBL-NECK-01'):
            mm = s.material.copy(); mm.name = f'M_{cid}_LBL-NECK-01_SUB-01_Paper'; ob.data.materials[i] = mm
    return ob


def attach(ob, coll_label, r, foil_set=True):
    ob.parent = r; ob.matrix_parent_inverse.identity()
    if foil_set: bpy.data.collections['LNK_Foil_Labels'].objects.link(ob)
    return ob
