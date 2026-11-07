import sys,json,numpy as np; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from p5map import model_to_p5
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
im=np.array(Image.open('plans/plan_5_aligned.png').convert('L'))
B=json.load(open('/tmp/beams.json'))
B=[b for b in B if b[3]>114.5 and (b[0]<130 or 130<b[0]<250 or b[0]>490)]
def top_of_band(b):
    return b[3]
for k,(x0,x1,z0,z1,fn) in enumerate(((-10,80,108,130,'a'),(80,170,108,132,'b'),(165,250,105,132,'c'),(450,560,105,130,'d'))):
    a,bb=model_to_p5(x0,z1); c,d=model_to_p5(x1,z0)
    fig,ax=plt.subplots(figsize=(18,18*(z1-z0)/(x1-x0)+.5)); ax.imshow(im[int(bb):int(d),max(int(a),0):int(c)],cmap='gray',extent=(x0,x1,z0,z1),aspect='equal')
    for i,b in enumerate(B):
        if x0<=(b[0]+b[1])/2<=x1:
            ax.plot([b[0],b[1]],[b[3]]*2,'r-',lw=2); ax.text((b[0]+b[1])/2,b[3]+.4,'B%d'%i,color='r',fontsize=9,ha='center')
    ax.set_xticks(np.arange(x0,x1,5)); ax.grid(alpha=.3); fig.savefig('qa/p5_beam_cands_%s.png'%fn,dpi=65,bbox_inches='tight')
json.dump(B,open('data/p5_beam_candidates_v1.json','w'))
print(len(B))
