import sys,json,numpy as np,cv2
sys.path.insert(0,'py')
from refdxf import load
from scipy import ndimage as ndi
L=load(sys.argv[1]); dil=float(sys.argv[2]); out=sys.argv[3]
use=['01_BODY_OUTER','02_KEELSON','03_STERN_KNEE','04_AFT_DIVISIONS','05_KEEL_HOG_FALSEKEEL','06_STEM_APRON','07_HEAD_GRIPE']+(sys.argv[4].split(',') if len(sys.argv)>4 else [])
S=20.0 # px per mm
x0,z0,x1,z1=-25,-12,625,125
W=int((x1-x0)*S);H=int((z1-z0)*S)
img=np.zeros((H,W),np.uint8)
def P(x,z): return (int(round((x-x0)*S)),int(round((z1-z)*S)))
for l in use:
    for s in L.get(l,[]):
        a=np.array(s)
        if a[:,0].max()<-20: continue
        cv2.polylines(img,[np.array([P(x,z) for x,z in a],np.int32)],False,255,1)
k=int(dil*S)*2+1
walls=cv2.dilate(img,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
free=(walls==0)
lab,n=ndi.label(free)
sizes=ndi.sum(free,lab,range(1,n+1))
border=set(np.unique(np.r_[lab[0],lab[-1],lab[:,0],lab[:,-1]]))
regs=[]
for i in range(1,n+1):
    if i in border: continue
    area=sizes[i-1]/S/S
    if area<0.8: continue
    m=(lab==i).astype(np.uint8)
    m=cv2.dilate(m,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))  # undo wall dilation
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c=max(cs,key=cv2.contourArea)
    c=cv2.approxPolyDP(c,0.6,True)[:,0,:]
    ring=[(x/S+x0,z1-y/S) for x,y in c]
    regs.append({'id':len(regs),'area':area,'ring':ring+[ring[0]],'holes':[]})
regs.sort(key=lambda r:-r['area'])
for i,r in enumerate(regs): r['id']=i
json.dump(regs,open(out,'w'))
print(n,'components;',len(regs),'closed regions;',[round(r['area']) for r in regs[:30]])
