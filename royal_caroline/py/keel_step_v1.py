# keel + backbone thinned 1 mm per side (half-width 2.65 -> 1.65) from the rabbet line upward; frames keep their outer lines, the removed material is added at their inner base. Rudder parts (Y +-2.0) untouched.
import re,json,numpy as np
from shapely.geometry import Polygon,box
from scipy.interpolate import UnivariateSpline
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepCheck import BRepCheck_Analyzer
import rhino3dm as r3
SHIFT=0.6; HW=1.65; KB0=2.65
vol=lambda s:(lambda g:(BRepGProp.VolumeProperties_s(s,g),g.Mass())[1])(GProp_GProps())
def mesh_of(shape,tol=0.04):
    BRepMesh_IncrementalMesh(shape,tol,False,0.35,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        fc=(TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,"Face_s") else TopoDS.Face(ex.Current())); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(fc,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(fc.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((round(p.X(),3),round(p.Y(),3),round(p.Z(),3)))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return V,T
# rabbet chain (builder lines): aft = lower ends of F46-48 (his arranged lines), then approved rabbet, then stem rabbet points
T=json.load(open('data/aft_frames_tops_v1.json')); aft=sorted([(v['X'],v['pts'][0][1]) for k,v in T.items()],key=lambda a:a[0])
mid=json.load(open('data/rabbet_points_v3_ends.json')); mid=mid['points'] if 'points' in mid else mid
stem=[(p['X'],p['Z']) for p in json.load(open('data/rabbet_stem_points_v3.json'))]
chain=aft+[tuple(p[:2]) for p in mid]+stem
poly=Polygon(chain+[(chain[-1][0]+30,220),(-45,220),(-45,chain[0][1])]).buffer(0); print('cut region area %.0f valid %s'%(poly.area,poly.is_valid))
def prismY(pl,y0,y1):
    mk=BRepBuilderAPI_MakePolygon()
    for x,z in list(pl.exterior.coords)[:-1]: mk.Add(gp_Pnt(x,y0,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(0,y1-y0,0)).Shape()
cutters=[prismY(poly,HW,3.2),prismY(poly,-3.2,-HW)]
rd=STEPControl_Reader(); rd.ReadFile('rhino/RoyalCaroline_keel_solids_v4.step'); rd.TransferRoots(); ex=TopExp_Explorer(rd.OneShape(),TopAbs_SOLID); S=[]
while ex.More(): S.append(TopoDS.Solid(ex.Current())); ex.Next()
kn=re.findall(r"PRODUCT\('([^']*)'",open('rhino/RoyalCaroline_keel_solids_v4.step',errors='ignore').read())[:18]
RUD=('Split1[2]','Boss-Extrude4[2]','Split1[1]'); KEEL={}; REMOVED=[]
for n,s in zip(kn,S):
    t=gp_Trsf(); t.SetTranslation(gp_Vec(0,0,-SHIFT)); s=BRepBuilderAPI_Transform(s,t,True).Shape()
    if n not in RUD:
        v0=vol(s); rem=None
        for c in cutters:
            ct=BRepAlgoAPI_Common(s,c).Shape(); s=BRepAlgoAPI_Cut(s,c).Shape(); rem=ct if rem is None else rem
            if vol(ct)>1e-6: REMOVED.append(ct)
        print('%-18s volume %.0f -> %.0f mm3 (removed %.0f) valid %s'%(n,v0,vol(s),v0-vol(s),BRepCheck_Analyzer(s).IsValid()))
    KEEL[n]=s
V2=json.load(open('data/keel_keelson_v3.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0)
XF=json.load(open('data/frames_X.json'))['X_mm']; frames={b:XF[45-b] for b in range(1,46)}; frames.update({46:28.0,47:17.0,48:6.0})
def slab(x0,x1):
    mk=BRepBuilderAPI_MakePolygon()
    for x,z in ((x0,-20),(x1,-20),(x1,float(sK(min(x1,526.0)))-SHIFT),(x0,float(sK(min(x0,526.0)))-SHIFT)): mk.Add(gp_Pnt(x,-6,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(0,12,0)).Shape()
ADD={}
for b,xc in frames.items():
    for lay,(x0,x1) in (('A',(xc-4,xc)),('F',(xc,xc+4))):
        sl=slab(x0,x1); parts=[BRepAlgoAPI_Common(R,sl).Shape() for R in REMOVED]; parts=[p for p in parts if not p.IsNull() and vol(p)>1e-4]
        if parts: ADD['FRAME%02d_%s_added_inner_base'%(b,lay)]=parts
print('frame add-on pieces',len(ADD),'total vol %.1f'%sum(vol(p) for v in ADD.values() for p in v))
import pickle
f=r3.File3dm.Read('rhino/RoyalCaroline_keel_frames_1_51_stern_assembly_v7.3dm')
keep=[i for i,l in enumerate(f.Layers) if not l.Name.startswith('KEEL_')]; g=r3.File3dm(); g.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; M={}
for i in keep: l=f.Layers[i]; n=r3.Layer(); n.Name=l.Name; n.Color=l.Color; M[i]=g.Layers.Add(n)
for o in f.Objects:
    if o.Attributes.LayerIndex in M: a=o.Attributes; a.LayerIndex=M[a.LayerIndex]; g.Objects.Add(o.Geometry,a)
def add(layer,name,col,shape):
    V,Tr=mesh_of(shape); m=r3.Mesh()
    for v in V: m.Vertices.Add(*v)
    for t in Tr: m.Faces.AddFace(*t)
    m.Normals.ComputeNormals(); l=r3.Layer(); l.Name=layer; l.Color=col; li=g.Layers.Add(l); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=name; g.Objects.AddMesh(m,a)
for n,s in KEEL.items(): add('KEEL_'+n,n,(150,120,80,255),s)
for n,ps in ADD.items():
    for k,p in enumerate(ps): add(n,n+'_%d'%k,(80,200,80,255),p)
g.Write('rhino/RoyalCaroline_keel_step_assembly_v8.3dm',7); print('written',len(g.Objects))
