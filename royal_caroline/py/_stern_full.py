# Stern assembly v8: backbone aft part (builder profiles, 5.3 mm sided, X<=80) + rudder + six counter timbers + transoms (cut to F48, tenons) + frames 46-48 (v5)
import json,sys,io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import stern_frames_v10 as F
from shapely.geometry import Polygon
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakePolygon
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
BB=json.load(open('data/step44_profiles.json')); TH=5.3; XMAX=700.0
def xz_prism(poly,y0,y1):
    mp=BRepBuilderAPI_MakePolygon()
    for x,z in poly: mp.Add(gp_Pnt(x,y0,z))
    mp.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mp.Wire()).Face(),gp_Vec(0,y1-y0,0)).Shape()
clip=BRepPrimAPI_MakeBox(gp_Pnt(-100,-100,-50),gp_Pnt(XMAX,100,250)).Shape()
parts={}; rud=('Split1[1]','Split1[2]','Boss-Extrude4[2]')
for k,rg in BB.items():
    pg=Polygon(max(rg,key=lambda p:Polygon(p).area)).buffer(0).simplify(0.002)
    if pg.bounds[0]>XMAX: continue
    y=(-2.0,2.0) if k in rud else (-TH/2,TH/2)
    s=BRepAlgoAPI_Common(xz_prism(list(pg.exterior.coords)[:-1],*y),clip).Shape()
    parts[('RUDDER_' if k in rud else 'BACKBONE_')+k]=s
trs=[k for k in F.allp if k.startswith(('TRANSOM','WING','FRAME'))]
notch={}
for k,s in list(parts.items()):
    for t in trs:
        v=F.S.vol(BRepAlgoAPI_Common(s,F.allp[t]).Shape())
        if v>0.05: notch[(k,t)]=round(v,1); s=BRepAlgoAPI_Cut(s,F.allp[t]).Shape()
    parts[k]=s
print('backbone cut by transoms/frames (mm3):',notch)
allp={**parts,**F.allp}
bad=[n for n,s in allp.items() if not BRepCheck_Analyzer(s).IsValid()]
cl=[]; names=list(allp)
for i,a in enumerate(names):
    for b in names[i+1:]:
        if a.startswith(('BACKBONE','RUDDER')) and b.startswith(('BACKBONE','RUDDER')): continue
        if a.startswith('COUNTER') and b.startswith('COUNTER'): continue
        v=F.S.vol(BRepAlgoAPI_Common(allp[a],allp[b]).Shape())
        if v>0.05: cl.append((a,b,round(v,2)))
print('invalid',bad,'clashes',cl)
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
comp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(comp)
for s in allp.values(): bb.Add(comp,s)
w=STEPControl_Writer(); w.Transfer(comp,STEPControl_AsIs); w.Write('rhino/RoyalCaroline__stern_full.step')
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
import rhino3dm as r3
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
col=lambda n:(200,170,110,255) if n.startswith('BACK') else (180,120,200,255) if n.startswith('RUD') else (90,140,200,255) if n.startswith('FRAME') else (200,120,70,255)
for n,s in allp.items():
    BRepMesh_IncrementalMesh(s,0.05,False,0.3,True)
    l=r3.Layer(); l.Name=n; l.Color=col(n); idx=f.Layers.Add(l); m=r3.Mesh(); off=0
    ex=TopExp_Explorer(s,TopAbs_FACE)
    while ex.More():
        face=TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(face,loc)
        if tri is not None:
            tr_=loc.Transformation()
            for i in range(1,tri.NbNodes()+1):
                p=tri.Node(i).Transformed(tr_); m.Vertices.Add(p.X(),p.Y(),p.Z())
            rev=face.Orientation()==TopAbs_REVERSED
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); m.Faces.AddFace(off+a-1,off+(c if rev else b)-1,off+(b if rev else c)-1)
            off+=tri.NbNodes()
        ex.Next()
    m.Normals.ComputeNormals(); m.Compact(); at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=n; f.Objects.AddMesh(m,at)
f.Write('rhino/RoyalCaroline__stern_full.3dm',7); print('3dm',len(f.Objects))
