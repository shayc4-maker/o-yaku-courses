# 2D body plan Rhino file (plane X=-80 like the builder lines file: aft 9-18 at +Y, forward 1-8 at -Y, station 8 both) with the approved station splines + the approved END hooks of stations 1-8, WL I-VII levels, centreline, keel half-width; plus an image of the plan with the same lines on the original body plans
import json,sys,numpy as np,rhino3dm as r3
sys.path.insert(0,'py')
from scipy.interpolate import splprep
C=json.load(open('data/bodyplan_splines_v1.json')); ENDS=json.load(open('data/bodyplan_ends_proposed_v1.json')); STR={1:2,2:2}; XP=-80.0
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n; l.Visible=vis; l.Color=col; LI[n]=f.Layers.Add(l); return LI[n]
def add(g,ln,name):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=name; f.Objects.Add(g,a)
def spline(pts2,sg):
    q=np.array(pts2,float); keep=[0]+[i for i in range(1,len(q)) if np.hypot(*(q[i]-q[i-1]))>1e-6]; q=q[keep]; tck,u=splprep(q.T,k=3,s=0); t,c,k=tck
    P=[r3.Point3d(XP,sg*c[0][i],c[1][i]) for i in range(len(c[0]))]; nc=r3.NurbsCurve.Create(False,3,P); tt=t[1:-1]
    for i in range(len(nc.Knots)): nc.Knots[i]=float(tt[i])
    return nc
lF=layer('STATIONS_forward_1-8',(220,0,0,255)); lA=layer('STATIONS_aft_9-18',(0,0,220,255)); lE=layer('END_HOOKS_1-8_new',(0,160,0,255)); lG=layer('GUIDES_WL_centre_keel',(150,150,150,255)); lP=layer('POINTS_approved',(120,0,0,255),False); lPE=layer('POINTS_end',(0,160,0,255))
for n in range(1,19):
    P=C[str(n)]['points']; k=STR.get(n,0); q=P[:-1] if k else P; sides=[]
    if n>=8: sides.append((1,lA))
    if n<=8: sides.append((-1,lF))
    for sg,ly in sides:
        add(spline(q,sg),ly,f'ST{n:02d}')
        if k: add(r3.LineCurve(r3.Point3d(XP,sg*P[-2][0],P[-2][1]),r3.Point3d(XP,sg*P[-1][0],P[-1][1])),ly,f'ST{n:02d}_straight_top')
        if sg==-1 and str(n) in ENDS:
            e=ENDS[str(n)]; add(r3.LineCurve(r3.Point3d(XP,-e['end'][0],e['end'][1]),r3.Point3d(XP,-P[0][0],P[0][1])),lE,f'ST{n:02d}_end_hook')
            pa=r3.ObjectAttributes(); pa.LayerIndex=lPE; pa.Name=f'ST{n:02d}_end_pt'; f.Objects.AddPoint(r3.Point3d(XP,-e['end'][0],e['end'][1]),pa)
        pa=r3.ObjectAttributes(); pa.LayerIndex=lP; pa.Name=f'ST{n:02d}_pt'
        for y,z in P: f.Objects.AddPoint(r3.Point3d(XP,sg*y,z),pa)
for nm,z in (('I',8.7),('II',17.4),('III',26.1),('IV',34.8),('V',43.4),('VI',52.1),('VII',69.5)): add(r3.LineCurve(r3.Point3d(XP,-85,z),r3.Point3d(XP,85,z)),lG,'WL_'+nm)
add(r3.LineCurve(r3.Point3d(XP,0,-5),r3.Point3d(XP,0,140)),lG,'centreline')
for sg in (1,-1): add(r3.LineCurve(r3.Point3d(XP,sg*2.65,-5),r3.Point3d(XP,sg*2.65,40)),lG,'keel_half_width')
f.Write('rhino/RoyalCaroline_bodyplan_new_v1.3dm',7); print('3dm objects',len(f.Objects))
# image on the original plans
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import bodyplan_points_all as B
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SF=1.0325; COL=plt.cm.tab20(np.linspace(0,1,20))
for nm,plan,cf,box,ns,out,fs in (('fwd','plans/plan_1b_aligned.png','fwd',(2380,500,3750,2150),range(1,9),'qa/bodyplan_new_fwd.png',(13,15.7)),('aft','plans/plan_1a_aligned.png','aft',(1250,420,2400,2300),range(8,19),'qa/bodyplan_new_aft.png',(10,18.6))):
    im=Image.open(plan).convert('RGB').crop(box); fig,ax=plt.subplots(figsize=fs,dpi=100); ax.imshow(im,extent=(box[0],box[2],box[3],box[1]))
    for n in ns:
        L=np.array(C[str(n)]['curve']); x,y=B.px(B.CFG[cf],L[:,0]/(SF if cf=='aft' else 1.0),L[:,1]); ax.plot(x,y,'-',color=COL[(n*3)%20],lw=1.3); ax.text(x[-1],y[-1]-16,str(n),color=COL[(n*3)%20],fontsize=11,weight='bold',ha='center')
        if cf=='fwd' and str(n) in ENDS:
            e=ENDS[str(n)]; P0=C[str(n)]['points'][0]; xs,ys=B.px(B.CFG[cf],np.array([e['end'][0],P0[0]]),np.array([e['end'][1],P0[1]])); ax.plot(xs,ys,'-',color='lime',lw=2); ax.plot(xs[:1],ys[:1],'o',mfc='none',mec='lime',ms=9,mew=1.6)
    ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig(out,bbox_inches='tight'); plt.close(fig)
