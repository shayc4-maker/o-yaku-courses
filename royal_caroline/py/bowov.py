import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from bowsurf import *
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS=None
S=sys.argv[2]; QA=O+'/RoyalCaroline_Rhino/qa'
SEC={float(k):np.array(v) for k,v in json.load(open(O+'/bow_sections.json')).items()}
def ycont(z):
    out=[(x,float(np.interp(z,s[:,1],s[:,0]))) for x,s in sorted(SEC.items()) if s[0,1]<=z<=s[-1,1]]
    if z<=ZTOPB: out.append((Xr(z),YR))
    return np.array(sorted(out))
# (a) A1/4
PV=np.array([4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28])
PR=np.array([4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40])
f=np.polyfit(PV,PR,1); LO=(-0.00716,1271.3); K=1000/244.8/48
pxA=lambda X:(np.asarray(X)/K+PR[0]-f[1])/f[0]
pyA=lambda X,Y: np.polyval(LO,pxA(X))-np.asarray(Y)/K
im=Image.open(S+'/a/plan_1b_aligned.png').convert('RGB'); d=ImageDraw.Draw(im)
for n,z in WLZ.items():
    if n=='BASE': continue
    c=ycont(z)
    if len(c)>1: d.line(list(zip(pxA(c[:,0]),pyA(c[:,0],c[:,1]))),fill=(255,0,0),width=2)
u0,u1=int(pxA(510)),int(pxA(565)); v1=int(pyA(530,-2)); v0=int(pyA(530,50))
im.crop((u0,v0,u1,v1)).resize(((u1-u0)*2,(v1-v0)*2)).save(QA+'/bow1_on_A1-4_waterlines.png')
# (b) A1/1 profile
pxP=lambda X: np.asarray(X)/K+4194.98; pyP=lambda Z: 2104.73-np.asarray(Z)*102.1/8.689
im=Image.open(S+'/a/plan_1a_aligned.png').convert('RGB'); d=ImageDraw.Draw(im)
zz=np.linspace(ra[0,1],ZTOPB,100); d.line(list(zip(pxP([Xr(z) for z in zz]),pyP(zz))),fill=(255,0,0),width=3)
xs=sorted(SEC); d.line(list(zip(pxP(xs),pyP([SEC[x][-1,1] for x in xs]))),fill=(0,160,0),width=3)
for x in xs[::3]:
    s=SEC[x]; d.line([(pxP(x),pyP(s[0,1])),(pxP(x),pyP(s[-1,1]))],fill=(0,0,255),width=1)
im.crop((int(pxP(495)),int(pyP(125)),int(pxP(575)),int(pyP(-12)))).save(QA+'/bow2_on_A1-1_profile.png')
# (c) 4b and 4a plan views
A=0.08528; Bc=-67.8; CY=1086
px4=lambda X:(np.asarray(X)-Bc)/A; py4=lambda Y: CY-np.asarray(Y)/A
cols={50:(255,0,0),69.5:(0,170,0),80:(255,140,0),86:(0,0,255)}
for nm in ('plan_4b','plan_4a'):
    im=Image.open(S+'/t/'+nm+'.tif').convert('L').convert('RGB'); d=ImageDraw.Draw(im)
    for z,col in cols.items():
        c=ycont(z)
        if len(c)>1:
            for sg in (1,-1): d.line(list(zip(px4(c[:,0]),py4(sg*c[:,1]))),fill=col,width=4)
    im.crop((int(px4(495)),int(py4(70)),int(px4(575)),int(py4(-70)))).save(QA+f'/bow3_on_{nm}.png')
print('ok')
