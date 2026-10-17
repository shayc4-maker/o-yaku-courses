import sys,io,contextlib,numpy as np
mod=sys.argv[1]; out=sys.argv[2]
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); M=__import__(mod)
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import splprep,splev
def sp(A,n=400): tk,u=splprep(A.T,k=3,s=0); return np.array(splev(np.linspace(0,1,n),tk)).T
fig,ax=plt.subplots(1,3,figsize=(21,9)); rows=[]
for a,(fn,(xa,xb)) in zip(ax,((46,(24,28)),(47,(13,17)),(48,(2,6)))):
    for lay,x0,col in (('aft',xa,'tab:blue'),('fwd',xb,'tab:red')):
        o,t,r,faces=M.layer_nodes(fn,x0); a.plot(*sp(o).T,color=col,lw=2.2,label=f'{lay} layer block (X {x0}-{x0+4})'); a.plot(*sp(np.vstack([t,r[1:]])).T,color=col,lw=2.2)
        for Xf,(of,tf,rf) in faces.items(): a.plot(*sp(of).T,color=col,lw=.7,ls='--'); a.plot(*sp(np.vstack([tf,rf[1:]])).T,color=col,lw=.7,ls='--')
        rows.append((fn,lay,max(np.abs(o[:,0]-f[0][:,0]).max() for f in faces.values())))
    a.set_xlim(0,60); a.set_ylim(20,110); a.set_aspect('equal'); a.grid(alpha=.3); a.legend(fontsize=8); a.set_title(f'F{fn}: solid = layer block, dashed = exact line of each face')
plt.savefig(out,dpi=60,bbox_inches='tight')
for r in rows: print('F%d %s: max sanding allowance on the outer line %.1f mm'%r)
