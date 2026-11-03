import numpy as np
D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
g=np.load(D+'critic1_raw2.npy')[...,:3].mean(2)
base=363.5; mm=0.671; xc=270.95
for x in range(206,338,4):
    col=g[100:175,x-1:x+2].mean(1)
    # print compact column
    s=''.join(' .:-=+*#%@'[min(9,int((1-v)*30))] for v in col)
    print('%4d y=%+6.1fmm %s'%(x,(x-xc)*0.667,s))
print('rows 100..174, each char = 1 row; z(row100)=%.1f z(row174)=%.1f'%((base-100)*mm,(base-174)*mm))
