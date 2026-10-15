import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
a=np.array(Image.open(sys.argv[1]).convert('L'))<128
H,W=a.shape
def runs(v,off):
    out=[];c=v[0];s=0
    for i in range(1,len(v)):
        if v[i]!=c: out.append(('#' if c else '.',s+off,i-s)); c=v[i]; s=i
    out.append(('#' if c else '.',s+off,len(v)-s)); return out
# widest outer extents of B2 (left half of sheet) and B3
for y in range(1300,1900,50):
    r=a[y,:]; L=np.argmax(r[700:2700])+700; R=2700-np.argmax(r[700:2700][::-1])
    print('B2 y',y,'L',L,'R',R,'w',R-L)
for y in [1500,1600,1700]:
    print(y,[t for t in runs(a[y,830:1050],830) if t[2]>=2])
print('--- vertical profiles near keel')
for x in [1300,1450,1550,1650]:
    print(x,[t for t in runs(a[1950:2350,x],1950) if t[2]>=2])
