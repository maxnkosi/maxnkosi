import math, numpy as np
SRC='/Users/maxhlomendlini/Documents/Avante/avante/blender/build_avante_master.py'
code=open(SRC).read().split('# ---------------------------------------------------------------- materials')[0]
G={}; exec(compile(code,'bam','exec'),G)
outer=G['outer_r']; sec=G['section_r']; bS=G['body_S']; rnd=G['roundness']
z=np.arange(130,215,0.05)
for lab,f in [('v006 theta0',lambda zz: outer(0.0,zz)),('v005 (PROFILE/2)',lambda zz: G['width_at'](zz)/2)]:
    R=np.array([f(v) for v in z])
    def fl(m): A=np.vstack([z[m],np.ones(m.sum())]).T; return np.linalg.lstsq(A,R[m],rcond=None)[0]
    b1=fl((z>142)&(z<150)); b2=fl((R>0.6*44.5)&(R<0.85*44.5)&(z>150)&(z<185)); b3=fl((z>190)&(z<210))
    def inter(p,q): zz=(q[1]-p[1])/(p[0]-q[0]); return np.array([zz,p[0]*zz+p[1]])
    P=np.stack([z,R],1)
    for (p,q,nm) in [(b1,b2,'knuckle'),(b2,b3,'neck')]:
        V=inter(p,q); T=abs(math.atan(q[0])-math.atan(p[0])); g=np.min(np.linalg.norm(P-V,axis=1))
        print('%s %s vertex z %.1f r %.2f turn %.1f gap %.2f -> R %.1f'%(lab,nm,V[0],V[1],math.degrees(T),g,g/(1/math.cos(T/2)-1)))
    print('   cone angle %.1f deg from vertical'%math.degrees(math.atan(-b2[0])))
