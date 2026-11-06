# proposed END points (hook tips at the keel wall) of the forward stations 1-8, read from gridded zooms of the ORIGINAL body plan (plan_1b); for approval, nothing is changed in data/bodyplan_splines_v1.json
import sys,json,numpy as np
sys.path.insert(0,'py')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import bodyplan_points_all as B
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
cf=B.CFG['fwd']; C=json.load(open('data/bodyplan_splines_v1.json')); im=Image.open('plans/plan_1b_aligned.png').convert('RGB')
END={1:(2.85,26.05),2:(2.95,12.10),3:(2.85,2.80),4:(3.30,-0.55),5:(3.30,-0.55),6:(3.30,-0.55),7:(3.30,-0.55),8:(3.30,-0.55)}
json.dump({str(n):dict(first=C[str(n)]['points'][0],end=list(e)) for n,e in END.items()},open('data/bodyplan_ends_proposed_v1.json','w'))
fig,axs=plt.subplots(2,4,figsize=(24,14))
for n in range(1,9):
    p0=C[str(n)]['points'][0]; e=END[n]; ax=axs.ravel()[n-1]
    Y0,Y1,Z0,Z1=0.5,7.0,p0[1]-3.2,p0[1]+2.2
    xa,ya=B.px(cf,np.array([Y0,Y1]),np.array([Z1,Z0])); box=(int(xa[0]),int(ya[0]),int(xa[1]),int(ya[1]))
    ax.imshow(im.crop(box),extent=(Y0,Y1,Z0,Z1),aspect='equal'); ax.set_xticks(np.arange(Y0,Y1+.01,0.5)); ax.set_yticks(np.arange(np.ceil(Z0),Z1,0.5)); ax.grid(alpha=.35,color='r',lw=.4); ax.tick_params(labelsize=7)
    ax.plot([p0[0]],[p0[1]],'o',mfc='none',mec='b',ms=9); ax.plot([p0[0],e[0]],[p0[1],e[1]],'-',color='lime',lw=1); ax.plot([e[0]],[e[1]],'o',mfc='none',mec='lime',ms=12,mew=2)
    ax.text(e[0]+.15,e[1]-.35,'END %d (%.2f, %.2f)'%(n,*e),color='green',fontsize=11,weight='bold'); ax.axvline(2.65,color='gray',lw=.6); ax.set_title('station %d: approved first pt (blue) -> proposed end (green)'%n)
fig.savefig('qa/bodyplan_ends_proposed_v1.png',dpi=55,bbox_inches='tight')
