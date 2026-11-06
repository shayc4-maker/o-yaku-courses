# New keel and keelson (2D): keelson inner line = the builder's smooth spline, no pockets; keel top = surface spline with 2 mm deep pockets (one per frame, X-4..X+4, walls normal to the spline), floor = second spline 2 mm below, parallel
import sys,json,numpy as np
sys.path.insert(0,'py'); import step_chain as S
from scipy.interpolate import UnivariateSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
DEPTH=2.0; XJ=526.6
XF=json.load(open('data/frames_X.json'))['X_mm']
d=json.load(open('data/keelson_from_step_v1.json')); sK_=UnivariateSpline(d['ref_knots_X'],d['ref_knots_Z'],k=3,s=0)
c=json.load(open('data/keel_keelson_clean_v1.json')); kx=np.array(c['keel_line']['X']); kz=np.array(c['keel_line']['Z'])-c['keel_raise']
sKeel=UnivariateSpline(kx,kz,k=3,s=0)
keelson=lambda x: sK_(np.minimum(x,XJ+30))
def keel_surface(x):
    x=np.asarray(x,float); allowed=np.clip((XJ-x)/12.0,0,1)*1.0
    return np.minimum(sKeel(x),keelson(x)-allowed)
def nrm(x,f,h=0.05): dz=float((f(x+h)-f(x-h))/(2*h)); t=np.array([1.0,dz]); t/=np.hypot(*t); return np.array([-t[1],t[0]])
xs=np.arange(45,XJ+0.01,0.1)
pk=[(46-n,X-4,X+4) for n,X in enumerate(XF,1) if 50<X<528]; pk.sort(key=lambda p:p[1])
pts=[]; x=xs[0]
for b,a,bb in pk:
    pts+= [(xx,float(keel_surface(xx))) for xx in np.arange(x,a,0.2)]
    Pa=np.array([a,float(keel_surface(a))]); na=nrm(a,keel_surface); pts.append(tuple(Pa)); pts.append(tuple(Pa-DEPTH*na))
    for xx in np.arange(a+0.2,bb,0.2):
        P=np.array([xx,float(keel_surface(xx))]); pts.append(tuple(P-DEPTH*nrm(xx,keel_surface)))
    Pb=np.array([bb,float(keel_surface(bb))]); nb=nrm(bb,keel_surface); pts.append(tuple(Pb-DEPTH*nb)); pts.append(tuple(Pb)); x=bb+0.2
pts+= [(xx,float(keel_surface(xx))) for xx in np.arange(x,xs[-1],0.2)]
keel_top=np.array(pts)
gap=keelson(xs)-keel_surface(xs)
teeth=[pk[i+1][1]-pk[i][2] for i in range(len(pk)-1)]
print('pockets %d, depth %.1f mm (normal to the spline), width 8 mm; teeth between pockets %.1f-%.1f mm'%(len(pk),DEPTH,min(teeth),max(teeth)))
print('gap keelson spline - keel surface spline: X=300: %.2f mm, minimum for X<520: %.2f mm'%(float(np.interp(300,xs,gap)),gap[xs<520].min()))
json.dump(dict(depth=DEPTH,keelson_spline=dict(X=xs[::10].round(2).tolist(),Z=keelson(xs[::10]).round(3).tolist()),keel_surface=dict(X=xs[::10].round(2).tolist(),Z=keel_surface(xs[::10]).round(3).tolist()),pockets=[dict(builder=b,a=round(a,2),b=round(bb,2)) for b,a,bb in pk]),open('data/keel_keelson_v2.json','w'))
fig,axs=plt.subplots(3,1,figsize=(18,17),gridspec_kw={'height_ratios':[1,1,.8]})
for a_,(xl,yl) in zip(axs,(((470,535),(0,45)),((260,330),(-2,12)),((45,535),(-3,60)))):
    xx=np.linspace(max(xl[0],45),min(xl[1],XJ+8),800); a_.plot(xx,keelson(xx),'g',lw=2.2,label='keelson inner spline (smooth, no pockets)'); a_.plot(xx,keel_surface(xx),color='tab:brown',lw=1.0,label='keel surface spline')
    sl=(keel_surface(xx+.05)-keel_surface(xx-.05))/.1; a_.plot(xx,keel_surface(xx)-DEPTH*np.sqrt(1+sl**2),color='tab:brown',lw=1.0,ls='--',label='pocket floor spline (2 mm, parallel)')
    a_.plot(keel_top[:,0],keel_top[:,1],color='k',lw=1.6,label='keel top outline with pockets')
    for b,a,bb in pk:
        if xl[0]-8<a<xl[1]: a_.axvspan(a,bb,color='tab:blue',alpha=.08); a_.text((a+bb)/2,yl[1]-(yl[1]-yl[0])*.04,str(b),ha='center',fontsize=8 if a_ is not axs[2] else 5)
    a_.set_xlim(*xl); a_.set_ylim(*yl); a_.grid(alpha=.3); a_.set_ylabel('Z (mm)')
axs[0].legend(loc='upper left'); axs[0].set_title('New keel and keelson (2D): smooth keelson spline; keel with 2 mm pockets, two parallel splines; blue = frame width 8 mm')
fig.savefig('qa/keel_keelson_v2_2d.png',dpi=55,bbox_inches='tight')
