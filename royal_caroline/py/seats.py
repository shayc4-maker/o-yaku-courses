import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
S=sys.argv[2]
d=np.load(S+'/out/cls_keel.npz'); cross=d['cross'].astype(np.uint8); u0,v0=int(d['u0']),int(d['v0'])
a=1-np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L')).astype(np.float32)/255
cross=cv2.morphologyEx(cross,cv2.MORPH_OPEN,np.ones((5,5),np.uint8)); cross=cv2.morphologyEx(cross,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8))
n,lab,st,cen=cv2.connectedComponentsWithStats(cross)
fx=json.load(open(S+'/out/frames_X.json'))['X_mm']
out=[]
for i,x in enumerate(fx,1):
    if i==25: continue
    u,_=model_to_p5(x,0); j=int(u)-u0
    _,vlo=model_to_p5(x,-3); _,vhi=model_to_p5(x,60)
    cands=[]
    for l in set(lab[int(vhi)-v0:int(vlo)-v0,j-2:j+3].ravel())-{0}:
        xs,ys,w,h,A=st[l]
        if 30<w<90 and h>25 and A>1200: cands.append((ys+h,l))
    if not cands: out.append(dict(frame=i,x=x)); continue
    yb,l=max(cands)              # lowest block
    xs,ys,w,h,A=st[l]; m=lab[ys:ys+h,xs:xs+w]==l
    cols=np.arange(w//4,3*w//4); bot=np.median([np.where(m[:,c])[0].max() for c in cols]); top=np.median([np.where(m[:,c])[0].min() for c in cols])
    X0,_=p5_to_model(xs+u0,0); X1,_=p5_to_model(xs+w+u0,0)
    zb=float(p5_to_model(0,ys+bot+v0)[1]); zt=float(p5_to_model(0,ys+top+v0)[1])
    out.append(dict(frame=i,x=x,bx0=float(X0),bx1=float(X1),zb=zb,zt=zt))
# gaps: start inside white strip at mid-height of neighbour blocks, walk down/up
D=cv2.blur(a,(5,1))
for k in range(len(out)-1):
    A_,B_=out[k],out[k+1]
    if 'zb' not in A_ or 'zb' not in B_: continue
    xg=(A_['bx1']+B_['bx0'])/2; u,_=model_to_p5(xg,0); u=int(u)
    zm=(max(A_['zb'],B_['zb'])+min(A_['zt'],B_['zt']))/2; _,v=model_to_p5(xg,zm); v=int(v)
    colm=a[:,u-4:u+5].mean(1)
    # white strip contains thin horizontal lines; treat rows with mean<0.55 as 'open'
    r=v
    while colm[r]<0.55 or colm[r+1]<0.55 or colm[r+2]<0.55: r+=1
    rb=r
    r=v
    while colm[r]<0.55 or colm[r-1]<0.55 or colm[r-2]<0.55: r-=1
    A_['gap_after']=dict(x=float(xg),zbot=float(p5_to_model(0,rb)[1]),ztop=float(p5_to_model(0,r)[1]))
for o in out: print(o['frame'],round(o['x'],1),{k:(round(v,1) if isinstance(v,float) else {kk:round(vv,1) for kk,vv in v.items()}) for k,v in o.items() if k not in('frame','x')})
json.dump(out,open(S+'/out/seats_auto.json','w'))
