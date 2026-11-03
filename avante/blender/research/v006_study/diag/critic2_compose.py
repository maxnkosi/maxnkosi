"""Side-by-side sheets for the critic report. Blender -b --factory-startup --python critic2_compose.py"""
import bpy, numpy as np, os
R = '/Users/maxhlomendlini/Documents/Avante/avante/blender/'
D = R + 'research/v006_study/diag/'
def load(p, crop=None):
    im = bpy.data.images.load(p); w, h = im.size
    a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)[::-1]  # row 0 = top
    if a.shape[2] == 4 and im.channels == 3: a[..., 3] = 1
    a[..., 3] = 1
    if crop: x0, y0, x1, y1 = crop; a = a[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
    return a
def resize(a, H):
    h, w = a.shape[:2]; W = max(1, int(round(w * H / h)))
    ys = np.linspace(0, h - 1, H); xs = np.linspace(0, w - 1, W)
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int); y1 = np.minimum(y0 + 1, h - 1); x1 = np.minimum(x0 + 1, w - 1)
    fy = (ys - y0)[:, None, None]; fx = (xs - x0)[None, :, None]
    return (a[y0][:, x0] * (1 - fy) * (1 - fx) + a[y0][:, x1] * (1 - fy) * fx + a[y1][:, x0] * fy * (1 - fx) + a[y1][:, x1] * fy * fx)
def sheet(name, items, H=900):
    tiles = []
    for p, crop in items:
        if not os.path.exists(p): print('missing', p); continue
        tiles.append(resize(load(p, crop), H)); tiles.append(np.ones((H, 12, 4), np.float32))
    a = np.concatenate(tiles[:-1], 1)
    h, w = a.shape[:2]
    im = bpy.data.images.new(name, w, h, alpha=True); im.pixels = a[::-1].ravel()
    im.filepath_raw = D + name + '.png'; im.file_format = 'PNG'; im.save(); print('SHEET', name, w, h)
REF = R + 'research/references/bottle/'
# front: raw2 (bottle only) | v006 glass (same rig) | prototype glass | prototype full
sheet('critic2_sheet_front', [(REF + 'raw2.png', (0.33, 0.02, 0.67, 0.98)), (D + 'critic2_v006base_glasshero.png', (0.1, 0.08, 0.9, 0.92)),
                              (D + 'critic2_r4_plane_glasshero.png', (0.1, 0.08, 0.9, 0.92)), (D + 'critic2_r4_plane_fullhero.png', (0.1, 0.08, 0.9, 0.92))])
# 3/4: raw5 | v006 render | prototype full | raised-shoulder variant | v005
sheet('critic2_sheet_34', [(REF + 'raw5.png', None), (R + 'renders/v006_threequarter.png', (0.1, 0.08, 0.9, 0.92)),
                           (D + 'critic2_r4_plane_full34.png', (0.1, 0.08, 0.9, 0.92)), (D + 'critic2_r4_high_full34.png', (0.1, 0.08, 0.9, 0.92)),
                           (R + 'renders/v005_threequarter.png', (0.1, 0.08, 0.9, 0.92))])
sheet('critic2_sheet_glass34', [(D + 'critic2_v006base_glass34.png', (0.1, 0.08, 0.9, 0.92)), (D + 'critic2_r4_plane_glass34.png', (0.1, 0.08, 0.9, 0.92)),
                                (D + 'critic2_r4_high_glass34.png', (0.1, 0.08, 0.9, 0.92))])
sheet('critic2_sheet_shoulder', [(D + 'critic2_v006base_glassshoulder.png', None), (D + 'critic2_r3_plane_glassshoulder.png', None), (D + 'critic2_r4_plane_glassshoulder.png', None)], H=720)
sheet('critic2_sheet_label', [(D + 'critic2_v006base_shoulder.png', None), (D + 'critic2_r4_plane_shoulder.png', None), (D + 'critic2_r4_wrap_shoulder.png', None), (D + 'critic2_r4_high_shoulder.png', None)], H=720)
sheet('critic2_zoom_chamfercap', [(D + 'critic2_v006base_glassshoulder.png', (0.25, 0.35, 0.85, 0.8)), (D + 'critic2_r4_plane_glassshoulder.png', (0.25, 0.35, 0.85, 0.8))], H=600)
