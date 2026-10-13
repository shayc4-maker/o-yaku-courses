import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image, ImageDraw
S=sys.argv[2]
# frame blocks as drawn in plan_5 (X extents, bottom Z, top Z) - read at 1 mm grid, 3-4x zoom
B=[(443.7,448.9,3.2,10.0),(455.2,460.0,4.0,11.7),(466.0,470.0,5.1,13.2),(477.8,482.6,7.2,15.6),(488.8,493.6,10.2,19.0),
   (500.0,504.5,14.5,23.0),(510.7,515.7,19.2,29.0),(521.8,526.5,27.4,34.3)]
# white gaps between blocks: bottom (deadwood top) and top (keelson/apron underside)
G=[(None,None),(4.8,10.3),(5.7,11.5),(7.8,13.5),(10.3,16.0),(14.0,19.5),(17.8,22.5),(26.4,28.7)]
lower=[(430.0,4.6)]
for k,(x0,x1,zb,zt) in enumerate(B):
    gb=G[k][0] if G[k][0] is not None else 4.7
    lower+= [(x0,gb),(x0,zb),(x1,zb)]
    gbn=G[k+1][0] if k+1<len(G) else None
    if gbn is not None: lower+=[(x1,gbn)]
lower+=[(526.5,34.3)]
ceiling=[(500.0,26.4),(511.0,31.0),(522.9,36.4),(531.0,41.5),(540.0,48.5)]
upper=[(x1,zt) for (x0,x1,zb,zt) in B]   # frame tops
json.dump(dict(blocks=B,gaps=G,lower=lower,ceiling=ceiling),open(S+'/out/fwd_steps_plan5.json','w'),indent=1)
cur=np.array(json.load(open(S+'/out/backbone_contour.json'))['outer'])
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); d=ImageDraw.Draw(im)
def L(pts,col,w):
    pts=np.array(pts); u,v=model_to_p5(pts[:,0],pts[:,1]); d.line(list(zip(u,v)),fill=col,width=w)
L(cur,(255,0,0),3); L(lower,(0,170,0),4); L(ceiling,(0,90,255),4)
for x0,x1,zb,zt in B: L([(x0,zb),(x1,zb),(x1,zt),(x0,zt),(x0,zb)],(255,140,0),2)
u0,v1=model_to_p5(425,-5); u1,v0=model_to_p5(560,55)
c=im.crop((int(u0),int(v0),int(u1),int(v1))); c=c.resize((c.size[0]*2//3*2,c.size[1]*2//3*2)); c.save(S+'/out/RoyalCaroline_Rhino/qa/bow_steps_plan5_vs_model.png'); print(c.size)
