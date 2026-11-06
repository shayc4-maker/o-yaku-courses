# v2: keel-contact points for ST13-17 (ink traced down to the keel line Y~1.1), splines through the points in one colour per station; ST07-09 held back for a separate round
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import splprep,splev
import bodyplan_points_all as B
D=json.load(open('data/bodyplan_points_v1.json')); HOLD=(7,8,9)
def keel_trace(n):
    c=B.CFG['aft']; g=c['g']; p=np.array(D[str(n)]['points'])
    x0,y0=B.px(c,p[0,0],p[0,1]); x1,y1=B.px(c,p[1,0],p[1,1]); slope=(x0-x1)/(y0-y1); x=float(x0); r=int(round(y0)); tr=[(x,r)]
    while r<2140:
        r+=1; xp=x+slope; row=g[r,int(xp)-8:int(xp)+9]
        if row.max()<60: x=xp; continue
        m=row>0.5*row.max(); idx=np.where(m)[0]; rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); rr=min(rs,key=lambda q:abs(q.mean()-8))
        xc=int(xp)-8+(rr*row[rr]).sum()/row[rr].sum(); slope=0.7*slope+0.3*(xc-x); x=xc; tr.append((x,r))
        if (c['cx']-x)*c['k']<=1.15: break
    T=np.array([B.mm(c,a,b) for a,b in tr]); s=np.r_[0,np.cumsum(np.hypot(*np.diff(T,axis=0).T))]
    sel=[T[np.argmin(abs(s-t))] for t in np.arange(10.0,s[-1]-3.0,10.0)]+[T[-1]]
    return sel[::-1]            # bottom-most first? (list runs from the keel contact upwards)
for n in range(13,18):
    ext=keel_trace(n); D[str(n)]['points']=[[round(a,2),round(b,2)] for a,b in ext]+D[str(n)]['points']; D[str(n)]['keel_points']=len(ext)
json.dump(D,open('data/bodyplan_points_v2.json','w'))
COL=plt.cm.tab20(np.linspace(0,1,20))
def plot(ns,box,img,out,figw):
    c=B.CFG[B.which(ns[0])]; im=Image.open(img).convert('RGB').crop(box)
    fig,ax=plt.subplots(figsize=(figw,figw*(box[3]-box[1])/(box[2]-box[0])),dpi=110); ax.imshow(im,extent=(box[0],box[2],box[3],box[1]))
    for n in ns:
        d=D[str(n)]; col=COL[(n*3)%20]; p=np.array(d['points']); st=d['straight_top']
        q=p[:-1] if st else p; tck,_=splprep(q.T,k=3,s=0); yy,zz=splev(np.linspace(0,1,500),tck); x,y=B.px(c,yy,zz); ax.plot(x,y,'-',color=col,lw=1.4)
        if st: x2,y2=B.px(c,p[-2:,0],p[-2:,1]); ax.plot(x2,y2,'-',color=col,lw=1.4)
        a,b=B.px(c,p[:,0],p[:,1]); ax.plot(a,b,'o',mfc='none',mec=col,ms=4,mew=1)
        ax.text(a[-1],b[-1]-18,str(n),color=col,fontsize=11,ha='center',weight='bold')
    ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig(out,bbox_inches='tight'); plt.close(fig)
plot([1,2,3,4,5,6],(2400,500,3500,2150),'plans/plan_1b_aligned.png','qa/bodyplan_lines_fwd.png',12)
plot(range(10,19),(1250,420,2400,2300),'plans/plan_1a_aligned.png','qa/bodyplan_lines_aft.png',11)
print({n:D[str(n)].get('keel_points') for n in range(13,18)})
