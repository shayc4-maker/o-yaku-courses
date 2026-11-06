# 2D side view (plane Y=0, X-Z) of the whole backbone with the UPDATED rabbet line (data/rabbet_points_v3_ends.json), approved station ends, front frames 1-8 (outline from the loft ends to the floor) and all 45 frame positions; Rhino 3dm + PNG
import json,sys,numpy as np,rhino3dm as r3
sys.path.insert(0,'py')
from shapely.geometry import Polygon
from scipy.interpolate import CubicSpline,splprep
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
BB=json.load(open('data/step44_profiles.json')); PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
RB=json.load(open('data/rabbet_points_v3_ends.json'))['points']; R2=json.load(open('data/rabbet_points_v2_calibrated.json'))['points']; ENDS=json.load(open('data/bodyplan_ends_proposed_v1.json'))
XF=json.load(open('data/frames_X.json'))['X_mm']; F0=json.load(open('data/frames_bottom_side.json')); E3=json.load(open('data/frames_ends_v3.json'))
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4}; WL={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}
fr={}
for b in range(1,9):
    d={nm:(x,E3['%d_%s'%(b,nm)][2],fl) for b_,nm,x,hk,fl,st in F0 if int(b_)==b}
    xs=[d[k][0] for k in ('m','c','p')]; lo=[d[k][1] for k in ('m','c','p')]; hi=[d[k][2] for k in ('m','c','p')]
    fr[b]=[(xs[i],lo[i]) for i in range(3)]+[(xs[i],hi[i]) for i in (2,1,0)]
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Visible=vis; l.Color=col; LI[n]=f.Layers.Add(l); return LI[n]
def add(g,ln,name):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(g,a)
def spline(pts):
    q=np.array(pts,float); tck,u=splprep(q.T,k=3,s=0); t,c,k=tck; P=[r3.Point3d(c[0][i],0.0,c[1][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,3,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
poly=lambda pts,closed=False: r3.PolylineCurve([r3.Point3d(x,0.0,z) for x,z in (list(pts)+([pts[0]] if closed else []))])
lB=layer('BACKBONE_profiles',(120,120,120,255)); lR=layer('RABBET_NEW_v3',(0,0,0,255)); lR2=layer('RABBET_v2_ink_calibrated_ref',(150,150,150,255),False); lE=layer('STATION_ENDS_1-8',(0,160,0,255)); lF=layer('FRAMES_1-8_outline',(220,0,0,255)); lX=layer('FRAME_POSITIONS_1-45',(0,0,220,255)); lW=layer('WATERLINES_ref',(230,150,60,255),False)
for k,pg in PP.items(): add(poly(list(pg.exterior.coords)[:-1],True),lB,'BB_'+k)
add(spline(RB),lR,'RABBET_new'); add(spline(R2),lR2,'RABBET_v2')
for n,e in ENDS.items(): f.Objects.AddPoint(r3.Point3d(XST[int(n)],0.0,e['end'][1]),r3.ObjectAttributes()) if False else add(r3.LineCurve(r3.Point3d(XST[int(n)]-1,0,e['end'][1]),r3.Point3d(XST[int(n)]+1,0,e['end'][1])),lE,'ST%s_end'%n)
for b,p in fr.items(): add(poly(p,True),lF,'FRAME_%02d'%b)
for i,x in enumerate(XF):
    b=45-i if False else 46-(i+1)       # frames_X list order: index 0 = builder 45 (stern) ... builder b <-> XF[46-b-1]
    add(r3.LineCurve(r3.Point3d(x,0,-12),r3.Point3d(x,0,-9)),lX,'frame_%d_X%.1f'%(46-i-1 if False else 45-i,x))
for n,z in WL.items(): add(r3.LineCurve(r3.Point3d(-20,0,z),r3.Point3d(570,0,z)),lW,'WL_'+n)
f.Write('rhino/RoyalCaroline_keel_side_2D_new_rabbet_v1.3dm',7); print('3dm objects',len(f.Objects),'frames_X count',len(XF),'first/last',XF[0],XF[-1])
R3=CubicSpline([p[0] for p in RB],[p[1] for p in RB],bc_type='natural'); R2s=CubicSpline([p[0] for p in R2],[p[1] for p in R2],bc_type='natural')
fig,axs=plt.subplots(3,1,figsize=(19,20),gridspec_kw={'height_ratios':[.5,1.2,.9]})
for a,(xl,zl) in zip(axs,(((-20,570),(-14,75)),((440,545),(-12,45)),((-5,120),(-12,25)))):
    for k,pg in PP.items(): a.plot(*pg.exterior.xy,color='gray',lw=1)
    t=np.linspace(30,527.8,1500); a.plot(t,R3(t),'k--',lw=1.7,label='RABBET new'); a.plot(t,R2s(t),color='silver',lw=1,ls=':',label='rabbet v2 (ink)')
    for n,e in ENDS.items(): a.plot([XST[int(n)]],[e['end'][1]],'D',color='lime',mec='k',ms=7)
    for b,p in fr.items(): a.fill([q[0] for q in p],[q[1] for q in p],color='tab:red',alpha=.4,lw=0); a.plot([q[0] for q in p]+[p[0][0]],[q[1] for q in p]+[p[0][1]],color='tab:red',lw=.8)
    for n,z in WL.items(): a.axhline(z,color='#e6a050',lw=.5)
    for i,x in enumerate(XF): a.plot([x,x],[-12,-9.5],color='tab:blue',lw=.8)
    a.set_xlim(*xl); a.set_ylim(*zl); a.set_aspect('equal'); a.set_ylabel('Z (mm)'); a.grid(alpha=.2)
axs[0].legend(ncol=3,fontsize=9,loc='upper center'); axs[0].set_title('Whole backbone (STEP, not moved), updated rabbet (black dashed), approved station ends (green), front frames 1-8 outlines (red), frame positions (blue ticks)')
fig.savefig('qa/keel_side_2D_new_rabbet.png',dpi=55,bbox_inches='tight')
