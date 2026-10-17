# Body plan drawings from the plans (A1/2 aft = plan_1a, A1/3 forward = plan_1b) with the builder's station splines drawn over them in red/green
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ST=np.load('data/hull_stations_all.npz'); WL=np.load('data/hull_waterlines_all.npz')
def draw(img,box,cx,zI,k,side,names,out,title):
    im=Image.open(img).convert('RGB').crop(box); fig,ax=plt.subplots(figsize=(im.size[0]/150,im.size[1]/150),dpi=150); ax.imshow(im,extent=(box[0],box[2],box[3],box[1]))
    cm=plt.cm.tab10
    for n,kn in enumerate(names):
        v=ST[kn]; px=cx+side*v[:,1]/k; py=zI-(v[:,2]-8.7)/k; ax.plot(px,py,color='#e0201b' if n%2==0 else '#0a8f3c',lw=1.1); ax.text(px[-1],py[-1]-14,kn[2:],color='#e0201b',fontsize=7,ha='center')
    ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); ax.set_title(title,fontsize=9); fig.savefig(out,dpi=150,bbox_inches='tight'); plt.close(fig)
cx_a,zI_a,k_a=2385.0,2013.0,43.4/521.0
draw('plans/plan_1a_aligned.png',(1250,420,2400,2300),cx_a,zI_a,k_a,-1,[f'ST{n:02d}' for n in range(8,19)],'qa/bodyplan_aft_A1-2_with_splines.png','A1/2 aft body plan with the builder station splines 8-18 (red/green)')
cx_f,zI_f,k_f=2433.0,1903.0,8.65/103.3
draw('plans/plan_1b_aligned.png',(2380,500,3700,2150),cx_f,zI_f,k_f,+1,[f'ST{n:02d}' for n in range(1,9)],'qa/bodyplan_fwd_A1-3_with_splines.png','A1/3 forward body plan with the builder station splines 1-8 (red/green)')
