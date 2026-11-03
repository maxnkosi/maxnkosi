# D study: r(z) and curvature along the face centre / chamfer centre through the dome (read-only)
import math, importlib.util
spec = importlib.util.spec_from_file_location('bam', '/Users/maxhlomendlini/Documents/Avante/avante/blender/build_avante_master.py')
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
def R3(p0, p1, p2):
    a, b, c = math.dist(p0, p1), math.dist(p1, p2), math.dist(p0, p2)
    ar = abs((p1[0]-p0[0])*(p2[1]-p0[1]) - (p1[1]-p0[1])*(p2[0]-p0[0]))
    return a*b*c/(2*ar) if ar > 1e-14 else 1e9
for deg in (0, 45):
    th = math.radians(deg); h = 0.05
    print('theta', deg, ' z  r_out  face_r  dome_R  curvR(h=0.05)  curvR(h=0.5)')
    for i in range(0, 81):
        z = 136 + 0.5 * i
        f = lambda zz: (zz, B.outer_r(th, zz))
        print(f'{z:6.1f} {B.outer_r(th, z):7.3f} {B.section_r(th, B.body_S(z), B.roundness(z)):7.3f} {B.shoulder_R(z):7.3f} '
              f'{R3(f(z-h), f(z), f(z+h)):8.2f} {R3(f(z-0.5), f(z), f(z+0.5)):8.2f}')
