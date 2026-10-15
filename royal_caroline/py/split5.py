import sys,json,numpy as np
sys.path.insert(0,'py'); from p5map import *
from scipy.interpolate import splprep,splev
from shapely.geometry import Polygon,box,LineString,MultiPolygon
from shapely.ops import unary_union
O='out'; PK=O+'/RoyalCaroline_Rhino'
V=Polygon(json.load(open(O+'/backbone_contour_v5.json'))['outer']).buffer(0)
P10={p['name']:Polygon(p['poly']).buffer(0) for p in json.load(open(O+'/parts_v10.json')) if p['plane']=='XZ' and p['off']==0.0}
def sp(P,s=0.3,n=80):
    t,u=splprep(np.array(P,float).T,s=s,k=3); return [tuple(p) for p in np.array(splev(np.linspace(0,1,n),t)).T]
def left_of(line,big=900):   # polygon on the -X side of a polyline running bottom->top
    L=list(line); return Polygon([(L[0][0]-big,L[0][1])]+L+[(L[-1][0]-big,L[-1][1])]).buffer(0)
def below(line,big=900):     # polygon under a polyline running aft->fwd
    L=list(line); return Polygon([(L[0][0],L[0][1]-big)]+L+[(L[-1][0],L[-1][1]-big)]).buffer(0)
parts={}
taken=Polygon()
for n in ['STEM','KNEE_OF_HEAD_UPPER','KNEE_OF_HEAD_LOWER','APRON_1','APRON_2','APRON_3','GRIPE']:
    g=P10[n].intersection(V).difference(taken)
    if g.area>0.5: parts[n]=g; taken=taken.union(g)
R=V.difference(taken)
X0,X1=-60,700
# lines read from plan_5
L1=[(12.22,-0.5),(11.49,4.4),(10.62,8.5),(9.75,12.5),(8.59,16.9),(7.43,21.2),(6.28,25.3),(5.26,30.5),(3.96,35.1),(2.80,39.8),(1.35,44.4),(0.01,49.9),(-0.8,53.0),(-3.0,61.4),(-6,80),(-9,100)]
L1=sp(L1[:13],0.25)+L1[13:]
L2=[(16.2,9.6),(15.84,11.1),(14.39,16.3),(12.65,21.2),(10.62,25.6),(8.45,30.8)]
L2=sp(L2,0.15,40)+[(8.45,200)]
CAP=[(L1i) for L1i in []]
J=[(L1[0][0]-2,9.7),(10.3,9.7),(12.4,10.2),(15.84,11.1),(20,10.2),(30.7,8.9),(30.8,7.3),(39.9,6.2),(49.6,5.0),(59.7,4.1)]
def htop(x): return np.where(x<449.7,0.8,np.where(x<479.9,0.8+(x-449.7)*(3.4-0.8)/(479.5-449.7),-0.2+(x-479.9)*0.1745))
def ktop(x): return np.where(x<479.9,-0.2,-0.2+(x-479.9)*0.1745)
xs=np.r_[X0,np.arange(-20,700,0.25),X1]
Hpoly=below(list(zip(xs,htop(xs)+np.where(np.abs(xs-479.9)<0.13,0,0))))
# make vertical at 479.9 exact
hx=np.arange(-20,700,0.1); hz=htop(hx); line=[]
for x,z in zip(hx,hz):
    if x>=479.9 and line and line[-1][0]<479.9: line.append((479.9,3.4)); line.append((479.9,-0.2))
    line.append((x,float(z)))
Hpoly=below(line); Kpoly=below([(x,float(ktop(x))) for x in hx])
FK=R.intersection(box(X0,-50,X1,-7.4)); KE=R.intersection(Kpoly).difference(FK); HOG=R.intersection(Hpoly).difference(Kpoly)
UP=R.difference(Hpoly)
def scarf_split(G,cuts,zmid,zt,name):
    out={}; prev=Polygon(); k=1
    for x1,x2 in cuts+[(X1,X1)]:
        lp=Polygon([(X0,-50),(x1,-50),(x1,zmid),(x2,zmid),(x2,zt),(x2,60),(X0,60)]) if x1<X1 else box(X0,-50,X1,300)
        g=G.intersection(lp).difference(prev)
        if g.area>0.3: out['%s_%d'%(name,k)]=g; k+=1
        prev=prev.union(g)
    return out
parts.update(scarf_split(FK,[(126.5,130.5),(255.0,259.0),(377.5,381.0)],-8.4,-7.4,'FALSE_KEEL'))
parts.update(scarf_split(KE,[(168.1,168.1),(333.5,333.5)],-3,0,'KEEL'))
TEN=box(4.2,-0.8,7.6,0.8)
parts['HOG']=HOG.difference(TEN)
parts['KEEL_1']=parts['KEEL_1'].union(HOG.intersection(box(-50,-5,4.2,5))).difference(TEN).buffer(0)
parts['HOG']=parts['HOG'].difference(box(-50,-5,4.2,5))
L1p=left_of(L1)
parts['STERNPOST']=UP.intersection(L1p).union(TEN.intersection(V))
rest=UP.difference(L1p)
Jpoly=below(J+[(59.7,0.8),(59.7,-50)][:1]+[(59.7,-50)])
Jpoly=Polygon([(J[0][0],-50)]+J+[(59.7,-50)]).buffer(0)
lowJ=rest.intersection(Jpoly)
parts['DEADWOOD_AFT_LOWER']=lowJ
rest=rest.difference(Jpoly)
P2=rest.intersection(left_of(L2)).intersection(box(X0,-50,X1,30.65))
parts['INNER_POST_HEEL']=P2
parts['DEADWOOD_RISING']=rest.difference(P2)
frag=[]
for k,g in list(parts.items()):
    if isinstance(g,MultiPolygon):
        gs=sorted(g.geoms,key=lambda q:-q.area); parts[k]=gs[0]; frag+=[q for q in gs[1:] if q.area>0.2]
for q in frag:
    best=max(parts,key=lambda k:parts[k].buffer(0.05).intersection(q.exterior).length)
    print('merge frag %.1f %s -> %s'%(q.area,np.round(q.bounds,1).tolist(),best))
    u=parts[best].union(q.buffer(0.01)).buffer(0); u=max(getattr(u,'geoms',[u]),key=lambda z:z.area)
    parts[best]=Polygon(u.exterior.coords).intersection(V).buffer(0)
    if isinstance(parts[best],MultiPolygon): parts[best]=max(parts[best].geoms,key=lambda z:z.area)
for k in parts:
    parts[k]=parts[k].difference(unary_union([parts[o] for o in parts if o<k and o!=k]).buffer(0)) if False else parts[k]
def despike(g):
    c=list(g.exterior.coords)[:-1]; ch=True
    while ch:
        ch=False; n=len(c)
        for i in range(n):
            a,b,d=np.array(c[i-1]),np.array(c[i]),np.array(c[(i+1)%n]); u,v=b-a,d-b
            cr=abs(u[0]*v[1]-u[1]*v[0]); 
            if np.hypot(*u)<1e-4 or (cr<1e-3*max(np.hypot(*u),np.hypot(*v)) ): c.pop(i); ch=True; break
    return Polygon(c)
parts={k:despike(g) for k,g in parts.items()}
tot=unary_union(list(parts.values()))
print('coverage %.1f / %.1f'%(tot.area,V.area))
for k,g in parts.items(): print(k,round(g.area,1),np.round(g.bounds,1).tolist(),g.geom_type)
json.dump({k:np.array(g.exterior.coords).tolist() for k,g in parts.items()},open(O+'/backbone_split_v5.json','w'))
# split lines = part boundaries minus outer contour
ob=V.exterior.buffer(0.03)
segs=unary_union([g.exterior for g in parts.values()]).difference(ob)
segs=[s for s in getattr(segs,'geoms',[segs]) if s.length>0.2]
from PIL import Image, ImageDraw
im=Image.open('a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); dr=ImageDraw.Draw(im)
e=np.array(V.exterior.coords); u,v=model_to_p5(e[:,0],e[:,1]); dr.line(list(zip(u,v)),fill=(0,160,0),width=3)
for s in segs:
    c=np.array(s.coords); u,v=model_to_p5(c[:,0],c[:,1]); dr.line(list(zip(u,v)),fill=(220,0,160),width=3)
for nm,(xa,xb,za,zb,z) in {'aft':(-20,70,-12,60,2),'keel1':(100,280,-11,8,2),'keel2':(270,500,-11,12,2),'fwd':(440,612,-11,122,1)}.items():
    u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb); c=im.crop((int(u0),int(v0),int(u1),int(v1)))
    if z>1: c=c.resize((c.size[0]*z,c.size[1]*z))
    c.save(PK+f'/qa/split_v5_{nm}.png')
import rhino3dm as r3, ezdxf
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n,c): L_=r3.Layer(); L_.Name=n; L_.Color=(*c,255); return m.Layers.Add(L_)
def att(li,n): a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=n; return a
lc=lay('BACKBONE_CONTOUR_v5',(0,150,0)); ls=lay('SPLIT_LINES_v5',(220,0,160)); lp=lay('PARTS_v5',(60,60,60))
pc=lambda c:r3.PolylineCurve([r3.Point3d(float(x),0,float(z)) for x,z in c])
m.Objects.AddCurve(pc(V.exterior.coords),att(lc,'backbone_contour_v5'))
for s in segs: m.Objects.AddCurve(pc(s.coords),att(ls,'split'))
dd=ezdxf.new('R2010'); dd.units=ezdxf.units.MM; ms=dd.modelspace()
for k,g in parts.items():
    m.Objects.AddCurve(pc(g.exterior.coords),att(lp,k))
    dd.layers.add(k); ms.add_lwpolyline([tuple(p) for p in g.exterior.coords],close=True,dxfattribs={'layer':k})
m.Write(PK+'/RoyalCaroline_backbone_split_v5.3dm',8); dd.saveas(PK+'/RoyalCaroline_backbone_split_v5.dxf')
