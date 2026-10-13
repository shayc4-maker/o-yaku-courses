import numpy as np, json, sys
sys.path.insert(0,'py'); from p5map import *
from PIL import Image, ImageDraw
E=json.load(open('scan/fwd_edges.json')); L=json.load(open('scan/raw_lines.json'))
V=np.array(json.load(open('out/backbone_contour_v5.json'))['outer'])
xa,xb,za,zb,z=[float(t) for t in sys.argv[1:6]]; out=sys.argv[6]
im=Image.open('a/plan_5_aligned.png').convert('RGB').point(lambda t:160+t*95//255)
u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb); c=im.crop((int(u0),int(v0),int(u1),int(v1))).resize((int((u1-u0)*z),int((v1-v0)*z)))
d=ImageDraw.Draw(c); f=lambda a:[((uu-int(u0))*z,(vv-int(v0))*z) for uu,vv in zip(*model_to_p5(np.array(a)[:,0],np.array(a)[:,1]))]
d.line(f(V),fill=(0,170,0),width=2)
for l in L: d.line(f(l),fill=(120,160,255),width=1)
for k,p in E.items():
    d.line(f(p),fill=(220,0,140),width=2); m=f(p)[len(p)//2]; d.text((m[0]+4,m[1]-12),k,fill=(0,0,0))
c.save(out)
