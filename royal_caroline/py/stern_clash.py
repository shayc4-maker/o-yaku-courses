import json,numpy as np
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from shapely.geometry import Polygon
TH=5.3
def prism(pts3,vec):
    mp=BRepBuilderAPI_MakePolygon()
    for p in pts3: mp.Add(gp_Pnt(*p))
    mp.Close(); f=BRepBuilderAPI_MakeFace(mp.Wire()).Face()
    return BRepPrimAPI_MakePrism(f,gp_Vec(*vec)).Shape()
def clean(poly):
    pg=Polygon(poly).buffer(0).simplify(0.01)
    if pg.geom_type!='Polygon': pg=max(pg.geoms,key=lambda g:g.area)
    return list(pg.exterior.coords)[:-1]
def part(p):
    c=clean(p['poly']); o=p['off']; t=p['th']
    if p['plane']=='XZ': return prism([(x,o-t/2,z) for x,z in c],(0,t,0))
    if p['plane']=='XY': return prism([(x,y,o) for x,y in c],(0,0,t))
    if p['plane']=='YZ': return prism([(o,y,z) for y,z in c],(t,0,0))
def vol(s): g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
if __name__=='__main__':
    pv=json.load(open('data/parts_v10.json')); BB=json.load(open('data/step44_profiles.json'))
    bb={k:prism([(x,-TH/2,z) for x,z in clean(max(r,key=lambda p:Polygon(p).area))],(0,TH,0)) for k,r in BB.items()}
    st=[p for p in pv if p['group'] in('stern','rudder')]
    rows=[]
    for p in st:
        s=part(p)
        for k,b in bb.items():
            if k in('Split1[1]','Split1[2]','Boss-Extrude4[2]') and p['name']=='RUDDER': continue
            v=vol(BRepAlgoAPI_Common(s,b).Shape())
            if v>0.05: rows.append((p['name'],k,round(v,2)))
    for r in rows: print(r)
    json.dump(rows,open('data/stern_clash_v1.json','w'))
