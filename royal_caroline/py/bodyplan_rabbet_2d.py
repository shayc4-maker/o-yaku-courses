# body plan (approved station lines, data/bodyplan_splines_v1.json) stations 1-8 with the rabbet Z at each station X (data/rabbet_points_v1.json)
import json,numpy as np
from scipy.interpolate import CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4}
C=json.load(open('data/bodyplan_splines_v1.json')); pts=json.load(open('data/rabbet_points_v1.json'))['points']; R=CubicSpline([p[0] for p in pts],[p[1] for p in pts],bc_type='natural')
fig,axs=plt.subplots(2,2,figsize=(18,18),gridspec_kw={'height_ratios':[1.6,1]}); cm=plt.cm.tab10
for n in range(1,9):
    v=np.array(C[str(n)]['curve']); zr=float(R(XST[n])); col=cm((n-1)%10); lab='%d (X=%.1f, rabbet Z %.2f)'%(n,XST[n],zr)
    for r in (0,1):
        for c in (0,1):
            a=axs[r,c]; a.plot(np.r_[-v[::-1,0],v[:,0]],np.r_[v[::-1,1],v[:,1]],color=col,lw=1.1,label=lab if (r,c)==(0,0) else None)
            a.plot([-v[0,0],v[0,0]],[zr,zr],color=col,lw=.6,ls='--'); a.plot([v[0,0]],[v[0,1]],'x',color=col,ms=5)
    print('station',n,'X',XST[n],'line starts Y %.2f Z %.2f | rabbet Z %.2f | diff (line end - rabbet) %.2f'%(v[0,0],v[0,1],zr,v[0,1]-zr))
for (r,c),(xl,yl,t) in {(0,0):((-85,85),(-5,120),'body plan stations 1-8'),(0,1):((-14,14),(0,35),'bottom zoom, stations 1-8'),(1,0):((-14,14),(0,16),'stations 4-8'),(1,1):((-14,14),(16,36),'stations 1-2')}.items():
    a=axs[r,c]; a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(t); a.axvline(2.65,color='gray',lw=.5); a.axvline(-2.65,color='gray',lw=.5)
axs[0,0].legend(fontsize=7,loc='upper center'); fig.suptitle('Approved body plan, stations 1-8 (forward). x = start of the station line; dashed = rabbet Z at the station X (sheer plan)')
fig.savefig('qa/bodyplan_rabbet_1_8.png',dpi=55,bbox_inches='tight')
