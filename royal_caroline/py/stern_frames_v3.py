# Frames 46-48 (double, W=8, gap 3) from half-frame templates + outer breadth interpolated in X; F48 joined to transoms with tenons/pockets.
import json,sys,numpy as np
sys.path.insert(0,'py')
import stern_v5 as S   # gives S.allp (timbers+transoms), S.vol, helpers
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf,gp_Ax2,gp_Dir
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace,BRepBuilderAPI_MakePolygon,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism,BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common,BRepAlgoAPI_Cut,BRepAlgoAPI_Fuse
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
# ---- frames from the hull lines: Y at the waterline crossings (WL I-VII) + body-plan stations 16/17/18 (quadratic in X), splines through a few points
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.collections import HArray1_gp_Pnt as HArr
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge,BRepBuilderAPI_MakeWire
from scipy.interpolate import splprep,splev
D=np.load('data/hull_lines_stern.npz'); STX={'ST18':0.0,'ST17':14.6,'ST16':36.8}; W=4.7; YB=2.65
_b=json.load(open('data/f46_anchor_bias.json')); BZ=[p[0] for p in _b]; BY=[p[1] for p in _b]   # F46 (accepted) minus line-derived F46: carried along the flow to F47, F48
def stY(k,z): c=D[k]; return float(np.interp(z,c[:,2],c[:,1]))
def q3(vals,x): return float(np.polyval(np.polyfit(list(STX.values()),vals,2),x))
def wlY(k,X):
    v=D[k]; idx=np.where(np.diff(np.sign(v[:,0]-X))!=0)[0]
    return None if len(idx)==0 else float(np.interp(X,[v[idx[0],0],v[idx[0]+1,0]],[v[idx[0],1],v[idx[0]+1,1]])),float(v[0,2])
WL=['WL_I_plan','WL_II_plan','WL_III_plan','WL_IV_plan','WL_V_plan','WL_VI_plan_stern_part_only','WL_VII_plan_stern_part_only']
RAB=[(1.2,52.1),(6.3,43.4),(13.5,34.8),(21.1,26.1),(37.7,17.4)]   # rabbet points from the WL ends (X,Z)
def outer_pts(X):
    zf=float(np.interp(X,[p[0] for p in RAB],[p[1] for p in RAB]))
    top=[D[k][-1] for k in STX]; zt=q3([t[2] for t in top],X); yt=q3([t[1] for t in top],X)
    P={}
    for k in WL:
        r=wlY(k,X)
        if r and r[0] is not None and r[0]>3.6 and r[1]>zf+1.5: P[round(r[1],1)]=r[0]
    for z in (58,64,76,86,98,110,121):
        if z>zf+3 and all(abs(z-q)>3.5 for q in P): P[z]=q3([stY(k,z) for k in STX],X)
    P[round(zt,1)]=yt; pts=[(YB,zf)]+[(P[z],z) for z in sorted(P) if z<zt-2.5 or z==round(zt,1)]
    return [(y+(np.interp(z,BZ,BY)*min(1.0,max(0.0,(z-52)/8))),z) for y,z in pts]
def spline_edge(pts3):
    arr=HArr(1,len(pts3))
    for i,p in enumerate(pts3): arr.SetValue(i+1,gp_Pnt(*p))
    it=GeomAPI_Interpolate(arr,False,1e-6); it.Perform(); return BRepBuilderAPI_MakeEdge(it.Curve()).Edge()
def frame_profile(X):
    O=np.array(outer_pts(X)); tck,u=splprep(O.T,k=3,s=0); dy,dz=splev(u,tck,der=1); n=np.c_[dz,-dy]; n/=np.hypot(*n.T)[:,None]
    I=O-W*n; return O,I,tck
def new_poly(X,dense=True):
    O,I,tck=frame_profile(X); t=np.linspace(0,1,120); oy,oz=splev(t,tck)
    Iy,Iz=splev(t,splprep(I.T,k=3,s=0)[0]); P=Polygon(list(zip(oy,oz))+list(zip(Iy,Iz))[::-1]).buffer(0)
    P=P.intersection(sbx(YB,-10,200,300))
    if P.geom_type!='Polygon': P=max(P.geoms,key=lambda g:g.area)
    return P,(O[0,1],O[-1,1])
from shapely.geometry import box as sbx
def prism(P,x0,w=4.0,mirror=False):    # polygon prism (used for tenons)
    mp=BRepBuilderAPI_MakePolygon()
    for y,z in list(P.exterior.coords)[:-1]: mp.Add(gp_Pnt(x0,-y if mirror else y,z))
    mp.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mp.Wire()).Face(),gp_Vec(w,0,0)).Shape()
def frame_solid(X,x0,mirror):
    O,I,_=frame_profile(X); sg=-1 if mirror else 1
    E=lambda A:spline_edge([(x0,sg*y,z) for y,z in A]); w=BRepBuilderAPI_MakeWire()
    ln=lambda p,q:BRepBuilderAPI_MakeEdge(gp_Pnt(x0,sg*p[0],p[1]),gp_Pnt(x0,sg*q[0],q[1])).Edge()
    w.Add(E(O)); w.Add(ln(O[-1],I[-1])); w.Add(E(I[::-1])); w.Add(ln(I[0],O[0]))
    sh=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(w.Wire(),True).Face(),gp_Vec(4,0,0)).Shape()
    clip=BRepPrimAPI_MakeBox(gp_Pnt(x0-1,YB if not mirror else -200,-10),gp_Pnt(x0+5,200 if not mirror else -YB,300)).Shape()
    return BRepAlgoAPI_Common(sh,clip).Shape()
frames={}; info=[]
for fn,(xa,xb) in ((46,(24,28)),(47,(13,17)),(48,(2,6))):
    for lay,x0 in (('A',xa),('F',xb)):
        P,zr=new_poly(x0+2); info.append((fn,lay,round(P.area),[round(b,1) for b in P.bounds]))
        frames[f'FRAME{fn}_{lay}_S']=frame_solid(x0+2,x0,False); frames[f'FRAME{fn}_{lay}_P']=frame_solid(x0+2,x0,True)
# transoms: cut to F48 aft face X=2.0, tenons into F48 aft layer
XF=2.0; TD=2.2
def box(x0,x1,y0,y1,z0,z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0,y0,z0),gp_Pnt(x1,y1,z1)).Shape()
trs={}; pockets=[]; PA,_=new_poly(4.0)
from shapely.geometry import box as sb
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
def arched(poly,hw):   # XZ section shifted in X by the wing's plan arc kp*(y^2-Yc0^2), smooth loft
    ts=BRepOffsetAPI_ThruSections(True,False)
    for y in np.linspace(-hw,hw,9):
        dx=S.kp*(y*y-S.Yc[0]**2); mp=BRepBuilderAPI_MakePolygon()
        for x,z in poly: mp.Add(gp_Pnt(x+dx,y,z))
        mp.Close(); ts.AddWire(mp.Wire())
    ts.Build(); return ts.Shape()
T=json.load(open('data/stern_transom_outline_v2.json'))['transoms_normalized']
src={'TRANSOM_2':arched(T['T2']['poly'],37.8),'TRANSOM_3':arched(T['T3']['poly'],12.7),'WING_TRANSOM':S.allp['WING_TRANSOM']}
for n in ('TRANSOM_2','TRANSOM_3','WING_TRANSOM'):
    t=BRepAlgoAPI_Common(src[n],box(-100,XF,-100,100,0,200)).Shape()
    sec=BRepAlgoAPI_Common(t,box(XF-0.3,XF,-100,100,0,200)).Shape(); b=Bnd_Box(); BRepBndLib.Add_s(sec,b)
    z0,z1=b.CornerMin().Z()+0.7,b.CornerMax().Z()-0.7; h=b.CornerMax().Y()-0.7
    for sg in (False,True):
        for g,m in ((PA.buffer(-0.6).intersection(sb(0,z0,h,z1)),0),(PA.buffer(0.1).intersection(sb(0,z0-0.1,h+0.5,z1+0.1)),1)):
            for q in (getattr(g,'geoms',[g])):
                if q.geom_type!='Polygon' or q.area<1: continue
                if m==0: t=BRepAlgoAPI_Fuse(t,prism(q,XF-0.2,TD+0.2,sg)).Shape()
                else: pockets.append(prism(q,XF-0.01,TD+0.1,sg))
    trs[n]=t
for k in ('FRAME48_A_S','FRAME48_A_P'):
    for p in pockets: frames[k]=BRepAlgoAPI_Cut(frames[k],p).Shape()
allp={**{k:v for k,v in S.allp.items() if k.startswith('COUNTER')},**trs,**frames}
print('frames',info)
for n,s in allp.items():
    if not BRepCheck_Analyzer(s).IsValid(): print('INVALID',n)
names=list(allp); cl=[]
for i,a in enumerate(names):
    for b in names[i+1:]:
        if a.startswith('COUNTER') and b.startswith('COUNTER'): continue
        v=S.vol(BRepAlgoAPI_Common(allp[a],allp[b]).Shape())
        if v>0.05: cl.append((a,b,round(v,2)))
print('clashes',cl)
json.dump({'info':info,'clashes':cl},open('qa/stern_frames_v3.json','w'))
import pickle
S_names=allp
# export
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
comp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(comp)
for s in allp.values(): bb.Add(comp,s)
w=STEPControl_Writer(); w.Transfer(comp,STEPControl_AsIs); w.Write('rhino/RoyalCaroline_stern_frames_v3.step')
S.allp=allp
# mesh 3dm
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE,TopAbs_REVERSED
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS
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
                a,b,c=tri.Triangle(i).Get(); m.Faces.AddFace(off+a-1,off+(c if rev else b)-1,off+(b if rev else c)-1)
            off+=tri.NbNodes()
        ex.Next()
    m.Normals.ComputeNormals(); m.Compact(); at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=n; f.Objects.AddMesh(m,at)
f.Write('rhino/RoyalCaroline_stern_frames_v3_meshes.3dm',7); print('3dm',len(f.Objects))
# QA 2D
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(14,7))
for (fn,xs,c) in ((46,28,'tab:blue'),(47,17,'tab:green'),(48,6,'tab:red')):
    P,_=new_poly(xs); ax[0].plot(*zip(*P.exterior.coords),c,label=f'F{fn}')
    ax[0].plot(*zip(*[(-y,z) for y,z in P.exterior.coords]),c)
P,_=new_poly(4.0)
for k in STX: ax[0].plot(D[k][:,1],D[k][:,2],'k:',lw=.6); ax[0].plot(-D[k][:,1],D[k][:,2],'k:',lw=.6)
for n,(z0,z1) in {'T3':(53.3,57.6),'T2':(61.5,65.5),'WING':(71.8,75.8)}.items(): ax[0].axhspan(z0,z1,color='orange',alpha=.3); ax[0].text(0,(z0+z1)/2,n,ha='center')
ax[0].set_aspect('equal'); ax[0].legend(); ax[0].set_title('aft view YZ')
for z,nm in ((55.4,'T3'),(63.5,'T2'),(73.8,'WING')):
    for n,sh in allp.items():
        if not (n.startswith('TRANSOM') or n.startswith('WING') or n.startswith('FRAME4')): continue
        sl=BRepAlgoAPI_Common(sh,box(-100,100,-100,100,z-0.05,z+0.05)).Shape(); BRepMesh_IncrementalMesh(sl,0.05)
        ex=TopExp_Explorer(sl,TopAbs_FACE); xs=[];ys=[]
        while ex.More():
            fc=TopoDS.Face(ex.Current()); lc=TopLoc_Location(); tr=BRep_Tool.Triangulation_s(fc,lc)
            if tr is not None:
                for i in range(1,tr.NbNodes()+1): p=tr.Node(i).Transformed(lc.Transformation()); xs.append(p.X()); ys.append(p.Y())
            ex.Next()
        if xs: ax[1].scatter(ys,[x+{55.4:-40,63.5:0,73.8:40}[z]*0 for x in xs],s=0.5,c='orange' if not n.startswith('FRAME') else 'tab:red')
ax[1].set_aspect('equal'); ax[1].set_title('plan XY slices at Z=55.4/63.5/73.8 (Y horizontal, X vertical)'); ax[1].set_ylim(-12,12)
plt.savefig('qa/stern_frames_v3.png',dpi=80)
