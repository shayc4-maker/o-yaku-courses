import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
S=sys.argv[2]
a=1-np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L')).astype(np.float32)/255
u0,v1=model_to_p5(-20,-8); u1,v0=model_to_p5(450,70); u0,u1,v0,v1=int(u0),int(u1),int(v0),int(v1)
c=a[v0:v1,u0:u1]
gx=cv2.Sobel(c,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(c,cv2.CV_32F,0,1,ksize=3)
k=(15,15); s=4
Jxx=cv2.GaussianBlur(gx*gx,k,s); Jyy=cv2.GaussianBlur(gy*gy,k,s); Jxy=cv2.GaussianBlur(gx*gy,k,s)
tr=Jxx+Jyy; disc=np.sqrt(np.maximum((tr/2)**2-(Jxx*Jyy-Jxy**2),0)); coh=2*disc/(tr+1e-6)
dens=cv2.GaussianBlur(c,k,s)
np.savez_compressed(S+'/out/tex_mid.npz',coh=coh,dens=dens,u0=u0,v0=v0)
fx=json.load(open(S+'/out/frames_X.json'))['X_mm']
def col(x):
    u,_=model_to_p5(x,0); return int(u)-u0
def row(z): _,v=model_to_p5(0,z); return int(v)-v0
res=[]
for i,x in enumerate(fx,1):
    if i==25 or x>440: continue
    # frame column: cross = low coherence & dense
    j=col(x); prof_c=coh[:,j-3:j+4].mean(1); prof_d=dens[:,j-3:j+4].mean(1)
    cross=(prof_c<0.45)&(prof_d>0.3)
    # search upward from Z=-2 for first run of >=10 rows cross
    zb=None
    for r in range(row(-2),row(60),-1):
        if cross[r-10:r+1].all(): zb=float(p5_to_model(0,r+v0)[1]); break
    # gap column (midway to next frame)
    xn=fx[i] if i<len(fx) else x+11
    xg=(x+xn)/2; j2=col(xg); wd=dens[:,j2-2:j2+3].mean(1)
    gb=None
    for r in range(row(-2),row(60),-1):
        if (wd[r-6:r+1]<0.22).all(): gb=float(p5_to_model(0,r+v0)[1]); break
    res.append((i,round(x,1),zb,round(xg,1),gb)); print(i,round(x,1),'block-bottom',None if zb is None else round(zb,1),'| gap',round(xg,1),'white-bottom',None if gb is None else round(gb,1))
json.dump(res,open(S+'/out/mid_meas_auto.json','w'))
