import json,numpy as np,sys; sys.path.insert(0,'py')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from p1a_strip import warped
P=json.load(open('data/p1a_marks_v1.json')); col=dict(red='r',purple='m',yellow='orange',green='lime',other='c')
fig,axs=plt.subplots(3,1,figsize=(17,22))
for a,(x0,x1,z0,z1) in zip(axs,((-40,250,95,145),(220,470,92,125),(430,575,92,125))):
    a.imshow(warped((x0,x1),(z0,z1),0.06),cmap='gray',vmin=0,vmax=255,extent=(x0,x1,z0,z1),aspect='equal')
    for p in P:
        if x0<=p['X']<=x1 and z0<=p['Z']<=z1: a.plot(p['X'],p['Z'],'o',mfc='none',mec=col[p['g']],ms=9,mew=1.5); a.text(p['X'],p['Z']+.8,'%s\n%.1f,%.1f'%(p['id'],p['X'],p['Z']),fontsize=7,ha='center',color=col[p['g']])
    a.set_xlim(x0,x1);a.set_ylim(z0,z1);a.grid(alpha=.3)
axs[2].plot([559.3],[103.35],'bx',ms=12); axs[2].text(559.3,100.5,'E2 559.3,103.35',color='b',fontsize=8,ha='center'); axs[2].axvline(528.03,color='tab:red',lw=.8)
fig.savefig('qa/p1a_marks_v1.png',dpi=62,bbox_inches='tight')
