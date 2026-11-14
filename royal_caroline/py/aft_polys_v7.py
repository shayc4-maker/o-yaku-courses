# v3: F46-48 WHOLE frames (halves joined by a floor under the keelson), wall 1.8; F49-51 still halves. Was: aft frames F46-F51 as HALF frames (+Y / -Y), each standing on the keel wall (Y=2.65) - not whole. Band 3.2 mm inside the outer line; builder lines only. F46-48: 3 faces (own lines). F49-51: one line (mid) used for all 3 faces (ASSUMPTION, only mid lines exist).
import json,glob,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
from shapely.geometry import LineString,Polygon,box
SB=np.array(json.load(open('data/bulwark_line_v3.json'))['S1']); T=json.load(open('data/aft_frames_tops_v1.json')); KB=1.8; TH=3.2   # builder: keel/post thickness above the rabbet is reduced (neck half-width 1.8)
def dense(P,n=300): tck,u=splprep(np.array(P).T,k=min(3,len(P)-1),s=0); return np.array(splev(np.linspace(0,1,n),tck)).T
def extend(C,a,b):
    d0=C[0]-C[3]; d0/=np.hypot(*d0); d1=C[-1]-C[-4]; d1/=np.hypot(*d1); return np.vstack([C[0]+d0*a,C,C[-1]+d1*b])
def band(C,zbot=None,wall=False):
    E=extend(C,8,8); ls=LineString(E); best=None
    for sg in (1,-1):
        oc=ls.offset_curve(sg*TH)
        if oc.geom_type!='LineString' or oc.is_empty: continue
        c2=np.array(oc.coords); 
        if np.hypot(*(c2[0]-E[0]))>np.hypot(*(c2[-1]-E[0])): c2=c2[::-1]
        if best is None or c2[:,0].mean()<best[:,0].mean(): best=c2          # inner = towards the centre line
    poly=Polygon(np.vstack([E,best[::-1]])).buffer(0)
    if wall: poly=poly.intersection(box(KB,-50,300,400))
    if zbot is not None: poly=poly.intersection(box(-50,zbot,300,400))
    if poly.geom_type!='Polygon': poly=max(poly.geoms,key=lambda q:q.area)
    return poly
frames={}
for b,xc in ((46,28.0),(47,17.0),(48,6.0)):
    FP={}
    for nm,X in (('back',xc-4),('mid',xc),('front',xc+4)):
        FP[nm]=band(dense(T['F%d_%s'%(b,nm)]['pts']),wall=True)
    frames[b]=dict(xc=xc,FP=FP)
m=r3.File3dm.Read('rhino/RoyalCaroline_aft_timbers_lines_v5.3dm'); L={l.Index:l.Name for l in m.Layers}
import glob as _g
_D={}
for _f in _g.glob('/tmp/claude-0/-home-user-o-yaku-courses/db230f8a-8640-51de-bf4e-53423595c88f/scratchpad/'+'blank_*.npy'): _D.update({str(k):v for k,v in np.load(_f,allow_pickle=True).item().items()})
def _oy(P,z,tol=.6):
    P=np.asarray(P); mm=abs(P[:,1]-z)<tol; return P[mm][:,0].max() if mm.any() else np.nan
REF=[(_D[str(bb)]['xc'],_D[str(bb)]['FP']['mid']) for bb in (42,43,44,45)]+[(frames[bb]['xc'],np.array(frames[bb]['FP']['mid'].exterior.coords)) for bb in (46,47,48)]
MID={}; OUTP={}; DY={49:0.27+0.42,50:-1.08+2.0-1.85,51:-0.91+2.0-1.22}
for o in m.Objects:
    n=o.Attributes.Name
    if L[o.Attributes.LayerIndex].startswith('PROPOSED_frames') and hasattr(o.Geometry,'Domain'):
        g=o.Geometry; t=np.linspace(g.Domain.T0,g.Domain.T1,40); P=np.array([[q.X,q.Y,q.Z] for q in (g.PointAt(x) for x in t)]); b=int(n[1:3]); xc=-5.0-11.0*(b-49)
        C=dense(P[:,1:]); C[:,0]+=DY[b]; MID[b]=(xc,C)
def yfun(C):
    o=np.argsort(C[:,1]); return lambda z: np.interp(z,C[o,1],C[o,0],left=np.nan,right=np.nan)
FUN={b:(MID[b][0],yfun(MID[b][1])) for b in MID}
for b,(xc,C) in MID.items():
    zb=float(C[0,1]); zt=float(C[-1,1]); zs=np.linspace(zb,zt,60); FPf={}
    for nm,dx in (('back',-4.0),('mid',0.0),('front',4.0)):
        pts=[]
        for z in zs:
            xs=np.array([x for x,_ in REF]+[FUN[k][0] for k in FUN]); ys=np.array([_oy(P,z) for _,P in REF]+[FUN[k][1](z) for k in FUN]); ok=~np.isnan(ys); xs,ys=xs[ok],ys[ok]
            if nm=='mid': y=float(FUN[b][1](z))
            else:
                near=np.argsort(abs(xs-(xc+dx)))[:5]; cc=np.polyfit(xs[near],ys[near],min(3,len(near)-1)); y=float(np.polyval(cc,xc+dx))
            pts.append([y,z])
        OUTP.setdefault(b,{})[nm]=np.array(pts); FPf[nm]=band(np.array(pts),zbot=zb,wall=False)
    frames[b]=dict(xc=xc,FP=FPf)
    print('F%d outer Y at Z=110: back %.2f mid %.2f front %.2f'%((b,)+tuple(_oy(np.array(FPf[k].exterior.coords),110) for k in ('back','mid','front'))))
out={}
for b,D in sorted(frames.items()):
    z={k:float(np.interp(D['xc']+dx,SB[:,0],SB[:,1])) for k,dx in (('back',-4),('mid',0),('front',4))}
    if b<=48:
        from shapely.ops import unary_union
        fpw={}
        for k,v in D['FP'].items():
            zm=v.bounds[1]; fpw[k]=unary_union([v,Polygon([(-y,z) for y,z in v.exterior.coords]),box(-KB-0.01,zm,KB+0.01,zm+TH)]).buffer(0.01).buffer(-0.01)
        fp={k:np.array(v.exterior.coords) for k,v in fpw.items()}; env=unary_union([Polygon(q) for q in fp.values()]).buffer(0.01).buffer(-0.01)
        out['%d'%b]=dict(xc=D['xc'],env=np.array(env.exterior.coords),FP=fp,z=z); continue
    for side,sg in (('S',1),('P',-1)):
        fp={k:np.array([[sg*y,zz] for y,zz in v.exterior.coords]) for k,v in D['FP'].items()}
        env=Polygon(fp['back']).union(Polygon(fp['mid'])).union(Polygon(fp['front'])).buffer(0.01).buffer(-0.01)
        if env.geom_type!='Polygon': env=max(env.geoms,key=lambda q:q.area)
        out['%d_%s'%(b,side)]=dict(xc=D['xc'],env=np.array(env.exterior.coords),FP=fp,z=z)
    print('F%d X=%.1f'%(b,D['xc']),'areas back/mid/front %s mm2'%'/'.join('%.0f'%D['FP'][k].area for k in('back','mid','front')),'Z range %.1f..%.1f'%(D['FP']['mid'].bounds[1],D['FP']['mid'].bounds[3]))
np.save('/tmp/claude-0/-home-user-o-yaku-courses/db230f8a-8640-51de-bf4e-53423595c88f/scratchpad/aft_blank_v7.npy',out,allow_pickle=True)

np.save('/tmp/claude-0/-home-user-o-yaku-courses/db230f8a-8640-51de-bf4e-53423595c88f/scratchpad/'+'outer_pts_v7.npy',OUTP,allow_pickle=True)
