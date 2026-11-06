# 3D frames 1-8 (blanks before sanding): per frame ONE common cut outline (union of the three face outlines X-4, X, X+4; arm rule v2: loft with approved station ends, lower end on the updated rabbet, no shift), layer A (X-4..X) and F (X..X+4) as 4 mm prisms, laser lines = the final face outlines on X-4, X, X+4. Output: Rhino 3dm (extrusions + laser lines + backbone reference), STEP, checks (validity, volumes, clash with the backbone STEP)
import sys,json,numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
A=json.load(open('data/frames_arm_v2_1_2_3_4_5_6_7_8.json'))
mir=lambda g: affinity.scale(g,xfact=-1,yfact=1,origin=(0,0))
def full(half):
    h=Polygon(half).buffer(0); g=unary_union([h.buffer(0.01),mir(h).buffer(0.01)]).buffer(-0.01)
    return max(g.geoms,key=lambda q:q.area) if hasattr(g,'geoms') else g
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs,STEPControl_Reader
from OCP.TopoDS import TopoDS_Compound
from OCP.BRep import BRep_Builder
def prism(poly,x0,x1):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in list(poly.exterior.coords)[:-1]: mk.Add(gp_Pnt(x0,y,z))
    mk.Close(); return BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(mk.Wire()).Face(),gp_Vec(x1-x0,0,0)).Shape()
def vol(s): p=GProp_GProps(); BRepGProp.VolumeProperties_s(s,p); return p.Mass()
blanks={}; solids={}; lines={}; rep=[]
for b in range(1,9):
    d=A[str(b)]; xc=d['X']; faces={k:full(v['half']) for k,v in d['faces'].items()}
    env=unary_union([g.buffer(0.01) for g in faces.values()]).buffer(-0.01); env=max(env.geoms,key=lambda q:q.area) if hasattr(env,'geoms') else env; env=Polygon(env.exterior).simplify(0.003)   # fill the slivers between the face outlines (frame 1 flares strongly across the 8 mm)
    blanks[b]=env
    xf=d.get('x_front',xc+4)
    for lay,(x0,x1) in (('A',(xc-4,xc)),('F',(xc,xf))):
        s=prism(env,x0,x1); solids['FRAME%02d_%s'%(b,lay)]=s; ok=BRepCheck_Analyzer(s).IsValid(); rep.append((b,lay,ok,vol(s),env.area*(x1-x0)))
    for k,X in (('back',xc-4),('mid',xc),('front',xf)): lines['LASER%02d_%s'%(b,k)]=(X,np.array(faces[{'back':'X-4','mid':'X','front':'X+4'}[k]].exterior.coords))
    print('frame %d: blank area %.0f mm2 (faces %s)'%(b,env.area,[round(g.area) for g in faces.values()]))
print('valid:',all(r[2] for r in rep),'| volume check (prism vs area*4): max diff %.4f mm3'%max(abs(r[3]-r[4]) for r in rep))
# clash with the backbone STEP and between neighbouring frames
rd=STEPControl_Reader(); rd.ReadFile('rhino/backbone_builder_44.STEP'); rd.TransferRoots(); bb=rd.OneShape(); print('backbone STEP volume %.0f mm3'%vol(bb))
tot=0.0; cl=[]
for k,s in solids.items():
    c=BRepAlgoAPI_Common(s,bb); v=vol(c.Shape()) if c.IsDone() else float('nan'); cl.append((k,v)); tot+=v
print('overlap of frame blanks with the backbone STEP (mm3):',[(k,round(v,1)) for k,v in cl if v>0.05])
nb=[]
for b in range(1,8):
    for l1,l2 in ((('A'),('F')),):
        pass
ks=sorted(solids); 
for i in range(len(ks)):
    for j in range(i+1,len(ks)):
        v=vol(BRepAlgoAPI_Common(solids[ks[i]],solids[ks[j]]).Shape())
        if v>0.01: nb.append((ks[i],ks[j],round(v,2)))
print('frame-frame overlaps:',nb[:10] if nb else 'none')
cmp_=TopoDS_Compound(); bld=BRep_Builder(); bld.MakeCompound(cmp_)
for s in solids.values(): bld.Add(cmp_,s)
w=STEPControl_Writer(); w.Transfer(cmp_,STEPControl_AsIs); w.Write('rhino/RoyalCaroline_frames1-8_blanks_v1.step')
json.dump(dict(blank_areas={b:blanks[b].area for b in blanks},backbone_overlap={k:v for k,v in cl}),open('data/frames1-8_blanks_v1.json','w'))
# Rhino
import rhino3dm as r3
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Visible=vis; l.Color=col; LI[n]=f.Layers.Add(l); return LI[n]
def add(g,ln,name):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; return f.Objects.Add(g,a)
lA=layer('FRAMES_1-8_A_(back 4mm)',(200,60,60,255)); lF=layer('FRAMES_1-8_F_(front 4mm)',(60,60,200,255)); lL=layer('LASER_final_faces',(0,0,0,255)); lB=layer('BACKBONE_STEP_reference',(150,150,150,255)); lR=layer('RABBET_new',(0,0,0,255))
bad=0
for b,env in blanks.items():
    xc=A[str(b)]['X']
    xf=A[str(b)].get('x_front',xc+4)
    for lay,(x0,x1),ly in (('A',(xc-4,xc),lA),('F',(xc,xf),lF)):
        pts=[r3.Point3d(x0,y,z) for y,z in list(env.exterior.coords)]; cur=r3.PolylineCurve(pts)
        ex=r3.Extrusion.Create(cur,float(x1-x0),True)
        if ex is None: bad+=1; continue
        add(ex,ly,'FRAME%02d_%s'%(b,lay))
for nm,(X,r) in lines.items(): add(r3.PolylineCurve([r3.Point3d(X,y,z) for y,z in r]),lL,nm)
bf=r3.File3dm.Read('rhino/RoyalCaroline_backbone_solids_v1.3dm')
for ob in bf.Objects:
    if ob.Geometry.ObjectType.name=='Brep': add(ob.Geometry.Duplicate(),lB,'BB')
_rb=json.load(open('data/rabbet_points_v3_ends.json'))['points']
from scipy.interpolate import splprep
q=np.array(_rb,float); tck,u=splprep(q.T,k=3,s=0); t,c,k=tck; P=[r3.Point3d(c[0][i],0.0,c[1][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,3,P)
for i in range(len(nc.Knots)): nc.Knots[i]=float(t[1:-1][i])
add(nc,lR,'RABBET_new')
f.Write('rhino/RoyalCaroline_frames1-8_blanks_v1.3dm',7); print('3dm objects',len(f.Objects),'extrusion failures',bad)
