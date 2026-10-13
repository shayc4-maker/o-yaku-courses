import sys,numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d
Image.MAX_IMAGE_PIXELS=None
B=(np.array(Image.open(sys.argv[1]).convert('L'))<128).astype(float)
y0,y1,cx,half=map(int,sys.argv[2:6]); seed=int(sys.argv[6])
prev=seed; out=[]
for sgn in (1,-1):
    prev=seed
    for k in range(0,half+1,25):
        x=cx+sgn*k
        col=uniform_filter1d(B[y0:y1,x-6:x+7].mean(1),5)
        lo=max(prev-y0-8,0); hi=min(prev-y0+9,len(col)-1)
        # bottom edge of hatched band: largest negative gradient near prev
        g=np.diff(col); j=lo+np.argmin(g[lo:hi]); prev=j+y0
        out.append((sgn*k,prev))
out=sorted(set(out)); print(out)
xs=np.array([o[0] for o in out],float); ys=np.array([o[1] for o in out],float)
m=np.abs(xs)<=half; c=np.polyfit(xs[m],ys[m],2); print('fit y = %.6f x^2 + %.5f x + %.1f'%tuple(c),' drop at +-%d: %.1f px'%(half,c[0]*half**2))
