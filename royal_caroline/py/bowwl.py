import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from track import *
S=sys.argv[2]
PV=np.array([4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28])
PR=np.array([4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40])
f=np.polyfit(PV,PR,1); LO=(-0.00716,1271.3); K=1000/244.8/48
px=lambda X:(X/K+PR[0]-f[1])/f[0]
def mdl(u,v): X=(np.polyval(f,u)-PR[0])*K; return X,(np.polyval(LO,u)-v)*K
img=S+'/a/plan_1b_aligned.png'; D=load_dark(img); B=np.array(Image.open(img).convert('L'))<128
u=int(px(492)); cl=np.polyval(LO,u)
col=B[int(cl-70/K):int(cl-4/K),u]; runs=[];s=None
for i,v in enumerate(col):
    if v and s is None: s=i
    if not v and s is not None: runs.append((s+i-1)/2+int(cl-70/K)); s=None
print('X492 crossings Y:',[round(float((cl-r)*K),1) for r in runs])
keep=[r for r in runs if not (39.0<(cl-r)*K<44.0)]
runs=keep; names=['VII','VI','V','IV','III','II','I'][:len(runs)]
ylim=lambda p: np.polyval(LO,p[0])-p[1] < 3.6/K
stop=lambda p: p[0]<px(470) or p[0]>px(575) or ylim(p)
out={}
for nm,r in zip(names,runs):
    c=trace(D,(u,r),np.array([1.0,0.25]),stop,maxang=8,look=20)
    X,Y=mdl(c[:,0],c[:,1]); out[nm]=np.c_[X,Y].tolist()
    print(nm,'start Y %.1f'%Y[0],'end X %.2f Y %.2f'%(X[-1],Y[-1]),len(c))
json.dump(out,open(S+'/out/bow_wl_A14.json','w'))
