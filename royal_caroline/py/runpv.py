import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from track import *
from PIL import Image, ImageDraw
S=sys.argv[2]; img=S+'/a/plan_1b_aligned.png'; D=load_dark(img)
UP=(-0.00649,1232.6)
seeds={'VII':(5900,384),'VI':(5900,403.5),'V':(5900,448),'IV':(5900,527.5),'III':(5900,676),'II':(5900,847),'I':(5900,1067)}
stop=lambda p: p[0]<4120 or p[0]>10800 or p[1]>np.polyval(UP,p[0])-5 or p[1]<150
res={}
for k,s in seeds.items():
    c=trace_cut(D,s,stop,maxang=10); res[k]=c.tolist(); print(k,len(c),c[0].round(),c[-1].round())
json.dump(res,open(S+'/trpv.json','w'))
im=Image.open(img).convert('RGB'); dr=ImageDraw.Draw(im)
cols={'I':(255,0,0),'II':(255,140,0),'III':(200,200,0),'IV':(0,170,0),'V':(0,170,255),'VI':(0,0,255),'VII':(200,0,200)}
for k,c in res.items(): dr.line([tuple(p) for p in c],fill=cols[k],width=3)
im.crop((4000,150,10800,1300)).resize((2267,383),Image.LANCZOS).save(S+'/trpv.png')
im.crop((6800,250,9000,500)).save(S+'/trpv_mid.png')
