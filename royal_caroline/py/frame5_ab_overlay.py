# 2D: builder's frame 5 (our 41, X 480.3) line A + exact parallel 3.2 mm inward; line B = same for the next frame (builder 6 = our 40, X 468.4); overlaid
import json,numpy as np
from shapely.geometry import Polygon,LineString,box
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
P=json.load(open('data/frame_pieces_v10.json'))['pieces']; X=json.load(open('data/frames_X.json'))['X_mm']
def outer_line(fr):
    sel=[p for p in P if p['frame']==fr and p['layer']=='A' and p['side'] in('S','C')]
    U=unary_union([(Polygon(p['poly']).buffer(0).intersection(box(0,-10,100,200)) if p['side']=='C' else Polygon(p['poly']).buffer(0)).buffer(0.02) for p in sel]).buffer(-0.02)
    ring=np.array(U.exterior.coords)[:-1]; ib=int(np.argmin(ring[:,1]+0.001*ring[:,0])); it=int(np.argmax(ring[:,1]*1000+ring[:,0]))
    def chain(a,b):
        idx=[a]
        while idx[-1]!=b: idx.append((idx[-1]+1)%len(ring))
        return ring[idx]
    c1,c2=chain(ib,it),chain(it,ib)[::-1]; return c1 if c1[:,0].mean()>c2[:,0].mean() else c2
def inward(line,d):
    ls=LineString(line); best=None
    for side in ('left','right'):
        o=ls.parallel_offset(d,side,join_style=2)
        if o.is_empty: continue
        g=o if o.geom_type=='LineString' else max(o.geoms,key=lambda g:g.length)
        m=np.array(g.coords).mean(axis=0)
        if best is None or m[0]<best[0][0]: best=(m,np.array(g.coords))
    return best[1]
A=outer_line(41); B=outer_line(40); A_in=inward(A,3.2); B_in=inward(B,3.2)
fig,ax=plt.subplots(1,3,figsize=(21,9))
for a,(xl,yl) in zip(ax,(((0,70),(0,150)),((30,70),(40,110)),((0,40),(0,45)))):
    a.plot(A[:,0],A[:,1],'b',lw=2,label=f'A: outer line, frame 41 (builder 5), X={X[40]:.1f}'); a.plot(A_in[:,0],A_in[:,1],'b--',lw=1.3,label='A inner: parallel 3.2 mm inward')
    a.plot(B[:,0],B[:,1],'r',lw=2,label=f'B: outer line, frame 40 (builder 6), X={X[39]:.1f}'); a.plot(B_in[:,0],B_in[:,1],'r--',lw=1.3,label='B inner: parallel 3.2 mm inward')
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].legend(fontsize=8); ax[0].set_title('S side, aft view: A over B'); ax[1].set_title('zoom: widest part'); ax[2].set_title('zoom: base')
plt.savefig('qa/frame5_AB_overlay_2d.png',dpi=65,bbox_inches='tight')
# gap between the inner line of A and the outer line of B, measured at several Z
def Yat(line,z):
    ys=[l0[0]+(l1[0]-l0[0])*(z-l0[1])/(l1[1]-l0[1]) for l0,l1 in zip(line[:-1],line[1:]) if (l0[1]-z)*(l1[1]-z)<=0 and l0[1]!=l1[1]]; return max(ys) if ys else None
for z in (20,40,60,80,100,120):
    a,ai,b=Yat(A,z),Yat(A_in,z),Yat(B,z); print('Z %d: outer A %.1f  inner A %.1f  outer B %.1f  -> B outer minus A inner %.2f mm'%(z,a,ai,b,b-ai) if None not in (a,ai,b) else 'Z %d n/a'%z)
