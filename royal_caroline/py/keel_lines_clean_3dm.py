# the builder's APPROVED backbone lines (rhino/ref_final_from_builder.dxf, layers 01-07) as a lines-only 3dm: no image, no review layer 98, duplicates removed; XZ plane at Y=0 (2D polylines stored in XY are moved to XZ)
import numpy as np,ezdxf,json
import rhino3dm as r3
from collections import Counter,defaultdict
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=ezdxf.readfile('rhino/ref_final_from_builder.dxf'); ms=d.modelspace()
KEEP=['01_BODY_OUTER','02_KEELSON','03_STERN_KNEE','04_AFT_DIVISIONS','05_KEEL_HOG_FALSEKEEL','06_STEM_APRON','07_HEAD_GRIPE']
R=lambda v:tuple(round(float(c),2) for c in v)
ents=[]; skipped=Counter()
for e in ms:
    L=e.dxf.layer; t=e.dxftype()
    if L not in KEEP: skipped[(L,t)]+=1; continue
    if t=='LINE': P=[R((e.dxf.start.x,0.0,e.dxf.start.z)),R((e.dxf.end.x,0.0,e.dxf.end.z))]; ents.append(dict(L=L,t='line',P=P))
    elif t=='POLYLINE':
        V=np.array([list(v.dxf.location) for v in e.vertices])
        if np.ptp(V[:,2])<1e-6 and np.ptp(V[:,1])>=0: P=[R((x,0.0,y)) for x,y,z in V]      # drawn in the XY plane with (x,y)=(X,Z)
        else: P=[R((x,0.0,z)) for x,y,z in V]
        if min(p[0] for p in P)<-100: skipped[(L,'stray polyline X<-100')]+=1; continue
        ents.append(dict(L=L,t='poly',P=P))
    elif t=='SPLINE':
        cp=[R((p[0],0.0,p[2])) for p in e.control_points]; ents.append(dict(L=L,t='spline',P=cp,deg=e.dxf.degree,knots=list(e.knots),w=list(e.weights) if len(e.weights) else None))
def key(x):
    P=x['P']; 
    if x['t']=='poly' and len(P)==2: x=dict(x,t='line')
    f=tuple(P); r=tuple(P[::-1]); return (x['t'],min(f,r))
seen={}; keep=[]; dup=Counter()
for x in ents:
    k=key(x)
    if k in seen: dup[(x['L'],seen[k])]+=1; continue
    seen[k]=x['L']; keep.append(x)
# zero-length
keep=[x for x in keep if not(x['t']=='line' and x['P'][0]==x['P'][1])]
# curves lying (>=90 % of their length, within 0.03 mm) on another curve are duplicates too
from scipy.spatial import cKDTree
from scipy.interpolate import BSpline
def dense(x,step=0.1):
    P=np.array(x['P'])
    if x['t']=='spline':
        n=len(P); kn=np.array(x['knots']); return BSpline(kn,P[:,[0,2]],x['deg'])(np.linspace(kn[x['deg']],kn[n],200))
    P=P[:,[0,2]]; out=[np.linspace(a,b,max(2,int(np.hypot(*(b-a))/step)+1)) for a,b in zip(P[:-1],P[1:])]
    return np.vstack(out) if out else P
S=[dense(x) for x in keep]; allp=np.vstack(S); owner=np.concatenate([[i]*len(s) for i,s in enumerate(S)]); tree=cKDTree(allp); drop=set()
for i,s in enumerate(S):
    idx=tree.query_ball_point(s,0.03)
    if np.mean([any(owner[j]!=i and owner[j] not in drop for j in ii) for ii in idx])>=0.9: drop.add(i); dup[(keep[i]['L'],'covered by another curve')]+=1
keep=[x for i,x in enumerate(keep) if i not in drop]
print('read',len(ents),'kept',len(keep),'duplicates removed',sum(dup.values())); print('dup (layer, first seen on layer):',dict(dup)); print('skipped:',dict(skipped))
print('kept per layer:',dict(Counter((x['L'],x['t']) for x in keep)))
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
cols={'01_BODY_OUTER':(0,0,0,255),'02_KEELSON':(0,140,0,255),'03_STERN_KNEE':(140,80,30,255),'04_AFT_DIVISIONS':(220,0,0,255),'05_KEEL_HOG_FALSEKEEL':(0,0,220,255),'06_STEM_APRON':(200,0,200,255),'07_HEAD_GRIPE':(0,170,170,255)}
for L in KEEP: l=r3.Layer(); l.Name=L; l.Color=cols[L]; LI[L]=f.Layers.Add(l)
bad=0
for i,x in enumerate(keep):
    a=r3.ObjectAttributes(); a.LayerIndex=LI[x['L']]
    if x['t']=='line': g=r3.LineCurve(r3.Point3d(*x['P'][0]),r3.Point3d(*x['P'][1]))
    elif x['t']=='poly': g=r3.PolylineCurve([r3.Point3d(*p) for p in x['P']])
    else:
        n=len(x['P']); k=x['deg']; g=r3.NurbsCurve(3,False,k+1,n)
        for j,p in enumerate(x['P']): g.Points[j]=r3.Point4d(p[0],p[1],p[2],(x['w'][j] if x['w'] else 1.0))
        kn=x['knots'][1:-1]
        if len(kn)!=n+k-1: bad+=1; continue
        for j,v in enumerate(kn): g.Knots[j]=float(v)
    f.Objects.Add(g,a)
f.Write('rhino/RoyalCaroline_keel_approved_lines_clean_v1.3dm',7); print('objects',len(f.Objects),'spline knot-count errors',bad)
fig,axs=plt.subplots(2,1,figsize=(20,13)); cc={k:tuple(v/255 for v in c[:3]) for k,c in cols.items()}
for x in keep:
    P=np.array(x['P']); 
    if x['t']=='spline':
        from scipy.interpolate import BSpline
        n=len(P); kn=np.array(x['knots']); xs=np.linspace(kn[x['deg']],kn[n],40); P=BSpline(kn,P[:,[0,2]],x['deg'])(xs)
    else: P=P[:,[0,2]]
    for a in axs: a.plot(P[:,0],P[:,1],color=cc[x['L']],lw=1)
for a,(x0,x1) in zip(axs,((-60,300),(280,600))): a.set_xlim(x0,x1); a.set_ylim(-15,100); a.set_aspect('equal'); a.grid(alpha=.3)
fig.savefig('qa/keel_approved_lines_clean_v1.png',dpi=55,bbox_inches='tight')
