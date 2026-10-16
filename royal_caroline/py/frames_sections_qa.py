import sys,io,contextlib,numpy as np
mod=sys.argv[1]; out=sys.argv[2]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); M=__import__(mod)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
def tris(sh):
    BRepMesh_IncrementalMesh(sh,0.05); o=[]; ex=TopExp_Explorer(sh,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face(ex.Current()); lc=TopLoc_Location(); t=BRep_Tool.Triangulation_s(f,lc)
        if t is not None:
            P=[(t.Node(i).Transformed(lc.Transformation()).Y(),t.Node(i).Transformed(lc.Transformation()).Z()) for i in range(1,t.NbNodes()+1)]
            for i in range(1,t.NbTriangles()+1): a,b,c=t.Triangle(i).Get(); o.append([P[a-1],P[b-1],P[c-1]])
        ex.Next()
    return o
fig,ax=plt.subplots(1,3,figsize=(21,8))
for a,(fn,x) in zip(ax,((46,26.0),(47,15.0),(48,4.0))):
    for nm in ('S','P'):
        sl=BRepAlgoAPI_Common(M.frames[f'FRAME{fn}_A_{nm}'],BRepPrimAPI_MakeBox(gp_Pnt(x-0.1,-100,0),gp_Pnt(x+0.1,100,200)).Shape()).Shape()
        for t in tris(sl): a.fill([p[0] for p in t],[p[1] for p in t],color='tab:blue',alpha=.6,lw=0)
    ztop,zks=M.bbz(x); a.fill_between([-2.65,2.65],-10,ztop,color='#999'); a.fill_between([-2.65,2.65],zks,zks+6,color='#999')
    a.set_xlim(-45,45); a.set_ylim(0,90); a.set_aspect('equal'); a.set_title(f'F{fn} aft layer, section X={x} (grey = backbone)')
plt.savefig(out,dpi=60)
