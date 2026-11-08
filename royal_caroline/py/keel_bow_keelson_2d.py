# bow end v2 (2D): the keelson sits ON the keel/stem line. The chain (keel top R1 -> stem inner line R3, one tangent chain) is the contact surface; the keelson underside and the keelson top both merge TANGENTIALLY into that chain (underside at C1, top at C2 = the tip of the keelson wedge)
import json,numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import Polygon
D=json.load(open('data/keel_keelson_2d_v2.json')); CH=json.load(open('data/keel_bow_chains_2d_v1.json')); PR=json.load(open('data/step44_profiles.json'))
INNER=np.array(CH['inner']); BL=np.array(CH['stem_front']); U=np.array(D['underside']); T=np.array(D['keelson_top'])
unit=lambda d:d/np.hypot(*d); ang=lambda d:np.degrees(np.arctan2(d[1],d[0]))
# chain, resampled by arclength
s=np.r_[0,np.cumsum(np.hypot(*np.diff(INNER,axis=0).T))]; ss=np.arange(0,s[-1],0.25); CHn=np.c_[np.interp(ss,s,INNER[:,0]),np.interp(ss,s,INNER[:,1])]
def tan(P,i,k=6): return unit(P[min(i+k,len(P)-1)]-P[max(i-k,0)])
def bez(P0,d0,P3,d3,h0,h1,n=120):
    L=np.hypot(*(P3-P0)); Pb=np.array([P0,P0+d0*h0*L,P3-d3*h1*L,P3]); t=np.linspace(0,1,n)[:,None]; return (1-t)**3*Pb[0]+3*(1-t)**2*t*Pb[1]+3*(1-t)*t**2*Pb[2]+t**3*Pb[3]
def kappa(P):
    d1=np.gradient(P,axis=0); d2=np.gradient(d1,axis=0); return (d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])/np.hypot(d1[:,0],d1[:,1])**3
def best_join(P0,d0,zr,name):
    out=None
    for i in range(len(CHn)):
        z=CHn[i,1]
        if not(zr[0]<=z<=zr[1]) or CHn[i,0]<P0[0]: continue
        d3=tan(CHn,i)
        for h in (0.25,0.35,0.45):
            B=bez(P0,d0,CHn[i],d3,h,h); k=kappa(B); k=k[3:-3]; sc=int((np.diff(np.sign(k[np.abs(k)>5e-3]))!=0).sum()); score=(sc,float(np.abs(k).max()))
            if out is None or score<out[0]: out=(score,i,B,h)
    sc,i,B,h=out; print('%s: joins the chain at (%.2f,%.2f), curve length %.1f mm, curvature sign changes %d, min radius %.1f mm, tangent difference at the join %.2f deg'%(name,CHn[i,0],CHn[i,1],np.sum(np.hypot(*np.diff(B,axis=0).T)),sc[0],1/sc[1],abs(ang(tan(CHn,i))-ang(unit(B[-1]-B[-4])))))
    return CHn[i],B
dU=unit(U[-1]-U[-6]); C1,BU=best_join(U[-1],dU,(34,46),'keelson underside -> chain')
dT=unit(T[-1]-T[-6]); C2,BT=best_join(T[-1],dT,(46,66),'keelson top -> chain (wedge tip)')
# contact length where the keelson underside lies on the chain
i1=int(np.argmin(np.hypot(*(CHn-C1).T))); i2=int(np.argmin(np.hypot(*(CHn-C2).T))); print('keelson rests on the chain between (%.1f,%.1f) and (%.1f,%.1f): %.1f mm of contact'%(C1[0],C1[1],C2[0],C2[1],(i2-i1)*0.25))
# thickness of the wedge on the way: vertical gap between top blend and chain at C1's X
json.dump(dict(underside_end=BU.tolist(),top_end=BT.tolist(),C1=C1.tolist(),C2=C2.tolist()),open('data/keel_bow_keelson_2d_v2.json','w'))
fig,ax=plt.subplots(1,2,figsize=(20,11))
for a,(x0,x1,z0,z1) in zip(ax,((515,575,15,118),(518,552,26,70))):
    for k,v in PR.items():
        for q in v:
            P=np.array(q)
            if P[:,0].max()>x0 and P[:,0].min()<x1 and np.ptp(P[:,0])<700: a.plot(P[:,0],P[:,1],color='0.8',lw=.7)
    a.plot(CHn[:,0],CHn[:,1],'m',lw=2.4,label='keel top -> stem inner line (one chain)'); a.plot(BL[:,0],BL[:,1],'b',lw=2,label='stem front to the step')
    a.plot(U[:,0],U[:,1],'g',lw=1.8,label='keelson underside'); a.plot(BU[:,0],BU[:,1],'g',lw=1.8,ls='--'); a.plot(T[:,0],T[:,1],'k',lw=1.8,label='keelson top'); a.plot(BT[:,0],BT[:,1],'k',lw=1.8,ls='--')
    a.plot(*C1,'go',ms=7); a.plot(*C2,'ko',ms=7)
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].legend(fontsize=8,loc='upper left'); fig.savefig('qa/keel_bow_keelson_2d_v2.png',dpi=55,bbox_inches='tight')
