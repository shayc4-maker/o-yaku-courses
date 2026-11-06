# All 18 stations: splines through the approved points (+ shared foot points F), body plan drawing and photo overlays
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import splprep,splev
import bodyplan_points_all as B
A=json.load(open('data/bodyplan_points_approved.json')); Fp=json.load(open('data/bodyplan_F_points.json')); Faft=A['F']; Ffwd=Fp['F_fwd']
SF=1.0325   # aft plan (A1/2) Y scale correction: stations 9-18 and 8 sat 3.1 % inside the forward-plan stations 1-7 and the builder splines
P={n:[list(p) for p in A[str(n)]] for n in range(1,19)}
for n in range(8,19): P[n]=[[round(y*SF,2),z] for y,z in P[n]]
Faft=[round(Faft[0]*SF,2),Faft[1]]
# shared foot point F and the shared second point G of stations 6,7,8 (forward plan, circled by the builder)
for n in (4,6,7,8): P[n][0]=list(Ffwd)
G=[round(float(np.mean([P[n][1][0] for n in (6,7,8)])),2), round(sorted(P[n][1][1] for n in (6,7,8))[1]+0.15,2)]
for n in (6,7,8): P[n][1]=list(G)
for n in (9,10,11,12): P[n]=[list(Faft)]+P[n]
print('G',G)
STR={1:2,2:2}      # stations with a straight top: last 2 points = corner + top
COL=plt.cm.tab20(np.linspace(0,1,20)); curves={}
for n in range(1,19):
    p=np.array(P[n]); k=STR.get(n,0); q=p[:-1] if k else p
    # drop exact duplicates
    keep=[0]+[i for i in range(1,len(q)) if np.hypot(*(q[i]-q[i-1]))>1e-6]; q=q[keep]
    tck,_=splprep(q.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tck)
    d1=np.c_[splev(np.linspace(0,1,600),tck,der=1)]; d2=np.c_[splev(np.linspace(0,1,600),tck,der=2)]
    kap=(d1[0]*d2[1]-d1[1]*d2[0])/(d1[0]**2+d1[1]**2)**1.5; sc=int((np.diff(np.sign(kap))!=0).sum())
    line=np.c_[y,z]; 
    if k: line=np.r_[line,[p[-1]]]
    curves[n]=dict(points=P[n],curve=line.round(3).tolist(),curvature_sign_changes=sc)
    # deviation from the builder spline (nearest point distance)
    S=B.ST[f'ST{n:02d}'][:,1:]; from scipy.spatial import cKDTree; t=cKDTree(S); dd=t.query(line[::6])[0]
    print(f'ST{n:02d}: {len(P[n])} pts, curvature sign changes {sc}, distance to builder spline: mean {dd.mean():.2f} max {dd.max():.2f} mm')
json.dump(curves,open('data/bodyplan_splines_v1.json','w'))
# drawings
def pxc(cf,y,z): return B.px(B.CFG[cf],y,z)
for nm,plan,cf,box,ns,out,fs in (('fwd','plans/plan_1b_aligned.png','fwd',(2380,500,3750,2150),range(1,9),'qa/bodyplan_final_fwd.png',(13,15.7)),('aft','plans/plan_1a_aligned.png','aft',(1250,420,2400,2300),range(8,19),'qa/bodyplan_final_aft.png',(10,18.6))):
    im=Image.open(plan).convert('RGB').crop(box); fig,ax=plt.subplots(figsize=fs,dpi=110); ax.imshow(im,extent=(box[0],box[2],box[3],box[1])); ax.imshow(np.ones((2,2,4))*[1,1,1,0.45],extent=(box[0],box[2],box[3],box[1]))
    for n in ns:
        L=np.array(curves[n]['curve']); x,y=pxc(cf,L[:,0]/(SF if cf=='aft' else 1.0),L[:,1]); ax.plot(x,y,'-',color=COL[(n*3)%20],lw=1.3)
        ax.text(x[-1],y[-1]-16,str(n),color=COL[(n*3)%20],fontsize=11,weight='bold',ha='center')
    ax.set_xlim(box[0],box[2]); ax.set_ylim(box[3],box[1]); ax.axis('off'); fig.savefig(out,bbox_inches='tight'); plt.close(fig)
fig,ax=plt.subplots(figsize=(15,9.5),dpi=110)
for n in range(1,19):
    L=np.array(curves[n]['curve']); s=1 if n<=8 else -1
    ax.plot(s*L[:,0],L[:,1],'-',color=COL[(n*3)%20],lw=1.4); ax.text(s*L[-1,0],L[-1,1]+2,str(n),color=COL[(n*3)%20],fontsize=10,ha='center')
for z,lbl in zip((8.7,17.4,26.1,34.8,43.4,52.1,69.5),('I','II','III','IV','V','VI','VII')): ax.axhline(z,color='#bbb',lw=.5); ax.text(-82,z+.5,lbl,fontsize=8,color='#777')
ax.axvline(0,color='k',lw=.6,ls='-.'); ax.set_aspect('equal'); ax.set_xlim(-85,85); ax.set_ylim(-3,140); ax.set_title('Body plan: stations 9-18 (left, aft view) and 1-8 (right, forward view); Y mm, Z mm',fontsize=10)
fig.savefig('qa/bodyplan_final_clean.png',bbox_inches='tight')
