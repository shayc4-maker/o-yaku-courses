# How the frames sit in the keel/keelson channel: side view with all frame bands, level plots vs X, and the YZ section of one frame
import sys,numpy as np
sys.argv=[sys.argv[0]]
import frames_batch_2d as F
import matplotlib.pyplot as plt
from shapely.geometry import box as bx
xs=np.arange(440,527,0.5); KT=[];KS=[];KE=[]
for X in xs:
    try: kt,(a,b)=F.keel_levels(X); KT.append(kt); KS.append(a); KE.append(b)
    except Exception: KT.append(np.nan);KS.append(np.nan);KE.append(np.nan)
KT,KS,KE=map(np.array,(KT,KS,KE)); fr=[(b,F.XF[45-b]) for b in range(1,10)]
fig=plt.figure(figsize=(17,16)); ax1=fig.add_axes([.05,.58,.9,.38]); ax2=fig.add_axes([.05,.33,.9,.2]); ax3=fig.add_axes([.05,.04,.4,.25]); ax4=fig.add_axes([.55,.04,.4,.25])
for k,pg in F.PP.items(): ax1.fill(*pg.exterior.xy,color='#bbb',alpha=.55,lw=0); ax1.plot(*pg.exterior.xy,color='#777',lw=.4)
for b,X in fr:
    for xa,xb,c in ((X-4,X,'tab:blue'),(X,X+4,'tab:red')): ax1.axvspan(xa,min(xb,526.6),color=c,alpha=.18); ax2.axvspan(xa,min(xb,526.6),color=c,alpha=.18)
    ax1.text(X-3.5,57,str(b),fontsize=11,weight='bold'); ax2.text(X-3.5,max(np.nanmax(KS),30)+1,str(b),fontsize=9)
ax1.set_xlim(440,545); ax1.set_ylim(-12,62); ax1.set_aspect('equal'); ax1.set_title('Side view X-Z: keel + keelson (gray), frame layers A (blue) / F (red) numbered by builder number; the white channel is the opening'); ax1.grid(alpha=.2)
ax2.plot(xs,KT,'k-',label='keel top'); ax2.plot(xs,KS,'g-',label='keelson bottom'); ax2.plot(xs,KE,'g--',label='keelson top'); ax2.set_xlim(440,545); ax2.legend(loc='upper left'); ax2.grid(alpha=.3); ax2.set_title('Channel levels along X (steps are where the profile changes); frame bands behind')
# section of builder frame 5
for a_,b_,X in ((ax3,5,F.XF[40]),(ax4,2,F.XF[43])):
    for xl,col in ((X-4,'tab:blue'),(X,'tab:red')):
        p,i=F.face_poly(xl,xl)
        for g in (p,F.mirror(p)): a_.plot(*g.exterior.xy,color=col,lw=1)
    a_.add_patch(plt.Rectangle((-F.KB,-20),2*F.KB,i['keel_top']+20,color='#888',alpha=.6)); a_.add_patch(plt.Rectangle((-F.KB,i['ks_bot']),2*F.KB,i['ks_top']-i['ks_bot'],color='#888',alpha=.6))
    a_.set_xlim(-22,22); a_.set_ylim(i['keel_top']-8,i['ks_top']+14); a_.set_aspect('equal'); a_.grid(alpha=.25); a_.set_title('YZ section at frame %d, X-4 blue and X red'%b_)
fig.savefig('qa/channel_views.png',dpi=60,bbox_inches='tight')
# steps
d=np.where(np.abs(np.diff(KS))>0.4)[0]; print('keelson-bottom steps at X:',[round(xs[i],1) for i in d]); d2=np.where(np.abs(np.diff(KT))>0.4)[0]; print('keel-top steps at X:',[round(xs[i],1) for i in d2])
print('frame bands (builder,X-4,X+4):',[(b,round(X-4,1),round(X+4,1)) for b,X in fr])
