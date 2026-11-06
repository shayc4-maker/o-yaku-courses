# NEW waterlines I-VII (top view, X-Y at Z=const) that pass EXACTLY through the approved body plan stations (iron) and keep the shape of the approved top-view waterline between stations: points = (a) station crossings Y_n(Z_k) at X_n (18 stations), (b) plan WL points between stations shifted by the mismatch interpolated linearly between the neighbouring stations (plan points within 4 mm of a station are dropped). Spline through all points. For approval, nothing else is changed.
import json,numpy as np
from scipy.interpolate import CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
C=json.load(open('data/bodyplan_splines_v1.json')); W=json.load(open('data/wl_top_points_all.json'))
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
def cross(n,z):
    L=np.array(C[str(n)]['curve']); i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0]
    if len(i)==0: return None
    j=i[0]; t=(z-L[j,1])/(L[j+1,1]-L[j,1]) if L[j+1,1]!=L[j,1] else 0; return float(L[j,0]+t*(L[j+1,0]-L[j,0]))
out={}; rep=[]
fig,axs=plt.subplots(2,1,figsize=(20,16),gridspec_kw={'height_ratios':[1,1.2]})
cols=dict(zip(['I','II','III','IV','V','VI','VII'],['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
for k,v in W.items():
    z=v['z']; P=np.array(v['points_XY']); P=P[np.argsort(P[:,0])]; plan=lambda x: float(np.interp(x,P[:,0],P[:,1]))
    st=[(XST[n],cross(n,z)) for n in XST if cross(n,z) is not None]; st=sorted(st)
    xs=np.array([a for a,b in st]); ys=np.array([b for a,b in st]); d=np.array([y-plan(x) if P[0,0]<=x<=P[-1,0] else np.nan for x,y in st])
    ok=~np.isnan(d); xs_,d_=xs[ok],d[ok]
    pts=[(float(x),float(y),'station') for x,y in st]
    for x,y in P:
        if np.min(np.abs(xs-x))<4.0: continue
        pts.append((float(x),float(y+np.interp(x,xs_,d_)),'plan+corr'))
    pts.sort(); q=np.array([(a,b) for a,b,c in pts]); cs=CubicSpline(q[:,0],q[:,1])
    out[k]=dict(z=z,points=[[round(a,2),round(b,2),c] for a,b,c in pts],mismatch_at_stations={str(n):round(float(dd),2) for (n,dd) in zip([m for m in XST if cross(m,z) is not None][::-1] if False else [n for n in sorted(XST,key=lambda m:XST[m]) if cross(n,z) is not None],d)})
    rep.append((k,len(st),len(pts),float(np.nanmax(np.abs(d))),float(np.nanstd(d))))
    for a,(xl,yl) in zip(axs,(((-10,570),(0,80)),((420,570),(0,60)))):
        t=np.linspace(q[0,0],q[-1,0],1200); a.plot(t,cs(t),color=cols[k],lw=1.2); a.plot(P[:,0],P[:,1],'.',color=cols[k],ms=3,alpha=.5)
        a.plot([x for x,y,c in pts if c=='station'],[y for x,y,c in pts if c=='station'],'o',color=cols[k],mfc='none',ms=7); a.set_xlim(*xl); a.set_ylim(*yl)
for a in axs: a.set_aspect('equal'); a.grid(alpha=.25)
axs[0].set_title('NEW waterlines I-VII (top view): spline through the station crossings (circles, exact) and the plan points shifted by the interpolated mismatch (dots = old plan points)')
fig.savefig('qa/wl_new_v1.png',dpi=55,bbox_inches='tight'); json.dump(out,open('data/wl_new_points_v1.json','w'))
for r in rep: print('WL %-3s stations used %2d, points %3d, mismatch plan vs stations: max %.2f mm, std %.2f'%r)
