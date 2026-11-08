import sys,re,json,numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE,TopAbs_WIRE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Plane
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepTools import BRepTools_WireExplorer
P='rhino/backbone_builder_44.STEP'
r=STEPControl_Reader(); r.ReadFile(P); r.TransferRoots(); sh=r.OneShape()
names=re.findall(r"MANIFOLD_SOLID_BREP \( '([^']*)'",open(P,errors='ignore').read())
ex=TopExp_Explorer(sh,TopAbs_SOLID); i=0; SOL={}
while ex.More():
    s=TopoDS.Solid(ex.Current()); fe=TopExp_Explorer(s,TopAbs_FACE); best=None
    while fe.More():
        f=TopoDS.Face(fe.Current()); ad=BRepAdaptor_Surface(f)
        if ad.GetType()==GeomAbs_Plane:
            pl=ad.Plane(); n=pl.Axis().Direction(); o=pl.Location()
            if abs(abs(n.Y())-1)<1e-6 and abs(o.Y())<1e-6:
                g=GProp_GProps(); BRepGProp.SurfaceProperties_s(f,g)
                if best is None or g.Mass()>best[0]: best=(g.Mass(),f)
        fe.Next()
    SOL[names[i]]=(s,best[1] if best else None); i+=1; ex.Next()
if __name__=='__main__':
    for nm,(s,f) in SOL.items():
        if f is None: print(nm,'no Y=0 face'); continue
        we=TopExp_Explorer(f,TopAbs_WIRE); w=TopoDS.Wire(we.Current()); wx=BRepTools_WireExplorer(w); rows=[]
        while wx.More():
            e=wx.Current(); c=BRepAdaptor_Curve(e); a=c.Value(c.FirstParameter()); b=c.Value(c.LastParameter()); rows.append((str(c.GetType()).split('.')[-1],round(a.X(),1),round(a.Z(),1),round(b.X(),1),round(b.Z(),1))); wx.Next()
        from collections import Counter
        print(nm,'edges',len(rows),Counter(r[0] for r in rows))
