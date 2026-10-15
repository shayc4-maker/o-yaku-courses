import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from bowsurf import *
from shapely.geometry import Polygon, box, LineString
from shapely.ops import unary_union
N={float(k):np.array(v) for k,v in json.load(open(O+'/bow_sections_faired.json')).items()}
NX=np.array(sorted(N))
SID=4.0; GAP=0.05; ZREF=60.0; XF45=528.03+0.05; BW=2.75; XBH=546.0; ZHEAD=88.0; ZTOPC=119.6
def T(z): return float(np.interp(z,[0,120],[4.8,3.3]))
Y88_st1=yat(S1,ZHEAD)
def Yo(x,z):
    """outer moulded half-breadth at (x,z); None outside the hull"""
    if z>ZHEAD:
        if x>XBH or z>ZTOPC: return None
        y=Yo(x,ZHEAD-1e-6)
        if y is None: return None
        ys=yat(S1,z)
        return y+((ys-Y88_st1) if ys is not None else 0.0)
    if x<XS1:
        return yat(section(x,kind='pchip'),z)
    i=np.searchsorted(NX,x)
    if i>=len(NX): return None
    vals=[]
    for xx in (NX[max(i-1,0)],NX[i]):
        s=N[xx]
        if not (s[0,1]<=z<=s[-1,1]): return None if xx==NX[i] and x>NX[i]-1e-9 else None
        vals.append(float(np.interp(z,s[:,1],s[:,0])))
    x0,x1=NX[max(i-1,0)],NX[i]
    return vals[0] if x1==x0 else vals[0]+(vals[1]-vals[0])*(x-x0)/(x1-x0)
# ---- precomputed grid for speed ----
GX=np.arange(510,561,0.25); GZ=np.arange(0,ZTOPC+0.01,0.5)
YS1=np.array([yat(S1,z) if yat(S1,z) is not None else np.nan for z in GZ])
GY=np.full((len(GX),len(GZ)),np.nan)
for i,x in enumerate(GX):
    if x<XS1:
        Px=section(x,kind='pchip')
        for j,z in enumerate(GZ):
            if z<=ZHEAD:
                v=yat(Px,z); GY[i,j]=np.nan if v is None else v
    else:
        xx=NX[np.searchsorted(NX,x)] if x<=NX[-1] else None
        for j,z in enumerate(GZ):
            if z<=ZHEAD:
                v=Yo(x,z); GY[i,j]=np.nan if v is None else v
j88=int(round(ZHEAD/0.5))
for i,x in enumerate(GX):
    if x>XBH: continue
    for j in range(j88+1,len(GZ)):
        GY[i,j]=GY[i,j88]+(YS1[j]-YS1[j88]) if not np.isnan(GY[i,j88]) else np.nan
def Yv(x,z):
    fi=(np.asarray(x)-GX[0])/0.25; fj=(np.asarray(z)-GZ[0])/0.5
    i0=np.floor(fi).astype(int); j0=np.floor(fj).astype(int)
    ok=(i0>=0)&(i0<len(GX)-1)&(j0>=0)&(j0<len(GZ)-1)
    i0=np.clip(i0,0,len(GX)-2); j0=np.clip(j0,0,len(GZ)-2); a=fi-i0; b=fj-j0
    v=(GY[i0,j0]*(1-a)*(1-b)+GY[i0+1,j0]*a*(1-b)+GY[i0,j0+1]*(1-a)*b+GY[i0+1,j0+1]*a*b)
    return np.where(ok,v,np.nan)
def Yo(x,z):
    v=float(Yv(x,z)); return None if np.isnan(v) else v
# ---- reference inner curve at ZREF and its tangents ----
xs=np.arange(XS1,Xr(ZREF)-0.05,0.05)
yo=np.array([Yo(x,ZREF) for x in xs]); m=np.array([v is not None for v in yo]); xs=xs[m]; yo=np.array([v for v in yo if v is not None],float)
P=np.c_[xs,yo]; t=np.gradient(P,axis=0); t/=np.linalg.norm(t,axis=1)[:,None]
nin=np.c_[t[:,1],-t[:,0]]            # inward normal (starboard): rotate tangent -90
Pin=P+nin*T(ZREF)
def tangent_at(q):
    i=np.argmin(np.hypot(*(Pin-q).T)); return t[i]
# ---- march: classic cant layout. Heads touch along the OUTER surface at ZREF; heels step forward along the deadwood/apron ----
DH=float(sys.argv[2]) if len(sys.argv)>2 else 2.6
cants=[]
i0=np.argmax(P[:,0]>=XF45); Q=P[i0].copy(); k=0
xend=Xr(ZREF)-0.8
PAR=len(sys.argv)>3 and sys.argv[3]=='par'
while True:
    if PAR:
        th=np.radians(-DH); n=np.array([np.cos(th),np.sin(th)]); d=np.array([n[1],-n[0]]); H=Q+d*40
    else:
        H=np.array([XF45+k*DH,BW])
        d=(H-Q)/np.linalg.norm(H-Q); n=np.array([-d[1],d[0]])
        if n[0]<0: n=-n
    cants.append(dict(Q=Q.copy(),n=n.copy(),d=d.copy(),H=H.copy()))
    g=(P-Q)@n-(SID+GAP); j=np.where(g>=0)[0]
    if len(j)==0 or P[j[0],0]>xend: break
    Q=P[j[0]].copy(); k+=1
print('cant timbers per side:',len(cants))
# ---- build each timber in its own plane coordinates (u along d from Q, z) ----
ZS=np.arange(0,ZTOPC+0.01,0.5)
def face_band(A,d,z):
    """along line A+u d (horizontal, at height z): return (u_out,u_in) where line crosses outer surface and inner offset"""
    us=np.arange(-40,60,0.05); pts=A[None,:]+us[:,None]*d[None,:]
    yo=Yv(pts[:,0],np.full(len(us),z))
    inside=(~np.isnan(yo))&(pts[:,1]>=0)&(pts[:,1]<=np.nan_to_num(yo,nan=-1))
    if not inside.any(): return None
    # outermost crossing: first inside sample walking from outboard(-u) to inboard(+u)
    io=np.argmax(inside); uo=us[io]; x0,y0=pts[io]
    if z>ZHEAD and x0>XBH-0.4: return None      # entering through the head bulkhead, not the side
    sl=(Yv(x0+0.25,z)-Yv(x0-0.25,z))/0.5
    if np.isnan(sl): sl=0.0
    inw=np.array([sl,-1.0])/np.hypot(sl,1.0)
    c=max(abs(d@inw),0.35)
    return uo, uo+T(z)/c
pieces=[]
for ci,c in enumerate(cants):
    Q,n,d=c['Q'],c['n'],c['d']
    polys=[]
    for face in (0.0,SID):
        A=Q+n*face
        L=[];R=[]
        for z in ZS:
            b=face_band(A,d,z)
            if b is None: continue
            L.append((b[0],z)); R.append((b[1],z))
        if len(L)<3: continue
        # split into contiguous runs in z
        poly=Polygon(L+R[::-1]).buffer(0)
        polys.append(poly)
    if not polys: continue
    G=unary_union(polys).buffer(0)
    # linear clip constraints on u for both faces (frame 45, backbone, previous timber, head bulkhead)
    def ubounds(A):
        lo,hi=-1e9,1e9
        def lin(a,b):   # a + b*u >= 0
            nonlocal lo,hi
            if abs(b)<1e-9: 
                if a<0: lo,hi=1,0
                return
            r=-a/b
            if b>0: lo=max(lo,r)
            else: hi=min(hi,r)
        lin(A[0]-XF45,d[0])                     # X >= frame 45 fore face
        lin(A[1]-BW,d[1])                       # Y >= backbone half-siding
        if ci>0:
            p=cants[ci-1]; lin((A-p['Q'])@p['n']-SID+0.02,d@p['n'])
        return lo,hi
    lo0,hi0=ubounds(Q); lo1,hi1=ubounds(Q+n*SID)
    lo,hi=max(lo0,lo1),min(hi0,hi1)
    if hi<=lo: continue
    G=G.intersection(box(lo,-50,hi,500))
    # head bulkhead above ZHEAD: keep X<=XBH on both faces
    for A in (Q,Q+n*SID):
        if abs(d[0])>1e-6:
            ub=(XBH-A[0])/d[0]
            cut=box(-1e3,ZHEAD,ub,1e3) if d[0]>0 else box(ub,ZHEAD,1e3,1e3)
            G=G.difference(box(-1e3,ZHEAD,1e3,1e3).difference(cut)) if False else G
    if G.is_empty: continue
    if G.geom_type!='Polygon': G=max(G.geoms,key=lambda g:g.area)
    ang=np.degrees(np.arctan2(n[1],n[0]))
    nm='hawse' if Q[0]>545 else 'cant'
    pieces.append(dict(id=ci+1,piece=nm,Q=Q.tolist(),n=n.tolist(),d=d.tolist(),th=SID,angle=float(ang),poly=np.array(G.exterior.coords).tolist(),area=G.area))
    print('C%02d %s  Q=(%.2f,%.2f)  cant angle %.1f deg  area %.0f  u[%.1f,%.1f] z[%.1f,%.1f]'%(ci+1,nm,Q[0],Q[1],ang,G.area,*G.bounds[0::2],*G.bounds[1::2]))
json.dump(pieces,open(O+'/cant_pieces.json','w'))
