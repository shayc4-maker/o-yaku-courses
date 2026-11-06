# 5 frames BEFORE sanding: each layer = flat-cut blank (straight prism, 4 mm) covering both faces, flat horizontal seat/tab lines at the keel and keelson, laser marks = the final (sanded) face outlines drawn on the two faces
import sys,json,os,numpy as np
FR=[int(a) for a in sys.argv[1:]] or [1,2,3,4,5]; sys.argv=[sys.argv[0]]
os.environ['NOSTEP']='1'; os.environ['INNER_SMOOTH']='1'
sys.path.insert(0,'py')
import frames_batch_2d as F
from scipy.interpolate import UnivariateSpline
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0)
DEPTH=V2['depth']; XLIM=526.0; F.NOSTEP=True; F.PEN_LOW=DEPTH; KT0=F.keel_levels
F.keel_levels=lambda X:(lambda X:(float(kK(X)),(float(sK(X)),KT0(X)[1][1])))(min(X,XLIM))
def mesh_of(shape,tol=0.05):
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
def prism_x(poly,x0,x1):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in list(poly.exterior.coords)[:-1]: mk.Add(gp_Pnt(x0,y,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(x1-x0,0,0)).Shape()
def full(half):
    g=unary_union([half.buffer(0.01),F.mirror(half).buffer(0.01)]).buffer(-0.01)
    return max(g.geoms,key=lambda q:q.area) if hasattr(g,'geoms') else g
parts=np.load('/tmp/claude-0/x/parts3d.npy',allow_pickle=True).item(); out={k:v for k,v in parts.items() if not k.startswith('FRAME')}
lines=[]
for b in FR:
    xc=F.XF[46-b-1]; fm,im=F.face_poly(xc-4,xc-4); fc,ic=F.face_poly(xc,xc); fp,ip=F.face_poly(xc+4,xc+4)
    env=unary_union([fm.buffer(0.01),fc.buffer(0.01),fp.buffer(0.01)]).buffer(-0.01)      # ONE common cut outline for A and F: inner minimum .. outer maximum over the three faces
    floor=min(im['leg_bot'],ic['leg_bot'],ip['leg_bot']); seat=max(im['ks_bot'],ic['ks_bot'],ip['ks_bot']); env=unary_union([env,box(0,floor,F.KB,seat)])
    blank=full(env)
    for lay,(x0,x1) in (('A',(xc-4,xc)),('F',(xc,xc+4))):
        v,t=mesh_of(prism_x(blank,x0,x1)); out['FRAME%02d_%s'%(b,lay)]=dict(v=v,t=t)
    for X,hp,nm in ((xc-4,fm,'back'),(xc+4,fp,'front')):
        r=np.array(full(hp).exterior.coords); sg=-1 if nm=='back' else 1; lines.append(dict(name='LASER%02d_%s'%(b,nm),pts=np.c_[np.full(len(r),X+sg*0.03),r[:,0],r[:,1]].round(3).tolist()))
    lm=full(fc); r=np.array(lm.exterior.coords); lines.append(dict(name='LASER%02d_mid'%b,pts=np.c_[np.full(len(r),xc),r[:,0],r[:,1]].round(3).tolist()))
    print('frame',b,'common blank area %.0f mm2 (final faces %.0f / %.0f / %.0f); floor %.2f; seats %.2f / %.2f / %.2f'%(blank.area,full(fm).area,full(fc).area,full(fp).area,floor,im['ks_bot'],ic['ks_bot'],ip['ks_bot']))
np.save('/tmp/claude-0/x/parts_blanks.npy',dict(parts=out,lines=lines),allow_pickle=True)
