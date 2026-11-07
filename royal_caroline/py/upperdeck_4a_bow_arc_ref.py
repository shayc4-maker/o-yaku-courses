# plan_4a bow: FORM-REFERENCE arc only (builder): not taking points from the cluttered tip; the outer hull line from the keel/stem line (C at Y=2.65 from the mast centre line) back to the end of the frame band (cross bar, x~7200). Rough points picked on the heavy outer curve at chosen rows (ink run centres); no splines, no fitting. For approval.
import sys,json,numpy as np
sys.path.insert(0,'py')
from deckplan_outline import *
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=11.75; V=json.load(open('data/upperdeck_4a_bow_points_v2.json')); cl=V['centre_line_through_masts']; yc=lambda x:cl['m1'][1]+cl['slope']*(x-cl['m1'][0])
ink=load('4a')
def run_centre(y,xa,xb):
    row=ink[y-1:y+2,xa:xb].any(axis=0); idx=np.where(row)[0]; g=np.split(idx,np.where(np.diff(idx)>1)[0]+1); g=[r for r in g if len(r)>=3]
    return None if not g else float(xa+g[0].mean())
# builder: Q3-Q5 are on the line; Q1,Q2 had jumped to another line -> re-placed on the same heavy curve (continuation of the quadratic through Q3-Q5, nearest ink: y=700 double line centred, y=750 run 7255-7263); C moved to the nearby corner where the outer curve meets the top edge of the stem bar (row 1056)
Q=[(7215.0,700),(7259.0,750),(7296.0,800),(7360.5,900),(7386.5,950)]; C=(7424.0,1056.0)
rows=[dict(id='Q%d'%(i+1),x_px=x,y_px=y,Y_mm=round((yc(x)-y)/S,2)) for i,(x,y) in enumerate(Q)]+[dict(id='C',x_px=C[0],y_px=C[1],Y_mm=round((yc(C[0])-C[1])/S,2))]
json.dump(dict(plan='4a',note='form reference only',points=rows),open('data/upperdeck_4a_bow_arc_ref_v1.json','w'),indent=1)
for r in rows: print(r)
img=Image.open(BASE+FILES['4a']).convert('L'); bx=(7050,480,7650,1120); fig,ax=plt.subplots(figsize=(14,15)); ax.imshow(np.array(img.crop(bx)),cmap='gray',extent=(bx[0],bx[2],bx[3],bx[1]),aspect='equal')
H=[(r['H_x_px'],r['H_y_px']) for r in V['points']]; ax.plot([h[0] for h in H],[h[1] for h in H],'+',color='red',ms=12)
for r in rows: ax.plot(r['x_px'],r['y_px'],'x',color='blue',ms=13,mew=2.2); ax.text(r['x_px']+10,r['y_px']-10,r['id'],color='blue',fontsize=13,weight='bold')
ax.axhline(yc(7420.0)-2.65*S,color='g',lw=.6,ls=':'); ax.set_xlim(bx[0],bx[2]); ax.set_ylim(bx[3],bx[1]); ax.set_title('plan_4a bow: form-reference points Q1-Q5 on the heavy outer curve + C (keel/stem line Y=2.65); red = band points H')
fig.savefig('qa/upperdeck_4a_bow_arc_ref_v1.png',dpi=55,bbox_inches='tight')
