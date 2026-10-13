import sys, numpy as np
from PIL import Image
a=np.array(Image.open(sys.argv[1]).convert('L'))<128
lo,hi=int(sys.argv[2]),int(sys.argv[3])
for y in map(int,sys.argv[4:]):
    r=a[y,lo:hi]; xs=[];s=None
    for i,v in enumerate(r):
        if v and s is None: s=i
        if not v and s is not None: xs.append(((s+i-1)/2+lo, i-s)); s=None
    print(y,len(xs),[(round(x),w) for x,w in xs])
