# frame arm at one face plane (builder rule): exact hull line to the keel wall, one pocket-floor horizontal, inner line meets its end
import sys,os,json,numpy as np
sys.path.insert(0,'py')
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline,splprep,splev
from scipy.signal import savgol_filter
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open(os.environ.get('KK_JSON','data/keel_keelson_v2.json'))); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']; KB=F.KB; T=F.T; RAISE=float(os.environ.get('RAISE','2.0')); SHIFT=float(os.environ.get('SHIFT','0.6'));  # backbone lowered vs the body plan = frames raised vs the keel (builder, B3 check)
JOIN=float(os.environ.get('JOIN','34'))
def arm(X):
    floor=float(kK(min(X,526.0)))-DEPTH-SHIFT; seat=float(sK(min(X,526.0)))-SHIFT      # pocket floor on the keel, keelson spline underneath the keelson: the frame fills the gap between them at the centre
    P=F.hull_line(X)      # keep the line's own order (sorting by Z breaks flat midship frames)
    # hull line extended inward to the keel wall along its own cubic fit (last 10 mm), then the vertical wall
    m=(P[:,0]<=P[0,0]+10); c=np.polyfit(P[m,0],P[m,1],3); ys=np.linspace(KB,P[0,0],12,endpoint=False); ext=np.c_[ys,np.polyval(c,ys)]
    O=np.vstack([ext,P]); hk=float(ext[0,1])
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]; N=np.c_[-d[:,1],d[:,0]]; I=O+N*T
    # offset loops where the outer line bends tighter than T (radius<T): take the cleaned shapely offset instead of the raw normal offset
    from shapely.geometry import LineString
    for sg in (1,-1):
        oc=LineString(sm).offset_curve(sg*T)
        if oc.is_empty or oc.geom_type!='LineString': continue
        c2=np.array(oc.coords)
        if np.hypot(*(c2[0]-I[0]))>np.hypot(*(c2[-1]-I[0])): c2=c2[::-1]
        if np.hypot(*(c2[0]-I[0]))<1.0: I=c2; break
    # inner line: its own spline from the end of the floor line (KB, floor) through the exact offset points further out
    # inner line: ONE continuous curve. Z(y) = natural offset line Z_nat(y) + D * w(y); D = what is needed to reach the seat at the keel wall, w = quintic smoothstep from 1 (wall) to 0 (join, JOIN mm out): the line leaves the exact offset gradually, no break, tangent- and curvature-continuous at the join
    Il_=I[:int(np.argmax(I[:,0]))+1]; Iy=Il_[Il_[:,0]>=KB-1e-6]; Iy=Iy[np.argsort(Iy[:,0])]      # lower branch only (up to the widest point)
    D0=seat-float(np.interp(KB,Iy[:,0],Iy[:,1])); JOIN_=max(8.0,min(JOIN,8.0*abs(D0)))      # short blend when the seat is only slightly above the offset line (the long default made the inner line cross the outer one at frame 1)
    yj=KB+JOIN_
    if Iy[-1,0]<yj+1: raise ValueError('inner line too short for JOIN')
    z_nat=lambda y: np.interp(y,Iy[:,0],Iy[:,1]); D=seat-float(z_nat(KB))
    # inner line: cubic Hermite in y from the seat corner to the exact offset line (tangent join). The join is moved outward (JOIN, +10 mm steps) until the whole line is concave (never bends the wrong way)
    h=0.5; zn=lambda y: float(z_nat(y)); ymaxl=float(I[:int(np.argmax(I[:,0]))+1,0].max()); best=None
    for J in np.arange(JOIN_,min(ymaxl-KB-4,float(os.environ.get('JMAX','120'))),10.0):
        yj=KB+J; L=yj-KB; zj=zn(yj)
        if zj<seat+0.3: continue          # the line may not descend: join only where the offset line is above the seat level
        s1=(zn(yj+h)-zn(yj-h))/(2*h); s0=(zn(KB+h)-zn(KB))/h
        mch=(zj-seat)/L; s0=float(np.clip(s0,0.0,1.5*mch)); s1=float(np.clip(s1,0.0,3.0*mch))      # monotone non-decreasing cubic (Fritsch-Carlson): the line never dips below the seat
        yy=np.linspace(KB,yj,160); u=(yy-KB)/L; zc=seat*(2*u**3-3*u**2+1)+s0*L*(u**3-2*u**2+u)+zj*(-2*u**3+3*u**2)+s1*L*(u**3-u**2)
        cur=np.gradient(np.gradient(np.r_[zc,zn(yj+1.0),zn(yj+2.0),zn(yj+3.0)]))[:len(zc)]/((yy[1]-yy[0])**2)
        neg=float(-min(cur[3:-3].min(),0)); 
        if best is None or neg<best[0]: best=(neg,yj,zc,yy)
        if neg<0.004: break
    neg,yj,zc,yy=best; inner_conn=np.c_[yy,zc]
    inner=np.vstack([[[0.0,seat]],inner_conn,I[I[:,0]>yj+1e-9]])
    inner=inner[1:] if False else inner
    poly=Polygon(np.vstack([[[0,floor],[KB,floor]],[[KB,hk]],O[len(ext):],inner[::-1]])).buffer(0)
    return poly,dict(seat=seat,floor=floor,hull_at_wall=hk,inner_at_wall_natural=float(I[0,1]),O=O,inner=inner)
