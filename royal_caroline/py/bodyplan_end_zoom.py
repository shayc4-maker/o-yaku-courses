# zoom of the ORIGINAL forward body plan (plan_1b) at the keel: stations 1-3 ends, WL II/III ink rows, approved first points
import sys,json,numpy as np
sys.path.insert(0,'py')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import bodyplan_points_all as B
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
cf=B.CFG['fwd']; im=Image.open('plans/plan_1b_aligned.png').convert('RGB'); C=json.load(open('data/bodyplan_splines_v1.json'))
x0,y0=B.px(cf,np.array([-1.0]),np.array([32.0])); x1,y1=B.px(cf,np.array([14.0]),np.array([10.0])); box=(int(min(x0[0],x1[0])),int(min(y0[0],y1[0])),int(max(x0[0],x1[0])),int(max(y0[0],y1[0])))
fig,ax=plt.subplots(figsize=(10,10*(box[3]-box[1])/(box[2]-box[0])),dpi=110); ax.imshow(im.crop(box),extent=(box[0],box[2],box[3],box[1]))
for n,col in ((1,'tab:blue'),(2,'tab:orange'),(3,'tab:green')):
    L=np.array(C[str(n)]['curve']); x,y=B.px(cf,L[:,0],L[:,1]); ax.plot(x,y,color=col,lw=1); p=C[str(n)]['points'][0]; px_,py_=B.px(cf,np.array([p[0]]),np.array([p[1]])); ax.plot(px_,py_,'o',mfc='none',mec=col,ms=9); ax.text(px_[0]+8,py_[0],'st%d first pt (%.2f, %.2f)'%(n,*p),color=col,fontsize=8)
for nm,z in (('II',17.4),('III',26.1)):
    xs,ys=B.px(cf,np.array([-1,14]),np.array([z,z])); ax.plot(xs,ys,color='lime',lw=.8); ax.text(xs[1],ys[1]-3,'WL %s Z=%.1f (nominal)'%(nm,z),color='green',fontsize=8,ha='right')
xs,ys=B.px(cf,np.array([2.65,2.65]),np.array([10,32])); ax.plot(xs,ys,color='gray',lw=.6)
ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig('qa/bodyplan_end_zoom.png',bbox_inches='tight')
