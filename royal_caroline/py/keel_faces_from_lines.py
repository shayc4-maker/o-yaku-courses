# close the parts from the builder's lines (11e29a58-...keel_lines_v3.3dm): prune superseded old reference edges near the new chains, snap, node, polygonize, name the faces by the old approved parts
import json,numpy as np
from shapely.geometry import LineString,Polygon,Point,MultiLineString
from shapely.ops import unary_union,polygonize,snap
from shapely.strtree import STRtree
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=json.load(open('data/keel_lines_builder_v3b.json')); PR=json.load(open('data/step44_profiles.json'))
chains={}; keep=[]
for ln,P,nm,t in S:
    P=np.array(P)
    if ln in('01','02','03','04') and t=='NurbsCurve': chains[(ln,nm)]=LineString(P)
chain_geoms=[g for g in chains.values()]
def near_chain(p,tol):
    return any(g.distance(Point(p))<tol for g in chain_geoms)
dropped=0; lines=[]
for ln,P,nm,t in S:
    P=np.array(P)
    if ln=='90':
        # old reference edges superseded by the new chains (stepped keel top / keelson underside / old stem lines)
        for a,b in zip(P[:-1],P[1:]):
            m=(a+b)/2
            if (45<m[0]<552 and near_chain(a,2.2) and near_chain(b,2.2)) or (38<m[0]<56 and 30<m[1]<40 and near_chain(m,1.6)):
                dropped+=1; continue
            lines.append(LineString([a,b]))
    else:
        for a,b in zip(P[:-1],P[1:]):
            if np.hypot(*(b-a))>1e-9: lines.append(LineString([a,b]))
print('segments kept %d, old reference edges dropped %d'%(len(lines),dropped))
# snap endpoints within 0.05 mm
pts=np.array([c for l in lines for c in (l.coords[0],l.coords[-1])]); 
from scipy.cluster.hierarchy import fcluster,linkage
Z=linkage(pts,'single'); cl=fcluster(Z,0.05,'distance'); cen={c:pts[cl==c].mean(0) for c in set(cl)}; snapped=dict()
for p,c in zip(map(tuple,pts),cl): snapped[p]=cen[c]
L2=[LineString([snapped[tuple(l.coords[0])],snapped[tuple(l.coords[-1])]]) if len(l.coords)==2 else l for l in lines]
U=unary_union(L2); faces=list(polygonize(U)); print('faces',len(faces))
old={}
for k,v in PR.items():
    for j,q in enumerate(v):
        pg=Polygon(q).buffer(0)
        if pg.area>1: old['%s#%d'%(k,j)]=pg
rows=[]
for f in faces:
    if f.area<1.0: continue
    best=max(old.items(),key=lambda kv:f.intersection(kv[1]).area/f.union(kv[1]).area)
    iou=f.intersection(best[1]).area/f.union(best[1]).area; rows.append((best[0],round(iou,3),round(f.area,1),round(best[1].area,1),f))
rows.sort(key=lambda r:r[0])
for r in rows: print('%-22s IoU %.3f face area %8.1f old area %8.1f'%r[:4])
print('tiny faces (<1 mm2):',sum(1 for f in faces if f.area<1.0),'; old parts without a face:',[k for k in old if k not in [r[0] for r in rows]])
import pickle; pickle.dump([(r[0],r[1],r[4].wkt) for r in rows],open('/tmp/faces_v1.pkl','wb'))
fig,axs=plt.subplots(3,1,figsize=(20,24)); cm=plt.cm.tab20(np.linspace(0,1,len(rows)))
for a,(x0,x1,z0,z1) in zip(axs,((-40,575,-14,125),(-40,60,-14,140),(470,575,-5,118))):
    for i,r in enumerate(rows):
        f=r[4]; xs,ys=f.exterior.xy; a.fill(xs,ys,color=cm[i],alpha=.45); a.plot(xs,ys,color=cm[i],lw=.8)
        if x0<f.centroid.x<x1: a.text(f.centroid.x,f.centroid.y,r[0].replace('Boss-Extrude','BE'),fontsize=6,ha='center')
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.set_aspect('equal'); a.grid(alpha=.3)
fig.savefig('qa/keel_faces_from_lines_v1.png',dpi=48,bbox_inches='tight')
