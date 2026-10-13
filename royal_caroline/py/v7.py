import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import section, O
from joints import P as JP
from shapely.geometry import Polygon, LineString, box, MultiPolygon
from shapely.ops import unary_union
meta=json.load(open(O+'/meta.json')); K=meta['K']
fp=json.load(open(O+'/frame_pieces.json'))['pieces']; parts=json.load(open(O+'/parts_v4.json'))
pr=json.load(open(O+'/profile1a.json')); BW=2.65; SID=4.0
def polys(g):
    if g.is_empty: return []
    return [g] if g.geom_type=='Polygon' else [q for q in g.geoms if q.geom_type=='Polygon']
# ================= 1. CANT FRAMES / HAWSE PIECES =================
pv=json.load(open(sys.argv[2]+'/trpv.json'))
PV=np.array([4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28])
PR=np.array([4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40])
f=np.polyfit(PV,PR,1); LO=(-0.00716,1271.3)
c=np.array(pv['VII']); X7=(np.polyval(f,c[:,0])-PR[0])*K; Y7=(np.polyval(LO,c[:,0])-c[:,1])*K
m=X7>520; o=np.argsort(X7[m]); X7,Y7=X7[m][o],Y7[m][o]
XA=527.85; Y7a=float(np.interp(XA,X7,Y7)); XE7=float(X7[-1])
def g(t): return np.interp(XA+t*(XE7-XA),X7,Y7)/Y7a      # normalised waterline shape
ra=np.array(pr['stem_rabbet_aft']); ra=ra[np.argsort(ra[:,1])]
L5=np.array(json.load(open(O+'/bowlines_raw.json'))[5]['pts']); L5=L5[np.argsort(L5[:,1])]

def Xr(z):
    if z<=ra[-1,1]: return float(np.interp(z,ra[:,1],ra[:,0]))
    return float(np.interp(z,L5[:,1],L5[:,0])+(ra[-1,0]-np.interp(ra[-1,1],L5[:,1],L5[:,0])))
S1=section(XA,kind='pchip')
def Y1(z):
    out=[S1[i,0]+(z-S1[i,1])/(S1[i+1,1]-S1[i,1])*(S1[i+1,0]-S1[i,0]) for i in range(len(S1)-1) if (S1[i,1]-z)*(S1[i+1,1]-z)<=0 and S1[i,1]!=S1[i+1,1]]
    return max(out) if out else np.nan
ZTOP=lambda x: 119.4+(x-524)*0.12
def bow_section(x):
    zs=np.linspace(0,ZTOP(x),260); pts=[]
    for z in zs:
        y1=Y1(min(z,S1[-1,1]-0.01)); xr=Xr(z)
        if np.isnan(y1) or xr<=XA: continue
        t=(x-XA)/(xr-XA)
        if t>=1: continue
        y=max(BW,(y1-BW)*g(min(t,1))+BW)
        pts.append((y,z))
    P=np.array(pts); i0=np.where(P[:,0]>BW+0.01)[0][0]; return P[max(i0-1,0):]
def band(P,zr):
    T=np.gradient(P,axis=0); T/=np.linalg.norm(T,axis=1)[:,None]; N=np.c_[T[:,1],-T[:,0]]
    if N[len(N)//2,0]<0: N=-N
    t=np.interp(P[:,1],[0,P[-1,1]],[JP['T_FLOOR'],JP['T_TOP']]); In=P-N*t[:,None]
    return Polygon(np.r_[P,In[::-1]]).buffer(0)
cant=[]; cx=[]
x=528.15; k=46
while True:
    pcs=[]
    for lay in 'AF':
        xa=x+(0 if lay=='A' else SID); xb=xa+SID
        try: Pa=bow_section(xa); Pb=bow_section(xb)
        except Exception: Pa=None
        if Pa is None or len(Pa)<10 or len(Pb)<10: continue
        B=unary_union([band(Pa,0),band(Pb,0)]).intersection(box(BW+0.05,-50,200,500))
        for side,sg in (('S',1),('P',-1)):
            for q in polys(B):
                if q.area<4: continue
                P=np.array(q.exterior.coords)*[sg,1]
                pcs.append(dict(frame=k,layer=lay,piece='hawse' if xa>545 else 'cant',side=side,x0=xa,x1=xb,poly=P.tolist(),area=q.area))
    if not pcs: break
    cant+=pcs; cx.append((k,x+SID)); k+=1; x+=2*SID+3.2
print('cant/hawse frames',[(a,round(b,1)) for a,b in cx],'pieces',len(cant))
# remove anything overlapping backbone (bow pieces are at |Y|<2.65 so already clear)
fp+=cant
# ================= 1b. TOP TIMBERS CONTINUE UP AS BULWARK STANCHIONS (as in the real ship) =================
# side-top line (underside of cap rail) from A1/1 top line; stepped into flat runs (<=0.6 mm) so the cap rail can sit on them
RAIL=np.array([(20,131.9),(40,129.6),(60,127.8),(80,126.1),(95,126.0),(100,130.9),(120,130.2),(160,129.2),(180,128.7),(200,128.1),(225,127.7),
               (235,127.5),(245,103.0),(260,102.9),(280,102.9),(320,102.9),(340,103.1),(360,103.4),(380,103.9),(400,104.4),(420,105.2),(432,105.6),
               (446,118.6),(460,118.6),(480,118.6),(500,118.6),(520,119.6),(560,121.0)])
CAPT=1.2
def runs_of(xs):
    out=[];cur=[xs[0]]
    for x in xs[1:]:
        z=lambda v: float(np.interp(v,RAIL[:,0],RAIL[:,1]))
        zs=[z(v) for v in cur+[x]]
        if max(zs)-min(zs)<=0.6 and x-cur[0]<70: cur.append(x)
        else: out.append(cur); cur=[x]
    out.append(cur); return out
FXall=sorted(set(round((p['x0']+p['x1'])/2,2) for p in fp if p['piece'] in ('top','cant','hawse')))
RUNS=runs_of(FXall)
ZTOP={}
for r in RUNS:
    zr=float(np.mean([np.interp(v,RAIL[:,0],RAIL[:,1]) for v in r]))
    for v in r: ZTOP[v]=zr
def extend(p):
    xm=round((p['x0']+p['x1'])/2,2); zt=ZTOP.get(xm)
    if zt is None: return
    P=np.array(p['poly']); sg=1 if P[:,0].mean()>0 else -1; A=np.c_[np.abs(P[:,0]),P[:,1]]
    zmax=A[:,1].max()
    if zt<=zmax+0.2:   # side top below/at current top: trim
        q=Polygon(A).buffer(0).intersection(box(-1,-50,300,zt))
    else:
        lv=np.linspace(zmax-8,zmax-0.3,12); pts=[]
        Q=Polygon(A).buffer(0)
        from shapely.geometry import LineString as LS
        for z in lv:
            seg=Q.intersection(LS([(0,z),(300,z)]))
            if seg.is_empty: continue
            b=seg.bounds; pts.append((z,b[2],b[0]))
        pts=np.array(pts); fo=np.polyfit(pts[:,0],pts[:,1],1); w=float(np.median(pts[:,1]-pts[:,2]))
        w=min(w,3.3)
        zb=zmax-6
        yo0=np.polyval(fo,zb); yo1=np.polyval(fo,zt)
        q=unary_union([Q,Polygon([(yo0,zb),(yo1,zt),(yo1-w,zt),(yo0-w,zb)])]).buffer(0)
        q=q.intersection(box(-1,-50,300,zt))
    if q.geom_type!='Polygon': q=max(q.geoms,key=lambda g:g.area)
    C=np.array(q.exterior.coords); p['poly']=np.c_[sg*C[:,0],C[:,1]].tolist(); p['ztop_rail']=zt
for p in fp:
    if p['piece'] in ('top','cant','hawse'): extend(p)
json.dump(dict(runs=[[float(v) for v in r] for r in RUNS],ztop={str(k):v for k,v in ZTOP.items()}),open(O+'/rail_runs.json','w'))
# ================= 2. PORTS =================
PORTS=[(105.9,117.9,107.6,121.3),(147.7,160.0,106.8,120.6),(189.7,202.0,105.8,119.5),
       (284.2,295.0,86.0,95.5),(328.1,339.1,85.8,95.2),(373.3,384.4,86.3,96.1),(418.3,428.9,87.4,97.2)]
SL=2.0
def hb_at(xm,z):
    P=section(xm,kind='pchip')
    out=[P[i,0]+(z-P[i,1])/(P[i+1,1]-P[i,1])*(P[i+1,0]-P[i,0]) for i in range(len(P)-1) if (P[i,1]-z)*(P[i+1,1]-z)<=0 and P[i,1]!=P[i+1,1]]
    return max(out)
newfp=[]; port_frames=set()
for p in fp:
    q=Polygon(p['poly']).buffer(0)
    for (a,b,z0,z1) in PORTS:
        if p['x1']>a and p['x0']<b:
            q=q.difference(box(-200,z0-SL,200,z1+SL)); port_frames.add((p['frame'],p['layer']))
    for j,qq in enumerate(sorted(polys(q),key=lambda r:r.bounds[1])):
        if qq.area<1: continue
        d=dict(p); d['poly']=np.array(qq.exterior.coords).tolist(); d['area']=qq.area
        if j>0: d['piece']=p['piece']+'U'
        newfp.append(d)
fp=newfp
add=[]
for n,(a,b,z0,z1) in enumerate(PORTS,1):
    for nm,za,zb in (('SILL',z0-SL,z0),('LINTEL',z1,z1+SL)):
        tops=[max(np.array(p['poly'])[:,1]) for p in fp if p['piece'].startswith('top') and abs((p['x0']+p['x1'])/2-(a+b)/2)<30 and not (p['x1']>a and p['x0']<b)]
        if za>min(tops)-0.5: continue      # opening reaches the rail: no lintel
        zm=(za+zb)/2
        from shapely.geometry import LineString as LS
        ys=[]
        for p in fp:
            xm=(p['x0']+p['x1'])/2
            if abs(xm-(a+b)/2)>25 or (p['x1']>a and p['x0']<b) or np.array(p['poly'])[:,0].mean()<0: continue
            sg=Polygon(p['poly']).buffer(0).intersection(LS([(0,zm),(300,zm)]))
            if not sg.is_empty: ys.append((sg.bounds[2],sg.bounds[2]-sg.bounds[0]))
        y=float(np.mean([v[0] for v in ys])); t=float(min(v[1] for v in ys))
        for sg,sd in ((1,'S'),(-1,'P')):
            add.append(dict(name=f'PORT{n}_{nm}_{sd}',plane='XZ',off=sg*(y-t/2-0.15),th=t-0.3,group='ports',note=f'port {n}: X {a:.1f}-{b:.1f}, opening Z {z0:.1f}-{z1:.1f} (A1/1)',poly=box(a,za,b,zb).exterior.coords[:]))
# ================= 4. BUILDING JIG (upside-down, Hahn style) =================
ZB=136.0; TB=6.0; TW=3.0; tabs=[]
for p in fp:
    if not p['piece'].startswith('top') and p['piece'] not in ('cant','hawse'): continue
    if (p['frame'],p['layer']) in port_frames: continue
    P=np.array(p['poly']); zt=P[:,1].max(); topedge=P[P[:,1]>zt-0.6]; yc=topedge[:,0].mean()
    tab=box(yc-TW/2,zt-1.0,yc+TW/2,ZB+TB)
    q=unary_union([Polygon(P).buffer(0),tab]); p['poly']=np.array(q.exterior.coords).tolist(); p['tab']=dict(y=yc,z_cut=zt)
    tabs.append((p['x0'],p['x1'],yc))
xs0=min(t[0] for t in tabs)-15; xs1=max(t[1] for t in tabs)+15
board=box(xs0,-80,xs1,80)
holes=[box(a-0.1,yc-TW/2-0.1,b+0.1,yc+TW/2+0.1) for a,b,yc in tabs]
board=board.difference(unary_union(holes))
add.append(dict(name='JIG_BASEBOARD',plane='XY',off=ZB,th=TB,group='jig',note='hull is built upside-down on this board; frame tabs drop into the slots; cut tabs off at the engraved line after planking/clamps',
    poly=np.array(board.exterior.coords).tolist(),holes=[np.array(h.coords).tolist() for h in board.interiors]))
# keel-line spacers: longitudinal XZ fences between board and keel? (keel sits up, free). Add two stiffeners under board
for y in (-60,60):
    add.append(dict(name=f'JIG_STIFFENER_{"P" if y<0 else "S"}',plane='XZ',off=y,th=6.0,group='jig',note='glue under the board (board side up)',poly=box(xs0,ZB+TB,xs1,ZB+TB+20).exterior.coords[:]))
print('ports cut on',len(port_frames),'timbers; tabs',len(tabs),'; added',len(add),'parts')
for d in add: d['poly']=[list(map(float,v)) for v in d['poly']]
json.dump(dict(pieces=fp),open(O+'/frame_pieces_v7.json','w')); json.dump(parts+add,open(O+'/parts_v7.json','w'))
