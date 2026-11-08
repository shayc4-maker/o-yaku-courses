# close ALL parts from the builder's lines: prune the superseded old edges of the 3 front parts, close open polylines, snap, connect dangling ends, node, polygonize, name by IoU with the old approved parts
import json,numpy as np,pickle
from shapely.geometry import LineString,Polygon,Point,MultiPoint
from shapely.ops import unary_union,polygonize,nearest_points
from scipy.cluster.hierarchy import fcluster,linkage
from collections import Counter
S=json.load(open('data/keel_lines_builder_v3b.json')); PR=json.load(open('data/step44_profiles.json'))
old={}
for k,v in PR.items():
    for j,q in enumerate(v):
        pg=Polygon(q).buffer(0)
        if pg.area>1: old[k]=pg
chain={'01':None}
chains=[LineString(np.array(P)) for ln,P,nm,t in S if ln in('01','02','03','04') and t=='NurbsCurve']
def d_chain(p): return min(c.distance(Point(p)) for c in chains)
PRUNE=('APPROVED_Boss-Extrude2[2]','APPROVED_Boss-Extrude4[4]','APPROVED_Boss-Extrude2[1]')
segs=[]; dropped=Counter()
c04=[LineString(np.array(P)) for ln,P,nm,t in S if ln=='04' and t=='NurbsCurve'][0]; c02=[LineString(np.array(P)) for ln,P,nm,t in S if ln=='02' and t=='NurbsCurve'][0]; c03=[LineString(np.array(P)) for ln,P,nm,t in S if ln=='03' and t=='NurbsCurve'][0]
top_edge=None
for ln,P,nm,t in S:
    P=np.array(P)
    if ln=='90' and t=='PolylineCurve' and 1e-6<np.hypot(*(P[0]-P[-1]))<8: P=np.vstack([P,P[:1]])
    for a,b in zip(P[:-1],P[1:]):
        if np.hypot(*(b-a))<1e-9: continue
        m=(a+b)/2
        if ln=='90':
            drop=False
            if nm=='APPROVED_Boss-Extrude4[4]': drop=True
            elif nm=='APPROVED_Boss-Extrude2[2]': drop=(a[0]>516 and b[0]>516) or (38<m[0]<570 and d_chain(a)<2.4 and d_chain(b)<2.4 and d_chain(m)<2.4)
            elif nm=='APPROVED_Boss-Extrude2[1]': drop=(c04.distance(Point(a))<1.0 and c04.distance(Point(b))<1.0)
            elif nm=='APPROVED_Boss-Extrude3[3]': drop=(m[0]<53 and c02.distance(Point(m))<1.2) or (38<m[0]<53 and c03.distance(Point(m))<1.5)
            if drop: dropped[nm]+=1; continue
        segs.append((a,b))
# the stem top edge between the ends of the blue chain and the keel->stem chain
c01=[LineString(np.array(P)) for ln,P,nm,t in S if ln=='01' and t=='NurbsCurve'][0]
segs.append((np.array(c04.coords[0]),np.array(c01.coords[-1])))
print('segments',len(segs),'dropped',dict(dropped))
pts=np.array([p for a,b in segs for p in (a,b)]); cl=fcluster(linkage(pts,'single'),0.05,'distance'); cen={c:pts[cl==c].mean(0) for c in set(cl)}; mp={tuple(p):cen[c] for p,c in zip(pts,cl)}
L=[LineString([mp[tuple(a)],mp[tuple(b)]]) for a,b in segs]
# dangling endpoints -> connect to the nearest line within 0.4 mm
U=unary_union(L); from collections import defaultdict
deg=Counter()
for l in U.geoms if hasattr(U,'geoms') else [U]:
    for c in (l.coords[0],l.coords[-1]): deg[(round(c[0],3),round(c[1],3))]+=1
dang=[p for p,n in deg.items() if n==1]; print('dangling ends before repair:',len(dang))
add=[]
for p in dang:
    P=Point(p); best=None
    for l in (U.geoms if hasattr(U,'geoms') else [U]):
        if l.distance(P)<1e-9: continue
        d=l.distance(P)
        if d<0.4 and (best is None or d<best[0]): best=(d,nearest_points(l,P)[0])
    if best: add.append(LineString([p,(best[1].x,best[1].y)]))
print('repair connectors added:',len(add)); U=unary_union(list(U.geoms if hasattr(U,'geoms') else [U])+add)
faces=[f for f in polygonize(U)]; big=[f for f in faces if f.area>=1.0]; print('faces',len(faces),'big',len(big))
rows=[]
for f in big:
    k,pg=max(old.items(),key=lambda kv:f.intersection(kv[1]).area/f.union(kv[1]).area); rows.append((k,f.intersection(pg).area/f.union(pg).area,f))
rows.sort(key=lambda r:r[0])
for k,iou,f in rows: print('%-18s IoU %.3f face area %8.1f old %8.1f valid %s'%(k,iou,f.area,old[k].area,f.is_valid))
print('old parts without a face:',[k for k in old if k not in [r[0] for r in rows]])
pickle.dump([(k,f.wkt) for k,iou,f in rows],open('/tmp/faces_v3.pkl','wb'))
