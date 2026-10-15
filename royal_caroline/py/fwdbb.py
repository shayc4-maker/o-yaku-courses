import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from scipy.interpolate import PchipInterpolator, UnivariateSpline
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
S=sys.argv[2]; O=S+'/out'
d=json.load(open(O+'/fwd_steps_plan5.json')); B=d['blocks']; G=d['gaps']
fc=[(b[0]+b[1])/2 for b in B]
gx=[440.3]+[(B[k-1][1]+B[k][0])/2 for k in range(1,len(B))]; gz=[4.7]+[g[0] for g in G[1:]]
gt=[(B[k-1][1]+B[k][0])/2 for k in range(1,len(B))]; gtz=[g[1] for g in G[1:]]
# smooth curves (plan_5 spline character)
Sgap=PchipInterpolator(np.r_[[420,430],gx],np.r_[[4.6,4.6],gz])                     # deadwood top between frames
Sfb =PchipInterpolator(np.r_[[420,430],fc],np.r_[[3.0,3.1],[b[2] for b in B]])      # notch bottoms
tp=sorted([((b[0]+b[1])/2,b[3]) for b in B[4:]]+[(gt[k-1],G[k][1]) for k in range(5,len(B))])
tp=np.array(tp); cf=np.polyfit(tp[:,0],tp[:,1],2); Stop=lambda x: np.polyval(cf,x)          # apron underside (frame + gap tops)
ceil=np.array(d['ceiling']); Sceil=PchipInterpolator(ceil[:,0],ceil[:,1],extrapolate=True)
L=json.load(open(O+'/bowlines_raw.json')); l5=np.array(L[5]['pts']); l5=l5[np.argsort(l5[:,1])]; l13=np.array(L[13]['pts']); l13=l13[np.argsort(l13[:,1])]
def ln(xa,xb,f,n=None):
    xs=np.linspace(xa,xb,max(3,int((xb-xa)/0.25))); return [(x,float(f(x))) for x in xs]
# stepped inner line (deadwood top with notches), smooth segments
step=[]; X0=430.0
step+=ln(X0,B[0][0],Sgap)
for k,(x0,x1,zb,zt) in enumerate(B):
    step+=[(x0,float(Sgap(x0)))]; step+=ln(x0,x1,Sfb)
    nxt=B[k+1][0] if k+1<len(B) else None
    if nxt: step+=[(x1,float(Sgap(x1)))]+ln(x1,nxt,Sgap)
    else: step+=[(x1,float(Stop(x1)))]
XA=496.8   # aft end of apron (assumed: middle of gap 42-43, where keelson meets apron in plan_5)
x45=B[-1][1]
# removal regions
rem=[]
rem.append(Polygon(step+[(x45,float(Stop(x45))),(x45,200),(X0,200)]).buffer(0).intersection(box(X0,-50,XA+0.15,200)))
chan=ln(XA,x45,lambda x: Stop(x)) ; chan=chan[::-1]
stepA=[p for p in step if p[0]>=XA]
rem.append(Polygon(stepA+[(x45,float(Stop(x45)))]+chan).buffer(0))
# above the ceiling/stem-inner line
# stem inner face, read from plan_5 at 1 mm grid (4x zoom); joins l13 above Z 84
STEMIN=[(543.0,50.0),(546.0,55.0),(548.0,60.0),(550.5,65.0),(551.8,70.0),(553.0,75.0),(554.0,80.0),(554.8,84.0)]
up=ln(XA,ceil[-1,0],Sceil)+STEMIN+[tuple(p) for p in l13[l13[:,1]>84.2]]
up=np.array(up); rem.append(Polygon(np.r_[up,[[up[-1,0],300],[XA,300],[XA,float(Sceil(XA))]]]).buffer(0))
rem.append(box(X0-1,float(Stop(XA)),XA+0.15,300))      # keelson zone aft of apron (excluded part)
REM=unary_union(rem)
cur=Polygon(json.load(open(O+'/backbone_contour.json'))['outer']).buffer(0)
pr=json.load(open(O+'/profile1a.json')); rf=np.array(pr['stem_rabbet_fwd']); rf=rf[np.argsort(rf[:,1])]; rf=rf[rf[:,1]>-9.3]
LEFT=Polygon([(X0,-9.37)]+[tuple(p) for p in rf]+[(rf[-1,0],200),(X0,200)]).buffer(0)
fill=box(X0,-9.37,700,200).intersection(LEFT)
fwd=unary_union([cur.intersection(box(X0,-50,700,300)),fill]).difference(REM)
aft=cur.intersection(box(-100,-50,X0,300))
NEW=unary_union([aft,fwd]).buffer(0.02).buffer(-0.02)
NEW=max(getattr(NEW,'geoms',[NEW]),key=lambda g:g.area); NEW=Polygon(NEW.exterior.coords)   # drop internal slivers between old pieces
print('area old %.0f new %.0f  holes %d'%(cur.area,NEW.area,len(NEW.interiors)))
json.dump({'outer':np.array(NEW.exterior.coords).tolist(),'holes':[np.array(h.coords).tolist() for h in NEW.interiors],
           'curves':{'deadwood_top':[(float(x),float(Sgap(x))) for x in np.arange(430,527,0.5)],'notch_bottom':[(float(x),float(Sfb(x))) for x in np.arange(430,527,0.5)],
                     'apron_underside':[(float(x),float(Stop(x))) for x in np.arange(XA,x45+0.01,0.5)]}},open(O+'/backbone_contour_v2.json','w'))
from PIL import Image, ImageDraw
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); dr=ImageDraw.Draw(im)
def Ld(pts,col,w):
    pts=np.array(pts); u,v=model_to_p5(pts[:,0],pts[:,1]); dr.line(list(zip(u,v)),fill=col,width=w)
Ld(np.array(NEW.exterior.coords),(0,160,0),3)
for h in NEW.interiors: Ld(np.array(h.coords),(0,160,0),3)
for nm,(xa,xb,za,zb,f) in {'lower':(425,560,-5,55,2),'all':(425,612,-12,125,1)}.items():
    u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb)
    c=im.crop((int(u0),int(v0),int(u1),int(v1)))
    if f>1: c=c.resize((c.size[0]*4//3,c.size[1]*4//3))
    c.save(O+f'/RoyalCaroline_Rhino/qa/bow_backbone_v2_{nm}.png')

import rhino3dm as r3, ezdxf
PK=O+'/RoyalCaroline_Rhino'
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n,c): L_=r3.Layer(); L_.Name=n; L_.Color=(*c,255); return m.Layers.Add(L_)
def att(li,n): a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=n; return a
li=lay('BACKBONE_CONTOUR_v2',(0,150,0)); lo=lay('BACKBONE_CONTOUR_v1_old',(200,0,0)); lr=lay('REF_plan5_frame_blocks',(255,140,0))
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in NEW.exterior.coords]),att(li,'backbone_contour_v2'))
m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in cur.exterior.coords]),att(lo,'backbone_contour_v1'))
for x0,x1,zb,zt in B:
    m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(a,0,b) for a,b in ((x0,zb),(x1,zb),(x1,zt),(x0,zt),(x0,zb))]),att(lr,'plan5_frame_block'))
m.Write(PK+'/RoyalCaroline_backbone_contour_v2.3dm',8)
dd=ezdxf.new('R2010'); dd.units=ezdxf.units.MM; dd.modelspace().add_lwpolyline([tuple(p) for p in NEW.exterior.coords],close=True); dd.saveas(PK+'/RoyalCaroline_backbone_contour_v2.dxf')
print('written')
