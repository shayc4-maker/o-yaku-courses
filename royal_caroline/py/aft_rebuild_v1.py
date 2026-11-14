# rebuild F46-F51 from the builder's lines file (91445723): F46-48 faces from layer APPROVED_aft_frames_46_48_with_tops_on_S1, F49-51 from LATEST_F49_F51; whole F46-48 (floor under keelson, wall 2.65 = full keel), F49-51 halves; final (sanded) lofts; cut by the keel parts (clearance check)
import json,glob,re,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_Transform
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut,BRepAlgoAPI_Common
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepCheck import BRepCheck_Analyzer
S='/tmp/claude-0/-home-user-o-yaku-courses/db230f8a-8640-51de-bf4e-53423595c88f/scratchpad/'
KB=2.65; TH=3.2; SHIFT=0.6
SB=np.array(json.load(open('data/bulwark_line_v3.json'))['S1'])
m=r3.File3dm.Read(glob.glob('/root/.claude/uploads/*/91445723-*.3dm')[0]); L={l.Index:l.Name for l in m.Layers}
C={}
for o in m.Objects:
    n=L[o.Attributes.LayerIndex]; g=o.Geometry
    if (n.startswith('APPROVED_aft_frames_46_48') or n.startswith('LATEST_F49')) and hasattr(g,'Domain'):
        mm=re.match(r'F(\d+)[ _](back|mid|front)',o.Attributes.Name)
        if not mm: continue
        P=np.array([[q.X,q.Y,q.Z] for q in (g.PointAt(t) for t in np.linspace(g.Domain.T0,g.Domain.T1,200))]); C[(int(mm.group(1)),mm.group(2))]=P
print('curves',sorted(C))
def extend(Cc,a,b):
    d0=Cc[0]-Cc[3]; d0/=np.hypot(*d0); d1=Cc[-1]-Cc[-4]; d1/=np.hypot(*d1); return np.vstack([Cc[0]+d0*a,Cc,Cc[-1]+d1*b])
def band(Cc,wall,zbot=None):
    E=extend(Cc,8,8); ls=LineString(E); best=None
    for sg in (1,-1):
        oc=ls.offset_curve(sg*TH)
        if oc.geom_type!='LineString' or oc.is_empty: continue
        c2=np.array(oc.coords)
        if np.hypot(*(c2[0]-E[0]))>np.hypot(*(c2[-1]-E[0])): c2=c2[::-1]
        if best is None or c2[:,0].mean()<best[:,0].mean(): best=c2
    p=Polygon(np.vstack([E,best[::-1]])).buffer(0)
    if wall: p=p.intersection(box(KB,-50,300,400))
    if zbot is not None: p=p.intersection(box(-50,zbot,300,400))
    return max(p.geoms,key=lambda q:q.area) if p.geom_type!='Polygon' else p
FR={}
for b in (46,47,48,49,50,51):
    xc=C[(b,'mid')][0,0]; FP={}
    for nm in ('back','mid','front'):
        P=C[(b,nm)]; o=np.argsort(P[:,2]); YZ=np.c_[P[o,1],P[o,2]]
        if b<=48:
            h=band(YZ,True); zm=h.bounds[1]; w=unary_union([h,Polygon([(-y,z) for y,z in h.exterior.coords]),box(-KB-.01,zm,KB+.01,zm+TH)]).buffer(.01).buffer(-.01)
            FP[nm]=np.array(w.exterior.coords)
        else: FP[nm]=np.array(band(YZ,False,zbot=float(YZ[0,1])).exterior.coords)
    FR[b]=dict(xc=float(xc),FP=FP)
    print('F%d xc %.1f faces X %s'%(b,xc,[round(C[(b,k)][0,0],1) for k in('back','mid','front')]))
N=240
def resample(P):
    P=np.asarray(P,float)
    if np.allclose(P[0],P[-1]): P=P[:-1]
    a=0.5*np.sum(P[:,0]*np.roll(P[:,1],-1)-np.roll(P[:,0],-1)*P[:,1])
    if a<0: P=P[::-1]
    c=P.mean(0); mk=P[:,0]<=c[0]; i=int(np.argmin(np.where(mk,P[:,1],1e9))); P=np.roll(P,-i,axis=0); Q=np.vstack([P,P[0]]); s=np.r_[0,np.cumsum(np.hypot(*np.diff(Q,axis=0).T))]; u=np.linspace(0,s[-1],N,endpoint=False)
    return np.c_[np.interp(u,s,Q[:,0]),np.interp(u,s,Q[:,1])]
def wire(P,x):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in P: mk.Add(gp_Pnt(x,y,z))
    mk.Close(); return mk.Wire()
vol=lambda s:(lambda g:(BRepGProp.VolumeProperties_s(s,g),g.Mass())[1])(GProp_GProps())
def mesh(shape):
    BRepMesh_IncrementalMesh(shape,0.05,False,0.3,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        fc=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(fc,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(fc.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,b_,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b_)-1,base+(b_ if rev else c)-1))
        ex.Next()
    return V,T
import re as _re
rd=STEPControl_Reader(); rd.ReadFile('rhino/RoyalCaroline_keel_solids_v4.step'); rd.TransferRoots(); ex=TopExp_Explorer(rd.OneShape(),TopAbs_SOLID); KS=[]
while ex.More(): KS.append(TopoDS.Solid(ex.Current())); ex.Next()
kn=_re.findall(r"PRODUCT\('([^']*)'",open('rhino/RoyalCaroline_keel_solids_v4.step',errors='ignore').read())[:18]; KEEL={}
for n,s in zip(kn,KS):
    t=gp_Trsf(); t.SetTranslation(gp_Vec(0,0,-SHIFT)); KEEL[n]=BRepBuilderAPI_Transform(s,t,True).Shape()
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; report=[]
for b,D in FR.items():
    xc=D['xc']; FPr={k:resample(v) for k,v in D['FP'].items()}
    sides=[('',1)] if b<=48 else [('_S',1),('_P',-1)]
    for suf,sg in sides:
        for lay,(ka,kb),(xa,xb) in (('A',('back','mid'),(xc-4,xc)),('F',('mid','front'),(xc,xc+4))):
            ts=BRepOffsetAPI_ThruSections(True,True); ts.AddWire(wire(FPr[ka]*[sg,1],xa)); ts.AddWire(wire(FPr[kb]*[sg,1],xb)); ts.Build(); sh=ts.Shape()
            v0=vol(sh); cl=[]
            for kn_,ks in KEEL.items():
                cm=BRepAlgoAPI_Common(sh,ks).Shape(); v=vol(cm) if not cm.IsNull() else 0
                if v>0.01: cl.append((kn_,round(v,1))); sh=BRepAlgoAPI_Cut(sh,ks).Shape()
            if b==48:
                TRn=json.load(open('data/stern_transom_outline_v2.json'))['transoms_normalized']
                for k_,hw in (('T2',37.8),('T3',12.7)):
                    mk=BRepBuilderAPI_MakePolygon()
                    for x_,z_ in TRn[k_]['poly']: mk.Add(gp_Pnt(x_,-hw,z_))
                    mk.Close()
                    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
                    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
                    pr=BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(0,2*hw,0)).Shape(); cn=vol(BRepAlgoAPI_Common(sh,pr).Shape()); sh=BRepAlgoAPI_Cut(sh,pr).Shape(); cl.append(('notch '+k_,round(cn,1)))
            report.append(('F%d%s_%s'%(b,suf,lay),round(v0),round(vol(sh)),cl,BRepCheck_Analyzer(sh).IsValid()))
            V,T=mesh(sh); mh=r3.Mesh()
            for v in V: mh.Vertices.Add(*v)
            for t in T: mh.Faces.AddFace(*t)
            mh.Normals.ComputeNormals(); l=r3.Layer(); l.Name='FRAME%d%s_%s_final'%(b,suf,lay); l.Color=(217,179,130,255); li=f.Layers.Add(l); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=l.Name; f.Objects.AddMesh(mh,a)
for x in report: print(x)
f.Write(S+'aft_rebuilt_frames.3dm',7)
