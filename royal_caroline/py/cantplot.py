import sys,json,numpy as np
sys.argv=[sys.argv[0],sys.argv[1]]; sys.path.insert(0,sys.argv[1])
src=open(sys.argv[1]+'/cants.py').read(); exec(src[:src.index('# ---- march:')])
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString
C=json.load(open(O+'/cant_pieces.json'))
fig,axs=plt.subplots(1,4,figsize=(20,6))
for ax,z in zip(axs,(32,45,65,100)):
    xs=np.arange(512,560,0.25); yo=Yv(xs,np.full(len(xs),z)); ax.plot(xs,yo,'k-',lw=1)
    ax.plot(xs,yo-T(z),'k--',lw=.6)
    ax.axvline(528.03,color='brown',lw=2); ax.axhline(2.65,color='slateblue',lw=2)
    for c in C:
        G=Polygon(c['poly']); seg=G.intersection(LineString([(-100,z),(100,z)]))
        if seg.is_empty: continue
        for sgm in getattr(seg,'geoms',[seg]):
            u0,u1=sgm.bounds[0],sgm.bounds[2]
            Q=np.array(c['Q']);n=np.array(c['n']);d=np.array(c['d'])
            quad=np.array([Q+u0*d,Q+u1*d,Q+u1*d+n*4,Q+u0*d+n*4,Q+u0*d])
            ax.fill(quad[:,0],quad[:,1],alpha=.5); ax.text(*(Q+u0*d),str(c['id']),fontsize=7)
    ax.set_title(f'Z={z}'); ax.set_aspect('equal'); ax.set_xlim(522,560); ax.set_ylim(0,45); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(O+'/cant_debug.png',dpi=70)
