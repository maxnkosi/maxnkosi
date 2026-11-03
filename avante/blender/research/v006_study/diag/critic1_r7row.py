import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
a=np.load(D+'critic1_raw7.npy')[...,:3]
L=a.mean(2)
acc=[];accR=[]
for y in range(560,720):
    r=a[y].min(1); idx=np.where(r<0.85)[0]; i0,i1=idx[0],idx[-1]
    acc.append(L[y,i0-2:i0+40]); accR.append(L[y,i1-39:i1+3][::-1])
print('raw7 L',' '.join('%2d'%int(v*99) for v in np.mean(acc,0)))
print('raw7 R',' '.join('%2d'%int(v*99) for v in np.mean(accR,0)))
print('px/mm',306.58/89.0)
