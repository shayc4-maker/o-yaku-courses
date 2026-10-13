import sys,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
B=np.array(Image.open(sys.argv[1]).convert('L'))<128
x0,y0,y1,cx=map(int,sys.argv[2:6])
for dx in range(-700,701,100):
    x=cx+dx; col=B[y0:y1,x-3:x+4].mean(1)>0.6
    runs=[];s=None
    for i,v in enumerate(col):
        if v and s is None: s=i
        if not v and s is not None: runs.append((s+y0,i-s)); s=None
    print(dx,runs)
