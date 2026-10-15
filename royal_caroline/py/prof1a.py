import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from track import *
S=sys.argv[2]; D=load_dark(S+'/a/plan_1a_aligned.png')
K=1000/244.8/48; X0=4194.98
def Z(y): return (2104.73-y)*8.689/102.1   # profile WL scale: model mm above baseline
res={}
stop=lambda p: p[1]>2222 or p[1]<700 or p[0]>11372 or p[0]<9600
for name,seed in {'stem_rabbet_aft':(10422,1750),'stem_rabbet_fwd':(10441,1750),'stem_outer':(10617,1750)}.items():
    c=trace_cut(D,seed,stop,maxang=10,maxturn=np.radians(50)); res[name]=c; print(name,len(c),c[0].round(),c[-1].round())
out={k:np.c_[(v[:,0]-X0)*K,Z(v[:,1])].tolist() for k,v in res.items()}
# sternpost lines (fit)
aft=np.array([(4012,1150),(4038,1300),(4064,1450),(4100,1650),(4134,1850),(4168,2050),(4186,2150)],float)
fore=np.array([(4122,1450),(4162,1650),(4206,1850),(4249,2050)],float)
fa=np.polyfit(aft[:,1],aft[:,0],1); ff=np.polyfit(fore[:,1],fore[:,0],1)
print('post aft x=%.4f y+%.1f ; fore x=%.4f y+%.1f'%(*fa,*ff))
out['post_aft_fit']=list(fa); out['post_fore_fit']=list(ff)
json.dump(out,open(S+'/out/profile1a.json','w'))
from PIL import Image, ImageDraw
im=Image.open(S+'/a/plan_1a_aligned.png').convert('RGB'); d=ImageDraw.Draw(im)
for k,c in res.items(): d.line([tuple(p) for p in c],fill={'stem_rabbet_aft':(255,0,0),'stem_rabbet_fwd':(0,160,0),'stem_outer':(0,0,255)}[k],width=3)
for f,col in ((fa,(255,0,255)),(ff,(0,180,180))):
    d.line([(np.polyval(f,1000),1000),(np.polyval(f,2215),2215)],fill=col,width=3)
im.crop((9700,600,11372,2300)).resize((836,850)).save(S+'/prof_bow.png'); im.crop((3850,700,4500,2300)).save(S+'/prof_stern.png')
