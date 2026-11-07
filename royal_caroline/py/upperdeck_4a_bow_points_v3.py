# plan_4a bow v3: planking here is about HALF the lower deck's (builder) -> 0.8 mm; H moved slightly inward onto the centre of the thick outer line (first thick ink run, >= 5 px, within -2..+14 px inward of the v2 position); H1 placed from the local curve trend (quadratic through H2-H4 extrapolated), snapped within +-5 px; F = H + 0.8 mm inward, snapped to the nearest drawn line within +-0.25 mm. Points only.
import sys,json,numpy as np
sys.path.insert(0,'py')
V2=json.load(open('data/upperdeck_4a_bow_points_v2.json'))
from deckplan_outline import *
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=11.75; PLANK=0.8; ink=load('4a'); cl=V2['centre_line_through_masts']; yc=lambda x:cl['m1'][1]+cl['slope']*(x-cl['m1'][0])
H0=np.array([[r['H_x_px'],r['H_y_px']] for r in V2['points']])
def normals(P):
    out=[]
    for k in range(len(P)):
        t=P[min(k+1,len(P)-1)]-P[max(k-1,0)]; t=t/np.hypot(*t); n=np.array([-t[1],t[0]]); out.append(n if n[1]>0 else -n)
    return out
N0=normals(H0)
def thick_run_centre(p,n,lo=-2,hi=14,minw=5):
    d=np.arange(lo,hi+1,1.0); prof=np.array([ink[int(round((p+n*x)[1])),int(round((p+n*x)[0]))] for x in d]); idx=np.where(prof)[0]
    if len(idx)==0: return p,False
    runs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); thick=[r for r in runs if len(r)>=minw]
    r=thick[0] if thick else runs[0]; return p+n*d[int(round(r.mean()))],bool(thick)
H=[];info=[]
for k in range(1,len(H0)):
    h,tk=thick_run_centre(H0[k],N0[k]); H.append(h); info.append(tk)
# H1 from the curve trend: quadratic through H2,H3,H4 (x -> y), extrapolated to x = H2.x - 139
Hx=np.array([h[0] for h in H[:3]]); Hy=np.array([h[1] for h in H[:3]]); c=np.polyfit(Hx,Hy,2); x1=H[0][0]-139; guess=np.array([x1,np.polyval(c,x1)])
p1,_=thick_run_centre(guess+np.array([0,-5.0]),np.array([0,1.0]),lo=0,hi=10,minw=3); H=[p1]+H; info=[False]+info
N=normals(np.array(H)); rows=[]
for k,h in enumerate(H):
    fp,okf=thick_run_centre(h+N[k]*PLANK*S-N[k]*0.25*S,N[k],lo=0,hi=int(0.5*S),minw=1)
    rows.append(dict(id=k+1,H_x_px=round(float(h[0]),1),H_y_px=round(float(h[1]),1),H_Y_mm=round((yc(h[0])-h[1])/S,2),F_x_px=round(float(fp[0]),1),F_y_px=round(float(fp[1]),1),F_Y_mm=round((yc(fp[0])-fp[1])/S,2),F_on_drawn_line=bool(okf),H_on_thick_line=bool(info[k]),shift_H_vs_v2_px=round(float(np.hypot(*(h-(H0[k] if True else h)))),1)))
json.dump(dict(plan='4a',plank_mm=PLANK,points=rows),open('data/upperdeck_4a_bow_points_v3.json','w'),indent=1)
for r in rows: print(r)
img=Image.open(BASE+FILES['4a']).convert('L'); fig,axs=plt.subplots(2,1,figsize=(18,22))
for a,bx in zip(axs,((5900,150,7500,1000),(6000,250,7300,620))):
    a.imshow(np.array(img.crop(bx)),cmap='gray',extent=(bx[0],bx[2],bx[3],bx[1]),aspect='equal')
    for r in rows:
        a.plot(r['H_x_px'],r['H_y_px'],'+',color='red',ms=13,mew=1.5); a.plot(r['F_x_px'],r['F_y_px'],'x',color='blue',ms=9,mew=1.6)
        if bx[0]<=r['H_x_px']<=bx[2]: a.text(r['H_x_px']+6,r['H_y_px']-14,str(r['id']),color='red',fontsize=10,weight='bold')
    a.set_xlim(bx[0],bx[2]); a.set_ylim(bx[3],bx[1])
axs[0].set_title('plan_4a bow v3: H (red) on the thick outer line, F (blue) = H + 0.8 mm inward')
fig.savefig('qa/upperdeck_4a_bow_points_v3.png',dpi=55,bbox_inches='tight')
