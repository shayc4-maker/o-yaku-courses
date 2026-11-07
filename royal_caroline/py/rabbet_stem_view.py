# side view of the first 5 frames on the keel plan (sheer plan plan_1a recalibrated into model coordinates) with the rabbet v3, frame lower ends, STEP stem profiles and the plane-1 (Y=2.65) bow points; used to continue the rabbet up the stem
import sys,json,numpy as np
sys.path.insert(0,'py')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import map_coordinates
from scipy.interpolate import CubicSpline
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
cal=json.load(open('data/plan_calibration_v2.json'))['sheer_1a']; ax_,bx_,cx_=cal['dX']; az,bz,cz=cal['dZ']
ink=lambda X,Z:(X+ax_+bx_*(X-270)+cx_*Z, Z+az+bz*(X-270)+cz*Z)
im=np.array(Image.open('plans/plan_1a_aligned.png').convert('L')).astype(float)
def warped(xl,zl,res=0.085):
    nx=int((xl[1]-xl[0])/res); nz=int((zl[1]-zl[0])/res); Xg=xl[0]+(np.arange(nx)+.5)*res; Zg=zl[1]-(np.arange(nz)+.5)*res; XX,ZZ=np.meshgrid(Xg,Zg); xi,zi=ink(XX,ZZ)
    return map_coordinates(im,[ZR-zi/KZ,(xi-X0)/KX],order=1,cval=255)
A=json.load(open('data/frames_outer_approved_v1.json')); RB=json.load(open('data/rabbet_points_v3_ends.json'))['points']; R3=CubicSpline([p[0] for p in RB],[p[1] for p in RB],bc_type='natural')
BB=json.load(open('data/step44_profiles.json')); PL=json.load(open('data/bow_plank_splines_v1.json'))
fig,axs=plt.subplots(2,1,figsize=(18,22),gridspec_kw={'height_ratios':[1,1.25]})
for a,(xl,zl) in zip(axs,(((440,570),(-12,45)),((480,615),(15,125)))):
    a.imshow(warped(xl,zl),extent=(xl[0],xl[1],zl[0],zl[1]),cmap='gray',vmin=0,vmax=255,aspect='equal',alpha=.7)
    for k,v in BB.items():
        pg=Polygon(max(v,key=lambda q:Polygon(q).area))
        if pg.bounds[2]>470: a.plot(*pg.exterior.xy,color='gray',lw=.7)
    t=np.linspace(430,527.8,300); a.plot(t,R3(t),'k--',lw=1.6,label='rabbet v3')
    for b in range(1,6):
        for nm,col in (('back','tab:blue'),('mid','k'),('front','tab:red')):
            v=A[str(b)][nm]; C=np.array(v['curve']); a.plot([v['X']],[C[0,1]],'o',color=col,ms=5); a.text(v['X'],C[0,1]-2.2,str(b) if nm=='mid' else '',fontsize=9,ha='center')
    pl=PL['0']['points']; a.plot([p[1] for p in pl],[p[2] for p in pl],'m+',ms=11,mew=1.6,label='plane 1 (Y=2.65) points')
    a.set_xlim(*xl); a.set_ylim(*zl); a.grid(alpha=.25); a.legend(fontsize=8,loc='upper left')
axs[0].set_title('side view, frames 1-5 (circles = lower end of the face lines: blue back, black mid, red front) on the recalibrated keel plan, rabbet v3 (dashed)')
axs[1].set_title('bow / stem zone: where the rabbet continues up the stem (magenta = plane-1 points from the waterline ends and the deck)')
fig.savefig('qa/rabbet_stem_view_v1.png',dpi=55,bbox_inches='tight')
