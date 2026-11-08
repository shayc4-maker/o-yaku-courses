# aft parts (sternpost, rudder parts): replace the approved edges that correspond to the builder's horizontal / parallel / inclined lines by those lines (neighbour edges re-intersected, shared vertices of other parts moved with them); 2D check
import json,numpy as np
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
PR=json.load(open('data/step44_profiles.json')); F4=json.load(open('data/keel_full_2d_v4.json')); NEW={int(k):np.array(v) for k,v in F4['aft'].items()}
unit=lambda d:d/np.hypot(*d); ang=lambda d:np.degrees(np.arctan2(d[1],d[0]))
def clean(P):
    P=np.array(P); P=P[np.r_[True,np.any(np.diff(P,axis=0)!=0,axis=1)]]
    if np.hypot(*(P[0]-P[-1]))<1e-9: P=P[:-1]
    return P
PARTS={}
for k,v in PR.items():
    for j,q in enumerate(v):
        P=clean(q)
        if P[:,0].min()<20 and np.ptp(P[:,0])<700 and len(P)<200: PARTS['%s#%d'%(k,j)]=P
print('aft parts considered:',{k:len(v) for k,v in PARTS.items()})
def inter(p0,d0,p1,d1):
    A=np.array([d0,-d1]).T
    if abs(np.linalg.det(A))<1e-6: return None
    t=np.linalg.solve(A,p1-p0); return p0+d0*t[0]
moves=[]      # (old vertex, new vertex)
OUT={k:v.copy() for k,v in PARTS.items()}
report=[]
for i,L in NEW.items():
    a,b=L; d=unit(b-a); m=(a+b)/2; best=None
    for k,P in PARTS.items():
        for e in range(len(P)):
            p,q=P[e],P[(e+1)%len(P)]
            if np.hypot(*(q-p))<1.5: continue
            de=unit(q-p); dang=abs((ang(d)-ang(de)+90)%180-90); em=(p+q)/2; off=abs((em-m)[0]*(-d[1])+(em-m)[1]*d[0])
            # his segment must lie along the edge (projection overlap) and be close
            if np.hypot(*(em-m))<14 and dang<12 and off<1.0:
                sc=off+0.3*dang
                if best is None or sc<best[0]: best=(sc,k,e,dang,off)
    if best is None: report.append((i,'no matching approved edge')); continue
    _,k,e,dang,off=best; P=OUT[k]; n=len(P); i0,i1=e,(e+1)%n; pprev=P[(e-1)%n]; pnext=P[(e+2)%n]
    new0=inter(a,d,pprev,unit(P[i0]-pprev)) if True else None; new1=inter(a,d,pnext,unit(P[i1]-pnext))
    # when a neighbour edge is almost parallel to the new line, project the vertex onto the line instead
    def proj(p): return a+d*np.dot(p-a,d)
    if new0 is None or np.hypot(*(new0-P[i0]))>6: new0=proj(P[i0])
    if new1 is None or np.hypot(*(new1-P[i1]))>6: new1=proj(P[i1])
    moves.append((P[i0].copy(),new0)); moves.append((P[i1].copy(),new1))
    report.append((i,k,e,round(dang,2),round(off,3),round(float(np.hypot(*(new0-P[i0]))),3),round(float(np.hypot(*(new1-P[i1]))),3)))
# apply the moves to every part (shared vertices move together)
moved=0
for old,new in moves:
    for k,P in OUT.items():
        for j in range(len(P)):
            if np.hypot(*(P[j]-old))<0.06: P[j]=new; moved+=1
print('vertex moves applied (incl. shared vertices of neighbouring parts): %d'%moved)
for r in report: print('#%s -> %s'%(r[0],r[1:]))
print()
for k in PARTS:
    A0=Polygon(PARTS[k]); A1=Polygon(OUT[k]); dv=np.hypot(*(OUT[k]-PARTS[k]).T).max()
    print('%-22s valid before %s after %s | area %.1f -> %.1f mm2 | max vertex shift %.3f mm'%(k,A0.is_valid,A1.is_valid,A0.area,A1.area,dv))
json.dump({k:v.tolist() for k,v in OUT.items()},open('data/aft_parts_2d_v1.json','w'))
fig,axs=plt.subplots(1,2,figsize=(22,13))
for a_,(x0,x1,z0,z1) in zip(axs,((-36,15,-12,92),(-20,8,40,82))):
    for k in PARTS:
        P0=np.vstack([PARTS[k],PARTS[k][:1]]); P1=np.vstack([OUT[k],OUT[k][:1]]); a_.plot(P0[:,0],P0[:,1],color='0.65',lw=1); a_.plot(P1[:,0],P1[:,1],color='tab:red',lw=1.2)
    for i,L in NEW.items(): a_.plot(L[:,0],L[:,1],color='tab:blue',lw=2.2,alpha=.8)
    a_.set_xlim(x0,x1); a_.set_ylim(z0,z1); a_.set_aspect('equal'); a_.grid(alpha=.3)
axs[0].set_title('aft parts: grey = approved, red = with the builder lines (blue) replacing the matching edges')
fig.savefig('qa/aft_parts_2d_v1.png',dpi=55,bbox_inches='tight')
