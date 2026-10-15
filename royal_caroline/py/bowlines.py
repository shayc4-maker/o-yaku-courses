import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *; from track import *
from PIL import Image, ImageDraw
S=sys.argv[2]
B=np.array(Image.open(S+'/a/plan_5_open.png').convert('L'))<128
D=load_dark(S+'/a/plan_5_open.png',sigma=2.0)
def runs_at(Z,Xa,Xb):
    u0,v=model_to_p5(Xa,Z); u1,_=model_to_p5(Xb,Z); v=int(round(float(v)))
    row=B[v-2:v+3,int(u0):int(u1)].any(0); out=[];s=None
    for i,b in enumerate(row):
        if b and s is None: s=i
        if not b and s is not None: out.append(int(u0)+(s+i)//2); s=None
    return v,out
seeds=[]
for Z,Xa,Xb in ((40,505,575),(70,545,600),(95,550,610),(15,495,545),(55,530,590),(-3,495,530)):
    v,xs=runs_at(Z,Xa,Xb)
    for u in xs:
        X,_=p5_to_model(u,v); seeds.append((u,v,round(float(X),1),Z))
print(len(seeds)); print([(s[2],s[3]) for s in seeds])
stop=lambda p: p[0]<6600 or p[0]>8600 or p[1]<400 or p[1]>2100
lines=[]
for (u,v,X,Z) in seeds:
    c=trace_cut(D,(u,v),stop,maxang=8,look=24,maxturn=np.radians(30),minscore=0.12)
    if len(c)<25: continue
    XX,ZZ=p5_to_model(c[:,0],c[:,1]); P=np.c_[XX,ZZ]
    # dedupe: skip if mostly overlapping an existing line
    dup=False
    for L in lines:
        Q=np.array(L['pts']); d=np.min(np.hypot(P[:,None,0]-Q[None,:,0],P[:,None,1]-Q[None,:,1]),axis=1)
        if (d<0.6).mean()>0.6: dup=True; break
    if not dup: lines.append(dict(seed=(X,Z),pts=P.tolist()))
print('lines',len(lines))
json.dump(lines,open(S+'/out/bowlines_raw.json','w'))
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t: 160+t*95//255); d=ImageDraw.Draw(im)
import colorsys
for i,L in enumerate(lines):
    P=np.array(L['pts']); u,v=model_to_p5(P[:,0],P[:,1]); col=tuple(int(255*c) for c in colorsys.hsv_to_rgb((i*0.13)%1,1,0.85))
    d.line(list(zip(u,v)),fill=col,width=5); m=len(P)//2; d.text((u[m]+6,v[m]),str(i),fill=col)
    print(i,'seed',L['seed'],'ends',np.round(P[0],1),np.round(P[-1],1),'n',len(P))
u0,v1=model_to_p5(485,-12); u1,v0=model_to_p5(612,124)
im.crop((int(u0),int(v0),int(u1),int(v1))).save(S+'/bowlines.png')
