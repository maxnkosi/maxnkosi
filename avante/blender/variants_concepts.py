"""Concept assemblies 5, 6, 7 and 10, built from the Figma layer exports (textures/variants_src).

Each concept is one uniform similarity transform from its Figma frame to the v009 bottle (artwork never
stretched), chosen per concept so that its whole design (top element to label bottom) fits the flat glass:
  - label bottom on Z_BOT = 15 mm (clear of the heel fillet, which ends at about 14 mm);
  - top element at most Z_TOP = 153 mm (1 mm under the arch onset at the panel centre, 154.05 mm);
  - scale = min(rev D 0.019356 mm/u, fit). Concept 6 keeps rev D exactly; Concept 5 is 95.2 %, Concepts 7
    and 10 are 91.4 % (their medallion and copy are taller than the Imperial's flat face).
Physical interpretation of each Figma element (see README, "Variants v001"):
  navy / cream wrap labels   SUB-01 felt (dyed-through navy; natural cream for Concept 10), offset ink,
                             FOIL-01 hot foil, EMB-01 emboss on wordmarks and monograms, like Concept 1
  gold art on bare glass     PRT-01 bright-gold precious-metal screen print, fired on
  navy medallions (6, 10)    SUB-01 navy paper roundel, foil ring + embossed foil monogram
  bronze coin (7)            MED-01 die-struck metal seal, polished relief on a satin turned field
  neck                       capsule as v009 (all navy, no gold pinline, as the four Figma concepts);
                             collar flag LBL-NECK-01 (identical artwork) on Concepts 6, 7, 10
"""
import bpy, math
import numpy as np
import build_avante_master as B
import variants_kit as K

Z_BOT, Z_TOP = 15.0, 153.0
CX = 218 + 4597 / 2          # concept bottle centre line (frame-relative u)
NAVY, GOLD, CREAM_INK, CREAM, BLUE, TINT = '#003653', '#E7C187', '#FFE2B8', '#EEE4D6', '#286789', '#184868'

SPEC = {
    'C05': dict(top=3986, bottom=11476, collar=False, foil='4:18',
                labels=[dict(name='LBL-BAND-01', y=(7319, 8093), stock='navy', stops=[(7319, 8093, NAVY)],
                             layers=[('4:18', 'emboss')]),
                        dict(name='LBL-PANEL-01', y=(8193, 11476), stock='navy', stops=[(8193, 11476, NAVY)],
                             layers=[('4:19', 'ink'), ('4:24', 'ink'), ('4:25', 'ink'), ('4:21', 'ink'),
                                     ('4:20', 'emboss'), ('4:22', 'ink'), ('4:23', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:26'])], discs=[]),
    'C06': dict(top=4468, bottom=11390, collar=True, foil='4:330',
                labels=[dict(name='LBL-FRONT-02', y=(7845, 11390), stock='navy',
                             stops=[(7845, 7866, GOLD), (7866, 10916, NAVY), (10916, 11232, CREAM), (11232, 11390, NAVY)],
                             foil_rows=[(7845, 7866)],
                             layers=[('4:321', 'ink'), ('4:329', 'foil'), ('4:330', 'foil'), ('4:327', 'foil'), ('4:328', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:322', '4:331'])],
                discs=[dict(name='LBL-MEDAL-01', group=(1388, 6684, 2258), kind='paper', over_label=True,
                            rings=[(1129, 20, GOLD, 'foil'), (1042, 20, TINT, 'ink')], layers=[('4:326', 'emboss')])]),
    'C07': dict(top=3592, bottom=11390, collar=True, foil='4:222',
                labels=[dict(name='LBL-FRONT-02', y=(7835, 11390), stock='navy',
                             stops=[(7835, 10916, NAVY), (10916, 11232, CREAM), (11232, 11390, NAVY)],
                             layers=[('4:213', 'ink'), ('4:214', 'emboss'), ('4:221', 'foil'), ('4:222', 'foil'),
                                     ('4:219', 'foil'), ('4:197', 'foil'), ('4:198', 'foil'), ('4:220', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:223'])],
                discs=[dict(name='MED-COIN-01', group=(1367, 3592, 2258), kind='metal', over_label=False,
                            rings=[(1129, 87, GOLD, 'emboss60')], layers=[('4:218', 'emboss')])]),
    'C10': dict(top=3592, bottom=11390, collar=True, foil='4:253',
                labels=[dict(name='LBL-FRONT-03', y=(7835, 11390), stock='cream',
                             stops=[(7835, 10916, CREAM), (10916, 11232, '#004060'), (11232, 11390, CREAM)],
                             layers=[('4:254', 'emboss_ink'), ('4:253', 'foil'), ('4:261', 'ink'), ('4:262', 'ink'),
                                     ('4:259', 'ink'), ('4:237', 'foil'), ('4:238', 'foil'), ('4:260', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:263'])],
                discs=[dict(name='LBL-MEDAL-01', group=(1367, 3592, 2258), kind='paper', over_label=False,
                            rings=[(1129, 20, GOLD, 'foil'), (1042, 20, TINT, 'ink')], layers=[('4:258', 'emboss')])]),
}


def resize(a, w, h):
    """bilinear resize of an (H, W, C) array."""
    H, W = a.shape[:2]
    ys = np.clip((np.arange(h) + 0.5) * H / h - 0.5, 0, H - 1); xs = np.clip((np.arange(w) + 0.5) * W / w - 0.5, 0, W - 1)
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int); y1 = np.minimum(y0 + 1, H - 1); x1 = np.minimum(x0 + 1, W - 1)
    fy = (ys - y0)[:, None, None]; fx = (xs - x0)[None, :, None]
    return (a[y0][:, x0] * (1 - fy) * (1 - fx) + a[y0][:, x1] * (1 - fy) * fx + a[y1][:, x0] * fy * (1 - fx) + a[y1][:, x1] * fy * fx).astype(np.float32)


def ring_layer(c, nid, cx, cy, r_out, width, colour, alpha=1.0):
    """synthetic ring (a Figma stroke lost in the flattened export), r_out and width in Figma units."""
    s = int(round(2 * r_out * K.PXU)); yy, xx = np.mgrid[0:s, 0:s] + 0.5
    rr = np.hypot(xx - s / 2, yy - s / 2) / K.PXU
    a = np.clip(r_out - rr, 0, 1) * np.clip(rr - (r_out - width), 0, 1) * alpha
    arr = np.zeros((s, s, 4), np.float32); arr[..., :3] = K.hexrgb(colour); arr[..., 3] = a
    c.overrides[nid] = arr
    c.nodes[nid] = dict(x=c.frame['x'] + cx - r_out, y=c.frame['y'] + cy - r_out, width=2 * r_out, height=2 * r_out)


class Fit:
    def __init__(self, sp):
        self.bottom = sp['bottom']
        self.s = min(K.U, (Z_TOP - Z_BOT) / (sp['bottom'] - sp['top']))
    def z(self, y): return Z_BOT + (self.bottom - y) * self.s
    def x(self, xr): return (xr - CX) * self.s


def build_concept(cid, subs, r):
    sp = SPEC[cid]; c = K.Concept(cid); c.overrides = {}; f = Fit(sp)
    K.U_SAVE = K.U; K.U = f.s          # composite() reports mm with the concept's scale
    try:
        if cid == 'C05':  # tonal roundel behind the V.S.O.P block: white at low opacity in Figma, the same
            # monogram as 4:20 (the white export carries no shape), so 4:20's shape at 4:19's size, as tint ink
            p = c.png('4:20'); n19 = c.nodes['4:19']
            a = resize(p, n19['png_w'], n19['png_h']); a[..., :3] = K.hexrgb(TINT); c.overrides['4:19'] = a
        r['scale_mm_per_u'] = f.s; r['scale_vs_revD'] = round(f.s / K.U_SAVE, 4)
        emblems, made, prints = [], [], []
        # ---- wrap labels
        for L in sp['labels']:
            y0, y1 = L['y']; z0, z1 = f.z(y0), f.z(y1)
            roles = [(n, {'emboss_ink': 'ink'}.get(ro, ro)) for n, ro in L['layers']]
            files, wh = c.composite((0, y0, 4969, y1), roles, f'{cid}_{L["name"]}')
            embn = [n for n, ro in L['layers'] if ro == 'emboss_ink']
            if embn:   # blind emboss on ink (Concept 10 navy wordmark): emboss height without foil
                files2, _ = c.composite((0, y0, 4969, y1), [(n, 'emboss') for n in embn], f'{cid}_{L["name"]}_EMBINK')
                files['emb'] = files2['emb']
            stops = [((a - y0) / (y1 - y0), (b - y0) / (y1 - y0), hx) for a, b, hx in L['stops']]
            band_fn = K.band_image(f'{cid}_{L["name"]}', stops)
            if L.get('foil_rows'):   # full-width foil rule: merge into the foil mask across the whole wrap
                files['foil_rows'] = [((a - y0) / (y1 - y0), (b - y0) / (y1 - y0)) for a, b in L['foil_rows']]
            s_end = K.back_corner_arc(z1) - 6.0
            art_box = (f.x(0), K.zv(z0), 4969 * f.s, (y1 - y0) * f.s)
            ob = K.band(f'{cid}_{L["name"]}', subs['Labels'], z0, z1, s_end, art_box)
            m = K.mat_paper(f'M_{cid}_{L["name"]}_SUB-01_Paper', band_fn, files, (art_box[2], art_box[3]), stock=L['stock'])
            if L.get('foil_rows'): add_foil_rows(m, files['foil_rows'])
            K.paper_shell(ob, m, cid, L['stock'])
            if 'emb' in files: K.dice(ob)
            K.attach(ob, subs['Labels'], r); made.append(ob.name)
        # ---- prints on glass
        for P in sp['prints']:
            bx = [c.rel(n) for n in P['nodes']]; mg = 40
            x0 = min(b[0] for b in bx) - mg; y0 = min(b[1] for b in bx) - mg
            x1 = max(b[0] + b[2] for b in bx) + mg; y1 = max(b[1] + b[3] for b in bx) + mg
            files, wh = c.composite((x0, y0, x1, y1), [(n, 'ink') for n in P['nodes']], f'{cid}_{P["name"]}')
            z0, z1 = f.z(y0), f.z(y1)
            s_end = max(abs(f.x(x0)), abs(f.x(x1)))
            art_box = (f.x(x0), K.zv(z0), (x1 - x0) * f.s, (y1 - y0) * f.s)
            ob = K.band(f'{cid}_{P["name"]}', subs['Labels'], z0, z1, s_end, art_box, off=0.004, corner=0.5)
            ob.data.materials.append(K.mat_glass_print(f'M_{cid}_{P["name"]}_PRT-01_GoldPrint', files, (art_box[2], art_box[3])))
            prints.append(ob.name); r['print_z'] = (z0 + z1) / 2 * B.MM
            B.shade_smooth(ob, 30)
            K.attach(ob, subs['Labels'], r); made.append(ob.name)
        # ---- medallions
        for D in sp['discs']:
            gx, gy, gd = D['group']; R_u = gd / 2; cxr, cyr = gx + R_u, gy + R_u
            layers = []
            for i, (ro_u, w_u, col, role) in enumerate(D['rings']):
                nid = f'ring{i}'
                ring_layer(c, nid, cxr, cyr, ro_u, w_u, col, 0.6 if role == 'emboss60' else 1.0)
                layers.append((nid, 'emboss' if role.startswith('emboss') else role))
            layers += D['layers']
            files, wh = c.composite((cxr - R_u, cyr - R_u, cxr + R_u, cyr + R_u), layers, f'{cid}_{D["name"]}')
            R_mm, tex_mm = R_u * f.s, gd * f.s
            zc = f.z(cyr)
            if D['kind'] == 'paper':
                off = B.LABEL_GAP + (B.LABEL_T + 0.004 if D['over_label'] else 0.0)
                ob = K.disc(f'{cid}_{D["name"]}', subs['Emblems'], f.x(cxr), zc, R_mm, tex_mm, off)
                bu = ob.data.uv_layers.new(name='BandUV')
                for i in range(len(bu.data)): bu.data[i].uv = ob.data.uv_layers['UVMap'].data[i].uv
                band_fn = K.band_image(f'{cid}_{D["name"]}', [(0, 1, NAVY)], 16)
                m = K.mat_paper(f'M_{cid}_{D["name"]}_SUB-01_Paper', band_fn, files, (tex_mm, tex_mm), stock='navy')
                K.paper_shell(ob, m, cid, 'navy')
            else:
                ob = K.disc(f'{cid}_{D["name"]}', subs['Emblems'], f.x(cxr), zc, R_mm, tex_mm, 0.004)
                ob.data.materials.append(K.mat_metal_medallion(f'M_{cid}_{D["name"]}_MED-01_StruckMetal', files, tex_mm))
                edge = B.mat_simple(f'M_{cid}_MED-01_Edge', **{'Base Color': (0.80, 0.56, 0.25, 1), 'Metallic': 1.0, 'Roughness': 0.3})
                ob.data.materials.append(edge)
                sol = ob.modifiers.new('blank', 'SOLIDIFY'); sol.thickness = 0.30 * B.MM; sol.offset = 1.0
                sol.use_rim = True; sol.use_even_offset = True; sol.material_offset_rim = 1
                bev = ob.modifiers.new('rolled_edge', 'BEVEL'); bev.width = 0.12 * B.MM; bev.segments = 3
                bev.limit_method = 'ANGLE'; bev.angle_limit = math.radians(50)
                B.shade_smooth(ob, 30)
            K.dice(ob)
            K.attach(ob, subs['Emblems'], r); emblems.append(ob.name)
            r['emblem_z'] = zc * B.MM
        # ---- neck
        if sp['collar']:
            col = K.copy_collar(cid, subs['Labels'], r); bpy.data.collections['LNK_Foil_Labels'].objects.link(col)
        cap = bpy.data.objects[f'{cid}_SLV-CAP-01_Capsule']   # all navy (no gold pinline in these concepts)
        cap.material_slots[1].link = 'OBJECT'; cap.material_slots[1].material = bpy.data.materials['M_SUB-03_ShrinkFilm_INK-01-S']
        fb = c.rel(sp['foil']); r['foil_z'] = f.z(fb[1] + fb[3] / 2) * B.MM
        r['emblems'] = ','.join(emblems); r['prints'] = ','.join(prints)
        print('AVANTE_CONCEPT', cid, 'scale', round(f.s, 6), 'vs revD', r['scale_vs_revD'], made + emblems)
    finally:
        K.U = K.U_SAVE


def add_foil_rows(m, rows):
    """full-wrap foil rule (Concept 6's gold line along the label top): foil = max(art foil, row band in BandUV)."""
    nt = m.node_tree
    mix = [n for n in nt.nodes if n.bl_idname == 'ShaderNodeMixShader'][0]
    link = mix.inputs['Fac'].links[0]; src = link.from_socket
    uvm = nt.nodes.new('ShaderNodeUVMap'); uvm.uv_map = 'BandUV'
    sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(uvm.outputs[0], sep.inputs[0])
    acc = src
    for a, b in rows:   # BandUV v runs 1 (top) to 0 (bottom)
        lo, hi = 1 - b, 1 - a
        g1 = B.math_node(nt, 'GREATER_THAN', sep.outputs['Y'], lo); g2 = B.math_node(nt, 'LESS_THAN', sep.outputs['Y'], hi)
        acc = B.math_node(nt, 'MAXIMUM', acc, B.math_node(nt, 'MULTIPLY', g1, g2))
    nt.links.new(acc, mix.inputs['Fac'])


BUILD = {cid: (lambda subs, r, cid=cid: build_concept(cid, subs, r)) for cid in SPEC}
