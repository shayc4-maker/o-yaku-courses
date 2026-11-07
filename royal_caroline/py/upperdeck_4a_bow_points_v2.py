# plan_4a bow v2: the detected band edge is the OUTER (planking) line -> these are H; F (frame line) = H moved INWARD by the planking thickness 1.6 mm, re-centred on the nearest drawn line. H1 re-placed on the outer line (the first detection slipped inward at the gun bracket). Points only.
import sys,json,numpy as np
sys.path.insert(0,'py')
V1=json.load(open('data/upperdeck_4a_bow_points_v1.json'))
from deckplan_outline import *
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=11.75; PLANK=1.6; ink=load('4a'); cl=V1['centre_line_through_masts']; yc=lambda x:cl['m1'][1]+cl['slope']*(x-cl['m1'][0])
def centre_on_ink(p,n,win):
    prof=[(d,ink[int(round((p+n*d)[1])),int(round((p+n*d)[0]))]) for d in np.arange(-win,win+0.5,1.0)]; on=[d for d,v in prof if v]
    if not on: return p,False
    runs=np.split(np.array(on),np.where(np.diff(on)>1.5)[0]+1); r=min(runs,key=lambda q:abs(q.mean())); return p+n*r.mean(),True
old=V1['points']; H=[np.array([r['F_x_px'],r['F_y_px']],float) for r in old[1:]]          # old F2..F9 are on the outer line
# re-place H1: predicted by extrapolating H2,H3 one step to the left (guess only), then centred on the outer line's ink (+-14 px, vertical)
x1=int(H[0][0]-139); pred=H[0]+(H[0]-H[1])/np.hypot(*(H[0]-H[1]))*139; p1,ok1=centre_on_ink(np.array([x1,pred[1]]),np.array([0.0,1.0]),14)
H=[p1]+H; H=[np.array(h,float) for h in H]
rows=[]
for k,h in enumerate(H):
    t=H[min(k+1,len(H)-1)]-H[max(k-1,0)]; t/=np.hypot(*t); n=np.array([-t[1],t[0]]); n=n if n[1]>0 else -n      # inward = larger y (towards the centre row)
    hc,okh=centre_on_ink(h,-n,0.25*S)
    fp,okf=centre_on_ink(hc+n*PLANK*S,n,0.35*S)
    rows.append(dict(id=k+1,H_x_px=round(float(hc[0]),1),H_y_px=round(float(hc[1]),1),H_Y_mm=round((yc(hc[0])-hc[1])/S,2),F_x_px=round(float(fp[0]),1),F_y_px=round(float(fp[1]),1),F_Y_mm=round((yc(fp[0])-fp[1])/S,2),F_on_drawn_line=bool(okf)))
json.dump(dict(plan='4a',plank_mm=PLANK,centre_line_through_masts=cl,points=rows),open('data/upperdeck_4a_bow_points_v2.json','w'),indent=1)
for r in rows: print(r)
img=Image.open(BASE+FILES['4a']).convert('L'); fig,axs=plt.subplots(2,1,figsize=(18,22))
for a,bx in zip(axs,((5900,150,7500,1000),(6000,250,7300,620))):
    a.imshow(np.array(img.crop(bx)),cmap='gray',extent=(bx[0],bx[2],bx[3],bx[1]),aspect='equal')
    for r in rows:
        a.plot(r['H_x_px'],r['H_y_px'],'+',color='red',ms=13,mew=1.5); a.plot(r['F_x_px'],r['F_y_px'],'x',color='blue',ms=9,mew=1.6)
        if bx[0]<=r['H_x_px']<=bx[2]: a.text(r['H_x_px']+6,r['H_y_px']-14,str(r['id']),color='red',fontsize=10,weight='bold')
    a.set_xlim(bx[0],bx[2]); a.set_ylim(bx[3],bx[1])
axs[0].set_title('plan_4a bow v2: H = outer (planking) line (red), F = frame line = H moved inward 1.6 mm (blue)')
fig.savefig('qa/upperdeck_4a_bow_points_v2.png',dpi=55,bbox_inches='tight')
