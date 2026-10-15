import sys,json; sys.path.insert(0,'py')
from PIL import Image,ImageDraw,ImageFont
from p5map import *
Image.MAX_IMAGE_PIXELS=None
DPI=200; A4=(int(8.27*DPI),int(11.69*DPI))
try: F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
except Exception: F=ImageFont.load_default()
def page(img,title,corner_labels,grid=None,landscape=False):
    W,H=A4 if not landscape else (A4[1],A4[0])
    P=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(P)
    m=90; avail=(W-2*m,H-2*m-60); s=min(avail[0]/img.size[0],avail[1]/img.size[1])
    im=img.convert('RGB').resize((int(img.size[0]*s),int(img.size[1]*s)),Image.LANCZOS); im=Image.blend(im,Image.new('RGB',im.size,'white'),0.75)   # plan lightened to 75 % white so pen colours stand out
    ox,oy=m,m+60; P.paste(im,(ox,oy)); d.text((m,m-10),title,fill=(0,0,0),font=F)
    w,h=im.size
    if grid:
        for (u,v,lab,horiz) in grid(s):
            x,y=ox+u,oy+v
            if horiz: d.line([(ox,y),(ox+w,y)],fill=(120,160,255),width=1); d.text((ox+3,y-22),lab,fill=(0,0,200),font=F)
            else: d.line([(x,oy),(x,oy+h)],fill=(120,160,255),width=1); d.text((x+3,oy+3),lab,fill=(0,0,200),font=F)
    for (cx,cy),lab in zip([(ox+12,oy+12),(ox+w-12,oy+12),(ox+12,oy+h-12),(ox+w-12,oy+h-12)],corner_labels):
        d.line([(cx-18,cy),(cx+18,cy)],fill=(255,0,0),width=3); d.line([(cx,cy-18),(cx,cy+18)],fill=(255,0,0),width=3)
        tx=cx+22 if cx<W/2 else cx-260; ty=cy+10 if cy<H/2 else cy-34; d.text((tx,ty),lab,fill=(255,0,0),font=F)
    return P
pages=[]; reg={}
# A: plan_5 side profile of the stern (model mm)
im5=Image.open('plans/plan_5_aligned.png'); X0,Z1,X1,Z0=-48,165,35,55
(u0,v0),(u1,v1)=model_to_p5(X0,Z1),model_to_p5(X1,Z0); c=im5.crop((int(u0),int(v0),int(u1),int(v1)))
def g5(s):
    out=[]
    for X in range(-40,40,10): u=(model_to_p5(X,Z1)[0]-int(u0))*s; out.append((u,0,'X%d'%X,False))
    for Z in range(60,170,10): v=(model_to_p5(X0,Z)[1]-int(v0))*s; out.append((0,v,'Z%d'%Z,True))
    return out
pages.append(page(c,'A  plan_5 side view, stern. Grid = model mm (X fwd, Z up). Mark: counter timber axis/edges, knee points, wing transom Z72-78',
  ['X%d Z%d'%(X0,Z1),'X%d Z%d'%(X1,Z1),'X%d Z%d'%(X0,Z0),'X%d Z%d'%(X1,Z0)],g5))
reg['A']={'file':'plan_5_aligned.png','crop_px':[int(u0),int(v0),int(u1),int(v1)],'corners_model_mm':[[X0,Z1],[X1,Z1],[X0,Z0],[X1,Z0]]}
# B: plan_7 aft elevation (native px of plan_7.tif)
T7='/root/.claude/uploads/9b1663d1-123c-5304-bded-1182034acdbc/78e92e00-plan_7.tif'
im7=Image.open(T7).convert('L'); S=3.362; b7=(int(150*S),int(105*S),int(700*S),int(560*S)); c7=im7.crop(b7)
def g7(s):
    out=[]
    for x in range(100,c7.size[0],200): out.append((x*s,0,'x%d'%(x+b7[0]),False))
    for y in range(100,c7.size[1],200): out.append((0,y*s,'y%d'%(y+b7[1]),True))
    return out
pages.append(page(c7,'B  plan_7 aft elevation (1/48). Grid = source pixels. Mark: the 6 counter timbers: bottom and top point of each (3 pairs), centre line, one point on the top arch',
  ['x%d y%d'%(b7[0],b7[1]),'x%d y%d'%(b7[2],b7[1]),'x%d y%d'%(b7[0],b7[3]),'x%d y%d'%(b7[2],b7[3])],g7,landscape=True))
reg['B']={'file':'plan_7.tif','crop_px':list(b7)}
# C: plan_4a stern plan
T4='/root/.claude/uploads/9b1663d1-123c-5304-bded-1182034acdbc/05c0c5f0-plan_4a.tif'
im4=Image.open(T4).convert('L'); S4=8507/1700.0; b4=(int(95*S4),int(60*S4),int(270*S4),int(420*S4)); c4=im4.crop(b4)
def g4(s):
    out=[]
    for x in range(100,c4.size[0],200): out.append((x*s,0,'x%d'%(x+b4[0]),False))
    for y in range(100,c4.size[1],200): out.append((0,y*s,'y%d'%(y+b4[1]),True))
    return out
pages.append(page(c4,'C  plan_4a stern in plan (1/48). Grid = source pixels. Mark: 3 points on the aft arch (centre, left, right) and the wing transom ends',
  ['x%d y%d'%(b4[0],b4[1]),'x%d y%d'%(b4[2],b4[1]),'x%d y%d'%(b4[0],b4[3]),'x%d y%d'%(b4[2],b4[3])],g4))
reg['C']={'file':'plan_4a.tif','crop_px':list(b4)}
pages=[pages[0],pages[1]]; pages[0].save('qa/print_sheets_stern_v2.pdf',save_all=True,append_images=pages[1:],resolution=DPI)
json.dump(reg,open('data/print_sheets_stern_v2.json','w')); print('ok',[p.size for p in pages])
