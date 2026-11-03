import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
# average band profile at left/right silhouette across body rows, aligned on the subpixel silhouette edge
for name,thr,rows,mmpx in [('raw2',0.90,range(190,330),0.671),('raw1',0.90,range(215,350),0.735)]:
    g=np.load(D+'critic1_%s.npy'%name)[...,:3].mean(2)
    acc={'L':[], 'R':[]}
    for y in rows:
        r=g[y]; idx=np.where(r<thr)[0]; i0,i1=idx[0],idx[-1]
        acc['L'].append(r[i0-2:i0+14]); acc['R'].append(r[i1-13:i1+3][::-1])
    for s in 'LR':
        m=np.mean(acc[s],0); print(name,s,' '.join('%2d'%int(v*99) for v in m))
