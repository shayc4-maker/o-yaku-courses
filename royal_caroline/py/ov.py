import sys,json,numpy as np
from PIL import Image, ImageDraw
img,js,x0,y0,x1,y1,z,out=sys.argv[1],sys.argv[2],*map(int,sys.argv[3:8]),sys.argv[8]
im=Image.open(img).convert('RGB').crop((x0,y0,x1,y1)); im=im.resize(((x1-x0)*z,(y1-y0)*z),Image.NEAREST); dr=ImageDraw.Draw(im)
cols=[(255,0,0),(0,170,0),(0,0,255),(255,0,255),(0,180,180),(230,120,0)]
for i,(k,c) in enumerate(sorted(json.load(open(js)).items(),key=lambda t:int(t[0]))):
    c=(np.array(c)-[x0,y0])*z+z/2
    dr.line([tuple(p) for p in c],fill=cols[i%6],width=1)
    m=c[(c[:,0]>0)&(c[:,1]>0)&(c[:,0]<im.size[0])&(c[:,1]<im.size[1])]
    if len(m): dr.text(tuple(m[len(m)//2]+[4,0]),k,fill=cols[i%6])
im.save(out)
