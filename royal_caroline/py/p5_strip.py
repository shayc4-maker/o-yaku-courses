import sys,numpy as np; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from p5map import model_to_p5,p5_to_model
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
im=np.array(Image.open('plans/plan_5_aligned.png').convert('L'))
H,W=im.shape; print(W,H,p5_to_model(0,0),p5_to_model(W,H))
x0,x1=float(sys.argv[1]),float(sys.argv[2]); z0,z1=float(sys.argv[3]),float(sys.argv[4])
a,b=model_to_p5(x0,z1); c,d=model_to_p5(x1,z0)
fig,ax=plt.subplots(figsize=(16,16*(z1-z0)/(x1-x0)+.6)); ax.imshow(im[max(int(b),0):int(d),max(int(a),0):int(c)],cmap='gray',extent=(x0,x1,z0,z1),aspect='equal')
ax.set_xticks(np.arange(x0,x1+1,10)); ax.set_yticks(np.arange(z0,z1+1,10)); ax.grid(alpha=.35); fig.savefig(sys.argv[5],dpi=70,bbox_inches='tight')
