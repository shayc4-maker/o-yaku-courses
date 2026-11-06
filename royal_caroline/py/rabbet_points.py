# rabbet line (upper of the double black line on the sheer plan A1/1): ink centred per column, minimum knots for a cubic spline (tol), overshoot of the frame bottoms vs it
import json,numpy as np
from PIL import Image
from scipy.interpolate import CubicSpline
Image.MAX_IMAGE_PIXELS=None
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
im=np.array(Image.open('plans/plan_1a_aligned.png').convert('L'))
GRID=[9.2,17.8,26.8,35.4,44.1]
def runs(X,zlo,zhi):
    c=int(round((X-X0)/KX)); col=im[:,c-2:c+3].min(axis=1); a=int(ZR-zhi/KZ); b=int(ZR-zlo/KZ); d=col[a:b]<110; out=[];i=0
    while i<len(d):
        if d[i]:
            j=i
            while j<len(d) and d[j]: j+=1
            out.append(round((ZR-(a+(i+j)/2))*KZ,2)); i=j
        else: i+=1
    return out
# knots read from the ink centre of the upper line of the double black line (checked at X=400..528 step 10 and midships step 50)
pts=[(30,0.0),(100,-0.04),(200,0.09),(300,0.26),(400,0.34),(430,0.47),(450,0.85),(460,1.66),(470,3.02),(480,4.93),(490,7.4),(500,10.88),(510,15.64),(520,22.14),(528,28.8)]
cs=CubicSpline([p[0] for p in pts],[p[1] for p in pts],bc_type='natural')
X=np.array([p[0] for p in pts],float); Z=np.array([p[1] for p in pts])
chk=[(Xc,float(min(runs(Xc,-3,32),key=lambda z:abs(z-cs(Xc))))) for Xc in (60,150,250,350,415,440,455,465,475,485,495,505,515,525)]
print('check (X, ink, spline):',[(x,z,round(float(cs(x)),2)) for x,z in chk])
rows=json.load(open('data/frames_bottom_side.json')); over={}
for b,nm,x,hk,fl,st in rows:
    d=hk-float(cs(x)); over.setdefault(int(b),[]).append(round(d,2))
json.dump(dict(points=[list(p) for p in pts],overshoot=over),open('data/rabbet_points_v1.json','w'))
print({b:min(v) for b,v in over.items()})
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig,axs=plt.subplots(3,1,figsize=(19,20),gridspec_kw={'height_ratios':[.5,1.1,.8]})
for a,(xl,zl) in zip(axs,(((-20,570),(-14,62)),((440,545),(-12,45)),((220,330),(-12,14)))):
    box=(int((xl[0]-X0)/KX)-5,int(ZR-zl[1]/KZ)-5,int((xl[1]-X0)/KX)+5,int(ZR-zl[0]/KZ)+5); c=Image.open('plans/plan_1a_aligned.png').convert('RGB').crop(box)
    a.imshow(c,extent=(box[0]*KX+X0,box[2]*KX+X0,(ZR-box[3])*KZ,(ZR-box[1])*KZ),aspect='equal')
    t=np.linspace(30,528,2000); a.plot(t,cs(t),color='lime',lw=1)
    for i,(px,pz) in enumerate(pts):
        if xl[0]<=px<=xl[1]: a.plot(px,pz,'o',mfc='none',mec='m',ms=7); a.text(px,pz+(2 if a is not axs[2] else 1),'%d (%.1f, %.2f)'%(i+1,px,pz),fontsize=7,color='m',ha='center')
    byf={}
    for b,nm,x,hk,fl,st in rows: byf.setdefault(b,{})[nm]=(x,hk,fl,st)
    for b,d in byf.items():
        xs3=[d[k][0] for k in ('m','c','p')]
        if xl[0]-8<xs3[1]<xl[1]+8: a.plot(xs3,[d[k][1] for k in ('m','c','p')],color='r',lw=1.5)
    a.set_xlim(*xl); a.set_ylim(*zl)
axs[0].set_title('Rabbet line (upper of the double black line): reference points (magenta, id and X,Z) + spline (green); red = frame bottom at the keel wall, NOT shifted')
fig.savefig('qa/rabbet_points_v1.png',dpi=55,bbox_inches='tight')
