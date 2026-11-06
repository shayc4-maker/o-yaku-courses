# FRAME 1 by points only (no self-made lines): faces X-4=520.03, X=524.03 (interpolated between stations 2 and 1) and X+4=528.03 (= station 1, approved). Original body plan leads; original waterlines give only the SHAPE of the progression between the two stations: u_k(X) = (Y_WL(X)-Y_WL(X2)) / (Y_WL(X1)-Y_WL(X2)) at each waterline height; point Y = Y_st2(Z_k) + u_k * (Y_st1(Z_k) - Y_st2(Z_k)). Bottom point ON the new rabbet (Z = rabbet(X)), above WL VII the progression u_VII is used for the station points. Points then joined by an interpolating cubic spline.
import json,numpy as np
from scipy.interpolate import CubicSpline,splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
C=json.load(open('data/bodyplan_splines_v1.json')); W=json.load(open('data/wl_top_points_all.json')); ENDS=json.load(open('data/bodyplan_ends_proposed_v1.json'))
RB=json.load(open('data/rabbet_points_v3_ends.json'))['points']; R3=CubicSpline([p[0] for p in RB],[p[1] for p in RB],bc_type='natural')
X1,X2=527.8,505.8; XC=524.0326; FACES={'back X-4':XC-4,'mid X':XC,'front X+4':XC+4}; WL={'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}
def ycross(n,z):
    L=np.array(C[str(n)]['curve']); i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0]
    j=i[0]; t=(z-L[j,1])/(L[j+1,1]-L[j,1]); return float(L[j,0]+t*(L[j+1,0]-L[j,0]))
def ywl(k,x):
    P=np.array(W[k]['points_XY']); P=P[np.argsort(P[:,0])]
    if x>P[-1,0]: s=(P[-1,1]-P[-3,1])/(P[-1,0]-P[-3,0]); return float(P[-1,1]+s*(x-P[-1,0]))      # linear extension past the end of the waterline
    return float(np.interp(x,P[:,0],P[:,1]))
U={}
for k in WL:
    a,b=ywl(k,X2),ywl(k,X1); U[k]=lambda x,k=k,a=a,b=b:(ywl(k,x)-a)/(b-a)
P1=np.array(C['1']['points']); P2=np.array(C['2']['points'])
up_z=[z for z in P1[:,1] if z>WL['VII']+4]       # approved station-1 points above WL VII
res={}; fig,axs=plt.subplots(2,1,figsize=(14,24),gridspec_kw={'height_ratios':[1,1.15]}); col={'back X-4':'tab:blue','mid X':'k','front X+4':'tab:red'}
for nm,X in FACES.items():
    zr=float(R3(X)); ye=float(np.interp(X,[X2,X1],[ENDS['2']['end'][0],ENDS['1']['end'][0]])); pts=[('rabbet end',ye,zr)]
    if nm.startswith('front'):
        # station 1 itself (approved): its own points above the hook, end point on the rabbet
        pts+= [('st1 pt%d'%i,float(y),float(z)) for i,(y,z) in enumerate(P1) if z>zr+0.2 and i<len(P1)-2]
        pts+= [('st1 corner',float(P1[-2,0]),float(P1[-2,1])),('st1 top',float(P1[-1,0]),float(P1[-1,1]))]
        res[nm]=dict(X=X,u={},points=pts); continue
    u={}
    for k,z in WL.items():
        if z<=zr+0.5: continue
        u[k]=U[k](X); y2=ycross(2,z) if z>np.array(C['2']['curve'])[:,1].min() else float(np.interp(z,[ENDS['2']['end'][1],P2[0,1]],[ENDS['2']['end'][0],P2[0,0]])); y1=ycross(1,z) if z>=np.array(C['1']['curve'])[:,1].min() else float(np.interp(z,[ENDS['1']['end'][1],P1[0,1]],[ENDS['1']['end'][0],P1[0,0]]))
        pts.append(('WL '+k,y2+u[k]*(y1-y2),z))
    uv=U['VII'](X)
    for z in up_z:
        if z>WL['VII']+4 and z<P1[-2,1]-0.1:
            y2=float(np.interp(z,np.array(C['2']['curve'])[:,1],np.array(C['2']['curve'])[:,0])); y1=float(np.interp(z,np.array(C['1']['curve'])[:,1],np.array(C['1']['curve'])[:,0])); pts.append(('up Z%.0f'%z,y2+uv*(y1-y2),float(z)))
    yc=P2[-2,0]+uv*(P1[-2,0]-P2[-2,0]); zc=P2[-2,1]+uv*(P1[-2,1]-P2[-2,1]); yt=P2[-1,0]+uv*(P1[-1,0]-P2[-1,0]); zt=P2[-1,1]+uv*(P1[-1,1]-P2[-1,1]); pts+= [('corner',yc,zc),('top',yt,zt)]
    res[nm]=dict(X=X,u=u,points=pts)
for nm,d in res.items():
    pts=d['points']; q=np.array([(y,z) for _,y,z in pts]); body=q[:-1]; tck,uu=splprep(body.T,k=3,s=0); y,z=splev(np.linspace(0,1,500),tck); line=np.r_[np.c_[y,z],[q[-1]]]; d['curve']=line.round(3).tolist()
    print('%s X=%.2f: rabbet Z %.2f | u = %s | %d points'%(nm,d['X'],pts[0][2],{k:round(v,2) for k,v in d['u'].items()},len(pts)))
    for a in axs:
        a.plot(np.r_[-line[::-1,0],line[:,0]],np.r_[line[::-1,1],line[:,1]],color=col[nm],lw=1.2,label='%s X=%.1f'%(nm,d['X'])); a.plot(q[:,0],q[:,1],'o',color=col[nm],mfc='none',ms=5)
    for i,(lab,yy,zz) in enumerate(pts): axs[1].text(yy+.6,zz+.4,'%d (%.1f, %.1f)'%(i,yy,zz),fontsize=7,color=col[nm],clip_on=True)
axs[0].set_xlim(-60,60); axs[0].set_ylim(15,125); axs[1].set_xlim(0,40); axs[1].set_ylim(18,70)
for a in axs: a.set_aspect('equal'); a.grid(alpha=.3)
axs[0].legend(); axs[0].set_title('Frame 1, front view: 1 line = station 1 (approved, red) in front, 2 interpolated lines behind it (mid 524, back 520); circles = points'); axs[1].set_title('zoom right side with point numbers')
fig.savefig('qa/frame1_points_v1.png',dpi=60,bbox_inches='tight'); json.dump({k:dict(X=v['X'],u=v['u'],points=[[l,round(y,3),round(z,3)] for l,y,z in v['points']]) for k,v in res.items()},open('data/frame1_points_v1.json','w'))
with PdfPages('qa/frame1_points_v1.pdf') as pdf: pdf.savefig(fig)
