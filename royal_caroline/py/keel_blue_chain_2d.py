# the builder's R2 (stem front upper) and #180 (stem lower spline) as ONE tangent line: interpolating spline through nodes taken from both curves, end tangents clamped to the outer ends; the joint kink (15.9 deg) disappears
import json,numpy as np
from scipy.interpolate import CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=json.load(open('data/builder_ref_curves_keel_v2.json')); byi={r['i']:np.array(r['pts'])[:,[0,2]] for r in R}
R2=byi[174]; S=byi[180]
if np.hypot(*(S[0]-np.array([480.58,-0.66])))>1: S=S[::-1]
unit=lambda d:d/np.hypot(*d); ang=lambda d:np.degrees(np.arctan2(d[1],d[0]))
def along(P,n):   # n nodes at equal arclength incl. both ends
    s=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]; q=np.linspace(0,s[-1],n); return np.c_[np.interp(q,s,P[:,0]),np.interp(q,s,P[:,1])]
dA=unit(R2[1]-R2[0]); dB=unit(S[1]-S[0])      # outer end tangents: R2 top end (pointing down along the curve) and #180 bottom end (pointing up along the curve) -> chain runs top -> bottom, so flip the second
dB=-dB
def build(nR,nS,drop_joint=0):
    A=along(R2,nR); B=along(S[::-1],nS)              # B runs top -> bottom
    nodes=np.vstack([A[:-1] if drop_joint<1 else A[:-2],B[1:] if drop_joint<2 else B[2:]]) if drop_joint else np.vstack([A,B])
    t=np.r_[0,np.cumsum(np.hypot(*np.diff(nodes,axis=0).T))]
    fx=CubicSpline(t,nodes[:,0],bc_type=((1,dA[0]),(1,dB[0]))); fz=CubicSpline(t,nodes[:,1],bc_type=((1,dA[1]),(1,dB[1]))); tt=np.linspace(0,t[-1],4000); C=np.c_[fx(tt),fz(tt)]
    d1=np.c_[fx(tt,1),fz(tt,1)]; d2=np.c_[fx(tt,2),fz(tt,2)]; k=(d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])/np.hypot(*d1.T)**3
    sc=int((np.diff(np.sign(k[np.abs(k)>1e-4]))!=0).sum()); dev2=max(np.min(np.hypot(*(C-p).T)) for p in R2[::5]); dev180=max(np.min(np.hypot(*(C-p).T)) for p in S[::5])
    return C,nodes,sc,dev2,dev180,1/abs(k).max()
best=None
for nR,nS,dj in ((6,8,0),(5,8,0),(4,8,0),(5,7,0),(4,7,0),(5,8,1),(6,8,2),(4,9,0),(3,8,0)):
    C,nodes,sc,d2,d180,rmin=build(nR,nS,dj); print('R2 nodes %d, #180 nodes %d, drop %d: curvature sign changes %d, max distance from R2 %.2f mm, from #180 %.2f mm, min radius %.0f mm'%(nR,nS,dj,sc,d2,d180,rmin))
    sco=(sc,max(d2,d180))
    if best is None or sco<best[0]: best=(sco,C,nodes,(nR,nS,dj))
sco,C,nodes,cfg=best; print('chosen',cfg,sco)
json.dump(dict(chain=C.tolist(),nodes=nodes.tolist(),cfg=cfg),open('data/keel_blue_chain_2d_v1.json','w'))
fig,ax=plt.subplots(1,2,figsize=(20,11))
for a,(x0,x1,z0,z1) in zip(ax,((470,575,-5,118),(535,572,40,75))):
    a.plot(R2[:,0],R2[:,1],'c--',lw=1.2,label='R2 (yours)'); a.plot(S[:,0],S[:,1],'orange',ls='--',lw=1.2,label='#180 (yours)'); a.plot(C[:,0],C[:,1],'b',lw=2,label='ONE tangent chain'); a.plot(nodes[:,0],nodes[:,1],'bo',ms=4)
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].legend(fontsize=8); fig.savefig('qa/keel_blue_chain_2d_v1.png',dpi=55,bbox_inches='tight')
