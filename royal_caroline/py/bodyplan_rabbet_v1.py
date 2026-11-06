# body plan stations 1-8 refit: end point moved HORIZONTALLY to the keel half-width (Y=2.65) at the rabbet Z of the station X; spline through the new points; original forward body plan (plan_1b) as background
import json,sys,numpy as np
sys.path.insert(0,'py')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from scipy.interpolate import splprep,splev,CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import bodyplan_points_all as B
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4}; KB=2.65
C=json.load(open('data/bodyplan_splines_v1.json')); pts=json.load(open('data/rabbet_points_v1.json'))['points']; R=CubicSpline([p[0] for p in pts],[p[1] for p in pts],bc_type='natural')
STR={1:2,2:2}; new={}
for n in range(1,9):
    p=[list(q) for q in C[str(n)]['points']]; zr=round(float(R(XST[n])),2); old=p[0]; p[0]=[KB,zr]
    k=STR.get(n,0); q=np.array(p[:-1] if k else p)
    keep=[0]+[i for i in range(1,len(q)) if np.hypot(*(q[i]-q[i-1]))>1e-6]; q=q[keep]
    tck,_=splprep(q.T,k=3,s=0); u=np.linspace(0,1,600); y,z=splev(u,tck); d1=np.array(splev(u,tck,der=1)); d2=np.array(splev(u,tck,der=2))
    kap=(d1[0]*d2[1]-d1[1]*d2[0])/(d1[0]**2+d1[1]**2)**1.5; sc=int((np.diff(np.sign(kap))!=0).sum())
    line=np.c_[y,z]
    if k: line=np.r_[line,[p[-1]]]
    new[n]=dict(points=p,curve=line.round(3).tolist(),curvature_sign_changes=sc,old_first=old,rabbet_Z=zr,X=XST[n],old_sign_changes=C[str(n)]['curvature_sign_changes'])
    print('station %d: end (%.2f,%.2f) -> (%.2f,%.2f); curvature sign changes old %d new %d'%(n,old[0],old[1],KB,zr,C[str(n)]['curvature_sign_changes'],sc))
json.dump(new,open('data/bodyplan_rabbet_v1.json','w'))
cf=B.CFG['fwd']; im=Image.open('plans/plan_1b_aligned.png').convert('RGB'); cm=plt.cm.tab10
def draw(a,box,zoom):
    c=im.crop(box); a.imshow(c,extent=(box[0],box[2],box[3],box[1])); a.imshow(np.ones((2,2,4))*[1,1,1,0.35],extent=(box[0],box[2],box[3],box[1]))
    for n in range(1,9):
        col=cm((n-1)%10); L=np.array(new[n]['curve']); O=np.array(C[str(n)]['curve'])
        xo,yo=B.px(cf,O[:,0],O[:,1]); a.plot(xo,yo,'--',color=col,lw=.7,alpha=.8)
        x,y=B.px(cf,L[:,0],L[:,1]); a.plot(x,y,'-',color=col,lw=1.2)
        for yy,zz in ([(KB,new[n]['rabbet_Z'])]): px_,py_=B.px(cf,np.array([yy]),np.array([zz])); a.plot(px_,py_,'o',mfc='none',mec='lime',ms=7)
        if not zoom: a.text(x[-1],y[-1]-16,str(n),color=col,fontsize=11,weight='bold',ha='center')
    xk,yk=B.px(cf,np.array([KB,KB]),np.array([-4,120])); a.plot(xk,yk,color='gray',lw=.6)
    a.set_xlim(box[0],box[2]); a.set_ylim(box[3],box[1]); a.axis('off')
fig,ax=plt.subplots(figsize=(13,15.7),dpi=80); draw(ax,(2380,500,3750,2150),False); fig.savefig('qa/bodyplan_rabbet_v1_full.png',bbox_inches='tight'); plt.close(fig)
x0,y0=B.px(cf,np.array([-3.0]),np.array([40.0])); x1,y1=B.px(cf,np.array([14.0]),np.array([-4.0]))
bx=(int(min(x0[0],x1[0]))-20,int(min(y0[0],y1[0]))-20,int(max(x0[0],x1[0]))+20,int(max(y0[0],y1[0]))+20); print('zoom box',bx)
fig,ax=plt.subplots(figsize=(13,13*(bx[3]-bx[1])/(bx[2]-bx[0])),dpi=90); draw(ax,bx,True); fig.savefig('qa/bodyplan_rabbet_v1_zoom.png',bbox_inches='tight'); plt.close(fig)
