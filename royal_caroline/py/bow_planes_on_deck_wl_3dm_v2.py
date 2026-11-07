import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import splev
D=json.load(open('data/bow_deck_waterline_v2.json')); PS=json.load(open('data/bow_plane_sketch_v5.json')); W=json.load(open('data/wl_top_centered_v1.json')); RB=json.load(open('data/rabbet_iron_v4.json')); A5=json.load(open('data/frames_outer_approved_v5.json'))
src=r3.File3dm.Read('/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/84b9e1b4-RoyalCaroline_frames_outer_half_lifted_v1.3dm')
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col):
    if n not in LI: l=r3.Layer(); l.Name=n; l.Color=col; LI[n]=f.Layers.Add(l)
    return LI[n]
def add(g,ln,name): a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(g,a)
def nurbs(q3,k=3):
    q=np.array(q3,float); keep=[0]+[i for i in range(1,len(q)) if np.linalg.norm(q[i]-q[i-1])>1e-6]; q=q[keep]; kk=min(k,len(q)-1); tck,_=splprep(q.T,k=kk,s=0); t,c,kd=tck
    P=[r3.Point3d(c[0][i],c[1][i],c[2][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,kd,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
lA=layer('APPROVED_frames_half_+Y_v2',(200,0,0,255))
for o in src.Objects: add(o.Geometry.Duplicate(),lA,o.Attributes.Name)
lF=layer('FRAME1_front_with_v5_top',(255,0,0,255)); F=A5['1']['front']; add(r3.PolylineCurve([r3.Point3d(528.03,y,z) for y,z in F['curve']]+[r3.Point3d(528.03,y,z) for y,z in F['top'][1:]]),lF,'F01_front_v5')
lR=layer('RABBET_iron_line_final',(0,0,0,255)); add(nurbs([(x,1.8,z) for x,z in RB['points']]),lR,'RABBET_final_to_M48')
lD=layer('DECK_WATERLINE_Z101',(255,120,0,255)); cv=D['curve']; add(nurbs([(x,y,D['Z']) for x,y in cv[::6]]+[(cv[-1][0],cv[-1][1],D['Z'])]),lD,'deck_WL_Z101_through_frames_to_rabbet')
lS=layer('PLANE_SPLINES_5',(200,0,200,255)); lPl=layer('PLANES_parallel_to_keel',(180,180,255,255)); fig,ax=plt.subplots(figsize=(8,10))
for j in range(5):
    p=PS[str(j)]; 
    if j==0: continue
    pts=[tuple(q) for q in p['points'][:-1]]+[(D['plane_tops'][str(j)][0],D['Z'])]
    ms=r3.Mesh()
    for (x,z) in ((500,10),(570,10),(570,110),(500,110)): ms.Vertices.Add(x,p['Y'],z)
    ms.Faces.AddFace(0,1,2,3); ms.Normals.ComputeNormals(); add(ms,lPl,'PLANE_%d_Y%.2f'%(j+1,p['Y']))
    q=[(x,p['Y'],z) for x,z in pts]; add(nurbs(q),lS,'SPLINE_plane%d_Y%.2f'%(j+1,p['Y']))
    tck,_=splprep(np.array(q).T,k=min(3,len(q)-1),s=0); xs,ys,zs=splev(np.linspace(0,1,150),tck); ax.plot(xs,zs,lw=1.5,label='plane %d'%(j+1)); ax.plot([a[0] for a in q],[a[2] for a in q],'k.')
ax.plot([x for x,z in RB['curve']],[z for x,z in RB['curve']],'k-',label='rabbet'); ax.axhline(101,color='tab:orange',ls=':'); ax.set_xlim(500,570); ax.set_ylim(0,125); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(fontsize=8); ax.set_title('side view, tops on the deck WL Z=101')
fig.savefig('qa/bow_planes_deckwl_side_v2.png',dpi=60,bbox_inches='tight')
for k,v in W.items():
    l=layer('WL_%s_z%.1f_reference'%(k,v['z']),(90,90,200,255)); add(nurbs([(x,y,v['z']) for x,y in v['points_XY']]),l,'WL_%s'%k)
f.Write('rhino/RoyalCaroline_bow_planes_deck_WL_v2.3dm',7); print(len(f.Objects))
