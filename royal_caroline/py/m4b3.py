import sys, numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d
Image.MAX_IMAGE_PIXELS=None
a=np.array(Image.open(sys.argv[1]).convert('L'))<128
x0,x1=int(sys.argv[2]),int(sys.argv[3]); side=sys.argv[4]
xs=np.arange(x0,x1); wf=[]
for x in xs:
    col=a[:,x]
    if side=='top':
        t=np.argmax(col[60:1200])+60; seg=col[t+30:t+48]
    else:
        b=2300-np.argmax(col[1200:2300][::-1]); seg=col[b-48:b-30]
    wf.append(1-seg.mean())
wf=uniform_filter1d(np.array(wf),5); w=wf>0.55
runs=[];s=None
for i,v in enumerate(w):
    if v and s is None: s=i
    if not v and s is not None:
        if i-s>18: runs.append((s+x0,i+x0))
        s=None
c=np.array([(s+e)/2 for s,e in runs]); p=np.diff(c)
print(len(c),'spaces'); print('centers',np.round(c).astype(int).tolist()); print('pitch',np.round(p).astype(int).tolist())
