# frame arm at one face plane (builder rule): exact hull line to the keel wall, one pocket-floor horizontal, inner line meets its end
import sys,os,json,numpy as np
sys.path.insert(0,'py')
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline,splprep,splev
from scipy.signal import savgol_filter
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']; KB=F.KB; T=F.T; RAISE=float(os.environ.get('RAISE','2.0')); JOIN=float(os.environ.get('JOIN','50'))
def arm(X):
    floor=float(kK(min(X,526.0)))-DEPTH; seat=float(sK(min(X,526.0)))      # pocket floor on the keel, keelson spline underneath the keelson: the frame fills the gap between them at the centre
    P=F.hull_line(X)      # keep the line's own order (sorting by Z breaks flat midship frames)
    # hull line extended inward to the keel wall along its own cubic fit (last 10 mm), then the vertical wall
    m=(P[:,0]<=P[0,0]+10); c=np.polyfit(P[m,0],P[m,1],3); ys=np.linspace(KB,P[0,0],12,endpoint=False); ext=np.c_[ys,np.polyval(c,ys)]
    O=np.vstack([ext,P]); hk=float(ext[0,1])
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]; N=np.c_[-d[:,1],d[:,0]]; I=O+N*T
    # inner line: its own spline from the end of the floor line (KB, floor) through the exact offset points further out
    # inner line: ONE continuous curve. Z(y) = natural offset line Z_nat(y) + D * w(y); D = what is needed to reach the seat at the keel wall, w = quintic smoothstep from 1 (wall) to 0 (join, JOIN mm out): the line leaves the exact offset gradually, no break, tangent- and curvature-continuous at the join
    Iy=I[I[:,0]>=KB-1e-6]; Iy=Iy[np.argsort(Iy[:,0])]; yj=KB+JOIN
    if Iy[-1,0]<yj+1: raise ValueError('inner line too short for JOIN')
    z_nat=lambda y: np.interp(y,Iy[:,0],Iy[:,1]); D=seat-float(z_nat(KB))
    h=0.5; s0=float((z_nat(KB+h)-z_nat(KB))/h); s1=float((z_nat(yj+h)-z_nat(yj-h))/(2*h)); L=yj-KB; zj=float(z_nat(yj))
    s0=min(s0,1.5*(zj-seat)/L) if zj>seat else min(s0,0.0); yy=np.linspace(KB,yj,80); u=(yy-KB)/L; H=lambda a,b,c,d_: a*(2*u**3-3*u**2+1)+b*L*(u**3-2*u**2+u)+c*(-2*u**3+3*u**2)+d_*L*(u**3-u**2)
    inner_conn=np.c_[yy,H(seat,s0,zj,s1)]      # cubic Hermite in y: starts at the seat corner with the natural slope of the offset line, joins the exact offset line tangentially at JOIN mm
    inner=np.vstack([[[0.0,seat]],inner_conn,I[I[:,0]>yj]])
    inner=inner[1:] if False else inner
    poly=Polygon(np.vstack([[[0,floor],[KB,floor]],[[KB,hk]],O[len(ext):],inner[::-1]])).buffer(0)
    return poly,dict(seat=seat,floor=floor,hull_at_wall=hk,inner_at_wall_natural=float(I[0,1]),O=O,inner=inner)
