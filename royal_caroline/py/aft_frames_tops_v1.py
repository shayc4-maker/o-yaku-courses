# builder approved: aft frame tops go to the bulwark lower line S1. Iron lines (builder's arranged curves) unchanged below; only a tangent extension to S1 at each face X.
import json,numpy as np
from scipy.interpolate import BSpline,splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
d=json.load(open('data/aft_frames_builder_v1.json'))['curves']; S=np.array(json.load(open('data/bulwark_line_v3.json'))['S1'])
out={}; fig,a=plt.subplots(figsize=(11,12)); 
for k,c in sorted(d.items()):
    nm=k.split()[0]; cv=np.array(c['cv']); kn=np.array(c['knots']); kn=np.r_[kn[0],kn,kn[-1]]; X=cv[0,0]
    sp=BSpline(kn,cv[:,1:],c['deg']); t=np.linspace(kn[3],kn[-4],400); P=sp(t); Z1=np.interp(X,S[:,0],S[:,1])
    tan=P[-1]-P[-6]; tan/=np.linalg.norm(tan); dz=Z1-P[-1,1]; top=P[-1]+tan*dz/tan[1]
    idx=np.r_[np.arange(0,len(P)-1,25),len(P)-1]; Q=np.vstack([P[idx],top])
    tck,u=splprep(Q.T,s=0,k=3); R=np.array(splev(np.linspace(0,1,300),tck)).T
    out[nm]=dict(X=X,pts=Q.round(3).tolist(),top_Y=round(top[0],2),top_Z=round(Z1,2),added_len=round(float(np.linalg.norm(top-P[-1])),2))
    a.plot(R[:,0],R[:,1],lw=1); a.plot(*top,'ro',ms=4); a.plot(P[:,0],P[:,1],'k',lw=.4); a.text(top[0]+.5,top[1]+.3,nm,fontsize=7)
    print(nm,'X=%g'%X,'+%.2f mm to Z %.2f, Y %.2f'%(out[nm]['added_len'],Z1,top[0]))
a.set_aspect('equal'); a.grid(alpha=.3); a.set_title('Aft frames 46-48 faces, Y-Z. Black = your lines, colour = same + tangent extension to bulwark S1 (red dot)')
fig.savefig('qa/aft_frames_tops_v1.png',dpi=70,bbox_inches='tight'); json.dump(out,open('data/aft_frames_tops_v1.json','w'))
