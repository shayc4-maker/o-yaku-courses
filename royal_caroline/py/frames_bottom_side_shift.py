# side view: the whole existing backbone (STEP profiles, NOT moved) on the original sheer plan + the lower end of every frame (outer line at the keel wall, pocket floor, seat) at X-4..X+4
import sys,json,numpy as np
sys.path.insert(0,'py')
from frame_arm import *
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
BB=json.load(open('data/step44_profiles.json'))
PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
import os; SH=float(os.environ.get('SHIFT','0.6'))
rows=json.load(open('data/frames_bottom_side_shift.json'))
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0; img=Image.open('plans/plan_1a_aligned.png').convert('RGB')
fig,axs=plt.subplots(3,1,figsize=(19,22),gridspec_kw={'height_ratios':[0.5,1.1,0.8]})
for a,(xl,zl) in zip(axs,(((-20,570),(-14,62)),((440,545),(-12,45)),((220,330),(-12,14)))):
    box=(int((xl[0]-X0)/KX)-5,int(ZR-zl[1]/KZ)-5,int((xl[1]-X0)/KX)+5,int(ZR-zl[0]/KZ)+5); c=img.crop(box)
    a.imshow(c,extent=(box[0]*KX+X0,box[2]*KX+X0,(ZR-box[3])*KZ,(ZR-box[1])*KZ),aspect='equal')
    for k,pg in PP.items(): x_,z_=pg.exterior.xy; a.plot(x_,np.array(z_)-SH,color='tab:blue',lw=1.0)
    byf={}
    for b,nm,x,hk,fl,st in rows: byf.setdefault(b,{})[nm]=(x,hk,fl,st)
    for b,d in byf.items():
        xs3=[d[k][0] for k in ('m','c','p')]
        if xl[0]-8<xs3[1]<xl[1]+8:
            a.fill(xs3+xs3[::-1],[d[k][2] for k in ('m','c','p')]+[d[k][1] for k in ('p','c','m')],color='tab:red',alpha=.55,lw=0)
            a.plot(xs3,[d[k][1] for k in ('m','c','p')],color='r',lw=1.2)
            if a is not axs[0]: a.text(xs3[1],zl[1]-2,str(b),ha='center',fontsize=8)
    a.set_xlim(*xl); a.set_ylim(*zl); a.set_ylabel('Z (mm)')
axs[0].set_title('Side view (equal scale in X and Z, no stretching): sheer plan (original), whole existing backbone lowered 0.6 mm (blue outlines) = frames raised 0.6 vs the keel, frames lower end in red = from the outer line at the keel wall up to the pocket floor, at X-4, X, X+4')
fig.savefig('qa/frames_bottom_side_shift.png',dpi=55,bbox_inches='tight')
lo=np.array([(r[0],r[3]) for r in rows if r[1]=='c']); print('lowest frame points: min Z %.2f at frame %d; frame bottoms at Z (builder 1,5,10,23,30,40,45):'%(lo[:,1].min(),lo[lo[:,1].argmin(),0]),[ (int(b),round(float(z),2)) for b,z in lo if int(b) in (1,5,10,23,30,40,45)])
