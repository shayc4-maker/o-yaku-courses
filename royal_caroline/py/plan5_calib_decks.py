# step 1: (a) calibration check of plan_5 (aligned frame, mapping py/p5map.py) against the STEP backbone outlines: distance from the projected outline points to the nearest ink; (b) long near-horizontal ink lines (deck candidates) in the bow zone X 400-610, labelled for the builder to name
import json,sys,numpy as np,cv2
sys.path.insert(0,'py')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from p5map import model_to_p5,p5_to_model
from scipy.ndimage import distance_transform_edt
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
al=np.array(Image.open('plans/plan_5_aligned.png').convert('L')); ink=al<110
D=distance_transform_edt(~ink)
BB=json.load(open('data/step44_profiles.json')); d=[];names=[]
for k,v in BB.items():
    if k in ('Split1[1]','Split1[2]','Boss-Extrude4[2]'): continue
    pg=Polygon(max(v,key=lambda q:Polygon(q).area)); xy=np.array(pg.exterior.coords)
    px,py=model_to_p5(xy[:,0],xy[:,1]); ok=(px>=0)&(px<al.shape[1])&(py>=0)&(py<al.shape[0]); dd=D[py[ok].astype(int),px[ok].astype(int)]; d+=list(dd)
d=np.array(d)*0.0851; print('calibration check, backbone outline points -> nearest plan_5 ink: n=%d median %.2f mm, 75%% %.2f, 90%% %.2f mm'%(len(d),np.median(d),np.percentile(d,75),np.percentile(d,90)))
# deck candidates: long near-horizontal ink components
b=(ink*255).astype(np.uint8); k=cv2.getStructuringElement(cv2.MORPH_RECT,(70,1)); op=cv2.morphologyEx(b,cv2.MORPH_OPEN,k)
n,lab,st,cen=cv2.connectedComponentsWithStats(op,connectivity=8); Kx=1000/244.8/48
rows=[]
for i in range(1,n):
    x,y,w,h,a=st[i]; 
    if w<300: continue                # >= 25 mm long
    X0,Z0=p5_to_model(x,y+h/2); X1,Z1=p5_to_model(x+w,y+h/2); thick=h*Kx
    if X1<380: continue
    rows.append((i,float(X0),float(X1),float(Z0),float(thick),int(w)))
rows.sort(key=lambda r:-r[3]); print('long near-horizontal ink lines in the bow zone (X>380): id, X range, Z (mean of the run), thickness mm'); 
for r in rows: print('  %3d  X %.0f..%.0f  Z %.1f  thick %.2f  len %.0f mm'%(r[0],r[1],r[2],r[3],r[4],(r[2]-r[1])))
fig,ax=plt.subplots(figsize=(20,12)); px0,py0=model_to_p5(380,170); px1,py1=model_to_p5(615,-12); box=(int(px0),int(py1)*0+int(py0),int(px1),int(py1))
crop=al[box[1]:box[3],box[0]:box[2]]; ax.imshow(crop,cmap='gray',extent=(380,615,-12,170),aspect='equal'); 
cm=plt.cm.tab20
for j,(i,X0,X1,Z0,th,w) in enumerate(rows):
    m=(lab==i); ys,xs=np.where(m); Xs,Zs=p5_to_model(xs,ys); sel=(Xs>380); ax.plot(Xs[sel],Zs[sel],'.',ms=1,color=cm(j%20)); ax.text((X0+X1)/2,Z0+1.2,'%d: Z %.1f'%(i,Z0),fontsize=7,color=cm(j%20),ha='center')
ax.set_xlim(380,615); ax.set_ylim(-12,170); ax.grid(alpha=.25); ax.set_title('plan_5 bow zone: long near-horizontal lines (deck candidates), ids and mean Z (model mm)')
fig.savefig('qa/plan5_deck_candidates.png',dpi=60,bbox_inches='tight')
json.dump([dict(id=r[0],X0=r[1],X1=r[2],Z=r[3],thick=r[4]) for r in rows],open('data/plan5_deck_candidates.json','w'))
