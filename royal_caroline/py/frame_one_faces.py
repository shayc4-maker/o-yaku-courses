# One frame: the three face planes X-4, X, X+4, each built with the keel/keelson levels read at ITS OWN X (they rise towards the bow)
import sys,numpy as np
sys.argv=[sys.argv[0]]+sys.argv[1:]
import frames_batch_2d as F
from shapely.ops import unary_union
import matplotlib.pyplot as plt
b=int(sys.argv[1]); OUR=46-b; xc=F.XF[OUR-1]; faces={}
for nm,X in (('X-4',xc-4),('X',xc),('X+4',xc+4)):
    try: poly,info=F.face_poly(X,X)
    except Exception: print('%-4s X=%6.2f  no keel-keelson gap here (keel and keelson are one solid, the stem)'%(nm,X)); continue
    faces[nm]=(X,poly,info)
    print('%-4s X=%6.2f  keel top Z=%5.2f  keelson bottom %5.2f top %5.2f  leg bottom %5.2f  leg tops %5.2f'%(nm,X,info['keel_top'],info['ks_bot'],info['ks_top'],info['leg_bot'],info['zt']))
cols={'X-4':'tab:blue','X':'k','X+4':'tab:red'}
fig,axs=plt.subplots(1,3,figsize=(22,10),gridspec_kw={'width_ratios':[1,1,1]})
def draw(a,xl,yl,t):
    for nm,(X,poly,info) in faces.items():
        for g in (poly,F.mirror(poly)):
            for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color=cols[nm],lw=1.2)
        a.axhline(info['keel_top'],color=cols[nm],lw=.5,ls=':'); a.axhline(info['ks_bot'],color=cols[nm],lw=.5,ls='--')
    i0=faces['X'][2]; a.add_patch(plt.Rectangle((-F.KB,-20),2*F.KB,i0['keel_top']+20,color='#888',alpha=.35)); a.add_patch(plt.Rectangle((-F.KB,i0['ks_bot']),2*F.KB,i0['ks_top']-i0['ks_bot'],color='#888',alpha=.35))
    a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(t,fontsize=10)
lo=faces['X-4'][2]; hi=faces[list(faces)[-1]][2]
draw(axs[0],(-85,85),(-5,115),'frame %d (our %d): faces X-4 blue, X black, X+4 red'%(b,OUR))
draw(axs[1],(-14,40),(lo['keel_top']-4,hi['keel_top']+12),'keel lap: keel top Z X-4 %.2f, X %.2f'%(lo['keel_top'],hi['keel_top']))
draw(axs[2],(-14,40),(lo['ks_bot']-4,hi['ks_top']+8),'keelson bottom: X-4 %.2f, X %.2f'%(lo['ks_bot'],hi['ks_bot']))
fig.savefig('qa/frame%d_faces_2d.png'%b,dpi=60,bbox_inches='tight')
