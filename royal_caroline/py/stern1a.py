import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from track import *
from PIL import Image, ImageDraw
S=sys.argv[2]; D=load_dark(S+'/a/plan_1a_aligned.png')
K=1000/244.8/48
def XZ(c): return np.c_[(c[:,0]-4194.98)*K,(2104.73-c[:,1])*8.689/102.1]
stop=lambda p: p[1]<330 or p[1]>1135 or p[0]<3540 or p[0]>4030
face=trace_cut(D,(3805,850),stop,maxang=10,maxturn=np.radians(40))
print('face',face[0].round(),face[-1].round(),len(face))
r=[(y,x) for y in range(1075,1125,4) for x in [None]]
under=trace_cut(D,(3950,1090),stop,maxang=10,maxturn=np.radians(40))
print('under',under[0].round(),under[-1].round(),len(under))
json.dump({'stern_face':XZ(face).tolist(),'counter_under':XZ(under).tolist()},open(S+'/out/stern1a.json','w'))
im=Image.open(S+'/a/plan_1a_aligned.png').convert('RGB'); d=ImageDraw.Draw(im)
d.line([tuple(p) for p in face],fill=(255,0,0),width=3); d.line([tuple(p) for p in under],fill=(0,0,255),width=3)
im.crop((3550,250,4300,1250)).save(S+'/p1a_counter_tr.png')
