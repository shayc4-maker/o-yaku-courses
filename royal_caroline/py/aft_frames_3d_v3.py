# 3D blanks of ONE frame (layers A: X-4..X, F: X..X+4, common blank prism) + laser lines (3 final faces) -> 3dm (meshes+curves) and STEP
import sys,json,numpy as np
B=np.load(sys.argv[1] if len(sys.argv)>1 else '/tmp/blank_batch.npy',allow_pickle=True).item()
import rhino3dm as r3
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
def prism(poly,x0,x1):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in poly[:-1]: mk.Add(gp_Pnt(x0,y,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(x1-x0,0,0)).Shape()
def mesh_of(shape,tol=0.05):
    BRepMesh_IncrementalMesh(shape,tol,False,0.3,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(f.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,bb,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else bb)-1,base+(bb if rev else c)-1))
        ex.Next()
    return V,T
def slab(x0,x1,z0,z1):
    mk=BRepBuilderAPI_MakePolygon()
    for x,z in ((x0,-5),(x1,-5),(x1,z1),(x0,z0)): mk.Add(gp_Pnt(x,-200,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(0,400,0)).Shape()
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
TR=json.load(open('data/stern_transom_outline_v2.json'))['transoms_normalized']; HW={'T2':37.8,'T3':12.7}
def notch(sh,b):
    if str(b)!='48': return sh
    for k,hw in HW.items():
        mk=BRepBuilderAPI_MakePolygon()
        for x,z in TR[k]['poly']: mk.Add(gp_Pnt(x,-hw,z))
        mk.Close(); pr=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(0,2*hw,0)).Shape(); sh=BRepAlgoAPI_Cut(sh,pr).Shape()
    return sh
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def layer(n,col): l=r3.Layer(); l.Name=n; l.Color=col; return f.Layers.Add(l)
comp=TopoDS_Compound(); bb_=BRep_Builder(); bb_.MakeCompound(comp); lL=layer('LASER_final_faces',(255,0,0,255))
for b,D in B.items():
    xc=D['xc']; env=D['env']
    for lay,(x0,x1),col in (('A',(xc-4,xc),(120,170,230,255)),('F',(xc,xc+4),(230,170,120,255))):
        z0=D['z']['back' if lay=='A' else 'mid']; z1=D['z']['mid' if lay=='A' else 'front']
        sh=BRepAlgoAPI_Common(prism(env,x0,x1),slab(x0,x1,z0,z1)).Shape(); sh=notch(sh,b);  ok=BRepCheck_Analyzer(sh).IsValid(); gp=GProp_GProps(); BRepGProp.VolumeProperties_s(sh,gp); print('aft frame',b,lay,'valid',ok,'volume %.0f mm3'%gp.Mass(),'top Z %.2f -> %.2f'%(z0,z1))
        bb_.Add(comp,sh); V,T=mesh_of(sh); m=r3.Mesh()
        for v in V: m.Vertices.Add(*v)
        for t in T: m.Faces.AddFace(*t)
        m.Normals.ComputeNormals(); a=r3.ObjectAttributes(); a.LayerIndex=layer('FRAME%s_%s_blank'%(b,lay),col); a.Name='FRAME%s_%s'%(b,lay); f.Objects.AddMesh(m,a)
    for nm,X in (('back',xc-4),('mid',xc),('front',xc+4)):
        P=D['FP'][nm]; pl=r3.PolylineCurve([r3.Point3d(X+(-0.03 if nm=='back' else 0.03 if nm=='front' else 0),y,z) for y,z in P]); a=r3.ObjectAttributes(); a.LayerIndex=lL; a.Name='LASER%s_%s'%(b,nm); f.Objects.AddCurve(pl,a)
name='frames_%s'%('_'.join(map(str,B.keys())))
f.Write('rhino/RoyalCaroline_aft_frames_whole46_48_v3_only.3dm',7); print('3dm',len(f.Objects))
