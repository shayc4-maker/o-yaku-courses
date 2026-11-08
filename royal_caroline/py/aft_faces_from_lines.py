# aft parts from the builder's rearranged lines: polygonize the aft window (X<62), closing the open old polylines, then name faces by the old approved parts
import json,numpy as np
from shapely.geometry import LineString,Polygon,Point
from shapely.ops import unary_union,polygonize
from scipy.cluster.hierarchy import fcluster,linkage
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=json.load(open('data/keel_lines_builder_v3b.json')); PR=json.load(open('data/step44_profiles.json'))
old={}
for k,v in PR.items():
    for j,q in enumerate(v):
        pg=Polygon(q).buffer(0)
        if pg.area>1: old[k]=pg
segs=[]
for ln,P,nm,t in S:
    P=np.array(P)
    if ln in('01','02','03','04') and t=='NurbsCurve': continue            # long chains handled separately
    if not(P[:,0].min()<62 and P[:,0].max()<70 and np.ptp(P[:,0])<80): continue
    if ln=='90' and t=='PolylineCurve' and np.hypot(*(P[0]-P[-1]))>1e-6 and np.hypot(*(P[0]-P[-1]))<8: P=np.vstack([P,P[:1]])      # close the old outlines that were left open
    for a,b in zip(P[:-1],P[1:]):
        if np.hypot(*(b-a))>1e-9: segs.append((LineString([a,b]),ln,nm))
print('segments in the aft window:',len(segs))
pts=np.array([c for s,_,_ in segs for c in (s.coords[0],s.coords[-1])]); cl=fcluster(linkage(pts,'single'),0.06,'distance'); cen={c:pts[cl==c].mean(0) for c in set(cl)}; mp={tuple(p):cen[c] for p,c in zip(pts,cl)}
L=[LineString([mp[tuple(s.coords[0])],mp[tuple(s.coords[-1])]]) for s,_,_ in segs]
U=unary_union(L); faces=[f for f in polygonize(U) if f.area>0.5]
print('faces',len(faces))
rows=[]
for f in faces:
    best=max(old.items(),key=lambda kv:f.intersection(kv[1]).area/f.union(kv[1]).area); iou=f.intersection(best[1]).area/f.union(best[1]).area; rows.append((best[0],iou,f))
rows.sort(key=lambda r:r[0])
for k,iou,f in rows: print('%-18s IoU %.3f face area %7.1f old %7.1f  (valid %s, bounds X %.1f..%.1f Z %.1f..%.1f)'%(k,iou,f.area,old[k].area,f.is_valid,*f.bounds[0::2],*f.bounds[1::2]) if False else '%-18s IoU %.3f area %7.1f old %7.1f valid %s bbox X %.1f..%.1f Z %.1f..%.1f'%(k,iou,f.area,old[k].area,f.is_valid,f.bounds[0],f.bounds[2],f.bounds[1],f.bounds[3]))
import pickle; pickle.dump([(k,f.wkt) for k,iou,f in rows],open('/tmp/aft_faces_v1.pkl','wb'))
fig,axs=plt.subplots(1,2,figsize=(22,13)); cm=plt.cm.tab20(np.linspace(0,1,max(len(rows),1)))
for a,(x0,x1,z0,z1) in zip(axs,((-36,64,-14,140),(-26,6,40,85))):
    for i,(k,iou,f) in enumerate(rows):
        xs,ys=f.exterior.xy; a.fill(xs,ys,color=cm[i],alpha=.5); a.plot(xs,ys,color='k',lw=.6)
        for h in f.interiors: a.plot(*h.xy,color='r',lw=.6)
        if x0<f.centroid.x<x1 and z0<f.centroid.y<z1: a.text(f.centroid.x,f.centroid.y,k.replace('Boss-Extrude','BE'),fontsize=7,ha='center')
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.set_aspect('equal'); a.grid(alpha=.3)
fig.savefig('qa/aft_faces_from_lines_v1.png',dpi=50,bbox_inches='tight')
