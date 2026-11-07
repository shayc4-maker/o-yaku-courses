# side view: frame 1 faces (X lines) on plan_5 (aligned), with iron rabbet
import sys,json,numpy as np; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from p5map import model_to_p5
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
im=np.array(Image.open('plans/plan_5_aligned.png').convert('L'))
A=json.load(open('data/frames_outer_approved_v2.json')); R=json.load(open('data/rabbet_iron_v1.json'))
print(list(R.keys())[:8])
xl,zl=(495,600),(0,125)
x0,z0=model_to_p5(xl[0],zl[0]); x1,z1=model_to_p5(xl[1],zl[1])
crop=im[int(z1):int(z0),int(x0):int(x1)]
fig,a=plt.subplots(figsize=(11,13))
a.imshow(crop,cmap='gray',extent=(xl[0],xl[1],zl[0],zl[1]),aspect='equal')
for nm,c in (('back','tab:blue'),('mid','k'),('front','tab:red')):
    v=A['1'][nm]; C=np.array(v['curve']); zt=C[:,1].max(); zb=C[0,1] if C[0,1]<C[-1,1] else C[-1,1]
    a.plot([v['X']]*2,[C[:,1].min(),zt],color=c,lw=1.6,label='frame 1 %s X=%.2f Z %.1f..%.1f'%(nm,v['X'],C[:,1].min(),zt))
    print(nm,v['X'],C[:,1].min(),zt)
a.set_xlim(*xl);a.set_ylim(*zl);a.grid(alpha=.3);a.legend(fontsize=8,loc='upper left')
a.set_title('plan_5 side view, frame 1 faces (vertical lines in X)')
fig.savefig('qa/frame1_front_on_plan5_v1.png',dpi=80,bbox_inches='tight')
