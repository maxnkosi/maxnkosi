import numpy as np, math
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
def sil(name,thr):
    g=np.load(D+'critic1_%s.npy'%name)[...,:3].min(2); H,W=g.shape; out=np.full((H,2),np.nan)
    for y in range(H):
        r=g[y]; idx=np.where(r<thr)[0]
        if len(idx)<3: continue
        i0,i1=idx[0],idx[-1]
        out[y]=(i0-1+(r[i0-1]-thr)/(r[i0-1]-r[i0]), i1+(r[i1]-thr)/(r[i1]-r[i1+1]))
    return out
def seg_dist(p,P):
    best=1e9
    for i in range(len(P)-1):
        a,b=P[i],P[i+1]; d=b-a; t=np.clip(((p-a)@d)/(d@d),0,1); best=min(best,np.linalg.norm(a+t*d-p))
    return best
def fitline(z,R): A=np.vstack([z,np.ones_like(z)]).T; return np.linalg.lstsq(A,R,rcond=None)[0]
for name,thr,base,sz in [('raw2',0.90,363.5,0.6713),('raw1',0.90,385.5,None),('raw7',0.85,797.5,None)]:
    s=sil(name,thr); ys=np.arange(len(s)); xc=np.nanmedian((s[:,0]+s[:,1])/2)
    w=s[:,1]-s[:,0]; Wm=np.nanmax(w[int(base*0.3):int(base-5)]); sx=89.0/Wm; sz=sz or sx
    z=(base-ys)*sz
    for side,col,sg in [('L',0,-1),('R',1,1)]:
        R=(s[:,col]-xc)*sg*sx
        ok=~np.isnan(R)
        # lines
        Wr=w/Wm
        mb=ok&(z>142)&(z<150); mc=ok&(Wr>0.6)&(Wr<0.85)&(z>150)&(z<185); mn=ok&(z>190)&(z<210)
        b1=fitline(z[mb],R[mb]); b2=fitline(z[mc],R[mc]); b3=fitline(z[mn],R[mn])
        def inter(p,q): zz=(q[1]-p[1])/(p[0]-q[0]); return np.array([zz,p[0]*zz+p[1]])
        V1=inter(b1,b2); V2=inter(b2,b3)
        T1=abs(math.atan(b2[0])-math.atan(b1[0])); T2=abs(math.atan(b3[0])-math.atan(b2[0]))
        P=np.stack([z[ok],R[ok]],1)
        g1=seg_dist(V1,P); g2=seg_dist(V2,P)
        R1=g1/(1/math.cos(T1/2)-1); R2=g2/(1/math.cos(T2/2)-1)
        print('%s %s: knuckle vertex z=%.1f r=%.2f turn %.1f deg gap %.2f -> R %.1f | neck vertex z=%.1f r=%.2f turn %.1f gap %.2f -> R %.1f | cone %.1f deg from vert'%(
            name,side,V1[0],V1[1],math.degrees(T1),g1,R1,V2[0],V2[1],math.degrees(T2),g2,R2,math.degrees(math.atan(-b2[0]))))
