# frame arm at one face plane (builder rule): exact hull line to the keel wall, one pocket-floor horizontal, inner line meets its end
import sys,os,json,numpy as np
sys.path.insert(0,'py')
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline,splprep,splev
from scipy.signal import savgol_filter
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']; KB=F.KB; T=F.T
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
