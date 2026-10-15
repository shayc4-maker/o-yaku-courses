import sys,json,numpy as np,re
sys.path.insert(0,sys.argv[1]); from hull import O
from joints import Zb, P as JP
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
fp=json.load(open(O+'/frame_pieces_v8.json'))['pieces']; parts=json.load(open(O+'/parts_v8.json'))
def strip(p):
    q=Polygon(p['poly']).buffer(0)
    if 'tab' in p: q=q.intersection(box(-300,-100,300,p['tab']['z_cut']))
    return q
YZ=[(p['x0'],p['x1'],strip(p)) for p in fp if np.array(p['poly'])[:,0].mean()>0]
YZ+=[(p['off'],p['off']+p['th'],Polygon(p['poly']).buffer(0)) for p in parts if p['plane']=='YZ' and np.array(p['poly'])[:,0].mean()>0 and p['group'] in ('stern',)]
def yin(xa,xb,za,zb,reach=0.0):
    best=None
    for x0,x1,P in YZ:
        if x1<xa-reach or x0>xb+reach: continue
        q=P.intersection(box(3.0,za,200,zb))
        if q.is_empty: continue
        v=q.bounds[0]; best=v if best is None else min(best,v)
    return best
OPEN=[(109.5,142.5,16,55),(131.5,142,-56,-38.5),(242,274,46,64),(242,258,-64,-46),(278.6,312.3,-14.5,14.5),(387.4,439.3,-14.5,14.5),(12,32,-23.6,23.6)]
MAST=[(92.0,4.3),(261.5,5.5),(495.9,5.2),(349.4,4.5)]
beams={}
for p in parts:
    m=re.match(r'(.+)_BEAM_(\d+)(_\d)?$',p['name'])
    if not m or p['group']!='decks': continue
    P=np.array(p['poly']); key=(m.group(1),m.group(2))
    b=beams.setdefault(key,dict(deck=m.group(1),x=p['off']+p['th']/2,sided=p['th'],ymax=0,zbot=1e9,ztop_c=None,pieces=[]))
    b['ymax']=max(b['ymax'],np.abs(P[:,0]).max()); b['zbot']=min(b['zbot'],P[:,1].min()); b['pieces'].append(P)
    if np.abs(P[:,0]).min()<0.5: b['ztop_c']=P[:,1].max(); b['zbot_c']=P[np.abs(P[:,0])<0.5][:,1].min()
clamps={}
for p in parts:
    m=re.match(r'(.+)_CLAMP_(\d+)_S$',p['name'])
    if m and p['group']=='decks':
        P=np.array(p['poly']); clamps.setdefault(m.group(1),[]).append((P[:,0].min(),P[:,0].max(),p['off'],p['th'],P[:,1].min(),P[:,1].max()))
add=[]
def mirror(poly): return [[-x,z] for x,z in poly]
# ---------------- HANGING KNEES (vertical, under each beam end, over the clamp) ----------------
HK_T=2.5; HK_ARM=9.0; HK_DROP=11.0; HK_W=2.0
for (deck,n),b in sorted(beams.items()):
    if deck.startswith('GANGWAY'): continue
    cl=[c for c in clamps.get(deck,[]) if c[0]-0.1<=b['x']<=c[1]+0.1]
    if not cl: continue
    c=cl[0]; yci=c[2]-c[3]/2            # clamp inner face
    if b['ymax']<yci-1: continue        # beam does not reach the side (cut by an opening)
    zb=b['zbot']; x0=b['x']-HK_T/2; x1=b['x']+HK_T/2
    if any(abs(b['x']-mx)<r+3 for mx,r in MAST): continue
    y_out=yci-0.05
    poly=Polygon([(y_out-HK_ARM,zb),(y_out,zb),(y_out,zb-HK_DROP),(y_out-HK_W,zb-HK_DROP),(y_out-HK_W,zb-HK_W-1.5),(y_out-HK_W-1.5,zb-HK_W),(y_out-HK_ARM,zb-1.6)]).buffer(0)
    # keep inside the hull below the clamp (the side tumbles in at the lower deck)
    clip=[]
    for z in np.arange(zb-HK_DROP-0.5,zb-c[5]+c[5]+0.01,0.5):
        yi=yin(x0,x1,z,z+0.5) 
        if yi is not None: clip.append(box(-200,z,yi-0.1,z+0.5))
    if clip: poly=poly.intersection(unary_union(clip+[box(-200,c[4],200,500)]))
    poly=poly.difference(box(yci,c[4]-0.05,300,c[5]+0.05))
    if poly.is_empty: continue
    if poly.geom_type!='Polygon': poly=max(poly.geoms,key=lambda g:g.area)
    if poly.area<8: continue
    co=np.array(poly.exterior.coords).tolist()
    for sd,pp in (('S',co),('P',mirror(co))):
        add.append(dict(name=f'{deck}_HANGING_KNEE_{n}_{sd}',plane='YZ',off=x0,th=HK_T,group='knees',note='hanging knee under the beam end, notched over the clamp',poly=pp))
# ---------------- LODGING KNEES (horizontal, aft face of each beam, against the side) ----------------
LK_ARM_Y=9.0; LK_ARM_X=8.0; LK_W=1.8; LK_H=2.0
OP=unary_union([box(a,c,b,d) for a,b,c,d in OPEN]+[box(mx-r-1,-r-1,mx+r+1,r+1) for mx,r in MAST])
for (deck,n),b in sorted(beams.items()):
    cl=[c for c in clamps.get(deck,[]) if c[0]-0.1<=b['x']<=c[1]+0.1]
    if not cl: continue
    c=cl[0]; zb=b['zbot']
    if b['ymax']<c[2]-c[3]/2-1: continue
    xf=b['x']+b['sided']/2+0.05
    xs=np.linspace(xf,xf+LK_ARM_X,9)
    ys=[]
    for x in xs:
        v=yin(x-0.3,x+0.3,zb,zb+LK_H,reach=1.5); ys.append(v if v is not None else np.nan)
    ys=np.array(ys)
    if np.isnan(ys).all(): continue
    ys=np.where(np.isnan(ys),np.nanmin(ys),ys)-0.1
    side=Polygon(np.r_[np.c_[xs,ys],np.c_[xs[::-1],ys[::-1]-LK_W]])
    arm=box(xf,ys[0]-LK_ARM_Y,xf+LK_W,ys[0])
    throat=Polygon([(xf+LK_W,ys[0]-LK_W-2.5),(xf+LK_W,ys[0]-LK_W),(xf+LK_W+2.5,ys[0]-LK_W)])
    poly=unary_union([side,arm,throat]).buffer(0)
    # must not foul the next beam or an opening
    nxt=[bb for bb in beams.values() if bb['deck']==deck and 0<bb['x']-b['x']<LK_ARM_X+6]
    if nxt or poly.intersects(OP) or Polygon(np.c_[np.array(poly.exterior.coords)[:,0],-np.array(poly.exterior.coords)[:,1]]).intersects(OP): continue
    co=np.array(poly.exterior.coords).tolist()
    for sd,pp in (('S',co),('P',[[x,-y] for x,y in co])):
        add.append(dict(name=f'{deck}_LODGING_KNEE_{n}_{sd}',plane='XY',off=zb,th=LK_H,group='knees',note='lodging knee on the clamp, against the side and the aft face of the beam',poly=pp))
# ---------------- PILLARS (centreline, hold and between decks) ----------------
PS=2.6
def beam_at(deck_prefix,x,tol):
    c=[b for b in beams.values() if b['deck'].startswith(deck_prefix) and abs(b['x']-x)<=tol and b.get('ztop_c') is not None]
    return min(c,key=lambda b:abs(b['x']-x)) if c else None
def clear(x): return all(not (a-PS<x<b+PS and c<0<d) for a,b,c,d in OPEN) and all(abs(x-mx)>r+PS for mx,r in MAST)
for b in sorted(beams.values(),key=lambda b:b['x']):
    if b.get('ztop_c') is None or not clear(b['x']): continue
    x=b['x']
    if b['deck'].startswith('LOWER_DECK'):
        zbase=float(Zb(x))+JP['KS_T']; ztop=b['zbot_c']
        if ztop-zbase>6: add.append(dict(name=f'PILLAR_HOLD_X{x:.0f}',plane='XZ',off=0.0,th=PS,group='pillars',note='hold pillar, keelson to lower-deck beam',poly=box(x-PS/2,zbase,x+PS/2,ztop).exterior.coords[:]))
    if b['deck']=='MAIN_DECK':
        lb=beam_at('LOWER_DECK',x,2.5)
        if lb is not None:
            add.append(dict(name=f'PILLAR_TWEENDECK_X{x:.0f}',plane='XZ',off=0.0,th=PS,group='pillars',note='between-deck pillar, lower-deck beam to main-deck beam',poly=box(x-PS/2,lb['ztop_c'],x+PS/2,b['zbot_c']).exterior.coords[:]))
for d in add: d['poly']=[list(map(float,v)) for v in d['poly']]
from collections import Counter
print(Counter(d['group'] for d in add))
json.dump(parts+add,open(O+'/parts_v9.json','w')); json.dump(dict(pieces=fp),open(O+'/frame_pieces_v9.json','w'))
