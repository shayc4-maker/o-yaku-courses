# Closed backbone parts (v5 split + keelson + stern knee from the builder's final DXF) -> closed curves + 5.3 mm solids
import sys,json,numpy as np
sys.path.insert(0,'py')
from refdxf import load
from shapely.geometry import Polygon
import rhino3dm as r3, ezdxf
TH=5.3
L=load('rhino/ref_final_from_builder.dxf')
parts={k:[tuple(p) for p in v] for k,v in json.load(open('data/backbone_parts_v1.json')).items()}
seats=json.load(open('data/seat_fix_report.json'))   # [i,a,b,z,zu,src]
def pieces(layer,filt):
    out=[]
    for s in L[layer]:
        a=np.array(s)
        if filt(a): out.append(a)
    return out
def near(a,x,z,t=.3): return (abs(a[0,0]-x)<t and abs(a[0,1]-z)<t) or (abs(a[-1,0]-x)<t and abs(a[-1,1]-z)<t)
def chain(pcs,start):
    # order pieces head-to-tail beginning at 'start' point
    pcs=list(pcs); cur=np.array(start); out=[cur]
    while pcs:
        for i,a in enumerate(pcs):
            if np.hypot(*(a[0]-cur))<.35: seg=a
            elif np.hypot(*(a[-1]-cur))<.35: seg=a[::-1]
            else: continue
            out+= [tuple(p) for p in seg[1:]]; cur=seg[-1]; pcs.pop(i); break
        else: break
    return out
def zfun(cs):
    xs=np.concatenate([c[:,0] for c in cs]); zs=np.concatenate([c[:,1] for c in cs]); o=np.argsort(xs,kind='stable')
    return lambda x: float(np.interp(x,xs[o],zs[o]))
# ---- keelson
blue=[a for a in pieces('03_STERN_KNEE',lambda a:a[:,0].min()>40 and len(a)>3 and a[:,1].max()<60)]
zb=zfun(blue)
red=pieces('02_KEELSON',lambda a: len(a)>=5 and abs(a[0,0]-a[-1,0])>3)+pieces('01_BODY_OUTER',lambda a: len(a)==5 and abs(a[0,0]-195)<.1 and abs(a[-1,0]-389.12)<.1)
red=[a for a in red if a[:,0].min()>=50.9 and a[:,0].max()<=526.8 and a[:,1].min()>11.5]
zr=zfun(red)
XA,XB=41.25,526.6
top=[(41.25,38.06),(51.08,33.98)]+[(x,zr(x)) for x in np.linspace(51.08,XB,400)[1:]]
bot=[]
pk={round(s[1],2):s for s in seats}
xs=np.linspace(41.2,XB,600); sel=[s for s in seats if s[1]>=41.2]
x=41.2; bot.append((41.2,zb(41.2)))
for s in sel:
    _,a,b,z,zu,_=s
    for xx in xs[(xs>x)&(xs<a)]: bot.append((xx,zb(xx)))
    bot+=[(a,zb(a)),(a,zu),(b,zu),(b,zb(b))]; x=b
for xx in xs[xs>x]: bot.append((xx,zb(xx)))
bot[-1]=(XB,zb(XB))
kp=top+[(XB,zr(XB))][:0]
keelson=top+[(XB,zr(XB))]+bot[::-1]
# ---- stern knee
upper=chain(pieces('03_STERN_KNEE',lambda a:a[:,1].min()>30 and a[:,0].max()<52 and len(a)>2 and a[:,1].max()>36 and np.hypot(*(a[0]-a[-1]))>1.5 and a[0,1]>a[-1,1] and (a[:,0].min()>-5.5)),(-4.60,75.78))
low=chain(pieces('03_STERN_KNEE',lambda a:a[:,0].max()<37 and np.hypot(*(a[0]-a[-1]))>10 and a[:,1].min()>35),(36.9,36.9))
sp=np.array(parts['STERNPOST']); 
def post_x(z):
    # fore face of the post: points of the polygon between z 53..76 on the fore side (max x at given z for z>53)
    fore=[p for p in parts['STERNPOST'] if 53<=p[1]<=83.3 and p[0]>-9.0]
    f=sorted(fore,key=lambda p:p[1]); return float(np.interp(z,[p[1] for p in f],[p[0] for p in f]))
knee=[(post_x(upper[0][1]),upper[0][1])]+upper+[(41.25,38.06),(40.8,36.9)]+low[:]
knee+= [(post_x(low[-1][1]),low[-1][1])]
for name,poly in (('KEELSON',keelson),('STERN_KNEE',knee)):
    pg=Polygon(poly); 
    if not pg.is_valid:
        from shapely.validation import explain_validity; print(name,explain_validity(pg)); pg=max(pg.buffer(0).geoms,key=lambda g:g.area) if pg.buffer(0).geom_type=="MultiPolygon" else pg.buffer(0)
    parts[name]=[(round(x,3),round(z,3)) for x,z in pg.exterior.coords]
    print(name,len(poly),'valid',pg.is_valid,round(pg.area,1),[round(v,1) for v in pg.bounds])
# make parts disjoint: keelson/knee take priority over deadwood-rising and others
from shapely.ops import unary_union
cut=unary_union([Polygon(parts['KEELSON']),Polygon(parts['STERN_KNEE'])])
for k in list(parts):
    if k in('KEELSON','STERN_KNEE'): continue
    pg=Polygon(parts[k])
    if pg.intersection(cut).area>0.3:
        d=pg.difference(cut)
        g=[d] if d.geom_type=='Polygon' else sorted(d.geoms,key=lambda g:-g.area)
        print('cut',k,'area',round(pg.area,1),'->',[round(x.area,1) for x in g])
        parts[k]=[(round(x,3),round(z,3)) for x,z in g[0].exterior.coords]
# clean rings
for k,v in parts.items():
    pg=Polygon(v).simplify(0.002)
    parts[k]=[(round(x,3),round(z,3)) for x,z in pg.exterior.coords]
names=list(parts); P={k:Polygon(v) for k,v in parts.items()}
for i,a in enumerate(names):
    for b in names[i+1:]:
        ar=P[a].intersection(P[b]).area
        if ar>0.3: print('overlap',a,b,round(ar,2))
json.dump(parts,open('data/backbone_parts_v2.json','w'))
# ---- 3dm: closed curve + solid per part
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
import matplotlib; cols=matplotlib.colormaps['tab20'].colors
for n,(k,v) in enumerate(parts.items()):
    li=r3.Layer(); li.Name=k; li.Color=tuple(int(255*t) for t in cols[n%20])+(255,); idx=f.Layers.Add(li)
    pl=r3.Polyline(len(v))
    for x,z in v: pl.Add(x,TH/2,z)
    cv=pl.ToPolylineCurve()
    ex=r3.Extrusion.Create(cv,TH,True)
    at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=k
    br=ex.ToBrep(True) if ex else None
    if br is not None:
        bb=br.GetBoundingBox(); br.Translate(r3.Vector3d(0,-TH/2-bb.Min.Y,0))
    if br is None or not br.IsSolid: print('NOT SOLID',k)
    else: f.Objects.AddBrep(br,at)
    pl2=r3.Polyline(len(v))
    for x,z in v: pl2.Add(x,0,z)
    at2=r3.ObjectAttributes(); at2.LayerIndex=idx; at2.Name=k+'_profile'
    f.Objects.AddPolyline(pl2,at2)
f.Write('rhino/RoyalCaroline_backbone_solids_v1.3dm',7)
print(len(f.Objects),'objects')
