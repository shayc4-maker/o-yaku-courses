# extend the straight tops of bow frames 1-8 (all faces) up to the bulwark lower line (data/bulwark_line_v1.json); curves untouched -> data/frames_outer_approved_v3.json
import json,numpy as np,copy
A=json.load(open('data/frames_outer_approved_v2.json')); L=json.load(open('data/bulwark_line_v1.json'))
segs=[np.array(v) for k,v in L.items() if abs(np.array(v)[-1,0]-np.array(v)[0,0])>1]
def zline(X):
    for a in segs:
        if a[:,0].min()<=X<=a[:,0].max(): o=np.argsort(a[:,0]); return float(np.interp(X,a[o,0],a[o,1]))
B=copy.deepcopy(A); rep=[]
for b in range(1,9):
    for nm in ('back','mid','front'):
        v=B[str(b)][nm]; C=np.array(v['curve']); z=zline(v['X'])
        if v.get('top'):
            p0,p1=np.array(v['top'][0]),np.array(v['top'][1]); d=p1-p0
        else:
            p0=C[-1]; d=C[-1]-C[-6]; p1=p0.copy()
        d=d/d[1]; new=p1+d*(z-p1[1]); old=p1[1]
        v['top']=[p0.tolist(),new.tolist()]; v['top_ext']=True
        rep.append((b,nm,round(v['X'],2),round(old,2),round(z,2),round(float(np.hypot(*(new-p1))),2),round(float(d[0]),3)))
for r in rep: print(r)
json.dump(B,open('data/frames_outer_approved_v3.json','w'))
