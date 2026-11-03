import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
def sil(name,thr):
    g=np.load(D+'critic1_%s.npy'%name)[...,:3].min(2); H,W=g.shape; out=np.full((H,2),np.nan)
    for y in range(H):
        r=g[y]; idx=np.where(r<thr)[0]
        if len(idx)<3: continue
        i0,i1=idx[0],idx[-1]
        out[y]=(i0-1+(r[i0-1]-thr)/(r[i0-1]-r[i0]), i1+(r[i1]-thr)/(r[i1]-r[i1+1]))
    return out
for name,thr,sc in [('raw2',0.90,0.669),('raw1',0.90,0.735),('raw7',0.85,0.2903)]:
    s=sil(name,thr); w=s[:,1]-s[:,0]; ok=np.where(~np.isnan(w))[0]; last=ok[-1]
    print('==',name,'last row',last,'(mm/px %.3f)'%sc)
    ref=w[last-int(20/sc)]  # width at ~20 mm
    for j in range(int(16/sc),-1,-1):
        y=last-j
        if j%max(1,int(1/sc))==0: print('   h=%5.1f mm  half-inset vs z20: %5.2f mm   L %.1f R %.1f'%(j*sc,(ref-w[y])/2*sc,s[y,0],s[y,1]))
