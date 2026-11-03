# D study: inner-wall radius either side of z=185 (inner_width switches to BORE), read-only
import math, importlib.util
spec = importlib.util.spec_from_file_location('bam', '/Users/maxhlomendlini/Documents/Avante/avante/blender/build_avante_master.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
bt = 17.8
for z in (184.0, 184.9, 184.99, 185.0, 185.5):
    S = B.inner_width(z, bt); t = B.roundness(z); cut = B.WALL if z < 185 else None
    r = [B.dome_cut(B.section_r(math.radians(d), S, t), z, cut) if cut is not None else B.section_r(math.radians(d), S, t) for d in (0, 45)]
    print(f'z={z}: inner r(0deg)={r[0]:.3f} r(45deg)={r[1]:.3f}  outer r(0)={B.outer_r(0, z):.3f}')
