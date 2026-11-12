# the builder's approved lines file (his latest keel lines e7f275e3) + context (approved stations 16-18, approved frame 45 faces) + PROPOSED outer lines of the missing aft frames F46-F48 (points and splines, +Y half)
import json,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
SRC='/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/e7f275e3-RoyalCaroline_keel_lines_v3.3dm'
N=r3.File3dm.Read(SRC); f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; M={}
for i,l in enumerate(N.Layers): n=r3.Layer(); n.Name=l.Name; n.Color=l.Color; n.Visible=l.Visible; M[i]=f.Layers.Add(n)
for o in N.Objects: a=o.Attributes; a.LayerIndex=M[a.LayerIndex]; f.Objects.Add(o.Geometry,a)
print('copied',len(f.Objects),'objects from the builder file')
def layer(n,c): l=r3.Layer(); l.Name=n; l.Color=c; return f.Layers.Add(l)
def nurbs3(X,L,tol=0.02):
    P=np.c_[np.full(len(L),X),L]; tck,u=splprep(P.T,k=3,s=len(P)*tol**2); t,c,k=tck; m=len(c[0]); cv=r3.NurbsCurve(3,False,k+1,m)
    for i in range(m): cv.Points[i]=r3.Point4d(float(c[0][i]),float(c[1][i]),float(c[2][i]),1.0)
    for i,v in enumerate(t[1:-1]): cv.Knots[i]=float(v)
    return cv
C=json.load(open('data/bodyplan_centered_v1.json')); A5=json.load(open('data/frames_outer_approved_v5.json')); PR=json.load(open('data/aft_frames_proposal_v1.json'))
Ls=layer('APPROVED_context_stations_16_17_18 (body plan, +Y)',(120,120,120,255)); Lf=layer('APPROVED_context_frame_45_faces (+Y)',(0,0,0,255))
for n,X in ((16,36.8),(17,14.6),(18,0.0)):
    L=np.array(C[str(n)]['curve']); a=r3.ObjectAttributes(); a.LayerIndex=Ls; a.Name='station_%d X=%.1f'%(n,X); f.Objects.AddCurve(nurbs3(X,L),a)
for nm in ('back','mid','front'):
    v=A5['45'][nm]; L=np.array(v['curve']); L=np.vstack([L,np.array(v['top'])[1:]]) if v.get('top') else L; a=r3.ObjectAttributes(); a.LayerIndex=Lf; a.Name='F45_%s X=%.2f'%(nm,v['X']); f.Objects.AddCurve(nurbs3(v['X'],L),a)
Lc=layer('PROPOSED_aft_frames_46_48_outer_lines (splines, +Y)',(220,0,0,255)); Lp=layer('PROPOSED_aft_frames_46_48_points (ids Y,Z)',(220,120,0,255))
for k,v in PR.items():
    b,nm=k.split('_'); X=v['X']; L=np.array(v['curve']); a=r3.ObjectAttributes(); a.LayerIndex=Lc; a.Name='F%s_%s X=%.1f (%s)'%(b,nm,X,v['kind']); f.Objects.AddCurve(nurbs3(X,L),a)
    for i,(kind,y,z) in enumerate(v['points']): a=r3.ObjectAttributes(); a.LayerIndex=Lp; a.Name='F%s_%s_p%d %s Y%.2f Z%.2f'%(b,nm,i+1,kind,y,z); f.Objects.AddPoint(r3.Point3d(X,y,z),a)
f.Write('rhino/RoyalCaroline_approved_lines_with_aft_frames_proposal_v1.3dm',7); print('objects',len(f.Objects))
# picture: end view (Y-Z) of stations, frame 45 and the proposal; side view of the lower ends against the approved keel lines
fig,axs=plt.subplots(1,2,figsize=(22,12),gridspec_kw={'width_ratios':[1.1,1]})
a=axs[0]
for n in (16,17,18): L=np.array(C[str(n)]['curve']); a.plot(L[:,0],L[:,1],color='0.6',lw=1,ls='--'); a.text(L[-1,0]+.5,L[-1,1],'st %d'%n,color='0.4',fontsize=8)
for nm in ('back','mid','front'): v=A5['45'][nm]; L=np.array(v['curve']); a.plot(L[:,0],L[:,1],'k',lw=1.2)
cols={'46':'tab:red','47':'tab:blue','48':'tab:green'}
for k,v in PR.items():
    b,nm=k.split('_'); L=np.array(v['curve']); a.plot(L[:,0],L[:,1],color=cols[b],lw=1.4); P=np.array([[y,z] for _,y,z in v['points']]); a.plot(P[:,0],P[:,1],'o',color=cols[b],ms=3)
a.set_xlim(0,56); a.set_ylim(0,140); a.set_aspect('equal'); a.grid(alpha=.3); a.set_title('end view (Y-Z): grey dashed = approved stations 16/17/18, black = approved frame 45, red/blue/green = PROPOSED F46/F47/F48 faces (points = dots)')
a=axs[1]
S=json.load(open('data/keel_lines_builder_v3d.json'))
for ln,Pp,nm,t in S:
    Pp=np.array(Pp)
    if ln=='90': a.plot(Pp[:,0],Pp[:,1],color='0.8',lw=.6)
for k,v in PR.items():
    b,nm=k.split('_'); z0,z1=v['points'][0][2],v['points'][-1][2]; a.plot([v['X']]*2,[z0,z1],color=cols[b],lw=2); a.plot(v['X'],z0,'s',color=cols[b]); a.text(v['X']+.4,z0-3,'%.1f'%z0,fontsize=7,color=cols[b]); a.text(v['X']+.4,z1+1,'%.1f'%z1,fontsize=7,color=cols[b])
a.set_xlim(-12,48); a.set_ylim(-12,140); a.set_aspect('equal'); a.grid(alpha=.3); a.set_title('side view: lower end (square) and top of each proposed face over the approved keel group outlines')
fig.savefig('qa/aft_frames_proposal_v1.png',dpi=50,bbox_inches='tight')
