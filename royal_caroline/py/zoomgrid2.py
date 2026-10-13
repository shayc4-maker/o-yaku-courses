import sys; sys.path.insert(0,sys.argv[1])
from p5map import *
from PIL import Image, ImageDraw
S=sys.argv[2]; X0,X1,Z0,Z1,z=map(float,sys.argv[3:8]); out=sys.argv[8]
im=Image.open(S+'/a/'+(sys.argv[9] if len(sys.argv)>9 else 'plan_5_aligned.png')).convert('RGB')
u0,v1=model_to_p5(X0,Z0); u1,v0=model_to_p5(X1,Z1)
c=im.crop((int(u0),int(v0),int(u1),int(v1))); z=int(z); c=c.resize((c.size[0]*z,c.size[1]*z),Image.LANCZOS); d=ImageDraw.Draw(c)
import numpy as np
for X in np.arange(np.ceil(X0),X1,1):
    u,_=model_to_p5(X,Z0); x=(u-int(u0))*z
    col=(0,0,255) if X%10==0 else ((120,120,255) if X%5==0 else (205,205,255))
    d.line([(x,0),(x,c.size[1])],fill=col,width=1)
    if X%5==0: d.text((x+2,2),str(int(X)),fill=(0,0,200))
for Z in np.arange(np.ceil(Z0),Z1,1):
    _,v=model_to_p5(X0,Z); y=(v-int(v0))*z
    col=(255,0,0) if Z%10==0 else ((255,120,120) if Z%5==0 else (255,210,210))
    d.line([(0,y),(c.size[0],y)],fill=col,width=1)
    if Z%5==0: d.text((2,y+1),str(int(Z)),fill=(200,0,0))
c.save(out); print(c.size)
