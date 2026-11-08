# 2D study: keelson top line as an OFFSET of the new underside (constant normal thickness), vs the STEP top; thickness along X; aft joint zoom
import json,re,sys,numpy as np; sys.argv=['x']
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
NP=json.load(open('data/keel_keelson_points_v1.json')); PR=json.load(open('data/step44_profiles.json'))
def curve(k,n=8000):
    P=np.array(NP[k]['points']); tck,_=splprep(P.T,k=3,s=0); X,Z=splev(np.linspace(0,1,n),tck); return X,Z,tck
Xu,Zu,_=curve('keelson_under'); Xt,Zt,_=curve('keelson_top')
d1=np.gradient(Zu,Xu); nrm=np.c_[-d1,np.ones_like(d1)]; nrm/=np.hypot(*nrm.T)[:,None]
def offset_top(tfun):
    t=tfun(Xu); Q=np.c_[Xu,Zu]+nrm*t[:,None]; return Q[:,0],Q[:,1]
def curv(x,z):
    d1=np.gradient(z,x); d2=np.gradient(d1,x); return d2/(1+d1**2)**1.5
OPT={'A: constant 6.0':lambda x:np.full_like(x,6.0),
     'B: 6.0 midship, tapering to 5.0 at the stem start and 5.0 at the stern end':lambda x:np.interp(x,[45,120,200,400,526.6],[5.0,5.6,6.0,6.0,5.0])}
res={}
for nm,f in OPT.items():
    x,z=offset_top(f); res[nm]=(x,z); 
    ztop0=np.interp(x,Xt,Zt); dz=z-ztop0; k=curv(x,z); sc=int((np.diff(np.sign(k[np.abs(k)>1e-4]))!=0).sum())
    print('%-70s top moves vs STEP top: %.2f..%.2f mm (at stern X50 %.2f, X300 %.2f, X520 %.2f); curvature sign changes %d'%(nm,dz.min(),dz.max(),np.interp(50,x,dz),np.interp(300,x,dz),np.interp(520,x,dz),sc))
fig,axs=plt.subplots(3,1,figsize=(18,18),gridspec_kw={'height_ratios':[1.3,0.8,1.3]})
a=axs[0]; a.plot(Xu,Zu,'g',lw=1.5,label='underside (new)'); a.plot(Xt,Zt,'k',lw=1.5,label='top (STEP, smoothed)')
for (nm,(x,z)),c in zip(res.items(),('tab:red','tab:blue')): a.plot(x,z,c,lw=1.2,ls='--',label=nm)
a.set_xlim(40,545); a.set_ylim(0,55); a.set_aspect('equal'); a.grid(alpha=.3); a.legend(fontsize=8); a.set_title('keelson, side view')
a=axs[1]; Tn=[]
for i in range(0,len(Xu),20):
    p=np.array([Xu[i],Zu[i]]); s=np.linspace(0,60,3001); q=p[None,:]+s[:,None]*nrm[i][None,:]; zt=np.interp(q[:,0],Xt,Zt,left=np.nan,right=np.nan); r=q[:,1]-zt; ok=np.where(np.isfinite(r))[0]; j=ok[np.where(np.diff(np.sign(r[ok]))!=0)[0]]
    Tn.append((Xu[i],s[j[0]] if len(j) else np.nan))
Tn=np.array(Tn); a.plot(Tn[:,0],Tn[:,1],'k',label='STEP top (normal thickness)')
for nm,f in OPT.items(): a.plot(Xu[::20],f(Xu[::20]),ls='--',label=nm)
a.set_ylim(2,7); a.grid(alpha=.3); a.legend(fontsize=8); a.set_title('keelson thickness along X (mm)')
a=axs[2]
cols={'Boss-Extrude3[3]':'tab:brown','Boss-Extrude4[4]':'tab:green'}
for k,c in cols.items():
    from shapely.geometry import Polygon
    P=np.array(max(PR[k],key=lambda q:Polygon(q).area)); a.fill(P[:,0],P[:,1],color=c,alpha=.25); a.plot(P[:,0],P[:,1],color=c,lw=1)
a.text(33,45.5,'stern knee (Boss-Extrude3[3])',color='tab:brown'); a.text(60,24,'keelson (Boss-Extrude4[4])',color='tab:green')
a.plot(Xu,Zu,'g',lw=1.5); a.plot(Xt,Zt,'k',lw=1.2,label='STEP top (shared edge knee/keelson)')
for (nm,(x,z)),c in zip(res.items(),('tab:red','tab:blue')): a.plot(x,z,c,lw=1.3,ls='--',label=nm.split(':')[0])
a.annotate('notch 1.16 mm:\n(36.9,36.9)->(41.23,36.9)->(41.25,38.06)',xy=(41.2,37.5),xytext=(24,32),arrowprops=dict(arrowstyle='->'),fontsize=9)
a.set_xlim(22,70); a.set_ylim(26,50); a.set_aspect('equal'); a.grid(alpha=.3); a.legend(fontsize=8); a.set_title('aft joint: stern knee rests on the keelson top; the knee has a 1.16 mm notch at the aft end')
fig.savefig('qa/keelson_top_offset_2d_v1.png',dpi=55,bbox_inches='tight')
