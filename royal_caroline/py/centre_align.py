# ONE centre for all views: every body plan station Y and every top-view waterline Y is re-expressed from the DRAWN centreline of its own view (fitted on the dash-dot centre ink: forward body plan Yc(Z)=1.645-0.00799*Z, aft body plan Yc(Z)=-0.728+0.00701*Z (raw, before the aft 1.0325 scale), top view Yc(X)=-1.166+0.00717*X). Plan dimensions (measured): keel half-width 2.6 (fwd 2.60 / aft 2.65), neck half-width 1.8 (wall ink centre - centreline at clean rows). Station end points: Y moved HORIZONTALLY to the neck wall, Z kept.
import json,numpy as np
C=json.load(open('data/bodyplan_splines_v1.json')); W=json.load(open('data/wl_top_points_all.json')); E=json.load(open('data/bodyplan_ends_proposed_v1.json')); SF=1.0325; NECK=1.8; KEEL=2.62
def ycs(n,z): return (1.645-0.00799*z) if n<=8 else SF*(-0.728+0.00701*z)
out={}
for n in range(1,19):
    d=C[str(n)]; P=np.array(d['points']); L=np.array(d['curve'])
    P2=np.c_[P[:,0]-np.array([ycs(n,z) for z in P[:,1]]),P[:,1]]; L2=np.c_[L[:,0]-np.array([ycs(n,z) for z in L[:,1]]),L[:,1]]
    out[str(n)]=dict(points=P2.round(3).tolist(),curve=L2.round(3).tolist(),curvature_sign_changes=d['curvature_sign_changes'])
json.dump(out,open('data/bodyplan_centered_v1.json','w'))
ends={n:dict(first=[round(float(out[n]['points'][0][0]),3),out[n]['points'][0][1]],end=[NECK,E[n]['end'][1]],end_tip_centered=[round(float(E[n]['end'][0]-ycs(int(n),E[n]['end'][1])),3),E[n]['end'][1]]) for n in E}
json.dump(ends,open('data/bodyplan_ends_centered_v1.json','w'))
Wc={}
for k,v in W.items(): Wc[k]=dict(z=v['z'],points_XY=[[x,round(y-(-1.166+0.00717*x),3)] for x,y in v['points_XY']],length_mm=v.get('length_mm'))
json.dump(Wc,open('data/wl_top_centered_v1.json','w'))
json.dump(dict(centre_fwd='Yc(Z)=1.645-0.00799*Z',centre_aft_raw='Yc(Z)=-0.728+0.00701*Z (before SF=1.0325)',centre_top='Yc(X)=-1.166+0.00717*X',keel_half=KEEL,neck_half=NECK,note='keel walls fwd -1.0/4.19 and aft 1.96/-3.33 (centre to centre 5.19 / 5.29); neck right wall 3.22-3.31 minus centreline ~1.5 = 1.64-1.86'),open('data/plan_centre_v1.json','w'),indent=1)
for n in (1,2,3,4,8,9,18): print('station',n,'first point old',C[str(n)]['points'][0],'-> centered',out[str(n)]['points'][0],'| widest Y old %.2f -> %.2f'%(max(np.array(C[str(n)]['curve'])[:,0]),max(np.array(out[str(n)]['curve'])[:,0])))
print('ends (Y at the neck, Z kept):',{n:v['end'] for n,v in ends.items()}); print('old hook tips relative to the true centre:',{n:v['end_tip_centered'] for n,v in list(ends.items())[:3]})
