# D study: slope discontinuities (creases) in the v006 shoulder construction (read-only)
import math, importlib.util
spec = importlib.util.spec_from_file_location('bam', '/Users/maxhlomendlini/Documents/Avante/avante/blender/build_avante_master.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
e = 1e-4
def kink(f, z, name):
    sl = (f(z) - f(z - e)) / e; sr = (f(z + e) - f(z)) / e
    print(f'{name:38s} z={z:6.1f}: slope below {sl:+.4f}, above {sr:+.4f} -> crease {math.degrees(abs(math.atan(sr) - math.atan(sl))):.2f} deg')
kink(lambda z: B.body_S(z) / 2, B.Z_HOLD, 'body half-width (face plane), Z_HOLD')
kink(B.shoulder_R, B.Z_ARCH_F, 'dome radius, Z_ARCH_F join')
kink(B.shoulder_R, B.Z_ARCH_C, 'dome radius, Z_ARCH_C join')
for z in (145, 150, 155, 157.5, 160, 162.5, 165, 182.5, 185, 188, 190, 215, 216.5):
    f2 = lambda zz: (B.width_at(zz + e) - 2 * B.width_at(zz) + B.width_at(zz - e)) / e / e / 2
    print(f'  pchip curvature jump at knot {z}: d2r below {(B.width_at(z) - 2*B.width_at(z-e) + B.width_at(z-2*e))/e/e/2:+.4f}, above {(B.width_at(z+2*e) - 2*B.width_at(z+e) + B.width_at(z))/e/e/2:+.4f} 1/mm')
