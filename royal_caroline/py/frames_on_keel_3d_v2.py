# frames 1-5 blanks on the keel (deadwood with pockets) and keelson, 3D, for the builder to judge the seat width vs the slope; keel/keelson from build3d_v2 (STEP outlines + 1 mm pockets), clipped to X>=430
import sys,os,json,numpy as np
sys.argv=['x']; sys.path.insert(0,'py')
# --- keel/keelson from the STEP profiles (data/step44_profiles.json; the STEP upload itself is gone): keelson = Boss-Extrude4[4], keel/deadwood = Boss-Extrude2[2]; upper/lower envelopes, our spline for the keelson underside and the keel top with 1 mm pockets (as build3d_v2.py)
import frames_batch_2d as F
from shapely.geometry import Polygon,LineString,box
from scipy.interpolate import UnivariateSpline
os.environ['NOSTEP']='1'
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']
PR=json.load(open('data/step44_profiles.json')); KS=Polygon(max(PR['Boss-Extrude4[4]'],key=lambda q:Polygon(q).area)).buffer(0); KP=Polygon(max(PR['Boss-Extrude2[2]'],key=lambda q:Polygon(q).area)).buffer(0)
def env(pg,x,which):
    l=pg.intersection(LineString([(x,-50),(x,300)])); 
    if l.is_empty: return None
    zs=[c[1] for g in (l.geoms if hasattr(l,'geoms') else [l]) for c in g.coords]; return max(zs) if which=='up' else min(zs)
XJ=526.6; XS=np.arange(45.0,XJ+0.01,0.2)
up=np.array([(x,env(KS,x,'up')) for x in XS if env(KS,x,'up') is not None]); lowk=np.array([(x,env(KP,x,'low')) for x in XS if env(KP,x,'low') is not None])
low=np.c_[XS,sK(np.minimum(XS,XJ+30))]
def surf(x): x=np.asarray(x,float); return np.minimum(kK(x),sK(np.minimum(x,XJ+30))-np.clip((XJ-x)/12.0,0,1)*1.0)
def nrm(x,f,h=0.05): dz=float((f(x+h)-f(x-h))/(2*h)); t=np.array([1.0,dz]); t/=np.hypot(*t); return np.array([-t[1],t[0]])
pk=sorted([(46-n,xx-4,xx+4) for n,xx in enumerate(F.XF,1) if 50<xx<528],key=lambda p:p[1]); pts=[]; x=XS[0]
for b_,a_,bb in pk:
    pts+=[(xx,float(surf(xx))) for xx in np.arange(x,a_,0.2)]
    Pa=np.array([a_,float(surf(a_))]); pts.append(tuple(Pa)); pts.append(tuple(Pa-DEPTH*nrm(a_,surf)))
    for xx in np.arange(a_+0.2,bb,0.2): pts.append(tuple(np.array([xx,float(surf(xx))])-DEPTH*nrm(xx,surf)))
    Pb=np.array([bb,float(surf(bb))]); pts.append(tuple(Pb-DEPTH*nrm(bb,surf))); pts.append(tuple(Pb)); x=bb+0.2
pts+=[(xx,float(surf(xx))) for xx in np.arange(x,XS[-1],0.2)]
keel_top=np.array(pts)
keelson=Polygon(np.vstack([up,low[::-1]])).buffer(0); keel=Polygon(np.vstack([lowk,keel_top[::-1]])).buffer(0); print('keelson area %.0f keel area %.0f valid %s %s'%(keelson.area,keel.area,keelson.is_valid,keel.is_valid))
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
def mesh_of(shape,tol=0.08):
    BRepMesh_IncrementalMesh(shape,tol,False,0.3,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(f.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return np.array(V,float),np.array(T,int)
def prism(poly,y0,y1):
    pts=list(poly.exterior.coords)[:-1]; mk=BRepBuilderAPI_MakePolygon()
    for x,z in pts: mk.Add(gp_Pnt(x,y0,z))
    mk.Close(); fc=BRepBuilderAPI_MakeFace(mk.Wire()).Face(); return BRepPrimAPI_MakePrism(fc,gp_Vec(0,y1-y0,0)).Shape()
parts={}
XC=430.0
import rhino3dm as r3
from shapely.geometry import box
for nm,pg in (('KEELSON',keelson),('KEEL_DEADWOOD',keel)):
    g=pg.intersection(box(XC,-50,545,300)); geoms=g.geoms if hasattr(g,'geoms') else [g]; V=[];T=[]
    for q in geoms:
        if q.geom_type!='Polygon' or q.area<5: continue
        v,t=mesh_of(prism(q,-2.65,2.65)); T.extend((t+len(V)).tolist()); V.extend(v.tolist())
    parts[nm]=dict(v=np.array(V),t=np.array(T)); print(nm,len(V),'verts')
N=r3.File3dm.Read('rhino/RoyalCaroline_frames_1_2_3_4_5_blanks_v1.3dm'); f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
for i,l in enumerate(N.Layers): n=r3.Layer(); n.Name=l.Name; n.Color=l.Color; LI[i]=f.Layers.Add(n)
for o in N.Objects: a=o.Attributes; a.LayerIndex=LI[a.LayerIndex]; f.Objects.Add(o.Geometry,a)
for nm,col in (('KEELSON',(150,110,60,255)),('KEEL_DEADWOOD',(110,80,50,255))):
    l=r3.Layer(); l.Name=nm; l.Color=col; li=f.Layers.Add(l); m=r3.Mesh()
    for v in parts[nm]['v']: m.Vertices.Add(*v)
    for t in parts[nm]['t']: m.Faces.AddFace(*t)
    m.Normals.ComputeNormals(); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=nm; f.Objects.AddMesh(m,a)
B=json.load(open('data/bow_lines_builder_final_v1.json')); l=r3.Layer(); l.Name='RABBET_final'; l.Color=(0,0,0,255); li=f.Layers.Add(l)
a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name='rabbet'; f.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(*p) for p in B['RABBET_final_to_M48']]),a)
f.Write('rhino/RoyalCaroline_frames1-5_on_keel_v1.3dm',7); print('objects',len(f.Objects))
