import sys,json,numpy as np
from scipy.interpolate import UnivariateSpline
S=sys.argv[1]; OUT=S+'/out'
PXM=244.8; K=1000/PXM/48           # model mm per px (horizontal)
S_WL=(2104.73-1287.92)/8/PXM        # real m per WL unit (profile)
LV=[0,1,2,3,4,5,6,8]                # base,I..VI,VII in WL units
WLN=['BASE','I','II','III','IV','V','VI','VII']
WLY={'1a':[2113.24,2010.99,1907.20,1802.92,1699.13,1597.16,1493.06,1287.56],
     '1b':[2003.18,1902.94,1800.12,1694.90,1591.62,1489.78,1385.70,1182.74]}
CL={'1a':2394.0,'1b':2453.0}
ST_PROF=[4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40]
STX={18-i:(x-ST_PROF[0])*K for i,x in enumerate(ST_PROF)}   # station -> X model mm (fwd from st18)
def z_of_y(y,sheet):
    ys=np.array(WLY[sheet]); lv=np.array(LV,float)
    # piecewise linear; extrapolate with end segments
    zu=np.interp(y,ys[::-1],lv[::-1])
    lo=y>ys[0]; hi=y<ys[-1]
    zu=np.where(lo,(ys[0]-y)/(ys[0]-ys[1])*(lv[1]-lv[0]),zu)
    zu=np.where(hi,lv[-1]+(ys[-1]-y)/(ys[-2]-ys[-1])*(lv[-1]-lv[-2]),zu)
    return zu*S_WL*1000/48           # model mm above baseline
def smooth(c,rms=0.6):
    c=np.asarray(c,float); keep=np.ones(len(c),bool)
    for it in range(4):
        p=c[keep]; u=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]
        ok=np.r_[True,np.diff(u)>1e-6]; p,u=p[ok],u[ok]
        sx=UnivariateSpline(u,p[:,0],s=len(u)*rms**2); sy=UnivariateSpline(u,p[:,1],s=len(u)*rms**2)
        U=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]
        # residual of all pts vs nearest param approx: use own param for kept
        res=np.hypot(sx(u)-p[:,0],sy(u)-p[:,1])
        bad=res>max(2.0,3*np.sqrt((res**2).mean()))
        if not bad.any(): break
        idx=np.where(keep)[0][ok][bad]; keep[idx]=False
    uu=np.arange(0,u[-1],2.0); uu=np.r_[uu,u[-1]]
    return np.c_[sx(uu),sy(uu)], int((~keep).sum()), float(np.sqrt((res**2).mean()))
stations={}
for sheet,fn,sgn in [('1a','tr1a_fix.json',-1),('1b','tr1b_fix.json',+1)]:
    for k,c in json.load(open(S+'/'+fn)).items():
        sm,nrej,rms=smooth(c)
        Y=sgn*(sm[:,0]-CL[sheet])*K; Z=z_of_y(sm[:,1],sheet)
        P=np.c_[Y,Z]
        if P[0,1]>P[-1,1]: P=P[::-1]      # order keel -> top
        stations[(int(k),sheet)]=P
        print('st %2s %s pts %4d rejected %3d rms %.2fpx  Y[%.2f..%.2f] Z[%.2f..%.2f]'%(k,sheet,len(P),nrej,rms,P[:,0].min(),P[:,0].max(),P[:,1].min(),P[:,1].max()))
np.save(OUT+'/stations.npy',{f'{k}_{s}':v for (k,s),v in stations.items()},allow_pickle=True)
json.dump({'K':K,'S_WL_m':S_WL,'STX':STX,'WLZ_mm':{n:l*S_WL*1000/48 for n,l in zip(WLN,LV)}},open(OUT+'/meta.json','w'),indent=1)
# station 8 both halves compare
a=stations[(8,'1a')]; b=stations[(8,'1b')]
zz=np.linspace(max(a[:,1].min(),b[:,1].min())+1,min(a[:,1].max(),b[:,1].max())-1,200)
def yat(P,z):
    i=np.argsort(P[:,1]); return np.interp(z,P[i,1],P[i,0])
d=np.array([yat(a,z)-yat(b,z) for z in zz]); print('st8 1a-1b: mean %.2f rms %.2f max %.2f mm(model)'%(d.mean(),np.sqrt((d**2).mean()),abs(d).max()))
