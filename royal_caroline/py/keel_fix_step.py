# the builder's keel (rhino/backbone_builder_44.STEP, 18 solids): KEEL top surface, KEELSON underside and top replaced by the clean points+spline lines (no pockets), division into parts kept; thickness 5.3 mm centred on Y=0 for the backbone parts (aft bodies X<0 keep 4.0, centred) -> rhino/RoyalCaroline_keel_builder_fixed_v1.step
import sys,re,json,numpy as np; sys.argv=['x']
exec(open('py/step_edges_dump.py').read().split("if __name__")[0])
from scipy.interpolate import splprep,splev
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.OCP.collections import HArray1_gp_Pnt as TColgp_HArray1OfPnt
from OCP.BRepCheck import BRepCheck_Analyzer
NP=json.load(open('data/keel_keelson_points_v1.json'))
def wire_edges(f):
    out=[]
    we=TopExp_Explorer(f,TopAbs_WIRE)
    while we.More():
        w=TopoDS.Wire(we.Current()); wx=BRepTools_WireExplorer(w); E=[]
        while wx.More():
            e=wx.Current(); c=BRepAdaptor_Curve(e); a=c.Value(c.FirstParameter()); b=c.Value(c.LastParameter())
            if wx.Orientation().name=='TopAbs_REVERSED': a,b=b,a
            E.append(((a.X(),a.Z()),(b.X(),b.Z()))); wx.Next()
        out.append(E); we.Next()
    return out
def mkwire(items):
    mw=BRepBuilderAPI_MakeWire()
    for it in items:
        if it[0]=='line':
            (x0,z0),(x1,z1)=it[1],it[2]
            if abs(x0-x1)<1e-9 and abs(z0-z1)<1e-9: continue
            mw.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(x0,0,z0),gp_Pnt(x1,0,z1)).Edge())
        else:
            pts=it[1]; arr=TColgp_HArray1OfPnt(1,len(pts))
            for i,(x,z) in enumerate(pts): arr.SetValue(i+1,gp_Pnt(x,0,z))
            ip=GeomAPI_Interpolate(arr,False,1e-6); ip.Perform(); mw.Add(BRepBuilderAPI_MakeEdge(ip.Curve()).Edge())
    return mw.Wire()
def spline_pts(key,va,vb,fade=40.0,xs_limit=None):
    """points of the new curve between vertex va and vb (x,z), the ends forced onto the vertices with a linear fade of the difference"""
    P=np.array(NP[key]['points']); tck,_=splprep(P.T,k=3,s=0); u=np.linspace(0,1,4000); X,Z=splev(u,tck)
    x0,x1=sorted((va[0],vb[0])); keepm=(P[:,0]>x0+0.5)&(P[:,0]<x1-0.5); Q=[tuple(p) for p in P[keepm]]
    def zc(x): return float(np.interp(x,X,Z)) if X[0]<=x<=X[-1] else None
    # extend the curve linearly at the ends if the vertex lies beyond the data
    def zext(x):
        z=zc(x)
        if z is not None: return z
        if x>X[-1]: s=(Z[-1]-Z[-40])/(X[-1]-X[-40]); return float(Z[-1]+s*(x-X[-1]))
        s=(Z[40]-Z[0])/(X[40]-X[0]); return float(Z[0]+s*(x-X[0]))
    dz={ 'a':va[1]-zext(va[0]),'b':vb[1]-zext(vb[0]) }
    pts=[(va[0],va[1])]+[(x,z+(dz['a']*max(0,1-abs(x-va[0])/fade)+dz['b']*max(0,1-abs(x-vb[0])/fade))) for x,z in Q]+[(vb[0],vb[1])]
    pts=sorted(pts,key=lambda p:p[0],reverse=(va[0]>vb[0])); return pts,dz
def poly_run(E,pred):
    mid=[((a[0]+b[0])/2,(a[1]+b[1])/2) for a,b in E]; idx=[i for i,m in enumerate(mid) if pred(m)]; return idx
REPORT=[]
def fix_keel(E):
    # E from the stem tip back along the top: 0,1 keep (1 shortened); 2..186 stepped top chain replaced
    vend=E[186][1]                      # (45.2,10.07)
    zt=spline_pts('keel_top',(526.6,0.0),vend)[0]  # temp to get extrapolation
    P=np.array(NP['keel_top']['points']); s=(P[-1,1]-P[-4,1])/(P[-1,0]-P[-4,0]); zn=float(P[-1,1]+s*(526.6-P[-1,0]))
    va=(526.6,zn); pts,dz=spline_pts('keel_top',va,vend); items=[('line',)+E[0],('line',E[1][0],va),('spline',pts)]+[('line',)+e for e in E[187:]]
    REPORT.append(('keel top: vertex end (%.1f,%.2f) delta %.3f ; stem vertex (526.6,%.2f)'%(vend[0],vend[1],dz['b'],zn))); return items
def fix_keelson(E):
    # underside chain: edges 86..268 replaced; also removes the tab edges 0,1 and the vertical 268
    vs=E[86][0]; vtop=E[1][1]                      # (45.67,32.81) and (526.6,33.62)
    pts,dz=spline_pts('keelson_under',vs,vtop); items=[('line',)+e for e in E[2:86]]+[('spline',pts)]
    REPORT.append('keelson underside: start vertex (%.2f,%.2f) delta %.3f; stem corner (526.6,%.2f) delta %.3f'%(vs[0],vs[1],dz['a'],vtop[1],dz['b'])); return items,E
def prism_from_wires(wires,y0,th):
    f=BRepBuilderAPI_MakeFace(wires[0]).Face()
    for w in wires[1:]: f=BRepBuilderAPI_MakeFace(f,w).Face()
    t=gp_Trsf(); t.SetTranslation(gp_Vec(0,y0,0)); f=BRepBuilderAPI_Transform(f,t,True).Shape()
    return BRepPrimAPI_MakePrism(f,gp_Vec(0,th,0)).Shape()
def vol(s): g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
AFT={'Split1[1]','Split1[2]','Boss-Extrude4[2]'}
res={}
for nm,(s,f) in SOL.items():
    W=wire_edges(f); th,y0=(4.0,-2.0) if nm in AFT else (5.3,-2.65)
    if nm=='Boss-Extrude2[2]': items=fix_keel(W[0]); wires=[mkwire(items)]+[mkwire([('line',)+e for e in w]) for w in W[1:]]
    elif nm=='Boss-Extrude4[4]':
        items,_=fix_keelson(W[0]); wires=[mkwire(items)]+[mkwire([('line',)+e for e in w]) for w in W[1:]]
    else: wires=None
    if wires is None:
        t=gp_Trsf(); t.SetTranslation(gp_Vec(0,y0,0)); f2=BRepBuilderAPI_Transform(f,t,True).Shape(); sol=BRepPrimAPI_MakePrism(f2,gp_Vec(0,th,0)).Shape()   # original face (holes and exact edges kept)
    else: sol=prism_from_wires(wires,y0,th)
    sol0=sol
    _=None
    sol=sol0
    ok=BRepCheck_Analyzer(sol).IsValid(); v=vol(sol); v0=vol(s)
    res[nm]=(sol,ok,v,v0,th); print('%-18s valid %s thickness %.1f volume %.0f (orig %.0f x %.3f = %.0f)'%(nm,ok,th,v,v0,th/4.0,v0*th/4.0))
print('\n'.join(map(str,REPORT)))
import pickle
from OCP.STEPCAFControl import STEPCAFControl_Writer
from OCP.TDocStd import TDocStd_Document
from OCP.XCAFApp import XCAFApp_Application
from OCP.XCAFDoc import XCAFDoc_DocumentTool
from OCP.TCollection import TCollection_ExtendedString,TCollection_AsciiString
from OCP.TDataStd import TDataStd_Name
from OCP.TDF import TDF_Label
app=XCAFApp_Application.GetApplication_s(); doc=TDocStd_Document(TCollection_ExtendedString('MDTV-XCAF')); app.InitDocument(doc)
st=XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
for nm,(sol,ok,v,v0,th) in res.items():
    lab=st.AddShape(sol,False); TDataStd_Name.Set_s(lab,TCollection_ExtendedString(nm))
w=STEPCAFControl_Writer(); w.Transfer(doc); w.Write('rhino/RoyalCaroline_keel_builder_fixed_v1.step'); print('written')
