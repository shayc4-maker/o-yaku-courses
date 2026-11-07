# BOW: 5 splines in 5 planes parallel to the keel (Y = const = inner faces of the 5 hawse-timber planks: 2.65 + 8.97*j, j=0..4), perpendicular to the transverse frames. Points: (a) at the front face of frame 1 (X 528.03 = station 1, approved) the Z where station 1 reaches Y_j; (b) waterlines IV-VII forward of station 1: X where the waterline reaches Y_j (waterline points beyond 527.8 + the station 1 crossing at the same Z); (c) the upper deck (plan_4a frame-line points F8,F9 + arc Q1-Q5 (outer line minus 0.8 mm plank) + C): X where the deck outline reaches Y_j, at the deck height Z=100 (inferred from the approved frames: the plan frame line matches the frames at Z~100 near the bow). Frames govern (width before planking). Spline = interpolating cubic through the points. For approval.
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
C=json.load(open('data/bodyplan_centered_v1.json')); ENDS=json.load(open('data/bodyplan_ends_centered_v1.json')); W=json.load(open('data/wl_top_centered_v1.json'))
L1=np.vstack([ENDS['1']['end'],np.array(C['1']['curve'])]); WLZ={'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}; XF1=528.03; Y0=2.65; DY=(47.5-Y0)/5; PLANES=[Y0+DY*j for j in range(5)]
def z_at_y(L,y):
    for i in range(len(L)-1):
        if (L[i,0]-y)*(L[i+1,0]-y)<=0 and L[i,0]!=L[i+1,0]: return float(L[i,1]+(y-L[i,0])/(L[i+1,0]-L[i,0])*(L[i+1,1]-L[i,1]))
    return None
def y_at_z(L,z):
    i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0]
    return float(np.interp(z,L[:,1],L[:,0])) if len(i) else None
# upper deck outline (X registered at C = stem aft face 555.0; Y from the symmetric mid-line; Z=100), frame line
V4=json.load(open('data/upperdeck_4a_bow_points_v4.json'))['points']; Q=json.load(open('data/upperdeck_4a_bow_arc_ref_v1.json'))['points']; S=11.75; ym=lambda x:1061.7-0.00136*x
deck=[]
for r in V4[-2:]: deck.append((555.0+(r['F_x_px']-7424)/S,(ym(r['F_x_px'])-r['F_y_px'])/S))
for r in Q:
    if r['id']=='C': deck.append((555.0,Y0)); continue
    deck.append((555.0+(r['x_px']-7424)/S,(ym(r['x_px'])-r['y_px'])/S-0.8))          # outer line -> frame line (plank 0.8)
deck=np.array(sorted(deck,key=lambda p:p[0])); ZD=100.0
print('upper deck outline points (X, Y frame line) at Z=%.0f:'%ZD,[(round(x,1),round(y,1)) for x,y in deck])
res={}
for j,Yj in enumerate(PLANES):
    pts=[]; za=z_at_y(L1,Yj); pts.append(('station 1 (front face of frame 1)',XF1,za))
    for k,Zk in WLZ.items():
        y1=y_at_z(L1,Zk)
        if y1 is None or (j>0 and Yj>=y1-0.3): continue
        P=np.array(W[k]['points_XY']); P=P[np.argsort(P[:,0])]; m=P[:,0]>527.8; Pf=np.vstack([[527.8,y1],P[m]]) if m.any() else np.array([[527.8,y1],P[-1]])
        Pf=Pf[np.argsort(-Pf[:,1])]            # Y descending toward the stem
        if Yj<Pf[-1,1]: x=Pf[-1,0]
        else: x=float(np.interp(Yj,Pf[::-1,1],Pf[::-1,0]))
        if pts and abs(x-pts[-1][1])<1.0 and abs(Zk-pts[-1][2])<2.5: continue          # redundant with the previous point (would only make a kink)
        pts.append(('WL '+k,x,Zk))
    xd=float(np.interp(Yj,deck[::-1,1],deck[::-1,0])) if deck[:,1].min()<=Yj<=deck[:,1].max() else None
    yd_max=y_at_z(L1,ZD)
    if xd is not None and Yj<yd_max: pts.append(('upper deck',xd,ZD))
    res[j]=dict(Y=Yj,points=[(n,round(x,2),round(z,2)) for n,x,z in pts])
    print('plane %d Y=%.2f:'%(j+1,Yj),res[j]['points'])
json.dump({str(k):v for k,v in res.items()},open('data/bow_plank_splines_v1.json','w'),indent=1)
# Rhino + image
f=r3.File3dm.Read('rhino/RoyalCaroline_bow_lines_in_space_v1.3dm'); LI={f.Layers[i].Name:i for i in range(len(f.Layers))}
def layer(n,col):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Color=col; LI[n]=f.Layers.Add(l); return LI[n]
lS=layer('BOW_5_splines_planes_parallel_to_keel',(200,0,200,255)); lP=layer('BOW_5_splines_points',(120,0,120,255))
cols=plt.cm.viridis(np.linspace(0,.9,5)); fig,ax=plt.subplots(figsize=(15,10)); curves={}
for j,r in res.items():
    q=np.array([(x,r['Y'],z) for _,x,z in r['points']]); 
    if len(q)>=2:
        tck,u=splprep(q.T,k=min(3,len(q)-1),s=0); t,c,k=tck; P=[r3.Point3d(c[0][i],c[1][i],c[2][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,k,P); tt=t[1:-1]
        for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
        a=r3.ObjectAttributes(); a.LayerIndex=lS; a.Name='BOW_plane%d_Y%.2f'%(j+1,r['Y']); f.Objects.Add(nc,a)
        xs,ys,zs=splev(np.linspace(0,1,200),tck); ax.plot(xs,zs,color=cols[j],lw=1.4,label='plane %d Y=%.2f'%(j+1,r['Y']))
    for n,x,z in r['points']:
        pa=r3.ObjectAttributes(); pa.LayerIndex=lP; pa.Name='plane%d_%s'%(j+1,n); f.Objects.AddPoint(r3.Point3d(x,r['Y'],z),pa); ax.plot(x,z,'o',color=cols[j],ms=5)
f.Write('rhino/RoyalCaroline_bow_lines_in_space_v2.3dm',7)
from shapely.geometry import Polygon
BB=json.load(open('data/step44_profiles.json'))
for k,v in BB.items():
    pg=Polygon(max(v,key=lambda q:Polygon(q).area))
    if pg.bounds[2]>500: ax.plot(*pg.exterior.xy,color='gray',lw=.8)
RB=json.load(open('data/rabbet_points_v3_ends.json'))['points']; ax.plot([p[0] for p in RB if p[0]>480],[p[1] for p in RB if p[0]>480],'k--',lw=1)
ax.axvline(528.03,color='r',ls=':',lw=.8); ax.set_xlim(500,615); ax.set_ylim(15,125); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(fontsize=8); ax.set_title('bow: 5 splines in planes parallel to the keel (side view X-Z), STEP stem/head profiles (grey), rabbet; red = front face of frame 1')
fig.savefig('qa/bow_plank_splines_v1.png',dpi=60,bbox_inches='tight')
