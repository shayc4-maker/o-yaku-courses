import sys,json,numpy as np
sys.path.insert(0,'py')
from refdxf import load
from shapely.geometry import LineString,Point,Polygon
from shapely.ops import unary_union,polygonize,snap,nearest_points
L=load(sys.argv[1]); tol=float(sys.argv[2]); use=sys.argv[4].split(',')
lines=[]
for l in use:
    for s in L.get(l,[]):
        a=np.array(s)
        if len(a)<2 or a[:,0].max()<-20: continue
        lines.append(LineString(a))
# iterative endpoint snapping to nearest other line (within tol)
for it in range(2):
    new=[]
    for i,ln in enumerate(lines):
        pts=list(ln.coords)
        for k in (0,-1):
            p=Point(pts[k]); best=None
            for j,o in enumerate(lines):
                if j==i: continue
                d=o.distance(p)
                if d<1e-9: best=None;break
                if d<tol and (best is None or d<best[0]): best=(d,nearest_points(p,o)[1])
            if best: pts[k]=(best[1].x,best[1].y)
        new.append(LineString(pts))
    lines=new
u=unary_union(lines)
faces=sorted(polygonize(u),key=lambda p:-p.area)
print(len(faces),'faces',[round(f.area) for f in faces[:15]])
json.dump([{'id':i,'area':f.area,'ring':list(f.exterior.coords),'holes':[list(h.coords) for h in f.interiors]} for i,f in enumerate(faces)],open(sys.argv[3],'w'))
# dangling endpoints
from collections import Counter
