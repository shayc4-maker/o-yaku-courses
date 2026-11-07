# solid dark beam rectangles on plan_1a (sheer plan), model coords; top edge = max Z of the block
import sys,json,numpy as np,cv2; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from p1a_strip import ink,KX,X0,KZ,ZR,im
b=(im<128).astype(np.uint8); k=int(2.0/0.085); er=cv2.erode(b,np.ones((k,k),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(er)
# inverse of ink: model from pixel, iterate (ink is near-identity shift)
def model(px,py):
    xi=px*KX+X0; zi=(ZR-py)*KZ; X,Z=xi,zi
    for _ in range(4):
        a,c=ink(X,Z); X+=xi-a; Z+=zi-c
    return X,Z
out=[]
for i in range(1,n):
    x,y,w,h,a=st[i]; xa,ya,xb,yb=x-0,y,x+w+k,y+h+k
    Xa,Za=model(xa,ya); Xb,Zb=model(xb,yb)
    if -20<Xa<570 and Za>70 and (Xb-Xa)>3 and (Za-Zb)>3 and a>50: out.append(dict(X0=round(Xa,1),X1=round(Xb,1),Zbot=round(Zb,2),Ztop=round(Za,2)))
out.sort(key=lambda o:o['X0'])
for i,o in enumerate(out): o['id']='K%d'%i; print(o)
json.dump(out,open('data/p1a_beam_blocks_v1.json','w'),indent=1)
