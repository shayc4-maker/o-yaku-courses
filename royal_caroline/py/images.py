import sys,json,numpy as np
from PIL import Image
S=sys.argv[1]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
meta=json.load(open(O+'/meta.json')); K=meta['K']; WLZ=meta['WLZ_mm']
zl=np.array(list(WLZ.values()))
def zfit(ys): return np.polyfit(ys,zl,1)   # z = a*y + b (mm)
f1a=zfit([2113.24,2010.99,1907.20,1802.92,1699.13,1597.16,1493.06,1287.56])
f1b=zfit([2003.18,1902.94,1800.12,1694.90,1591.62,1489.78,1385.70,1182.74])
fpr=zfit([2104.73,2001.84,1901.54,1795.99,1694.46,1591.90,1494.11,1287.92])
PV=np.array([4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28])
PR=np.array([4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40])
fx=np.polyfit(PV,PR,1); LO=(-0.00716,1271.3); X_BP=-80.0
frames=[]
def save(src,box,name):
    im=Image.open(src).convert('L').crop(box); im.save(PK+'/images/'+name,optimize=True); return im.size
# body plan aft (A1/2) left half -> Y negative
b=(1250,450,2394,2300); save(S+'/a/plan_1a_aligned.png',b,'bodyplan_aft_A1-2.png')
y0=(b[0]-2394)*K; y1=(b[2]-2394)*K; zb=np.polyval(f1a,b[3]); zt=np.polyval(f1a,b[1])
frames.append(dict(file='bodyplan_aft_A1-2.png',origin=[X_BP-0.5,y0,zb],xaxis=[0,1,0],yaxis=[0,0,1],w=y1-y0,h=zt-zb))
b=(2453,450,3750,2200); save(S+'/a/plan_1b_aligned.png',b,'bodyplan_fwd_A1-3.png')
y0=(b[0]-2453)*K; y1=(b[2]-2453)*K; zb=np.polyval(f1b,b[3]); zt=np.polyval(f1b,b[1])
frames.append(dict(file='bodyplan_fwd_A1-3.png',origin=[X_BP-0.5,y0,zb],xaxis=[0,1,0],yaxis=[0,0,1],w=y1-y0,h=zt-zb))
# profile A1/1 in XZ plane at Y=-100
b=(3900,100,11372,2400); save(S+'/a/plan_1a_aligned.png',b,'profile_A1-1.png')
x0=(b[0]-PR[0])*K; x1=(b[2]-PR[0])*K; zb=np.polyval(fpr,b[3]); zt=np.polyval(fpr,b[1])
frames.append(dict(file='profile_A1-1.png',origin=[x0,100.0,zb],xaxis=[1,0,0],yaxis=[0,0,1],w=x1-x0,h=zt-zb))
# plan view A1/4 in XY plane at Z=-30 ; account for CL tilt
b=(3900,150,11000,1300)
im=Image.open(S+'/a/plan_1b_aligned.png').convert('L').crop(b); sl=LO[0]
im=im.transform(im.size,Image.AFFINE,(1,0,0,sl,1,0),resample=Image.BICUBIC,fillcolor=255)
im.save(PK+'/images/halfbreadth_A1-4.png',optimize=True)
ycl=np.polyval(LO,b[0])-b[1]          # centreline row in sheared crop (constant)
x0=(np.polyval(fx,b[0])-PR[0])*K; x1=(np.polyval(fx,b[2])-PR[0])*K
yb=(ycl-(b[3]-b[1]))*K; yt=ycl*K
frames.append(dict(file='halfbreadth_A1-4.png',origin=[x0,yb,-30.0],xaxis=[1,0,0],yaxis=[0,1,0],w=x1-x0,h=yt-yb))
for fr in frames:
    fr['origin']=[float(v) for v in fr['origin']]; fr['w']=float(fr['w']); fr['h']=float(fr['h'])
json.dump(frames,open(PK+'/images/frames.json','w'),indent=1)
print(json.dumps(frames,indent=1))
