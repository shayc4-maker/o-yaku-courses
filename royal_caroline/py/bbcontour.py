import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
O=sys.argv[2]+'/out'
parts=json.load(open(O+'/parts_v10.json')); fp=json.load(open(O+'/frame_parts.json'))['parts']
bb=[p for p in parts if p['group']=='backbone' and not p['name'].startswith('KEELSON') and p['plane']=='XZ']
print(sorted(p['name'] for p in bb))
U=unary_union([Polygon(p['poly']).buffer(0) for p in bb])
fill=[box(p['x0']-0.06,p['joint'][0]-0.01,p['x1']+0.06,p['joint'][0]+1.01) for p in fp]
U=unary_union([U]+[f for f in fill if f.intersects(U.buffer(0.05))]).buffer(0.05).buffer(-0.05)
geoms=sorted(getattr(U,'geoms',[U]),key=lambda g:-g.area)
print('pieces in union',len(geoms),[round(g.area,1) for g in geoms[:5]],'holes',[len(g.interiors) for g in geoms[:3]])
C=geoms[0]; ext=np.array(C.exterior.coords)
json.dump({'outer':ext.tolist(),'holes':[np.array(h.coords).tolist() for h in C.interiors]},open(O+'/backbone_contour.json','w'))
# 3dm + dxf
import rhino3dm as r3, ezdxf
PK=O+'/RoyalCaroline_Rhino'
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
L=r3.Layer(); L.Name='BACKBONE_CONTOUR'; L.Color=(200,0,0,255); li=m.Layers.Add(L)
a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name='backbone_outer_contour'
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in ext]),a)
for h in C.interiors:
    m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in h.coords]),a)
m.Write(PK+'/RoyalCaroline_backbone_contour_v1.3dm',8)
d=ezdxf.new('R2010'); d.units=ezdxf.units.MM; d.modelspace().add_lwpolyline([tuple(p) for p in ext],close=True)
d.saveas(PK+'/RoyalCaroline_backbone_contour_v1.dxf')
# overlays
from PIL import Image, ImageDraw
S=sys.argv[2]
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:120+t*135//255); dr=ImageDraw.Draw(im)
u,v=model_to_p5(ext[:,0],ext[:,1]); dr.line(list(zip(u,v)),fill=(255,0,0),width=4)
u0,v1=model_to_p5(-25,-14); u1,v0=model_to_p5(615,135)
im.crop((int(u0),int(v0),int(u1),int(v1))).save(PK+'/qa/backbone_contour_on_plan5.png')
for nm,(xa,xb,za,zb) in {'stern':(-25,110,-14,135),'bow':(440,615,-14,125)}.items():
    u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb)
    im.crop((int(u0),int(v0),int(u1),int(v1))).save(PK+f'/qa/backbone_contour_on_plan5_{nm}.png')
K=1000/244.8/48
im=Image.open(S+'/a/plan_1a_aligned.png').convert('RGB').point(lambda t:120+t*135//255); dr=ImageDraw.Draw(im)
dr.line(list(zip(ext[:,0]/K+4194.98,2104.73-ext[:,1]*102.1/8.689)),fill=(255,0,0),width=4)
im.crop((int(-25/K+4194.98),int(2104.73-135*102.1/8.689),int(615/K+4194.98),int(2104.73+14*102.1/8.689))).save(PK+'/qa/backbone_contour_on_A1-1.png')
print('X %.1f..%.1f Z %.1f..%.1f'%(*C.bounds[0::2],*C.bounds[1::2]))
