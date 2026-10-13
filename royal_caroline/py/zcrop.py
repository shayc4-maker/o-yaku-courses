import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image, ImageDraw
S=sys.argv[2]; im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB')
fx=json.load(open(S+'/out/frames_X.json'))['X_mm']
tiles=[]
for f in map(int,sys.argv[3].split(',')):
    X=fx[f-1]; u,_=model_to_p5(X,0); u=int(u)
    c=im.crop((u-90,1500,u+90,2060)).resize((360,1120)); d=ImageDraw.Draw(c)
    for Z in range(-8,42,2):
        _,v=model_to_p5(X,Z); y=(v-1500)*2
        d.line([(0,y),(25 if Z%10 else 50,y)],fill=(255,0,0) if Z%10==0 else (0,0,255),width=2)
        if Z%10==0: d.text((52,y-6),str(Z),fill=(255,0,0))
    d.text((150,5),f'F{f}',fill=(255,0,0)); tiles.append(c)
W=sum(t.size[0] for t in tiles); out=Image.new('RGB',(W,1120),'white'); x=0
for t in tiles: out.paste(t,(x,0)); x+=t.size[0]
out.save(sys.argv[4])
