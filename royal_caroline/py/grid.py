import sys, numpy as np
from PIL import Image
from scipy.signal import find_peaks
Image.MAX_IMAGE_PIXELS=None
def load(n): return np.array(Image.open(n).convert('L'))<128
a=load(sys.argv[1]); x0,x1,y0,y1=map(int,sys.argv[2:6]); mode=sys.argv[6]
sub=a[y0:y1,x0:x1]
if mode=='h':
    s=sub.sum(1); pk,_=find_peaks(s,height=float(sys.argv[7])*(x1-x0),distance=15)
    for p in pk: print('y',p+y0,'frac %.2f'%(s[p]/(x1-x0)))
else:
    s=sub.sum(0); pk,_=find_peaks(s,height=float(sys.argv[7])*(y1-y0),distance=15)
    for p in pk:
        # subpixel centre: weighted over +-4
        w=s[max(p-4,0):p+5]; c=(np.arange(len(w))*w).sum()/w.sum()+max(p-4,0)
        print('x %.1f'%(c+x0),'frac %.2f'%(s[p]/(y1-y0)))
