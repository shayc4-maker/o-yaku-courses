# Stern v2: counter timbers canted by the angle of the stern windows in plan_5 (12.5 deg, top aft), wing transom, sternpost notched
import json,math,numpy as np,rhino3dm as r3
from shapely.geometry import Polygon,box
TH=5.3; ANG=12.5; T=math.tan(math.radians(ANG))
pv={p['name']:p for p in json.load(open('data/parts_v10.json'))}
parts=json.load(open('data/backbone_parts_v2.json')) if False else None
BB=json.load(open('data/step44_profiles.json'))
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n,rgb):
    l=r3.Layer(); l.Name=n; l.Color=rgb+(255,); return f.Layers.Add(l)
def extrude_xz(poly,y0,y1,layer,name):
    pl=r3.Polyline(len(poly)+1)
    for x,z in poly: pl.Add(x,y0,z)
    pl.Add(poly[0][0],y0,poly[0][1])
    ex=r3.Extrusion.Create(pl.ToPolylineCurve(),y1-y0,True); br=ex.ToBrep(True); bb=br.GetBoundingBox()
    v=np.array([[br.Vertices[i].Location.Y] for i in range(len(br.Vertices))]); br.Translate(r3.Vector3d(0,y0-v.min(),0))
    assert br.IsSolid and br.IsValid,name
    at=r3.ObjectAttributes(); at.LayerIndex=layer; at.Name=name; f.Objects.AddBrep(br,at)
def extrude_xy(poly,z0,z1,layer,name):   # profile in XY, extruded along Z
    pg=Polygon(poly).buffer(0).simplify(0.005)
    if pg.geom_type!='Polygon': pg=max(pg.geoms,key=lambda g:g.area)
    poly=list(pg.exterior.coords)[:-1]
    pl=r3.Polyline(len(poly)+1)
    for x,y in poly: pl.Add(x,y,z0)
    pl.Add(poly[0][0],poly[0][1],z0)
    ex=r3.Extrusion.Create(pl.ToPolylineCurve(),z1-z0,True); br=ex.ToBrep(True)
    v=np.array([br.Vertices[i].Location.Z for i in range(len(br.Vertices))]); br.Translate(r3.Vector3d(0,0,z0-v.min()))
    assert br.IsSolid and br.IsValid,name
    at=r3.ObjectAttributes(); at.LayerIndex=layer; at.Name=name; f.Objects.AddBrep(br,at)
# backbone context except the sternpost (rebuilt notched) 
ib=lay('BACKBONE_builder',(150,150,150))
for k,rg in BB.items():
    pg=Polygon(max(rg,key=lambda p:Polygon(p).area)).buffer(0).simplify(0.002)
    if k=='Boss-Extrude5[3]':   # sternpost
        wt=pv['WING_TRANSOM']; a=np.array(wt['poly']); xt0,xt1=a[:,0].min(),a[:,0].max(); zt0,zt1=wt['off'],wt['off']+wt['th']
        post=pg.difference(box(xt0-0.0,zt0,xt1,zt1))
        assert post.geom_type=='Polygon',post.geom_type
        print('post area',round(pg.area,1),'-> notched',round(post.area,1),'transom X',xt0,xt1,'Z',zt0,zt1)
        extrude_xz(list(post.exterior.coords)[:-1],-TH/2,TH/2,lay('STERNPOST_notched',(120,170,90)),'STERNPOST_notched')
    elif k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]'):
        extrude_xz(list(pg.exterior.coords)[:-1],-TH/2,TH/2,ib,k)
# rudder = builder's three bodies, as in the STEP
ir=lay('RUDDER_builder',(180,120,200))
for k in('Split1[1]','Split1[2]','Boss-Extrude4[2]'):
    pg=Polygon(max(BB[k],key=lambda p:Polygon(p).area)).buffer(0).simplify(0.002); extrude_xz(list(pg.exterior.coords)[:-1],-2,2,ir,k)
# --- measured from plan_7 (aft elevation) and plan_4a (plan view); see STATE.md
R=95.0                                  # plan radius of the aft line (mm), sag = y^2/(2R); same arch measured in the elevation
sag=lambda y: y*y/(2*R)
HW=49.0
def arc_poly(xa,xf,n=40):
    ys=np.linspace(-HW,HW,n)
    return [(xa+sag(y),y) for y in ys]+[(xf+sag(y),y) for y in ys[::-1]]
iw=lay('WING_TRANSOM',(220,80,60))
extrude_xy(arc_poly(-11.8,-5.0),72.0,78.0,iw,'WING_TRANSOM')
for n in ('TRANSOM_2_1','TRANSOM_2_2','TRANSOM_3_1','TRANSOM_3_2'):
    p=pv[n]; extrude_xy([tuple(q) for q in p['poly']],p['off'],p['off']+p['th'],lay(n,(200,150,80)),n)
Y=[7.8,26.4,44.1]; SPLAY=[1.8,5.5,8.9]; ZB=78.0; ZC=147.9
DROP=[round(sag(y),1) for y in Y]; print('Y',Y,'splay',SPLAY,'arch drop/foot shift',DROP)
XL=-11.8; W=5.0; sec=W/math.cos(math.radians(ANG)); ZTOP=[ZC-d for d in DROP]
def poly_for(i):
    xl=lambda z: XL+DROP[i]-T*(z-ZB)
    return [(xl(ZB),ZB),(xl(ZB)+sec,ZB),(xl(ZTOP[i])+sec,ZTOP[i]),(xl(ZTOP[i]),ZTOP[i])]
ic=lay('COUNTER_TIMBERS',(90,140,200))
def shear_y(br,t,z0):
    xf=r3.Transform(1.0)
    # y' = y + t*(z - z0): build by composing a shear matrix through rotation-free linear map
    return br
for s_,sg in (('S',1),('P',-1)):
    for i,y in enumerate(Y):
        tz=math.tan(math.radians(SPLAY[i])); pl_=poly_for(i); yc=sg*y
        pl=r3.Polyline(len(pl_)+1)
        for x,z in pl_: pl.Add(x,yc-2.0,z)
        pl.Add(pl_[0][0],yc-2.0,pl_[0][1])
        ex=r3.Extrusion.Create(pl.ToPolylineCurve(),4.0,True); br=ex.ToBrep(True)
        v=np.array([br.Vertices[k].Location.Y for k in range(len(br.Vertices))]); br.Translate(r3.Vector3d(0,yc-2.0-v.min(),0))
        xf=r3.Transform(1.0); xf.M12=sg*tz; xf.M13=-sg*tz*ZB
        assert br.Transform(xf)
        vv=np.array([[br.Vertices[k].Location.X,br.Vertices[k].Location.Y,br.Vertices[k].Location.Z] for k in range(len(br.Vertices))])
        assert br.IsSolid and br.IsValid,(s_,y)
        at=r3.ObjectAttributes(); at.LayerIndex=ic; at.Name='COUNTER_TIMBER_%s%d'%(s_,i+1); f.Objects.AddBrep(br,at)
        if i==2 and sg==1: print('outer S top vertex y range',vv[:,1].min().round(1),vv[:,1].max().round(1),'z',vv[:,2].min(),vv[:,2].max().round(1))
f.Write('rhino/RoyalCaroline_stern_v3.3dm',7)
json.dump({'angle_deg':ANG,'counter_Y':Y,'splay_deg':SPLAY,'foot_shift':DROP,'ztop':ZTOP,'R_plan':R},open('data/stern_v3_params.json','w'))
print(len(f.Objects),'objects')
