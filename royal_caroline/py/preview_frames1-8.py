# quick oblique wire preview of the frame blanks 1-8 (outline at X-4, X, X+4) with the new rabbet and the backbone side outline (not a render)
import json,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
from scipy.interpolate import CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
A=json.load(open('data/frames_arm_v2_1_2_3_4_5_6_7_8.json')); mir=lambda g: affinity.scale(g,xfact=-1,yfact=1,origin=(0,0))
def full(half):
    h=Polygon(half).buffer(0); g=unary_union([h.buffer(0.01),mir(h).buffer(0.01)]).buffer(-0.01); return max(g.geoms,key=lambda q:q.area) if hasattr(g,'geoms') else g
th=np.radians(55); ph=np.radians(22)
def proj(X,Y,Z): return -(X*np.cos(th)-Y*np.sin(th))*-1, Z*np.cos(ph)+(X*np.sin(th)+Y*np.cos(th))*np.sin(ph)
fig,axs=plt.subplots(1,2,figsize=(20,9))
for a,vw in zip(axs,(dict(th=55,ph=22),dict(th=125,ph=30))):
    t_=np.radians(vw['th']); p_=np.radians(vw['ph'])
    pr=lambda X,Y,Z:(X*np.cos(t_)-Y*np.sin(t_),Z*np.cos(p_)+(X*np.sin(t_)+Y*np.cos(t_))*np.sin(p_))
    for b in range(1,9):
        d=A[str(b)]; xc=d['X']; fs={k:full(v['half']) for k,v in d['faces'].items()}; env=Polygon(unary_union([g.buffer(0.01) for g in fs.values()]).buffer(-0.01).exterior) if not hasattr(unary_union([g.buffer(0.01) for g in fs.values()]).buffer(-0.01),'geoms') else Polygon(max(unary_union([g.buffer(0.01) for g in fs.values()]).buffer(-0.01).geoms,key=lambda q:q.area).exterior)
        r=np.array(env.exterior.coords)
        for X,c,lw in ((xc-4,'tab:red',.8),(xc,'gray',.5),(xc+4,'tab:blue',.8)): u,v=pr(np.full(len(r),X),r[:,0],r[:,1]); a.plot(u,v,color=c,lw=lw)
        for i in range(0,len(r),max(1,len(r)//14)): u,v=pr(np.array([xc-4,xc+4]),np.array([r[i,0]]*2),np.array([r[i,1]]*2)); a.plot(u,v,color='k',lw=.25)
    a.set_aspect('equal'); a.axis('off')
axs[0].set_title('Frames 1-8 blanks, view from the bow side (red = back face X-4, blue = front face X+4)',fontsize=10); axs[1].set_title('view from the other side',fontsize=10)
fig.savefig('qa/frames1-8_preview.png',dpi=55,bbox_inches='tight')
