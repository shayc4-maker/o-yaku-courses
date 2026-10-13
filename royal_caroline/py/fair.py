import sys,json,numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=sys.argv[1]
meta=json.load(open(S+'/out/meta.json')); K=meta['K']; WLZ=meta['WLZ_mm']; STX={int(k):v for k,v in meta['STX'].items()}
st=np.load(S+'/out/stations.npy',allow_pickle=True).item()
PV=np.array([4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28])
PR=np.array([4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40])
f=np.polyfit(PV,PR,1); print('plan->profile x fit',f, 'rms',np.sqrt(np.mean((np.polyval(f,PV)-PR)**2)))
LO=(-0.00716,1271.3)
def ycross(P,z):
    out=[]
    for i in range(len(P)-1):
        z0,z1=P[i,1],P[i+1,1]
        if (z0-z)*(z1-z)<=0 and z0!=z1:
            t=(z-z0)/(z1-z0); out.append(P[i,0]+t*(P[i+1,0]-P[i,0]))
    return max(out) if out else np.nan
pv=json.load(open(S+'/trpv.json'))
WLN=['I','II','III','IV','V','VI','VII']
fig,axs=plt.subplots(7,1,figsize=(11,17),sharex=True)
report={}
for ax,n in zip(axs,WLN):
    xs=[];ys=[]
    for s in range(1,19):
        P=st.get(f'{s}_1a', st.get(f'{s}_1b')); y=ycross(P,WLZ[n])
        if not np.isnan(y) and y>3.3: xs.append(STX[s]); ys.append(y)
    xs=np.array(xs); ys=np.array(ys); o=np.argsort(xs); xs,ys=xs[o],ys[o]
    ax.plot(xs,ys,'o-',color='C0',label='body plan sections (this trace)')
    if n in pv:
        c=np.array(pv[n]); X=(np.polyval(f,c[:,0])-PR[0])*K; Y=(np.polyval(LO,c[:,0])-c[:,1])*K
        if n in ('VI','VII'):
            m=X<(6500-PR[0])*K; ax.plot(X[m],Y[m],'-',color='C3',lw=1,label='half-breadth plan A1/4')
        else: ax.plot(X,Y,'-',color='C3',lw=1,label='half-breadth plan A1/4')
        # diffs at stations
        d=[]
        for x,y in zip(xs,ys):
            j=np.argmin(abs(X-x))
            if abs(X[j]-x)<1 and not (n in('VI','VII') and x>(6500-PR[0])*K): d.append(Y[j]-y)
        report[n]=np.round(d,2).tolist()
    # fairness of body-plan WL: deviation from smoothing spline through station points
    if len(xs)>5:
        from scipy.interpolate import UnivariateSpline
        sp=UnivariateSpline(xs,ys,s=len(xs)*0.15**2); r=ys-sp(xs)
        report[n+'_bodyfair_rms']=float(np.sqrt((r**2).mean())); report[n+'_bodyfair_max']=float(abs(r).max())
    ax.set_ylabel(f'WL {n}\nY mm'); ax.grid(alpha=.3)
axs[0].legend(loc='lower center'); axs[-1].set_xlabel('X model mm from station 18 (1:48)')
fig.suptitle('Royal Caroline 1:48 - waterline half-breadths: body plan vs half-breadth plan'); fig.tight_layout(); fig.savefig(S+'/out/compare_waterlines.png',dpi=90)
for k,v in report.items(): print(k,v)
# scale fit: plan = a * body
B=[];Pp=[];info=[]
for n in WLN:
    if n not in pv: continue
    c=np.array(pv[n]); X=(np.polyval(f,c[:,0])-PR[0])*K; Y=(np.polyval(LO,c[:,0])-c[:,1])*K
    for s in range(1,19):
        P=st.get(f'{s}_1a', st.get(f'{s}_1b')); y=ycross(P,WLZ[n]); x=STX[s]
        if np.isnan(y) or y<3.3: continue
        if n in('VI','VII') and x>(6500-PR[0])*K: continue
        j=np.argmin(abs(X-x))
        if abs(X[j]-x)<1: B.append(y); Pp.append(Y[j]); info.append((s,n))
B=np.array(B);Pp=np.array(Pp)
a=(B*Pp).sum()/(B*B).sum(); r=Pp-a*B
print('N',len(B),'best scale plan/body = %.4f'%a,' resid rms %.2f mm, max %.2f'%(np.sqrt((r**2).mean()),abs(r).max()))
print('raw diff rms %.2f'%np.sqrt(((Pp-B)**2).mean()))
for (s,n),v in zip(info,r):
    if abs(v)>1.0: print('  big resid st',s,n,'%.2f'%v)
