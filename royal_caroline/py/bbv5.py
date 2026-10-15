import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from scipy.interpolate import splprep, splev
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
S=sys.argv[2]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
d4=json.load(open(O+'/backbone_contour_v4.json')); V4=Polygon(d4['outer']).buffer(0)
fw=json.load(open(O+'/fwd_steps_plan5.json'))['blocks']
def sp(P,s,n=200):
    P=np.array(P,float); t,u=splprep(P.T,s=s,k=3); return np.array(splev(np.linspace(0,1,n),t)).T
# ---- aft line read from plan_5 (zooms zI/zJ) ----
FACE=[(-8.24,83.8),(-7.8,80),(-6.6,75.5),(-5.5,71.6),(-4.95,68.8),(-3.9,63),(-3.0,61.4),(-1.9,57.2),(-0.8,53.0)]
DW=[(5.4,53.0),(6.57,49.6),(8.01,46.4),(10.62,39.8),(12.36,35.7),(14.97,31.4),(18.1,26.0),(22.1,20.8),(25.9,18.0),(29.3,16.1),(32.7,14.1),(35.0,12.4)]
face=sp(FACE,0.6,60); face[0]=FACE[0]; face[-1]=FACE[-1]
dw=sp(DW,0.6,160); dw[0]=DW[0]
XJ=35.0
# v4 seat line at XJ (join)
def first_top(P,x):
    g=P.intersection(LineString([(x,-9.0),(x,300)]))
    gs=sorted(getattr(g,'geoms',[g]),key=lambda s:s.bounds[1]); return gs[0].bounds[3]
zj=first_top(V4,XJ); dw=dw[dw[:,0]<XJ-0.05]
for k in range(len(dw)):
    if dw[k,0]>31: w=(dw[k,0]-31)/(XJ-31); dw[k,1]=(1-w)*dw[k,1]+w*first_top(V4,dw[k,0])
dw=np.r_[dw,[(XJ,zj)]]
aft_line=np.r_[[(-16.0,83.8)],face,dw]
cutter=Polygon(np.r_[[(-40,83.8)],aft_line,[(XJ,300),(-40,300)]]).buffer(0)
fill=Polygon(np.r_[aft_line,[(XJ,-9.37),(0.2,-9.37)]]).buffer(0)
N=unary_union([V4.difference(cutter),fill]).buffer(0.005).buffer(-0.005)
N=max(getattr(N,'geoms',[N]),key=lambda g:g.area)
# ---- one horizontal seat per frame (flat at the plan block-bottom level) ----
blocks=[tuple(b) for b in d4['blocks']]+[(fw[k][0],fw[k][1]) for k in (5,6,7)]
seats=[]
for i,(a,b) in enumerate(blocks):
    c=(a+b)/2
    if i>=len(d4['blocks']): z0=fw[5+i-len(d4['blocks'])][2]
    elif i==len(d4['blocks'])-1: z0=fw[4][2]
    else: z0=first_top(N,c)
    zs=[first_top(N,x) for x in np.linspace(a+0.02,b-0.02,15)]
    N=N.difference(box(a,z0,b,max(zs)+0.02)).union(box(a,z0-3,b,z0) if min(zs)<z0 else Polygon())
    seats.append((a,b,z0,max(zs)-min(zs)))
N=N.buffer(0.005).buffer(-0.005); N=max(getattr(N,'geoms',[N]),key=lambda g:g.area)
N=Polygon(N.exterior.coords).simplify(0.03)
print('area v4 %.0f -> v5 %.0f  verts %d'%(V4.area,N.area,len(N.exterior.coords)))
for i,(a,b,z0,r) in enumerate(seats): print('F%d %.1f-%.1f seat %.2f rise %.2f'%(i+1 if i<42 else i+1,a,b,z0,r))
json.dump({'outer':np.array(N.exterior.coords).tolist(),'seats':seats,'post_face':FACE,'deadwood_curve':DW},open(O+'/backbone_contour_v5.json','w'))
# ---- outputs ----
from PIL import Image, ImageDraw
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); dr=ImageDraw.Draw(im)
e=np.array(N.exterior.coords); u,v=model_to_p5(e[:,0],e[:,1]); dr.line(list(zip(u,v)),fill=(0,160,0),width=3)
for nm,(xa,xb,za,zb,z) in {'aft':(-20,70,-12,90,2),'aft_frames':(25,140,-10,25,3),'mid1':(110,300,-6,20,2),'mid2':(290,500,-6,30,2),'fwd':(480,560,-10,50,2),'head':(540,612,65,125,1)}.items():
    u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb); c=im.crop((int(u0),int(v0),int(u1),int(v1)))
    if z>1: c=c.resize((c.size[0]*z,c.size[1]*z))
    c.save(PK+f'/qa/backbone_v5_{nm}.png')
u0,v1=model_to_p5(-25,-12); u1,v0=model_to_p5(615,135); im.crop((int(u0),int(v0),int(u1),int(v1))).save(PK+'/qa/backbone_v5_all.png')
import rhino3dm as r3, ezdxf
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n,c): L_=r3.Layer(); L_.Name=n; L_.Color=(*c,255); return m.Layers.Add(L_)
def att(li,n): a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=n; return a
l5=lay('BACKBONE_CONTOUR_v5',(0,150,0)); l4=lay('BACKBONE_CONTOUR_v4_old',(200,0,0)); lb=lay('REF_frame_seats',(255,140,0))
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in e]),att(l5,'backbone_contour_v5'))
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in V4.exterior.coords]),att(l4,'backbone_contour_v4'))
for i,(a,b,z0,r) in enumerate(seats):
    m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(a,0,z0),r3.Point3d(b,0,z0)]),att(lb,'seat_F%d'%(i+1)))
m.Write(PK+'/RoyalCaroline_backbone_contour_v5.3dm',8)
dd=ezdxf.new('R2010'); dd.units=ezdxf.units.MM; dd.modelspace().add_lwpolyline([tuple(p) for p in e],close=True); dd.saveas(PK+'/RoyalCaroline_backbone_contour_v5.dxf')
