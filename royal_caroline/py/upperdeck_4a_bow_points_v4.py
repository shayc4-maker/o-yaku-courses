# plan_4a bow v4 (literal application of the builder's corrections to v2): plank 0.8 mm (half of the lower deck); red H2-H9 a bit external -> moved inward by 0.3 mm along the normal; H1 still inward -> moved outward by 0.45 mm; F = H + 0.8 mm inward. No snapping.
import sys,json,numpy as np
sys.path.insert(0,'py')
V2=json.load(open('data/upperdeck_4a_bow_points_v2.json'))
from deckplan_outline import *
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ink=load('4a'); S=11.75; PLANK=0.8; SHIFT_IN=0.3; SHIFT_OUT1=0.45; cl=V2['centre_line_through_masts']; yc=lambda x:cl['m1'][1]+cl['slope']*(x-cl['m1'][0])
H0=np.array([[r['H_x_px'],r['H_y_px']] for r in V2['points']])
N=[]
for k in range(len(H0)):
    t=H0[min(k+1,len(H0)-1)]-H0[max(k-1,0)]; t=t/np.hypot(*t); n=np.array([-t[1],t[0]]); N.append(n if n[1]>0 else -n)
H=[]
for k,h in enumerate(H0): H.append(h-N[k]*SHIFT_OUT1*S if k==0 else h+N[k]*SHIFT_IN*S)
rows=[]
for k,h in enumerate(H):
    f=h+N[k]*PLANK*S; rows.append(dict(id=k+1,H_x_px=round(float(h[0]),1),H_y_px=round(float(h[1]),1),H_Y_mm=round((yc(h[0])-h[1])/S,2),F_x_px=round(float(f[0]),1),F_y_px=round(float(f[1]),1),F_Y_mm=round((yc(f[0])-f[1])/S,2)))
json.dump(dict(plan='4a',plank_mm=PLANK,points=rows),open('data/upperdeck_4a_bow_points_v4.json','w'),indent=1)
for r in rows: print(r)
# measured band structure for the record: vertical ink runs at x of H2..H4 (mm from the topmost thin line)
for x in (6184,6322,6460):
    col=ink[:,x-1:x+2].any(axis=1); idx=np.where(col[280:420])[0]+280; g=np.split(idx,np.where(np.diff(idx)>1)[0]+1); rr=[(int(a[0]),int(a[-1])) for a in g]; top=rr[0][0] if rr else 0
    print('x=%d runs (mm below the first ink line):'%x,[(round((a-top)/S,2),round((b-top)/S,2)) for a,b in rr][:8])
img=Image.open(BASE+FILES['4a']).convert('L'); fig,axs=plt.subplots(2,1,figsize=(18,22))
for a,bx in zip(axs,((5900,150,7500,1000),(5950,260,6800,470))):
    a.imshow(np.array(img.crop(bx)),cmap='gray',extent=(bx[0],bx[2],bx[3],bx[1]),aspect='equal')
    for r in rows:
        a.plot(r['H_x_px'],r['H_y_px'],'+',color='red',ms=13,mew=1.5); a.plot(r['F_x_px'],r['F_y_px'],'x',color='blue',ms=9,mew=1.6)
        if bx[0]<=r['H_x_px']<=bx[2]: a.text(r['H_x_px']+6,r['H_y_px']-14,str(r['id']),color='red',fontsize=10,weight='bold')
    a.set_xlim(bx[0],bx[2]); a.set_ylim(bx[3],bx[1])
axs[0].set_title('plan_4a bow v4: H (red), F (blue) = H + 0.8 mm inward')
fig.savefig('qa/upperdeck_4a_bow_points_v4.png',dpi=55,bbox_inches='tight')
