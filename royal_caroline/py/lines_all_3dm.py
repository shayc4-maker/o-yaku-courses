# Rhino file with ALL existing approved lines in space (for checking): body plan stations 1-18 (+Y and mirror), approved station end hooks 1-8, waterlines I-VII (top view), rabbet (calibrated upper line, Y=0), side line D (Y=0, plan coords calibrated), backbone solids for reference. No frames, no solids built from lines.
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep
C=json.load(open('data/bodyplan_splines_v1.json')); W=json.load(open('data/wl_top_points_all.json')); ENDS=json.load(open('data/bodyplan_ends_proposed_v1.json'))
RB=json.load(open('data/rabbet_points_v2_calibrated.json'))['points']; SD=json.load(open('data/sideD_points.json')); cal=json.load(open('data/plan_calibration_v2.json'))['sheer_1a']
ax_,bx_,cx_=cal['dX']; az,bz,cz=cal['dZ']; ink=lambda X,Z:(X+ax_+bx_*(X-270)+cx_*Z, Z+az+bz*(X-270)+cz*Z)
def model(Xi,Zi):
    X,Z=Xi,Zi
    for _ in range(4): xi,zi=ink(X,Z); X,Z=X-(xi-Xi),Z-(zi-Zi)
    return X,Z
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Visible=vis; l.Color=col; LI[n]=f.Layers.Add(l); return LI[n]
def add(g,ln,name):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(g,a)
def spline3d(pts2,mapper):
    q=np.array(pts2,float); keep=[0]+[i for i in range(1,len(q)) if np.hypot(*(q[i]-q[i-1]))>1e-6]; q=q[keep]; tck,u=splprep(q.T,k=3,s=0); t,c,k=tck
    P=[r3.Point3d(*mapper(c[0][i],c[1][i])) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,3,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
STR={1:2,2:2}
lS=layer('STATIONS_bodyplan_approved_+Y',(220,0,0,255)); lSm=layer('STATIONS_bodyplan_approved_-Y',(220,120,120,255)); lE=layer('STATION_END_hooks_1-8_approved',(0,160,0,255)); lW=layer('WATERLINES_I-VII_+Y',(230,120,0,255)); lWm=layer('WATERLINES_I-VII_-Y',(240,180,110,255))
lR=layer('RABBET_upper_calibrated_Y0',(0,0,0,255)); lRp=layer('RABBET_points_calibrated',(0,0,0,255),False); lD=layer('SIDE_LINE_D_Y0_calibrated',(0,90,200,255)); lPS=layer('POINTS_stations',(120,0,0,255),False); lPW=layer('POINTS_waterlines',(160,90,0,255),False)
for n in range(1,19):
    P=C[str(n)]['points']; k=STR.get(n,0); q=P[:-1] if k else P; X=XST[n]
    for sg,ly in ((1,lS),(-1,lSm)):
        add(spline3d(q,lambda y,z:(X,sg*y,z)),ly,f'ST{n:02d}')
        if k: add(r3.LineCurve(r3.Point3d(X,sg*P[-2][0],P[-2][1]),r3.Point3d(X,sg*P[-1][0],P[-1][1])),ly,f'ST{n:02d}_straight_top')
        if str(n) in ENDS:
            e=ENDS[str(n)]; add(r3.LineCurve(r3.Point3d(X,sg*e['end'][0],e['end'][1]),r3.Point3d(X,sg*P[0][0],P[0][1])),lE,f'ST{n:02d}_end_hook')
    pa=r3.ObjectAttributes(); pa.LayerIndex=lPS; pa.Name=f'ST{n:02d}_pt'
    for y,z in P: f.Objects.AddPoint(r3.Point3d(X,y,z),pa)
for k,v in W.items():
    Z=v['z']; P=v['points_XY']
    for sg,ly in ((1,lW),(-1,lWm)): add(spline3d(P,lambda x,y:(x,sg*y,Z)),ly,f'WL_{k}')
    pa=r3.ObjectAttributes(); pa.LayerIndex=lPW; pa.Name=f'WL_{k}_pt'
    for x,y in P: f.Objects.AddPoint(r3.Point3d(x,y,Z),pa)
add(spline3d(RB,lambda x,z:(x,0.0,z)),lR,'RABBET_upper')
pa=r3.ObjectAttributes(); pa.LayerIndex=lRp; pa.Name='RABBET_pt'
for x,z in RB: f.Objects.AddPoint(r3.Point3d(x,0.0,z),pa)
for nm in ('top_edge','bottom_edge'):
    pts=[model(x,z) for x,z in SD[nm]]; add(r3.PolylineCurve([r3.Point3d(x,0.0,z) for x,z in pts]),lD,'D_'+nm)
add(r3.LineCurve(r3.Point3d(*model(*SD['top_edge'][0])[:1],0.0,model(*SD['top_edge'][0])[1]),r3.Point3d(model(*SD['bottom_edge'][0])[0],0.0,model(*SD['bottom_edge'][0])[1])),lD,'D_end_left')
b=r3.File3dm.Read('rhino/RoyalCaroline_backbone_solids_v1.3dm'); BL={i:b.Layers[i].Name for i in range(len(b.Layers))}
for ob in b.Objects:
    if ob.Geometry.ObjectType.name!='Brep': continue
    add(ob.Geometry.Duplicate(),layer('BACKBONE_'+BL[ob.Attributes.LayerIndex],(150,150,150,255)),BL[ob.Attributes.LayerIndex])
f.Write('rhino/RoyalCaroline_all_approved_lines_v1.3dm',7); print('objects',len(f.Objects),'layers',len(f.Layers))
