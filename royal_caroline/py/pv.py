import sys,json,numpy as np
from PIL import Image
a=1-np.array(Image.open(sys.argv[1]).convert('L')).astype(float)/255
B=a>0.5
ST=[4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28]
out={}
for i,x in enumerate(ST):
    st=18-i
    # sample columns offset +-6..10 px from station line (avoid the vertical line itself), average positions
    res=[]
    for dx in (-9,-7,7,9):
        col=B[200:1260,int(round(x+dx))]; rr=[];s=None
        for j,v in enumerate(col):
            if v and s is None: s=j
            if not v and s is not None: rr.append(((s+j-1)/2+200,j-s)); s=None
        res.append(rr)
    # centerline: bottom-most run in 1195..1230
    print(st, [[(round(c,1),w) for c,w in r if c>100] for r in res[1:3]])
