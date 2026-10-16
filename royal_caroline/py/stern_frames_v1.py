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
parts={p['name']:p for p in json.load(open('data/parts_v10.json'))}
H1=Polygon(parts['HALF_FRAME_H1_S']['poly']); H2=Polygon(parts['HALF_FRAME_H2_S']['poly'])
fp=[Polygon(p['poly']).buffer(0) for p in json.load(open('data/frame_pieces_v10.json'))['pieces'] if p['frame']==1 and p['side'] in('S','C')]
F1=unary_union(fp)
refs=[(12.0,H2),(24.0,H1),(39.0,F1)]   # (layer-centre X, shape)
SS=np.linspace(0.04,0.96,47)
def outer(P):
    zb,zt=P.bounds[1],P.bounds[3]; y=[]
    for s in SS:
        g=P.intersection(LineString([(-100,zb+s*(zt-zb)),(100,zb+s*(zt-zb))]))
        y.append(g.bounds[2] if not g.is_empty else np.nan)
    y=np.array(y); ok=~np.isnan(y); return np.interp(SS,SS[ok],y[ok]),zb,zt
O=[outer(P) for _,P in refs]; Xr=[r[0] for r in refs]
def fitq(vals,x): return np.polyval(np.polyfit(Xr,vals,2),x)
def new_poly(xc):
    T,(yt,zbt,ztt)=(H1,O[1]) if xc>=16 else (H2,O[0])
    yo=np.array([fitq([O[k][0][i] for k in range(3)],xc) for i in range(len(SS))])
    zb=fitq([O[k][1] for k in range(3)],xc); zt=fitq([O[k][2] for k in range(3)],xc)
    pts=[]
    for y,z in T.exterior.coords[:-1]:
        s=(z-zbt)/(ztt-zbt); pts.append((y+np.interp(s,SS,yo)-np.interp(s,SS,yt), zb+s*(zt-zb)))
    return Polygon(pts).buffer(0),(zb,zt)
def prism(P,x0,w=4.0,mirror=False):
    mp=BRepBuilderAPI_MakePolygon()
    for y,z in list(P.exterior.coords)[:-1]: mp.Add(gp_Pnt(x0,-y if mirror else y,z))
    mp.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mp.Wire()).Face(),gp_Vec(w,0,0)).Shape()
frames={}; info=[]
for fn,x0s in ((46,(24,28)),(47,(13,17)),(48,(2,6))):
    for L,x0 in zip('FA',x0s[::-1]) if False else zip(('fwd','aft'),x0s[::-1] if False else x0s[::-1]):
        pass
for fn,(xa,xb) in ((46,(24,28)),(47,(13,17)),(48,(2,6))):
    for lay,x0 in (('A',xa),('F',xb)):       # A = aft layer (lower X), F = forward layer
        P,zr=new_poly(x0+2); info.append((fn,lay,round(P.area),[round(b,1) for b in P.bounds]))
        frames[f'FRAME{fn}_{lay}_S']=prism(P,x0); frames[f'FRAME{fn}_{lay}_P']=prism(P,x0,mirror=True)
# transoms: cut to F48 aft face X=2.0, tenons into F48 aft layer
XF=2.0; TD=2.2
def box(x0,x1,y0,y1,z0,z1): return BRepPrimAPI_MakeBox(gp_Pnt(x0,y0,z0),gp_Pnt(x1,y1,z1)).Shape()
trs={}; pockets=[]; PA,_=new_poly(4.0)
from shapely.geometry import box as sb
for n in ('TRANSOM_2','TRANSOM_3','WING_TRANSOM'):
    t=BRepAlgoAPI_Common(S.allp[n],box(-100,XF,-100,100,0,200)).Shape()
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
json.dump({'info':info,'clashes':cl},open('qa/stern_frames_v1.json','w'))
import pickle
S_names=allp
# export
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
comp=TopoDS_Compound(); bb=BRep_Builder(); bb.MakeCompound(comp)
for s in allp.values(): bb.Add(comp,s)
w=STEPControl_Writer(); w.Transfer(comp,STEPControl_AsIs); w.Write('rhino/RoyalCaroline_stern_frames_v1.step')
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
f.Write('rhino/RoyalCaroline_stern_frames_v1_meshes.3dm',7); print('3dm',len(f.Objects))
# QA 2D
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,ax=plt.subplots(1,2,figsize=(14,7))
for (fn,xs,c) in ((46,28,'tab:blue'),(47,17,'tab:green'),(48,6,'tab:red')):
    P,_=new_poly(xs+2); ax[0].plot(*zip(*P.exterior.coords),c,label=f'F{fn}')
    ax[0].plot(*zip(*[(-y,z) for y,z in P.exterior.coords]),c)
P,_=new_poly(4.0)
ax[0].plot(*zip(*F1.exterior.coords) if F1.geom_type=='Polygon' else [[],[]],'k:',lw=.5)
for n,(z0,z1) in {'T3':(53.3,57.6),'T2':(61.5,65.5),'WING':(71.8,75.8)}.items(): ax[0].axhspan(z0,z1,color='orange',alpha=.3); ax[0].text(0,(z0+z1)/2,n,ha='center')
ax[0].set_aspect('equal'); ax[0].legend(); ax[0].set_title('aft view YZ')
from OCP.BRepBndLib import BRepBndLib
cols={'COUNTER':'gray','TRANSOM':'orange','WING':'orange','FRAME':'tab:blue'}
for n,s in allp.items():
    b=Bnd_Box(); BRepBndLib.Add_s(s,b); c=next(v for k,v in cols.items() if n.startswith(k))
    ax[1].add_patch(plt.Rectangle((b.CornerMin().X(),b.CornerMin().Z()),b.CornerMax().X()-b.CornerMin().X(),b.CornerMax().Z()-b.CornerMin().Z(),fill=False,ec=c,lw=.8))
ax[1].set_xlim(-55,45); ax[1].set_ylim(10,150); ax[1].set_aspect('equal'); ax[1].set_title('side XZ bounding boxes')
plt.savefig('qa/stern_frames_v1.png',dpi=80)
