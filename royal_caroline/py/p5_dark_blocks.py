import sys,json,numpy as np,cv2; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from p5map import p5_to_model
im=np.array(Image.open('plans/plan_5_aligned.png').convert('L'))
b=(im<128).astype(np.uint8)
# fill-test: erode so that only solid black blocks survive (>=1.2 mm square)
k=int(1.2/0.0849); er=cv2.erode(b,np.ones((k,k),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(er)
out=[]
for i in range(1,n):
    x,y,w,h,a=st[i]; 
    x0,x1=x-0,x+w+k; y0,y1=y,y+h+k   # restore bbox after erosion
    X0,Z1=p5_to_model(x0,y0); X1,Z0=p5_to_model(x1,y1)
    if 85<Z1<130 and 1.2<(X1-X0)<20 and (Z1-Z0)<14: out.append((round(float(X0),1),round(float(X1),1),round(float(Z0),1),round(float(Z1),1)))
out.sort()
for o in out: print(o)
json.dump(out,open('/tmp/blocks.json','w'))
