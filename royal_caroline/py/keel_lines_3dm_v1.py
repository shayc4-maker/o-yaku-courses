# lines-only Rhino file of the full corrected 2D (keel group, side view XZ at Y=0): one NURBS per continuous tangent chain + aft lines + approved outlines (reference) + the builder's original reference curves (hidden)
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
from shapely.geometry import Polygon
R=json.load(open('data/builder_ref_curves_keel_v2.json')); byi={r['i']:np.array(r['pts'])[:,[0,2]] for r in R}; PR=json.load(open('data/step44_profiles.json'))
K2=json.load(open('data/keel_keelson_2d_v2.json')); CH=json.load(open('data/keel_bow_chains_2d_v1.json')); KB=json.load(open('data/keel_bow_keelson_2d_v2.json')); F4=json.load(open('data/keel_full_2d_v4.json')); BLU=np.array(json.load(open('data/keel_blue_chain_2d_v1.json'))['chain'])
def dedupe(P):
    out=[P[0]]
    for p in P[1:]:
        if np.hypot(*(p-out[-1]))>1e-6: out.append(p)
    return np.array(out)
def join_dense(parts):
    P=parts[0]
    for q in parts[1:]:
        if np.hypot(*(P[-1]-q[0]))>np.hypot(*(P[-1]-q[-1])): q=q[::-1]
        P=np.vstack([P,q])
    return dedupe(P)
def nurbs(P,n=None,name=''):
    P=dedupe(P); sd=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]; L=sd[-1]
    # least-squares B-spline with the fewest control points that stays within 0.02 mm of the drawing
    for rms in (0.02,0.014,0.01,0.007,0.005,0.003,0.002,0.001):
        tck,u=splprep(P.T,k=3,s=len(P)*rms**2,u=sd/L); X,Z=splev(np.linspace(0,1,60000),tck); C=np.c_[X,Z]
        dev=max(np.min(np.hypot(*(C-p).T)) for p in P[::max(1,len(P)//400)])
        if dev<0.02: break
    t,c,k=tck; m=len(c[0]); cv=r3.NurbsCurve(3,False,k+1,m)
    for i in range(m): cv.Points[i]=r3.Point4d(float(c[0][i]),0.0,float(c[1][i]),1.0)
    for i,v in enumerate(t[1:-1]): cv.Knots[i]=float(v)
    ends=(np.hypot(*(C[0]-P[0])),np.hypot(*(C[-1]-P[-1])))
    print('%-40s %3d control points, length %.1f mm, max deviation %.3f mm, end points off by %.3f / %.3f mm'%(name,m,L,dev,ends[0],ends[1])); return cv
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    l=r3.Layer(); l.Name=n; l.Color=col; l.Visible=vis; LI[n]=f.Layers.Add(l)
def add(g,ln,name): a=r3.ObjectAttributes(); a.LayerIndex=LI[ln]; a.Name=name; f.Objects.Add(g,a)
layer('01_KEEL_TOP_to_STEM_INNER',(220,0,0,255)); layer('02_KEELSON_UNDERSIDE',(0,150,0,255)); layer('03_KEELSON_TOP',(0,0,0,255)); layer('04_STEM_FRONT',(0,0,220,255)); layer('05_AFT_LINES_horizontal',(255,140,0,255)); layer('06_AFT_LINES_inclined_parallel',(0,170,170,255)); layer('07_KNEE_END_and_CAP',(150,80,30,255)); layer('08_NODES',(120,0,120,255)); layer('90_APPROVED_outlines_reference',(170,170,170,255)); layer('91_BUILDER_original_reference_curves',(200,200,0,255),False)
# 01: keel top (stern part, mine) + R1 + chain from the R1 end up the stem inner line (R3)
kt=np.array(K2['keel_top']); inner=np.array(CH['inner'])    # inner already = R1 (reversed) + blend + R3 upward
chain=join_dense([kt,inner]); add(nurbs(chain,name='01 keel top -> stem inner line'),'01_KEEL_TOP_to_STEM_INNER','KEEL_TOP_to_STEM_INNER')
# 02: knee underside R6 + keelson underside + the end that merges into the chain
R6=byi[178]; U=np.array(K2['underside']); BU=np.array(KB['underside_end']); add(nurbs(join_dense([R6,U,BU]),name='02 keelson underside (with R6, end)'),'02_KEELSON_UNDERSIDE','KEELSON_UNDERSIDE')
# 03: keelson top + end merging into the chain
T=np.array(K2['keelson_top']); BT=np.array(KB['top_end']); add(nurbs(join_dense([T,BT]),name='03 keelson top (with end)'),'03_KEELSON_TOP','KEELSON_TOP')
# 04: stem front chain
add(nurbs(BLU,name='04 stem front (R2+#180 as one)'),'04_STEM_FRONT','STEM_FRONT')
# 05/06 aft
for k,v in F4['aft'].items():
    P=np.array(v); i=int(k); lay='05_AFT_LINES_horizontal' if i in (182,183,184,185,190) else '06_AFT_LINES_inclined_parallel'
    add(r3.LineCurve(r3.Point3d(P[0][0],0,P[0][1]),r3.Point3d(P[1][0],0,P[1][1])),lay,'AFT_%d'%i)
# 07 knee end R5 (as drawn) and cap R7
for i,nm in ((177,'KNEE_END_R5'),(179,'KEELSON_AFT_CAP_R7')):
    P=byi[i]; add(nurbs(P,name=nm) if i==177 else r3.LineCurve(r3.Point3d(P[0][0],0,P[0][1]),r3.Point3d(P[-1][0],0,P[-1][1])),'07_KNEE_END_and_CAP',nm)
# nodes
nodes={'keel top start (X45)':kt[0],'R1/stern joint (432.92,3.68)':kt[-1],'keelson underside meets the chain (539.7,45.8)':np.array(KB['C1']),'keelson top wedge tip (549.4,65.8)':np.array(KB['C2']),'stem step (531.25,22.88)':np.array([531.25,22.88]),'forefoot junction (500.72,4.45)':np.array([500.72,4.45]),'#180 lower end (480.58,-0.66)':np.array([480.58,-0.66])}
for n,p in nodes.items(): a=r3.ObjectAttributes(); a.LayerIndex=LI['08_NODES']; a.Name=n; f.Objects.AddPoint(r3.Point3d(p[0],0,p[1]),a)
# approved outlines
for k,v in PR.items():
    for q in v:
        P=np.array(q); P=P[np.r_[True,np.any(np.diff(P,axis=0)!=0,axis=1)]]
        if len(P)>2: add(r3.PolylineCurve([r3.Point3d(x,0,z) for x,z in P]+[r3.Point3d(P[0][0],0,P[0][1])]),'90_APPROVED_outlines_reference','APPROVED_'+k)
# original reference curves (hidden)
for i,P in byi.items(): add(r3.PolylineCurve([r3.Point3d(x,0,z) for x,z in P[::3]]),'91_BUILDER_original_reference_curves','BUILDER_%d'%i)
f.Write('rhino/RoyalCaroline_keel_lines_v3.3dm',7); print('objects',len(f.Objects))
