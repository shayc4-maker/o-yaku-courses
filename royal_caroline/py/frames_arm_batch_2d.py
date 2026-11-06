# frames (builder numbers) in 2D by the builder's rule (frame_arm.py): floor + seat horizontals at the backbone width, wall at the keel, inner spline tangent to the offset line
import sys,json,numpy as np
bl=[int(a) for a in sys.argv[1:]]; sys.argv=[sys.argv[0]]
sys.path.insert(0,'py')
from frame_arm import *
from shapely.geometry import Polygon
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
mir=lambda g: __import__('shapely.affinity',fromlist=['scale']).scale(g,xfact=-1,yfact=1,origin=(0,0))
cols={'X-4':'tab:blue','X':'k','X+4':'tab:red'}; n=len(bl); fig,axs=plt.subplots(3,n,figsize=(5.4*n,16),gridspec_kw={'height_ratios':[1.5,1,1]}); axs=axs.reshape(3,n); out={}
for j,b in enumerate(bl):
    xc=F.XF[46-b-1]; arms={}
    try:
        for nm,X in (('X-4',xc-4),('X',xc),('X+4',xc+4)): arms[nm]=arm(X)
    except Exception as e: axs[0,j].set_title('frame %d FAILED: %s'%(b,str(e)[:80]),fontsize=8); print('frame',b,'FAILED',e); continue
    print('frame %d X=%.1f | floor %s | seat %s | wall %s | gap %s'%(b,xc,' / '.join('%.2f'%arms[k][1]['floor'] for k in arms),' / '.join('%.2f'%arms[k][1]['seat'] for k in arms),' / '.join('%.1f'%(arms[k][1]['floor']-arms[k][1]['hull_at_wall']) for k in arms),' / '.join('%.1f'%(arms[k][1]['seat']-arms[k][1]['floor']) for k in arms)))
    out[b]=dict(X=xc,faces={k:dict(floor=arms[k][1]['floor'],seat=arms[k][1]['seat'],wall=arms[k][1]['floor']-arms[k][1]['hull_at_wall'],half=[list(c) for c in (arms[k][0].exterior.coords if arms[k][0].geom_type=='Polygon' else max(arms[k][0].geoms,key=lambda q:q.area).exterior.coords)]) for k in arms})
    full=lambda g:(lambda u:max(u.geoms,key=lambda q:q.area) if hasattr(u,'geoms') else u)(unary_union([g.buffer(0.01),mir(g).buffer(0.01)]).buffer(-0.01))
    f0=arms['X'][1]['floor']; s0=arms['X'][1]['seat']
    for r,(xl,yl,t) in enumerate((((-85,85),(-5,115),'frame %d X=%.1f'%(b,xc)),((-14,14),(f0-5,s0+5),'centre: wall, floor, seat'),((-34,34),(f0-6,s0+16),'inner spline into the offset line'))):
        a=axs[r,j]
        for k,(p,i) in arms.items(): a.plot(*full(p).exterior.xy,color=cols[k],lw=1.3)
        a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(t,fontsize=9)
fig.savefig('qa/frames_arm_%s.png'%('_'.join(map(str,bl))),dpi=48,bbox_inches='tight'); json.dump(out,open('data/frames_arm_%s.json'%('_'.join(map(str,bl))),'w'))
