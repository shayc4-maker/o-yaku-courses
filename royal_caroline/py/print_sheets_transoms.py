import sys,json; sys.path.insert(0,'py')
from PIL import Image,ImageDraw,ImageFont
from p5map import *
Image.MAX_IMAGE_PIXELS=None
DPI=200; A4=(int(8.27*DPI),int(11.69*DPI)); F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
def page(img,title,labels,grid,landscape=False,white=0.82):
    W,H=A4 if not landscape else (A4[1],A4[0]); P=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(P); m=90
    s=min((W-2*m)/img.size[0],(H-2*m-60)/img.size[1]); im=img.convert('RGB').resize((int(img.size[0]*s),int(img.size[1]*s)),Image.LANCZOS)
    im=Image.blend(im,Image.new('RGB',im.size,'white'),white); ox,oy=m,m+60; P.paste(im,(ox,oy)); d.text((m,m-10),title,fill=(0,0,0),font=F); w,h=im.size
    for (u,v,lab,hz) in grid(s):
        x,y=ox+u,oy+v
        if hz: d.line([(ox,y),(ox+w,y)],fill=(150,180,255),width=1); d.text((ox+3,y-22),lab,fill=(0,0,200),font=F)
        else: d.line([(x,oy),(x,oy+h)],fill=(150,180,255),width=1); d.text((x+3,oy+3),lab,fill=(0,0,200),font=F)
    for (cx,cy),lab in zip([(ox+12,oy+12),(ox+w-12,oy+12),(ox+12,oy+h-12),(ox+w-12,oy+h-12)],labels):
        d.line([(cx-18,cy),(cx+18,cy)],fill=(255,0,0),width=3); d.line([(cx,cy-18),(cx,cy+18)],fill=(255,0,0),width=3)
        d.text((cx+22 if cx<W/2 else cx-260,cy+10 if cy<H/2 else cy-34),lab,fill=(255,0,0),font=F)
    return P
reg={}
# A: plan_7 aft elevation, lower stern (wing transom band down to the rudder)
T7='/root/.claude/uploads/9b1663d1-123c-5304-bded-1182034acdbc/78e92e00-plan_7.tif'; im7=Image.open(T7).convert('L'); b7=(520,1080,2340,1900); c7=im7.crop(b7)
def g7(s): return [(x*s,0,'x%d'%(x+b7[0]),False) for x in range(100,c7.size[0],200)]+[(0,y*s,'y%d'%(y+b7[1]),True) for y in range(100,c7.size[1],200)]
pA=page(c7,'A  plan_7 aft elevation, lower stern. Mark: ends (left/right) of transom 1,2,3 and their lower edge curves',['x%d y%d'%(b7[0],b7[1]),'x%d y%d'%(b7[2],b7[1]),'x%d y%d'%(b7[0],b7[3]),'x%d y%d'%(b7[2],b7[3])],g7,landscape=True)
reg['A']={'file':'plan_7.tif','crop_px':list(b7)}
# B: plan_5 side view, transoms region (model mm)
im5=Image.open('plans/plan_5_aligned.png'); X0,Z1,X1,Z0=-20,90,45,40
(u0,v0),(u1,v1)=model_to_p5(X0,Z1),model_to_p5(X1,Z0); c5=im5.crop((int(u0),int(v0),int(u1),int(v1)))
def g5(s): return [((model_to_p5(X,Z1)[0]-int(u0))*s,0,'X%d'%X,False) for X in range(-15,45,5)]+[(0,(model_to_p5(X0,Z)[1]-int(v0))*s,'Z%d'%Z,True) for Z in range(45,90,5)]
pB=page(c5,'B  plan_5 side view, transoms. Grid = model mm. Mark: Z and X extents of transoms 1,2,3 (corners)',['X%d Z%d'%(X0,Z1),'X%d Z%d'%(X1,Z1),'X%d Z%d'%(X0,Z0),'X%d Z%d'%(X1,Z0)],g5)
reg['B']={'file':'plan_5_aligned.png','crop_px':[int(u0),int(v0),int(u1),int(v1)],'corners_model_mm':[[X0,Z1],[X1,Z1],[X0,Z0],[X1,Z0]]}
pA.save('qa/print_sheets_transoms.pdf',save_all=True,append_images=[pB],resolution=DPI); json.dump(reg,open('data/print_sheets_transoms.json','w'))
print('ok',pA.size,pB.size)
