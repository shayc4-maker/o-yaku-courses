# side view v3: loft rebuilt with the approved END points prepended to stations 1-8 (curve otherwise unchanged); frames 1-8 silhouettes: red = previous (extended to the wall), blue = ends at the new loft, whole frame raised 0.6
import sys,json,numpy as np
sys.path.insert(0,'py')
import hull_new_sections as HN
E_=json.load(open('data/bodyplan_ends_proposed_v1.json'))
C2=json.load(open('data/bodyplan_splines_v1.json'))
for n,v in E_.items(): C2[n]['curve']=[list(v['end'])]+C2[n]['curve']; C2[n]['points']=[list(v['end'])]+C2[n]['points']
json.dump(C2,open('data/bodyplan_splines_v2_ends.json','w'))
HN.C=C2; HN._C={}; HN._CACHE='/tmp/claude-0/x/loft_ends_cache.pkl'; HN.SURF=None
import frames_batch_2d as FB
from scipy.interpolate import splprep,splev,CubicSpline
def hull_line_v2(X):
    P=HN.section(min(X,527.7)); zz=np.round(P[:,1],2); _,ui=np.unique(zz,return_index=True); P=P[ui]; P=P[np.argsort(P[:,1])]
    z0,z1=P[0,1],P[-1,1]; zs=np.r_[z0,np.linspace(z0,z1,15)[1:]]; pts=np.array([(float(np.interp(z,P[:,1],P[:,0])),float(z)) for z in zs])
    tk,u=splprep(pts.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tk); return np.c_[y,z]
R2=(lambda p:CubicSpline([q[0] for q in p],[q[1] for q in p],bc_type='natural'))(json.load(open('data/rabbet_points_v2_calibrated.json'))['points'])
rows={}
for b in range(1,9):
    xc=FB.XF[46-b-1]
    for nm,X in (('m',xc-4),('c',xc),('p',xc+4)):
        P=hull_line_v2(X); rows[(b,nm)]=(X,float(P[0,0]),float(P[0,1]))
    print('frame %d: end Y/Z (X-4,X,X+4) %s | minus calibrated rabbet (not raised) %s'%(b,[(round(rows[(b,k)][1],2),round(rows[(b,k)][2],2)) for k in 'mcp'],[round(rows[(b,k)][2]-float(R2(rows[(b,k)][0])),2) for k in 'mcp']))
json.dump({'%d_%s'%k:v for k,v in rows.items()},open('data/frames_ends_v3.json','w'))
