# OUTER lines of ALL frames 1-45 (faces X-4, X, X+4) by the points method, on the centre-aligned data: original body plan leads (stations), original waterlines only give the progression u(X) between the two bracketing stations; bottom point on the new rabbet (neck half-width 1.8) where the stations sit on the keel, else the interpolated station start; spline through the points. No inner lines.
import json,numpy as np
from scipy.interpolate import CubicSpline,splprep,splev
C=json.load(open('data/bodyplan_centered_v1.json')); W=json.load(open('data/wl_top_centered_v1.json')); ENDS=json.load(open('data/bodyplan_ends_centered_v1.json'))
RB=json.load(open('data/rabbet_points_v3_ends.json'))['points']; R3=CubicSpline([p[0] for p in RB],[p[1] for p in RB],bc_type='natural')
XF=json.load(open('data/frames_X.json'))['X_mm']; NECK=1.8
XS={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
WL={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}
ST={}
for n in XS:
    P=np.array(C[str(n)]['points']); L=np.array(C[str(n)]['curve']); first=np.array(ENDS[str(n)]['end']) if str(n) in ENDS else P[0].copy()
    ST[n]=dict(P=P,L=L,first=first,vtop=bool(abs(P[-1,0]-P[-2,0])<0.35 and P[-1,1]-P[-2,1]>3))
def y_at(n,z):
    s=ST[n]; L=s['L']; f=s['first']
    if z<L[:,1].min():
        return float(np.interp(z,[f[1],s['P'][0,1]],[f[0],s['P'][0,0]])) if f[1]-1e-9<=z else None
    i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0]
    if len(i)==0: return None
    j=i[0]; t=(z-L[j,1])/(L[j+1,1]-L[j,1]); return float(L[j,0]+t*(L[j+1,0]-L[j,0]))
def wl(k): P=np.array(W[k]['points_XY']); return P[np.argsort(P[:,0])]
def ywl(k,x):
    P=wl(k)
    if x>P[-1,0]: s=(P[-1,1]-P[-3,1])/(P[-1,0]-P[-3,0]); return float(P[-1,1]+s*(x-P[-1,0]))
    if x<P[0,0]: s=(P[2,1]-P[0,1])/(P[2,0]-P[0,0]); return float(P[0,1]+s*(x-P[0,0]))
    return float(np.interp(x,P[:,0],P[:,1]))
order=sorted(XS,key=lambda n:XS[n])
def face(X):
    for n in order:
        if abs(X-XS[n])<0.6: return station_face(n,X),'station %d'%n
    for a,b in zip(order[:-1],order[1:]):
        if XS[a]<X<XS[b]: return between(a,b,X),'between %d-%d'%(a,b)
    return None,'outside'
def bottom(X,A,B):
    fa,fb=ST[A]['first'],ST[B]['first']; t=(X-XS[A])/(XS[B]-XS[A])
    onkeel=lambda n:abs(ST[n]['first'][1]-float(R3(XS[n])))<1.2 if 30<=XS[n]<=527.8 else False
    if onkeel(A) and onkeel(B) and 30<=X<=527.8: return (NECK,float(R3(X)),'rabbet')
    return (float(fa[0]+t*(fb[0]-fa[0])),float(fa[1]+t*(fb[1]-fa[1])),'interp')
def station_face(n,X):
    s=ST[n]; P=s['P']; zb=float(R3(X)) if (30<=X<=527.8 and abs(s['first'][1]-float(R3(XS[n])))<1.2) else float(s['first'][1]); pts=[('bottom',float(s['first'][0]),zb)]
    n_=len(P); lim=n_-2 if s['vtop'] else n_-1
    pts+=[('st pt',float(y),float(z)) for y,z in P[:lim] if z>zb+0.2]
    if s['vtop']: pts+=[('corner',float(P[-2,0]),float(P[-2,1])),('top',float(P[-1,0]),float(P[-1,1]))]
    else: pts+=[('top',float(P[-1,0]),float(P[-1,1]))]
    return pts
def between(A,B,X):
    yb,zb,kind=bottom(X,A,B); pts=[('bottom '+kind,yb,zb)]; t=(X-XS[A])/(XS[B]-XS[A]); info={}
    for k,z in WL.items():
        if z<=zb+1.5: continue
        ya,yB=y_at(A,z),y_at(B,z)
        if ya is None or yB is None: continue
        a,b=ywl(k,XS[A]),ywl(k,XS[B]); P=wl(k)
        if abs(b-a)<1.0 or not(P[0,0]-5<=X<=P[-1,0]+5 and P[0,0]-5<=XS[A] and XS[B]<=P[-1,0]+5): u=t; mode='x'
        else: u=(ywl(k,X)-a)/(b-a); mode='wl'
        u=float(np.clip(u,-0.1,1.1)); pts.append(('WL '+k,ya+u*(yB-ya),z)); info[k]=(round(u,2),mode)
    a,b=ywl('VII',XS[A]),ywl('VII',XS[B]); Pw=wl('VII'); uv=(ywl('VII',X)-a)/(b-a) if abs(b-a)>=1.0 and Pw[0,0]-5<=X<=Pw[-1,0]+5 else t; uv=float(np.clip(uv,-0.1,1.1))
    sa,sb=ST[A],ST[B]; corner=sa['vtop'] and sb['vtop']
    zlim=min(sa['P'][-2 if sa['vtop'] else -1,1],sb['P'][-2 if sb['vtop'] else -1,1])-0.5
    for z in [z for z in sb['P'][:,1] if WL['VII']+4<z<zlim]:
        ya,yB=y_at(A,z),y_at(B,z)
        if ya is not None and yB is not None: pts.append(('up',ya+uv*(yB-ya),float(z)))
    if corner: pts+=[('corner',sa['P'][-2,0]+uv*(sb['P'][-2,0]-sa['P'][-2,0]),sa['P'][-2,1]+uv*(sb['P'][-2,1]-sa['P'][-2,1])),('top',sa['P'][-1,0]+uv*(sb['P'][-1,0]-sa['P'][-1,0]),sa['P'][-1,1]+uv*(sb['P'][-1,1]-sa['P'][-1,1]))]
    else: pts+=[('top',sa['P'][-1,0]+uv*(sb['P'][-1,0]-sa['P'][-1,0]),sa['P'][-1,1]+uv*(sb['P'][-1,1]-sa['P'][-1,1]))]
    return pts
def curve(pts,corner_last):
    q=np.array([(y,z) for _,y,z in pts]); q=q[np.argsort(q[:,1])] if False else q
    body=q[:-1] if corner_last else q
    keep=[0]+[i for i in range(1,len(body)) if np.hypot(*(body[i]-body[i-1]))>1e-6]; body=body[keep]; tck,u=splprep(body.T,k=3,s=0); y,z=splev(np.linspace(0,1,500),tck)
    return np.r_[np.c_[y,z],[q[-1]]] if corner_last else np.c_[y,z]
out={}; bad=[]; RAW={}
for b in range(1,46):
    xc=XF[45-b]; out[b]={}
    for nm,X in (('back',xc-4),('mid',xc),('front',xc+4)):
        pts,kind=face(X)
        if pts is None: bad.append((b,nm,X)); continue
        corner=any(p[0]=='corner' for p in pts); L=curve(pts,corner); RAW[(b,nm)]=L; out[b][nm]=dict(X=X,kind=kind,points=[[p[0],round(float(p[1]),3),round(float(p[2]),3)] for p in pts],curve=L.round(3).tolist())
json.dump({str(b):v for b,v in out.items()},open('data/frames_outer_all_v1.json','w'))
print('frames',len(out),'faces',sum(len(v) for v in out.values()),'outside:',bad)
# checks: progression monotone between faces of one frame, curvature sign changes of the outline
viol=[];sc=[]
for b,fr in out.items():
    if len(fr)<3: continue
    Ls={k:RAW[(b,k)] for k in fr}
    for z in np.arange(10,100,5.0):
        ys=[]
        for k in ('back','mid','front'):
            L=Ls[k]; 
            if L[:,1].min()<z<L[:,1].max(): ys.append(float(np.interp(z,L[:,1],L[:,0])))
            else: ys=None; break
        if ys and (ys[0]-ys[1])*(ys[1]-ys[2])<-0.01: viol.append((b,z,[round(v,1) for v in ys]))
    for k,L in Ls.items():
        sl=np.r_[0,np.cumsum(np.hypot(*np.diff(L,axis=0).T))]; t=np.arange(0,sl[-1],1.0); Y=np.interp(t,sl,L[:,0]); Z=np.interp(t,sl,L[:,1]); from scipy.ndimage import gaussian_filter1d as gf; Y=gf(Y,2); Z=gf(Z,2); d1y=np.gradient(Y); d1z=np.gradient(Z); kk=d1y*np.gradient(d1z)-d1z*np.gradient(d1y); s=np.sign(kk[3:-3][np.abs(kk[3:-3])>2e-3]); sc.append((b,k,int((np.diff(s)!=0).sum())))
print('non-monotone face progression (back/mid/front Y at a Z):',len(viol),viol[:12]); print('curvature sign changes per face: max',max(s[2] for s in sc),'; faces with >4:',[s for s in sc if s[2]>4][:15])
import collections; print('kinds:',collections.Counter(v['kind'].split(' ')[0] for fr in out.values() for v in fr.values()))
