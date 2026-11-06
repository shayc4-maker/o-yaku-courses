# FRAME N by points only (generic; run: python3 py/frame_points_wl.py N A B  with A = station behind, B = station ahead): faces 509.5 / 513.5 / 517.5 lie between station 2 (505.8, behind) and station 1 (527.8, ahead). Same method as frame 1: original body plan leads, original waterlines give only the progression u_k(X). Levels where station 1 does not exist (Z < 26.05, i.e. WL I, II): anchored on station 2 and the waterline shape, fading to the waterline end; levels closer than 1.5 mm above the rabbet are skipped (the hook segment spans them). Bottom point ON the new rabbet.
import json,sys,numpy as np
from scipy.interpolate import CubicSpline,splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
CEN=os.environ.get('CENTERED','0')=='1'; SUF='_centered' if CEN else ''
C=json.load(open('data/bodyplan_centered_v1.json' if CEN else 'data/bodyplan_splines_v1.json')); W=json.load(open('data/wl_top_centered_v1.json' if CEN else 'data/wl_top_points_all.json')); ENDS=json.load(open('data/bodyplan_ends_centered_v1.json' if CEN else 'data/bodyplan_ends_proposed_v1.json'))
RB=json.load(open('data/rabbet_points_v3_ends.json'))['points']; R3=CubicSpline([p[0] for p in RB],[p[1] for p in RB],bc_type='natural')
FN=int(sys.argv[1]); SA=int(sys.argv[2]); SB=int(sys.argv[3]); XS={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4}; XA,XB=XS[SA],XS[SB]; XCs=json.load(open('data/frames_X.json'))['X_mm']; XC=XCs[46-FN-1]; FACES={'back X-4':XC-4,'mid X':XC,'front X+4':XC+4}; WL={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}
PA=np.array(C[str(SA)]['points']); PB=np.array(C[str(SB)]['points']); LA=np.array(C[str(SA)]['curve']); LB=np.array(C[str(SB)]['curve'])
def y_at(L,P,n,z):   # n = station number      # station curve Y at Z, hook below the curve start
    if z<L[:,1].min(): return float(np.interp(z,[ENDS[str(n)]['end'][1],P[0,1]],[ENDS[str(n)]['end'][0],P[0,0]])) if z>=ENDS[str(n)]['end'][1]-1e-9 else None
    i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0]
    if len(i)==0: return None
    j=i[0]; t=(z-L[j,1])/(L[j+1,1]-L[j,1]); return float(L[j,0]+t*(L[j+1,0]-L[j,0]))
def wl(k):
    P=np.array(W[k]['points_XY']); return P[np.argsort(P[:,0])]
def ywl(k,x):
    P=wl(k)
    if x>P[-1,0]: s=(P[-1,1]-P[-3,1])/(P[-1,0]-P[-3,0]); return float(P[-1,1]+s*(x-P[-1,0]))
    return float(np.interp(x,P[:,0],P[:,1]))
res={}; col={'back X-4':'tab:blue','mid X':'k','front X+4':'tab:red'}
for nm,X in FACES.items():
    zr=float(R3(X)); ye=float(np.interp(X,[XA,XB],[ENDS[str(SA)]['end'][0],ENDS[str(SB)]['end'][0]])); pts=[('rabbet end',ye,zr)]; info={}
    if abs(X-XB)<0.6:      # this face lies on the station ahead: its approved points
        pts+=[('st%d pt%d'%(SB,i),float(y),float(z)) for i,(y,z) in enumerate(PB) if z>zr+0.2 and i<len(PB)-2]+[('st%d corner'%SB,float(PB[-2,0]),float(PB[-2,1])),('st%d top'%SB,float(PB[-1,0]),float(PB[-1,1]))]; info['station']=SB
        q=np.array([(y,z) for _,y,z in pts]); tck,uu=splprep(q[:-1].T,k=3,s=0); y,z=splev(np.linspace(0,1,500),tck); line=np.r_[np.c_[y,z],[q[-1]]]; res[nm]=dict(X=X,rabbet_Z=zr,info=info,points=[[l,round(float(a),3),round(float(b),3)] for l,a,b in pts],curve=line.round(3).tolist()); print('%s X=%.2f = station %d (approved)'%(nm,X,SB)); continue
    for k,z in WL.items():
        if z<=zr+1.5: continue
        ya=y_at(LA,PA,SA,z)
        if ya is None: continue
        yb=y_at(LB,PB,SB,z)
        if yb is not None:
            a,b=ywl(k,XA),ywl(k,XB); u=(ywl(k,X)-a)/(b-a); y=ya+u*(yb-ya); info[k]='u=%.2f'%u
        elif False:
            Pw=wl(k); xe=Pw[-1,0]; g=float(np.clip((X-XA)/(xe-XA),0,1)); y=ywl(k,X)+(ya-ywl(k,XA))*(1-g); info[k]='anchored g=%.2f'%g
        else: continue      # no station 1 at this level (below its start): no point, the line goes from the rabbet end to the next level
        pts.append(('WL '+k,y,z))
    uv=(ywl('VII',X)-ywl('VII',XA))/(ywl('VII',XB)-ywl('VII',XA)); info['VII u']=round(uv,2)
    for z in [z for z in PB[:,1] if z>WL['VII']+4 and z<PB[-2,1]-0.1]:
        y2=y_at(LA,PA,SA,z); y1=y_at(LB,PB,SB,z); pts.append(('up Z%.0f'%z,y2+uv*(y1-y2),float(z)))
    yc=PA[-2,0]+uv*(PB[-2,0]-PA[-2,0]); zc=PA[-2,1]+uv*(PB[-2,1]-PA[-2,1]); yt=PA[-1,0]+uv*(PB[-1,0]-PA[-1,0]); zt=PA[-1,1]+uv*(PB[-1,1]-PA[-1,1]); pts+=[('corner',yc,zc),('top',yt,zt)]
    q=np.array([(y,z) for _,y,z in pts]); tck,uu=splprep(q[:-1].T,k=3,s=0); y,z=splev(np.linspace(0,1,500),tck); line=np.r_[np.c_[y,z],[q[-1]]]
    res[nm]=dict(X=X,rabbet_Z=zr,info=info,points=[[l,round(float(a),3),round(float(b),3)] for l,a,b in pts],curve=line.round(3).tolist())
    print('%s X=%.2f rabbet Z %.2f | %s | %d points'%(nm,X,zr,info,len(pts)))
json.dump(res,open('data/frame%d_points%s_v1.json'%(FN,SUF),'w'))
f1=json.load(open('data/frame1_points_v1.json')) if False else None
fig,axs=plt.subplots(2,1,figsize=(14,24),gridspec_kw={'height_ratios':[1,1.15]})
for nm,d in res.items():
    line=np.array(d['curve']); q=np.array([[p[1],p[2]] for p in d['points']])
    for a in axs:
        a.plot(np.r_[-line[::-1,0],line[:,0]],np.r_[line[::-1,1],line[:,1]],color=col[nm],lw=1.2,label='%s X=%.1f'%(nm,d['X'])); a.plot(q[:,0],q[:,1],'o',color=col[nm],mfc='none',ms=5)
    for i,(l,yy,zz) in enumerate(d['points']): axs[1].text(yy+.6,zz+.4,'%d (%.1f, %.1f)'%(i,yy,zz),fontsize=7,color=col[nm],clip_on=True)
for n,c in ((SA,'gray'),(SB,'orange')):
    L=np.array(C[str(n)]['curve']); axs[0].plot(np.r_[-L[::-1,0],L[:,0]],np.r_[L[::-1,1],L[:,1]],color=c,lw=.8,ls='--',label='station %d (approved)'%n); axs[1].plot(L[:,0],L[:,1],color=c,lw=.8,ls='--')
axs[0].set_xlim(-70,70); axs[0].set_ylim(0,125); axs[1].set_xlim(0,40); axs[1].set_ylim(max(0,res['back X-4']['rabbet_Z']-4),res['back X-4']['rabbet_Z']+56)
for a in axs: a.set_aspect('equal'); a.grid(alpha=.3)
axs[0].legend(fontsize=8); axs[0].set_title('Frame %d, front view: three faces between station %d (grey dashed) and station %d (orange dashed)'%(FN,SA,SB)); axs[1].set_title('zoom right side with point numbers and coordinates')
fig.savefig('qa/frame%d_points%s_v1.png'%(FN,SUF),dpi=60,bbox_inches='tight')
from matplotlib.backends.backend_pdf import PdfPages
with PdfPages('qa/frame%d_points%s_v1.pdf'%(FN,SUF)) as pdf: pdf.savefig(fig)
