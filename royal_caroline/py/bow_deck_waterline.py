# deck-level waterline (Z=101, the plane of the forward deck picture): ONE spline through the frame-face crossings at Z=101 (frames 1-8, all faces), the builder's top line as general reference for Y 11-30, ending on the rabbet at Z=101; planes 2-5 tops sit on it; WL I-VII for reference
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ZD=101.0
A=json.load(open('data/frames_outer_approved_v5.json')); W=json.load(open('data/wl_top_centered_v1.json')); HIS=np.array(json.load(open('data/deck_top_line_builder_v1.json'))); R=np.array(json.load(open('data/rabbet_iron_v4.json'))['curve']); PS=json.load(open('data/bow_plane_sketch_v5.json'))
def y_at_z(v,z):
    C=np.array(v['curve']); C=np.vstack([C,np.array(v['top'])[1:]]) if v.get('top') else C
    i=np.where((C[:-1,1]-z)*(C[1:,1]-z)<=0)[0]; return float(np.interp(z,C[i[0]:i[0]+2,1],C[i[0]:i[0]+2,0])) if len(i) and C[i[0]+1,1]!=C[i[0],1] else None
fr=[]
for b in range(8,0,-1):
    for nm in ('back','mid','front'):
        y=y_at_z(A[str(b)][nm],ZD); fr.append((A[str(b)][nm]['X'],y))
i=np.where((R[:-1,1]-ZD)*(R[1:,1]-ZD)<=0)[0][0]; xr=float(np.interp(ZD,R[i:i+2,1],R[i:i+2,0])); yr=1.8
Yp=[PS[str(j)]['Y'] for j in range(5)]
# builder's line as general reference: shifted so that it ends on the rabbet at Z=101, then only used for Y 11.6/20.6 (its end part is replaced by frame continuity)
xh=lambda y:float(np.interp(y,HIS[:,1],HIS[:,0])); d0=xr-xh(1.8)
ref=[(xh(y)+d0*max(0,1-(y-1.8)/36.4),y) for y in (Yp[1],Yp[2])]
pts=fr+ref+[(xr,yr)]; pts=sorted(set((round(x,3),round(y,3)) for x,y in pts)); Q=np.array(pts)
tck,u=splprep(Q.T,k=3,s=0); uu=np.linspace(0,1,1500); X,Y=splev(uu,tck); d1=splev(uu,tck,der=1); d2=splev(uu,tck,der=2); kap=(d1[0]*d2[1]-d1[1]*d2[0])/(d1[0]**2+d1[1]**2)**1.5
sc=int((np.diff(np.sign(kap[np.abs(kap)>1e-4]))!=0).sum()); print('deck WL through %d points; curvature sign changes %d'%(len(Q),sc))
xs_at=lambda y:float(np.interp(y,Y[::-1],X[::-1]))
tops={j:xs_at(Yp[j]) for j in range(1,5)}; print({j:round(x,2) for j,x in tops.items()}); print('rabbet end',round(xr,2))
json.dump(dict(Z=ZD,points=pts,curve=[[float(a),float(b)] for a,b in zip(X[::5],Y[::5])],plane_tops={str(j):[tops[j],Yp[j],ZD] for j in tops}),open('data/bow_deck_waterline_v1.json','w'))
# figure
fig,ax=plt.subplots(figsize=(14,10)); ax.plot(X,Y,'-',color='tab:orange',lw=2.5,label='deck-level WL Z=101 (one spline)'); ax.plot(Q[:,0],Q[:,1],'k.',ms=6); ax.plot(HIS[:,0],HIS[:,1],'--',color='gray',label='your top line (reference)')
for j,x in tops.items(): ax.plot(x,Yp[j],'ro'); ax.text(x+.6,Yp[j],'plane %d  X%.1f'%(j+1,x))
cols=dict(zip('I II III IV V VI VII'.split(),plt.cm.viridis(np.linspace(0,.9,7))))
for k,v in W.items(): P=np.array(v['points_XY']); m=P[:,0]>470; ax.plot(P[m,0],P[m,1],color=cols[k],lw=1,label='WL %s z=%.1f'%(k,v['z']))
ax.set_xlim(470,565); ax.set_ylim(0,65); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(fontsize=8,loc='upper right'); ax.set_title('top view: deck-level waterline through the frames, ending on the rabbet; other waterlines for reference')
fig.savefig('qa/bow_deck_waterline_v1.png',dpi=65,bbox_inches='tight')
