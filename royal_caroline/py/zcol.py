import sys,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image, ImageDraw
S=sys.argv[2]; Z0,Z1=float(sys.argv[3]),float(sys.argv[4]); z=3
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB')
tiles=[]
for X in map(float,sys.argv[5].split(',')):
    u0,v1=model_to_p5(X-6,Z0); u1,v0=model_to_p5(X+6,Z1)
    c=im.crop((int(u0),int(v0),int(u1),int(v1))); c=c.resize((c.size[0]*z,c.size[1]*z)); d=ImageDraw.Draw(c)
    for Zt in np.arange(np.ceil(Z0),Z1,1):
        _,v=model_to_p5(X,Zt); y=(v-int(v0))*z
        d.line([(0,y),(30 if Zt%5==0 else 12,y)],fill=(255,0,0) if Zt%5==0 else (0,0,255),width=2)
        if Zt%5==0: d.text((32,y-6),str(int(Zt)),fill=(255,0,0))
    d.text((40,2),'X%d'%X,fill=(0,140,0)); tiles.append(c)
W=sum(t.size[0]+6 for t in tiles); H=max(t.size[1] for t in tiles); out=Image.new('RGB',(W,H),'white'); x=0
for t in tiles: out.paste(t,(x,0)); x+=t.size[0]+6
out.save(sys.argv[6]); print(out.size)
