import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
from scipy.ndimage import uniform_filter1d
S=sys.argv[2]
a=(np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L'))<128).astype(np.float32)
DECKS={'LOWER_DECK_AFT':[(137,44.6),(170,44.0),(190,43.3),(210,42.8),(233,42.6)],
 'LOWER_DECK_MID':[(237,40.0),(250,39.6),(290,39.6),(330,39.7),(370,39.8),(390,40.3),(430,41.0),(458,41.2)],
 'LOWER_DECK_FWD':[(462,49.4),(510,50.5),(527,51.3)],
 'CABIN_DECK':[(13,76.4),(30,75.6),(50,74.5),(70,73.7),(97,73.0)],
 'MAIN_DECK':[(101,86.8),(110,86.7),(150,86.0),(170,85.6),(190,85.0),(210,84.6),(230,82.8),(290,80.6),(330,80.3),(370,80.3),(410,80.6),(450,83.5),(470,84.1),(510,85.6),(527,86.2)],
 'POOP_DECK':[(13,121.4),(30,120.9),(50,120.6),(70,119.7),(97,118.8)]}
res={}
for name,tab in DECKS.items():
    tab=np.array(tab); xs=np.arange(tab[0,0],tab[-1,0],0.1)
    # cross-hatch texture: density in band 1.2..4.0 below plank top, high-pass on 'checker' => use density between 0.45-0.85 and variance
    d=[]
    for x in xs:
        zt=np.interp(x,tab[:,0],tab[:,1])
        u,v0=model_to_p5(x,zt-1.3); _,v1=model_to_p5(x,zt-3.8)
        d.append(a[int(v0):int(v1),int(u)-1:int(u)+2].mean())
    d=uniform_filter1d(np.array(d),15)
    on=d>0.42; blocks=[];s=None
    for i,v in enumerate(on):
        if v and s is None: s=i
        if not v and s is not None:
            if 2.2<=(i-s)*0.1<=9: blocks.append((round(xs[s],1),round(xs[i-1],1)))
            s=None
    res[name]=blocks; print(name,len(blocks),[(a_,round(b_-a_,1)) for a_,b_ in blocks])
json.dump(res,open(S+'/out/beam_x_p5.json','w'))
