# Closed regions (candidate parts) from lines_v1.json via shapely polygonize
import json,sys
from shapely.geometry import LineString
from shapely.ops import unary_union, polygonize
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
src=sys.argv[1]; out=sys.argv[2]
d=json.load(open(src))
ls=[LineString(e['pts']) for e in d if e['kind']!='frames' and len(e['pts'])>1]
fr=[e for e in d if e['kind']=='frames']
u=unary_union(ls)
faces=sorted(polygonize(u),key=lambda p:-p.area)
print(len(faces),'faces')
json.dump([{'id':i,'area':f.area,'ring':list(f.exterior.coords)} for i,f in enumerate(faces)],open(out+'.json','w'))
segs=[(0,260),(260,460)]
fig,axs=plt.subplots(3,1,figsize=(22,15))
xs=[(-20,200),(180,380),(360,560)]
for ax,(a,b) in zip(axs,xs):
    for i,f in enumerate(faces):
        x,y=f.exterior.xy
        ax.fill(x,y,alpha=.25,color=plt.cm.tab20(i%20)); ax.plot(x,y,'k',lw=.5)
        c=f.representative_point()
        if a<=c.x<=b and f.area>0.3: ax.text(c.x,c.y,str(i),fontsize=7,ha='center')
    ax.set_xlim(a,b);ax.set_ylim(-12,100);ax.set_aspect('equal')
plt.tight_layout();plt.savefig(out+'.png',dpi=80)
for i,f in enumerate(faces): print(i,round(f.area,1),[round(v,1) for v in f.bounds])
