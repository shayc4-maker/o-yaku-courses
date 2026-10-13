import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *; from hull import section
from PIL import Image
S=sys.argv[2]; O=S+'/out'
B=np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L'))<128
fx=json.load(open(O+'/frames_X.json'))['X_mm']
out=[]
for i,X in enumerate(fx,1):
    zr=section(X,kind='pchip')[0,1]
    u,v=model_to_p5(X,zr); u=int(round(float(u))); v=int(round(float(v)))
    # horizontal-line score: fraction dark over block width (+-22 px) per row, going up from seat
    rows=[]
    for y in range(v-4,v-260,-1):
        rows.append((y,B[y,u-20:u+21].mean()))
    rows=np.array(rows)
    # candidate: first row above v-25 where fraction>0.9 (a horizontal edge)
    top=None
    for y,f in rows:
        if y<v-25 and f>0.92: top=y; break
    zt=None if top is None else float((2045-top)*K*R5-9.37)
    out.append((i,round(X,2),round(float(zr),2),None if zt is None else round(zt,2), None if zt is None else round(zt-zr,2)))
    print(out[-1])
json.dump(out,open(O+'/throat_raw.json','w'))
