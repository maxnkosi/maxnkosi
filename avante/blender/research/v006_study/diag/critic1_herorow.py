import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
a=np.load(D+'critic1_v006hero.npy')[...,:3].mean(2)
for y in [700,1180,1250]:
    r=a[y]; print(y,' '.join('%2d'%int(min(v,0.99)*99) for v in r[270:360]))
    print(y,'R',' '.join('%2d'%int(min(v,0.99)*99) for v in r[640:730]))
