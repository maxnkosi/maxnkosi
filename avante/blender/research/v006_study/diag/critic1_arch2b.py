import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
g=np.load(D+'critic1_raw2.npy')[...,:3].mean(2)
base=363.5; mm=0.671; xc=270.95; mmx=0.667
ths=[0.03,0.05,0.08,0.12,0.2,0.3]
print('y(mm)  '+'  '.join('d>%.2f'%t for t in ths)+'   (z of LOWEST row with darkness>t, searching up from row 175 until first hit; mm)')
res={}
for x in range(208,336,2):
    col=1-g[95:176,x-1:x+2].mean(1)   # darkness, rows 95..175
    out=[]
    for t in ths:
        # scan from bottom up: first row where darkness exceeds t
        idx=np.where(col>t)[0]
        if len(idx)==0: out.append(np.nan); continue
        j=idx[-1]
        # subpixel between j and j+1
        if j+1<len(col): f=(col[j]-t)/(col[j]-col[j+1]); jj=j+f
        else: jj=j
        out.append((base-(95+jj))*mm)
    y=(x-xc)*mmx; res[x]=out
    print('%+6.1f '%y+'  '.join('%6.1f'%v for v in out))
