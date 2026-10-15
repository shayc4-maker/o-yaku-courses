import sys,json,numpy as np
sys.path.insert(0,'py')
from refdxf import load
from shapely.geometry import LineString,MultiLineString,Polygon,Point
from shapely.ops import unary_union,polygonize,snap
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
L=load(sys.argv[1]); tol=float(sys.argv[2]) if len(sys.argv)>2 else 0.12
use=['01_BODY_OUTER','02_KEELSON','03_STERN_KNEE','04_AFT_DIVISIONS','05_KEEL_HOG_FALSEKEEL','06_STEM_APRON','07_HEAD_GRIPE','10_FRAME_SEATS']
lines=[]
for l in use:
    for s in L.get(l,[]):
        a=np.array(s)
        if len(a)<2 or a[:,0].max()<-35 or a[:,0].min()<-35 and a[:,0].max()<0: continue
        if a[:,0].max()<-20: continue
        lines.append(LineString(a))
print(len(lines),'lines')
# endpoint snapping to nearest other geometry
u=unary_union(lines)
snapped=[]
allg=unary_union(lines)
for ln in lines:
    pts=list(ln.coords)
    for k in (0,-1):
        p=Point(pts[k]); others=unary_union([g for g in lines if g is not ln and g.distance(p)<tol*3]) if True else None
        if others and not others.is_empty and others.distance(p)>1e-9 and others.distance(p)<tol:
            from shapely.ops import nearest_points
            q=nearest_points(p,others)[1]; pts[k]=(q.x,q.y)
    snapped.append(LineString(pts))
u=unary_union(snapped)
faces=sorted(polygonize(u),key=lambda p:-p.area)
print(len(faces),'faces; areas>0.5:',sum(f.area>0.5 for f in faces))
json.dump([{'id':i,'area':f.area,'ring':list(f.exterior.coords),'holes':[list(h.coords) for h in f.interiors]} for i,f in enumerate(faces)],open(sys.argv[3],'w'))
