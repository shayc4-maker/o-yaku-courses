# bow end study (2D): chain 1 = keel top (R1) continued by the stem inner line (R3) in ONE tangent chain; chain 2 = stem front (R2) continued down to the step (531.25,22.88) in ONE spline; keelson ends shown as proposed
import json,numpy as np
from scipy.interpolate import CubicSpline
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=[np.array(c['pts'])[:,[0,2]] for c in json.load(open('data/builder_ref_curves_keel_v1.json'))]; R1,R2,R3,R4,R5,R6,R7=R; PR=json.load(open('data/step44_profiles.json')); D=json.load(open('data/keel_keelson_2d_v2.json'))
unit=lambda d:d/np.hypot(*d); ang=lambda d:np.degrees(np.arctan2(d[1],d[0]))
def dens_bez(P0,d0,P3,d3,h0=0.38,h1=0.38,n=200):
    L=np.hypot(*(P3-P0)); Pb=np.array([P0,P0+d0*h0*L,P3-d3*h1*L,P3]); t=np.linspace(0,1,n)[:,None]; return (1-t)**3*Pb[0]+3*(1-t)**2*t*Pb[1]+3*(1-t)*t**2*Pb[2]+t**3*Pb[3]
def curv_poly(P):
    d1=np.gradient(P,axis=0); d2=np.gradient(d1,axis=0); return (d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])/np.hypot(d1[:,0],d1[:,1])**3
# R3 oriented upward (from the keelson end to the top)
R3u=R3[::-1]; d_r1=unit(R1[0]-R1[6])           # R1 runs stem->stern: its stem end tangent points forward-up
P0=R1[0]
best=None
for Zj in (40,44,48,52,56,60,66):
    i=int(np.argmin(np.abs(R3u[:,1]-Zj))); Pj=R3u[i]; dj=unit(R3u[min(i+4,len(R3u)-1)]-R3u[max(i-4,0)])
    B=dens_bez(P0,unit(R1[0]-R1[8]),Pj,dj); chain=np.vstack([R1[::-1][-30:],B,R3u[i+1:]]); k=curv_poly(chain); sc=int((np.diff(np.sign(k[np.abs(k)>2e-4]))!=0).sum())
    print('junction on R3 at Z=%d (X %.1f): blend length %.1f mm, tangent at R1 end %.1f deg, R3 tangent there %.1f deg, curvature sign changes %d, max|k| %.3f'%(Zj,Pj[0],np.hypot(*(Pj-P0)),ang(unit(R1[0]-R1[8])),ang(dj),sc,abs(k).max()))
    if best is None or (sc,abs(k).max())<best[0]: best=((sc,abs(k).max()),Zj,B,Pj,i)
_,Zj,B,Pj,ij=best; print('chosen junction Z',Zj)
INNER=np.vstack([R1[::-1],B,R3u[ij+1:]])
# chain 2: stem front: R2 (from the top) continued down to the step with the approved stem-front vertices, tangent clamped at the R2 end
S=np.array(max(PR['Boss-Extrude2[2]'],key=lambda q:Polygon(q).area)); m=(S[:,0]>=531.2)&(S[:,0]<=559.4)&(S[:,1]>22)&(S[:,1]<64.5)&(S[:,0]>520)
V=S[m]; V=V[np.argsort(V[:,1])]; _,ui=np.unique(V.round(2),axis=0,return_index=True); V=V[np.sort(ui)]; V=V[np.argsort(V[:,1])]
pick=[V[0]]+[v for v in V[1:-1] if v[1]>26 and (v[1]-pick_last if (pick_last:=0) else True)]
sel=[(531.25,22.88),(538.58,29.59),(545.24,36.96),(551.36,46.26),(555.34,53.58),(R2[-1,0],R2[-1,1])]
sel=np.array(sel); dR2=unit(R2[-1]-R2[-6]); 
# parametrise by Z (the line is steep): X(Z), clamped slope dX/dZ at both ends
zz=sel[:,1]; xx=sel[:,0]; sR2=dR2[0]/dR2[1]
# slope at the step end: from the approved vertices just below/above the step
sS=(538.58-531.25)/(29.59-22.88)*0+ (533.77-531.25)/(25.04-22.88)
f=CubicSpline(zz,xx,bc_type=((1,sS),(1,sR2)))
zs=np.linspace(22.88,63.1,300); BL=np.c_[f(zs),zs]
print('blue: R2 end (%.2f,%.2f) tangent %.1f deg; continued down to the step (531.25,22.88); the spline passes the approved vertices within %.2f mm'%(R2[-1,0],R2[-1,1],ang(-dR2),max(abs(f(v[1])-v[0]) for v in V if 22.9<v[1]<63)))
fig,ax=plt.subplots(1,2,figsize=(20,11)); 
for a,(x0,x1,z0,z1) in zip(ax,((515,575,15,118),(515,560,15,70))):
    for k,v in PR.items():
        for q in v:
            P=np.array(q)
            if P[:,0].max()>x0 and P[:,0].min()<x1 and np.ptp(P[:,0])<700: a.plot(P[:,0],P[:,1],color='0.75',lw=.7)
    a.plot(INNER[:,0],INNER[:,1],'m',lw=2.2,label='NEW chain: keel top R1 -> stem inner line R3 (one tangent chain)')
    a.plot(R1[:,0],R1[:,1],'r--',lw=1,label='R1'); a.plot(R3[:,0],R3[:,1],color='purple',ls=':',lw=1,label='R3 as it was')
    a.plot(R2[:,0],R2[:,1],'b--',lw=1,label='R2'); a.plot(BL[:,0],BL[:,1],'b',lw=2.2,label='NEW stem front: R2 continued to the step')
    a.plot(D['underside'][-1][0],D['underside'][-1][1],'go'); xs_=np.array(D['underside']); a.plot(xs_[:,0],xs_[:,1],'g',lw=1.5,label='keelson underside'); xs_=np.array(D['keelson_top']); a.plot(xs_[:,0],xs_[:,1],'k',lw=1.5,label='keelson top'); xs_=np.array(D['R4_rebuilt']); a.plot(xs_[:,0],xs_[:,1],'c',lw=1.5,label='keelson bow edge (R4, rebuilt)')
    a.plot([531.25],[22.88],'bs'); a.annotate('the step',(531.25,22.88),(520,30),arrowprops=dict(arrowstyle='->'))
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].legend(fontsize=8,loc='upper left'); fig.savefig('qa/keel_bow_chains_2d_v1.png',dpi=55,bbox_inches='tight')
json.dump(dict(inner=INNER.tolist(),stem_front=BL.tolist(),junction_Z=float(Zj)),open('data/keel_bow_chains_2d_v1.json','w'))
