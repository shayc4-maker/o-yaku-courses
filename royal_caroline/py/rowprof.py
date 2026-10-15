import sys; sys.path.insert(0,'py'); from p5map import *
import numpy as np; from PIL import Image
im=np.array(Image.open('a/plan_5_aligned.png').convert('L'))<128
for xa,xb in [(70,120),(150,200),(230,280),(320,370),(400,440)]:
    u0,_=model_to_p5(xa,0); u1,_=model_to_p5(xb,0)
    out=[]
    for Z in np.arange(-10,4,0.1):
        _,v=model_to_p5(0,Z); out.append(im[int(round(float(v))),int(u0):int(u1)].mean())
    out=np.array(out); Zs=np.arange(-10,4,0.1)
    pk=[ (round(Zs[i],1),round(out[i],2)) for i in range(1,len(out)-1) if out[i]>0.75 and out[i]>=out[i-1] and out[i]>=out[i+1]]
    print(xa,xb,pk)
