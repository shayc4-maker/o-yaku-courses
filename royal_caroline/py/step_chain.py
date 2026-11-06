import numpy as np
from collections import defaultdict
from OCP.STEPControl import STEPControl_Reader
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE,TopAbs_EDGE,TopAbs_VERTEX
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.BRep import BRep_Tool
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
F=TopoDS.Face_s if hasattr(TopoDS,'Face_s') else TopoDS.Face; E=TopoDS.Edge_s if hasattr(TopoDS,'Edge_s') else TopoDS.Edge; V=TopoDS.Vertex_s if hasattr(TopoDS,'Vertex_s') else TopoDS.Vertex
def load():
    r=STEPControl_Reader(); r.ReadFile('/root/.claude/uploads/9b1663d1-123c-5304-bded-1182034acdbc/37a9e47e-44.STEP'); r.TransferRoots(); return r.OneShape()
def solids(sh):
    ex=TopExp_Explorer(sh,TopAbs_SOLID); out=[]
    while ex.More(): out.append(ex.Current()); ex.Next()
    return out
def side_chain(s):
    fe=TopExp_Explorer(s,TopAbs_FACE); best=None
    while fe.More():
        f=F(fe.Current()); a=BRepAdaptor_Surface(f); n=a.Plane().Axis().Direction(); g=GProp_GProps(); BRepGProp.SurfaceProperties_s(f,g)
        if abs(n.Y())>0.99 and (best is None or a.Plane().Location().Y()<best[1] or (abs(a.Plane().Location().Y()-best[1])<1e-6 and g.Mass()>best[2])): best=(f,a.Plane().Location().Y(),g.Mass())
        fe.Next()
    f=best[0]; ee=TopExp_Explorer(f,TopAbs_EDGE); segs=[]
    while ee.More():
        e=E(ee.Current()); va=TopExp_Explorer(e,TopAbs_VERTEX); p=[]
        while va.More(): q=BRep_Tool.Pnt_s(V(va.Current())); p.append((round(q.X(),3),round(q.Z(),3))); va.Next()
        segs.append(p[:2]); ee.Next()
    adj=defaultdict(list)
    for a,b in segs: adj[a].append(b); adj[b].append(a)
    start=min(adj,key=lambda p:p[0]); chain=[start]; prev=None; cur=start
    while True:
        nxt=[q for q in adj[cur] if q!=prev]
        if not nxt or (len(chain)>1 and nxt[0]==start): break
        prev,cur=cur,nxt[0]; chain.append(cur)
        if len(chain)>len(adj)+2: break
    return np.array(chain),best[1]
