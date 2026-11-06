# sheer plan recalibrated (data/plan_calibration_v2.json, affine X,Z from the station verticals and WL I-VII); image warped into MODEL coordinates; approved data untouched. Backbone (STEP), WL I-VII, rabbet spline re-expressed in model coords.
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import affine_transform
from scipy.interpolate import CubicSpline
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
cal=json.load(open('data/plan_calibration_v2.json'))['sheer_1a']; ax_,bx_,cx_=cal['dX']; az,bz,cz=cal['dZ']
ink=lambda X,Z:(X+ax_+bx_*(X-270)+cx_*Z, Z+az+bz*(X-270)+cz*Z)             # model -> ink
def model(Xi,Zi):                                                               # ink -> model (iterate)
    X,Z=Xi,Zi
    for _ in range(4): xi,zi=ink(X,Z); X,Z=X-(xi-Xi),Z-(zi-Zi)
    return X,Z
pts=json.load(open('data/rabbet_points_v1.json'))['points']; P2=[[round(float(a),2) for a in model(x,z)] for x,z in pts]
json.dump(dict(points=P2,note='rabbet points of v1 re-expressed in model coords by plan_calibration_v2'),open('data/rabbet_points_v2_calibrated.json','w'))
R=CubicSpline([p[0] for p in P2],[p[1] for p in P2],bc_type='natural')
WL={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}; W=json.load(open('data/wl_top_points_all.json'))
cols=dict(zip(WL,['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
BB=json.load(open('data/step44_profiles.json')); PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
im=np.array(Image.open('plans/plan_1a_aligned.png').convert('L')).astype(float)
def warped(xl,zl,res=0.085):
    nx=int((xl[1]-xl[0])/res); nz=int((zl[1]-zl[0])/res); out=np.zeros((nz,nx))
    Xg=xl[0]+(np.arange(nx)+.5)*res; Zg=zl[1]-(np.arange(nz)+.5)*res; XX,ZZ=np.meshgrid(Xg,Zg); xi,zi=ink(XX,ZZ)
    from scipy.ndimage import map_coordinates
    return map_coordinates(im,[ZR-zi/KZ,(xi-X0)/KX],order=1,cval=255)
fig,axs=plt.subplots(3,1,figsize=(19,22),gridspec_kw={'height_ratios':[0.5,1.1,0.8]})
for a,(xl,zl) in zip(axs,(((-20,570),(-14,75)),((440,545),(-12,45)),((220,330),(-12,14)))):
    a.imshow(warped(xl,zl),extent=(xl[0],xl[1],zl[0],zl[1]),cmap='gray',vmin=0,vmax=255,aspect='equal',alpha=.55)
    for k,pg in PP.items(): a.plot(*pg.exterior.xy,color='gray',lw=1.0)
    t=np.linspace(P2[0][0],P2[-1][0],1500); a.plot(t,R(t),color='k',lw=1.6,ls='--',label='rabbet (calibrated)')
    for n,z in WL.items():
        xe=float(np.array(W[n]['points_XY'])[:,0].max()); a.axhline(z,color=cols[n],lw=1.1,label='WL %s Z=%.1f'%(n,z)); a.plot([xe],[z],'o',color=cols[n],ms=7)
        if xl[0]<xe<xl[1] and zl[0]<z<zl[1]: a.text(xe+1,z+0.8,'%s %.1f'%(n,xe),color=cols[n],fontsize=9,weight='bold')
    a.set_xlim(*xl); a.set_ylim(*zl); a.set_ylabel('Z (mm)')
axs[0].legend(fontsize=8,ncol=4,loc='upper center'); axs[0].set_title('Sheer plan recalibrated into model coordinates (affine from verticals + WL I-VII); backbone STEP, WL and bow ends unchanged')
fig.savefig('qa/side_calibrated.png',dpi=55,bbox_inches='tight')
xs=np.linspace(440,531,9101)
for nm,z in (('I',8.7),('II',17.4),('III',26.1)):
    xe=float(np.array(W[nm]['points_XY'])[:,0].max()); x=xs[np.argmin(abs(R(xs)-z))]; print(nm,'rabbet X %.2f | WL top-view end %.1f | diff %.2f'%(x,xe,xe-x))
print('rabbet model Z at X=30,270,450,500,520,528:',[round(float(R(x)),2) for x in (30,270,450,500,520,528)])
