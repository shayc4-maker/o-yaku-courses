# stem front line (blue): ONE tangent spline from the R2 curve (top) through the step vertex (531.25,22.88) down to the next junction (500.72,4.45), ends clamped to the neighbouring tangents
import json,numpy as np
from scipy.interpolate import CubicSpline
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R2=np.array(json.load(open('data/builder_ref_curves_keel_v1.json'))[1]['pts'])[:,[0,2]]; PR=json.load(open('data/step44_profiles.json'))
unit=lambda d:d/np.hypot(*d); ang=lambda d:np.degrees(np.arctan2(d[1],d[0]))
# nodes on the approved stem-front/forefoot line (top -> bottom)
nodes=np.array([R2[-1],(555.34,53.58),(551.36,46.26),(545.24,36.96),(538.58,29.59),(531.25,22.88),(523.96,17.38),(516.71,12.58),(509.07,7.88),(500.72,4.45)])
t=np.r_[0,np.cumsum(np.hypot(*np.diff(nodes,axis=0).T))]
dA=unit(R2[-1]-R2[-8])                       # R2 runs top->bottom: its end tangent points down
dB=unit(np.array([497.92,3.45])-np.array([500.72,4.45]))     # the approved line continues below the junction toward (497.92,3.45)
fx=CubicSpline(t,nodes[:,0],bc_type=((1,dA[0]),(1,dB[0]))); fz=CubicSpline(t,nodes[:,1],bc_type=((1,dA[1]),(1,dB[1])))
tt=np.linspace(0,t[-1],1500); C=np.c_[fx(tt),fz(tt)]
d1=np.c_[fx(tt,1),fz(tt,1)]; d2=np.c_[fx(tt,2),fz(tt,2)]; k=(d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])/np.hypot(*d1.T)**3
sc=int((np.diff(np.sign(k[np.abs(k)>1e-4]))!=0).sum()); print('stem front spline: %d nodes, length %.1f mm, curvature sign changes %d, min radius %.0f mm'%(len(nodes),t[-1],sc,1/abs(k).max()))
print('tangent at the R2 end: spline %.2f deg vs R2 %.2f deg ; at the junction: spline %.2f deg vs approved next segment %.2f deg'%(ang(unit(C[1]-C[0])),ang(dA),ang(unit(C[-1]-C[-2])),ang(dB)))
S=np.array(max(PR['Boss-Extrude2[1]'],key=lambda q:Polygon(q).area)); Su=S[np.r_[True,np.any(np.diff(S,axis=0)!=0,axis=1)]]; V=Su[(Su[:,0]>=500.7)&(Su[:,0]<=531.3)&(Su[:,1]>4.3)&(Su[:,1]<23)]
dev=[float(np.min(np.hypot(*(C-v).T))) for v in V]; print('approved vertices on this line (%d): max distance to the spline %.2f mm'%(len(V),max(dev)))
# the old (approved) polyline curvature along the same stretch, for comparison
O=np.array(sorted([tuple(v) for v in V],key=lambda p:-p[0])); ko=np.gradient(np.arctan2(*np.gradient(O,axis=0).T[::-1]))
json.dump(dict(spline=C.tolist(),nodes=nodes.tolist()),open('data/keel_stem_front_2d_v1.json','w'))
fig,ax=plt.subplots(1,2,figsize=(20,10))
for a,(x0,x1,z0,z1) in zip(ax,((490,575,-2,118),(494,545,0,35))):
    for kk,v in PR.items():
        for q in v:
            P=np.array(q)
            if P[:,0].max()>x0 and P[:,0].min()<x1 and np.ptp(P[:,0])<700: a.plot(P[:,0],P[:,1],color='0.78',lw=.7)
    a.plot(V[:,0],V[:,1],'k.',ms=5,label='approved vertices'); a.plot(C[:,0],C[:,1],'b',lw=2,label='new stem front spline (one piece)'); a.plot(nodes[:,0],nodes[:,1],'bo',ms=5); a.plot(R2[:,0],R2[:,1],'c--',lw=1,label='R2')
    a.plot([500.72],[4.45],'rs',ms=8); a.annotate('next junction (500.72, 4.45)',(500.72,4.45),(505,-0.5),fontsize=8); a.annotate('the step (531.25, 22.88)',(531.25,22.88),(512,27),arrowprops=dict(arrowstyle='->'),fontsize=8)
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].legend(fontsize=8); fig.savefig('qa/keel_stem_front_2d_v1.png',dpi=55,bbox_inches='tight')
