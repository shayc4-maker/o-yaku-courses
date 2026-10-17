# Hull surface lofted through the body-plan station splines (the builder's lines), sectioned by planes X=const -> exact hull line at any X (no point mixing, no smoothing)
import numpy as np,sys,pickle
from OCP.gp import gp_Pnt,gp_Pln,gp_Dir
from OCP.collections import HArray1_gp_Pnt as HArr
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
ST=np.load('data/hull_stations_all.npz'); names=sorted(ST.files,key=lambda k:ST[k][0,0])
def wire_of(k,n=36):
    v=ST[k]; idx=np.linspace(0,len(v)-1,n).astype(int); X=float(v[0,0]); P=v[idx]
    arr=HArr(1,len(P))
    for i,p in enumerate(P): arr.SetValue(i+1,gp_Pnt(X,p[1],p[2]))
    it=GeomAPI_Interpolate(arr,False,1e-6); it.Perform(); return BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(it.Curve()).Edge()).Wire()
def build():
    ts=BRepOffsetAPI_ThruSections(False,False,1e-6)
    for k in names: ts.AddWire(wire_of(k))
    ts.Build(); return ts.Shape()
SURF=None
import os,pickle
_CACHE='/tmp/claude-0/x/loft_cache.pkl'
_C=pickle.load(open(_CACHE,'rb')) if os.path.exists(_CACHE) else {}
def section(X,n=300):
    global SURF
    key=round(X,2)
    if key in _C: return _C[key]
    if SURF is None: SURF=build()
    pl=gp_Pln(gp_Pnt(X,0,0),gp_Dir(1,0,0)); sec=BRepAlgoAPI_Section(SURF,pl); sec.Build(); ex=TopExp_Explorer(sec.Shape(),TopAbs_EDGE); pts=[]
    while ex.More():
        c=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()) if hasattr(TopoDS,'Edge_s') else TopoDS.Edge(ex.Current())); u0,u1=c.FirstParameter(),c.LastParameter()
        for u in np.linspace(u0,u1,n): p=c.Value(u); pts.append((p.Y(),p.Z()))
        ex.Next()
    P=np.array(pts); P=P[np.argsort(P[:,1])]; _C[key]=P; pickle.dump(_C,open(_CACHE,'wb')); return P
if __name__=='__main__':
    for X in (480.27,476.27,484.27,524.0):
        P=section(X); print('X',X,'points',len(P),'Z range',P[0,1].round(1),P[-1,1].round(1)); print('   Y at Z 8.7/17.4/26.1/34.8/43.4/66/90:',[round(float(np.interp(z,P[:,1],P[:,0])),1) for z in (8.7,17.4,26.1,34.8,43.4,66,90)])
