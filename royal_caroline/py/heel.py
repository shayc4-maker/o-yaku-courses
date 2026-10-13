import sys,numpy as np
from PIL import Image
def B(p): return np.array(Image.open(p).convert('L'))<128
def runs(v,off):
    out=[];s=None
    for i,b in enumerate(v):
        if b and s is None: s=i
        if not b and s is not None: out.append(((s+i-1)/2+off,i-s)); s=None
    return out
S=sys.argv[1]
a=B(S+'/a/plan_1a_aligned.png')
# 1a: post aft edge = leftmost dark run in x 3950..4300 for rows 1300..2200 (excluding horizontal WLs rows)
pts=[]
for y in range(1150,2200,5):
    r=[c for c,w in runs(a[y,3980:4300],3980) if w<=8]
    if r: pts.append((y,r[0]))
pts=np.array(pts); f=np.polyfit(pts[:,0],pts[:,1],1); res=pts[:,1]-np.polyval(f,pts[:,0]); m=abs(res)<3; f=np.polyfit(pts[m,0],pts[m,1],1)
# keel bottom 1a
kb=[]
for x in range(4400,9000,200):
    r=[c for c,w in runs(a[2150:2260,x],2150)]; kb.append(max(r))
kb=np.median(kb); print('1a post line x=%.4f*y+%.1f  keel bottom y=%.1f  heel x=%.1f'%(f[0],f[1],kb,np.polyval(f,kb)))
# foremost point 1a: max x of dark in rows 800..1300 beyond 11000
xs=[(y,np.where(a[y,10500:])[0].max()+10500) for y in range(800,1300) if a[y,10500:].any()]
y,x=max(xs,key=lambda t:t[1]); print('1a foremost',x,y)
b=B(S+'/a/plan_5_aligned.png')
pts=[]
for y in range(1650,2040,4):
    r=[c for c,w in runs(b[y,1180:1320],1180) if 3<=w<=10]
    if r: pts.append((y,r))
print('p5 rows sample',pts[::15][:8])
kb5=[]
for x in range(2000,6500,250):
    col=b[1950:2150,x]; ys=np.where(col)[0]; kb5.append(ys.max()+1950)
print('p5 keel bottom samples',kb5)
xs=[(y,np.where(b[y,8000:])[0].max()+8000) for y in range(600,1100) if b[y,8000:].any()]
y,x=max(xs,key=lambda t:t[1]); print('p5 foremost',x,y)
