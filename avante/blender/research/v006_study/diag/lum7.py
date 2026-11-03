import numpy as np
a = np.load('raw7_rgba.npy'); L = a[..., :3].mean(-1)
# smooth vertically
from numpy import convolve
for x in range(255, 550, 15):
    col = L[150:340, x-2:x+3].mean(1)
    k = np.ones(3)/3; cs = np.convolve(col, k, 'same')
    print(x, ' '.join('%3d' % int(v*255) for v in cs[::5]))
