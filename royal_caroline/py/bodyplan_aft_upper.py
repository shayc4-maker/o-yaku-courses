# Aft body plan A1/2, upper part: stations identified by line order counted from the right (18, 17, 16 ...) row by row; wide runs (crossing lines) rejected
import json,numpy as np
from scipy.signal import medfilt
import bodyplan_points_all as B
c=B.CFG['aft']; g=c['g']; k=c['k']
RTOP,RBOT=520,1300
def runs(r,x0=1400,x1=2300,maxw=10):
    w=g[r,x0:x1]; idx=np.where(w>90)[0]
    if len(idx)==0: return []
    rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1)
    return [x0+(q*w[q]).sum()/w[q].sum() for q in rs if len(q)<=maxw]
def columns():
    rows=np.arange(RTOP,RBOT,2); X={n:np.full(len(rows),np.nan) for n in range(8,19)}
    for i,r in enumerate(rows):
        rr=runs(r)[::-1]
        for j,a in enumerate(rr[:11]): X[18-j][i]=a
    return rows,X
if __name__=='__main__':
    rows,X=columns()
    for n in range(10,19):
        x=X[n]; ok=~np.isnan(x); print(n,'valid rows',ok.sum(),'of',len(rows))
    np.save('/tmp/claude-0/x/aft_cols.npy',{'rows':rows,'X':X},allow_pickle=True)
