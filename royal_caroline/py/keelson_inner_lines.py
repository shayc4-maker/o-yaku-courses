# Keelson inner (bottom) line: original profile, v1 (seat plateaus), v2 (full pockets, gaps 1.5 mm lower). Z axis stretched x3 so the 1.5 mm is visible
import sys,json,numpy as np
sys.argv=[sys.argv[0]]
import frames_batch_2d as F
import matplotlib.pyplot as plt
S=json.load(open('data/channel_seats_v2.json'))['seats']; W=1.5
xs=np.arange(380,530,0.1)
def old(X):
    try: kt,(a,b)=F.keel_levels(X); return a if a is not None else np.nan
    except Exception: return np.nan
O=np.array([old(x) for x in xs])
def seat_level(X):
    for s in S:
        if s['face_A']<=X<=s['face_end']: return s['keelson_bottom'],True
    # gap: level of the frame on the stern side (smaller X)
    prev=[s for s in S if s['face_end']<X]; return (max(prev,key=lambda s:s['face_end'])['keelson_bottom'] if prev else np.nan),False
V1=[];V2=[]
for x in xs:
    l,ins=seat_level(x); V1.append(l); V2.append(l if ins else l-W)
fig,axs=plt.subplots(2,1,figsize=(17,12))
for a,(xl,yl) in zip(axs,(((470,530),(14,36)),((380,445),(5,12)))):
    a.plot(xs,O,color='k',lw=2,label='original profile (before)'); a.plot(xs,V1,color='tab:orange',lw=1.4,label='v1 (seat plateau, previous level in gaps)'); a.plot(xs,V2,color='tab:green',lw=2,label='v2 (full pockets: gaps %.1f mm lower)'%W)
    for s in S:
        if xl[0]-5<s['X']<xl[1]+5: a.axvspan(s['face_A'],s['face_end'],color='tab:blue',alpha=.12); a.text(s['X'],yl[1]-.4,str(s['builder']),ha='center',fontsize=9)
    a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_ylabel('keelson bottom Z (mm)'); a.legend(loc='lower right')
axs[0].set_title('Keelson inner (bottom) line - frame seats shaded blue (X-4..X+4)')
fig.savefig('qa/keelson_inner_lines.png',dpi=60,bbox_inches='tight')
# numbers for frames 1-5
for s in S[-5:][::-1]:
    X=s['X']; print('frame %d seat %.1f-%.1f ceiling %.2f | original at X: %.2f | gap before(stern) level v2: %.2f'%(s['builder'],s['face_A'],s['face_end'],s['keelson_bottom'],old(X),[t for t in S if t['face_end']<s['face_A']][-1]['keelson_bottom']-W if [t for t in S if t['face_end']<s['face_A']] else float('nan')))
