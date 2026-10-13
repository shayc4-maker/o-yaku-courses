import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import section, STX, O
from scipy.interpolate import PchipInterpolator
from shapely.geometry import Polygon, LineString, box, MultiPolygon
from shapely.ops import split, unary_union
from joints import frame_joint, make_T, Zb as ZbJ
K=1000/244.8/48; X0=4194.98
def Zp(y): return (2104.73-np.asarray(y))*8.689/102.1
# ---------------- parameters (model mm)
SIDED_BB=5.3      # keel / hog / deadwood / stem / post / keelson sided (body plan keel = 5.28)
HOG=1.8           # keel+hog top above rabbet (plan_5 midship)
NOTCH=1.0         # registration notch depth (hog top & keelson underside)
CLR=0.1           # clearance in notch length
KS_T=4.7          # keelson moulded
ZKB=-9.37         # keel bottom
SIDED_FR=4.0
fx=json.load(open(O+'/frames_X.json'))['X_mm']
pr=json.load(open(O+'/profile1a.json'))
# rabbet / seat line Zr(X) from body plan heels (via section interpolation)
XS=np.linspace(0,528,529); ZR=np.array([section(x,kind='pchip')[0,1] for x in XS])
Zr=PchipInterpolator(XS,ZR,extrapolate=True)
def H(x): return np.maximum(Zr(x),0.0)+HOG
# keelson underside (read from plan_5 at frames 3..45)
KB=np.array([(39.0,37.9),(50.0,33.2),(61.25,29.2),(73.0,24.1),(94.74,18.5),(139.7,11.1),(183.7,7.7),(251.4,7.4),(357.4,7.4),(434.5,9.5),(457.8,11.9),(480.3,16.6),(502.2,23.3),(513.6,28.6),(524.0,33.9)])
# extend aft using same trend to frame 1
Zb=ZbJ
# sternpost lines X(Z)
fa,ff=pr['post_aft_fit'],pr['post_fore_fit']
def Xpost(f,Z):
    y=2104.73-np.asarray(Z)*102.1/8.689; return (np.polyval(f,y)-X0)*K
ZPT=83.8
# stem outer & rabbet
so=np.array(pr['stem_outer']); ra=np.array(pr['stem_rabbet_aft'])
so=so[np.argsort(so[:,0])] if False else so
# order stem_outer from keel bottom upward: start at min Z near keel
i0=np.argmin(so[:,1]+0.001*so[:,0]); 
if i0>len(so)/2: so=so[::-1]
# keep until the foremost point then up to max Z
imax=np.argmax(so[:,1]); so=so[:imax+1]
ZHEAD=so[-1,1]
ra=ra if ra[0,1]<ra[-1,1] else ra[::-1]
ra=ra[ra[:,0]>440]
# inner (apron/deadwood top) line forward of frame region: rabbet offset by HOG along normal (up/aft)
t=np.gradient(ra,axis=0); t/=np.linalg.norm(t,axis=1)[:,None]; n=np.c_[-t[:,1],t[:,0]]
if n[len(n)//2,1]<0: n=-n
rin=ra+n*HOG
rin=rin[rin[:,0]>fx[-1]+SIDED_FR+0.5]
# extend inner line up to head along last tangent
d=rin[-1]-rin[-8]; d/=np.linalg.norm(d); L=(ZHEAD-rin[-1,1])/max(d[1],1e-3)
rin=np.r_[rin,[rin[-1]+d*L]]
# ---------------- backbone outline (X,Z)
xpa_b=float(Xpost(fa,ZKB)); xpa_t=float(Xpost(fa,ZPT)); xpf_t=float(Xpost(ff,ZPT))
# aft top line: H(x) from post fore edge to frame 45 fore face
xs_aft=np.linspace(-20,fx[-1]+SIDED_FR+0.5,700)
top=np.c_[xs_aft,H(xs_aft)]
# clip at post fore line: keep x >= Xpost(ff, z)
top=top[top[:,0]>=Xpost(ff,top[:,1])]
outline=[(xpa_b,ZKB)]+[tuple(p) for p in so if p[0]>xpa_b+5]+[(so[-1,0],ZHEAD)]
outline+= [tuple(p) for p in rin[::-1]]+[tuple(p) for p in top[::-1]]
outline+= [(float(Xpost(ff,top[0,1])),float(top[0,1])),(xpf_t,ZPT),(xpa_t,ZPT)]
BB=Polygon(outline).buffer(0)
if BB.geom_type!='Polygon': BB=max(BB.geoms,key=lambda g:g.area)
# ---------------- cut lines
def cut(poly,line):
    r=split(poly,LineString(line)); return sorted(r.geoms,key=lambda g:g.centroid.x)
post_line=[(float(Xpost(ff,z)),z) for z in np.linspace(ZKB-2,ZPT+2,30)]
# keel/stem scarf (hooked, read from plan_5): top step at X=491.5 (Z HOG..-0.6), table to X=500, then down to (504.5,ZKB)
scarf=[(491.5,HOG+0.01),(491.5,-0.6),(500.0,-0.6),(504.5,ZKB-0.5)]
pieces={}
zz=np.linspace(ZKB,ZPT,40)
postpoly=Polygon(np.r_[np.c_[Xpost(fa,zz),zz],np.c_[Xpost(ff,zz),zz][::-1]]).buffer(0)
ten=Polygon([(float(Xpost(ff,-6.5)),-6.5),(float(Xpost(ff,-6.5))+3,-6.5),(float(Xpost(ff,-2.5))+3,-2.5),(float(Xpost(ff,-2.5)),-2.5)])
postpoly=unary_union([postpoly,ten])
pieces['STERNPOST']=BB.intersection(postpoly); rest=BB.difference(postpoly)
rest=max(rest.geoms,key=lambda g:g.area) if rest.geom_type!='Polygon' else rest
# separate stem: line = scarf + vertical up from (491.5,HOG) to above head
stem_cut=[(491.5,200)]+scarf
a=split(rest,LineString(stem_cut)); g=sorted(a.geoms,key=lambda g:g.centroid.x)
pieces['STEM']=g[-1]; rest=unary_union(g[:-1])
# keel = below Z=HOG ; deadwoods above
kl=split(rest,LineString([(-50,HOG),(600,HOG)])); g=list(kl.geoms)
keel=[p for p in g if p.centroid.y<HOG]; up=[p for p in g if p.centroid.y>=HOG]
pieces['KEEL']=unary_union(keel)
up=sorted(up,key=lambda g:g.centroid.x)
for j,p in enumerate(up):
    if p.area<1: continue
    pieces['DEADWOOD_AFT' if p.centroid.x<250 else 'DEADWOOD_FWD']=p
# ---------------- registration notches in the top of keel/deadwood/stem (hog top) at each frame
notches=[]
for i,x in enumerate(fx,1):
    x0,x1=x-SIDED_FR-CLR/2,x+SIDED_FR+CLR/2; zn,zt=frame_joint(i,H)
    notches.append(box(x0,zn,x1,zn+80))   # removes everything above notch bottom within the frame footprint
NB=unary_union(notches)
for k in list(pieces):
    if k=='STERNPOST': continue
    pieces[k]=pieces[k].difference(NB)
# ---------------- keelson
xk0,xk1=fx[0]-SIDED_FR-3,fx[-1]+SIDED_FR+3
xs=np.linspace(xk0,xk1,600); zb=Zb(xs)
ks=Polygon(np.r_[np.c_[xs,zb],np.c_[xs,zb+KS_T][::-1]])
kn=unary_union([box(x-SIDED_FR-CLR/2,frame_joint(i,H)[1]-12,x+SIDED_FR+CLR/2,frame_joint(i,H)[1]) for i,x in enumerate(fx,1)])
pieces['KEELSON']=ks.difference(kn)
for k,p in list(pieces.items()):
    if p.geom_type!='Polygon':
        g=sorted(p.geoms,key=lambda q:-q.area); print('  ',k,'dropping slivers',[round(q.area,2) for q in g[1:]]); pieces[k]=g[0]
for k,p in pieces.items(): print('%-13s area %8.1f  X %.1f..%.1f  Z %.1f..%.1f  type %s'%(k,p.area,*p.bounds[0::2],*p.bounds[1::2],p.geom_type))
json.dump({'params':dict(SIDED_BB=SIDED_BB,HOG=HOG,NOTCH=NOTCH,CLR=CLR,KS_T=KS_T,ZKB=ZKB),
           'pieces':{k:([list(map(list,p.exterior.coords))] if p.geom_type=='Polygon' else [list(map(list,q.exterior.coords)) for q in p.geoms]) for k,p in pieces.items()},
           'H_at_frames':[float(H(x)) for x in fx],'Zb_at_frames':[float(Zb(x)) for x in fx],'Zr_at_frames':[float(Zr(x)) for x in fx]},open(O+'/backbone.json','w'))
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(16,4.5)); cols=dict(KEEL='C0',STERNPOST='C3',STEM='C2',DEADWOOD_AFT='C1',DEADWOOD_FWD='C4',KEELSON='C5')
for k,p in pieces.items():
    for q in ([p] if p.geom_type=='Polygon' else p.geoms):
        c=np.array(q.exterior.coords); ax.fill(c[:,0],c[:,1],color=cols[k],alpha=.5,label=k); ax.plot(c[:,0],c[:,1],'k',lw=.4)
for x in fx: ax.add_patch(plt.Rectangle((x-SIDED_FR,float(H(x))-NOTCH),2*SIDED_FR,float(Zb(x))+NOTCH-float(H(x))+NOTCH,fill=False,ec='brown',lw=.5))
h,l=ax.get_legend_handles_labels(); u=dict(zip(l,h)); ax.legend(u.values(),u.keys(),fontsize=7,ncol=6,loc='upper center')
ax.set_aspect('equal'); ax.grid(alpha=.2); ax.set_xlim(-25,600); fig.tight_layout(); fig.savefig(O+'/backbone_preview.png',dpi=90)
