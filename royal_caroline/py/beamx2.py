import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image
from scipy.ndimage import uniform_filter1d
S=sys.argv[2]
a=(np.array(Image.open(S+'/a/plan_5_aligned.png').convert('L'))<128).astype(np.float32)
DECKS={'QD_ROOF':[(105,132.7),(110,132.5),(150,131.1),(170,130.6),(190,130.0),(210,129.5),(228,129.0)],
 'FORECASTLE':[(458,117.2),(470,117.2),(510,118.9),(530,119.7),(542,120.0)],
 'GANGWAY':[(245,99.5),(450,99.5)]}
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
json.dump(res,open(S+'/out/beam_x_p5_upper.json','w'))
