# Waterlines II-VII in the plan view (A1/4): ink traced, Y scale calibrated against the approved body plan, points every 20 mm
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.signal import medfilt
import line_follow as LF
img=Image.open('plans/plan_1b_aligned.png'); g=255-np.array(img.convert('L')).astype(float)
A_PX,B_PX=11.7655,4252.5          # px = A*X + B  (station verticals)
T=np.load('/tmp/claude-0/x/wl_traces.npy',allow_pickle=True).item(); cur1=np.load('/tmp/claude-0/x/wl1_px.npy')
cols=np.load('/tmp/claude-0/x/VII_VI_cols.npy')
def clean_cols(x,r):
    ok=~np.isnan(r); x=x[ok]; r=r[ok]; m=medfilt(r,21); g_=np.abs(r-m)<5; return np.c_[x[g_],r[g_]]
WL={}
cut_r=lambda t,xmin: t[:next(i for i in range(len(t)) if t[i,0]>xmin and t[i,1]>=1160)+1]
for k in ('II','III','IV','V'):
    t=T[k]; j=next(i for i in range(len(t)) if t[i,0]>9900 and t[i,1]>=1160); t=t[:j+1]
    iL=np.where(t[:,0]<4262)[0]; 
    if len(iL): i0=iL[-1]; 
    else: i0=0
    # stern: keep from the first point right of x=4262 on the final approach (traces loop around the post: use last index with x<4262 before the main body)
    body=np.where(t[:,0]>4700)[0][0]; pre=t[:body]; k0=np.where(pre[:,0]<=4262)[0]; i0=k0[-1] if len(k0) else 0
    WL[k]=t[i0:]
WL['III']=np.r_[WL['IV'][WL['IV'][:,0]<4513],WL['III'][WL['III'][:,0]>=4513]] if WL['III'][0,0]>4300 else WL['III']
for k,ci in (('VII',1),('VI',2)):
    c=clean_cols(cols[:,0],cols[:,ci]); WL[k]=c
v6=WL['VI']; v6=v6[np.where(v6[:,0]>=4306)[0][0]:]
Ls=LF.follow(g,v6[0,0],v6[0,1],-1,0.3,hw=3,miss_max=8,stop_wide=12,max_steps=300); v6=np.r_[Ls[::-1],v6[1:]]; WL['VI']=v6
for k in ('VI','VII'):
    t=WL[k]; p=t[-25:]; dx,dy=p[-1]-p[0]; R=LF.follow(g,t[-1,0],t[-1,1],dx,dy,hw=3,miss_max=8,stop_wide=12,max_steps=900)
    j=next((i for i in range(len(R)) if R[i,1]>=1160),len(R)-1); WL[k]=np.r_[t,R[1:j+1]]
for k in ('VI',): WL[k]=WL[k][WL[k][:,0]>=4262]
# VI near the stern: the Roman numeral labels (x 5100-5250) broke the column method -> follow the ink instead
Rf=LF.follow(g,4306,1166,1,-0.5,hw=3,miss_max=8,stop_wide=12,max_steps=4000); v=WL['VI']
WL['VI']=np.r_[v[v[:,0]<4306],Rf[(Rf[:,0]>=4306)&(Rf[:,0]<6200)],v[v[:,0]>=6200]]
# bow part of VI/VII re-followed (the Roman numeral labels next to the lines disturbed the column method there)
for k in ('VI','VII'):
    t=WL[k]; t=t[t[:,0]<=9900]; p=t[-25:]; dx,dy=p[-1]-p[0]; R=LF.follow(g,t[-1,0],t[-1,1],dx,dy,hw=3,miss_max=8,stop_wide=12,max_steps=1500)
    j=next((i for i in range(len(R)) if R[i,1]>=1160),len(R)-1); WL[k]=np.r_[t,R[1:j+1]]
for k,v in WL.items(): print(k,len(v),v[0].round(0),v[-1].round(0))

# ---- calibration of Y and points ----
WL['I']=cur1[:next(i for i in range(len(cur1)) if cur1[i,0]>10100 and cur1[i,1]>1150)+1]
for k in WL:
    t=WL[k]; WL[k]=t[t[:,0]>=4262] if k in ('VI','VII') and False else t
ZW={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}
C=json.load(open('data/bodyplan_splines_v1.json'))
Xs=np.array([527.8,505.8,472.0,438.0,404.4,370.7,336.0,303.4,270.9,235.7,202.2,169.7,136.2,103.4,70.6,36.8,14.6,0.0]); sid=list(range(1,19))
pairs=[]
for k,Z in ZW.items():
    if k=='I': continue
    t=WL[k]
    for X,n in zip(Xs,sid):
        cv=np.array(C[str(n)]['curve']); i=np.argmin(abs(cv[:,1]-Z)); 
        if abs(cv[i,1]-Z)>0.4: continue
        j=max(0,i-5); jj=min(len(cv)-1,i+5); slope=abs((cv[jj,0]-cv[j,0])/max(cv[jj,1]-cv[j,1],1e-6))
        if slope>2.0: continue
        cx=A_PX*X+B_PX; m=np.argmin(abs(t[:,0]-cx)); 
        if abs(t[m,0]-cx)>3: continue
        pairs.append((k,n,cv[i,0],t[m,1]))
pairs=np.array([(p[2],p[3]) for p in pairs]); keep=np.ones(len(pairs),bool)
for _ in range(6):
    s,c0=np.polyfit(pairs[keep,0],pairs[keep,1],1); res=pairs[:,1]-(s*pairs[:,0]+c0); keep=abs(res)<4*0.0 +3.0/ (-1/s) if False else abs(res)*(-1/s)<2.5
pairs=pairs[keep]; s,c0=np.polyfit(pairs[:,0],pairs[:,1],1); res=pairs[:,1]-(s*pairs[:,0]+c0)
print('crossings used',len(pairs),'; row = %.3f*Y + %.1f -> kY=%.5f mm/px centre row %.1f ; resid std %.2f mm max %.2f mm'%(s,c0,-1/s,c0,res.std()/-s,abs(res).max()/-s))
KY=-1/s; YR=c0
json.dump(dict(KY=KY,YR=YR,A_PX=A_PX,B_PX=B_PX,n_pairs=len(pairs),resid_std_mm=float(res.std()/-s)),open('data/wl_top_calibration.json','w'))
out={}
for k,t in WL.items():
    X=(t[:,0]-B_PX)/A_PX; Y=(YR-t[:,1])*KY; sA=np.r_[0,np.cumsum(np.hypot(np.diff(X),np.diff(Y)))]
    pts=[(round(float(X[np.argmin(abs(sA-q))]),1),round(float(Y[np.argmin(abs(sA-q))]),1)) for q in np.arange(0,sA[-1]-6,20.0)]+[(round(float(X[-1]),1),round(float(Y[-1]),1))]
    out[k]=dict(z=ZW[k],points_XY=pts,length_mm=round(float(sA[-1]),1)); print(k,len(pts),'pts, length %.0f mm'%sA[-1],'ends',pts[0],pts[-1])
json.dump(out,open('data/wl_top_points_all.json','w'))
box=(4100,200,11000,1300); fig,ax=plt.subplots(figsize=(19,6.7),dpi=100); ax.imshow(img.convert('RGB').crop(box),extent=(box[0],box[2],box[3],box[1]))
cm={'I':'#e41a1c','II':'#ff7f00','III':'#4daf4a','IV':'#377eb8','V':'#984ea3','VI':'#a65628','VII':'#f781bf'}
for k,v in out.items():
    P=np.array(v['points_XY']); px=A_PX*P[:,0]+B_PX; py=YR-P[:,1]/KY; ax.plot(px,py,'o',mfc='none',mec=cm[k],ms=5,mew=1.1); ax.text(px[len(px)//2],py[len(py)//2]-16,k,color=cm[k],fontsize=11,weight='bold')
ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig('qa/wl_top_all_points.png',bbox_inches='tight')
