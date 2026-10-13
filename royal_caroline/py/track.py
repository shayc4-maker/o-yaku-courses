import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
def load_dark(path, sigma=1.0):
    g=np.array(Image.open(path).convert('L')).astype(float)/255
    return gaussian_filter(1-g, sigma)
def samp(D,pts):
    return map_coordinates(D,[pts[:,1],pts[:,0]],order=1,mode='constant')
def local_dir(D,p,r=6):
    best=None
    for a in np.radians(np.arange(0,180,2)):
        u=np.array([np.cos(a),np.sin(a)]); t=np.arange(-r,r+1)
        s=samp(D,p+t[:,None]*u).sum()
        if best is None or s>best[0]: best=(s,u)
    return best[1]
def refine(D,p,d,w=2.5):
    n=np.array([-d[1],d[0]]); t=np.linspace(-w,w,11)
    v=samp(D,p+t[:,None]*n)**2
    if v.sum()<1e-6: return p
    return p+n*(v*t).sum()/v.sum()
def trace(D,seed,d0,stop,step=3.0,look=18,maxang=12,minscore=0.25,maxn=3000):
    p=refine(D,np.array(seed,float),d0); d=d0/np.linalg.norm(d0); out=[p.copy()]; miss=0
    for _ in range(maxn):
        best=None
        for da in np.radians(np.arange(-maxang,maxang+0.1,1.0)):
            c,s=np.cos(da),np.sin(da); u=np.array([c*d[0]-s*d[1],s*d[0]+c*d[1]])
            t=np.arange(2,look+1,1.0); sc=samp(D,p+t[:,None]*u).mean()-0.002*abs(np.degrees(da))
            if best is None or sc>best[0]: best=(sc,u)
        sc,u=best
        if sc<minscore:
            miss+=1
            if miss>3: break
        else: miss=0
        q=refine(D,p+step*u,u)
        nd=q-p; nd/=np.linalg.norm(nd); d=0.6*d+0.4*nd; d/=np.linalg.norm(d)
        p=q; out.append(p.copy())
        if stop(p): break
    return np.array(out)
def trace_both(D,seed,stop,**kw):
    d=local_dir(D,np.array(seed,float))
    a=trace(D,seed,d,stop,**kw); b=trace(D,seed,-d,stop,**kw)
    return np.r_[b[::-1],a[1:]]
def heading(c):
    d=np.diff(c,axis=0); return np.unwrap(np.arctan2(d[:,1],d[:,0]))
def cut_turns(c,seed_idx,win=8,maxturn=np.radians(35)):
    h=heading(c); n=len(h); lo,hi=0,len(c)-1
    for i in range(seed_idx,n-win):
        if abs(h[i+win]-h[i])>maxturn: hi=i+win//2; break
    for i in range(min(seed_idx,n-1),win,-1):
        if abs(h[i]-h[i-win])>maxturn: lo=i-win//2+1; break
    return c[lo:hi+1]
def trace_cut(D,seed,stop,maxturn=np.radians(35),**kw):
    d=local_dir(D,np.array(seed,float))
    a=trace(D,seed,d,stop,**kw); b=trace(D,seed,-d,stop,**kw)
    c=np.r_[b[::-1],a[1:]]; return cut_turns(c,len(b)-1,maxturn=maxturn)
def runs1d(v):
    out=[];s=None
    for i,b in enumerate(v):
        if b and s is None: s=i
        if not b and s is not None: out.append((s,i)); s=None
    if s is not None: out.append((s,len(v)))
    return out
def snap(B,curves,ids,rng,axis,outer_sign,wide=6.5):
    """axis='row': scan rows y in rng, find x; 'col': scan columns x in rng, find y.
    ids ordered outer->inner; outer_sign=+1 if outer has larger coordinate."""
    res={i:{} for i in ids}
    for t in rng:
        est=[]
        for i in ids:
            c=np.asarray(curves[i]); a,b=(1,0) if axis=='row' else (0,1)
            j=np.argmin(abs(c[:,a]-t)); 
            if abs(c[j,a]-t)>3: est=None; break
            est.append(c[j,b])
        if est is None: continue
        lo=int(min(est))-8; hi=int(max(est))+9
        v=B[t,lo:hi] if axis=='row' else B[lo:hi,t]
        rr=runs1d(v); pos=[]
        for s,e in rr:
            w=e-s; c0=lo+(s+e-1)/2
            if w>=wide*1.0 and w<wide*2.2: pos+= [c0-w/4,c0+w/4]
            elif w>=1: pos.append(c0)
        if len(pos)!=len(ids): continue
        pos=sorted(pos,reverse=(outer_sign>0))
        if max(abs(np.array(pos)-np.array(est)))>7: continue
        for i,p in zip(ids,pos): res[i][t]=p
    return res
def apply_snap(curves,res,axis):
    out={}
    for i,c in curves.items():
        c=np.array(c,float)
        if i in res and res[i]:
            a,b=(1,0) if axis=='row' else (0,1)
            ks=np.array(sorted(res[i])); vs=np.array([res[i][k] for k in ks])
            for j in range(len(c)):
                k=c[j,a]
                if ks.min()<=k<=ks.max():
                    near=abs(ks-k).min()
                    if near<=2: c[j,b]=np.interp(k,ks,vs)
        out[i]=c
    return out
