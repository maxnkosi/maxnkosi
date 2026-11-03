import numpy as np, sys
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
def edges(row, thr):
    # row: darkness-ish value (lower=object). find first/last index below thr with subpixel
    idx=np.where(row<thr)[0]
    if len(idx)==0: return None
    i0,i1=idx[0],idx[-1]
    def sub(i,j):  # crossing between i (above thr) and j (below)
        a,b=row[i],row[j]; return i+(a-thr)/(a-b)*(j-i) if a!=b else j
    L=sub(i0-1,i0) if i0>0 else i0; Rr=sub(i1+1,i1) if i1<len(row)-1 else i1
    return L,Rr
for name,thr in [('raw2',0.90),('raw1',0.90)]:
    a=np.load(D+'critic1_%s.npy'%name); g=a[...,:3].min(2)
    H,W=g.shape
    rows=[]
    for y in range(H):
        e=edges(g[y],thr)
        rows.append((y,)+(e if e else (np.nan,np.nan)))
    rows=np.array(rows)
    w=rows[:,2]-rows[:,1]
    ok=np.where(~np.isnan(w))[0]
    print(name,'shape',g.shape,'first/last object row',ok[0],ok[-1])
    np.save(D+'critic1_%s_sil.npy'%name,rows)
    for y in range(ok[0],ok[-1]+1,3 if name=='raw2' else 3):
        print(name,y,'L %.2f R %.2f W %.2f c %.2f'%(rows[y,1],rows[y,2],w[y],(rows[y,1]+rows[y,2])/2))
