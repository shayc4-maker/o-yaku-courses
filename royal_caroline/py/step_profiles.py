import sys,re,json,numpy as np
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE,TopAbs_WIRE,TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Plane
from OCP.BRepTools import BRepTools
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
r=STEPControl_Reader(); r.ReadFile(sys.argv[1]); r.TransferRoots(); sh=r.OneShape()
names=re.findall(r"MANIFOLD_SOLID_BREP \( '([^']*)'",open(sys.argv[1],errors='ignore').read())
ex=TopExp_Explorer(sh,TopAbs_SOLID); out={}; i=0
while ex.More():
    s=TopoDS.Solid(ex.Current()); fe=TopExp_Explorer(s,TopAbs_FACE); best=None
    while fe.More():
        f=TopoDS.Face(fe.Current()); ad=BRepAdaptor_Surface(f)
        if ad.GetType()==GeomAbs_Plane:
            pl=ad.Plane(); n=pl.Axis().Direction(); o=pl.Location()
            if abs(abs(n.Y())-1)<1e-6 and abs(o.Y())<1e-6:
                g=GProp_GProps(); BRepGProp.SurfaceProperties_s(f,g); 
                if best is None or g.Mass()>best[0]: best=(g.Mass(),f)
        fe.Next()
    f=best[1]; rings=[]
    we=TopExp_Explorer(f,TopAbs_WIRE)
    while we.More():
        w=TopoDS.Wire(we.Current()); pts=[]
        ee=TopExp_Explorer(w,TopAbs_EDGE)
        from OCP.BRepTools import BRepTools_WireExplorer
        wx=BRepTools_WireExplorer(w)
        while wx.More():
            e=wx.Current(); c=BRepAdaptor_Curve(e); d=GCPnts_QuasiUniformDeflection(c,0.01,c.FirstParameter(),c.LastParameter())
            ps=[(c.Value(d.Parameter(k)).X(),c.Value(d.Parameter(k)).Z()) for k in range(1,d.NbPoints()+1)]
            if wx.Orientation().name=='TopAbs_REVERSED': ps=ps[::-1]
            pts+=ps; wx.Next()
        rings.append(pts); we.Next()
    out[names[i] if i<len(names) else str(i)]=rings; i+=1; ex.Next()
json.dump(out,open(sys.argv[2],'w'))
cols=matplotlib.colormaps['tab20'].colors
rng=[(-35,215,-12,140),(205,420,-12,25),(410,625,-12,140)]
fig,axs=plt.subplots(3,1,figsize=(22,18))
for ax,(x0,x1,z0,z1) in zip(axs,rng):
    for n,(k,rg) in enumerate(out.items()):
        pg=Polygon(max(rg,key=lambda p:Polygon(p).area),[h for h in rg if h is not max(rg,key=lambda p:Polygon(p).area)])
        x,z=pg.exterior.xy; ax.fill(x,z,color=cols[n%20],alpha=.5); ax.plot(x,z,'k',lw=.5)
        c=pg.representative_point()
        if x0<=c.x<=x1 and z0<=c.y<=z1: ax.text(c.x,c.y,k.replace('Boss-Extrude','E'),fontsize=7,ha='center')
    ax.set_xlim(x0,x1);ax.set_ylim(z0,z1);ax.set_aspect('equal')
plt.tight_layout();plt.savefig(sys.argv[3],dpi=65)
print(len(out),'solids')
