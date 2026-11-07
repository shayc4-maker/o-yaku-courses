# Hull surface lofted through the NEW approved body-plan splines (data/bodyplan_splines_v1.json); section(X) = exact hull line at any X
import json,numpy as np,pickle,os
from OCP.gp import gp_Pnt,gp_Pln,gp_Dir
from OCP.collections import HArray1_gp_Pnt as HArr
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopoDS import TopoDS
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
C=json.load(open('data/bodyplan_splines_v1.json'))
def wire_of(n,m=40):
    v=np.array(C[str(n)]['curve']); s=np.r_[0,np.cumsum(np.hypot(*np.diff(v,axis=0).T))]; t=np.linspace(0,s[-1],m)
    P=np.c_[np.interp(t,s,v[:,0]),np.interp(t,s,v[:,1])]; arr=HArr(1,m)
    for i,p in enumerate(P): arr.SetValue(i+1,gp_Pnt(XST[n],p[0],p[1]))
    it=GeomAPI_Interpolate(arr,False,1e-6); it.Perform(); return BRepBuilderAPI_MakeWire(BRepBuilderAPI_MakeEdge(it.Curve()).Edge()).Wire()
SURF=None; _CACHE='/tmp/claude-0/x/loft_new_cache.pkl'; _C=pickle.load(open(_CACHE,'rb')) if os.path.exists(_CACHE) else {}
def build():
    ts=BRepOffsetAPI_ThruSections(False,False,1e-6)
    for n in sorted(XST,key=lambda k:XST[k]): ts.AddWire(wire_of(n))
    ts.Build(); return ts.Shape()
def section(X,n=300):
    global SURF
    key=round(X,2)
    if key in _C: return _C[key]
    if SURF is None: SURF=build()
    sec=BRepAlgoAPI_Section(SURF,gp_Pln(gp_Pnt(X,0,0),gp_Dir(1,0,0))); sec.Build(); ex=TopExp_Explorer(sec.Shape(),TopAbs_EDGE); pts=[]
    while ex.More():
        c=BRepAdaptor_Curve(TopoDS.Edge_s(ex.Current()) if hasattr(TopoDS,'Edge_s') else TopoDS.Edge(ex.Current())); u0,u1=c.FirstParameter(),c.LastParameter()
        for u in np.linspace(u0,u1,n): p=c.Value(u); pts.append((p.Y(),p.Z()))
        ex.Next()
    P=np.array(pts); P=P[np.argsort(P[:,1])]; _C[key]=P; pickle.dump(_C,open(_CACHE,'wb')); return P
if __name__=='__main__':
    for X in (280.46,284.46,288.46):
        P=section(X); print('X',X,len(P),'Z',P[0,1].round(1),'..',P[-1,1].round(1),'Y at Z 8.7/26.1/52/80/100:',[round(float(np.interp(z,P[:,1],P[:,0])),1) for z in (8.7,26.1,52,80,100)])
