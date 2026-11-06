import json,numpy as np
from scipy.signal import medfilt
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import bodyplan_points_all as B, bodyplan_aft_upper as U
c=U.c; rows,X=U.columns(); V2=json.load(open('data/bodyplan_points_v2.json')); AP=json.load(open('data/bodyplan_points_approved.json'))
def clean_rows():
    cnt=np.array([len(U.runs(r)) for r in rows]); mode=np.array([np.bincount(cnt[max(i-8,0):i+9]).argmax() for i in range(len(rows))])
    return cnt==mode
CL=clean_rows()
def centreline(n):
    x=X[n].copy(); ok=(~np.isnan(x))&CL
    # outliers against a running median of the clean samples
    r=rows[ok].astype(float); xv=x[ok]; m=medfilt(xv,9); g=np.abs(xv-m)<4; r=r[g]; xv=xv[g]
    # top: stop where the line turns onto the transom diagonal (|dx/drow|>0.8 over 10 rows)
    o=np.argsort(-r); r=r[o]; xv=xv[o]; stop=len(r)
    for i in range(10,len(r)):
        if abs(xv[i]-xv[i-10])/max(r[i-10]-r[i],1)>0.8: stop=i-10; break
    r=r[:stop]; xv=xv[:stop]
    from scipy.interpolate import UnivariateSpline
    o=np.argsort(r); sp=UnivariateSpline(r[o],xv[o],k=3,s=len(r)*0.8)
    rr=np.arange(r.max(),r.min()-1,-1.0); return sp(rr),rr
def pts(n):
    x,r=centreline(n); Y,Z=B.mm(c,x,r); s=np.r_[0,np.cumsum(np.hypot(np.diff(Y),np.diff(Z)))]
    up=[(Y[np.argmin(abs(s-t))],Z[np.argmin(abs(s-t))]) for t in np.arange(0,s[-1]-3,10.0)]+[(Y[-1],Z[-1])]
    zlim=Z[0]-5; low=[tuple(p) for p in V2[str(n)]['points'] if p[1]<zlim]
    return low+up,len(low)
if __name__=='__main__':
    NEW={}
    for n in range(10,19):
        p,nl=pts(n); NEW[n]=p
        if str(n) in AP:   # validation against approved stations
            a=np.array(AP[str(n)]); d=[np.min(np.hypot(*(a-np.array(q)).T)) for q in p[nl:]]; print(n,'vs approved: max dist of new upper points to approved points %.2f mm'%max(d))
    json.dump({str(k):[[round(a,2),round(b,2)] for a,b in v] for k,v in NEW.items()},open('data/bodyplan_aft_upper_v1.json','w'))
    box=(1250,420,2400,2300); im=Image.open('plans/plan_1a_aligned.png').convert('RGB').crop(box)
    fig,ax=plt.subplots(figsize=(11,18),dpi=110); ax.imshow(im,extent=(box[0],box[2],box[3],box[1])); cm=plt.get_cmap('tab10')
    for n in (10,11,12,14,15):
        p=np.array(NEW[n]); a,b=B.px(c,p[:,0],p[:,1]); ax.plot(a,b,'o',mfc='none',mec=cm(n%10),ms=5,mew=1.1); ax.text(a[-1],b[-1]-18,str(n),color=cm(n%10),fontsize=12,weight='bold',ha='center')
    ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig('qa/bodyplan_aft_10-15_points.png',bbox_inches='tight')
