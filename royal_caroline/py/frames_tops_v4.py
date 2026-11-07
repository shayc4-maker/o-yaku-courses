# frames 1-45 all faces: extend the top (straight, end tangent or existing straight top) up to the bulwark lower line v2 (bump straightened). Never trim; curves untouched -> data/frames_outer_approved_v4.json
import json,numpy as np,copy
A=json.load(open('data/frames_outer_approved_v2.json')); L=json.load(open('data/bulwark_line_v2.json'))
segs=[np.array(v) for v in L.values() if abs(np.array(v)[-1,0]-np.array(v)[0,0])>1]
def zline(X):
    for a in segs:
        if a[:,0].min()<=X<=a[:,0].max(): o=np.argsort(a[:,0]); return float(np.interp(X,a[o,0],a[o,1]))
B=copy.deepcopy(A); skipped=[]; ext=[]
for b in range(1,46):
    for nm in ('back','mid','front'):
        v=B[str(b)][nm]; C=np.array(v['curve']); z=zline(v['X'])
        if v.get('top'): p0,p1=np.array(v['top'][0]),np.array(v['top'][1]); d=p1-p0
        else: p0=C[-1]; d=C[-1]-C[-6]; p1=p0.copy()
        if z is None or z<=p1[1]+0.05: skipped.append((b,nm,round(v['X'],1),round(float(p1[1]),2),None if z is None else round(z,2))); continue
        if abs(d[1])<0.5*np.hypot(*d): d=np.array([0.,1.])   # near-horizontal end tangent -> vertical
        d=d/d[1]; new=p1+d*(z-p1[1]); v['top']=[p0.tolist(),new.tolist()]; v['top_ext']=True; ext.append((b,nm,float(np.hypot(*(new-p1))),float(d[0])))
print('extended',len(ext),'faces; max ext %.2f mm; max |dY/dZ| %.3f'%(max(e[2] for e in ext),max(abs(e[3]) for e in ext)))
print('not extended (frame top already at/above the line):'); [print(' ',s) for s in skipped]
json.dump(B,open('data/frames_outer_approved_v4.json','w'))
