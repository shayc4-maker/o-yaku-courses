import json,numpy as np,sys; sys.path.insert(0,'py')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from p1a_strip import warped
K=json.load(open('data/p1a_beam_blocks_v1.json'))
fig,axs=plt.subplots(2,1,figsize=(17,15))
for a,(x0,x1) in zip(axs,((-20,290),(280,570))):
    z0,z1=60,135; a.imshow(warped((x0,x1),(z0,z1),0.1),cmap='gray',vmin=0,vmax=255,extent=(x0,x1,z0,z1),aspect='equal')
    for k in K:
        if x0<=(k['X0']+k['X1'])/2<=x1:
            a.plot([k['X0'],k['X1']],[k['Ztop']]*2,'r-',lw=2.5); a.text((k['X0']+k['X1'])/2,k['Ztop']+1.2,'%s  Ztop %.1f\nX %.1f..%.1f'%(k['id'],k['Ztop'],k['X0'],k['X1']),color='r',fontsize=9,ha='center')
    a.set_xticks(np.arange(x0,x1,10)); a.grid(alpha=.3); a.set_xlim(x0,x1); a.set_ylim(z0,z1)
fig.savefig('qa/p1a_beam_blocks_v1.png',dpi=65,bbox_inches='tight')
