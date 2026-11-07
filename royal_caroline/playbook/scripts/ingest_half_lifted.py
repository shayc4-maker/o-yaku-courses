# ingest the builder's edited half-ship file (+Y side, after the lift) as the APPROVED outer lines v2: sample every face spline (Y,Z) at its X, keep the straight tops; the -Y side is the mirror. data/frames_outer_approved_v2.json
import json,numpy as np,rhino3dm as r3
NEW='/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/84b9e1b4-RoyalCaroline_frames_outer_half_lifted_v1.3dm'
f=r3.File3dm.Read(NEW); G={o.Attributes.Name:o.Geometry for o in f.Objects}
out={}
for b in range(1,46):
    out[str(b)]={}
    for nm in ('back','mid','front'):
        g=G['F%02d_%s_R'%(b,nm)]; d=g.Domain; ts=np.linspace(d.T0,d.T1,500); P=[g.PointAt(float(t)) for t in ts]; S=np.array([[p.Y,p.Z] for p in P]); X=P[0].X
        top=G.get('F%02d_%s_R_top'%(b,nm)); T=None
        if top is not None: s,e=top.PointAtStart,top.PointAtEnd; T=[[s.Y,s.Z],[e.Y,e.Z]]
        out[str(b)][nm]=dict(X=float(X),curve=S.round(4).tolist(),top=T,end=[float(S[0,0]),float(S[0,1])])
json.dump(out,open('data/frames_outer_approved_v2.json','w'))
print('faces',sum(len(v) for v in out.values()))
print('lower ends (X, Y, Z) of the faces, frames 1-10:')
for b in range(1,11):
    print(' frame',b,[(round(out[str(b)][nm]['X'],2),round(out[str(b)][nm]['end'][0],2),round(out[str(b)][nm]['end'][1],2)) for nm in ('back','mid','front')])
