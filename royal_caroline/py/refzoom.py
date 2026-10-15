import sys; sys.path.insert(0,'py')
from refdxf import load
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
L=load(sys.argv[1]); x0,x1,z0,z1=map(float,sys.argv[3:7]); skip=set(sys.argv[7].split(',')) if len(sys.argv)>7 else set()
cols={'01_BODY_OUTER':'tab:gray','02_KEELSON':'tab:red','03_STERN_KNEE':'tab:blue','04_AFT_DIVISIONS':'tab:green','05_KEEL_HOG_FALSEKEEL':'tab:brown','06_STEM_APRON':'tab:cyan','07_HEAD_GRIPE':'tab:purple','10_FRAME_SEATS':'k','98_JOINED_REVIEW_CURVES':'tab:orange'}
fig,ax=plt.subplots(figsize=(20,20*(z1-z0)/(x1-x0)))
for l,ss in L.items():
    if l in skip: continue
    for s in ss:
        a=np.array(s); ax.plot(a[:,0],a[:,1],color=cols.get(l,'k'),lw=1.4 if l!='98_JOINED_REVIEW_CURVES' else .8,alpha=1 if l!='98_JOINED_REVIEW_CURVES' else .6)
ax.set_xlim(x0,x1);ax.set_ylim(z0,z1);ax.set_aspect('equal');ax.grid(alpha=.2)
plt.tight_layout();plt.savefig(sys.argv[2],dpi=55)
