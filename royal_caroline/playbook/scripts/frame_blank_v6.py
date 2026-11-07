# ONE frame (builder number b) from the APPROVED outer lines v5 (frames_outer_approved_v5.json) with the final arm rule (frame_arm.py): exact outer line to the keel wall, pocket floor + seat horizontals, concave inner line (3.2 offset); common blank for layers A and F; laser lines = the three final faces
import sys,os,json,numpy as np
b=int(sys.argv[1]) if len(sys.argv)>1 else 23; sys.argv=[sys.argv[0]]
sys.path.insert(0,'py')
import frames_batch_2d as F
A5=json.load(open('data/frames_outer_approved_v5.json'))
def hull_approved(X):
    for nm in ('back','mid','front'):
        v=A5[str(b)][nm]
        if abs(v['X']-X)<0.01:
            C=np.array(v['curve']); C=C[C[:,0]>=3.2]
            if v.get('top'): C=np.vstack([C,np.array(v['top'])[1:]])
            return C
    raise KeyError(X)
F.hull_line=hull_approved
import frame_arm as FA
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
xc=A5[str(b)]['mid']['X']; arms={}
for nm,X in (('back',xc-4),('mid',xc),('front',xc+4)): arms[nm]=FA.arm(X)
mir=lambda g: __import__('shapely.affinity',fromlist=['scale']).scale(g,xfact=-1,yfact=1,origin=(0,0))
def full(g):
    u=unary_union([g.buffer(0.01),mir(g).buffer(0.01)]).buffer(-0.01); return max(u.geoms,key=lambda q:q.area) if hasattr(u,'geoms') else u
FP={k:full(arms[k][0]) for k in arms}; env=unary_union([FP[k].buffer(0.01) for k in FP]).buffer(-0.01); env=max(env.geoms,key=lambda q:q.area) if hasattr(env,'geoms') else env
for k in FP: print(k,'valid',FP[k].is_valid,'area %.0f'%FP[k].area,'floor %.2f seat %.2f'%(arms[k][1]['floor'],arms[k][1]['seat']))
print('common blank valid',env.is_valid,'area %.0f'%env.area,'bounds',[round(v,1) for v in env.bounds])
np.save('/tmp/frame_blank_%d.npy'%b,dict(xc=xc,FP={k:np.array(v.exterior.coords) for k,v in FP.items()},env=np.array(env.exterior.coords),info={k:{kk:vv for kk,vv in arms[k][1].items() if kk in('floor','seat','hull_at_wall')} for k in arms}),allow_pickle=True)
fig,axs=plt.subplots(1,3,figsize=(20,9),gridspec_kw={'width_ratios':[1.6,1,1]}); cols={'back':'tab:blue','mid':'k','front':'tab:red'}
for a,(xl,yl,t) in zip(axs,(((-85,85),(-5,110),'frame %d X=%.1f: 3 faces (blue X-4, black X, red X+4), grey = common blank'%(b,xc)),((-14,14),(arms['mid'][1]['floor']-5,arms['mid'][1]['seat']+5),'centre: wall, pocket floor, seat'),((-40,40),(arms['mid'][1]['floor']-5,arms['mid'][1]['seat']+30),'inner line into the offset line'))):
    a.fill(*env.exterior.xy,color='0.85'); 
    for k,p in FP.items(): a.plot(*p.exterior.xy,color=cols[k],lw=1.2)
    a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_title(t,fontsize=9)
fig.savefig('qa/frame_blank_%d_2d.png'%b,dpi=55,bbox_inches='tight')
