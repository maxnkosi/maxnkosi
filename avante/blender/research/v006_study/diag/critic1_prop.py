import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
def sil(name,thr):
    a=np.load(D+'critic1_%s.npy'%name); g=a[...,:3].min(2); H,W=g.shape; out=np.full((H,2),np.nan)
    for y in range(H):
        r=g[y]; idx=np.where(r<thr)[0]
        if len(idx)<3: continue
        i0,i1=idx[0],idx[-1]
        L=i0-1+(r[i0-1]-thr)/(r[i0-1]-r[i0]); R=i1+(r[i1]-thr)/(r[i1]-r[i1+1])
        out[y]=(L,R)
    return out
def report(name,thr,base,smooth=1):
    s=sil(name,thr); w=s[:,1]-s[:,0]
    if smooth>1:
        k=np.ones(smooth)/smooth; w=np.convolve(np.nan_to_num(w),k,'same')
    y0=base
    # max width row: search body region
    body=np.arange(int(base*0.25),int(base-5))
    wv=w[body]; im=body[np.nanargmax(wv)]; Wm=np.nanmax(wv)
    plate=body[wv>=0.99*Wm]
    # shoulder start: first row above plateau where w<Wm-1.0px*... use 0.5mm equivalent later
    # neck: min width between top and max row
    print('==',name,'base row',base,'Wmax %.2f px at row %d; plateau(>=.99) rows %d..%d'%(Wm,im,plate.min(),plate.max()))
    return s,w,Wm,im
s2,w2,W2,i2=report('raw2',0.90,363.5)
s1,w1,W1,i1=report('raw1',0.90,385.5)
s7,w7,W7,i7=report('raw7',0.85,797.5)
def z(y,base,W,mmW=89.0): return (base-y)*mmW/W   # width-scaled mm
for name,w,W,base in [('raw2',w2,W2,363.5),('raw1',w1,W1,385.5),('raw7',w7,W7,797.5)]:
    H=len(w); ys=np.arange(H)
    zz=(base-ys)*89.0/W; wr=w/W
    def zat(frac,lo,hi):  # highest/lowest z where wr crosses frac in (lo,hi) z range, going upward
        m=(zz>lo)&(zz<hi)&~np.isnan(wr)
        zs=zz[m][::-1]; ws=wr[m][::-1]  # ascending z
        for j in range(1,len(zs)):
            if ws[j-1]>=frac>ws[j]: return zs[j-1]+(ws[j-1]-frac)/(ws[j-1]-ws[j])*(zs[j]-zs[j-1])
        return np.nan
    out=[name]
    for f in [0.99,0.95,0.90,0.80,0.70,0.60,0.50,0.45,0.42,0.40]:
        out.append('%.2f@%.1f'%(f,zat(f,140,200)))
    print(' '.join(out))
    # cone slope from 0.85->0.55
    za,zb=zat(0.85,140,200),zat(0.55,140,200)
    print('  cone half-width slope dR/dz = %.3f -> %.1f deg from vertical'%((0.30*89/2)/(zb-za),np.degrees(np.arctan((0.30*89/2)/(zb-za)))))
    for zq in [2,5,10,20,40,60,80,100,120,140]:
        yq=base-zq*W/89.0; j=int(round(yq)); print('   z%5.1f W/Wmax %.3f'%(zq,np.nanmean(wr[j-1:j+2])),end='')
    print()
    # neck
    m=(zz>180)&(zz<215); print('  neck W/Wmax min %.3f median %.3f'%(np.nanmin(wr[m]),np.nanmedian(wr[m])))
