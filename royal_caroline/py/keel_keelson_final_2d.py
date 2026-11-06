# Keel (top line) and keelson (inner line) after the move to full pockets: both lines are smooth splines between the pockets; pocket walls >= W on both sides of every frame
import sys,json,numpy as np
W=float(sys.argv[1]) if len(sys.argv)>1 else 1.0; sys.argv=[sys.argv[0]]
import frames_batch_2d as F
from scipy.ndimage import uniform_filter1d
from scipy.interpolate import UnivariateSpline,PchipInterpolator
import matplotlib.pyplot as plt
S=json.load(open('data/channel_seats_v2.json'))['seats']; xs=np.arange(40,527,0.25)
def kl(X):
    try:
        kt,(a,b)=F.keel_levels(X); return (kt,np.nan if a is None else a,np.nan if b is None else b)
    except Exception: return (np.nan,)*3
K=np.array([kl(x) for x in xs],float); ok=~np.isnan(K[:,1]); Xo=xs[ok]; KT=K[ok,0]; KS=K[ok,1]; KE=K[ok,2]
def smooth(y): 
    y=uniform_filter1d(y,int(11/0.25),mode='nearest'); sp=UnivariateSpline(Xo[::8],y[::8],k=3,s=0.002*len(Xo[::8])); return sp
spS=smooth(KS); spK=smooth(KT)
sf=[t for t in S if Xo.min()<t['face_A'] and t['face_end']<Xo.max()]
# keelson: lowered so that the bow side wall >= W ; keel: raised so that BOTH walls >= W
dK=np.array([max(spS(t['face_end'])-t['keelson_bottom']+W,0)+0.1 for t in sf]); X_=np.array([t['X'] for t in sf]); o=np.argsort(X_)
dfun=PchipInterpolator(X_[o],dK[o])
# keel top floor of each seat = keel top level at the frame centre
Ffl=np.array([t['keel_top'] for t in sf]); eK=np.array([max(t['keel_top']+W-spK(t['face_A']),t['keel_top']+W-spK(t['face_end']),0)+0.1 for t in sf]); efun=PchipInterpolator(X_[o],eK[o])
ks_line=lambda x: spS(x)-dfun(np.clip(x,X_.min(),X_.max())); kt_line=lambda x: spK(x)+efun(np.clip(x,X_.min(),X_.max()))
clear=[(t['builder'],float(min(ks_line(np.linspace(t['face_A']-1.5,t['face_end']+1.5,30))-kt_line(np.linspace(t['face_A']-1.5,t['face_end']+1.5,30))))) for t in sf]
print('wall W=%.1f mm. keelson lowered %.2f..%.2f mm; keel raised %.2f..%.2f mm'%(W,dK.min(),dK.max(),eK.min(),eK.max()))
print('min vertical clearance keel-line to keelson-line (outside pockets), smallest 6:',[(b,round(c,2)) for b,c in sorted(clear,key=lambda c:c[1])[:6]])
json.dump(dict(wall=W,keelson_inner=dict(X=Xo[::8].tolist(),Z=(ks_line(Xo[::8])).round(3).tolist()),keel_top=dict(X=Xo[::8].tolist(),Z=(kt_line(Xo[::8])).round(3).tolist()),seats=S),open('data/keel_keelson_final_v1.json','w'))
fig,axs=plt.subplots(3,1,figsize=(17,17),gridspec_kw={'height_ratios':[1,1,.8]})
for a_,(xl,yl) in zip(axs,(((470,530),(-10,40)),((380,445),(-10,16)),((40,530),(-12,45)))):
    xx=np.linspace(*xl,800)
    # keel (below) and keelson (above) bodies: lower line = original outer lines untouched
    a_.fill_between(Xo,-15,KT,color='#ccc',alpha=.3,lw=0); a_.plot(Xo,KT,color='k',lw=.7,ls='--'); a_.plot(Xo,KS,color='k',lw=.7,ls='--')
    a_.plot(xx,kt_line(xx),color='tab:brown',lw=2,label='keel top: spline (raised)'); a_.plot(xx,ks_line(xx),color='g',lw=2,label='keelson inner line: spline (lowered)')
    for t in S:
        if xl[0]-8<t['X']<xl[1]+8:
            a_.plot([t['face_A']]*2,[t['keel_top'],float(kt_line(t['face_A']))],color='tab:brown',lw=2); a_.plot([t['face_end']]*2,[t['keel_top'],float(kt_line(t['face_end']))],color='tab:brown',lw=2); a_.plot([t['face_A'],t['face_end']],[t['keel_top']]*2,color='tab:brown',lw=2)
            a_.plot([t['face_A']]*2,[t['keelson_bottom'],float(ks_line(t['face_A']))],color='g',lw=2); a_.plot([t['face_end']]*2,[t['keelson_bottom'],float(ks_line(t['face_end']))],color='g',lw=2); a_.plot([t['face_A'],t['face_end']],[t['keelson_bottom']]*2,color='g',lw=2)
            a_.axvspan(t['face_A'],t['face_end'],color='tab:blue',alpha=.1); a_.text(t['X'],yl[1]-.8 if a_ is not axs[2] else yl[1]-2,str(t['builder']),ha='center',fontsize=8 if a_ is not axs[2] else 6)
    a_.set_xlim(*xl); a_.set_ylim(*yl); a_.grid(alpha=.3); a_.set_ylabel('Z (mm)')
axs[0].legend(loc='upper left'); axs[0].set_title('Keel top (brown) and keelson inner line (green): smooth spline between frames, a full pocket (wall >= %.1f mm both sides) at every frame; dashed = before; frames blue'%W)
fig.savefig('qa/keel_keelson_final_2d.png',dpi=60,bbox_inches='tight')
