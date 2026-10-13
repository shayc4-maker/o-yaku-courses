import sys,numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d
Image.MAX_IMAGE_PIXELS=None
B=(np.array(Image.open(sys.argv[1]).convert('L'))<128).astype(float)
y0,y1,cx=map(int,sys.argv[2:5]); xs=range(cx-int(sys.argv[5]),cx+int(sys.argv[5])+1,50)
for x in xs:
    col=B[y0:y1,x-6:x+7].mean(1)          # hatch averaged over 13 px -> band density ~0.4-0.6, lines ~1
    d=uniform_filter1d(col,7)
    i=np.argmax(d); 
    # band extent where d>0.3 around max
    a=i
    while a>0 and d[a]>0.3: a-=1
    b=i
    while b<len(d)-1 and d[b]>0.3: b+=1
    print(x-cx, 'band %d-%d  centre %.1f'%(a+y0,b+y0,(a+b)/2+y0))
