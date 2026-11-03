import numpy as np, zlib, struct
def write_png(path, img):  # img HxWx3 float 0..1
    a=(np.clip(img,0,1)*255).astype(np.uint8); h,w,_=a.shape
    raw=b''.join(b'\x00'+a[y].tobytes() for y in range(h))
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    open(path,'wb').write(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b''))
def crop(name,y0,y1,x0,x1,s,out,stretch=None,grid=None):
    D='/Users/maxhlomendlini/Documents/Avante/avante/blender/research/v006_study/diag/'
    a=np.load(D+'critic1_%s.npy'%name)[y0:y1,x0:x1,:3].copy()
    if stretch: lo,hi=stretch; a=(a-lo)/(hi-lo)
    a=np.repeat(np.repeat(a,s,0),s,1)
    if grid:  # horizontal tick lines every grid rows (in source px), red
        for yy in range(0,y1-y0,grid): a[yy*s,:, :]=[1,0,0]
    write_png(D+out,a)
