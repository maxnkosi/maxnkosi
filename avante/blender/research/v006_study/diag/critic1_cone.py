import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
def sil(name,thr):
    g=np.load(D+'critic1_%s.npy'%name)[...,:3].min(2); H,W=g.shape; out=np.full(H,np.nan)
    for y in range(H):
        r=g[y]; idx=np.where(r<thr)[0]
        if len(idx)<3: continue
        i0,i1=idx[0],idx[-1]
        L=i0-1+(r[i0-1]-thr)/(r[i0-1]-r[i0]); R=i1+(r[i1]-thr)/(r[i1]-r[i1+1]); out[y]=R-L
    return out
for name,thr,base,zs,ws in [('raw2',0.90,363.5,226.9/338.0,None),('raw1',0.90,385.5,None,None),('raw7',0.85,797.5,None,None)]:
    w=sil(name,thr); ys=np.arange(len(w))
    Wm=np.nanmax(w[int(base*0.3):int(base-5)])
    sx=89.0/Wm; sz=zs if zs else sx
    z=(base-ys)*sz; R=w*sx/2
    for lo,hi in [(0.60,0.85),(0.55,0.90)]:
        m=(w/Wm>lo)&(w/Wm<hi)&(z>140)&(z<185)
        A=np.vstack([z[m],np.ones(m.sum())]).T; (b,c),res,_,_=np.linalg.lstsq(A,R[m],rcond=None)
        resid=R[m]-(b*z[m]+c)
        h=Wm*sx/2  # 44.5
        zap=(h-c)/b
        print('%s fit %.2f-%.2f: dR/dz=%.3f (%.1f deg from vertical), rms %.2f max %.2f mm, n=%d | sharp apex z(R=%.2f)=%.1f'%(name,lo,hi,b,np.degrees(np.arctan(-b)),resid.std(),abs(resid).max(),m.sum(),h,zap))
        for a in [3.5,4.0,4.5,5.0,6.7]:
            rc=np.hypot(h,h-a); print('     leg %.1f: corner r %.2f -> corner z %.1f rise %.1f'%(a,rc,zap-(rc-h)/(-b),(rc-h)/(-b)))
    # silhouette 'start' : where R departs 0.5 mm below max plateau
    mm=(z>140)&(z<170); zz=z[mm]; RR=R[mm]; o=np.argsort(zz); zz,RR=zz[o],RR[o]
    st=zz[np.where(RR<h-0.5)[0][0]]; print('   silhouette 0.5mm-drop z=%.1f; z scale %.4f mm/px'%(st,sz))
