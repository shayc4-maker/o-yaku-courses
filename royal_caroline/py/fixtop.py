import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from scipy.interpolate import PchipInterpolator
S=sys.argv[2]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
C=Polygon(json.load(open(O+'/backbone_contour_v2.json'))['outer']).buffer(0)
# stem head read from plan_5 (1 mm grid, 3x zoom)
aft=np.array([(551.8,70),(553.0,75),(554.0,80),(554.8,84),(555.3,89),(555.8,95),(556.2,100),(556.6,106),(556.9,111.9)])
rgt=np.array([(567.8,116.6),(567.0,110),(566.2,100),(565.7,89),(564.8,83.5),(564.2,83.0)])
fa=PchipInterpolator(aft[:,1],aft[:,0]); za=np.linspace(70,111.9,60)
stem=Polygon(np.r_[np.c_[fa(za),za],rgt,[(560.0,70.0)]]).buffer(0)
# bowsprit underside: cut above the line through the stem top corners
p0,p1=np.array([556.9,111.9]),np.array([567.8,116.6]); k=(p1[1]-p0[1])/(p1[0]-p0[0])
above=Polygon([(548,p0[1]+k*(548-p0[0])),(572,p0[1]+k*(572-p0[0])),(572,200),(548,200)])
# head top arc
arc=np.array([(589.8,99.9),(590.7,103.4),(591.5,104.5),(592.8,104.9),(595.7,105.8),(600.0,106.3),(603.6,105.4),(606.2,103.6),(607.6,101.3),(608.1,97.7)])
head=Polygon(np.r_[arc,[(605,94),(592,94)]]).buffer(0)
headcut=Polygon(np.r_[arc,[(612,97.7),(612,130),(585,130),(585,99.9)]]).buffer(0)
N=unary_union([C,stem]).difference(above)
N=unary_union([N.difference(headcut),head]).buffer(0.02).buffer(-0.02)
N=max(getattr(N,'geoms',[N]),key=lambda g:g.area); N=Polygon(N.exterior.coords)
print('holes',len(N.interiors),'area %.0f -> %.0f'%(C.area,N.area))
d=json.load(open(O+'/backbone_contour_v2.json')); d['outer']=np.array(N.exterior.coords).tolist(); json.dump(d,open(O+'/backbone_contour_v3.json','w'))
from PIL import Image, ImageDraw
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); dr=ImageDraw.Draw(im)
e=np.array(N.exterior.coords); u,v=model_to_p5(e[:,0],e[:,1]); dr.line(list(zip(u,v)),fill=(0,160,0),width=4)
for nm,(xa,xb,za,zb) in {'head':(540,612,65,125),'all':(425,612,-12,125)}.items():
    u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb); im.crop((int(u0),int(v0),int(u1),int(v1))).save(PK+f'/qa/bow_backbone_v3_{nm}.png')
import rhino3dm as r3, ezdxf
m=r3.File3dm.Read(PK+'/RoyalCaroline_backbone_contour_v2.3dm')
L=r3.Layer(); L.Name='BACKBONE_CONTOUR_v3'; L.Color=(0,90,200,255); li=m.Layers.Add(L)
a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name='backbone_contour_v3'
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in e]),a)
m.Write(PK+'/RoyalCaroline_backbone_contour_v3.3dm',8)
dd=ezdxf.new('R2010'); dd.units=ezdxf.units.MM; dd.modelspace().add_lwpolyline([tuple(p) for p in e],close=True); dd.saveas(PK+'/RoyalCaroline_backbone_contour_v3.dxf')
