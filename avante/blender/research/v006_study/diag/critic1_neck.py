import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
for name,ys,x0,x1 in [('raw1',[110,125,250],90,230),('raw2',[65,75,250],195,345)]:
    g=np.load(D+'critic1_%s.npy'%name)[...,:3].min(2)
    for y in ys:
        print(name,y,' '.join('%2d'%int(v*99) for v in g[y,x0:x1]))
