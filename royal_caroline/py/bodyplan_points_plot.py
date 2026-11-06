import json,sys,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import bodyplan_points_all as B
D=json.load(open('data/bodyplan_points_v1.json'))
def plot(ns,box,img,out,figw=14):
    c=B.CFG[B.which(ns[0])]; im=Image.open(img).convert('RGB').crop(box)
    fig,ax=plt.subplots(figsize=(figw,figw*(box[3]-box[1])/(box[2]-box[0])),dpi=110); ax.imshow(im,extent=(box[0],box[2],box[3],box[1]))
    for n in ns:
        d=D[str(n)]; p=np.array(d['points']); x,y=B.px(c,p[:,0],p[:,1]); ax.plot(x,y,'o',mfc='none',mec='r',ms=5,mew=1)
        ax.text(x[-1],y[-1]-18,f'{n}',color='#d00',fontsize=11,ha='center',weight='bold')
        if d['straight_top']: ax.plot(x[-2:],y[-2:],'-',color='#00a000',lw=1.2)
    ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig(out,bbox_inches='tight'); plt.close(fig)
plot(range(1,9),(2400,500,3750,2150),'plans/plan_1b_aligned.png','qa/bodyplan_points_fwd.png')
plot(range(9,19),(1250,420,2400,2300),'plans/plan_1a_aligned.png','qa/bodyplan_points_aft.png',figw=11)
