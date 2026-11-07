# side section at Y=0: keel top (1 mm pockets), keelson underside, and the blanks of frames 1-5 (flat cut: horizontal floor/seat over the 8 mm) -> does the base follow the slope?
import sys,json,numpy as np; sys.path.insert(0,'py')
from shapely.geometry import Polygon,LineString
from scipy.interpolate import UnivariateSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']
D=np.load('/tmp/blank_batch.npy',allow_pickle=True).item(); SH=0.6
fig,ax=plt.subplots(figsize=(15,8)); xs=np.linspace(465,528,400); ax.plot(xs,kK(xs)-SH,'k-',label='keel top surface (-0.6)'); ax.plot(xs,kK(xs)-SH-DEPTH,'k--',label='pocket floor'); ax.plot(xs,sK(xs)-SH,'g-',label='keelson underside (seat)')
for b,d in D.items():
    xc=d['xc']; pg=Polygon(d['env']).buffer(0); l=pg.intersection(LineString([(0,-50),(0,300)])); zs=[c[1] for g in (l.geoms if hasattr(l,'geoms') else [l]) for c in g.coords]; z0,z1=min(zs),max(zs)
    ax.add_patch(plt.Rectangle((xc-4,z0),8,z1-z0,fill=False,ec='tab:red',lw=1.5)); ax.text(xc,z1+1,str(b),ha='center',color='tab:red')
    pf=kK(np.array([xc-4,xc+4]))-SH-DEPTH; print('frame %d: blank floor Z %.2f (flat) ; pocket floor at X-4 %.2f, X+4 %.2f ; gap under the flat floor (pocket - floor): %.2f / %.2f mm'%(b,z0,pf[0],pf[1],pf[0]-z0,pf[1]-z0))
ax.set_xlim(465,530); ax.set_ylim(0,45); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(loc='upper left'); ax.set_title('Y=0 section: flat-cut blanks (red, 8 mm) on the sloped pocket floor'); fig.savefig('qa/frames_on_keel_side_check.png',dpi=65,bbox_inches='tight')
