import sys,json; sys.path.insert(0,'py'); from p5map import *
import numpy as np
from PIL import Image, ImageDraw, ImageFont
DPI=300; PX=DPI/25.4; S=2.0
src=Image.open('a/plan_5_aligned.png').convert('L')
V=np.array(json.load(open('out/backbone_contour_v5.json'))['outer'])
F=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',34); Fs=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',26)
FB=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',40)
# (page orientation, [strips: id,xa,xb,za,zb, paper ox,oy mm])
pages=[('P',[('A',-24,68,-12,124,15,14)]),
       ('L',[('B',62,196,-12,30,12,14),('C',190,324,-12,30,12,112)]),
       ('L',[('D',318,446,-12,30,12,14)]),
       ('P',[('E',436,528,-14,124,15,14)]),
       ('P',[('F',520,614,-14,124,15,14)])]
out=[]; meta=[]
for n,(o,strips) in enumerate(pages):
    W,H=(210,297) if o=='P' else (297,210)
    pg=Image.new('RGB',(int(W*PX),int(H*PX)),'white'); d=ImageDraw.Draw(pg)
    d.text((12*PX,3*PX),f'Royal Caroline plan_5 backbone - sheet {n+1}/{len(pages)} - scale 2:1 - print at 100% (Actual size)',fill='black',font=F)
    for sid,xa,xb,za,zb,ox,oy in strips:
        ox,oy=ox*PX,oy*PX
        loc=lambda X,Z:((X-xa)*S*PX,(zb-Z)*S*PX)
        u0,v1=model_to_p5(xa,za); u1,v0=model_to_p5(xb,zb)
        w=int((xb-xa)*S*PX); h=int((zb-za)*S*PX)
        c=src.crop((int(round(float(u0))),int(round(float(v0))),int(round(float(u1))),int(round(float(v1))))).resize((w,h),Image.LANCZOS).point(lambda t:150+t*105//255).convert('RGB')
        ImageDraw.Draw(c).line([loc(x,z) for x,z in V],fill=(0,140,0),width=2)
        pg.paste(c,(int(ox),int(oy))); d.rectangle((ox,oy,ox+w,oy+h),outline=(160,160,160),width=2)
        d.text((ox+w/2-60,oy+h+8),f'strip {sid}   X {xa}..{xb}',fill='black',font=FB)
        mk=[]
        for X in (round(xa+5),round(xb-5)):
            for Z in (round(za+4),round(zb-4)):
                px,py=loc(X,Z); px+=ox; py+=oy; r=int(3.5*PX)
                d.ellipse((px-r,py-r,px+r,py+r),outline='black',width=3); d.line((px-r-15,py,px+r+15,py),fill='black',width=3); d.line((px,py-r-15,px,py+r+15),fill='black',width=3)
                d.text((px+r+6,py+6),f'{sid} X{X} Z{Z}',fill='black',font=Fs); mk.append((X,Z))
        meta.append(dict(sheet=n+1,strip=sid,xa=xa,xb=xb,za=za,zb=zb,marks=mk))
    bx,by=(W-60)*PX,(H-7)*PX; d.rectangle((bx,by,bx+20*PX,by+2*PX),fill='black'); d.text((bx+23*PX,by-6),'= 20 mm on paper',fill='black',font=Fs)
    out.append(pg)
out[0].save('out/RoyalCaroline_Rhino/print/backbone_trace_sheets.pdf',save_all=True,append_images=out[1:],resolution=DPI)
json.dump(meta,open('out/RoyalCaroline_Rhino/print/backbone_trace_sheets.json','w'),indent=1)
for i,p in enumerate(out): p.resize((p.size[0]//5,p.size[1]//5)).save(f'pv{i}.png')
