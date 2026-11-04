"""Variants v002: the user's edits to the review-page vectors (Figma pages 05-08, 3 Nov 2026) and the open
Figma comments, applied to Concepts 5, 6, 7 and 10. Concept 1's domed emboss is applied in
build_variants_master_v002.py (its label is the v009 rev D construction).

What changes against v001 (variants_concepts.py stays the v001 record):
- Sources: textures/variants_src_v002/<cid>/manifest.json (make_manifests_v002.py): review-copy bounds,
  re-exports of the layers whose pixels changed, deleted layers dropped, the C10 monogram added.
- Registration is frozen at v001 (same mm per Figma unit and the same label-bottom anchor per concept), so every
  edit moves on the bottle exactly as far as it moved in Figma. Nothing is refitted or stretched; a shorter label
  simply ends higher above the base, as drawn.
- Label geometry from the edited shapes: C06 wrap narrowed to the drawn edges (arc length -41.0 / +40.4 mm from
  the front centre, i.e. it now ends at the front-face edges instead of wrapping to the back corners); C07 and C10
  labels shortened; C10 cream ground #F7F2EC.
- Comments: "Domed emboss" (C05 AVANTE + panel monogram, C06 medallion, C07 AVANTE, C10 medallion): domed
  (pillow) emboss profile instead of the flat-topped die; on medallions the whole disc is domed as well.
  C07 coin "yes solid metal, 2x extrusion": MED-01 solid struck metal confirmed, blank 0.30 -> 0.60 mm.
"""
import bpy, math, os, copy
import numpy as np
import build_avante_master as B
import variants_kit as K
import variants_concepts as V1

K.SRC = os.path.join(K.HERE, 'textures', 'variants_src_v002')
K.OUT = os.path.join(K.HERE, 'textures', 'variants_v002')

NAVY, GOLD, CREAM, BLUE, TINT = V1.NAVY, V1.GOLD, V1.CREAM, V1.BLUE, V1.TINT
CREAM_V2 = '#F7F2EC'            # C10 label ground as edited (was #EEE4D6)
DOME_H = 0.25                   # P domed emboss height on letters/monograms (mm); v001 flat die 0.20
DISC_DOME_H = 0.45              # P whole-disc dome on domed medallions (mm, centre rise)

# frozen v001 registration: (mm per Figma unit, label-bottom anchor y)
FIT_V001 = {'C05': (0.01842456608811749, 11476), 'C06': (0.019356, 11390),
            'C07': (0.017696845344960247, 11390), 'C10': (0.017696845344960247, 11390)}

SPEC = {
    'C05': dict(collar=False, foil='4:18',
                labels=[dict(name='LBL-BAND-01', y=(7319, 8093), stock='navy', stops=[(7319, 8093, NAVY)],
                             layers=[('4:18', 'dome')]),
                        dict(name='LBL-PANEL-01', y=(8193, 11476), stock='navy', stops=[(8193, 11476, NAVY)],
                             layers=[('4:19', 'ink'), ('4:24', 'ink'), ('4:25', 'ink'), ('4:21', 'ink'),
                                     ('4:20', 'dome'), ('4:22', 'ink'), ('4:23', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:26'])], discs=[]),
    'C06': dict(collar=True, foil='4:330',
                labels=[dict(name='LBL-FRONT-02', y=(7845, 10832), stock='navy', x_edges=(397.67, 4601.52),
                             stops=[(7845, 7866, GOLD), (7866, 10332, NAVY), (10332, 10649, CREAM), (10649, 10832, NAVY)],
                             foil_rows=[(7845, 7866)],
                             layers=[('4:321', 'ink'), ('4:329', 'foil'), ('4:330', 'foil'), ('4:327', 'foil'), ('4:328', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:322', '4:331'])],
                discs=[dict(name='LBL-MEDAL-01', group=(1698.85, 6994.55, 1636.44), kind='paper', over_label=True, dome=True,
                            rings=[(818.22, 14.5, GOLD, 'foil'), (755.12, 14.5, TINT, 'ink')], layers=[('4:326', 'dome')])]),
    'C07': dict(collar=True, foil='4:222',
                labels=[dict(name='LBL-FRONT-02', y=(7828, 10660), stock='navy',
                             stops=[(7828, 10237.5, NAVY), (10237.5, 10554, CREAM), (10554, 10660, NAVY)],
                             layers=[('4:213', 'ink'), ('4:214', 'dome'), ('4:221', 'foil'), ('4:222', 'foil'),
                                     ('4:219', 'foil'), ('4:197', 'foil'), ('4:198', 'foil'), ('4:220', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:223'])],
                discs=[dict(name='MED-COIN-01', group=(1466.0, 3916.79, 2058.88), kind='metal', over_label=False, blank_mm=0.60,
                            rings=[(1029.44, 79.3, GOLD, 'emboss60')], layers=[('4:218', 'emboss')])]),
    'C10': dict(collar=True, foil='4:253',
                labels=[dict(name='LBL-FRONT-03', y=(7833, 10721), stock='cream',
                             stops=[(7833, 10287, CREAM_V2), (10287, 10603, '#004060'), (10603, 10721, CREAM_V2)],
                             layers=[('N57:262', 'foil'), ('4:253', 'foil'), ('4:254', 'emboss_ink'), ('4:261', 'ink'),
                                     ('4:262', 'ink'), ('4:259', 'ink'), ('4:260', 'ink')])],
                prints=[dict(name='PRT-GLASS-01', nodes=['4:263'])],
                discs=[dict(name='LBL-MEDAL-01', group=(1485.96, 4047.41, 2019.08), kind='paper', over_label=False, dome=True,
                            rings=[(1009.54, 17.9, GOLD, 'foil'), (931.68, 17.9, TINT, 'ink')], layers=[('4:258', 'dome')])]),
}


# ----------------------------------------------------------------- domed emboss
def distance_px(mask, steps=160):
    """inside distance (px) by repeated 3x3 erosion; cheap and good enough for a height profile."""
    m = mask > 0.5; d = np.zeros(mask.shape, np.float32); cur = m.copy()
    for i in range(steps):
        if not cur.any(): break
        d += cur
        e = cur.copy()
        e[1:, :] &= cur[:-1, :]; e[:-1, :] &= cur[1:, :]; e[:, 1:] &= cur[:, :-1]; e[:, :-1] &= cur[:, 1:]
        cur = e
    return d


def dome_profile(mask):
    """pillow emboss: each stroke rises to a rounded crest (quarter-circle section) instead of a flat top.
    Thin strokes rise less than thick ones, as a sculpted die does."""
    d = distance_px(mask)
    if d.max() <= 0: return mask
    rd = max(2.0, float(np.percentile(d[d > 0], 95)))
    t = np.clip(d / rd, 0, 1)
    h = np.sqrt(1 - (1 - t) ** 2)
    return K.blur(h * (mask > 0.5), 1.5).astype(np.float32)


def composite(self, box, layers, name):
    """variants_kit.Concept.composite with a 'dome' role (foil + domed emboss height)."""
    x0, y0, x1, y1 = box
    W, H = int(round((x1 - x0) * K.PXU)), int(round((y1 - y0) * K.PXU))
    art = np.zeros((H, W, 4), np.float32); foil = np.zeros((H, W), np.float32)
    emb = np.zeros((H, W), np.float32); dome = np.zeros((H, W), np.float32)
    for n, role in layers:
        p = self.png(n); rx, ry, rw, rh = self.rel(n)
        ox, oy = int(round((rx - x0) * K.PXU)), int(round((ry - y0) * K.PXU))
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
        if role in ('foil', 'emboss', 'dome'):
            foil[dy0:dy0 + ch, dx0:dx0 + cw] = a[..., 0] + f * (1 - a[..., 0])
        else:
            foil[dy0:dy0 + ch, dx0:dx0 + cw] = f * (1 - a[..., 0])
        tgt = emb if role == 'emboss' else dome if role == 'dome' else None
        if tgt is not None:
            e = tgt[dy0:dy0 + ch, dx0:dx0 + cw]; tgt[dy0:dy0 + ch, dx0:dx0 + cw] = np.maximum(e, a[..., 0])
    files = {'art': f'COLOR__{name}.png', 'foil': f'MASK-FOIL__{name}.png'}
    K.save_png(art, os.path.join(K.OUT, files['art']))
    K.save_png(foil, os.path.join(K.OUT, files['foil']), 'BW')
    if emb.max() > 0 or dome.max() > 0:
        # height in mm: flat die EMB-01 (0.20) and/or domed emboss (0.25), optionally on a domed disc
        hmm = np.zeros((H, W), np.float32)
        if emb.max() > 0: hmm = np.maximum(hmm, K.round_emboss(emb) * B.EMB_H)
        if dome.max() > 0: hmm = np.maximum(hmm, dome_profile(dome) * DOME_H)
        if getattr(self, 'disc_dome', False):   # whole medallion domed: spherical cap under the relief
            yy, xx = np.mgrid[0:H, 0:W] + 0.5
            rr = np.hypot(xx - W / 2, yy - H / 2) / (min(W, H) / 2)
            hmm = np.clip(1 - rr ** 2, 0, 1) * DISC_DOME_H + hmm * (rr < 1)
        scale = float(hmm.max())
        files['emb'] = f'HEIGHT-EMB__{name}.png'
        EMB_SCALE[files['emb']] = scale
        K.save_png((hmm / scale).astype(np.float32), os.path.join(K.OUT, files['emb']), 'BW', '16')
        print('AVANTE_V2 height', name, 'max', round(scale, 3), 'mm', 'dome' if dome.max() > 0 else '', 'disc' if getattr(self, 'disc_dome', False) else '')
    return files, ((x1 - x0) * K.U, (y1 - y0) * K.U)


EMB_SCALE = {}   # height-map file -> mm at 1.0


K.Concept.composite = composite


class FrozenFit:
    """v001 registration kept: same scale and the same anchor, so edits move 1:1 on the bottle."""
    def __init__(self, sp):
        self.s, self.bottom = sp['_fit']
    def z(self, y): return V1.Z_BOT + (self.bottom - y) * self.s
    def x(self, xr): return (xr - V1.CX) * self.s


def arc_to_x(x_mm, z):
    """true-length arc (mm) from the front centre to the surface point whose x is x_mm (one side) at height z."""
    th = np.linspace(-math.pi / 2, math.pi / 4, 2401)
    r = np.array([B.outer_r(float(t), z) for t in th])
    x, y = r * np.cos(th), r * np.sin(th)
    s = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
    i = int(np.argmax(x >= abs(x_mm))) if (x >= abs(x_mm)).any() else len(x) - 1
    return float(s[i])


_band = K.band
def band_v2(name, coll, z_top, z_bot, s_end, art_box_mm, **kw):
    ed = getattr(K, '_x_edges', None)
    if ed is not None and name.endswith(K._x_edges_name):
        # the artwork is laid on the glass by arc length (art x -> s, variants_kit.band art_box), so the drawn
        # label edges are arc lengths too: the label stops where its artwork stops
        lo, hi = -ed[0], ed[1]
        print('AVANTE_V2 narrowed wrap', name, 'edges at arc', round(-lo, 2), round(hi, 2), 'mm (was to the back corners)')
        return _band(name, coll, z_top, z_bot, lo, art_box_mm, s_end_hi=hi, **kw)
    return _band(name, coll, z_top, z_bot, s_end, art_box_mm, **kw)
K.band = band_v2


def build_concept(cid, subs, r):
    sp = copy.deepcopy(SPEC[cid]); sp['_fit'] = FIT_V001[cid]
    sp['top'] = 0; sp['bottom'] = FIT_V001[cid][1]
    V1.SPEC[cid] = sp
    V1.Fit = FrozenFit
    s = FIT_V001[cid][0]
    K._x_edges = None
    for L in sp['labels']:
        if 'x_edges' in L:
            K._x_edges = tuple((e - V1.CX) * s for e in L['x_edges']); K._x_edges_name = L['name']
    # medallion dome and coin blank thickness: hook disc/material creation
    _mat_paper, _mat_med, _disc = K.mat_paper, K.mat_metal_medallion, K.disc
    domed = {f'{cid}_{D["name"]}' for D in sp['discs'] if D.get('dome')}
    blank = {f'{cid}_{D["name"]}': D.get('blank_mm') for D in sp['discs'] if D.get('blank_mm')}
    _comp = K.Concept.composite
    def comp(self, box, layers, name):
        self.disc_dome = name in domed
        return _comp(self, box, layers, name)
    K.Concept.composite = comp
    def mat_paper(name, band_fn, files, art_wh, stock='navy', emb_h=B.EMB_H, varnish=None):
        if 'emb' in files: emb_h = EMB_SCALE.get(files['emb'], emb_h)
        return _mat_paper(name, band_fn, files, art_wh, stock=stock, emb_h=emb_h, varnish=varnish)
    def mat_med(name, files, tex_mm, relief_mm=0.25):
        if 'emb' in files: relief_mm = EMB_SCALE.get(files['emb'], B.EMB_H) * (0.25 / B.EMB_H)   # v001 coin relief 0.25
        return _mat_med(name, files, tex_mm, relief_mm)
    K.mat_metal_medallion = mat_med
    K.mat_paper = mat_paper
    try:
        V1.build_concept(cid, subs, r)
    finally:
        K.mat_paper, K.Concept.composite, K.mat_metal_medallion = _mat_paper, _comp, _mat_med
    for name, t in blank.items():
        ob = bpy.data.objects[name]; ob.modifiers['blank'].thickness = t * B.MM
        r['coin_blank_mm'] = t
    r['v002'] = 1


BUILD = {cid: (lambda subs, r, cid=cid: build_concept(cid, subs, r)) for cid in SPEC}
