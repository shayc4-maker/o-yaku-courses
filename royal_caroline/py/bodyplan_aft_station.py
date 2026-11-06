# One aft station: points (10 mm, from bodyplan_aft_upper_v1.json) + top point found by tracking the ink up to the transom diagonal
import sys,json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import bodyplan_points_all as B, bodyplan_aft_upper_points as P
n=int(sys.argv[1]); c=B.CFG['aft']; g=c['g']
pts=json.load(open('data/bodyplan_aft_upper_v1.json'))[str(n)]
y0,z0=pts[-1]; x,r=B.px(c,y0,z0); x=float(x); r=int(round(r)); slope=-0.17; tr=[]
while r>400:
    r-=1; xp=x+slope; w=g[r,int(xp)-4:int(xp)+5]; idx=np.where(w>90)[0]
    if len(idx)==0: break
    rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); q=min(rs,key=lambda q:abs(q.mean()-4))
    if len(q)>8: tr.append((r,x,0)); x=xp; continue
    xc=int(xp)-4+(q*w[q]).sum()/w[q].sum()
    if abs(xc-x)>2.0 and len(tr)>5: break          # runs onto the diagonal
    slope=0.85*slope+0.15*(xc-x); x=xc; tr.append((r,x,1))
good=[t for t in tr if t[2]==1]; rt,xt=good[-1][0],good[-1][1]
top=B.mm(c,xt,rt); print('top row',rt,'x',round(xt,1),'-> Y %.2f Z %.2f'%top)
pts=pts+[[round(top[0],2),round(top[1],2)]]; json.dump(pts,open(f'data/st{n:02d}_points.json','w'))
for i,p in enumerate(pts,1): print(i,p)
box=(1450,420,2400,2300); im=Image.open('plans/plan_1a_aligned.png').convert('RGB').crop(box)
fig,ax=plt.subplots(figsize=(9,15.5),dpi=110); ax.imshow(im,extent=(box[0],box[2],box[3],box[1]))
p=np.array(pts); a,b=B.px(c,p[:,0],p[:,1]); ax.plot(a,b,'o',mfc='none',mec='r',ms=7,mew=1.2)
for i,(xx,yy) in enumerate(zip(a,b)): ax.text(xx+8,yy,f'{i+1}  Y{p[i,0]:.1f} Z{p[i,1]:.1f}',color='r',fontsize=7,va='center')
ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig(f'qa/bodyplan_st{n:02d}_points.png',bbox_inches='tight')
