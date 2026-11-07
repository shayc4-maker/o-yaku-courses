# Central frame (our 23 = builder 23) planned on the NEW lofted body plan, with the agreed laps onto the keel and keelson, 2D
import sys,json,numpy as np
from shapely.geometry import Polygon,box,LineString
from shapely.ops import unary_union
from scipy.interpolate import splprep,splev
from scipy.signal import savgol_filter
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import hull_new_sections as HN
SHARP=__import__('os').environ.get('SHARP','1')=='1'; INNER_SMOOTH=__import__('os').environ.get('INNER_SMOOTH','1')=='1'; NOSTEP=__import__('os').environ.get('NOSTEP','0')=='1'; KB=2.65; T=3.2; PEN_LOW=2.5; PEN_UP=float(__import__("os").environ.get("PEN_UP","0.6"))
BB=json.load(open('data/step44_profiles.json')); XF=json.load(open('data/frames_X.json'))['X_mm']
PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
UB=unary_union(list(PP.values()))
mirror=lambda g: __import__('shapely.affinity',fromlist=['scale']).scale(g,xfact=-1,yfact=1,origin=(0,0))
def hull_line(X):
    P=HN.section(min(X,527.7)); zz=np.round(P[:,1],2); _,ui=np.unique(zz,return_index=True); P=P[ui]; P=P[np.argsort(P[:,1])]
    z0,z1=P[0,1],P[-1,1]; zs=np.r_[z0,np.linspace(z0,z1,15)[1:]]; pts=np.array([(float(np.interp(z,P[:,1],P[:,0])),float(z)) for z in zs]); pts[0,0]=max(pts[0,0],3.2)
    tk,u=splprep(pts.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tk); return np.c_[y,z]
GAP=None; KST=None
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
    if INNER_SMOOTH:     # normalise the inner line: smoothing spline through nodes every ~3 mm (removes the offset noise and the blend kink); deviation from the true offset stays < 0.15 mm
        from scipy.interpolate import splprep as _sp,splev as _sv
        sI=np.r_[0,np.cumsum(np.hypot(*np.diff(I,axis=0).T))]; nn=max(int(sI[-1]/3.0),8); tt=np.linspace(0,sI[-1],nn); Q=np.c_[np.interp(tt,sI,I[:,0]),np.interp(tt,sI,I[:,1])]
        tk_,u_=_sp(Q.T,k=3,s=nn*0.012); y_,z_=_sv(np.linspace(0,1,len(I)),tk_); I_old=I; I=np.c_[y_,z_]; I[0]=I_old[0]; I[-1]=I_old[-1]
    kk=int(np.where((I[:,0]>8)&(I[:,1]>zt+2.5))[0][0]); Pj=I[kk]; Tj=I[kk+2]-I[kk-2]; Tj=Tj/np.hypot(*Tj)
    if NOSTEP:      # across the backbone width (+-KB) two straight horizontal lines: the floor on the keel (pocket floor) and the seat under the keelson; no steps, no legs
        Ps=np.array([KB,ks_bot]); L=np.hypot(*(Pj-Ps)); sp=herm(Ps,np.array([1.0,0.0])*L*0.9,Pj,Tj*L*0.9); top=np.vstack([[[0.0,ks_bot]],sp,I[kk+1:]])
        poly=Polygon(np.vstack([[[0,leg_bot],[KB,leg_bot]],O[O[:,1]>leg_bot+1e-6],top[::-1]])).buffer(0).intersection(box(0,-10,200,300))
        return poly,dict(keel_top=keel_top,ks_bot=ks_bot,ks_top=ks_top,leg_bot=leg_bot,zt=ks_bot,O=O,I=I)
    Ps=np.array([KB+0.01,zt]); L=np.hypot(*(Pj-Ps)); sp=herm(Ps,np.array([1.0,0.0])*L*0.9,Pj,Tj*L*0.9)
    top=np.vstack([[[KB,ks_bot],[KB,zt]],sp[1:],I[kk+1:]])
    poly=Polygon(np.vstack([[[0,keel_top],[KB,keel_top],[KB,leg_bot]],O,top[::-1],[[0,ks_bot]]])).buffer(0).intersection(box(0,-10,200,300))
    return poly,dict(keel_top=keel_top,ks_bot=ks_bot,ks_top=ks_top,leg_bot=leg_bot,zt=zt,O=O,I=I)
def face_poly_sharp(Xf,Xlay):
    """no radii, no tangent joins: floor (horizontal, +-KB) -> straight to the exact hull line; seat (horizontal) -> straight out until it meets the inner line"""
    keel_top,(ks_bot,ks_top)=keel_levels(Xlay); leg_bot=keel_top-PEN_LOW
    P=hull_line(Xf); O=P[np.argsort(P[:,1])]
    # the floor (horizontal at leg_bot) runs outward until it meets the EXACT hull line; nothing is added or bent
    below=np.where(O[:,1]<leg_bot)[0]
    if len(below)==0 or below[-1]+1>=len(O): raise ValueError('hull line does not cross the floor level (floor %.2f, hull starts at %.2f)'%(leg_bot,O[0,1]))
    j=below[-1]; a_,b_=O[j],O[j+1]; t_=(leg_bot-a_[1])/(b_[1]-a_[1]); Pf=a_+t_*(b_-a_); O=np.vstack([Pf,O[j+1:]])
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d_=np.gradient(sm,axis=0); d_/=np.hypot(*d_.T)[:,None]; m=np.c_[-d_[:,1],d_[:,0]]; I=O+m*T
    if INNER_SMOOTH:
        from scipy.interpolate import splprep as _sp,splev as _sv
        sI=np.r_[0,np.cumsum(np.hypot(*np.diff(I,axis=0).T))]; nn=max(int(sI[-1]/3.0),8); tt=np.linspace(0,sI[-1],nn); Q=np.c_[np.interp(tt,sI,I[:,0]),np.interp(tt,sI,I[:,1])]
        tk_,u_=_sp(Q.T,k=3,s=nn*0.012); y_,z_=_sv(np.linspace(0,1,len(I)),tk_); I_old=I; I=np.c_[y_,z_]; I[0]=I_old[0]; I[-1]=I_old[-1]
    i0=int(np.argmax(I[:,0]>=KB-1e-6))
    cross=np.where((I[i0:,1]>=ks_bot))[0]
    if len(cross)==0: raise ValueError('inner line never reaches the seat')
    j=i0+int(cross[0])
    if j==i0: seat_end=np.array([I[j,0],ks_bot]); top=np.vstack([[[0.0,ks_bot]],[[KB,ks_bot]],I[j:]]) if I[j,0]>KB+1e-6 else np.vstack([[[0.0,ks_bot],[KB,ks_bot]],I[j:]])
    else:
        a,b=I[j-1],I[j]; t_=(ks_bot-a[1])/(b[1]-a[1]); Pc=a+t_*(b-a); top=np.vstack([[[0.0,ks_bot]],[Pc],I[j:]])
    poly=Polygon(np.vstack([[[0,leg_bot]],O,top[::-1]])).buffer(0).intersection(box(0,-10,200,300))
    return poly,dict(keel_top=keel_top,ks_bot=ks_bot,ks_top=ks_top,leg_bot=leg_bot,zt=ks_bot,O=O,I=I)
_face_poly_old=face_poly
def face_poly(Xf,Xlay):
    return face_poly_sharp(Xf,Xlay) if (NOSTEP and SHARP) else _face_poly_old(Xf,Xlay)

def frame(OUR):
    xc=XF[OUR-1]; res={}
    for lay,(x0,x1) in {'A':(xc-4,xc),'F':(xc,xc+4)}.items():
        fa,info=face_poly(x0,x0); fb,infob=face_poly(x1,x1); info['b']=infob; res[lay]=(unary_union([fa.buffer(0.01),fb.buffer(0.01)]).buffer(-0.01),fa,fb,info)
    return xc,res
if __name__=='__main__':
    builder=[int(a) for a in sys.argv[1:]]; n=len(builder); fig,axs=plt.subplots(3,n,figsize=(5.3*n,17),gridspec_kw={'height_ratios':[1.6,1,1]}); out={}
    for j,b in enumerate(builder):
        OUR=46-b
        try: xc,res=frame(OUR)
        except Exception as e:
            axs[0,j].set_title('builder %d: FAILED %s'%(b,e),fontsize=8); print('builder',b,'FAILED',e); continue
        iA=res['A'][3]; out[b]=dict(X=xc,keel_top=iA['keel_top'],ks_bot=iA['ks_bot'],ks_top=iA['ks_top'],A=list(res['A'][0].exterior.coords),F=list(res['F'][0].exterior.coords))
        print('builder %2d (our %2d) X=%6.1f keel top %5.2f keelson %5.2f..%5.2f gap %4.2f | area A %4.0f F %4.0f valid %s %s'%(b,OUR,xc,iA['keel_top'],iA['ks_bot'],iA['ks_top'],iA['ks_bot']-iA['keel_top'],res['A'][0].area,res['F'][0].area,res['A'][0].is_valid,res['F'][0].is_valid))
        def draw(a,xl,yl,title):
            for lay,col in (('A','tab:blue'),('F','tab:red')):
                blk,fa,fb,info=res[lay]
                for g in (unary_union([blk.buffer(0.02),mirror(blk).buffer(0.02)]).buffer(-0.02),):
                    for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.fill(*gg.exterior.xy,color=col,alpha=.18); a.plot(*gg.exterior.xy,color=col,lw=1.2)
                for g in (fa,fb,mirror(fa),mirror(fb)):
                    for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color=col,lw=.5,ls='--')
            a.add_patch(plt.Rectangle((-KB,-20),2*KB,iA['keel_top']+20,color='#888',alpha=.8)); a.add_patch(plt.Rectangle((-KB,iA['ks_bot']),2*KB,iA['ks_top']-iA['ks_bot'],color='#888',alpha=.8))
            a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(title,fontsize=9)
        draw(axs[0,j],(-85,85),(-5,115),'frame %d (our %d) X=%.1f'%(b,OUR,xc))
        draw(axs[1,j],(-14,40),(iA['keel_top']-12,iA['keel_top']+16),'keel lap: top %.2f, gap %.2f'%(iA['keel_top'],iA['ks_bot']-iA['keel_top']))
        draw(axs[2,j],(-14,40),(iA['ks_bot']-6,iA['ks_top']+10),'keelson %.2f..%.2f'%(iA['ks_bot'],iA['ks_top']))
    tag='b%d-%d'%(min(builder),max(builder)); fig.savefig('qa/frames5_%s.png'%tag,dpi=55,bbox_inches='tight'); json.dump(out,open('data/frames5_%s.json'%tag,'w'))
