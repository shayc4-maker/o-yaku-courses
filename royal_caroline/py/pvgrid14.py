import sys,numpy as np
from PIL import Image, ImageDraw
S=sys.argv[1]; X0,X1,Y0,Y1=map(float,sys.argv[2:6]); out=sys.argv[6]; z=int(sys.argv[7]) if len(sys.argv)>7 else 1
PV=np.array([4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28])
PR=np.array([4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40])
f=np.polyfit(PV,PR,1); LO=(-0.00716,1271.3); K=1000/244.8/48
px=lambda X:(X/K+PR[0]-f[1])/f[0]
py=lambda X,Y: np.polyval(LO,px(X))-Y/K
im=Image.open(S+'/a/plan_1b_aligned.png').convert('RGB')
u0,u1=int(px(X0)),int(px(X1)); v0,v1=int(py(X0,Y1))-5,int(py(X0,Y0))+5
c=im.crop((u0,v0,u1,v1)); c=c.resize((c.size[0]*z,c.size[1]*z)); d=ImageDraw.Draw(c)
for X in range(int(np.ceil(X0)),int(X1)+1):
    x=(px(X)-u0)*z
    d.line([(x,0),(x,c.size[1])],fill=(0,0,255) if X%10==0 else ((150,150,255) if X%5==0 else (225,225,255)))
    if X%10==0: d.text((x+2,2),str(X),fill=(0,0,200))
for Y in range(int(np.ceil(Y0)),int(Y1)+1):
    y=(py((X0+X1)/2,Y)-v0)*z
    d.line([(0,y),(c.size[0],y)],fill=(255,0,0) if Y%10==0 else ((255,150,150) if Y%5==0 else (255,225,225)))
    if Y%10==0: d.text((2,y+1),str(Y),fill=(200,0,0))
c.save(out); print(c.size)
