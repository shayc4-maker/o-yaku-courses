# assembly v2: v1 (keel group with pockets + 45 frames) + the stern of the previous round (transoms, wing transom, counter timbers, frames 46-48 from stern_assembly_v9) + the bow built from the 5 plane splines (HT1-HT10, 5 planks per side parallel to the centre plane); clash checks
import sys,re,json,numpy as np,time
from shapely.geometry import Polygon
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt,gp_Vec,gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace,BRepBuilderAPI_Transform
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepCheck import BRepCheck_Analyzer
import rhino3dm as r3
SHIFT=0.6
def vol(s): g=GProp_GProps(); BRepGProp.VolumeProperties_s(s,g); return g.Mass()
def mesh_of(shape,tol=0.04):
    BRepMesh_IncrementalMesh(shape,tol,False,0.35,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        fc=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(fc,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(fc.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((round(p.X(),3),round(p.Y(),3),round(p.Z(),3)))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return V,T
def solids_of(path):
    rd=STEPControl_Reader(); rd.ReadFile(path); rd.TransferRoots(); sh=rd.OneShape(); ex=TopExp_Explorer(sh,TopAbs_SOLID); out=[]
    while ex.More(): out.append(TopoDS.Solid(ex.Current())); ex.Next()
    return out
f1=r3.File3dm.Read('rhino/RoyalCaroline_keel_and_frames_assembly_v1.3dm'); print('v1 objects',len(f1.Objects))
CUTPARTS=('Boss-Extrude2[2]','Boss-Extrude3[3]','Boss-Extrude5[3]')
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LMAP={}
for i,l in enumerate(f1.Layers):
    if l.Name in ['KEEL_'+c for c in CUTPARTS]: continue
    n=r3.Layer(); n.Name=l.Name; n.Color=l.Color; LMAP[i]=f.Layers.Add(n)
for o in f1.Objects:
    if o.Attributes.LayerIndex in LMAP: a=o.Attributes; a.LayerIndex=LMAP[a.LayerIndex]; f.Objects.Add(o.Geometry,a)
print('copied objects',len(f.Objects))
def layer(n,col): l=r3.Layer(); l.Name=n; l.Color=col; return f.Layers.Add(l)
def add_mesh(li,name,shape):
    V,T=mesh_of(shape); m=r3.Mesh()
    for v in V: m.Vertices.Add(*v)
    for t in T: m.Faces.AddFace(*t)
    m.Normals.ComputeNormals(); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=name; f.Objects.AddMesh(m,a)
# keel group (lowered) for clash checks
kn=re.findall(r"PRODUCT\('([^']*)'",open('rhino/RoyalCaroline_keel_solids_v4.step',errors='ignore').read())[:18]; KEEL={}
for n,s in zip(kn,solids_of('rhino/RoyalCaroline_keel_solids_v4.step')):
    t=gp_Trsf(); t.SetTranslation(gp_Vec(0,0,-SHIFT)); KEEL[n]=BRepBuilderAPI_Transform(s,t,True).Shape()
# ---- stern from assembly v9: transoms, wing transom, counter timbers, frames 46-48 (indices 11,13..33); the aft backbone parts and the rudder are replaced by the new keel group
S9=solids_of('rhino/RoyalCaroline_stern_assembly_v9.step'); keep=[11]+list(range(13,34)); STERN={}
lab={11:'WING_TRANSOM',13:'COUNTER_TIMBER_1S',14:'COUNTER_TIMBER_1P',15:'COUNTER_TIMBER_2S',16:'COUNTER_TIMBER_2P',17:'COUNTER_TIMBER_3S',18:'COUNTER_TIMBER_3P',19:'TRANSOM_2',20:'TRANSOM_3',21:'TRANSOM_1_wing_piece'}
for i in keep:
    nm=lab.get(i); 
    if nm is None:
        fr={22:'F46_A_S',23:'F46_A_P',24:'F46_F_S',25:'F46_F_P',26:'F47_A_S',27:'F47_A_P',28:'F47_F_S',29:'F47_F_P',30:'F48_A_S',31:'F48_A_P',32:'F48_F_S',33:'F48_F_P'}; nm=fr[i]
    STERN[nm]=S9[i]
for nm,s in STERN.items(): add_mesh(layer('STERN_'+nm,(90,140,200,255)),nm,s)
print('stern solids added',len(STERN))
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
CUTLOG=[]
for cp in CUTPARTS:
    sh=KEEL[cp]; v0=vol(sh)
    for sn,ss in STERN.items():
        c=BRepAlgoAPI_Common(sh,ss).Shape(); v=vol(c) if not c.IsNull() else 0
        if v>0.2: sh=BRepAlgoAPI_Cut(sh,ss).Shape()
    KEEL[cp]=sh; CUTLOG.append((cp,round(v0,1),round(vol(sh),1),BRepCheck_Analyzer(sh).IsValid()))
    add_mesh(layer('KEEL_'+cp+' (cut by the stern parts)',(150,120,80,255)),cp,sh)
print('keel parts cut where the stern parts overlap (name, volume before, after, valid):',CUTLOG)
# ---- bow: HT planks from data/bow_ht_profiles_v3.pkl (previous-round rule on the new plane splines: head extension above the deck, cap X<=546, flat top)
import pickle
PRF=pickle.load(open('data/bow_ht_profiles_v3.pkl','rb')); HT={}
def prism_y(poly,y0,y1):
    mk=BRepBuilderAPI_MakePolygon()
    for x,z in poly[:-1]: mk.Add(gp_Pnt(x,y0,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(0,y1-y0,0)).Shape()
for k,pr in PRF.items():
    poly=np.array(pr['poly']); keep=[0]
    for i in range(1,len(poly)):
        if np.hypot(*(poly[i]-poly[keep[-1]]))>1e-6: keep.append(i)
    poly=poly[keep]; y0,y1=pr['y0'],pr['y1']
    for side in ('S','P'):
        ys=1 if side=='S' else -1; ht=(6-k) if side=='S' else (5+k); a_,b_=(y0,y1) if ys>0 else (-y1,-y0)
        HT['HT%d'%ht]=prism_y(poly,a_,b_)
    print('plank k=%d  Y %.2f..%.2f  area %.0f'%(k,y0,y1,pr['area']))
for nm,s in HT.items(): print('  %s valid %s volume %.0f'%(nm,BRepCheck_Analyzer(s).IsValid(),vol(s))); add_mesh(layer('BOW_'+nm,(200,170,90,255)),nm,s)
# ---- frames 1 and 45 solids (for the clash check against the bow/stern parts)
from OCP.gp import gp_Pnt as P3
def prism_x(poly,x0,x1):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in poly[:-1]: mk.Add(gp_Pnt(x0,y,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(x1-x0,0,0)).Shape()
FR={}
for part,bs in (('1_15',[1]),('31_45',[45])):
    D=np.load('/tmp/blank3_%s.npy'%part,allow_pickle=True).item()
    for b in bs:
        d=D[b]; xc=d['xc']; env=np.array(Polygon(d['env']).simplify(0.03).exterior.coords)
        FR['F%02d_A'%b]=prism_x(env,xc-4,xc); FR['F%02d_F'%b]=prism_x(env,xc,xc+4)
def clash(A,Bd,label):
    out=[]
    for an,a in A.items():
        for bn,bb in Bd.items():
            c=BRepAlgoAPI_Common(a,bb).Shape(); v=vol(c) if not c.IsNull() else 0
            if v>0.5: out.append((an,bn,round(v,1)))
    print(label,'overlaps >0.5 mm3:',out if out else 'none'); return out
clash(HT,KEEL,'bow HT vs keel group'); clash(HT,{k:v for k,v in FR.items() if k.startswith('F01')},'bow HT vs frame 1')
clash(STERN,KEEL,'stern vs keel group'); clash(STERN,{k:v for k,v in FR.items() if k.startswith('F45')},'stern vs frame 45'); clash(STERN,STERN,'stern internal') if False else None
f.Write('rhino/RoyalCaroline_keel_frames_stern_bow_assembly_v3.3dm',7)
import os; print('3dm %.1f MB'%(os.path.getsize('rhino/RoyalCaroline_keel_frames_stern_bow_assembly_v3.3dm')/1e6))
