import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import O
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
fp=json.load(open(O+'/frame_pieces_v5.json'))['pieces']; parts=json.load(open(O+'/parts_v5.json'))
parts=[p for p in parts if not p['name'].startswith('CLAMP_MAINDECK')]
TP,BM,BS,CH,CW=1.0,3.0,4.5,2.6,2.0
# beam round-up profile measured on plan_6 B2 (underside of main-deck planking = beam top), px 0.0851 mm
# t = |y| / half-span(740 px = 63 mm), drop in px
PT=np.array([0,.135,.27,.34,.405,.47,.54,.61,.675,.74,.81,.845,.88,.91,.945,1.0])
PD=np.array([0,.5,.5,1.5,2.5,3.5,5,6.5,9,12,15.5,17.5,22,25,27.5,30.5])*0.0851/63.0   # drop per mm of half-span
def drop(y,yref): return np.interp(np.abs(y)/yref,PT,PD)*yref
CAMB=float(PD[-1])
# beam stations read from plan_5 (A3/3): automatic block detection + visual check
STATIONS={'LOWER_DECK_AFT':[146.6,162.4,178.4,194.6,210.8,225.8],
 'LOWER_DECK_MID':[239.5,281.9,302.6,327.8,373.0,406.5,440.3],
 'LOWER_DECK_FWD':[466.0,486.0,509.0,524.0],
 'CABIN_DECK':[15.5,32.1,50.4,68.0,84.8],
 'MAIN_DECK':[103.5,131.6,146.4,164.1,179.4,195.5,211.6,227.6,242.3,300.0,325.0,374.5,406.5,440.3,461.1,478.0,509.1,524.5],
 'POOP_DECK':[19.4,37.2,52.8,68.5,83.2]}
FX=json.load(open(O+'/frames_X.json'))['X_mm']+[532.1,543.4]
# ---- timbers seen from inside (YZ items) ----
YZ=[(p['x0'],p['x1'],Polygon(p['poly']).buffer(0)) for p in fp if np.array(p['poly'])[:,0].mean()>0]
YZ+=[(p['off'],p['off']+p['th'],Polygon(p['poly']).buffer(0)) for p in parts if p['plane']=='YZ' and np.array(p['poly'])[:,0].mean()>0]
def yin(xa,xb,za,zb,reach=6.0):
    best=None
    for x0,x1,P in YZ:
        if x1<xa-reach or x0>xb+reach: continue
        q=P.intersection(box(3.0,za,200,zb))
        if q.is_empty: continue
        v=q.bounds[0]; best=v if best is None else min(best,v)
    return best
occ=sorted([(x0,x1) for x0,x1,_ in YZ])
def gaps(xa,xb):
    out=[]; m=occ[0][1]
    for a,b in occ[1:]:
        if a-m>=BS+0.1 and xa<=(a+m)/2<=xb: out.append((m+a)/2)
        m=max(m,b)
    return out
MAST=[(92.0,4.3),(261.5,5.5),(495.9,5.2)]
OPEN={'main':[(109.5,142.5,16,55),(131.5,142,-56,-38.5),(242,274,46,64),(242,258,-64,-46),(278.6,312.3,-14.5,14.5),(387.4,439.3,-14.5,14.5)],
      'lower':[(109.5,142.5,16,55),(131.5,142,-56,-38.5),(242,274,46,64),(242,258,-64,-46),(278.6,312.3,-14.5,14.5),(387.4,439.3,-14.5,14.5)],
      'cabin':[],'poop':[(12,32,-23.6,23.6)]}
HOLES={'main':[(349.4,4.5)]+MAST[1:],'lower':[(349.4,4.5)]+MAST[1:],'cabin':[MAST[0]],'poop':[MAST[0]]}
DECKS=[('LOWER_DECK_AFT','lower',[(137,44.6),(170,44.0),(190,43.3),(210,42.8),(233,42.6)]),
       ('LOWER_DECK_MID','lower',[(237,40.0),(250,39.6),(290,39.6),(330,39.7),(370,39.8),(390,40.3),(430,41.0),(458,41.2)]),
       ('LOWER_DECK_FWD','lower',[(462,49.4),(510,50.5),(527,51.3)]),
       ('CABIN_DECK','cabin',[(13,76.4),(30,75.6),(50,74.5),(70,73.7),(97,73.0)]),
       ('MAIN_DECK','main',[(101,86.8),(110,86.7),(150,86.0),(170,85.6),(190,85.0),(210,84.6),(230,82.8),(290,80.6),(330,80.3),(370,80.3),(410,80.6),(450,83.5),(470,84.1),(510,85.6),(527,86.2)]),
       ('POOP_DECK','poop',[(13,121.4),(30,120.9),(50,120.6),(70,119.7),(97,118.8)])]
add=[]
BXUSED={}
def openings(kind):
    g=[box(a,c,b,d) for a,b,c,d in OPEN[kind]]+[Point(x,0).buffer(r+0.2,32) for x,r in HOLES[kind]]
    return unary_union(g)
for name,kind,tab in DECKS:
    tab=np.array(tab); Zp=lambda x: float(np.interp(x,tab[:,0],tab[:,1]))
    xa,xb=tab[0,0],tab[-1,0]
    bx=list(STATIONS[name])
    bx=[x for x in bx if all(abs(x-mm)>r+BS/2+0.6 for mm,r in HOLES[kind])]
    BXUSED[name]=[round(x,1) for x in bx]
    # panels: group consecutive beams while Zp range <=0.6
    bounds=[xa]+[ (bx[i]+bx[i+1])/2 for i in range(len(bx)-1)]+[xb]
    # panel per run of bays
    panels=[]; i=0
    while i<len(bx):
        j=i
        while j+1<len(bx) and abs(Zp(bx[j+1])-Zp(bx[i]))<=0.6 and bx[j+1]-bx[i]<110: j+=1
        panels.append((i,j)); i=j+1
    OP=openings(kind)
    for pi,(i,j) in enumerate(panels):
        x0=xa if i==0 else (bx[i-1]+bx[i])/2+0.0
        x1=xb if j==len(bx)-1 else (bx[j]+bx[j+1])/2
        zt=np.mean([Zp(bx[k]) for k in range(i,j+1)]); zpb=zt-TP
        yref=yin(x0,x1,zpb-6,zpb,reach=1.0) or 60
        zbb=zpb-drop(yref,yref)-BM; zcb=zbb-CH          # clamp top = beam-end underside
        # clamps (XZ chords), one per side per panel
        yc=yin(x0,x1,zcb,zbb,reach=1.0)
        if yc is not None:
            for sg,sd in ((1,'S'),(-1,'P')):
                add.append(dict(name=f'{name}_CLAMP_{pi+1:02d}_{sd}',plane='XZ',off=sg*(yc-0.1-CW/2),th=CW,group='decks',note='clamp; beams rest on it',poly=box(x0+0.05,zcb,x1-0.05,zbb).exterior.coords[:]))
        # beams
        for k in range(i,j+1):
            x=bx[k]; yb=yin(x-BS/2,x+BS/2,zbb,zpb,reach=0.5)
            if yb is None: continue
            yb-=0.1
            bm=box(-yb,zbb,yb,zpb)
            # cut around openings crossing this beam (carlings added below)
            for a,b,c,d in OPEN[kind]:
                if a-BS/2<x<b+BS/2: bm=bm.difference(box(c-CW,zbb-1,d+CW,zpb+1))
            for jj,q in enumerate(sorted([g for g in ([bm] if bm.geom_type=='Polygon' else bm.geoms) if g.area>1],key=lambda g:g.bounds[0])):
                add.append(dict(name=f'{name}_BEAM_{k+1:02d}'+('' if bm.geom_type=='Polygon' else f'_{jj+1}'),plane='YZ',off=x-BS/2,th=BS,group='decks',
                                note='deck beam, X from plan_5 (A3/3), round-up profile traced from plan_6 B2',poly=np.array(q.exterior.coords).tolist()))
    # carlings along opening long sides, between the beams bounding the opening
    for n,(a,b,c,d) in enumerate(OPEN[kind],1):
        if b<xa or a>xb: continue
        pre=[x for x in bx if x<=a-BS/2]; nxt=[x for x in bx if x>=b+BS/2]
        if not pre or not nxt: continue
        ca,cb=pre[-1]+BS/2+0.05,nxt[0]-BS/2-0.05
        zl=[]
        for (i,j) in panels:
            lo=xa if i==0 else (bx[i-1]+bx[i])/2; hi=xb if j==len(bx)-1 else (bx[j]+bx[j+1])/2
            if hi>ca and lo<cb: zl.append(np.mean([Zp(bx[k]) for k in range(i,j+1)]))
        zpb=min(zl)-TP
        ylim=(yin(ca,cb,zpb-BM-CH,zpb,reach=1.0) or 999)-CW-0.3
        for yy,sd in ((c-CW/2,'1'),(d+CW/2,'2')):
            if abs(yy)+CW/2>ylim: continue
            ref_y=yin(ca,cb,zpb-6,zpb,reach=1.0) or 60
            ztop=zpb-float(drop(abs(yy)+CW/2,ref_y))
            add.append(dict(name=f'{name}_CARLING_{n}_{sd}',plane='XZ',off=yy,th=CW,group='decks',note='carling (longitudinal) at opening side',poly=box(ca,ztop-BM,cb,ztop).exterior.coords[:]))
    print(name,'beams',len(bx),[round(v,1) for v in bx])
for d in add: d['poly']=[list(map(float,v)) for v in d['poly']]
json.dump(parts+add,open(O+'/parts_v6.json','w')); json.dump(dict(pieces=fp),open(O+'/frame_pieces_v6.json','w'))
print('added',len(add)); json.dump(BXUSED,open(O+'/beam_x_used.json','w'),indent=0)
