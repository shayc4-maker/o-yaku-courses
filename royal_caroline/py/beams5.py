import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
S=sys.argv[2]
a=(np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L'))<128).astype(np.uint8)
# cross-hatch = high local density
dens=cv2.blur(a.astype(np.float32),(9,9))
m=(dens>0.55).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
out=[]
for i in range(1,n):
    x,y,w,h,A=st[i]
    if 18<w<110 and 15<h<80 and A/(w*h)>0.6:
        X0,Z1=p5_to_model(x,y); X1,Z0=p5_to_model(x+w,y+h)
        if Z1>30: out.append(dict(x0=float(X0),x1=float(X1),z0=float(Z0),z1=float(Z1)))
out.sort(key=lambda d:(round(d['z1']/5),d['x0']))
for d in out: print('X %6.1f-%6.1f (%.1f)  Z %5.1f-%5.1f (%.1f)'%(d['x0'],d['x1'],d['x1']-d['x0'],d['z0'],d['z1'],d['z1']-d['z0']))
json.dump(out,open(S+'/out/beam_blocks_p5.json','w'))
