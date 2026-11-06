# frames (builder numbers) 1-4: lower end ON the calibrated upper rabbet at each face X; the exact loft hull line is trimmed at Z=rabbet(X) (or extended along its own end tangent if it stops above), then the end point moves HORIZONTALLY to the keel half-width Y=2.65 (short horizontal piece). Loft = stations with the approved end points. 2D for approval.
import sys,json,numpy as np
bl=[int(a) for a in sys.argv[1:]] or [1,2,3,4]; sys.argv=[sys.argv[0]]
sys.path.insert(0,'py')
import hull_new_sections as HN
HN.C=json.load(open('data/bodyplan_splines_v2_ends.json')); HN._C={}; HN._CACHE='/tmp/claude-0/x/loft_ends_cache.pkl'; HN.SURF=None
import frames_batch_2d as FB
from scipy.interpolate import splprep,splev,CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KB=2.65
R2=(lambda p:CubicSpline([q[0] for q in p],[q[1] for q in p],bc_type='natural'))(json.load(open('data/rabbet_points_v2_calibrated.json'))['points'])
def hull_line_v2(X):
    P=HN.section(min(X,527.7)); zz=np.round(P[:,1],2); _,ui=np.unique(zz,return_index=True); P=P[ui]; P=P[np.argsort(P[:,1])]
    z0,z1=P[0,1],P[-1,1]; zs=np.r_[z0,np.linspace(z0,z1,15)[1:]]; pts=np.array([(float(np.interp(z,P[:,1],P[:,0])),float(z)) for z in zs]); tk,u=splprep(pts.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tk); return np.c_[y,z]
def end_on_rabbet(X):
    P=hull_line_v2(X); zr=float(R2(X)); note=''
    if P[0,1]<zr:                                  # trim
        i=int(np.argmax(P[:,1]>=zr)); y0=float(np.interp(zr,[P[i-1,1],P[i,1]],[P[i-1,0],P[i,0]])); L=np.vstack([[y0,zr],P[i:]]); note='trimmed %.2f'%(zr-P[0,1])
    else:                                          # extend along the end tangent
        t=P[6]-P[0]; t/=np.hypot(*t); s=(zr-P[0,1])/t[1] if abs(t[1])>1e-6 else 0; L=np.vstack([[P[0,0]+t[0]*s,zr],P]) if s>0 else P; note='extended %.2f'%(zr-P[0,1])
        if s<=0 or abs(zr-P[0,1])<1e-6: L=np.vstack([[P[0,0],zr],P[1:]]) if s<=0 else L
    return L,zr,note
cols={'X-4':'tab:blue','X':'k','X+4':'tab:red'}; fig,axs=plt.subplots(2,len(bl),figsize=(5.4*len(bl),11)); axs=axs.reshape(2,-1); out={}
for j,b in enumerate(bl):
    xc=FB.XF[46-b-1]; out[b]={}
    for nm,X in (('X-4',xc-4),('X',xc),('X+4',xc+4)):
        L,zr,note=end_on_rabbet(X); y_end=L[0,0]; full=np.vstack([[KB,zr],L]) if y_end>KB+1e-6 else L
        out[b][nm]=dict(X=X,rabbet_Z=zr,cut_Y=float(y_end),note=note)
        print('frame %d %s X=%.1f: end ON rabbet Z=%.2f (%s), hull line meets it at Y=%.2f, horizontal to Y=%.2f (%.2f mm)'%(b,nm,X,zr,note,y_end,KB,y_end-KB))
        for r in (0,1):
            a=axs[r,j]; a.plot(np.r_[-full[::-1,0],full[:,0]],np.r_[full[::-1,1],full[:,1]],color=cols[nm],lw=1.3); a.plot([KB,-KB],[zr,zr],'o',mfc='none',mec='lime',ms=7)
    z=out[b]['X']['rabbet_Z']
    for r,(xl,yl,t) in enumerate((((-85,85),(-5,115),'frame %d X=%.1f'%(b,xc)),((-14,14),(z-4,z+12),'bottom: ends on the rabbet'))): a=axs[r,j]; a.axvline(KB,color='gray',lw=.5); a.axvline(-KB,color='gray',lw=.5); a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(t,fontsize=9)
fn='_'.join(map(str,bl)); fig.suptitle('Frames: exact hull line trimmed/extended to the calibrated upper rabbet, then horizontal to the keel width. Blue X-4, black X, red X+4',fontsize=9); fig.savefig('qa/frames_on_rabbet_%s.png'%fn,dpi=60,bbox_inches='tight'); json.dump(out,open('data/frames_on_rabbet_%s.json'%fn,'w'))
