# dark (solid or hatched) beam-end rectangles under the top deck band on plan_5: density map, components, top edge
import sys,json,numpy as np,cv2; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from p5map import p5_to_model,model_to_p5
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
im=np.array(Image.open('plans/plan_5_aligned.png').convert('L')); b=(im<128).astype(np.float32)
d=cv2.blur(b,(int(0.9/0.0849),)*2); m=(d>0.55).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((9,9),np.uint8))
n,lab,st,_=cv2.connectedComponentsWithStats(m)
out=[]
for i in range(1,n):
    x,y,w,h,a=st[i]; X0,Zt=p5_to_model(x,y); X1,Zb=p5_to_model(x+w,y+h)
    if 108<Zt<128 and 1.8<(X1-X0)<9 and 1.0<(Zt-Zb)<5: out.append((round(float(X0),1),round(float(X1),1),round(float(Zb),2),round(float(Zt),2)))
out.sort()
for o in out: print(o)
json.dump(out,open('/tmp/beams.json','w'))
