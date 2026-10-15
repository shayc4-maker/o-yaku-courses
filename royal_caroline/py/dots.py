import numpy as np, cv2, json, sys, itertools
sys.path.insert(0,'py'); from p5map import *
DPI=300; PX=DPI/25.4; S=2.0
meta={m['strip']:m for m in json.load(open('out/RoyalCaroline_Rhino/print/backbone_trace_sheets.json'))}
lay={'A':(15,14,'P'),'B':(12,14,'L'),'C':(12,112,'L'),'D':(12,14,'L'),'E':(15,14,'P'),'F':(15,14,'P')}
scan_pages={1:['F'],2:['E'],3:['D'],4:['B','C'],5:['A']}
def expected(sid):
    m=meta[sid]; ox,oy,o=lay[sid]; W,H=((210,297) if o=='P' else (297,210))
    P=[(ox*PX+(X-m['xa'])*S*PX, oy*PX+(m['zb']-Z)*S*PX) for X,Z in m['marks']]
    return np.array(P),np.array(m['marks'],float),W*PX,H*PX
allpts=[]
for pg,sids in scan_pages.items():
    img=cv2.imread(f'scan2/p-{pg}.png'); g=cv2.medianBlur(cv2.cvtColor(img,cv2.COLOR_BGR2GRAY),5)
    c=cv2.HoughCircles(g,cv2.HOUGH_GRADIENT,dp=1,minDist=150,param1=100,param2=35,minRadius=30,maxRadius=50)
    C=c[0][:,:2] if c is not None else np.zeros((0,2))
    # page->scan: try 4 rotations of the page, fit similarity using all marks of all strips on the page
    E=[];M=[]
    for s in sids:
        e,mm,W,H=expected(s); E.append(e); M.append(mm)
    E=np.vstack(E); M=np.vstack(M)
    from shapely.geometry import Polygon
    from shapely import distance, points
    VV=Polygon(json.load(open('out/backbone_contour_v5.json'))['outer']).exterior
    hsv0=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); gm=((hsv0[...,0]>40)&(hsv0[...,0]<90)&(hsv0[...,1]>40)&(hsv0[...,2]>120))
    gy,gx=np.nonzero(gm); sel=np.random.default_rng(0).choice(len(gx),min(4000,len(gx)),replace=False); GP=np.float32(np.c_[gx[sel],gy[sel]])
    cands=[]
    for k in range(4):
        e=E.copy()
        for _ in range(k): e=np.c_[H - e[:,1], e[:,0]] if False else np.c_[ (W if _%2==0 else H) - e[:,1], e[:,0]]
        # recompute properly: rotate page k*90 deg clockwise
        e=E.copy(); w,h=W,H
        for _ in range(k): e=np.c_[h-e[:,1],e[:,0]]; w,h=h,w
        # scale ~0.94 guess; align centroid
        for sc in np.linspace(0.9,1.02,13):
            q=(e-e.mean(0))*sc+C.mean(0) if len(C) else e
            d=np.linalg.norm(q[:,None]-C[None],axis=2); j=d.argmin(1); r=d.min(1)
            if len(set(j))==len(j): cands.append((np.median(r),k,sc,j))
    cands.sort(key=lambda t:t[0]); scored=[]
    for med,k,sc,j in cands[:12]:
        e,mm,_,_=expected(sids[0]); src=C[j[0:4]]; Hm,_=cv2.findHomography(np.float32(src),np.float32(mm))
        if Hm is None: continue
        q=cv2.perspectiveTransform(GP[None],Hm)[0]; d=distance(points(q),VV); scored.append(((d<0.4).mean(),k,sc,j))
    scored.sort(key=lambda t:-t[0]); print('  contour fit',round(scored[0][0],2),'next',round(scored[1][0],2) if len(scored)>1 else None)
    _,k,sc,j=scored[0]
    for si,s in enumerate(sids):
        idx=slice(4*si,4*si+4); src=C[j[idx]]; dst=M[idx]
        Hm,_=cv2.findHomography(np.float32(src),np.float32(dst))
        # residual
        res=np.linalg.norm(cv2.perspectiveTransform(np.float32(src)[None],Hm)[0]-dst,axis=1).max()
        # dots
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV); Hh,Ss,Vv=[hsv[...,i].astype(int) for i in range(3)]
        mask=((Ss>70)&(Vv<170)).astype(np.uint8)
        mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7)))
        n,lab,st,cen=cv2.connectedComponentsWithStats(mask)
        # region of this strip in scan: map strip rectangle corners
        mm=meta[s]; inv=np.linalg.inv(Hm)
        rect=cv2.perspectiveTransform(np.float32([[mm['xa'],mm['za']],[mm['xb'],mm['za']],[mm['xb'],mm['zb']],[mm['xa'],mm['zb']]])[None],inv)[0]
        for i in range(1,n):
            a=st[i,4]
            if a<40 or a>900: continue
            x,y=cen[i]
            if cv2.pointPolygonTest(rect.reshape(-1,1,2),(float(x),float(y)),False)<0: continue
            hue=np.median(Hh[lab==i])
            col='G' if 35<=hue<=95 else ('B' if 95<hue<=140 else '?')
            X,Z=cv2.perspectiveTransform(np.float32([[[x,y]]]),Hm)[0,0]
            allpts.append(dict(strip=s,X=float(X),Z=float(Z),c=col,hue=float(hue),area=int(a)))
        print('page',pg,'strip',s,'rot',k*90,'scale %.3f'%sc,'mark residual %.2f mm'%res)
json.dump(allpts,open('scan2/dots.json','w'))
from collections import Counter
print(Counter((p['strip'],p['c']) for p in allpts))
