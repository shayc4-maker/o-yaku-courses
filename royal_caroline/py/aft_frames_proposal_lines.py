# PROPOSAL (not approved): outer lines of the missing aft frames F46-F48 (faces X-4, X, X+4) by the approved points method (py/frames_outer_all.py): original body plan stations 16/17/18 lead, original waterlines give the progression
import json,numpy as np
src=open('py/frames_outer_all.py').read().split("out={}; bad=[]; RAW={}")[0]; exec(src)
XC={46:28.0,47:17.0,48:6.0}          # centres: pitch 11 from frame 45 (X=39): double frame 8 mm + gap 3 mm (builder, earlier rounds)
P={}
for b,xc in XC.items():
    for nm,X in (('back',xc-4),('mid',xc),('front',xc+4)):
        pts,kind=face(X)
        if pts is None: print('outside',b,nm,X); continue
        corner=any(p[0]=='corner' for p in pts)
        if kind.startswith('between'):
            a_,b_=[int(x) for x in kind.split(' ')[1].split('-')]; tt=(X-XS[a_])/(XS[b_]-XS[a_]); v=(1-tt)*tangent_at(a_,None)+tt*tangent_at(b_,None); tan0=v/np.hypot(*v)
        else: tan0=tangent_at(int(kind.split(' ')[1]),None)
        L=curve(pts,corner,tan0); P[(b,nm)]=dict(X=X,kind=kind,points=[[p[0],round(float(p[1]),3),round(float(p[2]),3)] for p in pts],curve=L.round(3).tolist())
        print('F%d %-5s X=%5.1f %-16s %2d points; lower end (Y %.2f, Z %.2f); top (Y %.2f, Z %.2f)'%(b,nm,X,kind,len(pts),pts[0][1],pts[0][2],pts[-1][1],pts[-1][2]))
json.dump({'%d_%s'%k:v for k,v in P.items()},open('data/aft_frames_proposal_v1.json','w'))
