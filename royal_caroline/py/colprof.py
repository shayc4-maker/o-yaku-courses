import sys; sys.path.insert(0,'py'); from p5map import *
import numpy as np; from PIL import Image
im=np.array(Image.open('a/plan_5_aligned.png').convert('L'))<128
for nm,za,zb in [('false',-9.0,-7.9),('keel_lo',-6.8,-4.5),('keel_hi',-3.5,-0.8),('hog',0.0,0.6),('dw',1.1,1.7)]:
    _,v0=model_to_p5(0,zb); _,v1=model_to_p5(0,za)
    u0,_=model_to_p5(0,0); u1,_=model_to_p5(560,0)
    col=im[int(v0):int(v1)+1,int(u0):int(u1)].mean(0)
    X=p5_to_model(np.arange(int(u0),int(u1)),0)[0]
    pk=[round(float(X[i]),1) for i in range(1,len(col)-1) if col[i]>0.85 and col[i]>=col[i-1] and col[i]>=col[i+1]]
    # merge close
    m=[]; 
    for p in pk:
        if not m or p-m[-1]>0.6: m.append(p)
    print(nm,m)
