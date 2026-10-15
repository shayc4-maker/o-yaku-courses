import sys,json
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
F=json.load(open(sys.argv[1]))
rng=[(-30,215,-12,95),(205,420,-12,25),(410,625,-12,140)]
fig,axs=plt.subplots(3,1,figsize=(22,17))
for ax,(x0,x1,z0,z1) in zip(axs,rng):
    for f in F:
        p=Polygon(f['ring'],f['holes']); x,z=p.exterior.xy
        ax.fill(x,z,alpha=.4,color=plt.cm.tab20(f['id']%20)); ax.plot(x,z,'k',lw=.4)
        c=p.representative_point()
        if x0<=c.x<=x1 and z0<=c.y<=z1 and p.area>1: ax.text(c.x,c.y,str(f['id']),fontsize=7,ha='center')
    ax.set_xlim(x0,x1);ax.set_ylim(z0,z1);ax.set_aspect('equal')
plt.tight_layout();plt.savefig(sys.argv[2],dpi=65)
for f in F[:40]: 
    p=Polygon(f['ring'],f['holes']);print(f['id'],round(p.area,1),[round(v,1) for v in p.bounds])
