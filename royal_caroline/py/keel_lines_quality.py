# quality of the keel and keelson lines (side view): 4 lines from the STEP data, curvature, wiggles, and a points+spline rebuild with few points
import json,numpy as np
from scipy.interpolate import UnivariateSpline,LSQUnivariateSpline,splprep,splev,CubicSpline
from shapely.geometry import Polygon,LineString
V=json.load(open('data/keel_keelson_v2.json')); PR=json.load(open('data/step44_profiles.json'))
KS=Polygon(max(PR['Boss-Extrude4[4]'],key=lambda q:Polygon(q).area)).buffer(0); KP=Polygon(max(PR['Boss-Extrude2[2]'],key=lambda q:Polygon(q).area)).buffer(0)
def env(pg,x,which):
    l=pg.intersection(LineString([(x,-50),(x,300)]))
    if l.is_empty: return np.nan
    zs=[c[1] for g in (l.geoms if hasattr(l,'geoms') else [l]) for c in g.coords]; return max(zs) if which=='up' else min(zs)
X=np.arange(46.0,526.01,1.0)
L={'keelson_underside (seat)':(np.array(V['keelson_spline']['X']),np.array(V['keelson_spline']['Z'])),
   'keel_top_surface':(np.array(V['keel_surface']['X']),np.array(V['keel_surface']['Z'])),
   'keelson_top (STEP)':(X,np.array([env(KS,x,'up') for x in X])),
   'keel_bottom (STEP)':(X,np.array([env(KP,x,'low') for x in X]))}
def curv(xs,zs):
    s=CubicSpline(xs,zs); d1=s(xs,1); d2=s(xs,2); return d2/(1+d1**2)**1.5
def metrics(xs,zs):
    k=curv(xs,zs); sc=int((np.diff(np.sign(k[np.abs(k)>1e-4]))!=0).sum()); dk=np.gradient(k,xs); ext=int((np.diff(np.sign(dk[np.abs(dk)>2e-6]))!=0).sum())
    return sc,ext,abs(k).max()
out={}
for nm,(xs,zs) in L.items():
    ok=~np.isnan(zs); xs,zs=xs[ok],zs[ok]; print('\n==',nm,'n',len(xs),'X %.0f..%.0f'%(xs[0],xs[-1]),'| original: curvature sign changes %d, curvature extrema %d, max|k| %.4f'%metrics(xs,zs))
    for sp_far,sp_bow in ((60,30),(45,25),(40,20),(30,15)):
        kn=list(np.arange(xs[0]+sp_far,440,sp_far))+list(np.arange(440,xs[-1]-sp_bow/2,sp_bow)); kn=[k for k in kn if xs[0]<k<xs[-1]]
        f=LSQUnivariateSpline(xs,zs,kn,k=3); r=zs-f(xs); sc,ext,km=metrics(xs,f(xs))
        print('  knots %2d (far %d / bow %d mm): max dev %.3f rms %.3f | sign changes %d, curvature extrema %d, max|k| %.4f'%(len(kn),sp_far,sp_bow,abs(r).max(),r.std(),sc,ext,km))
