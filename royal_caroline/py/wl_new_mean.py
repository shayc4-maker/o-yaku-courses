# smooth "mean" waterlines: least-squares cubic B-spline with NK interior knots through all points (stations and shifted plan points, equal weight); reports how far each station crossing is from the smooth line (Y and the equivalent Z error) and the curvature sign changes
import json,numpy as np,sys
from scipy.interpolate import make_lsq_spline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
NK=int(sys.argv[1]) if len(sys.argv)>1 else 8
D=json.load(open('data/wl_new_points_v1.json')); C=json.load(open('data/bodyplan_splines_v1.json'))
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
def slope(n,z):
    L=np.array(C[str(n)]['curve']); i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0][0]; dy=L[i+1,0]-L[i,0]; dz=L[i+1,1]-L[i,1]; return abs(dz/dy) if abs(dy)>1e-9 else 50.0
def sc(sp,x0,x1,thr=1e-3):
    t=np.linspace(x0,x1,4000); k=sp(t,2); s=np.sign(k[np.abs(k)>thr]); return int((np.diff(s)!=0).sum())
cols=dict(zip(['I','II','III','IV','V','VI','VII'],['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
fig,axs=plt.subplots(2,1,figsize=(20,16),gridspec_kw={'height_ratios':[1,1.2]}); res={}
for k,v in D.items():
    pts=np.array([[p[0],p[1]] for p in v['points']]); typ=np.array([p[2] for p in v['points']]); z=v['z']; x=pts[:,0]; y=pts[:,1]; st=typ=='station'
    ki=np.linspace(x[0],x[-1],NK+2)[1:-1]; t=np.r_[[x[0]]*4,ki,[x[-1]]*4]; sp=make_lsq_spline(x,y,t,k=3)
    dy=np.abs(sp(x[st])-y[st]); dz=[dy[j]*slope(min(XST,key=lambda m:abs(XST[m]-x[st][j])),z) for j in range(st.sum())]
    res[k]=dict(z=z,knots=NK,max_station_dev_Y=float(dy.max()),max_station_dev_Z=float(max(dz)),mean_station_dev_Y=float(dy.mean()),sign_changes=sc(sp,x[0],x[-1]))
    print('WL %-3s NK=%d | station crossings off the smooth line: max %.2f mm in Y (%.2f mm in Z), mean %.2f mm | curvature sign changes %d'%(k,NK,dy.max(),max(dz),dy.mean(),res[k]['sign_changes']))
    for a,(xl,yl) in zip(axs,(((-10,570),(0,80)),((420,570),(0,60)))):
        t_=np.linspace(x[0],x[-1],1500); a.plot(t_,sp(t_),color=cols[k],lw=1.3); a.plot(x[st],y[st],'o',color=cols[k],mfc='none',ms=7); a.set_xlim(*xl); a.set_ylim(*yl)
for a in axs: a.set_aspect('equal'); a.grid(alpha=.25)
axs[0].set_title('Smooth mean waterlines (%d interior knots): circles = station crossings (approved body plan), the line passes near them, not through'%NK); fig.savefig('qa/wl_new_mean_v1.png',dpi=55,bbox_inches='tight'); json.dump(res,open('data/wl_new_mean_v1.json','w'))
