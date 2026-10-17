# Frames sitting on the keel and keelson (the agreed ח laps), 2D, any frame: python3 py/frames_on_keel_2d.py 45 44 ... (our numbering; builder = 46-ours)
import sys,io,json,contextlib,numpy as np
args=[int(a) for a in sys.argv[1:]] or [45,44,43,42,41,40,39,38,37,36]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import cutting_plan as C
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
from scipy.interpolate import splprep,splev
from scipy.signal import savgol_filter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KB=2.65; T=3.2; PEN_LOW=2.5; PEN_UP=2.5
ST=np.load('data/hull_stations_all.npz'); WL=np.load('data/hull_waterlines_all.npz'); BB=json.load(open('data/step44_profiles.json'))
sx={k:ST[k][0,0] for k in ST.files}
PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
UB=unary_union(list(PP.values()))
def Yst(z,X):
    ks=sorted(sx,key=lambda k:sx[k])
    below=[k for k in ks if sx[k]<=X]; above=[k for k in ks if sx[k]>X]
    if not below: a,b=ks[0],ks[1]
    elif not above: a,b=ks[-2],ks[-1]          # beyond the last station: linear extrapolation
    else: a,b=below[-1],above[0]
    ya=np.interp(z,ST[a][:,2],ST[a][:,1],left=np.nan,right=np.nan); yb=np.interp(z,ST[b][:,2],ST[b][:,1],left=np.nan,right=np.nan); w=(X-sx[a])/(sx[b]-sx[a]); return (1-w)*ya+w*yb
def Ywl(k,X):
    v=WL[k]; idx=np.where(np.diff(np.sign(v[:,0]-X))!=0)[0]; return None if len(idx)==0 else float(np.interp(X,[v[idx[0],0],v[idx[0]+1,0]],[v[idx[0],1],v[idx[0]+1,1]]))
WLK=[('WL_I_plan',8.7),('WL_II_plan',17.4),('WL_III_plan',26.1),('WL_IV_plan',34.8),('WL_V_plan',43.4)]
import hull_loft_sections as HL
def hull_line(i,X):
    """exact hull line at X = section of the lofted body-plan station splines; sampled at ~14 points on the exact section and joined by an interpolating spline; plan outline above the last station point"""
    P=HL.section(min(X,527.7)); zz=np.round(P[:,1],2); _,ui=np.unique(zz,return_index=True); P=P[ui]; P=P[np.argsort(P[:,1])]
    z0,z1=P[0,1],P[-1,1]; zs=np.r_[z0,np.linspace(z0,z1,13)[1:]]; pts=[(float(np.interp(z,P[:,1],P[:,0])),float(z)) for z in zs]
    old=C.face_outer(i,X); sh=pts[-1][0]-np.interp(z1,old[:,1],old[:,0]); top=[(np.interp(z,old[:,1],old[:,0])+sh*max(0,1-(z-z1)/40),z) for z in (z1+12,z1+26,142)]
    pts=np.array(pts+top); pts[0,0]=max(pts[0,0],3.2)
    tk,u=splprep(pts.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tk); return np.c_[y,z]
def keel_levels(X):
    g=UB.intersection(LineString([(X,-30),(X,200)])); sg=sorted((l.bounds[1],l.bounds[3]) for l in getattr(g,'geoms',[g]))
    sg=[s for s in sg if s[1]-s[0]>0.05]; mrg=[list(sg[0])]
    for s in sg[1:]:
        if s[0]-mrg[-1][1]<0.3: mrg[-1][1]=max(mrg[-1][1],s[1])
        else: mrg.append(list(s))
    keel_top=mrg[0][1]; 
    return keel_top,(mrg[1][0],mrg[1][1]) if len(mrg)>1 else (None,None)
def herm(P0,T0,P1,T1,n=40):
    t=np.linspace(0,1,n)[:,None]; return (2*t**3-3*t**2+1)*P0+(t**3-2*t**2+t)*T0+(-2*t**3+3*t**2)*P1+(t**3-t**2)*T1
def face_poly(i,Xf,Xlay):
    keel_top,(ks_bot,ks_top)=keel_levels(Xlay)
    if ks_bot is None: raise ValueError('no gap between keel and keelson at X=%.1f'%Xlay)
    leg_bot=keel_top-PEN_LOW; zt=ks_bot+PEN_UP
    P=hull_line(i,Xf); k=int(np.argmin(np.abs(P[:,1]-(leg_bot+8)))); p0=P[k]; t0=(P[k+3]-P[k-3]); t0=t0/np.hypot(*t0)*11
    blend=herm(np.array([KB,leg_bot]),np.array([0,5.0]),p0,t0); O=np.vstack([blend,P[k+1:]]); O=O[np.argsort(O[:,1])]
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d_=np.gradient(sm,axis=0); d_/=np.hypot(*d_.T)[:,None]; m=np.c_[-d_[:,1],d_[:,0]]; I=O+m*T
    kk=int(np.where((I[:,0]>8)&(I[:,1]>zt+2.5))[0][0]); Pj=I[kk]; Tj=I[kk+2]-I[kk-2]; Tj=Tj/np.hypot(*Tj)
    Ps=np.array([KB+0.01,zt]); L=np.hypot(*(Pj-Ps)); sp=herm(Ps,np.array([1.0,0.0])*L*0.9,Pj,Tj*L*0.9)
    top=np.vstack([[[KB,ks_bot],[KB,zt]],sp[1:],I[kk+1:]])
    poly=Polygon(np.vstack([[[0,keel_top],[KB,keel_top],[KB,leg_bot]],O,top[::-1],[[0,ks_bot]]])).buffer(0).intersection(box(0,-10,200,300))
    return poly,dict(keel_top=keel_top,ks_bot=ks_bot,ks_top=ks_top,leg_bot=leg_bot,zt=zt)
def frame(i):
    xc=C.X[i-1]; res={}
    for lay,(x0,x1) in {'A':(xc-4,xc),'F':(xc,xc+4)}.items():
        xl=(x0+x1)/2; fa,info=face_poly(i,x0,xl); fb,_=face_poly(i,x1,xl); res[lay]=(unary_union([fa.buffer(0.01),fb.buffer(0.01)]).buffer(-0.01),fa,fb,info)
    return xc,res
if __name__=='__main__':
    n=len(args); cols=5; rows=(n+cols-1)//cols; fig,axs=plt.subplots(rows,cols,figsize=(5.2*cols,8.5*rows)); axs=np.atleast_1d(axs).ravel(); log=[]
    for a,i in zip(axs,args):
        b=46-i
        try: xc,res=frame(i)
        except Exception as e: a.set_title(f'frame {b} (our {i}): {e}',fontsize=7); log.append((b,'FAILED',str(e))); continue
        for lay,col in (('A','tab:blue'),('F','tab:red')):
            blk,fa,fb,info=res[lay]
            for g in (unary_union([blk.buffer(0.02),C.mirror(blk).buffer(0.02)]).buffer(-0.02),):
                for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.fill(*gg.exterior.xy,color=col,alpha=.2); a.plot(*gg.exterior.xy,color=col,lw=1.1)
            for g in (fa,fb,C.mirror(fa),C.mirror(fb)):
                for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color=col,lw=.5,ls='--')
        iA=res['A'][3]; a.add_patch(plt.Rectangle((-KB,-20),2*KB,iA['keel_top']+20,color='#999')); a.add_patch(plt.Rectangle((-KB,iA['ks_bot']),2*KB,iA['ks_top']-iA['ks_bot'],color='#999'))
        a.set_aspect('equal'); a.set_xlim(-80,80); a.set_ylim(-5,150); a.grid(alpha=.2); a.set_title(f'frame {b} (our {i}) X={xc:.1f}  keel top {iA["keel_top"]:.1f}, keelson {iA["ks_bot"]:.1f}',fontsize=8)
        log.append((b,round(xc,1),round(iA['keel_top'],2),round(iA['ks_bot'],2),round(iA['leg_bot'],2)))
    plt.savefig('qa/frames_on_keel_2d_%s.png'%('b%d-%d'%(46-max(args),46-min(args))),dpi=42,bbox_inches='tight')
    for r in log: print(r)
