import numpy as np, json, sys
sys.path.insert(0,'py'); from p5map import *
from PIL import Image, ImageDraw, ImageFont
L=json.load(open('scan2/lines_v1.json')); D=json.load(open('scan2/dots_merged.json'))
V=np.array(json.load(open('out/backbone_contour_v5.json'))['outer'])
xa,xb,za,zb,z=[float(t) for t in sys.argv[1:6]]; out=sys.argv[6]; lab=len(sys.argv)>7
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
im=Image.open('a/plan_5_aligned.png').convert('RGB').point(lambda t:185+t*70//255)
u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb)
c=im.crop((int(u0),int(v0),int(u1),int(v1))).resize((int((u1-u0)*z),int((v1-v0)*z))); d=ImageDraw.Draw(c)
f=lambda X,Z:(((model_to_p5(X,Z)[0]-int(u0))*z),((model_to_p5(X,Z)[1]-int(v0))*z))
d.line([f(x,zz) for x,zz in V],fill=(0,170,0),width=2)
col={'line':(220,0,120),'spline':(0,90,230),'frames':(230,120,0)}
for l in L: d.line([f(*p) for p in l['pts']],fill=col[l['kind']],width=3)
for p in D:
    if not (xa<=p['X']<=xb and za<=p['Z']<=zb): continue
    x,y=f(p['X'],p['Z']); r=3
    d.ellipse((x-r,y-r,x+r,y+r),outline=(0,0,0))
    if lab: d.text((x+4,y-7),str(p['id']),fill=(0,0,0),font=F)
c.save(out)
