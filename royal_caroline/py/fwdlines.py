# fair the user's scanned bow lines into clean edges (model mm)
import numpy as np, json
from scipy.interpolate import splprep, splev
from scipy.ndimage import gaussian_filter1d
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import nearest_points
L=[np.array(l) for l in json.load(open('scan/raw_lines.json'))]
V=Polygon(json.load(open('out/backbone_contour_v5.json'))['outer'])
ZFK=-7.5; ZKT=-0.2; XB=452.0
J=dict(J0=(479.65,3.45),J3=(500.85,4.2),J9=(504.5,ZFK),J2=(531.5,22.7),J1=(547.3,40.2),J7=(553.95,49.8),
       J4=(560.3,64.4),J5=(563.6,78.7),J6=(583.7,84.05),J8=(569.6,63.7),J10=(540.6,24.4),J11=(584.85,68.15),
       L1=(573.0,80.7),L2=(580.6,83.15),C42=(480.5,-0.7))
def chain(ids):
    pts=None
    for i in ids:
        a=L[abs(i)]
        if pts is None:
            nxt=L[abs(ids[1])] if len(ids)>1 else a
            e=np.r_[nxt[0:1],nxt[-1:]]
            a=a if min(np.hypot(*(e-a[-1]).T))<=min(np.hypot(*(e-a[0]).T)) else a[::-1]; pts=list(a)
        else:
            a=a if np.hypot(*(a[0]-pts[-1]))<=np.hypot(*(a[-1]-pts[-1])) else a[::-1]; pts+=list(a)
    return np.array(pts)
def orient(p,a):  # make p start nearest a
    return p if np.hypot(*(p[0]-a))<=np.hypot(*(p[-1]-a)) else p[::-1]
def onc(p):  # project onto contour
    q=nearest_points(V.exterior,Point(p))[0]; return (q.x,q.y)
def fair(pts,a,b,straight_tol=0.3,s=0.02):
    pts=orient(np.asarray(pts,float),a)
    pts=np.r_[[a],pts[1:-1],[b]]
    ch=np.array(b)-np.array(a); n=np.array([-ch[1],ch[0]])/np.hypot(*ch)
    dev=np.abs((pts-np.array(a))@n).max()
    if dev<straight_tol: return np.array([a,b]),'line'
    # resample by arclength, spline with pinned ends
    seg=np.hypot(*np.diff(pts,axis=0).T); u=np.r_[0,np.cumsum(seg)]; keep=np.r_[True,seg>1e-6]; pts=pts[keep]; u=u[keep]
    w=np.ones(len(pts)); w[0]=w[-1]=100
    t,_=splprep(pts.T,u=u/u[-1],w=w,s=len(pts)*s,k=3)
    q=np.array(splev(np.linspace(0,1,max(20,int(u[-1]/0.4))),t)).T; q[0]=a; q[-1]=b
    return q,'curve'
E={}
def add(name,pts,a,b,**k): E[name]=fair(pts,a,b,**k)
c=lambda n:J[n]
# keel top: flat -0.2 to XB then user's rise to J0
p39=orient(L[39],(436,0)); p39=p39[p39[:,0]>XB+1]
q,_=fair(np.r_[[(XB,ZKT)],p39,[J['J0']]],(XB,ZKT),J['J0'],s=0.03); E['keeltop_rise']=(q,'curve')
E['keeltop_flat']=(np.array([(400,ZKT),(XB,ZKT)]),'line')
E['hog_top']=(np.array([(400,0.8),(XB,0.8)]),'line'); E['hog_butt']=(np.array([(XB,ZKT),(XB,0.8)]),'line')
E['fk_top']=(np.array([(400,ZFK),J['J9']]),'line')
add('e42a',L[42][L[42][:,0]<480.7],c('J0'),c('C42'))
add('e42b',L[42][L[42][:,0]>481],c('C42'),c('J3'))
add('e58',L[58],c('J9'),c('J3'))
add('eA',chain([3,17,-35]),c('J0'),c('J1'))
add('eB',chain([-1,-15]),c('J3'),c('J2'))
add('e8',L[8],c('J2'),c('J1'))
add('e23',L[23],c('J2'),c('J10'))
add('e41',L[41],c('J1'),c('J7')); add('e29',L[29],c('J7'),c('J4')); add('e12',L[12],c('J4'),c('J5'))
add('e14',L[14],c('J5'),onc(L[14][-1]))
add('e13',L[13],c('J5'),c('L1')); add('lensA',L[55],c('L1'),c('L2')); add('lensB',L[56],c('L1'),c('L2')); add('e10',L[10],c('L2'),c('J6'))
add('e40',L[40],c('J6'),c('J4')); add('e47',L[47],c('J6'),onc(L[47][-1]))
add('e52',L[52],c('J7'),c('J8'))
add('eC',chain([32,44,22,16]),c('J8'),onc(L[16][-1]))
add('e25',L[25],c('J8'),c('J11')); add('e46',L[46],c('J11'),onc(L[46][-1]))
add('e24',chain([-24,28]),onc(L[24][-1]),onc(L[28][-1]))
# outer strip: 0.7 mm inside contour, from the false-keel top line to J11
from shapely import segmentize
from shapely.ops import substring
U=np.vstack([L[i] for i in (36,27,9,30,11,20,4,6,50,31,5,51,53,48,38)])
ring=V.buffer(-0.7,join_style=1).exterior
ring=LineString(segmentize(ring,0.2).coords)
hz=LineString([(J['J9'][0],ZFK),(560,ZFK)]); ip=ring.intersection(hz)
ip=min(getattr(ip,'geoms',[ip]),key=lambda g:g.x); xi=ip.x
a=ring.project(ip); b=ring.project(Point(J['J11']))
cands=[substring(ring,min(a,b),max(a,b))]
# the other way round the ring
L1_=substring(ring,max(a,b),ring.length); L2_=substring(ring,0,min(a,b)); cands.append(LineString(list(L1_.coords)+list(L2_.coords)))
from scipy.spatial import cKDTree
tr=cKDTree(U)
best=min(cands,key=lambda g:np.mean(tr.query(np.array(segmentize(g,1.0).coords))[0]))
run=np.array(best.coords); run=orient(run,(xi,ZFK))
run=run[np.hypot(run[:,0]-J['J11'][0],run[:,1]-J['J11'][1])>0.5]
print('strip run',len(run),round(xi,2),'mean dist to user %.2f'%np.mean(tr.query(run)[0]))
strip=np.r_[[J['J9']],[(xi,ZFK)],run[1:],[J['J11']]]
# fillet around the horizontal->offset corner
seg=np.hypot(*np.diff(strip,axis=0).T); u=np.r_[0,np.cumsum(seg)]; uu=np.arange(0,u[-1],0.1)
R=np.c_[np.interp(uu,u,strip[:,0]),np.interp(uu,u,strip[:,1])]
Sm=np.c_[gaussian_filter1d(R[:,0],10,mode='nearest'),gaussian_filter1d(R[:,1],10,mode='nearest')]
wgt=np.clip(1-np.abs(uu-u[1])/3.0,0,1)[:,None]; R=R*(1-wgt)+Sm*wgt; R[0]=J['J9']; R[-1]=J['J11']
E['strip']=(LineString(R).simplify(0.02).coords,'curve')
out={k:np.array(v[0]).tolist() for k,v in E.items()}
json.dump(out,open('scan/fwd_edges.json','w'))
for k,(p,t) in E.items(): print(k,t,len(p))
# ---- straighten near-straight joints ----
for k in ('e29','e40','e52','eC'):
    p=np.array(E[k][0]); E[k]=(np.array([p[0],p[-1]]),'line')
# ---- parallel pairs: blend middle to constant offset of the reference ----
from shapely.ops import linemerge
def para(key,ref,dist,t0=0.12,t1=0.88):
    a=LineString(E[key][0]); R=ref
    pts=[];  n=max(40,int(a.length/0.3))
    for t in np.linspace(0,1,n):
        q=a.interpolate(t,normalized=True); r=R.interpolate(R.project(q)); v=np.array([q.x-r.x,q.y-r.y]); dn=np.hypot(*v)
        tgt=np.array([r.x,r.y])+v/dn*dist if dn>1e-6 else np.array([q.x,q.y])
        w=np.clip(min((t-0)/t0,(1-t)/(1-t1)),0,1); w=w*w*(3-2*w)
        pts.append(np.array([q.x,q.y])*(1-w)+tgt*w)
    pts=np.array(pts); pts[0]=E[key][0][0]; pts[-1]=E[key][0][-1]
    from scipy.ndimage import gaussian_filter1d as g
    sm=np.c_[g(pts[:,0],2,mode='nearest'),g(pts[:,1],2,mode='nearest')]; sm[0]=pts[0]; sm[-1]=pts[-1]
    E[key]=(sm,'curve')
para('e8',LineString(E['strip'][0]),5.0,0.2,0.8)
ref=linemerge([LineString(E[k][0]) for k in ('e42b','eB','e8')])
para('eA',ref,5.1,0.12,0.86)
out={k:np.array(v[0]).tolist() for k,v in E.items()}
json.dump(out,open('scan/fwd_edges.json','w'))
print('done')
