# New lines file: GRID/LABELS layout of the builder's lines file + NEW station splines (approved body plan), NEW waterlines (approved top view), backbone for reference
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
ORIG='/root/.claude/uploads/9b1663d1-123c-5304-bded-1182034acdbc/1df4766f-RoyalCaroline_lines_1to48_v1.3dm'
C=json.load(open('data/bodyplan_splines_v1.json')); W=json.load(open('data/wl_top_points_all.json'))
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col=None,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Visible=vis
    if col: l.Color=col
    LI[n]=f.Layers.Add(l); return LI[n]
def nurbs(P3,tck):
    t,c,k=tck; P=[r3.Point3d(*p) for p in P3]; nc=r3.NurbsCurve.Create(False,3,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
def add(geom,ln,name):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(geom,a)
def spline3d(pts2,mapper):
    q=np.array(pts2); keep=[0]+[i for i in range(1,len(q)) if np.hypot(*(q[i]-q[i-1]))>1e-6]; q=q[keep]; tck,u=splprep(q.T,k=3,s=0); t,c,k=tck
    return nurbs([mapper(c[0][i],c[1][i]) for i in range(len(c[0]))],tck)
STR={1:2,2:2}
# original layout: GRID, LABELS
o=r3.File3dm.Read(ORIG); OL={i:o.Layers[i].Name for i in range(len(o.Layers))}
for ob in o.Objects:
    n=OL[ob.Attributes.LayerIndex]
    if n in ('GRID','LABELS'):
        add(ob.Geometry.Duplicate(),layer(n,(0,150,0,255) if n=='GRID' else (80,80,80,255)),ob.Attributes.Name or n)
ln3=layer('STATIONS_3D_bodyplan_NEW',(220,0,0,255)); ln3m=layer('STATIONS_3D_bodyplan_NEW_mirror',(220,120,120,255)); ln2=layer('BODYPLAN_2D_NEW_at_X-80',(0,0,220,255))
lw=layer('WATERLINES_NEW_from_plan',(230,120,0,255)); lwm=layer('WATERLINES_NEW_mirror',(240,180,110,255)); lpS=layer('POINTS_stations_approved',(120,0,0,255),False); lpW=layer('POINTS_waterlines_approved',(160,90,0,255),False)
for n in range(1,19):
    d=C[str(n)]; P=d['points']; k=STR.get(n,0); q=P[:-1] if k else P; X=XST[n]
    for sg,ly in ((1,ln3),(-1,ln3m)):
        add(spline3d(q,lambda y,z:(X,sg*y,z)),ly,f'ST{n:02d}')
        if k: add(r3.LineCurve(r3.Point3d(X,sg*P[-2][0],P[-2][1]),r3.Point3d(X,sg*P[-1][0],P[-1][1])),ly,f'ST{n:02d}_straight_top')
    # flat body plan at X=-80 (aft stations 9-18 at +Y, forward 1-8 at -Y, station 8 on both)
    sides=[]; 
    if n>=8: sides.append(1)
    if n<=8: sides.append(-1)
    for sg in sides:
        add(spline3d(q,lambda y,z:(-80.0,sg*y,z)),ln2,f'ST{n:02d}_2D')
        if k: add(r3.LineCurve(r3.Point3d(-80.0,sg*P[-2][0],P[-2][1]),r3.Point3d(-80.0,sg*P[-1][0],P[-1][1])),ln2,f'ST{n:02d}_2D_straight_top')
    pa=r3.ObjectAttributes(); pa.LayerIndex=lpS; pa.Name=f'ST{n:02d}_pt'
    for y,z in P: f.Objects.AddPoint(r3.Point3d(X,y,z),pa)
for k,v in W.items():
    Z=v['z']; P=v['points_XY']
    for sg,ly in ((1,lw),(-1,lwm)): add(spline3d(P,lambda x,y:(x,sg*y,Z)),ly,f'WL_{k}')
    pa=r3.ObjectAttributes(); pa.LayerIndex=lpW; pa.Name=f'WL_{k}_pt'
    for x,y in P: f.Objects.AddPoint(r3.Point3d(x,y,Z),pa)
# backbone for reference
b=r3.File3dm.Read('rhino/RoyalCaroline_backbone_solids_v1.3dm'); BL={i:b.Layers[i].Name for i in range(len(b.Layers))}
for ob in b.Objects:
    if ob.Geometry.ObjectType.name!='Brep': continue
    add(ob.Geometry.Duplicate(),layer('BACKBONE_'+BL[ob.Attributes.LayerIndex],(150,150,150,255)),BL[ob.Attributes.LayerIndex])
f.Write('rhino/RoyalCaroline_lines_v2.3dm',7); print('objects',len(f.Objects),'layers',len(f.Layers))
