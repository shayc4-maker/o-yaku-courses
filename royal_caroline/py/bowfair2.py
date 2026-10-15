import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from bowsurf import *
from scipy.interpolate import UnivariateSpline
SEC={float(k):np.array(v) for k,v in json.load(open(O+'/bow_sections.json')).items()}
DEG=int(sys.argv[2]) if len(sys.argv)>2 else 5
def aft_wl(z):
    xs=np.arange(515,XS1+0.01,0.5); ys=[yat(section(x,kind='pchip'),z) for x in xs]
    m=np.array([y is not None for y in ys])
    if m.sum()<4: return None
    xs=xs[m]; ys=np.array([y for y in ys if y is not None]); 
    p=np.polyfit(xs-XS1,ys,3); return np.polyval(p,0),np.polyval(np.polyder(p),0)
WLUSE=True
def fwd_data(z):
    pts=[]
    for x in sorted(SEC):
        if x<=XS1+0.5: continue
        s=SEC[x]
        if s[0,1]<=z<=s[-1,1]: pts.append((x,float(np.interp(z,s[:,1],s[:,0]))))
    for n,zz in WLZ.items():
        if WLUSE and n!='BASE' and abs(zz-z)<0.6 and n in wl:
            c=wl[n]; c=c[c[:,0]>XS1+0.5]; pts=[p for p in pts if False]+[tuple(v) for v in c[::3]]
    return np.array(pts) if pts else None
NIT=int(sys.argv[4]) if len(sys.argv)>4 else 1
for it in range(NIT):
    FW={}
    for z in np.arange(26,ZTOPB+0.01,1.0):
        a=aft_wl(z); d=fwd_data(z)
        if a is None or d is None or len(d)<4: continue
        y0,s0=a; xr=Xr(z); L=xr-XS1
        if L<=1: continue
        t=(d[:,0]-XS1)/L
        # y(t)=y0 + s0*L*t + sum_{k=2..DEG} c_k t^k ,  y(1)=YR
        A=np.c_[[t**k for k in range(2,DEG+1)]].T; b=d[:,1]-y0-s0*L*t
        Ae=np.ones(DEG-1); be=YR-y0-s0*L
        # constrained LS via KKT
        M=np.block([[2*A.T@A,Ae[:,None]],[Ae[None,:],np.zeros((1,1))]]); r=np.r_[2*A.T@b,be]
        sol=np.linalg.solve(M,r); c=sol[:-1]
        FW[float(z)]=(y0,s0,L,c)
    SSEC=float(sys.argv[3]) if len(sys.argv)>3 else 0.01
    def Yf(z,x):
        y0,s0,L,c=FW[z]; t=(x-XS1)/L
        return y0+s0*L*t+sum(ck*t**(k+2) for k,ck in enumerate(c))
    NEW={}
    for x in np.r_[[XS1],np.arange(529,559.01,1.0)]:
        pts=[(YR,Zr(x))] if x>XS1 else []
        for z in sorted(FW):
            if x>=Xr(z)-0.05: continue
            pts.append((Yf(z,x),z))
        if x==XS1:
            P=section(XS1,kind='pchip'); P=P[P[:,1]>=26]; NEW[float(x)]=P; continue
        if len(pts)<4: continue
        P=np.array(sorted(pts,key=lambda p:p[1]))
        w=np.ones(len(P)); w[0]=30
        sz=UnivariateSpline(P[:,1],P[:,0],w=w,s=len(P)*SSEC,k=3); zz=np.linspace(P[0,1],P[-1,1],120)
        NEW[float(x)]=np.c_[sz(zz),zz]
    if it<NIT-1:
        SEC={k:v for k,v in NEW.items() if k>XS1}
        WLUSE=False
json.dump({str(k):v.tolist() for k,v in NEW.items()},open(O+'/bow_sections_faired.json','w'))
xs=np.array(sorted(NEW)); worst=[]
for z in np.arange(30,88.1,2):
    r=np.array([(x,np.interp(z,NEW[x][:,1],NEW[x][:,0])) for x in xs if NEW[x][0,1]<=z<=NEW[x][-1,1]])
    if len(r)<4: continue
    s1=np.diff(r[:,1])/np.diff(r[:,0]); worst.append(np.abs(np.diff(s1)).max())
print('DEG',DEG,'max slope change along waterlines: %.2f'%max(worst))
w2=[]
for x in xs[1:]:
    s=NEW[x]; dz=np.diff(s[:,1]); s1=np.diff(s[:,0])/dz; w2.append(np.abs(np.diff(s1)).max())
print('max slope change along sections (per 0.7mm): %.3f'%max(w2))
for n in ['IV','V','VI','VII']:
    z=WLZ[n]; d=[np.interp(z,NEW[x][:,1],NEW[x][:,0])-Ywl(n,x) for x in xs if x>XS1 and NEW[x][0,1]<=z<=NEW[x][-1,1] and Ywl(n,x) is not None]
    print(n,'faired - A1/4 traced: max %.2f mean %+.2f'%(np.max(np.abs(d)),np.mean(d)))
