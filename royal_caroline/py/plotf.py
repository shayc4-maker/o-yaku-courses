import json,numpy as np,sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O=sys.argv[1]; d=json.load(open(O+'/frame_parts.json'))
sel=[int(v) for v in sys.argv[2].split(',')]
fig,axs=plt.subplots(1,len(sel),figsize=(4.2*len(sel),5.2))
for ax,f in zip(axs,sel):
    for p in d['parts']:
        if p['frame']!=f: continue
        P=np.array(p['poly']); ax.fill(P[:,0],P[:,1],alpha=.35 if p['layer']=='A' else .2,color='C0' if p['layer']=='A' else 'C1',label=f"timber {p['layer']} X {p['x0']:.1f}-{p['x1']:.1f}")
        ax.plot(P[:,0],P[:,1],lw=.6,color='k')
    ax.axhline(0,color='gray',lw=.5); ax.axvline(0,color='gray',lw=.5,ls='--')
    ax.set_aspect('equal'); ax.set_title(f'frame {f}'); ax.legend(fontsize=6,loc='lower center'); ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig(sys.argv[3],dpi=80)
