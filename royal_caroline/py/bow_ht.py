# Forward frame: 10 hawse timbers HT1..HT10 (5 per side), vertical planks parallel to the centre plane
import json,numpy as np,cv2,rhino3dm as r3
from shapely.geometry import Polygon
from scipy.interpolate import interp1d
f0=r3.File3dm.Read('rhino/RoyalCaroline_hull_1to48_v9.3dm')
S={}
for o in f0.Objects:
    if f0.Layers[o.Attributes.LayerIndex].Name=='BOW_SURFACE_faired_sections':
        g=o.Geometry; n=g.PointCount; p=np.array([[g.Point(i).X,g.Point(i).Y,g.Point(i).Z] for i in range(n)])
        S[round(p[0,0],2)]=p
XS=np.array(sorted(S)); print(len(XS),'sections X',XS[0],XS[-1])
sec={}
for x in XS:
    p=S[x]; o=np.argsort(p[:,2]); sec[x]=(p[o,2],np.abs(p[o,1]))
ZMIN=interp1d(XS,[sec[x][0][0] for x in XS],bounds_error=False,fill_value=np.nan)
S1=sec[XS[0]]; ZHEAD=88.0; ZT=119.6; XBH=546.0; XA=528.08
def y_s1(z): return float(np.interp(z,S1[0],S1[1]))
Y88=y_s1(ZHEAD)
def Yo(x,z):
    if x<XS[0] or x>XS[-1]: return np.nan
    if z>ZHEAD:
        if x>XBH or z>ZT: return np.nan
        base=Yo(x,ZHEAD-1e-6)
        return base+(y_s1(z)-Y88) if not np.isnan(base) else np.nan
    i=np.searchsorted(XS,x); i0=max(i-1,0); vs=[]
    for xx in (XS[i0],XS[min(i,len(XS)-1)]):
        zz,yy=sec[xx]
        if z<zz[0]-1e-9 or z>zz[-1]+1e-9: return np.nan
        vs.append(float(np.interp(z,zz,yy)))
    x0,x1=XS[i0],XS[min(i,len(XS)-1)]
    return vs[0] if x1==x0 else vs[0]+(vs[1]-vs[0])*(x-x0)/(x1-x0)
GX=np.arange(XA,XS[-1]+0.001,0.1); GZ=np.arange(0,ZT+0.001,0.1)
Y=np.full((len(GZ),len(GX)),np.nan)
for i,x in enumerate(GX):
    zm=float(ZMIN(x))
    for j,z in enumerate(GZ):
        if z>=zm: Y[j,i]=Yo(x,z)
np.save('/tmp/claude-0/-home-user-o-yaku-courses/9b1663d1-123c-5304-bded-1182034acdbc/scratchpad/Ygrid.npy',Y)
def region(y0):
    m=(np.nan_to_num(Y,nan=-1)>=y0).astype(np.uint8)
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    if not cs: return None
    c=max(cs,key=cv2.contourArea)[:,0,:]
    pg=Polygon([(GX[0]+a*0.1,GZ[0]+b*0.1) for a,b in c]).buffer(0.05).simplify(0.04)
    return max(pg.geoms,key=lambda g:g.area) if pg.geom_type=='MultiPolygon' else pg
TH=5.3; HB=TH/2; Ymax=float(np.nanmax(Y[:, 0]))
W=(Ymax-HB)/5; print('Ymax',round(Ymax,2),'strip width',round(W,2))
HT={}
for k in range(1,6):
    y0=HB+(k-1)*W; y1=y0+W; pg=region(y0+0.01)
    HT[k]=(y0,y1,pg); print('plank',k,'y',round(y0,2),round(y1,2),'area',round(pg.area,1) if pg is not None else None,[round(v,1) for v in pg.bounds] if pg is not None else '')
import pickle; pickle.dump({k:(a,b,list(p.exterior.coords)) for k,(a,b,p) in HT.items()},open('data/bow_ht_profiles.pkl','wb'))

# ---- 3dm: planks as solids (extruded along Y), hawse-hole markers, context
f=r3.File3dm.Read('rhino/RoyalCaroline_frames45_on_new_keel_REF.3dm')
out=r3.File3dm(); out.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def L(name,rgb):
    l=r3.Layer(); l.Name=name; l.Color=rgb+(255,); return out.Layers.Add(l)
for o in f.Objects:
    n=f.Layers[o.Attributes.LayerIndex].Name
    if n in('BACKBONE_builder','FRAME_44','FRAME_45'):
        idx=[i for i in range(len(out.Layers)) if out.Layers[i].Name==n]
        idx=idx[0] if idx else L(n,(150,150,150))
        at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=o.Attributes.Name; out.Objects.AddBrep(o.Geometry,at)
def plank(name,k,side):
    y0,y1,pg=HT[k]; ys=1 if side=='S' else -1
    pts=[(x,ys*y0,z) for x,z in pg.exterior.coords]
    pl=r3.Polyline(len(pts))
    for p in pts: pl.Add(*p)
    ex=r3.Extrusion.Create(pl.ToPolylineCurve(),W*ys*-1 if False else W,True)
    br=ex.ToBrep(True); bb=br.GetBoundingBox()
    lo,hi=sorted((ys*y0,ys*y1)); br.Translate(r3.Vector3d(0,lo-bb.Min.Y,0))
    assert br.IsSolid and br.IsValid,name
    return br
rows=[]
for k in range(1,6):
    for side in ('S','P'):
        ht=(6-k) if side=='S' else (5+k)
        nm='HT%d'%ht; idx=L(nm,(200-30*k,120+20*k,80+20*(k%3)))
        br=plank(nm,k,side); at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=nm+'_%s_k%d'%(side,k); out.Objects.AddBrep(br,at)
        y0,y1,pg=HT[k]; rows.append((nm,side,round(y0,2),round(y1,2),round(pg.area,1),[round(v,1) for v in pg.bounds]))
# approximate hawse holes (HT2 starboard, HT9 port = 4th strip from the centre): dia 4, axis along X, Z 100
ih=L('HAWSE_HOLE_approx',(220,40,40))
y0,y1,pg=HT[4]; zc=100.0; yc=(y0+y1)/2
xs=GX[[np.nan_to_num(Yo(x,zc),nan=-1)>=y0+2 for x in GX]]
x0h,x1h=float(xs.min()),float(xs.max())
for ys in (1,-1):
    import math
    cyl=r3.Cylinder(r3.Circle(r3.Point3d(0,0,0),2.0),x1h-x0h)
    br=cyl.ToBrep(True,True); br.Transform(r3.Transform.Rotation(math.pi/2,r3.Vector3d(0,1,0),r3.Point3d(0,0,0))); br.Translate(r3.Vector3d(x0h,ys*yc,zc)); at=r3.ObjectAttributes(); at.LayerIndex=ih; at.Name='hawse_hole_%s'%('S' if ys>0 else 'P'); out.Objects.AddBrep(br,at)
out.Write('rhino/RoyalCaroline_bow_HT_v1.3dm',7)
print(rows); print('hole x',round(x0h,1),round(x1h,1),'y',round(yc,1))
