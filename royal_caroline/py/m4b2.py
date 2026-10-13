import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
a=np.array(Image.open(sys.argv[1]).convert('L'))<128
x0,x1=int(sys.argv[2]),int(sys.argv[3])
# find band: for each column, locate rows; use fixed local window by tracking top dark edge (outer planking line)
pxm=244.3
res=[]
for x in range(x0,x1):
    col=a[60:400,x]; top=np.argmax(col)+60
    res.append(top)
top=np.median(res); print('median top edge y',top)
# frame band approx top+25..top+55 ; compute white fraction per column with local top
wf=[]
for i,x in enumerate(range(x0,x1)):
    t=res[i]; seg=a[t+27:t+50,x]; wf.append(1-seg.mean())
wf=np.array(wf); sm=np.convolve(wf,np.ones(5)/5,'same')
w=sm>float(sys.argv[4])
runs=[];s=None
for i,v in enumerate(w):
    if v and s is None: s=i
    if not v and s is not None:
        if i-s>20: runs.append((s+x0,i+x0))
        s=None
print('white gaps',len(runs))
gw=[e-s for s,e in runs]; c=[(s+e)/2 for s,e in runs]; p=np.diff(c)
pair=[runs[i+1][0]-runs[i][1] for i in range(len(runs)-1)]
f=lambda v: f"{np.median(v):.0f}px = {np.median(v)/pxm:.3f} m = {np.median(v)/pxm*1000/48:.2f} mm@1:48 (IQR {np.percentile(v,25):.0f}-{np.percentile(v,75):.0f})"
print('space',f(gw)); print('frame pair (sided)',f(pair)); print('pitch',f(p))
