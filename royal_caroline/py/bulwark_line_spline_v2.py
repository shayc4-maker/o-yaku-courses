# bulwark lower line from the builder's marks M0-M48 (plan_1a): splines + straight steps; frame top ends vs the line
import json,numpy as np
from scipy.interpolate import splprep,splev
P={p['id']:p for p in json.load(open('data/p1a_marks_v1.json'))}
pt=lambda a,b:[(P['M%d'%i]['X'],P['M%d'%i]['Z']) for i in range(a,b+1)]
segs=[('S1','spline',pt(0,13)),('S2','straight',pt(13,16)),('S3','spline',pt(16,23)),('S4','straight',pt(23,24)),('S5','straight',pt(24,25)),
('S6','spline',pt(25,33)+pt(37,42)),('S9','straight',[pt(42,42)[0],pt(45,45)[0]]),('S10','straight',pt(45,48))]
def dense(kind,Q,n=60):
    Q=np.array(Q)
    if kind=='straight':
        if len(Q)>2:
            d=Q[-1]-Q[0]; nrm=np.array([-d[1],d[0]])/np.hypot(*d); print('  straight max dev %.2f mm'%np.abs((Q-Q[0])@nrm).max())
        return np.linspace(Q[0],Q[-1],n)
    k=min(3,len(Q)-1); tck,_=splprep(Q.T,k=k,s=0); return np.array(splev(np.linspace(0,1,n*3),tck)).T
LINE={}
for nm,kind,Q in segs:
    print(nm,kind,len(Q),'pts'); LINE[nm]=dense(kind,Q)
json.dump({k:v.tolist() for k,v in LINE.items()},open('data/bulwark_line_v2.json','w'))
def z_at(X):
    for nm,kind,Q in segs:
        a=LINE[nm]
        if a[:,0].min()-1e-6<=X<=a[:,0].max()+1e-6 and abs(a[-1,0]-a[0,0])>1:
            o=np.argsort(a[:,0]); return float(np.interp(X,a[o,0],a[o,1]))
    return None
A=json.load(open('data/frames_outer_approved_v2.json')); X=json.load(open('data/frames_X.json'))
print('frame b, face X, current top Z, line Z, diff')
for b in range(1,46):
    for nm in ('back','mid','front'):
        v=A[str(b)][nm]; C=np.array(v['curve']); t=v['top'][1][1] if v.get('top') else C[-1,1]
        z=z_at(v['X']); print(b,nm,round(v['X'],2),round(t,2),None if z is None else round(z,2),None if z is None else round(z-t,2),'' if v.get('top') else 'NO TOP')
