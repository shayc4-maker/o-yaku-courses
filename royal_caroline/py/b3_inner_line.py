# Plan 6 B3 (hull section fwd of main mast): inner (upper) and outer (lower) edge of the frame floor band near the keel, 2D, scale from the keel width (5.3 mm = 67 px)
import json,numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
Image.MAX_IMAGE_PIXELS=None
im=Image.open('plans/plan_6.png'); g=(255-np.array(im.convert('L')).astype(float))>90
K=5.3/67.0; cx=4217.5; ZK=2325.0      # Z measured from the keel top (row 2325), up positive
def runs_at(x):
    col=g[2150:2480,x-3:x+4].mean(1); d=uniform_filter1d(col,9); idx=np.where(d>0.30)[0]
    return [(2150+int(r[0]),2150+int(r[-1])) for r in (np.split(idx,np.where(np.diff(idx)>3)[0]+1) if len(idx) else []) if len(r)>=12]
IN=[];OUT=[]
for Y in (6,10,14,18,22,26,30,34,38,42):
    x=int(round(cx+Y/K)); r=[q for q in runs_at(x) if q[0]>2225 and q[1]<2370]
    # inner = bottom edge of the upper band; below Y=14 the band is the straight line at row 2280 under the keelson ceiling
    IN.append((x,2280 if Y<14 else r[0][1]))
    if len(r)>=2: OUT.append((x,r[1][0]))
    elif Y>=14 and len(r)==1 and r[0][0]>2300: OUT.append((x,r[0][0]))
IN=IN[:-1]; IN=np.array(IN,float); OUT=np.array(OUT,float)
mm=lambda a:np.c_[(a[:,0]-cx)*K,(ZK-a[:,1])*K]
pi,po=mm(IN),mm(OUT)
json.dump(dict(inner_YZ_from_keel_top=pi.round(2).tolist(),outer_YZ_from_keel_top=po.round(2).tolist(),note='Z relative to keel top; Y from centreline; scale 0.0791 mm/px from keel width'),open('data/b3_inner_line.json','w'))
box=(4000,2150,4900,2420); c=np.array(im.convert('RGB').crop(box))
fig,ax=plt.subplots(figsize=(17,5.4),dpi=90); ax.imshow(c,extent=(box[0],box[2],box[3],box[1]))
for P,col,nm in ((IN,'r','inner'),(OUT,'b','outer')):
    ax.plot(P[:,0],P[:,1],'o',mfc='none',mec=col,ms=6)
    for i,(a,b) in enumerate(P): ax.text(a,b-12 if col=='r' else b+22,'%d'%(i+1),color=col,fontsize=9,ha='center')
ax.axhline(2287,color='g',lw=.6); ax.text(4005,2283,'keelson bottom (row 2287)',color='g',fontsize=8); ax.axhline(2325,color='g',lw=.6); ax.text(4005,2321,'keel top (row 2325)',color='g',fontsize=8)
ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig('qa/b3_inner_line.png',bbox_inches='tight')
print(len(IN)); print('inner',pi.round(1).tolist()); print('outer',po.round(1).tolist())
