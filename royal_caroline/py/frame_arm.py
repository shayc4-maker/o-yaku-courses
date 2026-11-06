# frame arm at one face plane (builder rule): exact hull line to the keel wall, one pocket-floor horizontal, inner line meets its end
import sys,os,json,numpy as np
sys.path.insert(0,'py')
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline,splprep,splev
from scipy.signal import savgol_filter
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']; KB=F.KB; T=F.T; RAISE=float(os.environ.get('RAISE','2.0'))
def arm(X):
    floor=float(kK(min(X,526.0)))-DEPTH; seat=float(sK(min(X,526.0)))      # pocket floor on the keel, keelson spline underneath the keelson: the frame fills the gap between them at the centre
    P=F.hull_line(X); P=P[np.argsort(P[:,1])]
    # hull line extended inward to the keel wall along its own cubic fit (last 10 mm), then the vertical wall
    m=(P[:,0]<=P[0,0]+10); c=np.polyfit(P[m,0],P[m,1],3); ys=np.linspace(KB,P[0,0],12,endpoint=False); ext=np.c_[ys,np.polyval(c,ys)]
    O=np.vstack([ext,P]); hk=float(ext[0,1])
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]; N=np.c_[-d[:,1],d[:,0]]; I=O+N*T
    # inner line: its own spline from the end of the floor line (KB, floor) through the exact offset points further out
    # inner line continuation: a spline from the end of the seat line (KB, seat) that joins the exact offset line TANGENTIALLY further out; the start is a corner against the horizontal line
    cand=np.where((I[:,0]>=KB+6)&(I[:,1]>=seat+1.5))[0]
    if len(cand)==0: raise ValueError('inner line does not rise above the seat')
    jj=int(cand[0]); P3=I[jj]; T3=I[min(jj+3,len(I)-1)]-I[max(jj-3,0)]; T3=T3/np.hypot(*T3); P0=np.array([KB,seat]); ch=P3-P0; L=np.hypot(*ch); T0=ch/L
    tt=np.linspace(0,1,50)[:,None]; inner_conn=(2*tt**3-3*tt**2+1)*P0+(tt**3-2*tt**2+tt)*T0*L+(-2*tt**3+3*tt**2)*P3+(tt**3-tt**2)*T3*L
    inner=np.vstack([inner_conn,I[jj+1:]])
    poly=Polygon(np.vstack([[[0,floor],[KB,floor]],[[KB,hk]],O[len(ext):],inner[::-1],[[0,seat]]])).buffer(0)
    return poly,dict(seat=seat,floor=floor,hull_at_wall=hk,inner_at_wall_natural=float(I[0,1]),O=O,inner=inner)
