import sys,json,numpy as np
sys.path.insert(0,'py')
from deckplan_outline import *
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
A=json.load(open('data/frames_outer_approved_v1.json')); mx=[]
for b,fr in A.items():
    for nm,v in fr.items(): C=np.array(v['curve']); mx.append((v['X'],float(C[:,0].max())))
mx=np.array(sorted(mx)); S=11.75
fig,axs=plt.subplots(3,1,figsize=(18,15))
for a,(k,xo,d) in zip(axs,(('2b',990.3,2.93),('4a',982.3,2.97),('4b',926.6,3.46))):
    ink=load(k); m,top,bot=outline(ink); xs=np.where(~np.isnan(top))[0]; hw=(bot-top)/2; mid=(top+bot)/2; X=(xs-xo)/S
    a.plot(X,hw[xs]/S,'k',lw=1,label='plan %s: half-width of the outline (mm)'%k); a.plot(X,(mid[xs]-np.polyval(np.polyfit(xs,mid[xs],1),xs))/S,'g',lw=.6,label='centre offset (mm)')
    a.plot(mx[:,0],mx[:,1]+d,'r.',ms=3,label='model max half-breadth + %.2f mm (approved frames)'%d); a.set_xlim(-45,610); a.set_ylim(-12,85); a.grid(alpha=.3); a.legend(fontsize=8,loc='lower center'); a.set_title('deck plan %s: calibration state (scale %.2f px/mm, X offset %.0f px) - outline vs model'%(k,S,xo))
fig.savefig('qa/deckplans_calibration_state.png',dpi=55,bbox_inches='tight')
