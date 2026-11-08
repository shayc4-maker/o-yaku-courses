# photo of the reference plan normalised by the 18 station lines (data/photo_ref_calibration_v1.json) with the builder's APPROVED keel (STEP profiles, unchanged) over it
import numpy as np,cv2,json,sys
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
IM='/tmp/claude-0/-home-user-o-yaku-courses/db230f8a-8640-51de-bf4e-53423595c88f/images/8.jpg'
im=cv2.imread(IM,0); c=np.array(json.load(open('data/photo_ref_calibration_v1.json'))['quad']); sc=float(np.polyval(np.polyder(c),270.0))
PR=json.load(open('data/step44_profiles.json'))
Y0=float(sys.argv[1]) if len(sys.argv)>1 else 452.0; S=float(sys.argv[2]) if len(sys.argv)>2 else sc
px=lambda X:np.polyval(c,X); py=lambda Z:Y0-S*Z
fig,ax=plt.subplots(2,1,figsize=(20,12))
for a,(x0,x1) in zip(ax,((0,520),(500,1024))):
    a.imshow(im,cmap='gray')
    for k,col in (('Boss-Extrude4[4]','lime'),('Boss-Extrude2[2]','red'),('Boss-Extrude3[3]','orange'),('Boss-Extrude4[1]','magenta'),('Boss-Extrude2[1]','cyan'),('Boss-Extrude5[3]','yellow')):
        for q in PR.get(k,[]):
            P=np.array(q); 
            if np.ptp(P[:,0])>20: a.plot(px(P[:,0]),py(P[:,1]),color=col,lw=.7)
    a.set_xlim(x0,x1); a.set_ylim(480,380)
fig.savefig('qa/photo_overlay_approved_y%d.png'%int(Y0),dpi=60,bbox_inches='tight')
print('scale',S,'Y0',Y0)
