# Central frame (our 23 = builder 23) planned on the NEW lofted body plan, with the agreed laps onto the keel and keelson, 2D
import sys,json,numpy as np
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
from scipy.interpolate import splprep,splev
from scipy.signal import savgol_filter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import hull_new_sections as HN
OUR=int(sys.argv[1]) if len(sys.argv)>1 else 23
KB=2.65; T=3.2; PEN_LOW=2.5; PEN_UP=float(__import__("os").environ.get("PEN_UP","2.5"))
BB=json.load(open('data/step44_profiles.json')); XF=json.load(open('data/frames_X.json'))['X_mm']
PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
UB=unary_union(list(PP.values()))
mirror=lambda g: __import__('shapely.affinity',fromlist=['scale']).scale(g,xfact=-1,yfact=1,origin=(0,0))
def hull_line(X):
    P=HN.section(X); zz=np.round(P[:,1],2); _,ui=np.unique(zz,return_index=True); P=P[ui]; P=P[np.argsort(P[:,1])]
    z0,z1=P[0,1],P[-1,1]; zs=np.r_[z0,np.linspace(z0,z1,15)[1:]]; pts=np.array([(float(np.interp(z,P[:,1],P[:,0])),float(z)) for z in zs]); pts[0,0]=max(pts[0,0],3.2)
    tk,u=splprep(pts.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tk); return np.c_[y,z]
GAP=float(sys.argv[2]) if len(sys.argv)>2 else None; KST=float(sys.argv[3]) if len(sys.argv)>3 else None
def keel_levels(X):
    g=UB.intersection(LineString([(X,-30),(X,200)])); sg=sorted((l.bounds[1],l.bounds[3]) for l in getattr(g,'geoms',[g]))
    sg=[s for s in sg if s[1]-s[0]>0.05]; mrg=[list(sg[0])]
    for s in sg[1:]:
        if s[0]-mrg[-1][1]<0.3: mrg[-1][1]=max(mrg[-1][1],s[1])
        else: mrg.append(list(s))
    kt=mrg[0][1]
    if GAP is not None: return kt,(kt+GAP,kt+GAP+KST)       # B3 (plan 6) values: gap keel-keelson and keelson thickness
    return kt,(mrg[1][0],mrg[1][1]) if len(mrg)>1 else (None,None)
def herm(P0,T0,P1,T1,n=40):
    t=np.linspace(0,1,n)[:,None]; return (2*t**3-3*t**2+1)*P0+(t**3-2*t**2+t)*T0+(-2*t**3+3*t**2)*P1+(t**3-t**2)*T1
def face_poly(Xf,Xlay):
    keel_top,(ks_bot,ks_top)=keel_levels(Xlay); leg_bot=keel_top-PEN_LOW; zt=ks_bot+PEN_UP
    P=hull_line(Xf); k=int(np.argmin(np.abs(P[:,1]-(leg_bot+8)))); p0=P[k]; t0=(P[k+3]-P[k-3]); t0=t0/np.hypot(*t0)*11
    blend=herm(np.array([KB,leg_bot]),np.array([0,5.0]),p0,t0); O=np.vstack([blend,P[k+1:]]); O=O[np.argsort(O[:,1])]
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d_=np.gradient(sm,axis=0); d_/=np.hypot(*d_.T)[:,None]; m=np.c_[-d_[:,1],d_[:,0]]; I=O+m*T
    kk=int(np.where((I[:,0]>8)&(I[:,1]>zt+2.5))[0][0]); Pj=I[kk]; Tj=I[kk+2]-I[kk-2]; Tj=Tj/np.hypot(*Tj)
    Ps=np.array([KB+0.01,zt]); L=np.hypot(*(Pj-Ps)); sp=herm(Ps,np.array([1.0,0.0])*L*0.9,Pj,Tj*L*0.9)
    top=np.vstack([[[KB,ks_bot],[KB,zt]],sp[1:],I[kk+1:]])
    poly=Polygon(np.vstack([[[0,keel_top],[KB,keel_top],[KB,leg_bot]],O,top[::-1],[[0,ks_bot]]])).buffer(0).intersection(box(0,-10,200,300))
    return poly,dict(keel_top=keel_top,ks_bot=ks_bot,ks_top=ks_top,leg_bot=leg_bot,zt=zt,O=O,I=I)
xc=XF[OUR-1]; res={}
for lay,(x0,x1) in {'A':(xc-4,xc),'F':(xc,xc+4)}.items():
    xl=(x0+x1)/2; fa,info=face_poly(x0,xl); fb,_=face_poly(x1,xl); res[lay]=(unary_union([fa.buffer(0.01),fb.buffer(0.01)]).buffer(-0.01),fa,fb,info)
iA=res['A'][3]
print('frame our %d (builder %d) X=%.2f; faces X=%.2f/%.2f/%.2f'%(OUR,46-OUR,xc,xc-4,xc,xc+4))
print('keel top Z=%.2f, keelson bottom Z=%.2f top Z=%.2f; leg bottom Z=%.2f, top legs Z=%.2f'%(iA['keel_top'],iA['ks_bot'],iA['ks_top'],iA['leg_bot'],iA['zt']))
for lay in 'AF':
    b=res[lay][0]; print(lay,'area %.0f mm2 valid %s bounds %s'%(b.area,b.is_valid,[round(v,1) for v in b.bounds]))
json.dump({k:(res[k][0].exterior.coords[:] if hasattr(res[k][0],'exterior') else None) for k in 'AF'},open('data/frame%d_central_outline%s.json'%(46-OUR,'_B3' if GAP is not None else ''),'w'))
fig,axs=plt.subplots(1,3,figsize=(22,11),gridspec_kw={'width_ratios':[1.1,1,1]})
def draw(a,xlim,ylim,title,lab=True):
    for lay,col in (('A','tab:blue'),('F','tab:red')):
        blk,fa,fb,info=res[lay]
        for g in (unary_union([blk.buffer(0.02),mirror(blk).buffer(0.02)]).buffer(-0.02),):
            for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.fill(*gg.exterior.xy,color=col,alpha=.18); a.plot(*gg.exterior.xy,color=col,lw=1.3)
        for g in (fa,fb,mirror(fa),mirror(fb)):
            for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color=col,lw=.6,ls='--')
    a.add_patch(plt.Rectangle((-KB,-20),2*KB,iA['keel_top']+20,color='#888',alpha=.8)); a.add_patch(plt.Rectangle((-KB,iA['ks_bot']),2*KB,iA['ks_top']-iA['ks_bot'],color='#888',alpha=.8))
    a.set_aspect('equal'); a.set_xlim(*xlim); a.set_ylim(*ylim); a.grid(alpha=.25); a.set_title(title,fontsize=10)
draw(axs[0],(-85,85),(-5,110),'Frame builder %d (our %d), X=%.1f - layer A blue (X-4..X), layer F red (X..X+4); gray = keel + keelson; dashed = exact face lines'%(46-OUR,OUR,xc))
draw(axs[1],(-14,40),(iA['keel_top']-14,iA['keel_top']+22),'Bottom: laps onto the keel (keel top Z=%.1f, legs down to Z=%.1f)'%(iA['keel_top'],iA['leg_bot']))
draw(axs[2],(-14,40),(iA['ks_bot']-8,iA['ks_top']+24),'Top: inverted ח over the keelson (keelson Z %.1f-%.1f, leg tops Z=%.1f)'%(iA['ks_bot'],iA['ks_top'],iA['zt']))
for a,z in ((axs[1],iA['leg_bot']),(axs[1],iA['keel_top']),(axs[2],iA['zt']),(axs[2],iA['ks_bot'])): a.axhline(z,color='k',lw=.4,ls=':'); a.text(-13,z+.3,'Z=%.2f'%z,fontsize=8)
fig.savefig('qa/frame%d_central_2d%s.png'%(46-OUR,'_B3' if GAP is not None else ''),dpi=70,bbox_inches='tight')
