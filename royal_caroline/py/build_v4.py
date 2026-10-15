import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import section, O
from joints import P as JP, Zb, FX
from shapely.geometry import Polygon, LineString, box, MultiPolygon
from shapely.ops import split, unary_union
from shapely.validation import make_valid
bb=json.load(open(O+'/backbone.json')); pr=json.load(open(O+'/profile1a.json'))
PCS={k:Polygon(v[0]).buffer(0) for k,v in bb['pieces'].items()}
K=1000/244.8/48; X0=4194.98
def Xpost(f,Z): y=2104.73-np.asarray(Z)*102.1/8.689; return (np.polyval(f,y)-X0)*K
fa,ff=pr['post_aft_fit'],pr['post_fore_fit']
BW=2.65; parts=[]   # dict(name, plane, offset, thick, poly(list), group)
def add(name,poly,plane,off,th,group,note=''):
    geoms=[poly] if poly.geom_type=='Polygon' else [g for g in poly.geoms if g.geom_type=='Polygon']
    geoms=[g for g in geoms if g.area>0.3]
    for j,g in enumerate(sorted(geoms,key=lambda g:-g.area)):
        parts.append(dict(name=name+('' if len(geoms)==1 else f'_{j+1}'),plane=plane,off=float(off),th=float(th),group=group,note=note,poly=np.array(g.exterior.coords).tolist()))
def splitby(poly,line):
    r=split(poly,LineString(line)); return list(r.geoms)
def pick(geoms,fn): return unary_union([g for g in geoms if fn(g)])
# ---------------- stern knee (continuation of keelson aft to the wing transom) & deadwood fill
WT=dict(x0=-11.8,x1=-5.0,z0=72.0,z1=78.0)        # wing transom section at centreline (plan_5)
x_ks0=FX[0]-JP['SIDED_FR']-3                       # keelson aft end (X 32)
zk0=float(Zb(x_ks0)); KS=JP['KS_T']
knee=Polygon([(x_ks0+6,zk0-6*0.83),(x_ks0+6,zk0-6*0.83+KS),(WT['x1'],WT['z0']+KS),(WT['x1'],WT['z0'])])
slope=(WT['z0']-zk0)/(WT['x1']-x_ks0)
knee=Polygon([(x_ks0,zk0),(WT['x1'],WT['z0']),(WT['x1'],WT['z0']+KS),(x_ks0,zk0+KS)])
# scarf with keelson: overlap 6 mm, tabled -> simply butt + engraved; knee overlaps nothing
dw=PCS['DEADWOOD_AFT']
fill=Polygon([(x_ks0,0),(x_ks0,zk0),(WT['x1'],WT['z0']),(float(Xpost(ff,WT['z0'])),WT['z0']),(float(Xpost(ff,0)),0)]).buffer(0)
post_poly=PCS['STERNPOST']
dw=unary_union([dw,fill.difference(post_poly)]).difference(knee)
# keep frame notches: subtract frame footprints above notch bottom
for p in json.load(open(O+'/frame_parts.json'))['parts']:
    zn,zt=p['joint']; dw=dw.difference(box(p['x0']-0.05,zn,p['x1']+0.05,zn+80))
dw=dw.intersection(box(-30,1.8,200,200))
# deadwood in 3 layers (real deadwood was built up in layers)
lay=[]
rest=dw
for zc in (14.0,34.0):
    g=splitby(rest,[(-40,zc),(220,zc)]); lay.append(pick(g,lambda q:q.centroid.y<zc)); rest=pick(g,lambda q:q.centroid.y>=zc)
lay.append(rest)
for j,g in enumerate(lay,1): add(f'DEADWOOD_AFT_L{j}',g,'XZ',0,2*BW,'backbone','layered deadwood (model split)')
add('STERN_KNEE',knee,'XZ',0,2*BW,'backbone','continues keelson to wing transom (plan_5 cross-hatched band)')
# ---------------- keel / false keel / keelson split
ZFK=-7.0
keel=PCS['KEEL']; g=splitby(keel,[(-40,ZFK),(700,ZFK)])
fk=pick(g,lambda q:q.centroid.y<ZFK); kl=pick(g,lambda q:q.centroid.y>=ZFK)
# keel scarf (tabled, 40 mm, between frames 22/23 at X~279)
xs=279.2; sc=[(xs-20,ZFK-1),(xs-20,-2.6),(xs+20,-2.6),(xs+20,5)]
gs=splitby(kl,sc); add('KEEL_AFT',pick(gs,lambda q:q.centroid.x<xs),'XZ',0,2*BW,'backbone','tabled scarf 40 mm with KEEL_FWD')
add('KEEL_FWD',pick(gs,lambda q:q.centroid.x>=xs),'XZ',0,2*BW,'backbone')
add('FALSE_KEEL',fk,'XZ',0,2*BW,'backbone','plan_5 shows a false keel ~2.4 mm')
ks=PCS['KEELSON']; xs2=346.0; sc2=[(xs2-15,0),(xs2-15,float(Zb(xs2))+2.6),(xs2+15,float(Zb(xs2))+2.6),(xs2+15,80)]
gs=splitby(ks,sc2); add('KEELSON_AFT',pick(gs,lambda q:q.centroid.x<xs2),'XZ',0,2*BW,'backbone','tabled scarf 30 mm')
add('KEELSON_FWD',pick(gs,lambda q:q.centroid.x>=xs2),'XZ',0,2*BW,'backbone')
add('DEADWOOD_FWD',PCS['DEADWOOD_FWD'],'XZ',0,2*BW,'backbone')
# ---------------- stem split: apron (aft of rabbet), stem, gripe, knee of head
stem=PCS['STEM']
ra=np.array(pr['stem_rabbet_aft']); ra=ra[ra[:,1].argsort()]
t=np.gradient(ra,axis=0); t/=np.linalg.norm(t,axis=1)[:,None]; n=np.c_[t[:,1],-t[:,0]]
if n[len(n)//2,0]<0: n=-n          # forward normal
apron_line=ra-n*1.0                  # stem aft face 1 mm behind rabbet
fore_line=ra+n*7.5                   # stem fore face (moulded ~7.5 mm = 0.36 m)
def ext(L,top=130,bot=-20):
    d1=L[-1]-L[-8]; d1/=np.linalg.norm(d1); d0=L[0]-L[7]; d0/=np.linalg.norm(d0)
    return np.r_[[L[0]+d0*40],L,[L[-1]+d1*60]]
g=splitby(stem,ext(apron_line)); 
apron=pick(g,lambda q:q.representative_point().x<np.interp(q.representative_point().y,apron_line[:,1],apron_line[:,0]))
st2=pick(g,lambda q:q.representative_point().x>=np.interp(q.representative_point().y,apron_line[:,1],apron_line[:,0]))
g=splitby(st2,ext(fore_line))
stem_main=pick(g,lambda q:q.representative_point().x<np.interp(q.representative_point().y,fore_line[:,1],fore_line[:,0]))
outer=pick(g,lambda q:q.representative_point().x>=np.interp(q.representative_point().y,fore_line[:,1],fore_line[:,0]))
g=splitby(outer,[(450,22),(700,22)])
add('STEM',unary_union([stem_main,apron]).buffer(0.01).buffer(-0.01),'XZ',0,2*BW,'backbone','incl. apron; frames 42-45 seat in it; fore face ~7.5 mm fwd of rabbet (assumed)')
add('GRIPE',pick(g,lambda q:q.centroid.y<22),'XZ',0,2*BW,'backbone')
add('KNEE_OF_HEAD',pick(g,lambda q:q.centroid.y>=22),'XZ',0,2*BW,'backbone','lower part only; head rails/trailboards not included')
add('STERNPOST',post_poly,'XZ',0,2*BW,'backbone')
# ---------------- rudder (plan_5), fore edge = post aft line, thickness 4.0
Zt=134.0; ZB=-9.2
hinge=[(float(Xpost(fa,z)),z) for z in np.linspace(ZB,Zt,30)]
aft=[(-30.2,Zt),(-23.8,73.3),(-25.5,56.7),(-20.5,ZB)]
rud=Polygon(hinge+aft).buffer(0)
PINT=[4.3,23.0,41.4,60.3,78.9]
for z in PINT:   # gudgeon seats: 1.0 deep x 2.4 high notches in rudder fore edge (pintle straps)
    x=float(Xpost(fa,z)); rud=rud.difference(box(x-1.0,z-1.2,x+0.5,z+1.2))
add('RUDDER',rud,'XZ',0,4.0,'rudder','pintles/gudgeons at Z '+', '.join(map(str,PINT)))
# ---------------- wing transom & lower transoms (XY plane, thickness in Z)
def hb(x,z):
    P=section(max(x,0.0),kind='pchip'); out=[]
    for i in range(len(P)-1):
        z0,z1=P[i,1],P[i+1,1]
        if (z0-z)*(z1-z)<=0 and z0!=z1: out.append(P[i,0]+(z-z0)/(z1-z0)*(P[i+1,0]-P[i,0]))
    return max(out)
def transom(name,x0,x1,z0,z1,note):
    zm=(z0+z1)/2; xs=np.linspace(x0,x1,8); y=np.array([hb(x,zm) for x in xs])
    poly=Polygon(np.r_[np.c_[xs,y],np.c_[xs[::-1],-y[::-1]]]).buffer(0)
    poly=poly.difference(box(-50,-BW-0.05,200,BW+0.05)) if name!='WING_TRANSOM' else poly
    add(name,poly,'XY',z0,z1-z0,'stern',note)
CTY=(-41.5,-28.5,-14.5,14.5,28.5,41.5)
def transom_wt():
    zm=(WT['z0']+WT['z1'])/2; xs=np.linspace(WT['x0'],WT['x1'],8); y=np.array([hb(x,zm) for x in xs])
    poly=Polygon(np.r_[np.c_[xs,y],np.c_[xs[::-1],-y[::-1]]]).buffer(0)
    holes=[box(-11.85,y0-2.05,-9.75,y0+2.05) for y0 in CTY]
    for h in holes: poly=poly.difference(h)
    poly=poly.difference(box(-20,-BW-0.05,float(Xpost(ff,WT['z0']))+0.05,BW+0.05))   # let in over the post
    parts.append(dict(name='WING_TRANSOM',plane='XY',off=WT['z0'],th=WT['z1']-WT['z0'],group='stern',note='through-mortises for 6 counter timbers; bolted to fore side of post; round-up/round-aft ignored',
        poly=np.array(poly.exterior.coords).tolist(),holes=[np.array(h.coords).tolist() for h in poly.interiors]))
transom_wt()
transom('TRANSOM_2',-7.6,0.0,61.7,65.1,'P/S halves butt against post/deadwood')
transom('TRANSOM_3',-5.0,0.0,53.2,57.4,'P/S halves butt against post/deadwood')
# ---------------- counter timbers (XZ profile at Y = +-14.5, +-28.5, +-41.5)
outer=np.array([(-16.0,84.4),(-20.8,87.2),(-25.5,88.9),(-30.2,98.3),(-35.3,110.6),(-39.3,123.4),(-46.0,126.6),(-52.3,147.9)])
L=LineString(outer); inner=L.parallel_offset(4.0,'right',join_style=2)
ic=np.array(inner.coords)
if ic[0,1]>ic[-1,1]: ic=ic[::-1]
ct=Polygon(np.r_[[(-11.8,WT['z1']),(WT['x0']+0.0,WT['z1'])],outer,[(outer[-1,0]+4.2,outer[-1,1])],ic[::-1],[(-7.8,WT['z1'])]]).buffer(0)
ct=unary_union([ct,box(-11.8,WT['z0'],-9.8,WT['z1'])])   # through-tenon into wing transom
for y in (-41.5,-28.5,-14.5,14.5,28.5,41.5):
    add(f"COUNTER_TIMBER_{'P' if y<0 else 'S'}{abs(y):.0f}",ct,'XZ',y,4.0,'stern','6 counter timbers tenoned into the wing transom (B4); round-aft ignored')
# ---------------- fashion pieces & aft half-frames (YZ plane, P/S halves)
def halfframe(name,xa,xb,ztop=None):
    def solid(x):
        P=section(x,kind='pchip'); zr=P[0,1]; t=np.interp(P[:,1],[zr,P[-1,1]],[JP['T_FLOOR'],JP['T_TOP']])
        T=np.gradient(P,axis=0); T/=np.linalg.norm(T,axis=1)[:,None]; N=np.c_[T[:,1],-T[:,0]]
        if N[len(N)//2,0]<0: N=-N
        In=P-N*t[:,None]; return Polygon(np.r_[P,In[::-1]]).buffer(0)
    s=unary_union([solid(xa),solid(xb)]).intersection(box(BW+0.02,-50,200,500))
    if ztop is not None: s=s.intersection(box(-200,-50,200,ztop))
    for side,sg in (('S',1),('P',-1)):
        g=s if sg>0 else Polygon(np.array(s.exterior.coords)*[-1,1]) if s.geom_type=='Polygon' else s
        add(f'{name}_{side}',g,'YZ',xa,xb-xa,'stern','square half-frame (real ones canted), heel butts deadwood')
halfframe('HALF_FRAME_H1',22.0,26.0); halfframe('HALF_FRAME_H2',10.0,14.0)
halfframe('FASHION_PIECE',0.5,4.5,ztop=WT['z0'])
json.dump(parts,open(O+'/parts_v4.json','w'))
from collections import Counter
print(len(parts),'parts'); print(Counter(p['group'] for p in parts))
for p in parts: print('  %-26s %s off %7.2f th %.1f area %7.1f'%(p['name'],p['plane'],p['off'],p['th'],Polygon(p['poly']).area))
