import sys,json,numpy as np
sys.path.insert(0,'py')
from frame_arm import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
b=int(sys.argv[1]); xc=F.XF[46-b-1]
p,i=arm(xc); I=None
# natural inner line (offset of the exact outer line) from the arm data: recompute
P=F.hull_line(xc); P=P[np.argsort(P[:,1])]; m=(P[:,0]<=P[0,0]+10); c=np.polyfit(P[m,0],P[m,1],3); ys=np.linspace(KB,P[0,0],12,endpoint=False); ext=np.c_[ys,np.polyval(c,ys)]; O=np.vstack([ext,P])
from scipy.signal import savgol_filter
sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]; N=np.c_[-d[:,1],d[:,0]]; I=O+N*T
fl,st=i['floor'],i['seat']; hk=i['hull_at_wall']
fig,axs=plt.subplots(1,3,figsize=(24,8))
tit=['A: straight line from the seat end to the natural inner line (at Y=%.0f)','B: vertical drop at the keel wall to the natural inner line, then it follows the offset','C: seat horizontal until it meets the inner line (width %s mm)']
for k,a in enumerate(axs):
    a.plot(O[:,0],O[:,1],'b',lw=1.3); a.plot(-O[:,0],O[:,1],'b',lw=1.3); a.plot(I[:,0],I[:,1],'g',lw=1,ls='--'); a.plot(-I[:,0],I[:,1],'g',lw=1,ls='--')
    a.plot([-KB,KB],[fl,fl],'k',lw=2); a.plot([-KB,KB],[st,st],'k',lw=2); a.plot([KB,KB],[hk,fl],'k',lw=2); a.plot([-KB,-KB],[hk,fl],'k',lw=2)
    for sg in (1,-1):
        if k==0: j=int(np.argmax(I[:,0]>=KB+8)); a.plot([sg*KB,sg*I[j,0]],[st,I[j,1]],'r',lw=2.2)
        if k==1: j=int(np.argmax(I[:,0]>=KB)); a.plot([sg*KB,sg*KB],[st,I[j,1]],'r',lw=2.2)
        if k==2:
            cr=np.where(I[:,1]>=st)[0]; j=cr[0]; a.plot([sg*KB,sg*I[j,0]],[st,st],'r',lw=2.2)
    if k==2: ttl=tit[2]%('%.1f'%(2*I[cr[0],0]))
    elif k==0: ttl=tit[0]%(KB+8)
    else: ttl=tit[1]
    a.set_title(ttl,fontsize=10); a.set_aspect('equal'); a.set_xlim(-30,30); a.set_ylim(fl-5,st+8); a.grid(alpha=.3)
fig.savefig('qa/frame%d_variants.png'%b,dpi=55,bbox_inches='tight'); print('floor %.2f seat %.2f hull at wall %.2f; natural inner at the wall %.2f'%(fl,st,hk,I[0,1]))
