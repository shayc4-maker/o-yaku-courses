import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
a=np.array(Image.open(sys.argv[1]).convert('L'))<128
H=a.shape[0]
for x in range(3800,5200,100):
    c=a[:,x]; ys=np.where(c[:2150])[0]; t,b=ys[0],ys[-1]
    # bottom edge: last dark below 1900
    print(x,'top',t,'bot',b,'w px',b-t,'m %.3f'%((b-t)/244.3))
