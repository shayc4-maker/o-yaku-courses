import sys,json,numpy as np
from PIL import Image
S=sys.argv[1]
a=1-np.array(Image.open(S+'/a/plan_1b_aligned.png').convert('L')).astype(float)/255; B=a>0.5
meta=json.load(open(S+'/out/meta.json')); K=meta['K']; WLZ=meta['WLZ_mm']
st=np.load(S+'/out/stations.npy',allow_pickle=True).item()
PV=[4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28]
LO=(-0.00716,1271.3); UP=(-0.00649,1232.6)
def runs(col,off):
    rr=[];s=None
    for j,v in enumerate(col):
        if v and s is None: s=j
        if not v and s is not None: rr.append(((s+j-1)/2+off,j-s)); s=None
    return rr
def ycross(P,z):
    out=[]
    for i in range(len(P)-1):
        z0,z1=P[i,1],P[i+1,1]
        if (z0-z)*(z1-z)<=0 and z0!=z1:
            t=(z-z0)/(z1-z0); out.append((P[i,0]+t*(P[i+1,0]-P[i,0]), P[i+1]-P[i]))
    if not out: return None
    return max(out,key=lambda t:t[0])
def align(pred,obs):
    # order-preserving injective map pred->obs minimising |diff|; both sorted desc
    n,m=len(pred),len(obs); INF=1e9
    D=np.full((n+1,m+1),INF); D[0,:]=0; bk={}
    for i in range(1,n+1):
        for j in range(i,m+1):
            a=D[i,j-1]; b=D[i-1,j-1]+abs(pred[i-1]-obs[j-1])
            D[i,j]=min(a,b); bk[(i,j)]= 'skip' if a<=b else 'take'
    i,j=n,int(np.argmin(D[n])); res=[None]*n
    while i>0:
        if bk[(i,j)]=='take': res[i-1]=obs[j-1]; i-=1; j-=1
        else: j-=1
    return res
WLN=['I','II','III','IV','V','VI','VII']; rows=[]
print('diff = plan view - body plan, model mm (normal deviation in brackets)')
print('st '+''.join('%14s'%n for n in WLN))
for i,x in enumerate(PV):
    s=18-i; P=st.get(f'{s}_1a', st.get(f'{s}_1b'))
    cl=np.polyval(LO,x); ul=np.polyval(UP,x)
    ob=[]
    for dx in (-8,8):
        r=[cl-c for c,w in runs(B[250:int(ul)-3,int(round(x+dx))],250) if w>=2]
        ob.append(sorted(r,reverse=True))
    preds=[];names=[]
    for n in WLN:
        yc=ycross(P,WLZ[n])
        if yc is not None and yc[0]>3.3: preds.append(yc); names.append(n)
    order=np.argsort([-p[0] for p in preds])
    pv=[preds[k][0]/K for k in order]
    res=[]
    for o in ob:
        if len(o)>=len(pv): res.append(align(pv,o))
    line={}
    for jj,k in enumerate(order):
        vals=[r[jj] for r in res if r[jj] is not None]
        if not vals: continue
        obs=np.mean(vals); d=(obs-pv[jj])*K
        t=preds[k][1]; t=t/np.linalg.norm(t); nd=d*abs(t[1])   # normal dev = dY * |dz/ds|
        line[names[k]]=(d,nd); rows.append(dict(st=s,wl=names[k],body_mm=preds[k][0],plan_mm=obs*K,d=d,nd=nd))
    print('%2d '%s+''.join(('%+6.2f(%+5.2f)'%line[n] if n in line else '%14s'%'--') for n in WLN))
json.dump(rows,open(S+'/out/cmp_rows.json','w'),indent=0)
d=np.array([r['d'] for r in rows]); nd=np.array([r['nd'] for r in rows])
print('N=%d  dY mm: median %+.2f rms %.2f | normal dev mm: median %+.2f rms %.2f, |nd|>0.3: %d, >0.5: %d'%(len(d),np.median(d),np.sqrt((d**2).mean()),np.median(nd),np.sqrt((nd**2).mean()),(abs(nd)>0.3).sum(),(abs(nd)>0.5).sum()))
