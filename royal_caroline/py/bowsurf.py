import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import section, O
from scipy.interpolate import PchipInterpolator
W=json.load(open(O+'/bow_wl_A14.json')); WLZ=json.load(open(O+'/meta.json'))['WLZ_mm']
pr=json.load(open(O+'/profile1a.json')); ra=np.array(pr['stem_rabbet_aft']); ra=ra[np.argsort(ra[:,1])]
L5=np.array(json.load(open(O+'/bowlines_raw.json'))[5]['pts']); L5=L5[np.argsort(L5[:,1])]
YR=3.5                               # half-breadth at the rabbet (A1/4 waterline endings)
XS1=527.85; ZTOPB=88.0               # top of hull planking at the head (A1/1)
def Xr(z):
    if z<=ra[-1,1]: return float(np.interp(z,ra[:,1],ra[:,0]))
    return float(np.interp(z,L5[:,1],L5[:,0])+(ra[-1,0]-np.interp(ra[-1,1],L5[:,1],L5[:,0])))
zr_tab=np.array([(Xr(z),z) for z in np.linspace(ra[0,1],ZTOPB,300)])
def Zr(x): return float(np.interp(x,zr_tab[:,0],zr_tab[:,1]))
wl={n:np.array(c) for n,c in W.items()}
for n in wl: wl[n]=wl[n][np.argsort(wl[n][:,0])]
def Ywl(n,x):
    c=wl[n]
    if x>c[-1,0]: return None
    return float(np.interp(x,c[:,0],c[:,1]))
S1=section(XS1,kind='pchip')
def yat(P,z):
    o=[P[i,0]+(z-P[i,1])/(P[i+1,1]-P[i,1])*(P[i+1,0]-P[i,0]) for i in range(len(P)-1) if (P[i,1]-z)*(P[i+1,1]-z)<=0 and P[i,1]!=P[i+1,1]]
    return max(o) if o else None
c7=wl['VII']; Y7s1=float(np.interp(XS1,c7[:,0],c7[:,1])); X7e=c7[-1,0]
def gVII(t): return (float(np.interp(XS1+t*(X7e-XS1),c7[:,0],c7[:,1]))-YR)/(Y7s1-YR)
UPPER=[72,76,80,84,88]
def section_bow(x):
    """outer moulded section at x (>= ~500): list of (Y,Z) from rabbet up to top"""
    zr=Zr(x); pts=[(YR,zr)]
    for n in ['I','II','III','IV','V','VI','VII']:
        z=WLZ[n]
        if z<=zr+0.05: continue
        y=Ywl(n,x)
        if y is not None: pts.append((y,z))
    for z in UPPER:
        if z<=zr+0.05: continue
        y1=yat(S1,z); xr=Xr(z)
        if y1 is None: continue
        t=(x-XS1)/(xr-XS1)
        if t>=1: continue
        if x<XS1:
            P=section(x,kind='pchip'); y=yat(P,z)
            if y is None: continue
        else: y=YR+(y1-YR)*gVII(max(t,0))
        pts.append((y,z))
    pts=np.array(sorted(pts,key=lambda p:p[1]))
    return pts
if __name__=='__main__':
    for x in (505.76,516,527.85):
        P=section_bow(x); B=section(x,kind='pchip')
        d=[(z,y,yat(B,z)) for y,z in P[1:] if yat(B,z) is not None]
        print('X %.2f'%x,' '.join('Z%.0f:%+.2f'%(z,y-yb) for z,y,yb in d))

# ---- correction so the bow meets station 1 (and frame 45) exactly, fading to zero at the rabbet ----
def kfac(z):
    yb=yat(S1,z)
    ya=None
    for n in ['I','II','III','IV','V','VI','VII']:
        pass
    return None
KTAB={}
for n in ['IV','V','VI','VII']:
    z=WLZ[n]; yb=yat(S1,z); ya=Ywl(n,XS1)
    KTAB[z]=(yb-YR)/(ya-YR)
def section_fit(x,nz=120):
    P=section_bow(x)
    if len(P)<3: return None
    Y=P[:,0].copy(); Z=P[:,1]
    if x>=XS1-1e-6:
        kz=np.array(sorted(KTAB.items())); 
        for i in range(len(Y)):
            if Z[i] in KTAB or any(abs(Z[i]-k)<1e-6 for k in KTAB):
                k=float(np.interp(Z[i],kz[:,0],kz[:,1])); Y[i]=YR+(Y[i]-YR)*k
    f=PchipInterpolator(Z,Y); zz=np.linspace(Z[0],Z[-1],nz)
    return np.c_[f(zz),zz]
