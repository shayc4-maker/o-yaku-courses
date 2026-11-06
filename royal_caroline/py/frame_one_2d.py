# ONE frame in 2D (builder's rule): exact hull line (outer) ends at the keel wall (vertical wall up to the pocket floor); the inner line (hull offset 3.2) deviates slightly inward with its own spline and meets the end of the horizontal pocket-floor line (backbone width only) - no seat line, no radii, nothing invented
import sys,os,json,numpy as np
b=int(sys.argv[1]); sys.argv=[sys.argv[0]]
sys.path.insert(0,'py')
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline,splprep,splev
from scipy.signal import savgol_filter
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']; KB=F.KB; T=F.T
xc=F.XF[46-b-1]; fc={'X-4':xc-4,'X':xc,'X+4':xc+4}; cols={'X-4':'tab:blue','X':'k','X+4':'tab:red'}
def arm(X):
    floor=float(kK(min(X,526.0)))-DEPTH
    P=F.hull_line(X); P=P[np.argsort(P[:,1])]
    # hull line extended inward to the keel wall along its own cubic fit (last 10 mm), then the vertical wall
    m=(P[:,0]<=P[0,0]+10); c=np.polyfit(P[m,0],P[m,1],3); ys=np.linspace(KB,P[0,0],12,endpoint=False); ext=np.c_[ys,np.polyval(c,ys)]
    O=np.vstack([ext,P]); hk=float(ext[0,1])
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]; N=np.c_[-d[:,1],d[:,0]]; I=O+N*T
    # inner line: its own spline from the end of the floor line (KB, floor) through the exact offset points further out
    s_=np.r_[0,np.cumsum(np.hypot(*np.diff(I,axis=0).T))]; sel=[i for i in range(len(I)) if I[i,0]>=KB+6]; k0=sel[0]
    nodes=[(KB,floor)]+[tuple(I[k0+int(np.argmin(abs(s_[k0:]-(s_[k0]+dd))))]) for dd in (0,3,6,9)]
    tk,u=splprep(np.array(nodes).T,k=3,s=0); yy,zz=splev(np.linspace(0,1,40),tk); inner_conn=np.c_[yy,zz]
    inner=np.vstack([inner_conn,I[k0+int(np.argmin(abs(s_[k0:]-(s_[k0]+9))))+1:]])
    poly=Polygon(np.vstack([[[KB,floor]],[[KB,hk]],O[len(ext):],inner[::-1]])).buffer(0)
    return poly,dict(floor=floor,hull_at_wall=hk,inner_at_wall_natural=float(I[0,1]),O=O,inner=inner)
arms={n:arm(X) for n,X in fc.items()}
for n,(p,i) in arms.items(): print('%-4s floor %.2f | outer line at the keel wall %.2f (wall %.2f mm) | inner line natural at the wall %.2f -> moves %.2f mm to meet the floor end | arm area %.0f mm2 valid %s'%(n,i['floor'],i['hull_at_wall'],i['floor']-i['hull_at_wall'],i['inner_at_wall_natural'],i['floor']-i['inner_at_wall_natural'],p.area,p.is_valid))
mir=lambda g: __import__('shapely.affinity',fromlist=['scale']).scale(g,xfact=-1,yfact=1,origin=(0,0))
fig,axs=plt.subplots(1,3,figsize=(24,10))
def draw(a,xl,yl,title):
    for n,(p,i) in arms.items():
        for g in (p,mir(p)): a.plot(*g.exterior.xy,color=cols[n],lw=1.4)
        a.plot([-KB,KB],[i['floor']]*2,color=cols[n],lw=2)
    a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_title(title,fontsize=10)
f=arms['X'][1]['floor']
draw(axs[0],(-85,85),(-5,115),'frame %d X=%.1f: final lines at X-4 (blue), X (black), X+4 (red)'%(b,xc))
draw(axs[1],(-14,14),(f-6,f+8),'keel contact: wall at Y=2.65, horizontal pocket-floor line, inner line meets its end')
draw(axs[2],(-30,30),(f-8,f+22),'wider view of the same area')
fig.savefig('qa/frame%d_one_2d.png'%b,dpi=55,bbox_inches='tight')
