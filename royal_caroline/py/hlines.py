import sys,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
S=sys.argv[2]
B=np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L'))<128
for X in map(float,sys.argv[3].split(',')):
    u0,_=model_to_p5(X-4,0); u1,_=model_to_p5(X+4,0)
    _,vt=model_to_p5(X,140); _,vb=model_to_p5(X,30)
    rows=B[int(vt):int(vb),int(u0):int(u1)].mean(1)
    # hatched band: rows with density 0.35-0.7 continuous for >=8px ; lines: >0.85
    out=[]; i=0; n=len(rows)
    while i<n:
        if rows[i]>0.85:
            j=i
            while j<n and rows[j]>0.85: j+=1
            z=float(p5_to_model(0,int(vt)+(i+j)/2)[1]); out.append('L%.1f'%z); i=j
        else: i+=1
    print('X%4d'%X,' '.join(out))
