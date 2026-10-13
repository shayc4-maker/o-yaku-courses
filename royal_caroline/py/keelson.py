import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *; from track import *
from PIL import Image, ImageDraw
S=sys.argv[2]; D=load_dark(S+'/a/plan_5_aligned.png',sigma=1.2)
# seeds between frames 18 and 19 (X~233)
res={}
for name,Z in (('ks_bottom',7.6),('ks_top',12.2),('hog_top',1.8),('keel_top',0.0)):
    u,v=model_to_p5(233.7,Z)
    # refine seed: nearest dark row within +-6 px
    col=D[int(v)-8:int(v)+9,int(u)]; v=int(v)-8+int(np.argmax(col))
    stop=lambda p: p[0]<1100 or p[0]>8300 or p[1]<600 or p[1]>2100
    c=trace_cut(D,(u,v),stop,maxang=6,look=30,maxturn=np.radians(40),minscore=0.3)
    X,Z=p5_to_model(c[:,0],c[:,1]); res[name]=np.c_[X,Z].tolist(); print(name,len(c),'X %.1f..%.1f'%(X.min(),X.max()),'Z ends %.1f %.1f'%(Z[0],Z[-1]))
json.dump(res,open(S+'/out/p5_lines.json','w'))
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB'); d=ImageDraw.Draw(im)
cols={'ks_bottom':(255,0,0),'ks_top':(0,0,255),'hog_top':(0,170,0),'keel_top':(255,140,0)}
for k,c in res.items():
    c=np.array(c); u,v=model_to_p5(c[:,0],c[:,1]); d.line(list(zip(u,v)),fill=cols[k],width=4)
im.crop((900,900,8621,2100)).resize((2574,400)).save(S+'/ks_all.png')
im.crop((900,1200,3000,2100)).save(S+'/ks_stern.png'); im.crop((6200,700,8000,2100)).save(S+'/ks_bow.png')
