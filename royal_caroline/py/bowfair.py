import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from bowsurf import *
from scipy.interpolate import UnivariateSpline, PchipInterpolator
SEC={float(k):np.array(v) for k,v in json.load(open(O+'/bow_sections.json')).items()}
ZS=np.arange(0,ZTOPB+0.01,1.0)
XA=np.arange(470,518,2.0); WAFT=float(sys.argv[2]); SMO=float(sys.argv[3])
def raw_y(x,z):
    if x<518:
        P=section(x,kind='pchip'); return yat(P,z)
    xs=sorted(SEC); 
    # linear in x between stored sections
    i=np.searchsorted(xs,x)
    cands=[]
    for xx in xs:
        s=SEC[xx]
        if s[0,1]<=z<=s[-1,1]: cands.append((xx,float(np.interp(z,s[:,1],s[:,0]))))
    if not cands: return None
    c=np.array(cands)
    if x<c[0,0] or x>c[-1,0]: return None
    return float(np.interp(x,c[:,0],c[:,1]))
WLf={}
for z in ZS:
    xr=Xr(z) if z>=ra[0,1] else None
    pts=[]
    for x in XA:
        y=raw_y(x,z)
        if y is not None: pts.append((x,y,WAFT))
    for xx in sorted(SEC):
        if xr is not None and xx>=xr-0.2: continue
        y=raw_y(xx,z)
        if y is not None: pts.append((xx,y,WAFT if xx<=XS1+0.01 else 1.0))
    # A1/4 waterline itself where this z is a drawn waterline: stronger weight
    for n,zz in WLZ.items():
        if n!='BASE' and abs(zz-z)<0.5 and n in wl:
            c=wl[n]; c=c[c[:,0]>518]
            for x,y in c[::4]:
                pts=[p for p in pts if abs(p[0]-x)>0.3]; pts.append((x,y,3.0))
    if xr is not None and xr>500: pts.append((xr,YR,50.0))
    pts=np.array(sorted(pts))
    if len(pts)<6: continue
    _,u=np.unique(pts[:,0],return_index=True); pts=pts[u]
    sp=UnivariateSpline(pts[:,0],pts[:,1],w=pts[:,2],s=len(pts)*SMO,k=4)
    WLf[float(z)]=(sp,float(pts[-1,0]))
# rebuild sections from faired waterlines, then fair each section in Z
XS=np.r_[np.arange(518,527.85,2.0),[527.85],np.arange(529,559,1.0)]
NEW={}
for x in XS:
    zr=Zr(x) if x>500 else 0
    pts=[(YR,zr)] if x>495 else []
    for z,(sp,xe) in WLf.items():
        if z<=zr+0.2 or x>xe: continue
        pts.append((float(sp(x)),z))
    if len(pts)<5: continue
    P=np.array(sorted(pts,key=lambda p:p[1]))
    w=np.ones(len(P)); w[0]=50
    sz=UnivariateSpline(P[:,1],P[:,0],w=w,s=len(P)*0.05,k=4)
    zz=np.linspace(P[0,1],P[-1,1],120); NEW[float(x)]=np.c_[sz(zz),zz]
json.dump({str(k):v.tolist() for k,v in NEW.items()},open(O+'/bow_sections_faired.json','w'))
# checks
xs=np.array(sorted(NEW)); zs=np.arange(20,88.1,2); worst=0
for z in zs:
    row=[(x,np.interp(z,NEW[x][:,1],NEW[x][:,0])) for x in xs if NEW[x][0,1]<=z<=NEW[x][-1,1]]
    if len(row)<4: continue
    r=np.array(row); s1=np.diff(r[:,1])/np.diff(r[:,0]); s2=np.abs(np.diff(s1)); worst=max(worst,s2.max())
print('max slope change between neighbouring sections: %.2f (was up to 1.33)'%worst)
for n in ['IV','V','VI','VII']:
    z=WLZ[n]; d=[]
    for x in xs:
        s=NEW[x]
        if x<XS1 or not (s[0,1]<=z<=s[-1,1]): continue
        ya=Ywl(n,x)
        if ya is not None: d.append(np.interp(z,s[:,1],s[:,0])-ya)
    print(n,'faired - A1/4: max %.2f'%np.max(np.abs(d)))
for x in (518,524,527.85):
    P=section(x,kind='pchip'); s=NEW[float(x)]
    d=[np.interp(z,s[:,1],s[:,0])-yat(P,z) for z in np.arange(s[0,1]+1,s[-1,1]-1,3) if yat(P,z) is not None]
    print('X %.2f faired - body plan: max %.2f'%(x,np.max(np.abs(d))))
