# critic1: load refs via bpy, save top-down RGBA npy (float32) for numpy analysis inside Blender
import bpy, numpy as np, os, sys
R='/Users/maxhlomendlini/Documents/Avante/avante/blender/'
D=R+'research/v006_study/diag/'
srcs={'raw1':'research/references/bottle/raw1.png','raw2':'research/references/bottle/raw2.png',
 'raw5':'research/references/bottle/raw5.png','raw7':'research/references/bottle/raw7.png',
 'raw8':'research/references/bottle/raw8.png',
 'v006hero':'renders/v006_hero.png','v005hero':'renders/v005_hero.png',
 'v006tq':'renders/v006_threequarter.png','v006glass':'renders/v006_glass_only_threequarter.png',
 'v005glass':'renders/v005_tests/s1_glass_only.png','v006angle':'renders/v006_angle_avante.png'}
for k,p in srcs.items():
    if not os.path.exists(R+p): print('missing',p); continue
    im=bpy.data.images.load(R+p); w,h=im.size
    a=np.array(im.pixels[:],dtype=np.float32).reshape(h,w,4)[::-1]
    np.save(D+'critic1_%s.npy'%k,a); print(k,w,h,im.colorspace_settings.name)
