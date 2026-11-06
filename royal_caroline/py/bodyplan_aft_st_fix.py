# helper for aft stations: snap a point to the k-th line from the left at its row, track a line up from a seed point and intersect it with the transom diagonal
import json,numpy as np
import bodyplan_points_all as B
c=B.CFG['aft']; g=c['g']; k=c['k']
DIAG=(-0.803,2043.0)       # row = m*x + b (fit on the rib tops, resid 1.6 px)
def runs(r,x0=1400,x1=2330):
    w=g[r,x0:x1]; idx=np.where(w>90)[0]; rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1)
    return [x0+(q*w[q]).sum()/w[q].sum() for q in rs]
def snap_rank(p,rank):
    x,r=B.px(c,*p); r=int(round(r)); rr=runs(r); xn=rr[rank-1]; return list(map(float,B.mm(c,xn,r)))
def centre(r,xc,hw=5):
    w=g[r,int(xc)-hw:int(xc)+hw+1]; idx=np.where(w>90)[0]
    if len(idx)==0: return None
    q=min(np.split(idx,np.where(np.diff(idx)>1)[0]+1),key=lambda q:abs(q.mean()-hw)); return int(xc)-hw+(q*w[q]).sum()/w[q].sum()
def track_up(p,rmin=640):
    x,r=B.px(c,*p); r=int(round(r)); x=centre(r,x,8); T=[(r,x)]; slope=0.0
    while r>rmin:
        r-=1; xc=centre(r,x+slope,4)
        if xc is None or abs(xc-(x+slope))>3: x=x+slope; continue
        slope=0.9*slope+0.1*(xc-x); x=xc; T.append((r,x))
    return np.array(T)
def top_junction(T,rows=(730,800)):
    sel=T[(T[:,0]>=rows[0])&(T[:,0]<=rows[1])]; a2,b2=np.polyfit(sel[:,0],sel[:,1],1); m,b=DIAG
    row=(m*b2+b)/(1-m*a2); xs=a2*row+b2; return list(map(float,B.mm(c,xs,row))),(xs,row)
