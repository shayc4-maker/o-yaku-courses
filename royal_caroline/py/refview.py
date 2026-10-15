import sys; sys.path.insert(0,'py')
from refdxf import load
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
L=load(sys.argv[1])
cols={'01_BODY_OUTER':'#777','02_KEELSON':'tab:red','03_STERN_KNEE':'tab:blue','04_AFT_DIVISIONS':'tab:green','05_KEEL_HOG_FALSEKEEL':'tab:brown','06_STEM_APRON':'tab:cyan','07_HEAD_GRIPE':'tab:purple','98_JOINED_REVIEW_CURVES':'#f0a050'}
rng=[(-30,215,-12,95),(205,420,-12,25),(410,625,-12,140)]
fig,axs=plt.subplots(3,1,figsize=(20,17))
for ax,(x0,x1,z0,z1) in zip(axs,rng):
    for l,ss in L.items():
        for s in ss:
            a=np.array(s); ax.plot(a[:,0],a[:,1],color=cols.get(l,'k'),lw=.9 if l!='98_JOINED_REVIEW_CURVES' else .6,alpha=1 if l!='98_JOINED_REVIEW_CURVES' else .7)
    ax.set_xlim(x0,x1);ax.set_ylim(z0,z1);ax.set_aspect('equal');ax.grid(alpha=.2)
h=[plt.Line2D([],[],color=c,label=l) for l,c in cols.items()]
axs[0].legend(handles=h,loc='upper right',fontsize=8)
plt.tight_layout();plt.savefig(sys.argv[2],dpi=70)
