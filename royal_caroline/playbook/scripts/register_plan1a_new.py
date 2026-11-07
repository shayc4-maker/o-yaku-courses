# register the builder's new plan_5.tif (8616x2435) to plans/plan_1a_aligned.png (8621x2447; model mapping py/p5map.py): grid of template matches (normalised cross-correlation), least-squares affine new->aligned, residuals
import json,numpy as np,cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
new=np.array(Image.open('/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/84a5095a-plan_1a.tif').convert('L')); al=np.array(Image.open('plans/plan_1a_aligned.png').convert('L'))
inv=lambda a:cv2.GaussianBlur((255-a).astype(np.float32),(0,0),1.5)
N,Aa=inv(new),inv(al); print('new',new.shape,'aligned',al.shape)
H,Wd=new.shape; sx=al.shape[1]/Wd; sy=al.shape[0]/H
src=[];dst=[];sc=[]
th,tw=380,520
for gy in np.linspace(250,H-250,5):
    for gx in np.linspace(400,Wd-400,14):
        x0,y0=int(gx-tw/2),int(gy-th/2); T=N[y0:y0+th,x0:x0+tw]
        if T.std()<8: continue
        cx,cy=gx*sx,gy*sy; R=120; xa,ya=int(cx-tw/2-R),int(cy-th/2-R); xa=max(xa,0); ya=max(ya,0); S=Aa[ya:ya+th+2*R,xa:xa+tw+2*R]
        if S.shape[0]<th or S.shape[1]<tw: continue
        res=cv2.matchTemplate(S,T,cv2.TM_CCOEFF_NORMED); _,mx,_,loc=cv2.minMaxLoc(res)
        if mx>0.55:
            # sub-pixel refine by parabola
            lx,ly=loc; dx=0.0;dy=0.0
            if 0<lx<res.shape[1]-1: a,b,c=res[ly,lx-1],res[ly,lx],res[ly,lx+1]; dx=0.5*(a-c)/(a-2*b+c+1e-9)
            if 0<ly<res.shape[0]-1: a,b,c=res[ly-1,lx],res[ly,lx],res[ly+1,lx]; dy=0.5*(a-c)/(a-2*b+c+1e-9)
            src.append((gx,gy)); dst.append((xa+lx+dx+tw/2,ya+ly+dy+th/2)); sc.append(mx)
src=np.array(src);dst=np.array(dst); print('matches',len(src),'score min/med %.2f/%.2f'%(min(sc),np.median(sc)))
M=np.c_[src,np.ones(len(src))]; cx_,*_=np.linalg.lstsq(M,dst[:,0],rcond=None); cy_,*_=np.linalg.lstsq(M,dst[:,1],rcond=None)
r=np.c_[M@cx_-dst[:,0],M@cy_-dst[:,1]]
for _ in range(3):
    ok=np.hypot(*r.T)<max(3*np.median(np.hypot(*r.T)),1.0); cx_,*_=np.linalg.lstsq(M[ok],dst[ok,0],rcond=None); cy_,*_=np.linalg.lstsq(M[ok],dst[ok,1],rcond=None); r=np.c_[M@cx_-dst[:,0],M@cy_-dst[:,1]]
print('affine new->aligned: x\' = %.5f x %+.6f y %+.2f ; y\' = %+.6f x %.5f y %+.2f'%(cx_[0],cx_[1],cx_[2],cy_[0],cy_[1],cy_[2]))
print('inliers %d of %d; residual rms %.2f px max %.2f px (1 px = 0.0851 mm)'%(ok.sum(),len(ok),np.sqrt((r[ok]**2).sum(1).mean()),np.hypot(*r[ok].T).max()))
json.dump(dict(ax=[float(v) for v in cx_],ay=[float(v) for v in cy_],n=int(len(src)),inliers=int(ok.sum()),rms_px=float(np.sqrt((r[ok]**2).sum(1).mean()))),open('data/plan1a_new_to_aligned.json','w'))
