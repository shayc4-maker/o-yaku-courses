import numpy as np, json, sys
sys.path.insert(0,'py'); from p5map import *
from PIL import Image, ImageDraw, ImageFont
D=json.load(open('scan2/dots_merged.json'))
for i,d in enumerate(D): d['id']=i
json.dump(D,open('scan2/dots_merged.json','w'))
V=np.array(json.load(open('out/backbone_contour_v5.json'))['outer'])
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',int(sys.argv[7]) if len(sys.argv)>7 else 18)
xa,xb,za,zb,z=[float(t) for t in sys.argv[1:6]]; out=sys.argv[6]
im=Image.open('a/plan_5_aligned.png').convert('RGB').point(lambda t:180+t*75//255)
u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb)
c=im.crop((int(u0),int(v0),int(u1),int(v1))).resize((int((u1-u0)*z),int((v1-v0)*z))); d=ImageDraw.Draw(c)
f=lambda X,Z:(((model_to_p5(X,Z)[0]-int(u0))*z),((model_to_p5(X,Z)[1]-int(v0))*z))
d.line([f(x,zz) for x,zz in V],fill=(0,160,0),width=1)
for p in D:
    if not (xa<=p['X']<=xb and za<=p['Z']<=zb): continue
    x,y=f(p['X'],p['Z']); col=(0,150,0) if p['c']=='G' else (0,60,255); r=4
    d.ellipse((x-r,y-r,x+r,y+r),fill=col); d.text((x+5,y-8),str(p['id']),fill=(200,0,0),font=F)
c.save(out); print(c.size)
