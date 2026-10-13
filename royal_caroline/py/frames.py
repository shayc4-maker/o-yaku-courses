import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import *
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely.validation import make_valid
from joints import P as JP, frame_joint, make_T
from scipy.interpolate import PchipInterpolator
SIDED=4.0            # each timber, fore-aft (model mm)
T_FLOOR, T_TOP = 4.8, 3.3   # moulded thickness at heel / at head (model mm)
fx=json.load(open(O+'/frames_X.json')); FX=fx['X_mm']
_xs=np.linspace(-20,540,561); Zr=PchipInterpolator(_xs,[section(x,kind='pchip')[0,1] for x in _xs]); T=make_T(Zr)
def normals(P):
    T=np.gradient(P,axis=0); T/=np.linalg.norm(T,axis=1)[:,None]
    Nn=np.c_[T[:,1],-T[:,0]]     # rotate -90: for heel->top curve on +Y side gives outward
    if Nn[len(Nn)//2,0]<0: Nn=-Nn
    return Nn
def solid_and_inner(X):
    P=section(X,kind='pchip')                 # +Y side, heel->top
    zr=P[0,1]; yk=max(P[0,0],2.65); ztop=P[-1,1]
    S=Polygon(np.r_[P,[[-P[-1,0],ztop]],(P*[-1,1])[::-1],[[-yk,zr],[yk,zr]]]).buffer(0)
    t=np.interp(P[:,1],[zr,ztop],[T_FLOOR,T_TOP])
    In=P-normals(P)*t[:,None]
    top=ztop+30
    ring=np.r_[In,[[In[-1,0],top]],[[-In[-1,0],top]],(In*[-1,1])[::-1]]
    I=make_valid(Polygon(ring)).buffer(0)
    I=I.intersection(box(-200,zr+0.5,200,top))
    return S,I,P
def timber(xa,xb,i):
    Sa,Ia,Pa=solid_and_inner(xa); Sb,Ib,Pb=solid_and_inner(xb)
    S=unary_union([Sa,Sb]); I=Ia.intersection(Ib)
    zn,zt=frame_joint(i,T); kw=JP['KW']+0.05; W=JP['THROAT_W']; D=60
    keep=unary_union([box(-W,zn,W,zt),Polygon([(-W,zt),(W,zt),(W+D,zt-D),(-W-D,zt-D)])]).intersection(box(-200,zn,200,zt))
    keep=keep.difference(box(-200,zt-1e-9,-kw,500)).difference(box(kw,zt-1e-9,200,500))   # floor throat solid up to keelson notch
    F=S.difference(I.difference(keep))
    F=F.difference(box(-kw,-50,kw,zn))            # slot over keel/hog/deadwood (notch registration)
    F=unary_union([F,box(-kw,zn,kw,zt)])                     # centre column reaches notch bottom and keelson
    F=F.difference(box(-kw,zt,kw,zt+JP['KS_T']+1.0))         # keelson channel
    F=F.intersection(box(-200,-50,200,500))
    if F.geom_type!='Polygon': F=max(F.geoms,key=lambda g:g.area)
    return F,Pa,Pb
parts=[]
for i,xc in enumerate(FX,1):
    for tag,(xa,xb) in (('A',(xc-SIDED,xc)),('F',(xc,xc+SIDED))):
        F,Pa,Pb=timber(xa,xb,i)
        parts.append(dict(frame=i,layer=tag,x0=xa,x1=xb,poly=np.array(F.exterior.coords).tolist(),
            holes=[np.array(h.coords).tolist() for h in F.interiors],area=F.area,
            bbox=F.bounds,zr=float(min(Pa[0,1],Pb[0,1])),joint=frame_joint(i,T),ztop=float(max(Pa[-1,1],Pb[-1,1]))))
        # bevel = max distance between the two faces' outer curves
    print('frame %2d X=%6.2f  heelZ %.1f topZ %.1f  width %.1f  pieces F/A  area %.0f'%(i,xc,parts[-1]['zr'],parts[-1]['ztop'],parts[-1]['bbox'][2]-parts[-1]['bbox'][0],parts[-1]['area']))
json.dump(dict(SIDED=SIDED,T_FLOOR=T_FLOOR,T_TOP=T_TOP,parts=parts),open(O+'/frame_parts.json','w'))
