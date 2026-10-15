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
# wing transom (as v10 outline, Z 72..78) 
a=np.array(pv['WING_TRANSOM']['poly']); iw=lay('WING_TRANSOM',(220,80,60))
extrude_xy([tuple(p) for p in pv['WING_TRANSOM']['poly']],pv['WING_TRANSOM']['off'],pv['WING_TRANSOM']['off']+pv['WING_TRANSOM']['th'],iw,'WING_TRANSOM')
for n in ('TRANSOM_2_1','TRANSOM_2_2','TRANSOM_3_1','TRANSOM_3_2'):
    p=pv[n]; extrude_xy([tuple(q) for q in p['poly']],p['off'],p['off']+p['th'],lay(n,(200,150,80)),n)
# counter timbers: Y positions proportional to the stern photo (inner pair beside the post, then 0.40 and 0.73 of the wing transom half width)
HW=49.0; ys=[0.12*HW,0.40*HW,0.73*HW]; Y=[round(v,1) for v in ys]; print('counter Y',Y)
ZB,ZTOP=78.0,147.9; XL=-11.8; W=5.0; sec=W/math.cos(math.radians(ANG))
def counter():
    xl=lambda z: XL-T*(z-ZB)
    return [(xl(ZB),ZB),(xl(ZB)+sec,ZB),(xl(ZTOP)+sec,ZTOP),(xl(ZTOP),ZTOP)]
poly=counter(); ic=lay('COUNTER_TIMBERS',(90,140,200))
for s,sg in (('S',1),('P',-1)):
    for y in Y:
        yc=sg*y; extrude_xz(poly,yc-2.0,yc+2.0,ic,'COUNTER_TIMBER_%s%d'%(s,round(y)))
f.Write('rhino/RoyalCaroline_stern_v2.3dm',7)
json.dump({'angle_deg':ANG,'counter_Y':Y,'poly':poly},open('data/stern_v2_params.json','w'))
print(len(f.Objects),'objects')
