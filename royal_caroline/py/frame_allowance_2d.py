# Frame with sanding allowance from the layer's two faces: final surface = keelson spline (seat) and keel pocket floor (2 mm below the keel spline) at EACH face; the cut block = union of the two faces (innermost min / outermost max)
import sys,json,numpy as np
builder=[int(a) for a in sys.argv[1:]] or [5,23]; sys.argv=[sys.argv[0]]
import frames_batch_2d as F
import matplotlib.pyplot as plt
from shapely.ops import unary_union
from scipy.interpolate import UnivariateSpline
d=json.load(open('data/keelson_from_step_v1.json')); sK=UnivariateSpline(d['ref_knots_X'],d['ref_knots_Z'],k=3,s=0)       # keelson inner spline (builder STEP), no offset
c=json.load(open('data/keel_keelson_clean_v1.json')); kk=np.array(c['keel_line']['X']); kz=np.array(c['keel_line']['Z'])-c['keel_raise']; kK=UnivariateSpline(kk,kz,k=3,s=0)  # keel surface spline (STEP ramp)
POCKET=2.0
KT0=F.keel_levels
def lv(X):
    _,(kb,kt)=KT0(X); return float(kK(X)),(float(sK(X)),float(kt))
F.keel_levels=lv; F.PEN_LOW=POCKET; 
n=len(builder); fig,axs=plt.subplots(3,n,figsize=(9.5*n,17),gridspec_kw={'height_ratios':[1.5,1,1]})
axs=np.atleast_2d(axs.T).T if n>1 else axs.reshape(3,1)
for j,b in enumerate(builder):
    OUR=46-b; xc=F.XF[OUR-1]; res={}
    for lay,(x0,x1) in {'A':(xc-4,xc),'F':(xc,xc+4)}.items():
        fa,ia=F.face_poly(x0,x0); fb,ib=F.face_poly(x1,x1); cut=unary_union([fa.buffer(0.01),fb.buffer(0.01)]).buffer(-0.01); res[lay]=(cut,fa,fb,ia,ib)
        print('frame %d layer %s: keelson seat final %.2f (X=%.1f) / %.2f (X=%.1f) -> allowance %.2f mm | keel pocket floor final %.2f / %.2f -> allowance %.2f mm'%(b,lay,ia['ks_bot'],x0,ib['ks_bot'],x1,abs(ia['ks_bot']-ib['ks_bot']),ia['keel_top']-POCKET,ib['keel_top']-POCKET,abs(ia['keel_top']-ib['keel_top'])))
    iA=res['A'][3]; iF=res['F'][4]
    def draw(a,xl,yl,t):
        for lay,col in (('A','tab:blue'),('F','tab:red')):
            cut,fa,fb,ia,ib=res[lay]
            for g in (unary_union([cut.buffer(0.02),F.mirror(cut).buffer(0.02)]).buffer(-0.02),):
                for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.fill(*gg.exterior.xy,color=col,alpha=.12); a.plot(*gg.exterior.xy,color=col,lw=1.6)
            for g in (fa,fb,F.mirror(fa),F.mirror(fb)):
                for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color=col,lw=.7,ls='--')
        xs_=np.linspace(-14,40,50); a.plot(xs_*0+0,xs_*0,alpha=0)
        for X,cl in ((xc-4,'tab:blue'),(xc,'k'),(xc+4,'tab:red')):
            a.plot([-F.KB,F.KB],[float(sK(X))]*2,color=cl,lw=2.2); a.plot([-F.KB,F.KB],[float(kK(X))-POCKET]*2,color=cl,lw=2.2)
        a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(t,fontsize=10)
    draw(axs[0,j],(-85,85),(-5,115),'frame %d (our %d) X=%.1f: solid = cut outline with allowance, dashed = final face lines; layer A blue, F red'%(b,OUR,xc))
    z1=float(kK(xc)); z2=float(sK(xc))
    draw(axs[1,j],(-14,40),(z1-9,z1+14),'keel pocket (2 mm): floor line at X-4 (blue) / X (black) / X+4 (red)'); draw(axs[2,j],(-14,40),(z2-8,z2+12),'keelson seat = keelson spline at X-4 / X / X+4')
fig.savefig('qa/frame_allowance_'+'_'.join(map(str,builder))+'.png',dpi=48,bbox_inches='tight')
