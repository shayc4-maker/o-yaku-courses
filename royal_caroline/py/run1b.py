import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from track import *
from PIL import Image, ImageDraw
img=sys.argv[2]; D=load_dark(img)
CL=2453.0; KH=31
seeds={1:(2706,1440),2:(2954,1440),3:(3163,1440),4:(3264,1440),5:(3309,1440),6:(3324,1440),7:(3334,1440),8:(3340,1440)}
stop=lambda p: p[0]<CL+KH+7 or p[1]<500 or p[1]>2010 or p[0]>3700
res={}
for k,s in seeds.items():
    c=trace_cut(D,s,stop); res[k]=c.tolist(); print(k,len(c),c[0].round(),c[-1].round())
json.dump(res,open(sys.argv[3],'w'))
im=Image.open(img).convert('RGB'); dr=ImageDraw.Draw(im)
cols=[(255,0,0),(0,160,0),(0,0,255),(255,0,255),(0,180,180),(200,120,0)]
for i,(k,c) in enumerate(res.items()):
    dr.line([tuple(p) for p in c],fill=cols[i%6],width=2)
im.crop((2350,500,3750,2150)).save(sys.argv[4])
