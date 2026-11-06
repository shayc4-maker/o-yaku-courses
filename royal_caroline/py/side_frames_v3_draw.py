# updated side view: sheer plan recalibrated (data/plan_calibration_v2.json), backbone STEP, rabbet old (dashed grey) vs calibrated (black), WL I-VII, silhouettes of the frames: red = before (not raised), blue = raised 0.6 vs keel; planned data untouched
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import map_coordinates
from scipy.interpolate import CubicSpline
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
cal=json.load(open('data/plan_calibration_v2.json'))['sheer_1a']; ax_,bx_,cx_=cal['dX']; az,bz,cz=cal['dZ']
ink=lambda X,Z:(X+ax_+bx_*(X-270)+cx_*Z, Z+az+bz*(X-270)+cz*Z)
cs=lambda p: CubicSpline([q[0] for q in p],[q[1] for q in p],bc_type='natural')
R1=cs(json.load(open('data/rabbet_points_v1.json'))['points']); R2=cs(json.load(open('data/rabbet_points_v2_calibrated.json'))['points'])
WL={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}; W=json.load(open('data/wl_top_points_all.json'))
cols=dict(zip(WL,['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
BB=json.load(open('data/step44_profiles.json')); PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
im=np.array(Image.open('plans/plan_1a_aligned.png').convert('L')).astype(float)
def warped(xl,zl,res=0.085):
    nx=int((xl[1]-xl[0])/res); nz=int((zl[1]-zl[0])/res); Xg=xl[0]+(np.arange(nx)+.5)*res; Zg=zl[1]-(np.arange(nz)+.5)*res; XX,ZZ=np.meshgrid(Xg,Zg); xi,zi=ink(XX,ZZ)
    return map_coordinates(im,[ZR-zi/KZ,(xi-X0)/KX],order=1,cval=255)
F0=json.load(open('data/frames_bottom_side.json')); E3=json.load(open('data/frames_ends_v3.json'))
F1=[]      # new: lower end = the loft built with the approved end points (stations 1-8), NOT raised; upper edge = floor as before
for b_,nm,x,hk,fl,st in F0:
    k='%d_%s'%(int(b_),nm)
    if k in E3: F1.append([b_,nm,x,E3[k][2],fl,st])
def frames(rows):
    byf={}
    for b,nm,x,hk,fl,st in rows: byf.setdefault(int(b),{})[nm]=(x,hk,fl)
    return byf
fig,axs=plt.subplots(2,1,figsize=(19,19),gridspec_kw={'height_ratios':[1.2,1]})
for a,(xl,zl) in zip(axs,(((440,545),(-12,45)),((470,535),(-2,34)))):
    a.imshow(warped(xl,zl),extent=(xl[0],xl[1],zl[0],zl[1]),cmap='gray',vmin=0,vmax=255,aspect='equal',alpha=.5)
    for k,pg in PP.items(): a.plot(*pg.exterior.xy,color='gray',lw=1.0)
    t=np.linspace(430,528,800); a.plot(t,R1(t),color='gray',lw=1.2,ls=':',label='rabbet before (uncalibrated)'); a.plot(t,R2(t),color='k',lw=1.6,ls='--',label='rabbet calibrated')
    for n,z in WL.items():
        xe=float(np.array(W[n]['points_XY'])[:,0].max()); a.axhline(z,color=cols[n],lw=.9); a.plot([xe],[z],'o',color=cols[n],ms=7)
        if xl[0]<xe<xl[1] and zl[0]<z<zl[1]: a.text(xe+.6,z+.5,'%s'%n,color=cols[n],fontsize=10,weight='bold')
    for rows,col,fill,lab in ((F0,'tab:red',True,'frames before'),(F1,'tab:blue',False,'frames: loft with approved end points, not raised')):
        first=True
        for b,d in frames(rows).items():
            xs=[d[k][0] for k in ('m','c','p')]
            if not (xl[0]-8<xs[1]<xl[1]+8): continue
            lo=[d[k][1] for k in ('m','c','p')]; hi=[d[k][2] for k in ('m','c','p')]
            if fill: a.fill(xs+xs[::-1],hi+lo[::-1],color=col,alpha=.45,lw=0,label=lab if first else None)
            else: a.plot(xs+xs[::-1]+[xs[0]],hi+lo[::-1]+[hi[0]],color=col,lw=1.3,label=lab if first else None)
            first=False
            if a is axs[1]: a.text(xs[1],zl[1]-1.5,str(b),ha='center',fontsize=9)
    a.set_xlim(*xl); a.set_ylim(*zl); a.set_ylabel('Z (mm)')
axs[0].legend(fontsize=9,ncol=4,loc='upper left'); axs[0].set_title('Side view, sheer plan recalibrated. Frame silhouettes (outer line at the keel wall .. pocket floor, X-4..X+4): red = before (extended to the wall), blue outline = new loft ends (no raise). Dots = WL bow ends from the top view')
fig.savefig('qa/side_frames_v3.png',dpi=55,bbox_inches='tight')
print('rabbet model Z at X=497.1: before %.2f calibrated %.2f; WL I Z 8.7'%(R1(497.1),R2(497.1)))
