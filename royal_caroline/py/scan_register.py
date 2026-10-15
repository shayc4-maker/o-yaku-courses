import sys,json,numpy as np,cv2
PDF=sys.argv[1]; OUT=sys.argv[2]
import subprocess,os
os.makedirs(OUT,exist_ok=True)
subprocess.run(['pdftoppm','-r','150','-png',PDF,OUT+'/p'],check=True)
reg=json.load(open('data/print_sheets_stern.json'))
# template geometry at 200 dpi: reproduce print_sheets layout
DPI=200; A4=(int(8.27*DPI),int(11.69*DPI))
def tmpl(size_img,landscape):
    W,H=A4 if not landscape else (A4[1],A4[0]); m=90; av=(W-2*m,H-2*m-60); s=min(av[0]/size_img[0],av[1]/size_img[1])
    w,h=int(size_img[0]*s),int(size_img[1]*s); ox,oy=m,m+60
    return s,[(ox+12,oy+12),(ox+w-12,oy+12),(ox+12,oy+h-12),(ox+w-12,oy+h-12)],(ox,oy,w,h)
sizes={'A':None,'B':None,'C':None}
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
def crop_size(k):
    r=reg[k]['crop_px']; return (r[2]-r[0],r[3]-r[1])
def red_crosses(img):
    # crosses are thin dark lines (faded red after scanning): template-match a 27 px cross in the corner areas
    g=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY); H,W=g.shape
    L=27; T=np.full((L,L),255,np.uint8); T[L//2-1:L//2+2,:]=0; T[:,L//2-1:L//2+2]=0
    R=cv2.matchTemplate(g,T,cv2.TM_CCOEFF_NORMED); out=[]
    for (x0,x1,y0,y1) in [(0,W//3,0,H//3),(2*W//3,W,0,H//3),(0,W//3,2*H//3,H),(2*W//3,W,2*H//3,H)]:
        sub=R[max(y0-L//2,0):y1-L//2,max(x0-L//2,0):x1-L//2]; yy,xx=np.unravel_index(np.argmax(sub),sub.shape)
        out.append((xx+max(x0-L//2,0)+L//2,yy+max(y0-L//2,0)+L//2))
    return np.array(out,float)
def purple_blobs(img):
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); h,s,v=cv2.split(hsv)
    m=((h>=125)&(h<=165)&(s>60)&(v>60)).astype(np.uint8)   # violet / purple-magenta
    m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m,connectivity=8)
    return [(cen[i],st[i]) for i in range(1,n) if st[i][4]>25]
res={}
files=sorted(f for f in os.listdir(OUT) if f.startswith('p') and f.endswith('.png'))
for f,k in zip(files,['B','C','A']):   # scan order: B, C, A
    img=cv2.imread(OUT+'/'+f)
    best=None
    for rot in (0,1,2,3):
        im=np.rot90(img,rot).copy() if rot else img
        cr=red_crosses(im)
        if len(cr)<4: continue
        if rot not in (0,1,2,3): continue
        res_k={'rot':rot,'n':len(cr)}
        # pick the 4 extreme corners
        s=cr.sum(1); d=cr[:,0]-cr[:,1]
        tl=cr[np.argmin(s)];br=cr[np.argmax(s)];tr=cr[np.argmax(d)];bl=cr[np.argmin(d)]
        quad=np.array([tl,tr,bl,br],np.float32); w=np.hypot(*(tr-tl)); h=np.hypot(*(bl-tl))
        land=k=='B'
        if (w>h)==land: best=(rot,im,quad); break
    if best is None: print(k,'no crosses found'); continue
    rot,im,quad=best
    s,tc,(ox,oy,w,h)=tmpl(crop_size(k),k=='B')
    src=np.array(tc,np.float32)
    M=cv2.getPerspectiveTransform(quad,src)         # scan -> template (200 dpi page)
    r=reg[k]['crop_px']; bl=purple_blobs(im); pts=[]
    for c,st in bl:
        p=cv2.perspectiveTransform(np.array([[c]],np.float32),M)[0,0]
        u=(p[0]-ox)/s; v=(p[1]-oy)/s              # crop px
        pts.append({'src_px':[round(float(u+r[0]),1),round(float(v+r[1]),1)],'area':int(st[4]),'bbox_scan':[int(st[0]),int(st[1]),int(st[2]),int(st[3])]})
    pts.sort(key=lambda q:(q['src_px'][1],q['src_px'][0]))
    res[k]={'rot':rot,'marks':pts}
    print(k,'rot',rot,'marks',len(pts)); 
    for q in pts: print('   ',q['src_px'],q['area'])
json.dump(res,open('data/scan_marks_stern_1.json','w'))
