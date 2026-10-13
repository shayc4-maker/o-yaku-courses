import numpy as np, json, sys
sys.path.insert(0,'py'); from p5map import *
from PIL import Image, ImageDraw, ImageFont
D=json.load(open('scan2/dots_merged.json')); P=np.array([[d['X'],d['Z']] for d in D])
E=json.load(open(sys.argv[8])) if len(sys.argv)>8 else [(int(a),int(b)) for a,b,L,s in np.load('scan2/cand2.npy') if s>=float(sys.argv[7])]
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',15)
xa,xb,za,zb,z=[float(t) for t in sys.argv[1:6]]; out=sys.argv[6]
im=Image.open('a/plan_5_aligned.png').convert('RGB').point(lambda t:185+t*70//255)
u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb)
c=im.crop((int(u0),int(v0),int(u1),int(v1))).resize((int((u1-u0)*z),int((v1-v0)*z))); d=ImageDraw.Draw(c)
f=lambda X,Z:(((model_to_p5(X,Z)[0]-int(u0))*z),((model_to_p5(X,Z)[1]-int(v0))*z))
for a,b in E:
    d.line([f(*P[a]),f(*P[b])],fill=(230,0,120),width=2)
for p in D:
    if not (xa<=p['X']<=xb and za<=p['Z']<=zb): continue
    x,y=f(p['X'],p['Z']); col=(0,150,0) if p['c']=='G' else (0,60,255); r=4
    d.ellipse((x-r,y-r,x+r,y+r),fill=col); d.text((x+5,y-8),str(p['id']),fill=(120,0,0),font=F)
c.save(out)
