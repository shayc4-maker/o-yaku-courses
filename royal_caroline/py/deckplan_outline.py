# deck plans (4a, 4b, 2b): hull outline per column (closing+fill+opening to drop guns/bowsprit/lines), scale bar, tilt of the centre line
import sys,json,numpy as np,cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import binary_fill_holes,label
BASE='/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/'
FILES={'4a':'d86cb433-plan_4a.tif','4b':'7854f215-plan_4b.tif','2b':'a4bd9499-plan_2b.tif'}
def load(k): return np.array(Image.open(BASE+FILES[k]).convert('L'))<128
def outline(ink):
    b=(ink*255).astype(np.uint8); H,W=b.shape; hull_zone=b.copy(); hull_zone[int(H*0.80):,:]=0          # drop the scale bars at the bottom
    c=cv2.morphologyEx(hull_zone,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41))); f=binary_fill_holes(c>0).astype(np.uint8)*255
    o=cv2.morphologyEx(f,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(61,61))); n,lab,st,cen=cv2.connectedComponentsWithStats(o,connectivity=8); i=1+int(np.argmax(st[1:,cv2.CC_STAT_AREA])); m=lab==i
    cols=np.where(m.any(axis=0))[0]; top=np.full(W,np.nan); bot=np.full(W,np.nan)
    for x in cols: r=np.where(m[:,x])[0]; top[x]=r.min(); bot[x]=r.max()
    return m,top,bot
def scale_bar(ink):
    H,W=ink.shape; sub=ink[int(H*0.80):,:]; rows=sub.sum(axis=1); idx=np.where(rows>1200)[0]
    return int(H*0.80),idx,rows
if __name__=='__main__':
    for k in FILES:
        ink=load(k); m,top,bot=outline(ink); xs=np.where(~np.isnan(top))[0]; x0,x1=xs.min(),xs.max(); mid=(top+bot)/2; hw=(bot-top)/2
        sel=xs[(xs>x0+300)&(xs<x1-300)]; p=np.polyfit(sel,mid[sel],1); res=mid[sel]-np.polyval(p,sel)
        print('plan',k,'hull X extent px %d..%d (len %d px), max half-width %.0f px | centre row = %.1f + %.5f*x (tilt %.3f deg, resid std %.1f px)'%(x0,x1,x1-x0,hw[sel].max(),p[1],p[0],np.degrees(np.arctan(p[0])),res.std()))
        y0,idx,rows=scale_bar(ink); print('  scale-bar candidate rows (y):',[y0+int(i) for i in idx][:12])
