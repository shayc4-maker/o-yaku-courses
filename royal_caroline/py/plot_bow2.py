import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image, ImageDraw
S=sys.argv[2]; d=json.load(open(S+'/out/bow_check.json'))
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t: 150+t*105//255); dr=ImageDraw.Draw(im,'RGBA')
cols=[(255,0,0,90),(0,160,0,90),(0,0,255,90),(255,0,255,90),(255,160,0,110),(0,180,180,90),(120,60,0,90)]
for i,(k,polys) in enumerate(d.items()):
    for P in polys:
        P=np.array(P); u,v=model_to_p5(P[:,0],P[:,1]); pts=list(zip(u,v))
        dr.polygon(pts,fill=cols[i%7],outline=(0,0,0,255))
        c=P.mean(0); cu,cv=model_to_p5(c[0],c[1]); dr.text((cu,cv),k,fill=(0,0,0,255))
u0,v1=model_to_p5(455,-12); u1,v0=model_to_p5(612,124)
im.crop((int(u0),int(v0),int(u1),int(v1))).save(sys.argv[3])
