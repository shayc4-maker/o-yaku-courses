import sys,json,numpy as np
from PIL import Image, ImageDraw
S=sys.argv[1]
meta=json.load(open(S+'/out/meta.json')); K=meta['K']; WLZ=meta['WLZ_mm']
st=np.load(S+'/out/stations.npy',allow_pickle=True).item()
PV=[4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28]
LO=(-0.00716,1271.3)
def ycross(P,z):
    out=[]
    for i in range(len(P)-1):
        z0,z1=P[i,1],P[i+1,1]
        if (z0-z)*(z1-z)<=0 and z0!=z1:
            t=(z-z0)/(z1-z0); out.append(P[i,0]+t*(P[i+1,0]-P[i,0]))
    return max(out) if out else None
im=Image.open(S+'/a/plan_1b_aligned.png').convert('RGB'); d=ImageDraw.Draw(im)
cols={'I':(255,0,0),'II':(255,140,0),'III':(200,200,0),'IV':(0,170,0),'V':(0,170,255),'VI':(0,0,255),'VII':(200,0,200)}
for i,x in enumerate(PV):
    s=18-i; P=st.get(f'{s}_1a', st.get(f'{s}_1b')); cl=np.polyval(LO,x)
    for n,c in cols.items():
        y=ycross(P,WLZ[n])
        if y is None: continue
        yy=cl-y/K; d.ellipse([x-7,yy-7,x+7,yy+7],outline=c,width=3)
im.crop((4000,150,10800,1300)).resize((2267,383),Image.LANCZOS).save(S+'/pv_ov.png')
im.crop((8700,200,9500,800)).save(S+'/pv_ov5.png')
im.crop((5700,250,6800,1250)).resize((825,750)).save(S+'/pv_ov13.png')
