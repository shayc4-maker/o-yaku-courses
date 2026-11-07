# ingest the builder's corrected outer-lines Rhino file as the APPROVED geometry (frames 1-45, faces back/mid/front): sample every spline (Y,Z at the face X), keep the straight top segments, check mirror symmetry; for the 3 faces the builder edited asymmetrically (F03 front, F06 front, F36 back) choose one side by objective criteria (no belly, fewest curvature sign changes), tie -> +Y side. data/frames_outer_approved_v1.json (+Y master side; the -Y side is its mirror).
import json,numpy as np,rhino3dm as r3
f=r3.File3dm.Read('/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/c8f595d5-RoyalCaroline_frames_outer_lines_v1.3dm'); L={i:f.Layers[i].Name for i in range(len(f.Layers))}
G={o.Attributes.Name:o.Geometry for o in f.Objects if L[o.Attributes.LayerIndex].startswith('OUTER')}
def sample(g,n=500):
    d=g.Domain; ts=np.linspace(d.T0,d.T1,n); P=[g.PointAt(float(t)) for t in ts]; return np.array([[p.Y,p.Z] for p in P]),P[0].X
def metrics(S):
    sl=np.r_[0,np.cumsum(np.hypot(*np.diff(S,axis=0).T))]; t=np.arange(0,sl[-1],1.0); Y=np.interp(t,sl,S[:,0]); Z=np.interp(t,sl,S[:,1])
    from scipy.ndimage import gaussian_filter1d as gf; Y=gf(Y,2); Z=gf(Z,2); d1y=np.gradient(Y); d1z=np.gradient(Z); k=d1y*np.gradient(d1z)-d1z*np.gradient(d1y); s=np.sign(k[3:-3][np.abs(k[3:-3])>2e-3]); sc=int((np.diff(s)!=0).sum())
    iw=int(np.argmax(S[:,0])); z=S[:iw+1,1]; drop=float((np.maximum.accumulate(z)-z).max()); belly=float(S[0,1]-S[:,1].min()); return sc,drop,belly
out={}; chosen=[]
for b in range(1,46):
    out[str(b)]={}
    for nm in ('back','mid','front'):
        R,X=sample(G['F%02d_%s_R'%(b,nm)]); Lm,_=sample(G['F%02d_%s_L'%(b,nm)]); Lm=np.c_[-Lm[:,0],Lm[:,1]]
        asym=float(np.abs(R-Lm).max()); side='R'
        if asym>1e-3:
            mr,ml=metrics(R),metrics(Lm); score=lambda m:(m[2]>0.02 or m[1]>0.02, m[0], m[1]+m[2]); side='R' if score(mr)<=score(ml) else 'L'; chosen.append((b,nm,round(asym,2),side,mr,ml))
        S=R if side=='R' else Lm
        top=G.get('F%02d_%s_R_top'%(b,nm)); T=None
        if top is not None: s,e=top.PointAtStart,top.PointAtEnd; T=[[s.Y,s.Z],[e.Y,e.Z]] if side=='R' else None
        if top is not None and T is None: s,e=G['F%02d_%s_L_top'%(b,nm)].PointAtStart,G['F%02d_%s_L_top'%(b,nm)].PointAtEnd; T=[[-s.Y,s.Z],[-e.Y,e.Z]]
        out[str(b)][nm]=dict(X=float(X),side=side,curve=S.round(4).tolist(),top=T)
json.dump(out,open('data/frames_outer_approved_v1.json','w'))
print('faces',sum(len(v) for v in out.values()),'asymmetric faces (the builder edited the two sides differently):')
for c in chosen: print('  frame %d %s: R vs mirror(L) max diff %.2f mm | R (sign changes, Z drop, belly)=%s | L=%s -> %s side'%(c[0],c[1],c[2],tuple(round(v,3) for v in c[4]),tuple(round(v,3) for v in c[5]),c[3]))
