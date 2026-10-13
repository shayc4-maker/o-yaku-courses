import numpy as np
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import gaussian_filter, map_coordinates
im=np.array(Image.open('st/plan_1a_aligned.png')).astype(float)/255
dk=gaussian_filter(1-im[400:1700,1500:2500],1.0); OX,OY=1500,400
def dens(x,y): return map_coordinates(dk,[[y-OY],[x-OX]],order=1)[0]
def local_max_across(x,y,th):
    """re-centre (x,y) on the stroke centre perpendicular to direction th"""
    nx,ny=-np.sin(th),np.cos(th); best=None
    for t in np.linspace(-4,4,33):
        v=dens(x+nx*t,y+ny*t)
        if best is None or v>best[0]: best=(v,t)
    return x+nx*best[1],y+ny*best[1]
# start: top tip of curve 18
x,y,th=1886.0,512.0,np.deg2rad(95)
path=[(x,y)]; r=3.0
for step in range(3000):
    cands=[]
    for dth in np.deg2rad(np.arange(-30,31,3)):
        t=th+dth; xx,yy=x+r*np.cos(t),y+r*np.sin(t)
        s=np.mean([dens(x+k*np.cos(t),y+k*np.sin(t)) for k in (1.5,3.0,4.5,6.0)])
        cands.append((s-0.35*abs(dth),t,xx,yy))
    s,t,xx,yy=max(cands)
    th=0.6*th+0.4*t; x,y=local_max_across(xx,yy,th)
    path.append((x,y))
    if x>=2352 or y>1560: break
path=np.array(path); print(len(path), path[0], path[-1])
np.save('follow18.npy',path)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(11,14)); ax.imshow(im[400:1650,1500:2450],cmap='gray',extent=(1500,2450,1650,400)); ax.plot(path[:,0],path[:,1],'r-',lw=1); plt.savefig('follow18.png',dpi=70)
