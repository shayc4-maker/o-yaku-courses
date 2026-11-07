# LOWER DECK (plan_4b), BOW ONLY: reference POINTS on the outer edge of the hull outline (upper side of the drawing), for approval. No splines, no tracing: points at chosen arc spacing, each centred on the ink of the outer line (pixels only used to centre). Positions in plan pixels plus provisional distances (mm at 11.75 px/mm): Y from the local centre row, X from the stem tip.
import sys,json,numpy as np
sys.path.insert(0,'py')
from deckplan_outline import *
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=11.75
ink=load('4b'); m,top,bot=outline(ink); xs=np.where(~np.isnan(top))[0]; xtip=int(xs.max()); H,W=ink.shape
def ink_centre(x,ytop_guess):
    col=ink[:,x-1:x+2].any(axis=1); y=int(ytop_guess)
    # first ink run at/after the outline top
    r=np.where(col[max(y-6,0):y+40])[0]+max(y-6,0)
    if len(r)==0: return float(ytop_guess)
    run=[r[0]]
    for v in r[1:]:
        if v==run[-1]+1: run.append(v)
        else: break
    return float(np.mean(run))
# arc-length positions along the upper outline from the tip backwards (spacing ~12 mm, denser at the tip)
xsel=[x for x in xs if x>=5200]; pts=[]; last=None
xcur=xtip
for x in sorted(xsel,reverse=True):
    y=ink_centre(x,top[x]); p=np.array([x,y])
    if last is None or np.hypot(*(p-last))>=(70 if x>7500 else 140): pts.append((int(x),y)); last=p
cen=lambda x:(top[x]+bot[x])/2
hull=[(x,y) for x,y in pts if x<=7410]; hull=sorted(hull)        # hull edge points, aft -> bow
# corner where the hull edge meets the straight stem bar (top edge of the bar at y~1062)
cx=next(x for x in range(7350,7700) if top[x]>=1038); cy=ink_centre(cx,top[cx])
rows=[]; i=0
for x,y in hull: i+=1; rows.append(dict(id='H%d'%i,x_px=int(x),y_px=round(float(y),1),Y_from_centre_mm=round((cen(x)-y)/S,2),dX_from_tip_mm=round((x-xtip)/S,1)))
rows.append(dict(id='C',x_px=int(cx),y_px=round(float(cy),1),Y_from_centre_mm=round((cen(cx)-cy)/S,2),dX_from_tip_mm=round((cx-xtip)/S,1)))
rows.append(dict(id='T',x_px=int(xtip),y_px=round(float(ink_centre(xtip-3,top[xtip-3])),1),Y_from_centre_mm=0.0,dX_from_tip_mm=0.0))
json.dump(dict(plan='4b',scale_px_per_mm=S,tip_x_px=xtip,points=rows),open('data/lowerdeck_bow_points_v1.json','w'),indent=1)
for r in rows: print(r)
img=Image.open(BASE+FILES['4b']).convert('L'); box=(5100,120,8100,1100); crop=np.array(img.crop(box))
fig,axs=plt.subplots(2,1,figsize=(18,24),gridspec_kw={'height_ratios':[1,1]})
for a,(bx,tit) in zip(axs,((box,'lower deck (plan_4b) bow, upper edge: points for approval'),((6900,120,8100,1100),'zoom: stem tip'))):
    c=np.array(img.crop(bx)); a.imshow(c,cmap='gray',extent=(bx[0],bx[2],bx[3],bx[1]),aspect='equal')
    for r in rows:
        if bx[0]<=r['x_px']<=bx[2]: a.plot(r['x_px'],r['y_px'],'+',color='red',ms=14,mew=1.6); a.text(r['x_px']+8,r['y_px']-14,str(r['id']),color='red',fontsize=11,weight='bold')
    a.set_title(tit); a.set_xlim(bx[0],bx[2]); a.set_ylim(bx[3],bx[1])
fig.savefig('qa/lowerdeck_bow_points_v1.png',dpi=55,bbox_inches='tight')
