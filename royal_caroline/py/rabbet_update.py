# updated rabbet line: the calibrated ink-based upper rabbet (v2) lowered by a smooth deficit d(X) so that it passes exactly through the approved station END points at the bow (iron lines): d=0 up to station 3 (X=472), then PCHIP to the ends of stations 2 and 1. Keel half-width stays 2.65 (plan).
import json,numpy as np
from scipy.interpolate import CubicSpline,PchipInterpolator
P2=json.load(open('data/rabbet_points_v2_calibrated.json'))['points']; R=CubicSpline([p[0] for p in P2],[p[1] for p in P2],bc_type='natural')
E=json.load(open('data/bodyplan_ends_proposed_v1.json')); XST={1:527.8,2:505.8,3:472.0}
xs=[472.0,XST[2],XST[1]]; d=[0.0]+[E[str(n)]['end'][1]-float(R(XST[n])) for n in (2,1)]
D=PchipInterpolator(xs,d,extrapolate=False); dd=lambda x: np.where(x<=472.0,0.0,np.nan_to_num(D(np.clip(x,472.0,527.8)),nan=d[-1]))
knots=sorted(set([p[0] for p in P2 if p[0]<472]+[472.0,480,490,500,505.8,510,515,520,525,527.8]))
pts=[[round(float(x),2),round(float(R(x)+dd(np.array(x))),2)] for x in knots]
json.dump(dict(points=pts,note='rabbet v3: v2 calibrated minus smooth deficit through the approved station ends 2 and 1; d(505.8)=%.2f d(527.8)=%.2f'%(d[1],d[2])),open('data/rabbet_points_v3_ends.json','w'))
R3=CubicSpline([p[0] for p in pts],[p[1] for p in pts],bc_type='natural')
print('deficit at stations 2,1: %.2f %.2f'%(d[1],d[2])); print('check ends:',[(n,round(float(R3(XST[n])),2),E[str(n)]['end'][1]) for n in (1,2,3)])
print('rabbet v3 at X=500,510,520,525,528:',[round(float(R3(x)),2) for x in (500,510,520,525,528)],' v2:',[round(float(R(x)),2) for x in (500,510,520,525,528)])
E3=json.load(open('data/frames_ends_v3.json'))
for b in (1,2,3,4):
    print('frame',b,'loft end minus new rabbet:',[round(E3['%d_%s'%(b,k)][2]-float(R3(E3['%d_%s'%(b,k)][0])),2) for k in 'mcp'])
