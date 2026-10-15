import json,numpy as np
from scipy.interpolate import CubicSpline, PchipInterpolator
S='/tmp/claude-0/-home-user-o-yaku-courses/63728b8f-e365-510d-8e4b-6775a7fec844/scratchpad'; O=S+'/out'
meta=json.load(open(O+'/meta.json')); STX={int(k):v for k,v in meta['STX'].items()}
_st=np.load(O+'/stations.npy',allow_pickle=True).item()
N=241
def resample(P,n=N):
    u=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]; u/=u[-1]; t=np.linspace(0,1,n)
    return np.c_[np.interp(t,u,P[:,0]),np.interp(t,u,P[:,1])]
STN={}
for s in range(1,19):
    key='8_1a' if s==8 else (f'{s}_1a' if f'{s}_1a' in _st else f'{s}_1b')
    STN[s]=resample(_st[key])
def section(X,exclude=(),kind='cubic'):
    ss=[s for s in sorted(STN,key=lambda s:STX[s]) if s not in exclude]
    xs=np.array([STX[s] for s in ss]); A=np.stack([STN[s] for s in ss])   # (ns,N,2)
    f=CubicSpline(xs,A,axis=0,bc_type='natural') if kind=='cubic' else PchipInterpolator(xs,A,axis=0)
    return f(X)
def curve_dist(A,B):
    # max/mean distance from points of A to polyline B
    d=[]
    for p in A:
        v=B[1:]-B[:-1]; w=p-B[:-1]; t=np.clip((w*v).sum(1)/(v*v).sum(1),0,1); q=B[:-1]+t[:,None]*v
        d.append(np.hypot(*(p-q).T).min())
    return np.array(d)
if __name__=='__main__':
    for kind in ('cubic','pchip'):
        print(kind)
        for s in range(2,18):
            P=section(STX[s],exclude=(s,),kind=kind); d=curve_dist(P,STN[s])
            print('  LOO st %2d  mean %.2f  max %.2f mm'%(s,d.mean(),d.max()))
