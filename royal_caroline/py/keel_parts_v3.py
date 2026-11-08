# closed profiles of all 18 keel-group parts from the builder's lines: stem-front runs of the 5 parts and keel-top/stem-inner run of the keel/stem part replaced by the new chains; keelson rebuilt from its chains; aft parts from the polygonized lines; the rest unchanged
import json,pickle,numpy as np
from shapely.geometry import Polygon,LineString,Point
from shapely import wkt
from shapely.ops import unary_union
S=json.load(open('data/keel_lines_builder_v3d.json')); PR=json.load(open('data/step44_profiles.json'))
ch={}
for ln,P,nm,t in S:
    if ln in('01','02','03','04') and t=='NurbsCurve':
        P=np.array(P)
        if ln not in ch or len(P)>0 and np.sum(np.hypot(*np.diff(P,axis=0).T))>np.sum(np.hypot(*np.diff(ch[ln],axis=0).T)): ch[ln]=P
c01,c02,c03,c04=ch['01'],ch['02'],ch['03'],ch['04']
def rs(C,step=0.8):
    s=np.r_[0,np.cumsum(np.hypot(*np.diff(C,axis=0).T))]; q=np.arange(0,s[-1],step); q=np.r_[q,s[-1]]; return np.c_[np.interp(q,s,C[:,0]),np.interp(q,s,C[:,1])]
def idx_near(C,p): return int(np.argmin(np.hypot(*(C-p).T)))
def seg(C,p0,p1):
    i,j=idx_near(C,p0),idx_near(C,p1); out=C[i:j+1] if i<=j else C[j:i+1][::-1]; return out
old={}
for k,v in PR.items():
    q=np.array(max(v,key=lambda q:Polygon(q).area)); old[k]=q[np.r_[True,np.any(np.diff(q,axis=0)!=0,axis=1)]]
    if np.hypot(*(old[k][0]-old[k][-1]))<1e-9: old[k]=old[k][:-1]
newP={k:v.copy() for k,v in old.items()}; notes=[]
# ---- stem-front runs (parts sharing the old stem front line)
front_old=old['Boss-Extrude2[2]'][405:467]          # old stem front vertices (516.71,12.58) .. (567.99,116.59)
def replace_run(P,mask,chain,name):
    n=len(P); idx=np.where(mask)[0]
    if len(idx)<2: return P
    # contiguous cyclic run
    runs=[]; cur=[idx[0]]
    for a in idx[1:]:
        if a==cur[-1]+1: cur.append(a)
        else: runs.append(cur); cur=[a]
    runs.append(cur)
    if len(runs)>1 and runs[0][0]==0 and runs[-1][-1]==n-1: runs[0]=runs[-1]+runs[0]; runs.pop()
    run=max(runs,key=len); s,e=run[0],run[-1]; a,b=P[s],P[e]
    piece=seg(chain,a,b); 
    if np.hypot(*(piece[0]-a))>np.hypot(*(piece[-1]-a)): piece=piece[::-1]
    piece=rs(piece,0.8); keep=[i for i in range(n) if i not in set(run)]
    # polygon in order: vertices after e ... before s, then the chain from a-side to b-side
    after=[(e+1+k)%n for k in range(n-len(run))]; out=np.vstack([P[after],piece[::-1]]) if False else None
    rest=np.array([P[(e+1+k)%n] for k in range(n-len(run))]); newp=np.vstack([piece,rest])    # chain from a (start of run) to b (end of run) then the rest of the polygon after b
    notes.append('%s: run of %d vertices (%.2f,%.2f)->(%.2f,%.2f) replaced by %d chain points (end moves %.3f / %.3f mm)'%(name,len(run),a[0],a[1],b[0],b[1],len(piece),np.hypot(*(piece[0]-a)),np.hypot(*(piece[-1]-b)))); return newp
for k in ('Boss-Extrude2[2]','Boss-Extrude2[1]','Boss-Extrude5[1]','Boss-Extrude5[2]','Boss-Extrude6'):
    P=old[k]; mask=np.array([np.min(np.hypot(*(front_old-p).T))<0.06 for p in P])
    if k=='Boss-Extrude2[2]': mask[:405]=False; mask[467:]=False
    newP[k]=replace_run(P,mask,c04,k)
# ---- keel/stem part: keel top + stem inner run replaced by chain 01
P=newP['Boss-Extrude2[2]']; n=len(P)
iA0=int(np.argmin(np.hypot(*(P-np.array([556.87,111.12])).T))); iA1=int(np.argmin(np.hypot(*(P-np.array([45.2,10.07])).T)))
run=[(iA0+k)%n for k in range(((iA1-iA0)%n)+1)]; rest=np.array([P[(iA1+1+k)%n] for k in range(n-len(run))])
# pockets: 1 mm deep, floor parallel to the surface (walls along the surface normal), X-4..X+4 of every frame; clean chain elsewhere
XF=json.load(open('data/frames_X.json'))['X_mm']; DEPTH_P=1.0
def pocketed(c):
    c=c[np.argsort(c[:,0])] if False else c                 # stern -> stem order
    keel=c[c[:,0]<=526.49]; rest=c[c[:,0]>526.49]
    d=np.gradient(keel,axis=0); d/=np.hypot(*d.T)[:,None]; nrm=np.c_[-d[:,1],d[:,0]]               # up/left normal of a curve running stern->stem
    if nrm[len(nrm)//2,1]<0: nrm=-nrm
    X=keel[:,0]; out=[]; i=0; n=len(keel); pk=[]
    for b in range(1,45):
        xc=XF[45-b]; a_,b_=max(xc-4,46.0),min(xc+4,526.48)
        if b_-a_>1.0: pk.append((a_,b_))
    pk.sort()
    cur=0
    for a_,b_ in pk:
        ia=min(int(np.searchsorted(X,a_)),n-2); ib=min(int(np.searchsorted(X,b_)),n-1)
        out+=list(keel[cur:ia]); out.append(keel[ia]); out.append(keel[ia]-DEPTH_P*nrm[ia])
        out+=[keel[j]-DEPTH_P*nrm[j] for j in range(ia+1,ib)]
        out.append(keel[ib]-DEPTH_P*nrm[ib]); out.append(keel[ib]); cur=ib+1
    out+=list(keel[cur:]); out+=list(rest)
    return np.array(out),len(pk)
POCK=int(__import__('os').environ.get('POCKETS','1'))
if POCK:
    pk_chain,npk=pocketed(c01); notes.append('pockets: %d frame pockets cut into the keel top (1.0 mm deep along the normal, X-4..X+4)'%npk); inner=rs(pk_chain[::-1],0.8) if False else pk_chain[::-1]
else:
    inner=rs(c01[::-1],0.8)                                    # top -> stern
newP['Boss-Extrude2[2]']=np.vstack([inner,rest]); notes.append('Boss-Extrude2[2]: keel-top/stem-inner run of %d vertices replaced by chain 01 (%d points)'%(len(run),len(inner)))
# ---- keelson from its chains: cap top -> chain 03 -> C2 -> chain 01 (C2 to C1) -> chain 02 reversed to the cap bottom -> cap
c2=c03[-1]; c1=c02[-1]; capT=c03[0]; i=idx_near(c02,np.array([41.19,34.88])); capB=c02[i]
on01=seg(c01,c2,c1)                                          # C2 -> C1 along the keel-top/stem-inner chain
if np.hypot(*(on01[0]-c2))>np.hypot(*(on01[-1]-c2)): on01=on01[::-1]
und=c02[i:][::-1]                                             # C1 back to the cap bottom
kp=np.vstack([rs(c03,0.8),rs(on01,0.5),rs(und,0.8)]); newP['Boss-Extrude4[4]']=kp; notes.append('Boss-Extrude4[4]: rebuilt from chains 03, 01 (C2->C1), 02; cap bottom (%.2f,%.2f)'%tuple(capB))
# ---- aft parts: polygonized faces from the builder's aft lines (data from py/keel_faces_from_lines_v3.py)
F=[(k,wkt.loads(w)) for k,w in pickle.load(open('/tmp/faces_v4.pkl','rb'))]
def facefor(k,minarea): 
    c=[f for kk,f in F if kk==k and f.area>minarea]; return max(c,key=lambda f:f.area) if c else None
for k in ('Boss-Extrude5[3]','Boss-Extrude3[3]','Split1[2]'):
    f=facefor(k,20)
    if f is not None: newP[k]=np.array(f.exterior.coords)[:-1]; notes.append('%s: from the polygonized aft lines (area %.1f, old %.1f)'%(k,f.area,Polygon(old[k]).buffer(0).area))
# Boss-Extrude4[2] (the rudder end): ring from the builder's own edges (left edge, right edge, cap spline, bottom on Z=-9.37) - the polygonizer could not close it (Split1[1] runs along the same edge)
cap=[np.array(P) for ln,P,nm,t in S if ln=='01' and t=='NurbsCurve' and np.array(P)[:,0].max()<-20 and np.array(P)[:,1].min()>50][0]
if np.hypot(*(cap[0]-np.array([-23.959,56.458])))>np.hypot(*(cap[-1]-np.array([-23.959,56.458]))): cap=cap[::-1]
ring42=np.vstack([[(-20.594,-9.37),(-18.753,-9.37),(-18.773,-9.116),(-23.959,56.458)],cap[1:-1][::4],[(-25.512,56.852),(-20.617,-9.071)]]); p42=Polygon(ring42)
newP['Boss-Extrude4[2]']=ring42; notes.append('Boss-Extrude4[2]: ring from his edges, area %.1f (old %.1f)'%(p42.area,Polygon(old['Boss-Extrude4[2]']).buffer(0).area))
# Split1[1]: polygonized face closed over the thin gap to the new rudder-end ring, then 4[2] removed -> shared edge, no overlap
f11=facefor('Split1[1]',20)
if f11 is not None:
    g=f11.union(p42.buffer(0.0)).buffer(0.5).buffer(-0.5)       # close the thin gaps along the shared edge
    g=g.difference(p42.buffer(1e-4)); g=g.buffer(-0.005).buffer(0.005)
    g=max(g.geoms,key=lambda q:q.area) if hasattr(g,'geoms') else g
    newP['Split1[1]']=np.array(g.exterior.coords)[:-1]; notes.append('Split1[1]: polygonized face closed to the rudder end and minus Boss-Extrude4[2]: area %.1f (old %.1f, face %.1f)'%(g.area,Polygon(old['Split1[1]']).buffer(0).area,f11.area))
for nn in notes: print(nn)
rows=[]
for k,P in newP.items():
    pg=Polygon(P); v=pg.is_valid; pg2=pg if v else pg.buffer(0); rows.append((k,v,pg2.area,Polygon(old[k]).buffer(0).area,pg2))
print()
for k,v,a,a0,pg in rows: print('%-20s valid %-5s area %8.1f  (old %8.1f, %+.1f)'%(k,v,a,a0,a-a0))
pickle.dump({k:pg.wkt for k,v,a,a0,pg in rows},open('/tmp/parts_v3.pkl','wb'))
# overlaps
print('\noverlaps > 0.3 mm2:'); tot=0
for i in range(len(rows)):
    for j in range(i+1,len(rows)):
        o=rows[i][4].intersection(rows[j][4]).area
        if o>0.3: print('  %s x %s : %.2f mm2'%(rows[i][0],rows[j][0],o)); tot+=1
print('number of overlapping pairs:',tot)
