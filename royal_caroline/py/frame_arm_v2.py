# v2: loft with approved station ends, lower end on the updated rabbet, no shift, no raise
# frame arm at one face plane (builder rule): exact hull line to the keel wall, one pocket-floor horizontal, inner line meets its end
import sys,os,json,numpy as np
sys.path.insert(0,'py')
import frames_batch_2d as F
import hull_new_sections as HN
HN.C=json.load(open('data/bodyplan_splines_v2_ends.json')); HN._C={}; HN._CACHE='/tmp/claude-0/x/loft_ends_cache.pkl'; HN.SURF=None
from scipy.interpolate import CubicSpline
_rb=json.load(open('data/rabbet_points_v3_ends.json'))['points']; R3=CubicSpline([p[0] for p in _rb],[p[1] for p in _rb],bc_type='natural')
def hull_line_v2(X):
    if X>=527.0:          # the loft collapses in its last 0.8 mm before station 1 (Y@Z70 jumps 41.3 -> 29.4): use the approved station 1 line itself (527.8)
        P=np.array(HN.C['1']['curve']); P=P[np.argsort(P[:,1])]
    else: P=HN.section(X)
    zz=np.round(P[:,1],2); _,ui=np.unique(zz,return_index=True); P=P[ui]; P=P[np.argsort(P[:,1])]
    z0,z1=P[0,1],P[-1,1]; zs=np.r_[z0,np.linspace(z0,z1,15)[1:]]; pts=np.array([(float(np.interp(z,P[:,1],P[:,0])),float(z)) for z in zs]); tk,u=splprep(pts.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tk); return np.c_[y,z]
from scipy.interpolate import UnivariateSpline,splprep,splev
from scipy.signal import savgol_filter
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']; KB=F.KB; T=F.T; RAISE=float(os.environ.get('RAISE','2.0')); SHIFT=float(os.environ.get('SHIFT','0.0'));  # backbone lowered vs the body plan = frames raised vs the keel (builder, B3 check)
JOIN=float(os.environ.get('JOIN','34'))
def arm(X):
    floor=float(kK(min(X,526.0)))-DEPTH-SHIFT; seat=float(sK(min(X,526.0)))-SHIFT      # pocket floor on the keel, keelson spline underneath the keelson: the frame fills the gap between them at the centre
    P=hull_line_v2(X); zr=float(R3(X))      # loft with the approved station ends; lower end ON the updated rabbet
    if P[0,1]<zr:
        i=int(np.argmax(P[:,1]>=zr)); y0=float(np.interp(zr,[P[i-1,1],P[i,1]],[P[i-1,0],P[i,0]])); L=np.vstack([[y0,zr],P[i:]])      # trim
    else:
        L=np.vstack([[P[0,0],zr],P[1:]])      # tiny drop to the rabbet (<=0.35 mm)
    if L[0,0]<KB:                              # the end would lie inside the keel width: cut at the wall
        j=int(np.argmax(L[:,0]>=KB)); zk=float(np.interp(KB,[L[j-1,0],L[j,0]],[L[j-1,1],L[j,1]])); L=np.vstack([[KB,zk],L[j:]])
    O=np.vstack([[KB,L[0,1]],L]) if L[0,0]>KB+1e-6 else L
    ext=O[:1]; hk=float(O[0,1])
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]; N=np.c_[-d[:,1],d[:,0]]; I=O+N*T
    # inner line: its own spline from the end of the floor line (KB, floor) through the exact offset points further out
    # inner line: ONE continuous curve. Z(y) = natural offset line Z_nat(y) + D * w(y); D = what is needed to reach the seat at the keel wall, w = quintic smoothstep from 1 (wall) to 0 (join, JOIN mm out): the line leaves the exact offset gradually, no break, tangent- and curvature-continuous at the join
    Il_=I[:int(np.argmax(I[:,0]))+1]; Iy=Il_[Il_[:,0]>=KB-1e-6]; Iy=Iy[np.argsort(Iy[:,0])]      # lower branch only (up to the widest point)
    yj=KB+JOIN; yj=KB+JOIN
    if Iy[-1,0]<yj+1: raise ValueError('inner line too short for JOIN')
    z_nat=lambda y: np.interp(y,Iy[:,0],Iy[:,1]); D=seat-float(z_nat(KB))
    # inner line: cubic Hermite in y from the seat corner to the exact offset line (tangent join). The join is moved outward (JOIN, +10 mm steps) until the whole line is concave (never bends the wrong way)
    h=0.5; zn=lambda y: float(z_nat(y)); ymaxl=float(I[:int(np.argmax(I[:,0]))+1,0].max()); best=None
    # convexity guaranteed: cubic Hermite z''(0)=(2/L)(3m-2*s0-s1) >= 0 and z''(L)=(2/L)(2*s1+s0-3m) >= 0  <=>  max(0,3m-2*s1) <= s0 <= (3m-s1)/2, feasible iff m <= s1 <= 3m (m = chord slope, s1 = natural slope at the join). Smallest join distance that is feasible.
    for J in np.arange(JOIN,min(ymaxl-KB-4,120),2.0):
        yj=KB+J; L=yj-KB; zj=zn(yj)
        if zj<seat+0.3: continue
        s1=(zn(yj+h)-zn(yj-h))/(2*h); s0n=(zn(KB+h)-zn(KB))/h; m=(zj-seat)/L
        if not (m<=s1<=3*m): continue
        lo=max(0.0,3*m-2*s1); hi=(3*m-s1)/2
        if lo>hi+1e-9: continue
        s0=float(np.clip(s0n,lo,hi)); yy=np.linspace(KB,yj,160); u=(yy-KB)/L; zc=seat*(2*u**3-3*u**2+1)+s0*L*(u**3-2*u**2+u)+zj*(-2*u**3+3*u**2)+s1*L*(u**3-u**2)
        best=(0.0,yj,zc,yy); break
    if best is None: raise ValueError('no convex join found')
    neg,yj,zc,yy=best; inner_conn=np.c_[yy,zc]
    inner=np.vstack([[[0.0,seat]],inner_conn,I[I[:,0]>yj+1e-9]])
    inner=inner[1:] if False else inner
    poly=Polygon(np.vstack([[[0,floor],[KB,floor]],[[KB,hk]],O[len(ext):],inner[::-1]])).buffer(0)
    return poly,dict(seat=seat,floor=floor,hull_at_wall=hk,inner_at_wall_natural=float(I[0,1]),O=O,inner=inner)
