import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from scipy.interpolate import UnivariateSpline
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
S=sys.argv[2]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
V3=Polygon(json.load(open(O+'/backbone_contour_v3.json'))['outer']).buffer(0)
auto={d['frame']:d for d in json.load(open(O+'/seats_auto.json'))}
fx=json.load(open(O+'/frames_X.json'))['X_mm']
fw=json.load(open(O+'/fwd_steps_plan5.json'))['blocks']
XS,XA=29.3,496.8
# ---- notch blocks (plan_5 extents) ----
blocks=[]
for i in range(1,43):
    if i==1: blocks.append((36.9,40.8)); continue
    if i==25: blocks.append((fx[24]-2.6,fx[24]+2.6)); continue      # added frame (not drawn): model position
    if i==42: blocks.append((fw[4][0],fw[4][1])); continue
    a=auto[i]
    if 'bx0' not in a or a['zb']>15 and i>20: blocks.append((fx[i-1]-2.7,fx[i-1]+2.7)); continue
    c=(a['bx0']+a['bx1'])/2; blocks.append((c-2.7,c+2.7))
# ---- seat curve: block bottoms (plan_5) ----
pts=[(29.5,15.9),(31.0,15.2),(38.9,10.2)]
for i in range(2,42):
    a=auto.get(i,{})
    if 'zb' in a and not (i in (30,31)) and a['zb']<12 or (i<7 and 'zb' in a): pts.append(((a['bx0']+a['bx1'])/2,a['zb']))
pts+=[((fw[k][0]+fw[k][1])/2,fw[k][2]) for k in (4,5,6,7)]
P=np.array(sorted(pts)); w=np.ones(len(P)); w[:3]=3; w[-4:]=3
seat=UnivariateSpline(P[:,0],P[:,1],w=w,k=3,s=len(P)*0.04)
res=P[:,1]-seat(P[:,0]); print('seat fit rms %.2f max %.2f'%(np.sqrt((res**2).mean()),abs(res).max()))
def depth(x): return float(np.clip((x-75)/(106-75),0,1)*1.1)
# ---- stepped line ----
xs=np.arange(XS,XA+1e-6,0.1); line=[]
def innotch(x): return any(a<=x<=b for a,b in blocks)
for x in xs: line.append((x,float(seat(x))+(0 if innotch(x) else depth(x))))
L=np.array(line)
# make steps exactly vertical at block edges
out=[tuple(L[0])]
for k in range(1,len(L)):
    if abs(L[k,1]-L[k-1,1])>0.05: out.append((L[k,0],L[k-1,1]))
    out.append(tuple(L[k]))
L=np.array(out)
lower=Polygon(np.r_[L,[[XA,-9.37],[XS,-9.37]]]).buffer(0)
# knee bottom (cut white gap 29.3-32 under the knee)
knee=[p for p in json.load(open(O+'/parts_v10.json')) if p['name']=='STERN_KNEE'][0]
K=Polygon(knee['poly']).buffer(0)
def kbot(x):
    g=K.intersection(LineString([(x,-50),(x,300)])); return g.bounds[1] if not g.is_empty else 300
top=[(x,kbot(x)) for x in np.arange(XS,32.01,0.1)]+[(32.0,300),(XA,300)]
cut=Polygon(np.r_[L,top[::-1] and np.array([[XA,300]]+[t for t in top[::-1]])]).buffer(0)
N=unary_union([V3.difference(cut),lower.intersection(box(XS,-20,XA,300))])
N=N.buffer(0.01).buffer(-0.01); N=max(getattr(N,'geoms',[N]),key=lambda g:g.area); N=Polygon(N.exterior.coords)
# ---- local smoothing of two kinks (head join ~X590,Z101 ; stem aft face ~X554.7,Z84) ----
E=np.array(N.exterior.coords); seg=np.hypot(*np.diff(E,axis=0).T); u=np.r_[0,np.cumsum(seg)]
uu=np.arange(0,u[-1],0.1); R=np.c_[np.interp(uu,u,E[:,0]),np.interp(uu,u,E[:,1])]
Sm=np.c_[gaussian_filter1d(R[:,0],8,mode='wrap'),gaussian_filter1d(R[:,1],8,mode='wrap')]
for cx,cz,r in ((590.3,101.5,3.5),(554.7,84.2,3.0)):
    d=np.hypot(R[:,0]-cx,R[:,1]-cz); wgt=np.clip(1-d/r,0,1)[:,None]
    R=R*(1-wgt)+Sm*wgt
# thin back to keep vertices on straight runs
N2=Polygon(R).buffer(0).simplify(0.02)
print('area v3 %.0f -> v4 %.0f, vertices %d'%(V3.area,N2.area,len(N2.exterior.coords)))
json.dump({'outer':np.array(N2.exterior.coords).tolist(),'seat_points':P.tolist(),'blocks':blocks},open(O+'/backbone_contour_v4.json','w'))
# ---- outputs ----
from PIL import Image, ImageDraw
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); dr=ImageDraw.Draw(im)
e=np.array(N2.exterior.coords); uu_,vv=model_to_p5(e[:,0],e[:,1]); dr.line(list(zip(uu_,vv)),fill=(0,160,0),width=3)
for nm,(xa,xb,za,zb,z) in {'aft':(-20,120,-12,85,1),'mid1':(110,300,-6,20,2),'mid2':(290,500,-6,30,2),'head':(540,612,65,125,1)}.items():
    u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb); c=im.crop((int(u0),int(v0),int(u1),int(v1)))
    if z>1: c=c.resize((c.size[0]*z,c.size[1]*z))
    c.save(PK+f'/qa/backbone_v4_{nm}.png')
u0,v1=model_to_p5(-25,-12); u1,v0=model_to_p5(615,135); im.crop((int(u0),int(v0),int(u1),int(v1))).save(PK+'/qa/backbone_v4_all.png')
import rhino3dm as r3, ezdxf
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n,c): L_=r3.Layer(); L_.Name=n; L_.Color=(*c,255); return m.Layers.Add(L_)
def att(li,n): a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=n; return a
l4=lay('BACKBONE_CONTOUR_v4',(0,150,0)); l3=lay('BACKBONE_CONTOUR_v3_old',(200,0,0)); lb=lay('REF_plan5_frame_blocks',(255,140,0))
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in e]),att(l4,'backbone_contour_v4'))
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in V3.exterior.coords]),att(l3,'backbone_contour_v3'))
for a,b in blocks:
    zb=float(seat((a+b)/2)); m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(a,0,zb),r3.Point3d(b,0,zb)]),att(lb,'plan5_block'))
m.Write(PK+'/RoyalCaroline_backbone_contour_v4.3dm',8)
dd=ezdxf.new('R2010'); dd.units=ezdxf.units.MM; dd.modelspace().add_lwpolyline([tuple(p) for p in e],close=True); dd.saveas(PK+'/RoyalCaroline_backbone_contour_v4.dxf')
