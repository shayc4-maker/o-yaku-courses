import sys,json,os,subprocess,numpy as np,cv2
sys.path.insert(0,'py')
PDF,OUT=sys.argv[1],sys.argv[2]; os.makedirs(OUT,exist_ok=True)
subprocess.run(['pdftoppm','-r','150','-png',PDF,OUT+'/p'],check=True)
reg=json.load(open('data/print_sheets_stern_v2.json'))
DPI=200; A4=(int(8.27*DPI),int(11.69*DPI))
def tmpl(sz,land):
    W,H=A4 if not land else (A4[1],A4[0]); m=90; av=(W-2*m,H-2*m-60); s=min(av[0]/sz[0],av[1]/sz[1]); w,h=int(sz[0]*s),int(sz[1]*s); ox,oy=m,m+60
    return s,[(ox+12,oy+12),(ox+w-12,oy+12),(ox+12,oy+h-12),(ox+w-12,oy+h-12)],(ox,oy)
def crosses(img):
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); H,W=g.shape; L=27; T=np.full((L,L),255,np.uint8); T[L//2-1:L//2+2,:]=0; T[:,L//2-1:L//2+2]=0
    R=cv2.matchTemplate(g,T,cv2.TM_CCOEFF_NORMED); out=[]
    for (x0,x1,y0,y1) in [(0,W//3,0,H//3),(2*W//3,W,0,H//3),(0,W//3,2*H//3,H),(2*W//3,W,2*H//3,H)]:
        sub=R[max(y0-L//2,0):y1-L//2,max(x0-L//2,0):x1-L//2]; yy,xx=np.unravel_index(np.argmax(sub),sub.shape); out.append((xx+max(x0-L//2,0)+L//2,yy+max(y0-L//2,0)+L//2))
    return np.array(out,float)
res={}
for f,k in zip(sorted(x for x in os.listdir(OUT) if x.startswith('p') and x.endswith('.png')),['A','B']):
    img=cv2.imread(OUT+'/'+f); r=reg[k]['crop_px']; sz=(r[2]-r[0],r[3]-r[1]); land=(k=='B'); best=None
    for rot in range(4):
        im=np.rot90(img,rot).copy() if rot else img; cr=crosses(im); s_=cr.sum(1); d=cr[:,0]-cr[:,1]
        tl=cr[np.argmin(s_)];br=cr[np.argmax(s_)];tr=cr[np.argmax(d)];bl=cr[np.argmin(d)]
        w=np.hypot(*(tr-tl));h=np.hypot(*(bl-tl))
        if (w>h)==land: best=(rot,im,np.array([tl,tr,bl,br],np.float32)); break
    rot,im,quad=best; s,tc,(ox,oy)=tmpl(sz,land); Mx=cv2.getPerspectiveTransform(quad,np.array(tc,np.float32))
    hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV); h,s_,v=cv2.split(hsv)
    def tosrc(pts):
        P=cv2.perspectiveTransform(np.array([pts],np.float32),Mx)[0]; return [[float((p[0]-ox)/s+r[0]),float((p[1]-oy)/s+r[1])] for p in P]
    yel=((h>=20)&(h<=38)&(s_>90)&(v>120)).astype(np.uint8)
    ys,xs=np.where(yel>0); ypts=tosrc(np.c_[xs,ys].astype(np.float32))
    dotm=(((h>=70)&(h<=170))&(s_>110)&(v>40)).astype(np.uint8)
    dotm=cv2.morphologyEx(dotm,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(dotm,connectivity=8)
    dots=[(cen[i],st[i][4],int(h[lab==i].mean())) for i in range(1,n) if 6<=st[i][4]<=260]
    dsrc=tosrc(np.array([d[0] for d in dots],np.float32)) if dots else []
    res[k]={'rot':rot,'yellow_src_px':ypts[::3],'dots':[{'src_px':[round(a,1),round(b,1)],'area':int(d[1]),'hue':d[2]} for (a,b),d in zip(dsrc,dots)]}
    print(k,'rot',rot,'yellow px',len(ypts),'dots',len(dots))
json.dump(res,open('data/scan_marks_stern_2.json','w'))
