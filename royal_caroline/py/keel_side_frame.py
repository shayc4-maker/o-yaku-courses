# Side view (X-Z) of the keel with its 1 mm pockets and the lower end of one frame (its arm end face against the keel wall)
import sys,json,numpy as np
b=int(sys.argv[1]) if len(sys.argv)>1 else 5; sys.argv=[sys.argv[0]]
sys.path.insert(0,'py'); import step_chain as S, frames_batch_2d as F
from scipy.interpolate import UnivariateSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
V2=json.load(open('data/keel_keelson_v2.json')); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0); DEPTH=V2['depth']
sh=S.load(); sol=S.solids(sh); C=S.side_chain(sol[16])[0]
i_end=int(np.argmax(C[:,0])); A=C[:i_end+1]; B=C[i_end:]; nh=lambda ch: sum(1 for k in range(len(ch)-1) if abs(ch[k,1]-ch[k+1,1])<2e-3 and abs(ch[k,0]-ch[k+1,0])>1.0)
sm=B if nh(A)>=nh(B) else A; sm=sm if sm[0,0]<sm[-1,0] else sm[::-1]
xc=F.XF[46-b-1]; xl=(xc-34,xc+34)
fig,ax=plt.subplots(2,1,figsize=(17,12),gridspec_kw={'height_ratios':[1.3,1]})
def keel(a,xl,yl):
    xs=np.linspace(*xl,900); top=kK(xs); m=(sm[:,0]>=xl[0]-2)&(sm[:,0]<=xl[1]+2); a.fill_between(xs,np.interp(xs,sm[m,0],sm[m,1]),top,color='#c9b79c',alpha=.6,label='keel (side view)')
    a.plot(xs,top,color='tab:brown',lw=1.2,label='keel surface spline')
    for n,X in enumerate(F.XF,1):
        if xl[0]-6<X<xl[1]+6:
            a0,a1=X-4,X+4; xx=np.linspace(a0,a1,40); fl=kK(xx)-DEPTH; a.fill_between(xx,fl,kK(xx),color='white',zorder=3); a.plot(xx,fl,color='k',lw=1.6,zorder=4); a.plot([a0,a0],[float(kK(a0))-DEPTH,float(kK(a0))],color='k',lw=1.6,zorder=4); a.plot([a1,a1],[float(kK(a1))-DEPTH,float(kK(a1))],color='k',lw=1.6,zorder=4)
            a.text(X,yl[1]-1,str(46-n),ha='center',fontsize=9)
    a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_ylabel('Z (mm)')
ztop=float(kK(xc))
keel(ax[0],xl,(-4,ztop+14))
# frame b: arm end face at the keel wall (seen from the side): from the exact hull line at the wall up to the pocket floor, sloping with the faces
from frame_arm import arm
fcx={'X-4':xc-4,'X':xc,'X+4':xc+4}; info={n:arm(X)[1] for n,X in fcx.items()}
xs3=[xc-4,xc,xc+4]; fl=[info[n]['floor'] for n in fcx]; hw=[info[n]['hull_at_wall'] for n in fcx]
ax[0].fill(xs3+xs3[::-1],fl+hw[::-1],color='tab:red',alpha=.45,zorder=5,label='frame %d: arm end face against the keel wall'%b); ax[0].plot(xs3,hw,'r-',lw=1.5,zorder=6)
ax[0].legend(loc='upper left')
for X,f_,h in zip(xs3,fl,hw): ax[0].annotate('',xy=(X,h),xytext=(X,f_),arrowprops=dict(arrowstyle='<->',color='r')); ax[0].text(X+.4,(f_+h)/2,'%.1f'%(f_-h),color='r',fontsize=9)
ax[0].annotate('',xy=(xc+9,float(kK(xc+9))),xytext=(xc+9,float(kK(xc+9))-DEPTH),arrowprops=dict(arrowstyle='<->',color='k')); ax[0].text(xc+9.6,float(kK(xc+9))-DEPTH/2,'pocket %.1f mm'%DEPTH,fontsize=9)
ax[0].set_title('Keel, side view. White = pockets (depth %.1f mm, 8 mm wide). Red = where frame %d (X-4, X, X+4) ends on the keel: the hull line at the keel wall is %.1f-%.1f mm below the pocket floor'%(DEPTH,b,min(f-h for f,h in zip(fl,hw)),max(f-h for f,h in zip(fl,hw))))
keel(ax[1],(xc-12,xc+12),(min(hw)-3,ztop+4))
ax[1].fill(xs3+xs3[::-1],fl+hw[::-1],color='tab:red',alpha=.45,zorder=5); ax[1].plot(xs3,hw,'r-',lw=1.5,zorder=6); ax[1].set_title('zoom')
fig.savefig('qa/keel_side_frame%d.png'%b,dpi=55,bbox_inches='tight'); print('floor',[round(x,2) for x in fl],'hull at wall',[round(x,2) for x in hw],'keel top at X',round(ztop,2))
