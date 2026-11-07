# NEXT DECK (plan_4a, the deck whose edge shows the frame heads as a hatched band), BOW: reference POINTS for approval, same method as the lower deck. Centre line through the mast centres (main disc 3860.9,1088.9; fore disc 6604.7,1085.7). F = outer edge of the hatched frame band (first dense region from outside, located on the drawing at chosen arc spacing; points only), H = F moved outward by the planking thickness 1.6 mm and re-centred on the nearest drawn line. No splines. The band ends at the cross bar (x~7195): beyond it the hull side is the thin head curves; C/T (stem) not placed here.
import sys,json,numpy as np,cv2
sys.path.insert(0,'py')
from deckplan_outline import *
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=11.75; PLANK=1.6
ink=load('4a'); f=cv2.boxFilter(ink.astype(np.float32),-1,(25,25))
m1=(3860.9,1088.9); m2=(6604.7,1085.7); sl=(m2[1]-m1[1])/(m2[0]-m1[0]); yc=lambda x:m1[1]+sl*(x-m1[0])
def band_edge(x):
    col=f[100:1090,x]; idx=np.where(col>0.45)[0]
    for i in idx:
        if (col[i:i+40]>0.40).all(): return i+100
    return None
xs=list(range(6020,7170)); ys=[band_edge(x) for x in xs]
# keep valid columns, smooth with a running median
ok=[(x,y) for x,y in zip(xs,ys) if y is not None]; X=np.array([a for a,b in ok]); Y=np.array([b for a,b in ok],float)
from scipy.ndimage import median_filter
# outlier gate only: reject a detection that is > 14 px from the local median of its neighbours (+-100 columns); the points themselves stay the local detections
for _ in range(3):
    loc=median_filter(Y,size=201,mode='nearest'); g=np.abs(Y-loc)<14; X,Y=X[g],Y[g]
Ys=median_filter(Y,size=31,mode='nearest')
sel=[0]; 
for i in range(1,len(X)):
    if np.hypot(X[i]-X[sel[-1]],Ys[i]-Ys[sel[-1]])>=140: sel.append(i)
Fp=np.array([(X[i],Ys[i]) for i in sel])
def centre_on_ink(p,n,win=0.4*S):
    prof=[(d,ink[int(round((p+n*d)[1])),int(round((p+n*d)[0]))]) for d in np.arange(-win,win+0.5,1.0)]; on=[d for d,v in prof if v]
    if not on: return p,False
    runs=np.split(np.array(on),np.where(np.diff(on)>1.5)[0]+1); r=min(runs,key=lambda q:abs(q.mean())); return p+n*r.mean(),True
rows=[]
for k,(x,y) in enumerate(Fp):
    t=Fp[min(k+1,len(Fp)-1)]-Fp[max(k-1,0)]; t/=np.hypot(*t); n=np.array([-t[1],t[0]]); n=n if n[1]<0 else -n          # outward = towards smaller y
    h,ok_=centre_on_ink(np.array([x,y])+n*PLANK*S,n); 
    rows.append(dict(id=k+1,F_x_px=int(x),F_y_px=round(float(y),1),F_Y_mm=round((yc(x)-y)/S,2),H_x_px=round(float(h[0]),1),H_y_px=round(float(h[1]),1),H_Y_mm=round((yc(h[0])-h[1])/S,2),H_on_drawn_line=bool(ok_)))
json.dump(dict(plan='4a',scale_px_per_mm=S,plank_mm=PLANK,centre_line_through_masts=dict(m1=m1,m2=m2,slope=sl),points=rows),open('data/upperdeck_4a_bow_points_v1.json','w'),indent=1)
for r in rows: print(r)
img=Image.open(BASE+FILES['4a']).convert('L'); fig,axs=plt.subplots(2,1,figsize=(18,22))
for a,bx in zip(axs,((5800,150,7500,1100),(6600,300,7500,760))):
    a.imshow(np.array(img.crop(bx)),cmap='gray',extent=(bx[0],bx[2],bx[3],bx[1]),aspect='equal')
    for r in rows:
        a.plot(r['F_x_px'],r['F_y_px'],'x',color='blue',ms=9,mew=1.6); a.plot(r['H_x_px'],r['H_y_px'],'+',color='red',ms=13,mew=1.5)
        if bx[0]<=r['F_x_px']<=bx[2]: a.text(r['H_x_px']+6,r['H_y_px']-14,str(r['id']),color='red',fontsize=10,weight='bold')
    a.set_xlim(bx[0],bx[2]); a.set_ylim(bx[3],bx[1])
axs[0].set_title('plan_4a bow: frame line F (blue, outer edge of the hatched frame band) and planking outer edge H (red, +1.6 mm outward)')
fig.savefig('qa/upperdeck_4a_bow_points_v1.png',dpi=55,bbox_inches='tight')
