import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import O
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
parts=json.load(open(O+'/parts_v4.json')); new=json.load(open(O+'/bow_backbone.json'))
fparts=json.load(open(O+'/frame_parts.json'))['parts']
drop={'STEM','GRIPE','KNEE_OF_HEAD','DEADWOOD_FWD'}
parts=[p for p in parts if p['name'] not in drop]
NB=unary_union([box(p['x0']-0.05,p['joint'][0],p['x1']+0.05,p['joint'][1]+5.7) for p in fparts])
NOTE=dict(STEM='follows plan_5 drawn lines (inner line / outer line); hooked scarf at heel',
          APRON='inside stem, between frames 42-45 and stem (plan_5)',GRIPE='forefoot; scarf with keel per plan_5',
          KNEE_OF_HEAD_LOWER='plan_5 lines',KNEE_OF_HEAD_UPPER='plan_5 lines (cheek line)',DEADWOOD_FWD='above keel, aft of apron',KEEL_FWD_TIP='')
keel=[p for p in parts if p['name']=='KEEL_FWD'][0]; fk=[p for p in parts if p['name']=='FALSE_KEEL'][0]
K=Polygon(keel['poly']).buffer(0); FK=Polygon(fk['poly']).buffer(0)
tip=Polygon(new.pop('KEEL_FWD_TIP')[0]).buffer(0)
reg=unary_union([Polygon(v[0]).buffer(0) for v in new.values()])
K=unary_union([K,tip]).difference(reg).difference(NB).difference(FK)
K=max(K.geoms,key=lambda g:g.area) if K.geom_type!='Polygon' else K
keel['poly']=np.array(K.exterior.coords).tolist()
FK=FK.difference(reg); FK=max(FK.geoms,key=lambda g:g.area) if FK.geom_type!='Polygon' else FK
fk['poly']=np.array(FK.exterior.coords).tolist()
KS=unary_union([Polygon(p['poly']).buffer(0) for p in parts if p['name'].startswith('KEELSON')])
for k,v in new.items():
    g=Polygon(v[0]).buffer(0).difference(NB).difference(FK).difference(KS)
    gs=[g] if g.geom_type=='Polygon' else sorted([q for q in g.geoms if q.area>0.3],key=lambda q:-q.area)
    gs=[q for q in gs if q.area>5]
    for j,q in enumerate(sorted(gs,key=lambda q:q.bounds[0])):
        nm=k if len(gs)==1 else f'{k}_{j+1}'
        parts.append(dict(name=nm,plane='XZ',off=0.0,th=5.3,group='backbone',note=NOTE[k],poly=np.array(q.exterior.coords).tolist()))
json.dump(parts,open(O+'/parts_v4.json','w')); print(len(parts),'parts')
