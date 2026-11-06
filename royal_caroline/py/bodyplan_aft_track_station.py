# Aft station n: keep points up to a seed point, then follow the ink centre upward (10 mm arc points) to the transom diagonal; check every point sits on ink
import sys,json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import bodyplan_points_all as B
n=int(sys.argv[1]); seed=int(sys.argv[2]); c=B.CFG['aft']; g=c['g']
src=json.load(open('data/bodyplan_aft_upper_v1.json'))[str(n)]; pts=[[float(a),float(b)] for a,b in src[:seed]]
def ink_dev(y,z):
    x,r=B.px(c,y,z); r=int(round(r)); w=g[r,int(x)-9:int(x)+10]; idx=np.where(w>90)[0]
    if len(idx)==0: return None
    q=min(np.split(idx,np.where(np.diff(idx)>1)[0]+1),key=lambda q:abs(q.mean()-9)); return (int(x)-9+(q*w[q]).sum()/w[q].sum()-x)*c['k']
y0,z0=pts[-1]; x,r=B.px(c,y0,z0); r=int(round(r)); x=float(x)
w=g[r,int(x)-8:int(x)+9]; idx=np.where(w>90)[0]; q=min(np.split(idx,np.where(np.diff(idx)>1)[0]+1),key=lambda q:abs(q.mean()-8)); x=int(x)-8+(q*w[q]).sum()/w[q].sum()
xa,ra=B.px(c,*pts[-2]); xb,rb=B.px(c,*pts[-1]); slope=float((xb-xa)/(rb-ra))*-1.0*-1.0 if False else float((xa-xb)/(ra-rb))*-1.0
tr=[(r,x)]; miss=0
while r>600:
    r-=1; xp=x+slope; w=g[r,int(xp)-4:int(xp)+5]; idx=np.where(w>90)[0]
    if len(idx)==0:
        miss+=1; x=xp
        if miss>12: break
        continue
    rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); q=min(rs,key=lambda q:abs(q.mean()-4))
    if len(q)>8: x=xp; continue
    xc=int(xp)-4+(q*w[q]).sum()/w[q].sum()
    if abs(xc-xp)>4.0: miss+=1; x=xp; 
    if abs(xc-xp)>4.0:
        if miss>12: break
        continue
    miss=0
    slope=0.9*slope+0.1*(xc-x); x=xc; tr.append((r,x))
tr=np.array(tr); Y,Z=B.mm(c,tr[:,1],tr[:,0]); s=np.r_[0,np.cumsum(np.hypot(np.diff(Y),np.diff(Z)))]
# top = last row where the local slope still agrees with the slope of the preceding 40 rows (the diagonal has a very different slope)
xs=tr[:,1]; end=len(tr)-1
for i in range(46,len(tr)):
    ref=(xs[i-6]-xs[i-46])/40; loc=(xs[i]-xs[i-6])/6
    if abs(loc-ref)>0.35: end=i-7; break
up=[(Y[np.argmin(abs(s-t))],Z[np.argmin(abs(s-t))]) for t in np.arange(10,s[end]-3,10.0)]+[(Y[end],Z[end])]
pts+= [[round(a,2),round(b,2)] for a,b in up]; json.dump(pts,open(f'data/st{n:02d}_points_v2.json','w'))
print('track rows',int(tr[0,0]),'->',int(tr[end,0]),'top Y %.2f Z %.2f'%(Y[end],Z[end]))
for i,p in enumerate(pts,1):
    d=ink_dev(*p); print(i,p,'ink offset %s'%('%.2f mm'%d if d is not None else 'no ink'))
for nm,box,fs,out in (('full',(1450,420,2400,2300),(9,15.5),f'qa/bodyplan_st{n:02d}_points.png'),('top',(1560,560,1820,1000),(7,12),f'qa/bodyplan_st{n:02d}_top_zoom.png')):
    im=Image.open('plans/plan_1a_aligned.png').convert('RGB').crop(box)
    fig,ax=plt.subplots(figsize=fs,dpi=110); ax.imshow(im,extent=(box[0],box[2],box[3],box[1]))
    p=np.array(pts); a,b=B.px(c,p[:,0],p[:,1]); ax.plot(a,b,'o',mfc='none',mec='r',ms=7 if nm=='full' else 6,mew=1.2)
    for i,(xx,yy) in enumerate(zip(a,b)):
        if nm=='full' or yy<1000: ax.text(xx+8,yy,f'{i+1}  Y{p[i,0]:.1f} Z{p[i,1]:.1f}',color='r',fontsize=7 if nm=='full' else 9,va='center')
    ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig(out,bbox_inches='tight'); plt.close(fig)
