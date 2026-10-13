import json,numpy as np
from matplotlib.path import Path
O='/tmp/claude-0/-home-user-o-yaku-courses/63728b8f-e365-510d-8e4b-6775a7fec844/scratchpad/out'
R=0.5; X=np.arange(-60,615,R)+R/2; Y=np.arange(-82,82,R)+R/2; Z=np.arange(-12,165,R)+R/2
cnt=np.zeros((len(X),len(Y),len(Z)),np.uint8); owner=np.full(cnt.shape,-1,np.int32)
items=[]
for p in json.load(open(O+'/frame_pieces_v6.json'))['pieces']:
    items.append(dict(name=f"F{p['frame']:02d}{p['layer']}-{p['piece']}-{p['side']}",plane='YZ',off=p['x0'],th=p['x1']-p['x0'],poly=p['poly'],holes=[]))
for p in json.load(open(O+'/parts_v6.json')):
    p.setdefault('holes',[]); items.append(p)
def mask2d(poly,holes,U,V):
    uu,vv=np.meshgrid(U,V,indexing='ij'); pts=np.c_[uu.ravel(),vv.ravel()]
    m=Path(np.array(poly)).contains_points(pts)
    for h in holes: m&=~Path(np.array(h)).contains_points(pts)
    return m.reshape(uu.shape)
coll={}
for k,it in enumerate(items):
    P=np.array(it['poly'])
    if it['plane']=='YZ':
        iu=np.where((Y>=P[:,0].min())&(Y<=P[:,0].max()))[0]; iv=np.where((Z>=P[:,1].min())&(Z<=P[:,1].max()))[0]
        m=mask2d(P,it['holes'],Y[iu],Z[iv]); ia=np.where((X>=it['off'])&(X<it['off']+it['th']))[0]
        for i in ia:
            sl=(i,slice(iu[0],iu[-1]+1),slice(iv[0],iv[-1]+1)); prev=owner[sl][m]
            for o in np.unique(prev[prev>=0]): coll[(o,k)]=coll.get((o,k),0)+int((prev==o).sum())
            cnt[sl][m]+=1; o2=owner[sl]; o2[m]=k; owner[sl]=o2
    elif it['plane']=='XZ':
        iu=np.where((X>=P[:,0].min())&(X<=P[:,0].max()))[0]; iv=np.where((Z>=P[:,1].min())&(Z<=P[:,1].max()))[0]
        m=mask2d(P,it['holes'],X[iu],Z[iv]); y0=it['off']-it['th']/2
        for j in np.where((Y>=y0)&(Y<y0+it['th']))[0]:
            sl=(slice(iu[0],iu[-1]+1),j,slice(iv[0],iv[-1]+1)); prev=owner[sl][m]
            for o in np.unique(prev[prev>=0]): coll[(o,k)]=coll.get((o,k),0)+int((prev==o).sum())
            o2=owner[sl]; o2[m]=k; owner[sl]=o2
    else:  # XY, thickness in Z from off
        iu=np.where((X>=P[:,0].min())&(X<=P[:,0].max()))[0]; iv=np.where((Y>=P[:,1].min())&(Y<=P[:,1].max()))[0]
        m=mask2d(P,it['holes'],X[iu],Y[iv])
        for l in np.where((Z>=it['off'])&(Z<it['off']+it['th']))[0]:
            sl=(slice(iu[0],iu[-1]+1),slice(iv[0],iv[-1]+1),l); prev=owner[sl][m]
            for o in np.unique(prev[prev>=0]): coll[(o,k)]=coll.get((o,k),0)+int((prev==o).sum())
            o2=owner[sl]; o2[m]=k; owner[sl]=o2
res=sorted(((v*R**3,items[a]['name'],items[b]['name']) for (a,b),v in coll.items()),reverse=True)
print('items',len(items),'colliding pairs',len(res))
for v,a,b in res[:40]: print('  %7.2f mm3  %s  x  %s'%(v,a,b))
json.dump([(v,a,b) for v,a,b in res],open(O+'/collisions_v6.json','w'))
