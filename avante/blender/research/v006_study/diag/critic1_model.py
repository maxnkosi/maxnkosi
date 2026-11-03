# critic1: analytic checks on the v006 builder functions + softmin->radius conversion. Headless Blender.
import math, numpy as np
SRC='/Users/maxhlomendlini/Documents/Avante/avante/blender/build_avante_master.py'
code=open(SRC).read().split('# ---------------------------------------------------------------- materials')[0]
G={}; exec(compile(code,'bam','exec'),G)
softmin=G['softmin']
def sm(a,b,k):  # stable
    m=min(a,b); return m-k*math.log(math.exp(-(a-m)/k)+math.exp(-(b-m)/k))
print('== 1. softmin k -> equivalent fillet radius, generic 2D corner of turn angle T between two straight lines')
def corner_metrics(T_deg,k,ref_radial_offset_deg=0.0):
    # Lines in local frame: polyline vertex at origin, line1 along -x (normal +y), line2 at turn T. Use a polar
    # parametrisation about a far centre so softmin acts "radially" like in the builder: centre at distance D along the
    # inward direction making angle phi to the bisector (phi = ref_radial_offset_deg).
    T=math.radians(T_deg); D=60.0; phi=math.radians(ref_radial_offset_deg)
    # outward normals of the two lines
    n1=np.array([math.sin(-T/2),math.cos(-T/2)]); n2=np.array([math.sin(T/2),math.cos(T/2)])
    # centre (origin of rays): vertex - D*u where u = outward bisector rotated by phi
    u=np.array([math.sin(phi),math.cos(phi)]); C=-D*u
    p1=-(C@n1); p2=-(C@n2)   # distances of the lines from C (lines pass through vertex at origin)
    ths=np.linspace(-0.25,0.25,200001)   # ray angles around u
    pts=[];
    for th in ths[::1]:
        pass
    ang=np.arctan2(u[0],u[1])
    a=ang+ths
    dirs=np.stack([np.sin(a),np.cos(a)],1)
    r1=p1/(dirs@n1); r2=p2/(dirs@n2)
    r1[r1<0]=1e9; r2[r2<0]=1e9
    m=np.minimum(r1,r2); r=m-k*np.log(np.exp(-(r1-m)/k)+np.exp(-(r2-m)/k))
    P=C+dirs*r[:,None]
    d=np.diff(P,axis=0); s=np.concatenate([[0],np.cumsum(np.hypot(d[:,0],d[:,1]))])
    tang=np.arctan2(d[:,1],d[:,0]); tang=np.unwrap(tang)
    ss=(s[1:]+s[:-1])/2
    curv=np.abs(np.gradient(tang,ss))
    Rmin=1/curv.max()
    turn=abs(tang[-1]-tang[0])
    # turn-spread: arc length between 5% and 95% of the turn
    tt=np.abs(tang-tang[0])
    s05=np.interp(0.05*turn,tt,ss); s95=np.interp(0.95*turn,tt,ss)
    R_spread=(s95-s05)/(0.9*turn)
    # gap-equivalent: distance from sharp vertex (origin) to the curve, compared with a true fillet's R(1/cos(T/2)-1)
    gap=np.min(np.hypot(P[:,0],P[:,1]))
    R_gap=gap/(1/math.cos(T/2)-1)
    return Rmin,R_spread,R_gap
for T,phi,lab in [(45,17.8,'vertical face/chamfer edge (vertex at 40.34 deg, bisector 22.5 deg -> ray 17.8 deg off bisector)'),(45,0,'45 deg turn, ray on bisector'),(52.9,26.4,'panel centre arch: vertical face vs 37 deg cone, horizontal ray (26.4 deg off bisector)')]:
    print('  --',lab)
    for k in [1.2,0.8,0.7,0.6,0.3,0.25,0.18,0.12,0.10,0.07,0.05]:
        Rmin,Rs,Rg=corner_metrics(T,k,phi)
        print('   k=%.2f  Rmin %.2f  R_turnspread %.2f  R_gap %.2f   (ratios to k: %.1f %.1f %.1f)'%(k,Rmin,Rs,Rg,Rmin/k,Rs/k,Rg/k))
print()
print('== 2. v006 arch: carving onset (outer_r < section_r - tol) by theta')
sq=G['sq_radius']; sec=G['section_r']; bS=G['body_S']; rnd=G['roundness']; outer=G['outer_r']; wat=G['width_at']
S=wat(152.5); a=G['CHAMFER']*S
thv=math.degrees(math.atan(1-2*G['CHAMFER']))
print('   face/chamfer vertex theta = %.2f deg; chamfer leg at S(152.5)=%.2f: %.2f mm'%(thv,S,a))
for thd in [0,10,20,30,35,thv,45]:
    th=math.radians(thd); out=[]
    for tol in [0.05,0.2,0.5]:
        zz=np.arange(120,175,0.02); found=None
        for z in zz:
            if sec(th,bS(z),rnd(z))-outer(th,z)>tol: found=z; break
        out.append(found)
    y=sec(th,S,0)*math.sin(th)
    print('   theta %5.2f (y=%.1f): onset tol0.05 %.2f  tol0.2 %.2f  tol0.5 %.2f'%(thd,y,*out))
print()
print('== 3. v006 shoulder R(z) slope near the corner (deg from vertical)')
for z in [132,136,140,144,148,152,156,157.4,157.6,160,165]:
    d=(G['shoulder_R'](z+0.05)-G['shoulder_R'](z-0.05))/0.1
    print('   z %.1f shoulder_R %.2f dR/dz %.3f -> %.1f deg from vertical'%(z,G['shoulder_R'](z),d,math.degrees(math.atan(-d))))
print('== 4. PROFILE derived numbers'); 
for z in [140,145,150,152.5,155,157.5,160]: print('   W(%.1f)=%.2f'%(z,wat(z)))
