# aft sheer plan zoom in MODEL coords for the builder to mark the aft rabbet with pixels (picture only, nothing invented)
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import map_coordinates
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
cal=json.load(open('data/plan_calibration_v2.json'))['sheer_1a']; ax_,bx_,cx_=cal['dX']; az,bz,cz=cal['dZ']
ink=lambda X,Z:(X+ax_+bx_*(X-270)+cx_*Z, Z+az+bz*(X-270)+cz*Z)
im=np.array(Image.open('plans/plan_1a_aligned.png').convert('L')).astype(float)
xl,zl=(-25,75),(-8,62); res=0.05
nx=int((xl[1]-xl[0])/res); nz=int((zl[1]-zl[0])/res)
Xg=xl[0]+(np.arange(nx)+.5)*res; Zg=zl[1]-(np.arange(nz)+.5)*res; XX,ZZ=np.meshgrid(Xg,Zg); xi,zi=ink(XX,ZZ)
W=map_coordinates(im,[ZR-zi/KZ,(xi-X0)/KX],order=1,cval=255)
fig,a=plt.subplots(figsize=(20,13))
a.imshow(W,extent=(*xl,*zl),cmap='gray',vmin=0,vmax=255,aspect='equal')
a.set_xticks(range(-25,76,5)); a.set_yticks(range(-5,63,5)); a.grid(color='c',lw=.4,alpha=.6)
r=json.load(open('data/rabbet_points_v3_ends.json')); P=np.array(r['points'] if 'points' in r else r)[:,:2]
a.plot(P[:,0],P[:,1],'r-',lw=1.2,label='approved rabbet (ends at X=30)'); a.plot(P[:,0],P[:,1],'r.',ms=5)
c=json.load(open('data/aft_frames_builder_v1.json'))['curves']
for k,v in c.items():
    X,Z=v['cv'][0][0],v['cv'][0][2]; a.plot(X,Z,'o',color='orange',ms=7); a.text(X+.4,Z+.8,k[:7],color='orange',fontsize=9,weight='bold')
for n,x in (('st16',36.8),('st17',14.6),('st18',0.0)): a.axvline(x,color='g',lw=.8,ls='--'); a.text(x+.3,58,n,color='g')
a.set_xlim(*xl); a.set_ylim(*zl); a.legend(loc='upper right'); a.set_title('Aft sheer plan, model mm. Orange = lower end of the aft frames (your arranged lines). Mark rabbet with pixels.')
fig.savefig('qa/aft_rabbet_plan_v1.png',dpi=70,bbox_inches='tight')
