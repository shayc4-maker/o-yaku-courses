import json, numpy as np, networkx as nx, sys
sys.path.insert(0,'py')
from scipy.interpolate import splprep, splev, UnivariateSpline
D={d['id']:d for d in json.load(open('scan2/dots_merged.json'))}
seats=json.load(open('out/backbone_contour_v5.json'))['seats']
blocks=[(a,b) for a,b,z,r in seats]
SEAT={291,294,295,293,297,300,301,299,303,305,306,304}
BE=np.array([x for ab in blocks for x in ab])
def XY(i):
    x,z=D[i]['X'],D[i]['Z']
    if i in SEAT: x=float(BE[np.argmin(abs(BE-x))])
    return (x,z)
NOTCH=set([269,270,272,273,274,276,277,278,279,283,285,286,287,288,289]+list(range(184,199))+[180,182,183,179,176,177,173,174,170,171,169,168,166,167,164,163,162,159,158,157,156,155,154,152,151]+list(range(225,243))+list(range(200,219))+[220,221,223,224]+list(range(108,124))+list(range(125,128))+list(range(130,132))+list(range(133,142))+[143,144,147,148,149,150]+list(range(57,65))+list(range(67,93))+[43,44,45,47,128])
NOTCH-= {181,172,165,153,69}
NOTCH={i for i in NOTCH if D[i]['c']=='G'}   # blue keelson-top dots
auto=[tuple(e) for e in json.load(open('scan2/bow_edges.json'))]
E=[]
D['V1']=dict(id='V1',X=553.95,Z=49.8,c='G')
def ch(*ids): return [(a,b) for a,b in zip(ids[:-1],ids[1:])]
M=[(245,244),(244,247)]
# bow (manual, plan topology)
M+=ch(15,14,13,9,7)+[(20,19),(19,16),(16,15),(15,25),(26,12),(26,24)]
M+=ch(24,29,36,49)+ch(49,53,95,54,100,101,102)+[(102,104),(48,49),(50,51),(48,51),(38,39),(40,41),(41,38)]
M+=ch(93,83,52,51)+ch(50,46,39)+ch(94,87,65,40)+ch(33,37,43)
M+=ch(94,96,98,106)+[(94,99)]+ch(99,97,93)+[(93,103),(103,102),(103,107)]
# stem
M+=ch(0,1,2)+ch(2,10,21,30,31,33)
# stern: transoms / post
M+=[(247,248)]+ch(247,246,250,251,254,253,256,257,259,260,261,262)+[(262,282)]
M+=ch(248,249,255,264,266,271)+ch(251,252,258,265,267,269)+[(271,275),(269,270),(270,275)]
M+=[(262,263)]+ch(263,268,281,290,291)
M+=ch(291,294,295,293,297,300,301,299,303,305,306,304,307)
M+=[(282,280),(282,296),(280,292),(292,296),(292,298),(298,302),(302,308),(308,311),(311,314),(296,309)]
M+=ch(312,310,313,309,311)+ch(310,315,316,313)+[(312,317)]
M+=ch(314,160,145,106)+[(160,161),(145,146),(106,107)]
M+=ch(317,175,161,219,146,129,107)+[(178,175),(222,219),(132,129)]
# keelson top
M+=ch(275,284,195,189,181,172,165,153,243)+[(243,199),(199,142)]+ch(142,124,105,76,66,56,55,42,43)
E=list(set(tuple(sorted(e,key=str)) for e in E+M))
# ---- chains ----
G=nx.Graph(); G.add_edges_from(E)
green=lambda i:D[i]['c']=='G'
brk=lambda n:green(n) or G.degree(n)!=2
used=set(); chains=[]
for a,b in G.edges():
    if (a,b) in used or (b,a) in used: continue
    # walk both ways to breakpoints
    path=[a,b]; used.add((a,b))
    while not brk(path[-1]):
        nx_=[w for w in G[path[-1]] if w!=path[-2]][0]; used.add((path[-1],nx_)); path.append(nx_)
    while not brk(path[0]):
        nx_=[w for w in G[path[0]] if w!=path[1]][0]; used.add((nx_,path[0])); path.insert(0,nx_)
    chains.append(path)
out=[]
for c in chains:
    P=np.array([XY(i) for i in c])
    if len(c)==2: out.append(dict(ids=c,kind='line',pts=P.tolist()))
    else:
        k=min(3,len(c)-1); t,u=splprep(P.T,s=0,k=k)
        out.append(dict(ids=c,kind='spline',pts=np.array(splev(np.linspace(0,1,max(30,len(c)*15)),t)).T.tolist()))
FORCED=[[1,4,5,11,22,32,40],[0,3,18,20,25,28,34,38]]
from shapely.geometry import LineString as LS, Point as PT
for c in FORCED:
    P=np.array([XY(i) for i in c]); t,_=splprep(P.T,s=0,k=3); Q=np.array(splev(np.linspace(0,1,200),t)).T
    out.append(dict(ids=c,kind='spline',pts=Q.tolist()))
    if 38 in c:
        g=LS(Q); q=g.interpolate(g.project(PT(553.95,49.8)))
        out.append(dict(ids=['V1',26],kind='line',pts=[[q.x,q.y],list(XY(26))]))
# ---- keelson underside, aligned to frames ----
pts=[XY(i) for i in NOTCH if i not in (269,270)]
edge=[]   # per block edge: (x, zup, zlo)
for k,(a,b) in enumerate(blocks):
    for x in (a,b):
        near=[p for p in pts if abs(p[0]-x)<1.6]
        if not near: edge.append([x,None,None]); continue
        zs=sorted(p[1] for p in near)
        edge.append([x,zs[-1],zs[0] if len(zs)>1 and zs[-1]-zs[0]>0.3 else None])
E2=np.array([[e[0],e[1] if e[1] is not None else np.nan,e[2] if e[2] is not None else np.nan] for e in edge],float)
dep=np.nanmedian(E2[:,1]-E2[:,2]); print('median notch depth %.2f'%dep)
# fill: missing lower = upper - local depth; missing upper = lower + depth
ok=~np.isnan(E2[:,1])&~np.isnan(E2[:,2]); dloc=np.interp(E2[:,0],E2[ok,0],(E2[ok,1]-E2[ok,2]))
m=np.isnan(E2[:,2])&~np.isnan(E2[:,1]); E2[m,2]=E2[m,1]-dloc[m]
m=np.isnan(E2[:,1])&~np.isnan(E2[:,2]); E2[m,1]=E2[m,2]+dloc[m]
m=np.isnan(E2[:,1]); 
if m.any(): E2[m,1]=np.interp(E2[m,0],E2[~m,0],E2[~m,1]); E2[m,2]=E2[m,1]-np.interp(E2[m,0],E2[ok,0],(E2[ok,1]-E2[ok,2]))
# smooth the two lines lightly (frames rule), keep blue between-frame dots in aft
ku=[]
for k,(a,b) in enumerate(blocks):
    za_u,za_l=E2[2*k,1],E2[2*k,2]; zb_u,zb_l=E2[2*k+1,1],E2[2*k+1,2]
    ku+=[(a,za_l),(a,za_u),(b,zb_u),(b,zb_l)]
    if k+1<len(blocks):
        a2=blocks[k+1][0]; z2=E2[2*k+2,2]
        mid=[XY(q) for q in (276,286) if b<XY(q)[0]<a2]
        if mid:
            P=np.array([(b,zb_l)]+mid+[(a2,z2)]); t,_=splprep(P.T,s=0,k=2)
            ku+=[tuple(p) for p in np.array(splev(np.linspace(0,1,12),t)).T[1:-1]]
ku=[(float(x),float(z)) for x,z in ku]
out.append(dict(ids=['keelson_underside'],kind='frames',pts=ku))
json.dump(out,open('scan2/lines_v1.json','w'))
conn=set(i for e in E for i in e)|NOTCH|set(i for c in FORCED for i in c)
print('chains',len(chains),'unconnected dots:',sorted(set(D)-conn,key=str))
