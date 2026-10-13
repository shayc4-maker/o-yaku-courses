import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
S=sys.argv[2]
a=1-np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L')).astype(np.float32)/255
u0,v1=model_to_p5(-20,-8); u1,v0=model_to_p5(560,70); u0,u1,v0,v1=int(u0),int(u1),int(v0),int(v1)
c=a[v0:v1,u0:u1]
gx=cv2.Sobel(c,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(c,cv2.CV_32F,0,1,ksize=3)
k=(11,11); s=3
Jxx=cv2.GaussianBlur(gx*gx,k,s); Jyy=cv2.GaussianBlur(gy*gy,k,s); Jxy=cv2.GaussianBlur(gx*gy,k,s)
tr=Jxx+Jyy; disc=np.sqrt(np.maximum((tr/2)**2-(Jxx*Jyy-Jxy**2),0)); coh=2*disc/(tr+1e-6)
ang=0.5*np.degrees(np.arctan2(2*Jxy,Jxx-Jyy))     # gradient orientation
dens=cv2.GaussianBlur(c,k,s)
med=np.median(ang[(coh>0.6)&(dens>0.3)]); print('hatch gradient angle',med)
hatch=(coh>0.5)&(np.abs(((ang-med+90)%180)-90)<20)&(dens>0.25)
cross=(coh<0.4)&(dens>0.35)
np.savez_compressed(S+'/out/cls_keel.npz',hatch=hatch,cross=cross,u0=u0,v0=v0)
vis=np.full(c.shape+(3,),255,np.uint8); vis[hatch]=(90,90,230); vis[cross]=(230,60,60)
Image.fromarray(vis).save(S+'/cls_keel.png')
