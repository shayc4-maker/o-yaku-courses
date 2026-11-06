# waterlines with a Z-based tolerance: a station crossing may move in Y by TOLZ / slope (slope = dZ/dY of the station line at the crossing), i.e. every station line stays within TOLZ mm of the waterline POINT measured in the section plane (z-direction). Shallow crossings (low waterlines near the bilge) get a wide Y tolerance, steep ones a tight one. Least-squares cubic B-spline with the fewest knots meeting every crossing tolerance.
import json,numpy as np,sys
from scipy.interpolate import make_lsq_spline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
TOLZ=float(sys.argv[1]) if len(sys.argv)>1 else 0.25
D=json.load(open('data/wl_new_points_v1.json')); C=json.load(open('data/bodyplan_splines_v1.json'))
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
def slope(n,z):
    L=np.array(C[str(n)]['curve']); i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0][0]; dy=L[i+1,0]-L[i,0]; dz=L[i+1,1]-L[i,1]; return abs(dz/dy) if abs(dy)>1e-9 else 50.0
def sc(sp,x0,x1,thr=2e-4):
    t=np.linspace(x0,x1,4000); k=sp(t,2); s=np.sign(k[np.abs(k)>thr]); return int((np.diff(s)!=0).sum())
cols=dict(zip(['I','II','III','IV','V','VI','VII'],['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
fig,axs=plt.subplots(2,1,figsize=(20,16),gridspec_kw={'height_ratios':[1,1.2]}); res={}
for k,v in D.items():
    pts=np.array([[p[0],p[1]] for p in v['points']]); typ=np.array([p[2] for p in v['points']]); z=v['z']
    tol=np.full(len(pts),1.0); 
    for i,(x,y) in enumerate(pts):
        if typ[i]=='station':
            n=min(XST,key=lambda m:abs(XST[m]-x)); tol[i]=min(3.0,TOLZ/max(slope(n,z),0.08))
    x=pts[:,0]; y=pts[:,1]; w=1.0/tol; st=typ=='station'
    best=None
    for n in range(2,30):
        ki=np.linspace(x[0],x[-1],n+2)[1:-1]; t=np.r_[[x[0]]*4,ki,[x[-1]]*4]
        try: sp=make_lsq_spline(x,y,t,k=3,w=w)
        except Exception: continue
        dev=np.abs(sp(x)-y); ok=np.all(dev[st]<=tol[st]+1e-9) and np.all(dev[~st]<=1.0)
        if ok: best=(n,sp,dev,sc(sp,x[0],x[-1],1e-3)); break
    if best is None: print('WL',k,'no fit'); continue
    n,sp,dev,ch=best; res[k]=dict(z=z,knots=n,max_dev_station_Y=float(dev[st].max()),max_Z_error_at_stations=float(max((dev[i]*slope(min(XST,key=lambda m:abs(XST[m]-x[i])),z) for i in np.where(st)[0]))),sign_changes=ch)
    print('WL %-3s interior knots %2d | station crossings: max Y shift %.2f mm = max Z error %.2f mm | curvature sign changes (|k|>1e-3) %d'%(k,n,res[k]['max_dev_station_Y'],res[k]['max_Z_error_at_stations'],ch))
    for a,(xl,yl) in zip(axs,(((-10,570),(0,80)),((420,570),(0,60)))):
        t_=np.linspace(x[0],x[-1],1500); a.plot(t_,sp(t_),color=cols[k],lw=1.3); a.plot(x[st],y[st],'o',color=cols[k],mfc='none',ms=7); a.set_xlim(*xl); a.set_ylim(*yl)
for a in axs: a.set_aspect('equal'); a.grid(alpha=.25)
axs[0].set_title('Waterlines with Z-based tolerance %.2f mm at the stations (circles = station crossings); fewest knots'%TOLZ); fig.savefig('qa/wl_new_smooth2_v1.png',dpi=55,bbox_inches='tight'); json.dump(res,open('data/wl_new_smooth2_v1.json','w'))
