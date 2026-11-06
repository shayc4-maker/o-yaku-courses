# precise Z of the longitudinal lines (waterlines I-VII) on the sheer plan A1/1: ink centre per column (single clean run <0.8 mm wide), every 3 mm in X; per-line linear fit; joint plan tilt fitted against the body-plan WL Z
import numpy as np, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
im=np.array(Image.open('plans/plan_1a_aligned.png').convert('L'))
BP=dict(I=8.7,II=17.4,III=26.1,IV=34.8,V=43.4,VI=52.1,VII=69.5); NOM=dict(I=9.2,II=17.8,III=26.9,IV=35.5,V=44.2,VI=52.8,VII=70.4)
def center(c,zexp,win=1.6):
    col=im[:,c-1:c+2].min(axis=1); a=int(ZR-(zexp+win)/KZ); b=int(ZR-(zexp-win)/KZ); d=col[a:b]<110; runs=[];i=0
    while i<len(d):
        if d[i]:
            j=i
            while j<len(d) and d[j]: j+=1
            runs.append((j-i,(a+(i+j)/2))); i=j
        else: i+=1
    if len(runs)!=1 or runs[0][0]*KZ>0.8: return None
    return (ZR-runs[0][1])*KZ
D={}
for nm in BP:
    X=[];Z=[]
    for x in np.arange(20,520,3.0):
        z=center(int(round((x-X0)/KX)),NOM[nm])
        if z is not None: X.append(x);Z.append(z)
    X=np.array(X);Z=np.array(Z); m=np.abs(Z-np.median(Z))<0.45; D[nm]=(X[m],Z[m])
# joint model Z_ink = Zbp + a + b*(X-270)
A=[];y=[]
for nm,(X,Z) in D.items():
    for x,z in zip(X,Z): A.append([1,x-270]); y.append(z-BP[nm])
A=np.array(A);y=np.array(y); (a,b),*_=np.linalg.lstsq(A,y,rcond=None)
print('joint fit: offset a=%.3f mm at X=270, tilt b=%.5f mm/mm (%.2f mm over 500 mm)'%(a,b,b*500))
out={}
fig,ax=plt.subplots(figsize=(16,8))
for nm,(X,Z) in D.items():
    res=Z-BP[nm]-a-b*(X-270); out[nm]=dict(n=int(len(X)),median_ink_Z=float(np.median(Z)),res_mean=float(res.mean()),res_std=float(res.std()),bodyplan_Z=BP[nm])
    print('%-4s n %3d  ink Z(270) %.2f | body plan %.1f | residual after offset+tilt: mean %+.2f std %.2f'%(nm,len(X),np.interp(270,X,Z) if X.min()<270<X.max() else np.median(Z),BP[nm],res.mean(),res.std()))
    ax.plot(X,Z-BP[nm],'.',ms=3,label=nm)
xx=np.array([20,520]); ax.plot(xx,a+b*(xx-270),'k-',lw=1.2,label='joint offset+tilt'); ax.set_xlabel('X (mm)'); ax.set_ylabel('sheer-plan ink Z minus body-plan WL Z (mm)'); ax.grid(alpha=.3); ax.legend(ncol=8)
ax.set_title('Waterlines on the sheer plan sampled every 3 mm vs body plan WL Z: one common offset and a small tilt of the plan explain them')
fig.savefig('qa/sheer_wl_measure.png',dpi=70,bbox_inches='tight'); json.dump(dict(offset=float(a),tilt=float(b),lines=out),open('data/sheer_wl_measure.json','w'))
