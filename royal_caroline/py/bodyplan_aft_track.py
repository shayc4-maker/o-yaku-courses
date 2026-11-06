# Aft body plan A1/2: identify stations by line order (8..18 left->right) at row R0, then follow each ink line upward; points every 10 mm of arc
import json,numpy as np
import bodyplan_points_all as B
c=B.CFG['aft']; g=c['g']; k=c['k']; R0=1450
def runs(r,x0=1400,x1=2300,maxw=10):
    w=g[r,x0:x1]; idx=np.where(w>90)[0]
    if len(idx)==0: return []
    rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1)
    return [(x0+(q*w[q]).sum()/w[q].sum(),len(q)) for q in rs]
def seeds():
    rr=[a for a,w in runs(R0) if w<=10]; return {8+i:x for i,x in enumerate(rr[:9])}   # stations 8..16 left of x=1900
def track(x,r=R0):
    xs=[(x,r)]; slope=0.0; miss=0
    while r>380:
        r-=1; xp=x+slope; w=g[r,int(xp)-5:int(xp)+6]; idx=np.where(w>90)[0]
        if len(idx)==0:
            miss+=1; x=xp
            if miss>14: break
            continue
        rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); rrn=min(rs,key=lambda q:abs(q.mean()-5))
        if len(rrn)>9: miss+=1; x=xp; 
        else:
            xc=int(xp)-5+(rrn*w[rrn]).sum()/w[rrn].sum(); slope=0.8*slope+0.2*(xc-x); x=xc; miss=0; xs.append((x,r))
        if miss>14: break
    return np.array(xs)
def points(n,xs):
    Y,Z=B.mm(c,xs[:,0],xs[:,1]); s=np.r_[0,np.cumsum(np.hypot(np.diff(Y),np.diff(Z)))]
    pts=[(Y[np.argmin(abs(s-t))],Z[np.argmin(abs(s-t))]) for t in np.arange(0,s[-1]-3,10.0)]+[(Y[-1],Z[-1])]
    return pts
if __name__=='__main__':
    sd=seeds(); print({n:round(x,1) for n,x in sd.items()})
    out={}
    for n,x in sd.items():
        t=track(x); out[n]=t; print(n,'rows',int(t[0,1]),'->',int(t[-1,1]),'Z top',round(B.mm(c,0,t[-1,1])[1],1))
    np.save('/tmp/claude-0/x/aft_tracks.npy',out,allow_pickle=True)

def joint(seed,rows_end=380):
    ids=sorted(seed); x={n:seed[n] for n in ids}; sl={n:0.0 for n in ids}; miss={n:0 for n in ids}; alive=set(ids)
    T={n:[(x[n],R0)] for n in ids}
    for r in range(R0-1,rows_end,-1):
        rr=runs(r,1400,2300); ok=[(a,w) for a,w in rr if w<=14]
        last=-1
        for n in sorted(alive):
            xp=x[n]+sl[n]
            cand=[(abs(a-xp),j,a,w) for j,(a,w) in enumerate(ok) if abs(a-xp)<=6 and j>=last]
            if not cand: miss[n]+=1; x[n]=xp
            else:
                _,j,a,w=min(cand); sl[n]=0.8*sl[n]+0.2*(a-x[n]); x[n]=a; miss[n]=0; T[n].append((a,r))
                last=j if w<=9 else j      # merged blobs may be shared
            if miss[n]>12: alive.discard(n)
        if not alive: break
    return {n:np.array(t) for n,t in T.items()}
