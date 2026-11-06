# Frames in 2D on the NEW keel/keelson pockets (data/keel_keelson_clean_v1.json): per frame one floor and one ceiling for both layers and all three faces (X-4, X, X+4)
import sys,json,numpy as np
builder=[int(a) for a in sys.argv[1:]]; sys.argv=[sys.argv[0]]
import frames_batch_2d as F
import matplotlib.pyplot as plt
from shapely.ops import unary_union
D=json.load(open('data/keel_keelson_clean_v1.json')); P={p['builder']:p for p in D['pockets']}
KT=F.keel_levels
def levels_for(X):
    for p in P.values():
        if p['a']-0.02<=X<=p['b']+0.02: 
            _,(ks_b,ks_t)=KT(p['X']); return p['keel_floor'],(p['keelson_ceiling'],max(ks_t,p['keelson_ceiling']+5.0))
    return KT(X)
F.keel_levels=levels_for
n=len(builder); fig,axs=plt.subplots(3,n,figsize=(5.3*n,17),gridspec_kw={'height_ratios':[1.6,1,1]}); out={}
for j,b in enumerate(builder):
    OUR=46-b; p=P[b]; xc=F.XF[OUR-1]; res={}; print('frame',b,xc)
    for lay,(x0,x1) in {'A':(xc-4,xc),'F':(xc,xc+4)}.items():
        fa,info=F.face_poly(x0,x0); fb,_=F.face_poly(x1,x1); res[lay]=(unary_union([fa.buffer(0.01),fb.buffer(0.01)]).buffer(-0.01),fa,fb,info)
    iA=res['A'][3]; out[b]=dict(X=xc,floor=p['keel_floor'],ceiling=p['keelson_ceiling'],A=list(res['A'][0].exterior.coords),F=list(res['F'][0].exterior.coords))
    print('frame %2d X=%6.1f floor %5.2f ceiling %5.2f gap %4.2f | A area %.0f F area %.0f | A/F symmetric difference %.2f mm2'%(b,xc,p['keel_floor'],p['keelson_ceiling'],p['keelson_ceiling']-p['keel_floor'],res['A'][0].area,res['F'][0].area,res['A'][0].symmetric_difference(res['F'][0]).area))
    def draw(a,xl,yl,title):
        for lay,col in (('A','tab:blue'),('F','tab:red')):
            blk,fa,fb,info=res[lay]
            for g in (unary_union([blk.buffer(0.02),F.mirror(blk).buffer(0.02)]).buffer(-0.02),):
                for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.fill(*gg.exterior.xy,color=col,alpha=.18); a.plot(*gg.exterior.xy,color=col,lw=1.2)
        a.add_patch(plt.Rectangle((-F.KB,-20),2*F.KB,iA['keel_top']+20,color='#888',alpha=.8)); a.add_patch(plt.Rectangle((-F.KB,iA['ks_bot']),2*F.KB,iA['ks_top']-iA['ks_bot'],color='#888',alpha=.8))
        a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(title,fontsize=9)
    draw(axs[0,j],(-85,85),(-5,115),'frame %d (our %d) X=%.1f'%(b,OUR,xc)); draw(axs[1,j],(-14,40),(iA['keel_top']-12,iA['keel_top']+16),'keel pocket floor %.2f'%iA['keel_top']); draw(axs[2,j],(-14,40),(iA['ks_bot']-6,iA['ks_top']+10),'keelson pocket ceiling %.2f'%iA['ks_bot'])
tag='b%d-%d'%(min(builder),max(builder)); fig.savefig('qa/frames_pockets_%s.png'%tag,dpi=55,bbox_inches='tight'); json.dump(out,open('data/frames_pockets_%s.json'%tag,'w'))
