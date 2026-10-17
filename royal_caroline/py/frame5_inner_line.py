# 2D test, builder's frame 5 (= our frame 41): inner line from the plan-derived outer line; offset 5.0 mm at the base point shrinking linearly (by arc length) to 4.3 mm at the top; built from a few points joined by a spline
import json,numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
P=json.load(open('data/frame_pieces_v10.json'))['pieces']
sel=[p for p in P if p['frame']==41 and p['layer']=='A' and p['side'] in('S','C')]
parts=[]
for p in sel:
    g=Polygon(p['poly']).buffer(0)
    if p['side']=='C': g=g.intersection(box(0,-10,100,200))
    parts.append(g)
U=unary_union([g.buffer(0.02) for g in parts]).buffer(-0.02); ring=np.array(U.exterior.coords)[:-1]
ib=int(np.argmin(ring[:,1]+0.001*ring[:,0])); it=int(np.argmax(ring[:,1]*1000+ring[:,0]))
def chain(a,b):
    n=len(ring); idx=[a]
    while idx[-1]!=b: idx.append((idx[-1]+1)%n)
    return ring[idx]
c1,c2=chain(ib,it),chain(it,ib)[::-1]
outer,inner_old=(c1,c2) if c1[:,0].mean()>c2[:,0].mean() else (c2,c1)
# the outer line from the plans: arc-length parametrized, base point -> top
s=np.r_[0,np.cumsum(np.hypot(*np.diff(outer,axis=0).T))]; L=s[-1]
def O(t): return np.c_[np.interp(t,s,outer[:,0]),np.interp(t,s,outer[:,1])]
# normal (inward) along the line, from a lightly smoothed tangent
tt=np.linspace(0,L,400); Pt=O(tt); tk,_=splprep(Pt.T,k=3,s=len(tt)*0.05); u=np.linspace(0,1,400); x,y=splev(u,tk); dx,dy=splev(u,tk,der=1)
n_in=np.c_[-dy,dx]/np.hypot(dx,dy)[:,None]
# make sure the normal points inward (towards the inner chain)
mid=len(x)//2; 
if np.dot(n_in[mid],(inner_old[len(inner_old)//2]-np.array([x[mid],y[mid]])))<0: n_in=-n_in
arc=np.r_[0,np.cumsum(np.hypot(np.diff(x),np.diff(y)))]; d=5.0+(4.3-5.0)*arc/arc[-1]
dense=np.c_[x,y]+n_in*d[:,None]
# the new line from a few points joined by a spline: points at equal arc length
K=8; ids=[int(round(i*(len(x)-1)/(K-1))) for i in range(K)]; pts=dense[ids]
tk2,_=splprep(pts.T,k=3,s=0); xs,ys=splev(np.linspace(0,1,300),tk2)
dev=np.abs(np.hypot(*(np.c_[xs,ys][:,None,:]-dense[None,:,:]).transpose(2,0,1)).min(axis=1)).max()
fig,ax=plt.subplots(1,2,figsize=(14,10))
for a,(xl,yl) in zip(ax,(((0,70),(0,150)),((0,45),(0,50)))):
    a.plot(outer[:,0],outer[:,1],'b',lw=2,label='outer line (plans, piece outline)'); a.plot(inner_old[:,0],inner_old[:,1],color='gray',lw=1,ls=':',label='old inner edge of the pieces')
    a.plot(xs,ys,'r',lw=2,label=f'new inner line: spline through {K} points, offset 5.0 -> 4.3 mm'); a.plot(pts[:,0],pts[:,1],'ro',ms=5)
    for i in (0,len(x)//2,len(x)-1):
        a.plot([x[i],dense[i,0]],[y[i],dense[i,1]],'k',lw=.8); a.text((x[i]+dense[i,0])/2,(y[i]+dense[i,1])/2,f'{d[i]:.1f}',fontsize=8)
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].legend(fontsize=8); ax[0].set_title('builder frame 5 (our frame 41, layer A, S side)'); ax[1].set_title('zoom on the base')
plt.savefig('qa/frame5_inner_line_2d.png',dpi=70,bbox_inches='tight')
print('outer length %.1f mm, base point %s, top point %s, spline vs exact offset max dev %.3f mm'%(L,outer[0].round(1),outer[-1].round(1),dev))
