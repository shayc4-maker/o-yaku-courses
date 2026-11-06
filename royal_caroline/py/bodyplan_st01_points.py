# Station 1 on the forward body plan (A1/3): a point every 20 mm of arc length on the ink centre (pixels used only to centre the point on the line)
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
cx,zI,k=2433.0,1903.0,8.65/103.3
g=np.array(Image.open('plans/plan_1b_aligned.png').convert('L')).astype(float)
v=np.load('data/hull_stations_all.npz')['ST01'][:,1:]
s=np.r_[0,np.cumsum(np.hypot(*np.diff(v,axis=0).T))]
def px(y,z): return cx+y/k, zI-(z-8.7)/k
def mm(p,q): return (p-cx)*k, 8.7+(zI-q)*k
ZC=106.9   # corner measured on the ink: vertical x=48.65 above Z 106.9
sc=s[np.searchsorted(v[:,1]>0,True)] if False else s[np.argmin(abs(v[:,1]-ZC))]
tgt=[t for t in np.arange(0,sc,10.0) if sc-t>3.0]
out=[]
pts_extra=[(48.65,ZC),(48.65,117.4)]
for i,t in enumerate(tgt):
    j=min(np.searchsorted(s,t),len(s)-1); y,z=v[j]; a=max(j-30,0); b=min(j+30,len(s)-1)
    T=v[b]-v[a]; T/=np.linalg.norm(T); N=np.array([-T[1],T[0]])   # normal in mm
    pc=np.array(px(y,z)); Np=np.array([N[0],-N[1]])               # normal in pixel space
    off=np.arange(-24,25)                                          # +-2 mm
    prof=[]
    for o in off:
        q=pc+Np*o; vals=[g[int(round(q[1]+tt*(-Np[0]))),int(round(q[0]+tt*Np[1]))] for tt in range(-6,7)]
        prof.append(np.mean(vals))
    prof=255-np.array(prof); m=prof>0.35*prof.max()
    # ink run closest to the spline
    idx=np.where(m)[0]; runs=np.split(idx,np.where(np.diff(idx)>1)[0]+1)
    run=min(runs,key=lambda r:abs(off[r].mean())); w=prof[run]; o=(off[run]*w).sum()/w.sum()
    p=pc+Np*o; ym,zm=mm(*p); out.append((i+1,t,ym,zm,o*k))
    print(f'S1.{i+1:02d} arc {t:6.1f}  Y {ym:7.2f}  Z {zm:7.2f}  snap {o*k:+.2f} mm')
n0=len(out)
for q,(ye,ze) in enumerate(pts_extra): out.append((n0+q+1,-1,ye,ze,0.0)); print(f'S1.{n0+q+1:02d} {"corner" if q==0 else "top"}  Y {ye:7.2f}  Z {ze:7.2f}')
box=(2400,500,3150,1950)
fig,ax=plt.subplots(figsize=(9,17),dpi=110); ax.imshow(Image.open('plans/plan_1b_aligned.png').convert('RGB').crop(box),extent=(box[0],box[2],box[3],box[1]))
for n,t,ym,zm,so in out:
    p=px(ym,zm); ax.plot(*p,'o',mfc='none',mec='r',ms=7,mew=1.2); ax.text(p[0]+10,p[1],f'{n}  Y{ym:.1f} Z{zm:.1f}',color='r',fontsize=8,va='center')
P=[px(o[2],o[3]) for o in out[-2:]]; ax.plot([P[0][0],P[1][0]],[P[0][1],P[1][1]],'-',color='#00a000',lw=1)
ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig('qa/bodyplan_st01_points.png',bbox_inches='tight')
np.savetxt('data/st01_points_20mm.csv',np.array(out)[:,[0,2,3]],delimiter=',',header='n,Y,Z',fmt=['%d','%.2f','%.2f'])
