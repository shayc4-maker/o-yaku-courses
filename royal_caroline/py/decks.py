import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import O
from shapely.geometry import Polygon, box, Point
from shapely.ops import unary_union
fp=json.load(open(O+'/frame_pieces_v5.json'))['pieces']; parts=json.load(open(O+'/parts_v5.json'))
parts=[p for p in parts if not p['name'].startswith('CLAMP_MAINDECK')]
TP,BM,BS,CH,CW=1.0,2.5,4.0,2.6,2.0
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
def openings(kind):
    g=[box(a,c,b,d) for a,b,c,d in OPEN[kind]]+[Point(x,0).buffer(r+0.2,32) for x,r in HOLES[kind]]
    return unary_union(g)
for name,kind,tab in DECKS:
    tab=np.array(tab); Zp=lambda x: float(np.interp(x,tab[:,0],tab[:,1]))
    xa,xb=tab[0,0],tab[-1,0]
    bx=[x for x in FX if xa+2<=x<=xb-2]
    bx=[x for x in bx if all(abs(x-m)>r+BS/2+0.6 for m,r in HOLES[kind])]
    # keep about every other gap (~22 mm)
    sel=[]; 
    for x in bx:
        if not sel or x-sel[-1]>19: sel.append(x)
    bx=sel
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
        zt=np.mean([Zp(bx[k]) for k in range(i,j+1)]); zpb=zt-TP; zbb=zpb-BM; zcb=zbb-CH
        # plank outline from sampled inner surface
        xs=np.linspace(x0,x1,max(4,int((x1-x0)/1.0)))
        ys=[]
        for x in xs:
            v=yin(x-0.6,x+0.6,zpb,zt,reach=2.5); ys.append(v)
        ys=np.array([v if v is not None else np.nan for v in ys])
        ys=np.where(np.isnan(ys),np.nanmin(ys),ys)-0.1
        from scipy.ndimage import minimum_filter1d
        ys=minimum_filter1d(ys,5)
        pl=Polygon(np.r_[np.c_[xs,ys],np.c_[xs[::-1],-ys[::-1]]]).buffer(0).difference(OP)
        for q in ([pl] if pl.geom_type=='Polygon' else list(pl.geoms)):
            if q.area<3: continue
            add.append(dict(name=f'{name}_PLANK_{pi+1:02d}' + ('' if pl.geom_type=='Polygon' else f'_{len([a for a in add if a["name"].startswith(f"{name}_PLANK_{pi+1:02d}")])+1}'),plane='XY',off=zpb,th=TP,group='decks',
                            note=f'deck planking panel, top Z {zt:.2f} (plan_5); engrave plank lines',poly=np.array(q.exterior.coords).tolist(),holes=[np.array(h.coords).tolist() for h in q.interiors]))
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
                                note='deck beam (no camber)',poly=np.array(q.exterior.coords).tolist()))
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
            add.append(dict(name=f'{name}_CARLING_{n}_{sd}',plane='XZ',off=yy,th=CW,group='decks',note='carling at opening side',poly=box(ca,zpb-BM,cb,zpb).exterior.coords[:]))
    print(name,'beams',len(bx),'panels',len(panels))
for d in add: d['poly']=[list(map(float,v)) for v in d['poly']]
json.dump(parts+add,open(O+'/parts_v6.json','w')); json.dump(dict(pieces=fp),open(O+'/frame_pieces_v6.json','w'))
print('added',len(add))
