# Assembly v2: frames 1-45 + bow HT + builder backbone (5.3 mm, notched by transoms 1-3) + rudder + stern v5 (six tapered counter timbers, transoms 1-3)
import json,numpy as np,rhino3dm as r3
from shapely.geometry import Polygon
from shapely.ops import unary_union
src=r3.File3dm.Read('rhino/RoyalCaroline_assembly_v1.3dm'); v5=r3.File3dm.Read('rhino/RoyalCaroline_stern_v5_meshes.3dm')
BB=json.load(open('data/step44_profiles.json')); TH=5.3
T1=[(-9.2,75.8),(-4.9,75.7),(-3.4,71.8),(-7.9,71.9)]; T2=[(-6.0,65.5),(0.4,65.4),(3.2,61.5),(-4.8,61.7)]; T3=[(-3.5,57.3),(6.8,57.6),(11.0,53.3),(-2.45,53.4)]
TR=unary_union([Polygon(T1),Polygon(T2),Polygon(T3)])
drop={'COUNTER_TIMBERS','WING_TRANSOM','WING_TRANSOM_MARKS','TRANSOM_2_1','TRANSOM_2_2','TRANSOM_3_1','TRANSOM_3_2','STERNPOST_notched','BACKBONE_builder','RUDDER_builder'}
out=r3.File3dm(); out.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; L={}
def lay(n,col=(150,150,150,255)):
    if n not in L:
        l=r3.Layer(); l.Name=n; l.Color=col; L[n]=out.Layers.Add(l)
    return L[n]
n_kept=0
for o in src.Objects:
    lyr=src.Layers[o.Attributes.LayerIndex]
    if lyr.Name in drop: continue
    at=r3.ObjectAttributes(); at.LayerIndex=lay(lyr.Name,lyr.Color); at.Name=o.Attributes.Name; g=o.Geometry
    if isinstance(g,r3.Brep): out.Objects.AddBrep(g,at)
    elif isinstance(g,r3.Extrusion): out.Objects.AddBrep(g.ToBrep(True),at)
    elif isinstance(g,r3.Curve): out.Objects.AddCurve(g,at)
    elif isinstance(g,r3.Mesh): out.Objects.AddMesh(g,at)
    else:
        try: out.Objects.AddTextDot(g.Text,g.Point,at)
        except Exception: continue
    n_kept+=1
def ext_xz(poly,y0,y1,layer,name):
    pl=r3.Polyline(len(poly)+1)
    for x,z in poly: pl.Add(x,y0,z)
    pl.Add(poly[0][0],y0,poly[0][1]); ex=r3.Extrusion.Create(pl.ToPolylineCurve(),y1-y0,True); br=ex.ToBrep(True)
    v=np.array([br.Vertices[i].Location.Y for i in range(len(br.Vertices))]); br.Translate(r3.Vector3d(0,y0-v.min(),0))
    assert br.IsSolid and br.IsValid,name
    at=r3.ObjectAttributes(); at.LayerIndex=layer; at.Name=name; out.Objects.AddBrep(br,at)
ib=lay('BACKBONE_builder'); ir=lay('RUDDER_builder',(180,120,200,255)); notched=[]
for k,rg in BB.items():
    pg=Polygon(max(rg,key=lambda p:Polygon(p).area)).buffer(0).simplify(0.002)
    if k in('Split1[1]','Split1[2]','Boss-Extrude4[2]'): ext_xz(list(pg.exterior.coords)[:-1],-2,2,ir,k); continue
    d=pg.difference(TR)
    if d.area<pg.area-0.01: notched.append((k,round(pg.area-d.area,1)))
    if d.geom_type!='Polygon': d=max(d.geoms,key=lambda g:g.area)
    ext_xz(list(d.exterior.coords)[:-1],-TH/2,TH/2,ib,k)
print('backbone parts notched by transoms (area removed mm2):',notched)
for o in v5.Objects:
    n=v5.Layers[o.Attributes.LayerIndex].Name; at=r3.ObjectAttributes(); at.LayerIndex=lay(n,(90,140,200,255)); at.Name=n; out.Objects.AddMesh(o.Geometry,at)
out.Write('rhino/RoyalCaroline_assembly_v2.3dm',7); print(len(out.Objects),'objects,',len(out.Layers),'layers; kept',n_kept)
