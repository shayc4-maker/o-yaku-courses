# full assembly: keel group solids (with pockets; lowered 0.6 mm as in frame_arm SHIFT) + all 45 frames (layers A/F common blanks, top cut along the bulwark line, laser marks) as meshes in one 3dm; clash check frames vs keel/keelson
import sys,re,json,numpy as np,time
from shapely.geometry import Polygon
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepCheck import BRepCheck_Analyzer
import rhino3dm as r3
SHIFT=0.6; STEP='rhino/RoyalCaroline_keel_solids_v4.step'
def vol(s): g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
def mesh_of(shape,tol=0.04):
    BRepMesh_IncrementalMesh(shape,tol,False,0.35,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        fc=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(fc,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(fc.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((round(p.X(),3),round(p.Y(),3),round(p.Z(),3)))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return V,T
def add_mesh(f,li,name,shape):
    V,T=mesh_of(shape); m=r3.Mesh()
    for v in V: m.Vertices.Add(*v)
    for t in T: m.Faces.AddFace(*t)
    m.Normals.ComputeNormals(); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=name; f.Objects.AddMesh(m,a); return len(V)
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def layer(n,col): l=r3.Layer(); l.Name=n; l.Color=col; return f.Layers.Add(l)
# keel group
rd=STEPControl_Reader(); rd.ReadFile(STEP); rd.TransferRoots(); sh=rd.OneShape(); names=re.findall(r"PRODUCT\('([^']*)'",open(STEP,errors='ignore').read())[:18]
ex=TopExp_Explorer(sh,TopAbs_SOLID); KEEL={}; i=0
while ex.More():
    s=TopoDS.Solid(ex.Current()); t=gp_Trsf(); t.SetTranslation(gp_Vec(0,0,-SHIFT)); KEEL[names[i]]=BRepBuilderAPI_Transform(s,t,True).Shape(); i+=1; ex.Next()
nv=0
for nm,s in KEEL.items(): nv+=add_mesh(f,layer('KEEL_'+nm,(150,120,80,255)),nm,s)
print('keel group meshes: vertices',nv)
# frames
def prism(poly,x0,x1):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in poly[:-1]: mk.Add(gp_Pnt(x0,y,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(x1-x0,0,0)).Shape()
def slab(x0,x1,z0,z1):
    mk=BRepBuilderAPI_MakePolygon()
    for x,z in ((x0,-5),(x1,-5),(x1,z1),(x0,z0)): mk.Add(gp_Pnt(x,-200,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(0,400,0)).Shape()
lL=layer('LASER_final_faces',(255,0,0,255)); clash=[]; tv=0; t0=time.time()
keelc={k:KEEL[k] for k in ('Boss-Extrude2[2]','Boss-Extrude4[4]')}
for part in ('1_15','16_30','31_45'):
    B=np.load('/tmp/blank3_%s.npy'%part,allow_pickle=True).item()
    for b,D in B.items():
        xc=D['xc']; env=np.array(Polygon(D['env']).simplify(0.03).exterior.coords)
        for lay,(x0,x1),col in (('A',(xc-4,xc),(120,170,230,255)),('F',(xc,xc+4),(230,170,120,255))):
            z0=D['z']['back' if lay=='A' else 'mid']; z1=D['z']['mid' if lay=='A' else 'front']
            sh_=BRepAlgoAPI_Common(prism(env,x0,x1),slab(x0,x1,z0,z1)).Shape()
            for kn,ks in keelc.items():
                bb=BRepAlgoAPI_Common(sh_,ks).Shape(); v=vol(bb) if not bb.IsNull() else 0
                if v>0.5: clash.append((b,lay,kn,round(v,1)))
            tv+=add_mesh(f,layer('FRAME%02d_%s'%(b,lay),col),'FRAME%02d_%s'%(b,lay),sh_)
        for nm,X in (('back',xc-4),('mid',xc),('front',xc+4)):
            P=D['FP'][nm]; pl=r3.PolylineCurve([r3.Point3d(X+(-0.03 if nm=='back' else 0.03 if nm=='front' else 0),y,z) for y,z in np.array(Polygon(P).simplify(0.01).exterior.coords)]); a=r3.ObjectAttributes(); a.LayerIndex=lL; a.Name='LASER%02d_%s'%(b,nm); f.Objects.AddCurve(pl,a)
    print('frames',part,'done, %.0f s'%(time.time()-t0))
print('frame mesh vertices',tv,'; clashes frame layer vs keel/keelson (>0.5 mm3):',clash)
f.Write('rhino/RoyalCaroline_keel_and_frames_assembly_v1.3dm',7)
import os; print('3dm size %.1f MB'%(os.path.getsize('rhino/RoyalCaroline_keel_and_frames_assembly_v1.3dm')/1e6))
