import json,numpy as np,sys
from shapely.geometry import Polygon, box
O=sys.argv[1]
fp=json.load(open(O+'/frame_pieces_v9.json'))['pieces']; parts=json.load(open(O+'/parts_v9.json'))
C=json.load(open(O+'/cant_pieces.json'))
fp=[p for p in fp if p['piece'] not in ('cant','hawse')]
XC=528.1
out=[]
for p in parts:
    if p['name']=='JIG_BASEBOARD':
        p['holes']=[h for h in p['holes'] if np.array(h)[:,0].min()<XC]
    if p['name'].startswith('CAP_RAIL'):
        P=Polygon(p['poly']).buffer(0)
        if P.bounds[0]>=XC: continue
        if P.bounds[2]>XC:
            q=P.intersection(box(-1e3,-1e3,XC,1e3)); q=max(getattr(q,'geoms',[q]),key=lambda g:g.area); p['poly']=np.array(q.exterior.coords).tolist()
    out.append(p)
for c in C:
    for sd,sg in (('S',1),('P',-1)):
        Q=np.array(c['Q'])*[1,sg]; n=np.array(c['n'])*[1,sg]; d=np.array(c['d'])*[1,sg]
        out.append(dict(name=f"CANT_{c['id']:02d}_{sd}" if c['piece']=='cant' else f"HAWSE_{c['id']:02d}_{sd}",plane='CANT',Q=Q.tolist(),n=n.tolist(),d=d.tolist(),th=c['th'],
            off=0,group='cants',note=f"canted timber, {abs(c['angle']):.1f} deg to the square; outline drawn on its AFT face, bevel to the faired surface",poly=c['poly']))
json.dump(out,open(O+'/parts_v10.json','w')); json.dump(dict(pieces=fp),open(O+'/frame_pieces_v10.json','w'))
print(len(fp),len(out))
