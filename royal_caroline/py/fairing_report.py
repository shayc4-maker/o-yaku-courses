import json,numpy as np,sys
sys.argv=[sys.argv[0]]
exec(open('py/fairing.py').read().split("print('station: max point shift")[0])
from scipy.spatial import cKDTree
print('station | curvature sign changes (same method) original -> faired | max distance faired curve to the original curve (mm)')
for n in XST:
    o=curve_of(orig[n],n); new=curves[n]; t=cKDTree(o); dd=t.query(new[::3])[0].max(); print(' st %2d | %d -> %d | %.2f'%(n,station_sc(o),station_sc(new),dd))
cols=plt.cm.tab20(np.linspace(0,1,20)); XS=XST
fig,axs=plt.subplots(1,3,figsize=(24,12))
for n in XST:
    o=curve_of(orig[n],n); new=curves[n]; s=1 if n<=8 else -1; c=cols[(n*3)%20]
    for a in axs[:2]: a.plot(s*o[:,0],o[:,1],color='k',lw=.6); a.plot(s*new[:,0],new[:,1],color=c,lw=1.2)
    a=axs[0]; 
axs[0].set_xlim(-85,85); axs[0].set_ylim(-3,125); axs[0].set_aspect('equal'); axs[0].set_title('body plan: original (black) vs faired (colour): 1-8 right, 9-18 left')
axs[1].set_xlim(20,75); axs[1].set_ylim(35,80); axs[1].set_aspect('equal'); axs[1].set_title('zoom at the bilge (forward stations, right side)')
cl=dict(zip(WL,['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
for k,z in WL.items():
    P=np.array(W[k]['points_XY']); t=np.linspace(wlsp[k].t[0],wlsp[k].t[-1],1500); axs[2].plot(t,wlsp[k](t),color=cl[k],lw=1.3); axs[2].plot(P[:,0],P[:,1],'.',color=cl[k],ms=2,alpha=.5)
    for n in XST:
        c=cross(curves[n],z)
        if c is not None: axs[2].plot(XST[n],c,'o',mfc='none',mec=cl[k],ms=6)
axs[2].set_aspect('equal'); axs[2].set_xlim(-10,570); axs[2].set_ylim(0,80); axs[2].set_title('faired waterlines I-VII; circles = faired station crossings, dots = original plan points')
for a in axs: a.grid(alpha=.25)
fig.savefig('qa/fairing_v1.png',dpi=55,bbox_inches='tight')
fig,axs=plt.subplots(2,1,figsize=(20,14))
for k,z in WL.items():
    P=np.array(W[k]['points_XY']); t=np.linspace(wlsp[k].t[0],wlsp[k].t[-1],1500)
    for a,(xl,yl) in zip(axs,(((-10,570),(0,80)),((420,570),(0,60)))):
        a.plot(t,wlsp[k](t),color=cl[k],lw=1.3); a.plot(P[:,0],P[:,1],'.',color=cl[k],ms=3,alpha=.5); a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.25)
        for n in XST:
            c=cross(curves[n],z)
            if c is not None: a.plot(XST[n],c,'o',mfc='none',mec=cl[k],ms=7)
axs[0].set_title('Faired waterlines I-VII (top view): circles = faired stations crossing, dots = original plan points')
fig.savefig('qa/fairing_waterlines_v1.png',dpi=55,bbox_inches='tight')
