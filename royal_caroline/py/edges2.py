import numpy as np, json, sys
sys.path.insert(0,'py'); from p5map import *
from PIL import Image
from scipy.spatial import cKDTree
from scipy.ndimage import binary_dilation
D=json.load(open('scan2/dots_merged.json'))
P=np.array([[d['X'],d['Z']] for d in D]); C=np.array([d['c'] for d in D])
im=np.array(Image.open('a/plan_5_aligned.png').convert('L'))<140
K=1/ (model_to_p5(1,0)[0]-model_to_p5(0,0)[0])  # mm per px
def sc(a,b):
    L=np.hypot(*(b-a)); n=max(4,int(L/0.06)); t=np.linspace(0.12,0.88,n) if L>3 else np.linspace(0.2,0.8,n)
    pts=a+(b-a)*t[:,None]; u,v=model_to_p5(pts[:,0],pts[:,1])
    return im[np.round(v).astype(int),np.round(u).astype(int)].mean()
def best(a,b,r=0.35,st=0.07):
    offs=np.arange(-r,r+1e-9,st); d=(b-a)/np.hypot(*(b-a)); n=np.array([-d[1],d[0]])
    bs=0
    for oa in offs:
        for ob in offs:
            s=sc(a+n*oa,b+n*ob)
            if s>bs: bs=s
    return bs
tr=cKDTree(P); out=[]
for i in range(len(P)):
    nb=tr.query(P[i],k=9)[1][1:]
    for j in nb:
        if j<i and i in tr.query(P[j],k=9)[1][1:]: continue
        L=np.hypot(*(P[j]-P[i]))
        if L>60: continue
        out.append((min(i,j),max(i,j),L,best(P[i],P[j])))
out=sorted(set(out))
np.save('scan2/cand2.npy',np.array(out)); A=np.array(out)
print(len(A), np.histogram(A[:,3],bins=[0,.6,.7,.8,.9,.95,.98,1.01])[0])
