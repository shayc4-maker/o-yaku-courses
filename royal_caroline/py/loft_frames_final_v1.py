# final (sanded) frames: ruled loft between the final face polygons of each layer (A: back->mid, F: mid->front); no sanding allowance
import sys,glob,numpy as np,rhino3dm as r3
from OCP.gp import gp_Pnt
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.BRepCheck import BRepCheck_Analyzer
S='/tmp/claude-0/-home-user-o-yaku-courses/db230f8a-8640-51de-bf4e-53423595c88f/scratchpad/'
D={}
for f in glob.glob(S+'blank_*.npy'): D.update({str(k):v for k,v in np.load(f,allow_pickle=True).item().items()})
D.update({str(k):v for k,v in np.load(S+'aft_blank_v5.npy',allow_pickle=True).item().items()})
print('frame keys',len(D))
N=240
def resample(P):
    P=np.asarray(P,float)
    if np.allclose(P[0],P[-1]): P=P[:-1]
    a=0.5*np.sum(P[:,0]*np.roll(P[:,1],-1)-np.roll(P[:,0],-1)*P[:,1])
    if a<0: P=P[::-1]
    c=P.mean(0); m=P[:,0]<=c[0]; i=int(np.argmin(np.where(m,P[:,1],1e9)))      # start: lowest vertex on the -Y side
    P=np.roll(P,-i,axis=0); Q=np.vstack([P,P[0]]); s=np.r_[0,np.cumsum(np.hypot(*np.diff(Q,axis=0).T))]; u=np.linspace(0,s[-1],N,endpoint=False)
    return np.c_[np.interp(u,s,Q[:,0]),np.interp(u,s,Q[:,1])]
def wire(P,x):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in P: mk.Add(gp_Pnt(x,y,z))
    mk.Close(); return mk.Wire()
def mesh(shape):
    BRepMesh_IncrementalMesh(shape,0.05,False,0.3,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        fc=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(fc,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(fc.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return V,T
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; bad=[]
for key in sorted(D,key=lambda k:(int(k.split('_')[0]),k)):
    d=D[key]; xc=d['xc']; FP={k:resample(v) for k,v in d['FP'].items()}
    for lay,(ka,kb),(xa,xb) in (('A',('back','mid'),(xc-4,xc)),('F',('mid','front'),(xc,xc+4))):
        ts=BRepOffsetAPI_ThruSections(True,True); ts.AddWire(wire(FP[ka],xa)); ts.AddWire(wire(FP[kb],xb)); ts.Build(); sh=ts.Shape()
        ok=BRepCheck_Analyzer(sh).IsValid()
        if not ok: bad.append((key,lay))
        V,T=mesh(sh); m=r3.Mesh()
        for v in V: m.Vertices.Add(*v)
        for t in T: m.Faces.AddFace(*t)
        m.Normals.ComputeNormals(); l=r3.Layer(); l.Name='FRAME%s_%s_final'%(key,lay); l.Color=(217,179,130,255); li=f.Layers.Add(l); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=l.Name; f.Objects.AddMesh(m,a)
f.Write(S+'frames_final_lofts.3dm',7); print('written',len(f.Objects),'invalid',bad)
