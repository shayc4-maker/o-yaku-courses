import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from scipy.interpolate import UnivariateSpline
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
S=sys.argv[2]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
d=json.load(open(O+'/backbone_contour_v4.json')); V=Polygon(d['outer']).buffer(0)
T=np.array([(-5,76.7),(0,70.1),(4,66.4),(8,62.1),(12,58.0),(16,54.5),(20,51.8),(24,48.9),(28,46.5),(32,44.6)])   # band top (plan_5, classified cross band)
B=np.array([(-5,70.0),(0,64.0),(4,59.4),(8,55.4),(12,51.9),(16,49.2),(20,45.9),(24,43.7),(28,41.3),(32,39.7)])   # band bottom
st=UnivariateSpline(T[:,0],T[:,1],k=3,s=len(T)*0.08); sb=UnivariateSpline(B[:,0],B[:,1],k=3,s=len(B)*0.08)
xs=np.linspace(-5,32,150)
band=Polygon(np.r_[np.c_[xs,st(xs)],np.c_[xs[::-1],sb(xs[::-1])]]).buffer(0)
rem_top=Polygon(np.r_[np.c_[xs,st(xs)],[[32,300],[-5,300]]]).buffer(0)
seat=json.load(open(O+'/backbone_contour_v4.json'))['seat_points']
xg=np.linspace(29.3,32,30)
gap=Polygon(np.r_[np.c_[xg,np.interp(xg,[29.5,31.0],[15.9,15.2])],np.c_[xg[::-1],sb(xg[::-1])]]).buffer(0)
N=unary_union([V.difference(rem_top).difference(gap),band]).buffer(0.01).buffer(-0.01)
N=max(getattr(N,'geoms',[N]),key=lambda g:g.area); N=Polygon(N.exterior.coords).simplify(0.02)
print('area %.0f -> %.0f'%(V.area,N.area))
d['outer']=np.array(N.exterior.coords).tolist(); d['knee_top']=T.tolist(); d['knee_bottom']=B.tolist()
json.dump(d,open(O+'/backbone_contour_v4.json','w'))
from PIL import Image, ImageDraw
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); dr=ImageDraw.Draw(im)
e=np.array(N.exterior.coords); u,v=model_to_p5(e[:,0],e[:,1]); dr.line(list(zip(u,v)),fill=(0,160,0),width=3)
for nm,(xa,xb,za,zb,z) in {'aft':(-20,120,-12,85,1),'mid1':(110,300,-6,20,2),'mid2':(290,500,-6,30,2),'head':(540,612,65,125,1)}.items():
    u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb); c=im.crop((int(u0),int(v0),int(u1),int(v1)))
    if z>1: c=c.resize((c.size[0]*z,c.size[1]*z))
    c.save(PK+f'/qa/backbone_v4_{nm}.png')
u0,v1=model_to_p5(-25,-12); u1,v0=model_to_p5(615,135); im.crop((int(u0),int(v0),int(u1),int(v1))).save(PK+'/qa/backbone_v4_all.png')
import rhino3dm as r3, ezdxf
m=r3.File3dm.Read(PK+'/RoyalCaroline_backbone_contour_v4.3dm')
for o in m.Objects:
    if o.Attributes.Name=='backbone_contour_v4': m.Objects.Delete(o.Attributes.Id)
li=[i for i,l in enumerate(m.Layers) if l.Name=='BACKBONE_CONTOUR_v4'][0]
a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name='backbone_contour_v4'
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in e]),a)
m.Write(PK+'/RoyalCaroline_backbone_contour_v4.3dm',8)
dd=ezdxf.new('R2010'); dd.units=ezdxf.units.MM; dd.modelspace().add_lwpolyline([tuple(p) for p in e],close=True); dd.saveas(PK+'/RoyalCaroline_backbone_contour_v4.dxf')
