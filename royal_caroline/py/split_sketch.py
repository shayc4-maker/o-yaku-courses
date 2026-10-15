# Line sketch: v5 part split + frame seats over lines v2
import json,sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
sp=json.load(open('data/backbone_split_v5.json'))
c=json.load(open('data/backbone_contour_v5.json'))
ln=json.load(open('scan/lines_v1.json'))
col={'KEEL':'tab:brown','FALSE':'tab:olive','HOG':'tab:red','STEM':'tab:blue','APRON':'tab:cyan','GRIPE':'tab:purple','STERN':'tab:green','DEADWOOD':'tab:orange','INNER':'tab:pink','KNEE':'tab:gray'}
def cl(k):
    for p,v in col.items():
        if k.startswith(p): return v
    return 'k'
rng=[(-20,200),(180,380),(360,620)]
fig,axs=plt.subplots(3,1,figsize=(22,13))
for ax,(a,b) in zip(axs,rng):
    for e in ln:
        if e['kind']=='frames': continue
        x=[p[0] for p in e['pts']];z=[p[1] for p in e['pts']]
        ax.plot(x,z,color='0.6',lw=.6,ls='-' if e['kind']=='line' else '--')
    for k,v in sp.items():
        x=[p[0] for p in v];z=[p[1] for p in v]
        ax.plot(x,z,color=cl(k),lw=1.4)
        m=[p for p in v if a<=p[0]<=b]
        if m: q=m[len(m)//2]; ax.text(q[0],q[1]+1.5,k,fontsize=7,color=cl(k),ha='center')
    for s in c['seats']:
        if a<=s[0]<=b: ax.plot([s[0],s[1]],[s[2],s[2]],'k',lw=2)
    ax.set_xlim(a,b);ax.set_ylim(-12,120 if b>500 else 40);ax.set_aspect('equal');ax.grid(alpha=.2)
plt.tight_layout();plt.savefig('qa/split_sketch_v1.png',dpi=75)
