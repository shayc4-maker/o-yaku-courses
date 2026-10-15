import sys,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
S=sys.argv[2]
a=np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L')).astype(np.float32)/255
u0,v1=model_to_p5(430,-12); u1,v0=model_to_p5(612,124); u0,u1,v0,v1=int(u0),int(u1),int(v0),int(v1)
c=1-a[v0:v1,u0:u1]
gx=cv2.Sobel(c,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(c,cv2.CV_32F,0,1,ksize=3)
k=(21,21)
Jxx=cv2.GaussianBlur(gx*gx,k,6); Jyy=cv2.GaussianBlur(gy*gy,k,6); Jxy=cv2.GaussianBlur(gx*gy,k,6)
tr=Jxx+Jyy; det=Jxx*Jyy-Jxy**2; disc=np.sqrt(np.maximum((tr/2)**2-det,0))
l1=tr/2+disc; l2=tr/2-disc; coh=(l1-l2)/(l1+l2+1e-6)
dens=cv2.GaussianBlur(c,k,6); ang=0.5*np.degrees(np.arctan2(2*Jxy,Jxx-Jyy))
np.savez_compressed(S+'/out/tex_bow.npz',coh=coh,dens=dens,ang=ang,u0=u0,v0=v0)
cls=np.zeros(c.shape+(3,),np.uint8)+255
hatch=(dens>0.22)&(coh>0.55); cross=(dens>0.30)&(coh<=0.55)
cls[hatch]=(80,80,220); cls[cross]=(220,60,60)
out=(0.5*cls+0.5*np.dstack([255*(1-c)]*3)).astype(np.uint8)
Image.fromarray(out).resize((out.shape[1]//2,out.shape[0]//2)).save(S+'/tex_bow.png')
print(out.shape, 'angle of hatch median',np.median(ang[hatch]))
