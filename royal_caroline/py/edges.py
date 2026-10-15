import numpy as np, json, sys
sys.path.insert(0,'py'); from p5map import *
from PIL import Image
from scipy.spatial import cKDTree
D=json.load(open('scan2/dots_merged.json'))
P=np.array([[d['X'],d['Z']] for d in D]); C=np.array([d['c'] for d in D])
im=np.array(Image.open('a/plan_5_aligned.png').convert('L'))<140
def score(a,b,w=2):
    L=np.hypot(*(b-a)); n=max(3,int(L/0.08)); t=np.linspace(0.05,0.95,n)
    pts=a+(b-a)*t[:,None]; u,v=model_to_p5(pts[:,0],pts[:,1])
    d=(b-a)/L; nrm=np.array([-d[1],d[0]]); hit=np.zeros(n,bool)
    # perpendicular in pixel space (Z flips)
    pu,pv=nrm[0],-nrm[1]
    for s in range(-w,w+1):
        uu=np.round(u+pu*s).astype(int); vv=np.round(v+pv*s).astype(int)
        hit|=im[vv,uu]
    return hit.mean()
tr=cKDTree(P); E=[]
for i in range(len(P)):
    for j in tr.query_ball_point(P[i],30):
        if j<=i: continue
        E.append((i,j,np.hypot(*(P[j]-P[i])),score(P[i],P[j])))
E=np.array(E); print(len(E))
np.save('scan2/cand_edges.npy',E)
# baseline: random segments inside hatch
print('score hist',np.histogram(E[:,3],bins=[0,.5,.6,.7,.8,.85,.9,.95,1.01])[0])
