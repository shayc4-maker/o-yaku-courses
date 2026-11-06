import sys,numpy as np
sys.path.insert(0,'py')
import hull_new_sections as HN
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.gp import gp_Pnt
exec(open('py/build3d_parts.py').read().split("parts={}")[0].split("D=json.load")[0].replace("FR=[int(a) for a in sys.argv[1:]] or list(range(1,13))","").replace("sys.argv=[sys.argv[0]]","")) if False else None
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
def mesh_of(shape,tol=0.15):
    BRepMesh_IncrementalMesh(shape,tol,False,0.4,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(f.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return np.array(V,float),np.array(T,int)
HN.SURF=HN.build()
x0,x1=float(sys.argv[1]),float(sys.argv[2])
box=BRepPrimAPI_MakeBox(gp_Pnt(x0,0,-20),gp_Pnt(x1,90,160)).Shape(); com=BRepAlgoAPI_Common(HN.SURF,box); com.Build(); sh=com.Shape()
V,T=mesh_of(sh); print('hull patch',len(V),len(T),'Y %.1f..%.1f Z %.1f..%.1f'%(V[:,1].min(),V[:,1].max(),V[:,2].min(),V[:,2].max()))
np.save('/tmp/claude-0/x/hull_patch.npy',dict(v=V,t=T),allow_pickle=True)
