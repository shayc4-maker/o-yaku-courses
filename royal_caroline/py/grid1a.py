import sys,numpy as np
from PIL import Image, ImageDraw
S=sys.argv[1]; X0,X1,Z0,Z1=map(float,sys.argv[2:6]); out=sys.argv[6]; z=int(sys.argv[7])
K=1000/244.8/48; px=lambda X:X/K+4194.98; py=lambda Z:2104.73-Z*102.1/8.689
im=Image.open(S+'/a/plan_1a_aligned.png').convert('RGB')
u0,u1,v0,v1=int(px(X0)),int(px(X1)),int(py(Z1)),int(py(Z0))
c=im.crop((u0,v0,u1,v1)); c=c.resize((c.size[0]*z,c.size[1]*z)); d=ImageDraw.Draw(c)
for X in range(int(np.ceil(X0)),int(X1)+1):
    x=(px(X)-u0)*z; d.line([(x,0),(x,c.size[1])],fill=(0,0,255) if X%10==0 else ((150,150,255) if X%5==0 else (228,228,255)))
    if X%10==0: d.text((x+2,2),str(X),fill=(0,0,200))
for Z in range(int(np.ceil(Z0)),int(Z1)+1):
    y=(py(Z)-v0)*z; d.line([(0,y),(c.size[0],y)],fill=(255,0,0) if Z%10==0 else ((255,150,150) if Z%5==0 else (255,228,228)))
    if Z%10==0: d.text((2,y+1),str(Z),fill=(200,0,0))
c.save(out); print(c.size)
