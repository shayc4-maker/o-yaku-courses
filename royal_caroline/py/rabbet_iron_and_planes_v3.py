# (1) ONE continuous rabbet line (iron reference, the outer line of the bow frames next to the keel): interpolating cubic through the lower ends of the approved faces (frames 1-8, mid faces + front of frame 1) and the continuation points R1-R7, R10, E, E2; check against the other face ends. (2) the 5 sketch splines on 5 planes parallel to the keel redone: plane 1 = the rabbet, planes 2-5 from the UPDATED approved front face of frame 1 (F01 front), waterlines IV-VII forward of it and the upper deck. Rhino file with the planes as surfaces.
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
A=json.load(open('data/frames_outer_approved_v2.json')); R=json.load(open('data/rabbet_stem_points_v3.json')); W=json.load(open('data/wl_top_centered_v1.json')); MK={p['id']:p for p in json.load(open('data/p1a_marks_v1.json'))}
ends={(b,nm):(A[str(b)][nm]['X'],A[str(b)][nm]['end'][1]) for b in range(1,11) for nm in ('back','mid','front')}
sel=[ends[(b,'mid')] for b in range(8,0,-1)]+[ends[(1,'front')]]+[(r['X'],r['Z']) for r in R if r.get('id')!='E2']+[(MK['M48']['X'],MK['M48']['Z'])]
sel=sorted(set((round(x,3),round(z,3)) for x,z in sel))
Q=np.array(sel); tck,u=splprep(Q.T,k=3,s=0); uu=np.linspace(0,1,1500); X,Z=splev(uu,tck)
d1x,d1z=splev(uu,tck,der=1); d2x,d2z=splev(uu,tck,der=2); kap=(d1x*d2z-d1z*d2x)/(d1x**2+d1z**2)**1.5; sc=int((np.diff(np.sign(kap[np.abs(kap)>2e-4]))!=0).sum())
print('rabbet through %d points: curvature sign changes %d; X monotone %s'%(len(sel),sc,bool((np.diff(X)>=-1e-6).all())))
dev=[]
for (b,nm),(x,z) in ends.items():
    if x<446.5: continue
    i=int(np.argmin(np.hypot(X-x,Z-z))); dev.append((b,nm,round(float(np.hypot(X[i]-x,Z[i]-z)),3)))
print('distance of the lower ends of the OTHER faces (frames 1-10) to the rabbet: max %.3f mm; faces > 0.1:'%max(d[2] for d in dev),[d for d in dev if d[2]>0.1])
json.dump(dict(points=sel,curve=[[round(float(a),3),round(float(b),3)] for a,b in zip(X[::5],Z[::5])]),open('data/rabbet_iron_v3.json','w'))
# planes
Y0=2.65; DY=(47.5-Y0)/5; PL=[Y0+DY*j for j in range(5)]; F1=np.array(A['1']['front']['curve'])
def z_at_y(L,y):
    for i in range(len(L)-1):
        if (L[i,0]-y)*(L[i+1,0]-y)<=0 and L[i,0]!=L[i+1,0]: return float(L[i,1]+(y-L[i,0])/(L[i+1,0]-L[i,0])*(L[i+1,1]-L[i,1]))
def y_at_z(L,z):
    i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0]; return float(np.interp(z,L[:,1],L[:,0])) if len(i) else None
Cst=json.load(open('data/bodyplan_centered_v1.json')); V4=json.load(open('data/upperdeck_4a_bow_points_v4.json'))['points']; QA=json.load(open('data/upperdeck_4a_bow_arc_ref_v1.json'))['points']; S=11.75; ym=lambda x:1061.7-0.00136*x
deck=[]
for r in V4[-2:]: deck.append((555.0+(r['F_x_px']-7424)/S,(ym(r['F_x_px'])-r['F_y_px'])/S))
for r in QA:
    if r['id']=='C': deck.append((555.0,Y0)); continue
    deck.append((555.0+(r['x_px']-7424)/S,(ym(r['x_px'])-r['y_px'])/S-0.8))
deck=np.array(sorted(deck,key=lambda p:p[0])); ZD=100.0; BL=json.load(open('data/bulwark_line_v3.json')); S10=np.array([[528.03,MK['M45']['Z']],[MK['M48']['X'],MK['M48']['Z']]]); STEPTOP=json.load(open('data/frames_outer_approved_v5.json'))['1']['front']['top'][1][1]; WLZ={'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}; XF1=528.03
planes={}
for j,Yj in enumerate(PL):
    if j==0: planes[j]=dict(Y=Yj,points=[(round(float(x),2),round(float(z),2)) for x,z in zip(X[::25],Z[::25])],note='the rabbet (iron)'); continue
    pts=[(XF1,z_at_y(F1,Yj))]
    for k,Zk in WLZ.items():
        y1=y_at_z(F1,Zk)
        if y1 is None or Yj>=y1-0.3: continue
        P=np.array(W[k]['points_XY']); P=P[np.argsort(P[:,0])]; m=P[:,0]>527.8; Pf=np.vstack([[527.8,y1],P[m]]) if m.any() else np.array([[527.8,y1],P[-1]]); Pf=Pf[np.argsort(-Pf[:,1])]
        x=Pf[-1,0] if Yj<Pf[-1,1] else float(np.interp(Yj,Pf[::-1,1],Pf[::-1,0]))
        if abs(x-pts[-1][0])<1.0 and abs(Zk-pts[-1][1])<2.5: continue
        pts.append((x,Zk))
    if deck[:,1].min()<=Yj<=deck[:,1].max() and Yj<y_at_z(F1,ZD): xd=float(np.interp(Yj,deck[::-1,1],deck[::-1,0])); pts.append((xd,float(np.interp(xd,S10[:,0],S10[:,1]))))
    planes[j]=dict(Y=Yj,points=[(round(float(x),2),round(float(z),2)) for x,z in pts])
for j,p in planes.items(): print('plane %d Y=%.2f: %d points'%(j+1,p['Y'],len(p['points'])), p['points'] if j>0 else '(rabbet)')
json.dump({str(j):p for j,p in planes.items()},open('data/bow_plane_sketch_v4.json','w'),indent=1)
# Rhino
f=r3.File3dm.Read('rhino/RoyalCaroline_frames_outer_half_lifted_v1.3dm'); 
src=r3.File3dm.Read('/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/84b9e1b4-RoyalCaroline_frames_outer_half_lifted_v1.3dm'); f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Color=col; l.Visible=vis; LI[n]=f.Layers.Add(l); return LI[n]
def add(g,ln,name): a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(g,a)
def nurbs(q3,k=3):
    q=np.array(q3,float); keep=[0]+[i for i in range(1,len(q)) if np.linalg.norm(q[i]-q[i-1])>1e-6]; q=q[keep]; kk=min(k,len(q)-1); tck,_=splprep(q.T,k=kk,s=0); t,c,kd=tck
    P=[r3.Point3d(c[0][i],c[1][i],c[2][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,kd,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
lAp=layer('APPROVED_frames_half_+Y_v2',(200,0,0,255)); SL={i:src.Layers[i].Name for i in range(len(src.Layers))}
for o in src.Objects: add(o.Geometry.Duplicate(),lAp,o.Attributes.Name)
lR=layer('RABBET_iron_line_Y1.8',(0,0,0,255)); lP=layer('RABBET_points',(0,0,0,255)); lPl=layer('PLANES_parallel_to_keel',(180,180,255,255)); lSp=layer('PLANE_SPLINES_5',(200,0,200,255))
add(nurbs([(x,1.8,z) for x,z in sel]),lR,'RABBET_iron_Y1.8')
for i,(x,z) in enumerate(sel): a=r3.ObjectAttributes(); a.LayerIndex=lP; a.Name='rabbet_pt%d'%i; f.Objects.AddPoint(r3.Point3d(x,1.8,z),a)
for j,p in planes.items():
    ms=r3.Mesh()
    for (x,z) in ((500,10),(570,10),(570,110),(500,110)): ms.Vertices.Add(x,p['Y'],z)
    ms.Faces.AddFace(0,1,2,3); ms.Normals.ComputeNormals(); add(ms,lPl,'PLANE_%d_Y%.2f'%(j+1,p['Y']))
    q=[(x,p['Y'],z) for x,z in p['points']]
    if len(q)>=2: add(nurbs(q),lSp,'SPLINE_plane%d_Y%.2f'%(j+1,p['Y']))
lD=layer('DECK_EDGE_through_plane_tops',(255,120,0,255)); lF=layer('FRAME1_front_with_v5_top',(255,0,0,255))
tops=[(planes[j]['points'][-1][0],planes[j]['Y'],planes[j]['points'][-1][1]) for j in range(5)]
F5=json.load(open('data/frames_outer_approved_v5.json'))['1']['front']; fy=[(528.03,y,z) for y,z in F5['curve']]+[(528.03,y,z) for y,z in F5['top'][1:]]
add(r3.PolylineCurve([r3.Point3d(*p) for p in fy]),lF,'F01_front_v5'); add(nurbs(tops,2),lD,'deck_edge_tops_plane1-5')
f.Write('rhino/RoyalCaroline_bow_rabbet_and_plane_sketch_v3.3dm',7); print('3dm objects',len(f.Objects))
fig,ax=plt.subplots(figsize=(15,10)); cols=plt.cm.viridis(np.linspace(0,.9,5))
ax.plot(X,Z,'k-',lw=1.6,label='rabbet (iron), one spline'); ax.plot(Q[:,0],Q[:,1],'k.',ms=5)
for j,p in planes.items():
    if j==0: continue
    q=np.array([(x,p['Y'],z) for x,z in p['points']])
    if len(q)>=2:
        tck2,_=splprep(q.T,k=min(3,len(q)-1),s=0); xs,ys,zs=splev(np.linspace(0,1,200),tck2); ax.plot(xs,zs,color=cols[j],lw=1.3,label='plane %d Y=%.2f'%(j+1,p['Y'])); ax.plot(q[:,0],q[:,2],'o',color=cols[j],ms=4)
ax.axvline(528.03,color='r',ls=':',lw=.8)
ax.plot([528.03,528.03],[S10[0,1],STEPTOP],color='tab:orange',lw=2.5,label='step = frame 1 front face (X 528.03)'); ax.plot(S10[:,0],S10[:,1],color='tab:orange',lw=2,label='deck/bulwark line (builder S10, from the step)'); ax.set_xlim(470,570); ax.set_ylim(0,125); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(fontsize=8); ax.set_title('rabbet (one continuous iron line) and the 4 other plane splines (side view)')
fig.savefig('qa/rabbet_iron_and_planes_v3.png',dpi=60,bbox_inches='tight')
