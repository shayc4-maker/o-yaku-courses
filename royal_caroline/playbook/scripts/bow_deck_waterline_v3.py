# deck WL Z=101 v3: frame crossings (iron, X<=528.1) + the builder's red sketch (read from his screenshot, X>531) + rabbet end; weighted smoothing spline s=0.4 -> rounder forward, tangent-continuous with the part through the frames; planes 2-5 re-fitted to it
import json,numpy as np
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D2=json.load(open('data/bow_deck_waterline_v2.json')); Q=np.array(D2['points']); PS=json.load(open('data/bow_plane_sketch_v5.json')); W=json.load(open('data/wl_top_centered_v1.json'))
px=[(880,338),(1000,375),(1130,425),(1250,490),(1400,590),(1500,690),(1600,820),(1680,960),(1730,1080),(1752,1198)]
red=np.array([(480+(a-377)/17.19,(1225-b)/17.17) for a,b in px]); fr=Q[Q[:,0]<=528.1]
pts=np.vstack([fr,red[red[:,0]>531],[[560.14,1.8]]]); pts=pts[np.argsort(pts[:,0])]; w=np.ones(len(pts)); w[-1]=50
tck,u=splprep(pts.T,k=3,w=w,s=0.4); uu=np.linspace(0,1,1500); X,Y=splev(uu,tck); d1=splev(uu,tck,der=1); d2=splev(uu,tck,der=2); k=(d1[0]*d2[1]-d1[1]*d2[0])/(d1[0]**2+d1[1]**2)**1.5
print('curvature sign changes',int((np.diff(np.sign(k[np.abs(k)>1e-3]))!=0).sum()),'min radius %.0f'%(1/abs(k).max()))
C=np.c_[X,Y]; print('max dev from frame crossings %.2f; from the red sketch %.2f'%(max(np.min(np.hypot(*(C-p).T)) for p in fr),max(np.min(np.hypot(*(C-p).T)) for p in red[1:])))
Yp=[PS[str(j)]['Y'] for j in range(5)]; tops={j:float(np.interp(Yp[j],Y[::-1],X[::-1])) for j in range(1,5)}; print({j:round(x,2) for j,x in tops.items()})
json.dump(dict(Z=101.0,points=pts.tolist(),smooth_s=0.4,curve=[[float(a),float(b)] for a,b in zip(X[::5],Y[::5])],plane_tops={str(j):[tops[j],Yp[j],101.0] for j in tops}),open('data/bow_deck_waterline_v3.json','w'))
fig,ax=plt.subplots(figsize=(14,10)); ax.plot(X,Y,'-',color='tab:orange',lw=2.5,label='deck WL Z=101 v3'); ax.plot(red[:,0],red[:,1],'--',color='r',lw=1.2,label='your red sketch'); ax.plot(fr[:,0],fr[:,1],'k.',ms=6)
for j,x in tops.items(): ax.plot(x,Yp[j],'bo'); ax.text(x+.6,Yp[j],'plane %d X%.1f'%(j+1,x))
cols=dict(zip('I II III IV V VI VII'.split(),plt.cm.viridis(np.linspace(0,.9,7))))
for kk,v in W.items(): P=np.array(v['points_XY']); m=P[:,0]>470; ax.plot(P[m,0],P[m,1],color=cols[kk],lw=1,label='WL %s'%kk)
ax.set_xlim(470,565); ax.set_ylim(0,65); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(fontsize=8); ax.set_title('deck-level WL v3 (rounder, tangent to the frame part)'); fig.savefig('qa/bow_deck_waterline_v3.png',dpi=65,bbox_inches='tight')
