import math, numpy as np
SRC='/Users/maxhlomendlini/Documents/Avante/avante/blender/build_avante_master.py'
code=open(SRC).read().split('# ---------------------------------------------------------------- materials')[0]
G={}; exec(compile(code,'bam','exec'),G)
outer=G['outer_r']
for thd in [0,40.34,45]:
    th=math.radians(thd); print('theta',thd)
    for z in np.arange(156.0,159.01,0.25):
        d=(outer(th,z+0.02)-outer(th,z-0.02))/0.04
        print('   z %.2f r %.3f slope-from-vertical %.2f deg'%(z,outer(th,z),math.degrees(math.atan(-d))))
# Z_HOLD crease at theta 0
for z in [151.5,152,152.4,152.6,153]:
    d=(outer(0,z+0.02)-outer(0,z-0.02))/0.04; print('theta0 z %.1f slope %.2f deg'%(z,math.degrees(math.atan(-d))))
# v006 front silhouette width (max over theta of r cos theta) vs raw2 at z
for z in [150,152.5,155,157.5,160,162.5]:
    w=2*max(outer(math.radians(t/10),z)*math.cos(math.radians(t/10)) for t in range(-450,451))
    print('front W(%.1f)=%.2f'%(z,w))
