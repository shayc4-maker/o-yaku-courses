# LOWER DECK (plan_4b) BOW, points for approval (v2): centre line = line through the mast centres (main disc, fore disc); stem line C/T at Y = half keel width WITHOUT rabbet (5.3/2 = 2.65) from that centre line; hull outer edge points H (as v1, Y re-measured from the new centre line); FRAME-LINE points F = H offset inward by the planking thickness (measured in the drawing: lines of the band at ~0.9 and ~1.6 mm from the outer edge) and re-centred on the nearest drawn line. Points only, no splines.
import sys,json,numpy as np
sys.path.insert(0,'py')
from deckplan_outline import *
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
S=11.75; PLANK=1.6; KEELHALF=2.65
ink=load('4b'); V1=json.load(open('data/lowerdeck_bow_points_v1.json')); xtip=V1['tip_x_px']
m1=(3837.2,1093.3); m2=(6612.0,1082.0); slope=(m2[1]-m1[1])/(m2[0]-m1[0]); yc=lambda x:m1[1]+slope*(x-m1[0])
print('centre line through the mast centres: y = %.1f %+.5f*(x-3837.2) (tilt %.3f deg)'%(m1[1],slope,np.degrees(np.arctan(slope))))
H=[(r['id'],r['x_px'],r['y_px']) for r in V1['points'] if r['id'].startswith('H')]
def centre_on_ink(p,n,win=0.35*S):
    prof=[(d,ink[int(round((p+n*d)[1])),int(round((p+n*d)[0]))]) for d in np.arange(-win,win+0.5,1.0)]; on=[d for d,v in prof if v]
    if not on: return p,False
    runs=np.split(np.array(on),np.where(np.diff(on)>1.5)[0]+1); r=min(runs,key=lambda q:abs(q.mean())); return p+n*r.mean(),True
pts=np.array([(x,y) for _,x,y in H],float); rows=[]; F=[]
for i,(id_,x,y) in enumerate(H):
    t=pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]; t/=np.hypot(*t); n=np.array([-t[1],t[0]]); n=n if n[1]>0 else -n      # inward (towards the centre row)
    fp,ok=centre_on_ink(pts[i]+n*PLANK*S,n); F.append((fp,ok))
    rows.append(dict(id=id_,x_px=int(x),y_px=round(float(y),1),Y_mm=round((yc(x)-y)/S,2),dX_from_tip_mm=round((x-xtip)/S,1),frame_id='F'+id_[1:],frame_x_px=round(float(fp[0]),1),frame_y_px=round(float(fp[1]),1),frame_Y_mm=round((yc(fp[0])-fp[1])/S,2),frame_on_drawn_line=bool(ok)))
# C: where the hull outer edge reaches Y=2.65 from the centre line; T: the tip on the same line
yline=lambda x:yc(x)-KEELHALF*S
def edge_y(x):
    col=ink[:,x-1:x+2].any(axis=1); r=np.where(col[900:1120])[0]+900
    return float(r[0]) if len(r) else None
cx=next((x for x in range(7380,7480) if edge_y(x) is not None and edge_y(x)>=yline(x)),7425)
rows.append(dict(id='C',x_px=cx,y_px=round(yline(cx),1),Y_mm=KEELHALF,dX_from_tip_mm=round((cx-xtip)/S,1))); rows.append(dict(id='T',x_px=int(xtip),y_px=round(yline(xtip),1),Y_mm=KEELHALF,dX_from_tip_mm=0.0))
json.dump(dict(plan='4b',scale_px_per_mm=S,plank_mm=PLANK,keel_half_mm=KEELHALF,centre_line_through_masts=dict(m1=m1,m2=m2,slope=slope),points=rows),open('data/lowerdeck_bow_points_v2.json','w'),indent=1)
print('hull Y from the mast centre line: H1 %.2f H9 %.2f H14 %.2f H18 %.2f mm; C at dX %.1f mm from the tip'%(rows[0]['Y_mm'],rows[8]['Y_mm'],rows[13]['Y_mm'],rows[17]['Y_mm'],(cx-xtip)/S))
print('frame-line points on a drawn line: %d of %d'%(sum(1 for r in rows if r.get('frame_on_drawn_line')),sum(1 for r in rows if 'frame_id' in r)))
img=Image.open(BASE+FILES['4b']).convert('L'); fig,axs=plt.subplots(2,1,figsize=(18,24))
for a,(bx,tit) in zip(axs,(((5100,120,8100,1100),'lower deck bow: outer edge H (red), frame line F (blue, offset 1.6 mm), C/T on Y=2.65 (green), centre line through the mast centres (dashed)'),((6900,300,8100,1100),'zoom'))):
    a.imshow(np.array(img.crop(bx)),cmap='gray',extent=(bx[0],bx[2],bx[3],bx[1]),aspect='equal')
    for r in rows:
        if r['id'] in ('C','T'): a.plot(r['x_px'],r['y_px'],'+',color='green',ms=16,mew=2); a.text(r['x_px']+8,r['y_px']-14,r['id'],color='green',fontsize=12,weight='bold')
        elif bx[0]<=r['x_px']<=bx[2]:
            a.plot(r['x_px'],r['y_px'],'+',color='red',ms=13,mew=1.5); a.text(r['x_px']+8,r['y_px']-12,r['id'],color='red',fontsize=9,weight='bold'); a.plot(r['frame_x_px'],r['frame_y_px'],'x',color='blue',ms=8,mew=1.5)
    xx=np.array([bx[0],bx[2]]); a.plot(xx,yc(xx),'k--',lw=.6); a.plot(xx,yline(xx),'g:',lw=.8); a.set_xlim(bx[0],bx[2]); a.set_ylim(bx[3],bx[1]); a.set_title(tit,fontsize=10)
fig.savefig('qa/lowerdeck_bow_points_v2.png',dpi=55,bbox_inches='tight')
