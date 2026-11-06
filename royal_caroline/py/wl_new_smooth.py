# smooth waterlines: least-squares cubic B-spline (few knots) through the station crossings + the plan points (shifted by the interpolated mismatch) at the ends; the fewest knots that keep every station crossing within TOL mm; reports max deviation at the stations and curvature sign changes
import json,numpy as np,sys
from scipy.interpolate import make_lsq_spline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
TOL=float(sys.argv[1]) if len(sys.argv)>1 else 0.3
D=json.load(open('data/wl_new_points_v1.json')); F=json.load(open('data/wl_new_fair_v1.json'))
def sc(sp,x0,x1):
    t=np.linspace(x0,x1,4000); k=sp(t,2); s=np.sign(k[np.abs(k)>2e-4]); return int((np.diff(s)!=0).sum())
cols=dict(zip(['I','II','III','IV','V','VI','VII'],['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
fig,axs=plt.subplots(2,1,figsize=(20,16),gridspec_kw={'height_ratios':[1,1.2]}); res={}
for k,v in D.items():
    pts=np.array([[p[0],p[1]] for p in v['points']]); typ=np.array([p[2] for p in v['points']]); st=pts[typ=='station']
    # data = all points (stations weight 10 = near exact, plan points weight 1) -> least squares spline
    x=pts[:,0]; y=pts[:,1]; w=np.where(typ=='station',10.0,1.0)
    best=None
    for n in range(2,30):
        ki=np.linspace(x[0],x[-1],n+2)[1:-1]; t=np.r_[[x[0]]*4,ki,[x[-1]]*4]
        try: sp=make_lsq_spline(x,y,t,k=3,w=w)
        except Exception: continue
        dev=np.abs(sp(st[:,0])-st[:,1]).max(); ch=sc(sp,x[0],x[-1])
        if dev<=TOL: best=(n,sp,dev,ch); break
    if best is None: print('WL',k,'no fit within TOL'); continue
    n,sp,dev,ch=best; res[k]=dict(z=v['z'],knots=n,max_dev_at_stations=float(dev),sign_changes=ch)
    print('WL %-3s interior knots %2d | max distance to the station crossings %.2f mm | curvature sign changes %d'%(k,n,dev,ch))
    for a,(xl,yl) in zip(axs,(((-10,570),(0,80)),((420,570),(0,60)))):
        t_=np.linspace(x[0],x[-1],1500); a.plot(t_,sp(t_),color=cols[k],lw=1.3); a.plot(st[:,0],st[:,1],'o',color=cols[k],mfc='none',ms=7); a.set_xlim(*xl); a.set_ylim(*yl)
for a in axs: a.set_aspect('equal'); a.grid(alpha=.25)
axs[0].set_title('Smooth waterlines: least-squares spline with the fewest knots, every station crossing within %.2f mm (circles)'%TOL); fig.savefig('qa/wl_new_smooth_v1.png',dpi=55,bbox_inches='tight'); json.dump(res,open('data/wl_new_smooth_v1.json','w'))
