# reference photo of somebody's identical plan (IMG_06, 'Disposition of frames'): normalise X by the station lines (quadratic), Z with the same scale, overlay our keel/keelson lines
import numpy as np,cv2,json,sys
from scipy.signal import find_peaks
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
IM='/tmp/claude-0/-home-user-o-yaku-courses/db230f8a-8640-51de-bf4e-53423595c88f/images/8.jpg'
im=cv2.imread(IM,0).astype(float); H,W=im.shape
band=im[215:330]; prof=(band.max(axis=0)-band).mean(axis=0); prof=np.convolve(prof,np.ones(3)/3,'same'); pk,_=find_peaks(prof,height=prof.max()*0.2,distance=8); pk=pk.astype(float)
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
Xs=np.array(list(XST.values())); a0,b0=1.6415,15.75
pred=b0+a0*Xs; obs=np.array([pk[np.argmin(np.abs(pk-p))] if np.min(np.abs(pk-p))<9 else np.nan for p in pred]); ok=np.isfinite(obs)
c=np.polyfit(Xs[ok],obs[ok],2); fit=np.polyval(c,Xs); print('stations used %d/18; quadratic px=%.3f+%.4f X+%.2e X^2; residual rms %.2f px, max %.2f px'%(ok.sum(),c[2],c[1],c[0],np.sqrt(np.mean((fit[ok]-obs[ok])**2)),np.abs(fit[ok]-obs[ok]).max()))
sc=np.polyval(np.polyder(c),270.0); print('scale at midship %.4f px/mm (%.3f mm/px)'%(sc,1/sc))
json.dump(dict(quad=c.tolist(),stations_used=int(ok.sum())),open('data/photo_ref_calibration_v1.json','w'))
Y0=float(sys.argv[1]) if len(sys.argv)>1 else 452.0
px=lambda X:np.polyval(c,X); py=lambda Z:Y0-sc*Z
NP=json.load(open('data/keel_keelson_points_v1.json'))
fig,ax=plt.subplots(2,1,figsize=(20,12)); 
for a,(x0,x1) in zip(ax,((0,520),(500,1024))):
    a.imshow(im,cmap='gray'); 
    for k,col in (('keel_top','r'),('keelson_under','lime'),('keelson_top','cyan')):
        P=np.array(NP[k]['points']); tck,_=splprep(P.T,k=3,s=0); X,Z=splev(np.linspace(0,1,1500),tck); a.plot(px(X),py(Z),col,lw=.9,label=k)
    a.set_xlim(x0,x1); a.set_ylim(480,380); a.legend(fontsize=8)
fig.savefig('qa/photo_overlay_check_y%d.png'%int(Y0),dpi=60,bbox_inches='tight')
