import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *; from hull import section
from PIL import Image, ImageDraw
S=sys.argv[2]; O=S+'/out'
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB'); d=ImageDraw.Draw(im)
pr=json.load(open(O+'/profile1a.json'))
for k,col in (('stem_rabbet_aft',(255,0,0)),('stem_rabbet_fwd',(0,170,0)),('stem_outer',(0,0,255))):
    c=np.array(pr[k]); u,v=model_to_p5(c[:,0],c[:,1]); d.line(list(zip(u,v)),fill=col,width=4)
Kp=1000/244.8/48
for f,col in ((pr['post_aft_fit'],(255,0,255)),(pr['post_fore_fit'],(0,190,190))):
    ys=np.array([1000,2215]); xs=np.polyval(f,ys); X=(xs-4194.98)*Kp; Z=(2104.73-ys)*8.689/102.1
    u,v=model_to_p5(X,Z); d.line(list(zip(u,v)),fill=col,width=4)
for Z,col in ((0,(255,140,0)),(-9.37,(255,140,0))):
    u,v=model_to_p5(np.array([-20,560]),np.array([Z,Z])); d.line(list(zip(u,v)),fill=col,width=2)
fx=json.load(open(O+'/frames_X.json'))['X_mm']
for i,X in enumerate(fx,1):
    P=section(X,kind='pchip'); zr=P[0,1]
    u,v=model_to_p5(np.array([X,X]),np.array([zr,zr+4.8])); d.line(list(zip(u,v)),fill=(255,0,0),width=5)
    u0,v0=model_to_p5(np.array([X-4,X+4]),np.array([zr,zr])); d.line(list(zip(u0,v0)),fill=(255,0,0),width=3)
im.crop((900,1300,3400,2150)).save(S+'/ov5_stern.png'); im.crop((5900,500,8621,2150)).resize((1360,825)).save(S+'/ov5_bow.png')
im.crop((3300,1700,6000,2100)).save(S+'/ov5_mid.png')
