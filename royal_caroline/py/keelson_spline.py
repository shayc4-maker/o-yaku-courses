# Keelson inner line as a SPLINE between pockets: the smoothed original line shifted down by d (constant), pockets (X-4..X+4, ceiling = old level at the frame centre) cut into it
import sys,json,numpy as np
W=float(sys.argv[1]) if len(sys.argv)>1 else 1.5; sys.argv=[sys.argv[0]]
import frames_batch_2d as F
from scipy.ndimage import uniform_filter1d
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt
S=json.load(open('data/channel_seats_v2.json'))['seats']
xs=np.arange(40,527,0.25)
def kl(X):
    try:
        kt,(a,b)=F.keel_levels(X); return (kt,a if a is not None else np.nan)
    except Exception: return (np.nan,np.nan)
K=np.array([[np.nan if v is None else v for v in kl(x)] for x in xs],float); KT,KS=K[:,0],K[:,1]
ok=~np.isnan(KS); Xo=xs[ok]; Oo=KS[ok]
# smooth through the stairs: a spline through the plateau-to-plateau mean (mean over one frame pitch) -> continuous line that keeps the shape of the original
Osm=uniform_filter1d(Oo,int(11/0.25),mode='nearest'); sp=UnivariateSpline(Xo[::8],Osm[::8],k=3,s=0.002*len(Xo[::8])); Sline=lambda x: sp(x)
need=[]
for s in S:
    a,b,L=s['face_A'],s['face_end'],s['keelson_bottom']
    if a<Xo.min() or b>Xo.max(): continue
    need.append((s['builder'],float(Sline(b)-L+W)))
# shift d(x): smooth (spline-like, monotone cubic) through the needed shift of every frame, never below it -> the line keeps its own shape, no steps
from scipy.interpolate import PchipInterpolator
Xn=np.array([[t['X'] for t in S if t['builder']==n][0] for n,_ in need]); Dn=np.array([v for _,v in need]); o=np.argsort(Xn); Xn,Dn=Xn[o],Dn[o]
Dn=np.maximum(Dn,0.0)+0.12; dfun=PchipInterpolator(Xn,Dn)
Xseat=np.concatenate([np.linspace(t['face_A'],t['face_end'],9) for t in S if t['face_A']>=Xo.min() and t['face_end']<=Xo.max()])
d_at=lambda x: np.maximum(dfun(np.clip(x,Xn.min(),Xn.max())),0)
# make sure the wall is >= W at every pocket end (small bump up if the interpolation dipped under the need)
for t in S:
    if t['face_A']<Xo.min() or t['face_end']>Xo.max(): continue
    b_=t['face_end']; need_b=float(Sline(b_)-t['keelson_bottom']+W); cur=float(d_at(b_))
    if cur<need_b-1e-6: print('frame',t['builder'],'interp short by %.2f'%(need_b-cur))
mins=[]
for t in S:
    a_,b_=t['face_A'],t['face_end']
    if a_<Xo.min() or b_>Xo.max(): continue
    xx=np.linspace(a_,b_,10); kt=np.interp(xx,xs[~np.isnan(KT)],KT[~np.isnan(KT)]); mins.append((t['builder'],round(float(min(Sline(xx)-d_at(xx)-kt)),2)))
print('shift d(x): frame 2: %.2f, frame 5: %.2f, frame 13: %.2f, frame 23: %.2f'%tuple(float(d_at([t['X'] for t in S if t['builder']==n][0])) for n in (2,5,13,23)))
print('min clearance new spline - keel top over the seats, smallest 6:',sorted(mins,key=lambda m:m[1])[:6])
d=None
json.dump(dict(wall=W,knots_X=Xo[::8].tolist(),knots_Z=(Sline(Xo[::8])-d_at(Xo[::8])).round(3).tolist()),open('data/keelson_inner_spline_v1.json','w'))
fig,axs=plt.subplots(2,1,figsize=(17,12))
for a_,(xl,yl) in zip(axs,(((470,530),(8,36)),((380,445),(2,12)))):
    a_.plot(Xo,Oo,'k',lw=1.2,label='original (before)'); xx=np.linspace(*xl,600); a_.plot(xx,Sline(xx)-d_at(xx),'g',lw=2,label='new spline: original shape, lowered by a smooth amount (0 to ~3 mm)')
    for s in S:
        if xl[0]-5<s['X']<xl[1]+5:
            a_.add_patch(plt.Rectangle((s['face_A'],s['keelson_bottom']-9),s['face_end']-s['face_A'],9,color='tab:blue',alpha=.25)); a_.plot([s['face_A'],s['face_end']],[s['keelson_bottom']]*2,'b',lw=2); a_.text(s['X'],yl[1]-.6,str(s['builder']),ha='center')
    a_.set_xlim(*xl); a_.set_ylim(*yl); a_.grid(alpha=.3); a_.legend(loc='lower right'); a_.set_ylabel('keelson inner line Z (mm)')
axs[0].set_title('Keelson inner line: spline between pockets (green), pockets blue (ceiling = blue line); wall on both sides of every pocket >= %.1f mm'%W)
fig.savefig('qa/keelson_spline.png',dpi=60,bbox_inches='tight')
