import sys,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image, ImageDraw
S=sys.argv[2]; im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB')
tiles=[]
for X in map(float,sys.argv[3].split(',')):
    u,_=model_to_p5(X,0); u=int(u); _,vt=model_to_p5(X,155); _,vb=model_to_p5(X,-12); vt=int(vt); vb=int(vb)
    c=im.crop((u-120,vt,u+120,vb)); d=ImageDraw.Draw(c)
    for Z in range(-10,156,5):
        _,v=model_to_p5(X,Z); y=v-vt; d.line([(0,y),(15 if Z%10 else 35,y)],fill=(255,0,0) if Z%10==0 else (0,0,255),width=2)
        if Z%10==0: d.text((37,y-6),str(Z),fill=(255,0,0))
    d.text((120,4),f'X{X:.0f}',fill=(255,0,0)); tiles.append(c)
W=sum(t.size[0] for t in tiles); H=max(t.size[1] for t in tiles); out=Image.new('RGB',(W,H),'white'); x=0
for t in tiles: out.paste(t,(x,0)); x+=t.size[0]
out.save(sys.argv[4])
