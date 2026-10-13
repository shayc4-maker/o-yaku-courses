import sys,numpy as np
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
S=sys.argv[1]; name=sys.argv[2]; X0,X1,Y0,Y1=map(float,sys.argv[3:7]); out=sys.argv[7]
A=0.08528; B=-67.8; CY=1086
px=lambda X:(X-B)/A; py=lambda Y: CY-Y/A
im=Image.open(S+'/t/'+name+'.tif').convert('L').convert('RGB')
c=im.crop((int(px(X0)),int(py(Y1)),int(px(X1)),int(py(Y0)))); d=ImageDraw.Draw(c)
ox,oy=int(px(X0)),int(py(Y1))
for X in range(int(np.ceil(X0)),int(X1)):
    if X%5: continue
    x=px(X)-ox; d.line([(x,0),(x,c.size[1])],fill=(0,0,255) if X%10==0 else (170,170,255),width=1)
    if X%10==0: d.text((x+2,2),str(X),fill=(0,0,200))
for Y in range(int(np.ceil(Y0)),int(Y1)):
    if Y%5: continue
    y=py(Y)-oy; d.line([(0,y),(c.size[0],y)],fill=(255,0,0) if Y%10==0 else (255,170,170),width=1)
    if Y%10==0: d.text((2,y+1),str(Y),fill=(200,0,0))
c.save(out); print(c.size)
