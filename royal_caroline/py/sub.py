import sys,numpy as np
from PIL import Image
a=1-np.array(Image.open(sys.argv[1]).convert('L')).astype(float)/255
x0,x1=map(int,sys.argv[2:4]); mode=sys.argv[4]
for g in map(float,sys.argv[5:]):
    g=int(round(g))
    if mode=='h': prof=a[g-6:g+7,x0:x1].sum(1)
    else: prof=a[x0:x1,g-6:g+7].sum(0)
    prof=prof-np.median(prof[[0,1,-2,-1]]); prof[prof<0]=0
    c=(np.arange(-6,7)*prof).sum()/prof.sum()+g
    print('%.2f'%c,end=' ')
print()
