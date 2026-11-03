import numpy as np, sys
name=sys.argv[1]; ys=[int(v) for v in sys.argv[2].split(',')]; x0,x1=int(sys.argv[3]),int(sys.argv[4])
a = np.load(name+'_rgba.npy'); L = a[..., :3].mean(-1)
for y in ys:
    row = L[y-2:y+3, x0:x1].mean(0)
    print(y, ' '.join('%d:%d' % (x0+i, int(v*255)) for i, v in enumerate(row)))
