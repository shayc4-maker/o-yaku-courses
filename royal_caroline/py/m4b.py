import sys, numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
a=np.array(Image.open(sys.argv[1]).convert('L'))<128
H,W=a.shape
for x in [3000,4000,5000,5600]:
    col=a[:400,x]; ys=np.where(col)[0]
    print(x, 'first dark y', ys[:1], 'dark density 120-260:', ''.join('#' if col[y] else '.' for y in range(120,260)))
