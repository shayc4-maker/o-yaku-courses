import sys,json,numpy as np
from PIL import Image
S=sys.argv[1]
a=1-np.array(Image.open(S+'/a/plan_1b_aligned.png').convert('L')).astype(float)/255; B=a>0.5
meta=json.load(open(S+'/out/meta.json')); K=meta['K']; WLZ=meta['WLZ_mm']
st=np.load(S+'/out/stations.npy',allow_pickle=True).item()
PV=[4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28]
def runs(col,off):
    rr=[];s=None
    for j,v in enumerate(col):
        if v and s is None: s=j
        if not v and s is not None: rr.append(((s+j-1)/2+off,j-s)); s=None
    return rr
# centre lines: find the two long horizontal lines near y 1150-1250 at many x
xs=np.arange(4300,10400,50); lo=[];up=[]
for x in xs:
    r=[c for c,w in runs(B[1140:1260,x],1140) if w<=6]
    if len(r)<2: continue
    lo.append((x,max(r))); up.append((x,sorted(r)[-2]))
lo=np.array(lo); up=np.array(up)
def rfit(a):
    m=np.ones(len(a),bool)
    for _ in range(3):
        f=np.polyfit(a[m,0],a[m,1],1); r=a[:,1]-np.polyval(f,a[:,0]); m=abs(r)<2
    return f
lo=rfit(lo); up=rfit(up)
print('lower line y=%.5f x + %.1f ; upper %.5f x + %.1f ; sep %.1f'%(lo[0],lo[1],up[0],up[1],np.polyval(lo,7000)-np.polyval(up,7000)))
def yat(P,z):
    # outermost Y at height z
    out=[]
    for i in range(len(P)-1):
        z0,z1=P[i,1],P[i+1,1]
        if (z0-z)*(z1-z)<=0 and z0!=z1:
            t=(z-z0)/(z1-z0); out.append(P[i,0]+t*(P[i+1,0]-P[i,0]))
    return max(out) if out else None
rows=[]
WLN=['I','II','III','IV','V','VI','VII']
print('st  '+'  '.join('%8s'%n for n in WLN)+'   (body-plan hb mm / diff plan-body px wrt lower CL)')
for i,x in enumerate(PV):
    s=18-i; P=st.get(f'{s}_1a', st.get(f'{s}_1b'))
    cl=np.polyval(lo,x)
    obs=[]
    for dx in (-8,8):
        obs+= [cl-c for c,w in runs(B[200:1170,int(round(x+dx))],200) if w>=2]
    obs=np.array(obs); line=[]
    for n in WLN:
        y=yat(P,WLZ[n]); 
        if y is None: line.append('    --   '); continue
        pred=y/K
        d=obs-pred; j=np.argmin(abs(d))
        dd=np.median([v for v in d if abs(v-d[j])<3]) if abs(d[j])<45 else np.nan
        rows.append((s,n,y,pred,dd)); line.append('%5.1f/%+5.1f'%(y,dd))
    print('%2d '%s+' '.join(line))
json.dump(rows,open(S+'/out/cmp_rows.json','w'))
d=np.array([r[4] for r in rows if not np.isnan(r[4])]); print('all diffs px: median %.1f  IQR %.1f..%.1f'%(np.median(d),*np.percentile(d,[25,75])))
