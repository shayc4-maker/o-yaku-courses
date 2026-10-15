# Stern v5: six counter timbers from the builder's approved profile (one closed outline: lines + clean splines), tapered in side and aft view.
import json,math,numpy as np,sys
from shapely.geometry import LineString,Point,Polygon,box as sbox
from shapely.ops import substring
from scipy.interpolate import splprep,splev
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf,gp_Ax2,gp_Dir
from OCP.collections import HArray1_gp_Pnt as TColgp_HArray1OfPnt
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform,BRepBuilderAPI_MakePolygon
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
S=json.load(open('data/stern_side_points_v3.json'))
R0,R1=map(np.array,S['strip_right_edge']); L0,L1=map(np.array,S['strip_left_edge'])
trR=np.array(S['transition_right']); trL=np.array(S['transition_left']); G=np.array(S['knee_lower_green']); B=np.array(S['knee_upper_blue_parallel'])
def dense(arr,k,n=400):
    tck,u=splprep(arr.T,k=k,s=0); t=np.linspace(0,1,n); x,z=splev(t,tck); dx,dz=splev(t,tck,der=1); return np.c_[x,z],np.c_[dx,dz]
def ext(P,T,e=10):
    a=T[0]/np.hypot(*T[0]); b=T[-1]/np.hypot(*T[-1]); return LineString([tuple(P[0]-a*e)]+list(map(tuple,P))+[tuple(P[-1]+b*e)])
pR,tR=dense(trR,2); pL,tL=dense(trL,2); pG,tG=dense(G,3); pB,tB=dense(B,3)
lR,lL,lG,lB=ext(pR,tR),ext(pL,tL),ext(pG,tG),ext(pB,tB)
def pt(g): return np.array(g.coords[0]) if g.geom_type=='Point' else np.array(list(g.geoms)[0].coords[0])
JR=pt(lR.intersection(lB)); JL=pt(lL.intersection(lG)); ztr=75.75; cut=LineString([(-60,ztr),(20,ztr)])
EB=pt(lB.intersection(cut)); EG=pt(lG.intersection(cut))
def sub(line,a,b): return substring(line,line.project(Point(a)),line.project(Point(b)))
pieces=[('line',[R0,R1]),('spl',sub(lR,R1,JR)),('spl',sub(lB,JR,EB)),('line',[EB,EG]),('spl',sub(lG,EG,JL)),('spl',sub(lL,JL,L1)),('line',[L1,L0]),('line',[L0,R0])]
# minimal control points per spline piece (arclength-spaced), checked against the dense curve
ctrl=[]
for kind,s in pieces:
    if kind=='line': ctrl.append((kind,[np.array(s[0]),np.array(s[1])])); continue
    n=5 if s.length>12 else 4
    P=np.array([s.interpolate(d).coords[0] for d in np.linspace(0,s.length,n)]); ctrl.append((kind,list(P)))
def make_edge(kind,P,y=0.0):
    if kind=='line': return BRepBuilderAPI_MakeEdge(gp_Pnt(P[0][0],y,P[0][1]),gp_Pnt(P[1][0],y,P[1][1])).Edge()
    arr=TColgp_HArray1OfPnt(1,len(P))
    for i,p in enumerate(P): arr.SetValue(i+1,gp_Pnt(p[0],y,p[1]))
    it=GeomAPI_Interpolate(arr,False,1e-6); it.Perform(); return BRepBuilderAPI_MakeEdge(it.Curve()).Edge()
def profile_face(dx=0.0,y=-40.0):
    w=BRepBuilderAPI_MakeWire()
    for kind,P in ctrl: w.Add(make_edge(kind,[np.array(p)+np.array([dx,0]) for p in P],y))
    return BRepBuilderAPI_MakeFace(w.Wire(),True).Face()
def vol(s): g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
def poly_prism(pts3,vec):
    mp=BRepBuilderAPI_MakePolygon()
    for p in pts3: mp.Add(gp_Pnt(*p))
    mp.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mp.Wire()).Face(),gp_Vec(*vec)).Shape()
# ---- placement from the builder's data
Yc=[7.5,23.2,40.2]; Zdeck=[120.0,119.7,118.6]; SPL=[1.8,5.5,8.9]
kp=4.7/40.2**2; kz=5.85e-3; ZTOP0=float(R0[1]); TAPER=-0.0155; T119=3.0
t=lambda z:T119+TAPER*(z-119.0)
timbers={}
for i in range(3):
    tz=math.tan(math.radians(SPL[i])); yc=lambda z,i=i: Yc[i]+tz*(Zdeck[i]-z)        # inward lean towards the top
    dx=kp*(Yc[i]**2-Yc[0]**2)
    ytop=yc(ZTOP0); ztop=ZTOP0-kz*(ytop**2-yc(ZTOP0)*0-(yc(ZTOP0)*0)) if False else ZTOP0-kz*(ytop**2-(Yc[0]+math.tan(math.radians(SPL[0]))*(Zdeck[0]-ZTOP0))**2)
    prism=BRepPrimAPI_MakePrism(profile_face(dx,-70.0),gp_Vec(0,140,0)).Shape()
    z0,z1=60.0,160.0
    yL=lambda z: yc(z)-t(z)/2; yR=lambda z: yc(z)+t(z)/2
    wedge=poly_prism([(-100,yL(z0),z0),(-100,yR(z0),z0),(-100,yR(z1),z1),(-100,yL(z1),z1)],(200,0,0))
    s=BRepAlgoAPI_Common(prism,wedge).Shape()
    s=BRepAlgoAPI_Common(s,BRepPrimAPI_MakeBox(gp_Pnt(-100,-100,50),gp_Pnt(100,100,ztop)).Shape()).Shape()
    timbers['S%d'%(i+1)]=s
    tr=gp_Trsf(); tr.SetMirror(gp_Ax2(gp_Pnt(0,0,0),gp_Dir(0,1,0)))
    timbers['P%d'%(i+1)]=BRepBuilderAPI_Transform(s,tr,True).Shape()
    print('timber',i+1,'Yc deck',Yc[i],'dx %.2f'%dx,'ztop %.2f'%ztop,'t(top) %.2f t(foot) %.2f'%(t(ztop),t(75.75)),'valid',BRepCheck_Analyzer(s).IsValid(),'vol %.1f'%vol(s))
# ---- transoms 1-3 (builder chains) as XZ profiles, plan arc for the wing transom
T1=[(-9.2,75.8),(-4.9,75.7),(-3.4,71.8),(-7.9,71.9)]; T2=[(-6.0,65.5),(0.4,65.4),(3.2,61.5),(-4.8,61.7)]; T3=[(-3.5,57.3),(6.8,57.6),(11.0,53.3),(-2.45,53.4)]
def xz_prism(poly,y0,y1): return poly_prism([(x,y0,z) for x,z in poly],(0,y1-y0,0))
trans={'TRANSOM_2':xz_prism(T2,-37.8,37.8),'TRANSOM_3':xz_prism(T3,-12.7,12.7)}
# wing transom: plan arc (aft edge follows the timber feet), Z 71.85..75.75 (block 1)
ys=np.linspace(-49,49,50); xa=-8.55; xf=-4.15
wt=poly_prism([(xa+kp*(y*y-Yc[0]**2),y,71.85) for y in ys]+[(xf+kp*(y*y-Yc[0]**2),y,71.85) for y in ys[::-1]],(0,0,3.9)); trans['WING_TRANSOM']=wt
allp={**{'COUNTER_TIMBER_'+k:v for k,v in timbers.items()},**trans}
names=list(allp); rows=[]
for i,a in enumerate(names):
    for b in names[i+1:]:
        v=vol(BRepAlgoAPI_Common(allp[a],allp[b]).Shape())
        if v>0.05: rows.append((a,b,round(v,2)))
print('clashes among stern parts',rows)
import pickle; pickle.dump({k:None for k in allp},open('/tmp/_names.pkl','wb'))
# ---- export: STEP + 3dm (meshes, layer per part)
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
comp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(comp)
for s in allp.values(): bb.Add(comp,s)
w=STEPControl_Writer(); w.Transfer(comp,STEPControl_AsIs); w.Write('rhino/RoyalCaroline_stern_v5.step')
import rhino3dm as r3
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
for n,s in allp.items():
    BRepMesh_IncrementalMesh(s,0.05,False,0.3,True)
    l=r3.Layer(); l.Name=n; idx=f.Layers.Add(l); m=r3.Mesh(); off=0
    ex=TopExp_Explorer(s,TopAbs_FACE)
    while ex.More():
        face=TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(face,loc)
        if tri is not None:
            tr_=loc.Transformation()
            for i in range(1,tri.NbNodes()+1):
                p=tri.Node(i).Transformed(tr_); m.Vertices.Add(p.X(),p.Y(),p.Z())
            rev=face.Orientation()==TopAbs_REVERSED
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); 
                m.Faces.AddFace(off+a-1,off+(c if rev else b)-1,off+(b if rev else c)-1)
            off+=tri.NbNodes()
        ex.Next()
    m.Normals.ComputeNormals(); m.Compact(); at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=n; f.Objects.AddMesh(m,at)
f.Write('rhino/RoyalCaroline_stern_v5_meshes.3dm',7); print('written',len(f.Objects),'objects')
