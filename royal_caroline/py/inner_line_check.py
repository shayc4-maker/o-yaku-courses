import sys,numpy as np
b=int(sys.argv[1]); sys.argv=[sys.argv[0]]
import os; os.environ['NOSTEP']='1'
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline
import json
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0)
KT0=F.keel_levels
F.keel_levels=lambda X:(lambda X:(float(kK(X)),(float(sK(X)),KT0(X)[1][1])))(min(X,526.0)); F.PEN_LOW=V2['depth']
OUR=46-b; xc=F.XF[OUR-1]
for X in (xc-4,xc,xc+4):
    p,info=F.face_poly(X,X); I=info['I']; O=info['O']
    d=np.gradient(I,axis=0); dd=np.gradient(d,axis=0); k=(d[:,0]*dd[:,1]-d[:,1]*dd[:,0])/(d[:,0]**2+d[:,1]**2)**1.5
    sc=int((np.diff(np.sign(k[5:-5]))!=0).sum()); print('X %.1f inner line: %d points, curvature sign changes %d, max |kappa| %.3f'%(X,len(I),sc,abs(k[5:-5]).max()))
    d=np.gradient(O,axis=0); dd=np.gradient(d,axis=0); k=(d[:,0]*dd[:,1]-d[:,1]*dd[:,0])/(d[:,0]**2+d[:,1]**2)**1.5
    print('     outer line: curvature sign changes %d'%int((np.diff(np.sign(k[5:-5]))!=0).sum()))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
p,info=F.face_poly(xc,xc); I=info['I']; O=info['O']
fig,ax=plt.subplots(1,3,figsize=(20,8))
ax[0].plot(O[:,0],O[:,1],'b',lw=1); ax[0].plot(I[:,0],I[:,1],'r',lw=1); ax[0].set_aspect('equal'); ax[0].set_xlim(0,60); ax[0].set_ylim(20,115); ax[0].grid(alpha=.3)
def kap(P): d=np.gradient(P,axis=0); dd=np.gradient(d,axis=0); return (d[:,0]*dd[:,1]-d[:,1]*dd[:,0])/(d[:,0]**2+d[:,1]**2)**1.5
s=np.r_[0,np.cumsum(np.hypot(*np.diff(I,axis=0).T))]; ax[1].plot(s[5:-5],kap(I)[5:-5],'r'); ax[1].plot(np.r_[0,np.cumsum(np.hypot(*np.diff(O,axis=0).T))][5:-5],kap(O)[5:-5],'b'); ax[1].set_ylim(-.3,.3); ax[1].grid(alpha=.3); ax[1].set_title('curvature outer (blue) inner (red)')
ax[2].plot(O[:,0],O[:,1],'b',lw=1); ax[2].plot(I[:,0],I[:,1],'r',lw=1); ax[2].set_aspect('equal'); ax[2].set_xlim(30,60); ax[2].set_ylim(55,110); ax[2].grid(alpha=.3)
fig.savefig('/tmp/claude-0/x/inner1.png',dpi=50,bbox_inches='tight')
