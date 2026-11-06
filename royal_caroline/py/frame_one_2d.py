# ONE frame in 2D: exact hull lines, horizontal floor and seat, laser (final) lines at X-4 / X / X+4, common cut outline
import sys,os,json,numpy as np
b=int(sys.argv[1]); sys.argv=[sys.argv[0]]
os.environ['NOSTEP']='1'; os.environ['SHARP']='1'; os.environ['INNER_SMOOTH']='1'
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0)
KT0=F.keel_levels; F.keel_levels=lambda X:(lambda X:(float(kK(X)),(float(sK(X)),KT0(X)[1][1])))(min(X,526.0)); F.PEN_LOW=V2['depth']
xc=F.XF[46-b-1]; fc={'X-4':xc-4,'X':xc,'X+4':xc+4}; cols={'X-4':'tab:blue','X':'k','X+4':'tab:red'}
faces={n:F.face_poly(X,X) for n,X in fc.items()}
env=unary_union([f[0].buffer(0.01) for f in faces.values()]).buffer(-0.01)
fig,axs=plt.subplots(1,3,figsize=(24,10),gridspec_kw={'width_ratios':[1,1,1]})
def draw(a,xl,yl,title):
    full=lambda g: unary_union([g.buffer(0.01),F.mirror(g).buffer(0.01)]).buffer(-0.01)
    for gg in (lambda g:(g.geoms if hasattr(g,'geoms') else [g]))(full(env)): a.plot(*gg.exterior.xy,color='#888',lw=1.2,ls='--')
    for n,(p,info) in faces.items():
        for gg in (lambda g:(g.geoms if hasattr(g,'geoms') else [g]))(full(p)): a.plot(*gg.exterior.xy,color=cols[n],lw=1.4)
    a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_title(title,fontsize=10)
i=faces['X'][1]
draw(axs[0],(-85,85),(-5,115),'frame %d X=%.1f: final lines at X-4 (blue), X (black), X+4 (red); common cut outline dashed gray'%(b,xc))
draw(axs[1],(-16,16),(i['leg_bot']-3,i['leg_bot']+7),'floor on the keel: horizontal line out to the EXACT hull line (floor %.2f / %.2f / %.2f)'%tuple(f[1]['leg_bot'] for f in faces.values()))
draw(axs[2],(-16,16),(i['ks_bot']-3,i['ks_bot']+7),'seat under the keelson: horizontal out to the inner line (seat %.2f / %.2f / %.2f)'%tuple(f[1]['ks_bot'] for f in faces.values()))
fig.savefig('qa/frame%d_one_2d.png'%b,dpi=55,bbox_inches='tight')
for n,(p,info) in faces.items(): print(n,'floor %.2f seat %.2f; first hull point after the floor %s'%(info['leg_bot'],info['ks_bot'],info['O'][0].round(2).tolist()))
