# Builder frame 5 (our 41, X 480.3), 2D, from the hull lines (waterlines I-V + body-plan stations 3/2 interpolated in X; old plan outline above Z 105), the builder's keel/keelson profiles, true-offset inner lines, keel/keelson inverted-U laps, double sanding lines, piece joints.
import sys,io,json,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import cutting_plan as C
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union,split
from shapely import affinity
from scipy.interpolate import splprep,splev
from scipy.signal import savgol_filter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
i=41; xc=C.X[i-1]; KB=2.65; T=3.2; PEN_LOW=2.5; PEN_UP=2.5
ST=np.load('data/hull_stations_all.npz'); WL=np.load('data/hull_waterlines_all.npz'); BB=json.load(open('data/step44_profiles.json'))
sx={k:ST[k][0,0] for k in ST.files}
def Yst(z,X):
    ks=sorted(sx,key=lambda k:abs(sx[k]-X))[:2]; a,b=sorted(ks,key=lambda k:sx[k]); ya=np.interp(z,ST[a][:,2],ST[a][:,1],left=np.nan,right=np.nan); yb=np.interp(z,ST[b][:,2],ST[b][:,1],left=np.nan,right=np.nan); w=(X-sx[a])/(sx[b]-sx[a]); return (1-w)*ya+w*yb
def Ywl(k,X):
    v=WL[k]; idx=np.where(np.diff(np.sign(v[:,0]-X))!=0)[0]; return None if len(idx)==0 else float(np.interp(X,[v[idx[0],0],v[idx[0]+1,0]],[v[idx[0],1],v[idx[0]+1,1]]))
WLK=[('WL_I_plan',8.7),('WL_II_plan',17.4),('WL_III_plan',26.1),('WL_IV_plan',34.8),('WL_V_plan',43.4)]
def hull_points(X):
    pts=[(Ywl(k,X),z) for k,z in WLK if Ywl(k,X) is not None]
    sl=(pts[1][0]-pts[0][0])/(pts[1][1]-pts[0][1]); zf=pts[0][1]-(pts[0][0]-3.2)/sl; foot=(3.2,zf)           # foot where the hull line reaches the keel wall
    up=[(Yst(z,X),z) for z in (56,66,76,86,96,104)]; up=[p for p in up if not np.isnan(p[0])]
    old=C.face_outer(i,X); y104=np.interp(104,old[:,1],old[:,0]); sh=up[-1][0]-y104           # old plan outline above, shifted to meet the hull lines
    top=[(np.interp(z,old[:,1],old[:,0])+sh*max(0,1-(z-104)/40),z) for z in (116,130,142)]
    return np.array([foot]+pts+up+top)
def hull_line(X):
    P=hull_points(X); tk,u=splprep(P.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tk); return np.c_[y,z],P
def zr(name,Xq):
    p=Polygon(max(BB[name],key=lambda q:Polygon(q).area)).buffer(0); g=p.intersection(LineString([(Xq,-30),(Xq,200)])); return g.bounds[1],g.bounds[3]
def herm(P0,T0,P1,T1,n=40):
    t=np.linspace(0,1,n)[:,None]; return (2*t**3-3*t**2+1)*P0+(t**3-2*t**2+t)*T0+(-2*t**3+3*t**2)*P1+(t**3-t**2)*T1
def face_poly(Xf,Xlay):
    keel_top=zr('Boss-Extrude2[2]',Xlay)[1]; ks_bot,ks_top=zr('Boss-Extrude4[4]',Xlay); leg_bot=keel_top-PEN_LOW; zt=ks_bot+PEN_UP
    P,_=hull_line(Xf); k=int(np.argmin(np.abs(P[:,1]-(leg_bot+8)))); p0=P[k]; t0=(P[k+3]-P[k-3]); t0=t0/np.hypot(*t0)*11
    blend=herm(np.array([KB,leg_bot]),np.array([0,-1.0])*-5,p0,t0)           # hull line merges tangentially into the keel wall, leg bottom at keel top - PEN_LOW
    O=np.vstack([blend,P[k+1:]]); O=O[np.argsort(O[:,1])]
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d_=np.gradient(sm,axis=0); d_/=np.hypot(*d_.T)[:,None]
    Yx=np.interp(O[:,1],*[np.array(a) for a in zip(*[(z,(Yst(z,Xf+6)-Yst(z,Xf-6))/12) for z in np.linspace(O[0,1],104,30)])]) if False else 0
    m=np.c_[-d_[:,1],d_[:,0]]; I=O+m*T
    kk=int(np.where((I[:,0]>8)&(I[:,1]>zt+2.5))[0][0]); Pj=I[kk]; Tj=I[kk+2]-I[kk-2]; Tj=Tj/np.hypot(*Tj)
    Ps=np.array([KB+0.01,zt]); L=np.hypot(*(Pj-Ps)); sp=herm(Ps,np.array([1.0,0.0])*L*0.9,Pj,Tj*L*0.9)
    top=np.vstack([[[KB,ks_bot],[KB,zt]],sp[1:],I[kk+1:]])
    poly=Polygon(np.vstack([[[0,keel_top],[KB,keel_top],[KB,leg_bot]],O,top[::-1],[[0,ks_bot]]])).buffer(0).intersection(box(0,-10,200,300))
    return poly,dict(keel_top=keel_top,ks_bot=ks_bot,ks_top=ks_top,leg_bot=leg_bot,zt=zt)
LAY={'A':(xc-4,xc),'F':(xc,xc+4)}; res={}
for lay,(x0,x1) in LAY.items():
    xl=(x0+x1)/2; fa,info=face_poly(x0,xl); fb,_=face_poly(x1,xl); blk=unary_union([fa.buffer(0.01),fb.buffer(0.01)]).buffer(-0.01); res[lay]=(blk,fa,fb,info)
fig,ax=plt.subplots(1,3,figsize=(27,12),gridspec_kw={'width_ratios':[1.3,1,1]})
for lay,col in (('A','tab:blue'),('F','tab:red')):
    blk,fa,fb,info=res[lay]
    for a in ax:
        for g in (unary_union([blk.buffer(0.02),C.mirror(blk).buffer(0.02)]).buffer(-0.02),):
            for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.fill(*gg.exterior.xy,color=col,alpha=.18); a.plot(*gg.exterior.xy,color=col,lw=1.6)
        for g in (fa,fb,C.mirror(fa),C.mirror(fb)):
            for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color=col,lw=.7,ls='--')
for a,(xl,yl) in zip(ax,(((-75,75),(-12,150)),((-14,40),(-6,32)),((-10,10),(2,24)))):
    for lay,xq in (('A',xc-2),):
        info=res['A'][3]; a.add_patch(plt.Rectangle((-KB,-20),2*KB,info['keel_top']+20,color='#999')); a.add_patch(plt.Rectangle((-KB,info['ks_bot']),2*KB,info['ks_top']-info['ks_bot'],color='#999'))
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.3)
iA,iF=res['A'][3],res['F'][3]
ax[0].set_title(f'builder frame 5 (our 41), X={xc:.1f}: layer A (blue, X {xc-4:.1f}-{xc:.1f}) and F (red, X {xc:.1f}-{xc+4:.1f}); thick = block, dashed = exact lines of each face',fontsize=9)
ax[1].set_title(f'keel top {iA["keel_top"]:.2f}/{iF["keel_top"]:.2f}, keelson bottom {iA["ks_bot"]:.2f}/{iF["ks_bot"]:.2f} (A/F)',fontsize=9); ax[2].set_title('zoom: ח joints',fontsize=9)
plt.savefig('qa/frame5_precise_2d.png',dpi=50,bbox_inches='tight')
print('hull points face X=%.1f:'%xc,np.round(hull_points(xc),1).tolist())
print('A:',{k:round(v,2) for k,v in iA.items()},'F:',{k:round(v,2) for k,v in iF.items()})
