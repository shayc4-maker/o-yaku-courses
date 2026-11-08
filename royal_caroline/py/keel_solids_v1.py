# solids of the 18 keel-group parts from the builder's lines: changed parts from the new closed profiles, unchanged parts from the original STEP faces; 5.3 mm centred (aft rudder bodies 4.0 mm); STEP + 3dm (meshes) for approval
import sys,re,json,pickle,numpy as np; sys.argv=['x']
exec(open('py/step_edges_dump.py').read().split("if __name__")[0])
exec(open('py/keel_parts_v1.py').read().split("rows=[]")[0].replace("print(nn)","pass"))
from shapely.geometry import Polygon
from shapely.validation import make_valid
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopAbs import TopAbs_FACE as TAF
def wire_edges(f):
    out=[]
    we=TopExp_Explorer(f,TopAbs_WIRE)
    while we.More():
        w=TopoDS.Wire(we.Current()); wx=BRepTools_WireExplorer(w); E=[]
        while wx.More():
            e=wx.Current(); c=BRepAdaptor_Curve(e); a=c.Value(c.FirstParameter()); b=c.Value(c.LastParameter())
            if wx.Orientation().name=='TopAbs_REVERSED': a,b=b,a
            E.append(((a.X(),a.Z()),(b.X(),b.Z()))); wx.Next()
        out.append(E); we.Next()
    return out
CHANGED=['Boss-Extrude2[2]','Boss-Extrude2[1]','Boss-Extrude5[1]','Boss-Extrude5[2]','Boss-Extrude6','Boss-Extrude4[4]','Boss-Extrude5[3]','Boss-Extrude3[3]','Split1[1]','Split1[2]','Boss-Extrude4[2]']
AFT={'Split1[1]','Split1[2]','Boss-Extrude4[2]'}
def dd(P):
    out=[P[0]]
    for p in P[1:]:
        if np.hypot(*(p-out[-1]))>1e-6: out.append(p)
    if np.hypot(*(out[0]-out[-1]))<1e-6: out=out[:-1]
    return np.array(out)
def clean(P):
    pg=Polygon(dd(P))
    if not pg.is_valid: pg=make_valid(pg)
    if pg.geom_type!='Polygon': pg=max([g for g in pg.geoms if g.geom_type=='Polygon'],key=lambda g:g.area)
    return pg
def wire_from_ring(R):
    mw=BRepBuilderAPI_MakeWire(); n=len(R)
    for i in range(n):
        a,b=R[i],R[(i+1)%n]
        if np.hypot(*(a-b))<1e-7: continue
        mw.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(a[0],0,a[1]),gp_Pnt(b[0],0,b[1])).Edge())
    return mw.Wire()
def vol(s): g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
SOLID={}; rep=[]
for nm,(s,f) in SOL.items():
    th,y0=(4.0,-2.0) if nm in AFT else (5.3,-2.65)
    if nm in CHANGED:
        pg=clean(newP[nm])
        from shapely.geometry.polygon import orient
        if nm=='Boss-Extrude5[2]':
            W=wire_edges(f); rings=[np.array([p[0] for p in w]) for w in W]; ars=[Polygon(r).buffer(0).area for r in rings]; holes=[r for r,a in zip(rings,ars) if a<max(ars)]
            pg=orient(Polygon(pg.exterior.coords,holes=[h for h in holes]),1.0)
        else: pg=orient(pg,1.0)
        face=BRepBuilderAPI_MakeFace(wire_from_ring(np.array(pg.exterior.coords)[:-1])).Face()
        HOLES=[np.array(h.coords)[:-1] for h in pg.interiors]
        rep.append((nm,'new profile',pg.is_valid,round(pg.area,1),round(Polygon(old[nm]).buffer(0).area,1)))
    else: face=f; rep.append((nm,'original face',True,None,None))
    t=gp_Trsf(); t.SetTranslation(gp_Vec(0,y0,0)); f2=BRepBuilderAPI_Transform(face,t,True).Shape(); sol=BRepPrimAPI_MakePrism(f2,gp_Vec(0,th,0)).Shape()
    if nm in CHANGED and nm=='Boss-Extrude5[2]':
        from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
        for Hh in HOLES:
            hf=BRepBuilderAPI_MakeFace(wire_from_ring(Hh)).Face(); t2=gp_Trsf(); t2.SetTranslation(gp_Vec(0,y0-1,0)); hf=BRepBuilderAPI_Transform(hf,t2,True).Shape(); sol=BRepAlgoAPI_Cut(sol,BRepPrimAPI_MakePrism(hf,gp_Vec(0,th+2,0)).Shape()).Shape()
    ok=BRepCheck_Analyzer(sol).IsValid(); v=vol(sol); SOLID[nm]=(sol,ok,v,th); print('%-18s %-13s valid %s  thickness %.1f  volume %8.0f mm3'%(nm,rep[-1][1],ok,th,v))
# overlaps between the solids
pairs=[]; names=list(SOLID)
for i in range(len(names)):
    for j in range(i+1,len(names)):
        c=BRepAlgoAPI_Common(SOLID[names[i]][0],SOLID[names[j]][0]).Shape(); v=vol(c) if not c.IsNull() else 0
        if v>0.5: pairs.append((names[i],names[j],round(v,1)))
print('overlapping pairs (mm3):',pairs)
pickle.dump({n:(ok,v,th) for n,(s,ok,v,th) in SOLID.items()},open('/tmp/solids_info.pkl','wb'))
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TCollection import TCollection_ExtendedString
from OCP.TDataStd import TDataStd_Name
app=XCAFApp_Application.GetApplication_s(); doc=TDocStd_Document(TCollection_ExtendedString('MDTV-XCAF')); app.InitDocument(doc); st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
for nm,(sol,ok,v,th) in SOLID.items(): lab=st.AddShape(sol,False); TDataStd_Name.Set_s(lab,TCollection_ExtendedString(nm))
w=STEPCAFControl_Writer(); w.Transfer(doc); w.Write('rhino/RoyalCaroline_keel_solids_v2.step')
# 3dm (meshes) for viewing
import rhino3dm as r3
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
def mesh_of(shape,tol=0.03):
    BRepMesh_IncrementalMesh(shape,tol,False,0.3,True); V=[];T=[]; ex=TopExp_Explorer(shape,TAF)
    while ex.More():
        fc=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(fc,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(fc.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return V,T
f3=r3.File3dm(); f3.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; cols=plt_cols=None
for nm,(sol,ok,v,th) in SOLID.items():
    l=r3.Layer(); l.Name=nm+(' (NEW)' if nm in CHANGED else ''); l.Color=(220,120,40,255) if nm in CHANGED else (150,150,150,255); li=f3.Layers.Add(l)
    V,T=mesh_of(sol); m=r3.Mesh()
    for p in V: m.Vertices.Add(*p)
    for t in T: m.Faces.AddFace(*t)
    m.Normals.ComputeNormals(); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=nm; f3.Objects.AddMesh(m,a)
f3.Write('rhino/RoyalCaroline_keel_solids_v2_meshes.3dm',7); print('written')
