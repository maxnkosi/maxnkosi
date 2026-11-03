"""v005 texture prep. Originals in textures/ are never modified; new files are written next to them.

  blender -b --factory-startup --python prep_v005_textures.py

1. COLOR__LBL-FRONT-01_v005.png  the tone-on-tone bird/spear graphic (#286789) toned down to
   about dL* 7 above the navy flood (#003653), same hue. Anti-aliased edges are remapped along the
   navy-to-graphic line, so the artwork's shape and position are unchanged. (Client decision 3 Nov 2026.)
2. HEIGHT-EMB-01__LBL-FRONT-01.exr  rounded emboss profile from MASK-EMB-01 at 2x (40 px/mm):
   Gaussian blur sigma 0.15 mm, then smootherstep from the mask edge (b = 0.5) to b = 0.97, so the
   foil edge sits at the foot of the shoulder and thin strokes emboss lower (line-width rule).
"""
import bpy, numpy as np, os

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, 'textures')
PX_PER_MM = 20.0  # front artwork: 4870 px over 243.469 mm

def load(name):
    im = bpy.data.images.load(os.path.join(T, name)); im.colorspace_settings.name = 'Non-Color'
    w, h = im.size; a = np.empty(w * h * 4, np.float32); im.pixels.foreach_get(a)
    return a.reshape(h, w, 4), w, h

def to_lin(c): return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def lstar(rgb):  # sRGB 0-1 -> CIE L*
    Y = to_lin(np.asarray(rgb)) @ np.array([0.2126, 0.7152, 0.0722])
    return 116 * np.cbrt(Y) - 16 if Y > 0.008856 else 903.3 * Y

# ---- 1. graphic tone-down
a, w, h = load('COLOR__LBL-FRONT-01.png')
navy = np.array([0x00, 0x36, 0x53]) / 255.0; graphic = np.array([0x28, 0x67, 0x89]) / 255.0
d = graphic - navy; L0 = lstar(navy)
lo, hi = 0.0, 1.0  # solve k so the new graphic sits dL* = 7 above navy
for _ in range(40):
    k = (lo + hi) / 2
    if lstar(navy + k * d) - L0 > 7.0: hi = k
    else: lo = k
k = (lo + hi) / 2
rgb = a[..., :3]
t = np.clip(((rgb - navy) @ d) / (d @ d), 0.0, 1.0)
off = np.linalg.norm(rgb - (navy + t[..., None] * d), axis=-1)
on_line = (off < 6 / 255.0) & (t > 0.0)
rgb[on_line] = navy + (k * t[on_line])[..., None] * d
out = bpy.data.images.new('COLOR_v005', w, h, alpha=True); out.colorspace_settings.name = 'sRGB'
out.pixels.foreach_set(a.reshape(-1))
out.filepath_raw = os.path.join(T, 'COLOR__LBL-FRONT-01_v005.png'); out.file_format = 'PNG'; out.save()
print('PREP graphic k=%.3f new=#%02X%02X%02X dL*=%.2f pixels=%d' % ((k,) + tuple(np.round((navy + k * d) * 255).astype(int)) + (lstar(navy + k * d) - L0, int(on_line.sum()))))

# ---- 2. rounded emboss height
m, w, h = load('MASK-EMB-01__LBL-FRONT-01.png')
m = m[..., 0].astype(np.float32)
m = np.repeat(np.repeat(m, 2, axis=0), 2, axis=1)  # 40 px/mm
sigma_px = 0.15 * PX_PER_MM * 2
box = int(round(np.sqrt(12 * sigma_px ** 2 / 3 + 1))) | 1  # three box passes ~ Gaussian

def box_blur(x, r, axis):
    pad = [(0, 0)] * x.ndim; pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(x, pad, mode='edge'), axis=axis, dtype=np.float64)
    n = x.shape[axis]
    hi_ = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis); lo_ = np.take(c, np.arange(0, n), axis=axis)
    return ((hi_ - lo_) / (2 * r + 1)).astype(np.float32)

b = m
for _ in range(3):
    b = box_blur(box_blur(b, box // 2, 0), box // 2, 1)
s = np.clip((b - 0.5) / (0.97 - 0.5), 0.0, 1.0)
hgt = s * s * s * (s * (s * 6 - 15) + 10)  # smootherstep
H, W = hgt.shape
out = bpy.data.images.new('HEIGHT_v005', W, H, alpha=False, float_buffer=True); out.colorspace_settings.name = 'Non-Color'
px = np.ones((H, W, 4), np.float32); px[..., 0] = px[..., 1] = px[..., 2] = hgt
out.pixels.foreach_set(px.reshape(-1))
ims = bpy.context.scene.render.image_settings  # single-channel half-float EXR, ZIP: a few MB, not 470
ims.file_format = 'OPEN_EXR'; ims.color_mode = 'BW'; ims.color_depth = '16'; ims.exr_codec = 'ZIP'
out.save_render(os.path.join(T, 'HEIGHT-EMB-01__LBL-FRONT-01.exr'), scene=bpy.context.scene)
print('PREP height %dx%d box=%d max=%.3f' % (W, H, box, float(hgt.max())))
