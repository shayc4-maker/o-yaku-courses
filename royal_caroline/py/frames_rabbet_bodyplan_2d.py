# body plan (Y-Z sections) of frames (builder numbers) with the exact outer hull line ending at the rabbet spline (data/rabbet_points_v1.json) at each face X; dotted = the part cut off
import sys,json,numpy as np
bl=[int(a) for a in sys.argv[1:]]; sys.argv=[sys.argv[0]]
sys.path.insert(0,'py')
import frames_batch_2d as F
from scipy.interpolate import CubicSpline,UnivariateSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
pts=json.load(open('data/rabbet_points_v1.json'))['points']; R=CubicSpline([p[0] for p in pts],[p[1] for p in pts],bc_type='natural')
V2=json.load(open('data/keel_keelson_v2.json')); sK=UnivariateSpline(V2['keelson_spline']['X'],V2['keelson_spline']['Z'],k=3,s=0); kK=UnivariateSpline(V2['keel_surface']['X'],V2['keel_surface']['Z'],k=3,s=0)
KB=F.KB; cols={'X-4':'tab:blue','X':'k','X+4':'tab:red'}; n=len(bl)
fig,axs=plt.subplots(2,n,figsize=(5.4*n,12),gridspec_kw={'height_ratios':[1.5,1.2]}); axs=axs.reshape(2,n); out={}
for j,b in enumerate(bl):
    xc=F.XF[46-b-1]; out[b]={}
    for nm,X in (('X-4',xc-4),('X',xc),('X+4',xc+4)):
        P=F.hull_line(X)            # exact hull line, own order (lowest end first)
        m=(P[:,0]<=P[0,0]+10); c=np.polyfit(P[m,0],P[m,1],3); ys=np.linspace(KB,P[0,0],12,endpoint=False); O=np.vstack([np.c_[ys,np.polyval(c,ys)],P])   # extended inward to the keel wall as in frame_arm
        zr=float(R(X)); i=int(np.argmax(O[:,1]>=zr)) if (O[:,1]>=zr).any() else 0
        if i>0: y0=float(np.interp(zr,[O[i-1,1],O[i,1]],[O[i-1,0],O[i,0]])); keep=np.vstack([[y0,zr],O[i:]]); cut=O[:i+1]
        else: y0=float(O[0,0]); keep=O; cut=O[:1]
        sl=lambda A: np.degrees(np.arctan2(A[1,1]-A[0,1],A[1,0]-A[0,0]))
        out[b][nm]=dict(X=X,rabbet_Z=zr,cut_Y=y0,wall_Z=float(O[0,1]),below=float(zr-O[0,1]),angle=float(sl(keep[:12:11]) if len(keep)>11 else 0.0))
        for r in (0,1):
            a=axs[r,j]; a.plot(np.r_[-keep[::-1,0],keep[:,0]],np.r_[keep[::-1,1],keep[:,1]],color=cols[nm],lw=1.3)
            a.plot(np.r_[-cut[::-1,0],cut[:,0]],np.r_[cut[::-1,1],cut[:,1]],color=cols[nm],lw=.8,ls=':')
            a.plot([y0,-y0],[zr,zr],'o',mfc='none',mec='lime',ms=6)
    for r,(xl,yl,t) in enumerate((((-85,85),(-5,115),'frame %d X=%.1f  body plan'%(b,xc)),((-14,14),(out[b]['X']['rabbet_Z']-5,out[b]['X']['rabbet_Z']+12),'bottom: cut points (green) on the rabbet'))):
        a=axs[r,j]; a.axvline(KB,color='gray',lw=.5); a.axvline(-KB,color='gray',lw=.5)
        a.plot([-KB,KB],[float(kK(min(xc,526))),float(kK(min(xc,526)))],color='gray',lw=.6); a.plot([-KB,KB],[float(sK(min(xc,526))),float(sK(min(xc,526)))],color='gray',lw=.6)
        a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(t,fontsize=9)
    print('frame %d'%b,' | '.join('%s: rabbet Z %.2f, hull at wall %.2f (cut off %.2f), cut Y %.2f'%(k,v['rabbet_Z'],v['wall_Z'],v['below'],v['cut_Y']) for k,v in out[b].items()))
fig.suptitle('Outer (iron) hull line ending at the rabbet. Blue X-4, black X, red X+4. Dotted = cut off below the rabbet. Grey = keel wall, keel top, keelson bottom (not shifted)',fontsize=9)
fn='_'.join(map(str,bl)); fig.savefig('qa/frames_rabbet_bodyplan_%s.png'%fn,dpi=60,bbox_inches='tight'); json.dump(out,open('data/frames_rabbet_bodyplan_%s.json'%fn,'w'))
