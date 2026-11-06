# Keelson inner line from the builder's STEP: reference spline = the ramp vertices of the bottom chain (plateau/notch vertices removed); new line = constant offset below it; pockets from his plateaus, raised where needed for walls >= W on both sides
import sys,json,numpy as np
OFF=float(sys.argv[1]) if len(sys.argv)>1 else 1.0; W=float(sys.argv[2]) if len(sys.argv)>2 else 1.0
from scipy.interpolate import UnivariateSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
C=np.load('/tmp/claude-0/x/keelson_chain.npy')
# bottom chain = chain part below the upper line: split at the point of max X (nose); chain starts at min X
i_end=int(np.argmax(C[:,0])); A=C[:i_end+1]; B=C[i_end:]
def ismaxz(ch): return ch[:,1].mean()
low,up=(A,B) if A[:,1].mean()<B[:,1].mean() else (B,A)
low=low if low[0,0]<low[-1,0] else low[::-1]
# plateau (horizontal) segments -> notch vertices
ramp=[];plat=[]
for k in range(len(low)):
    p=low[k]; h=False
    for q in (low[k-1] if k>0 else None, low[k+1] if k+1<len(low) else None):
        if q is not None and abs(q[1]-p[1])<2e-3 and abs(q[0]-p[0])>1.0: h=True
    (plat if h else ramp).append(p)
ramp=np.array(ramp); plat=np.array(plat).reshape(-1,2)
# remove vertical-step top vertices: points whose X equals a plateau vertex X but Z differs are ramp ends (kept) ; drop duplicates in X
print('bottom chain vertices %d: ramp %d, plateau %d'%(len(low),len(ramp),len(plat)))
# keep only ramp vertices that are not the upper ends of vertical steps (those coincide in X with a plateau vertex and are higher than the ramp)
keepR=[]
for p in ramp:
    near=plat[np.abs(plat[:,0]-p[0])<1e-3]
    if len(near) and p[1]>=near[:,1].min()-1e-3: continue
    keepR.append(p)
R=np.array(keepR); R=R[np.argsort(R[:,0])]
sp=UnivariateSpline(R[:,0],R[:,1],k=3,s=len(R)*0.004); res=R[:,1]-sp(R[:,0]); print('reference spline through %d ramp vertices: residual std %.3f mm, max %.3f'%(len(R),res.std(),abs(res).max()))
# plateaus -> seats: pairs of plateau vertices with same Z
seats=[]; pl=plat[np.argsort(plat[:,0])]; used=set()
for k in range(len(pl)-1):
    if abs(pl[k,1]-pl[k+1,1])<1e-3 and k not in used and 1.0<pl[k+1,0]-pl[k,0]<12: seats.append((pl[k,0],pl[k+1,0],pl[k,1])); used.update([k,k+1])
print('plateaus found:',len(seats),seats[:3],'...')
S0=lambda x: sp(x)
xs=np.arange(R[:,0].min(),R[:,0].max(),0.25)
new=S0(xs)-OFF; spn=UnivariateSpline(xs[::8],new[::8],k=3,s=0)
rows=[]
for a,b,L in seats:
    ce=max(L,float(spn(a))+W,float(spn(b))+W); rows.append((a,b,L,ce))
print('plateaus raised for the walls (mm): max %.2f, frames raised: %d of %d'%(max(r[3]-r[2] for r in rows),sum(1 for r in rows if r[3]>r[2]+1e-6),len(rows)))
json.dump(dict(offset=OFF,wall=W,ref_knots_X=xs[::8].round(2).tolist(),ref_knots_Z=S0(xs[::8]).round(3).tolist(),new_knots_Z=new[::8].round(3).tolist(),pockets=[dict(a=round(a,2),b=round(b,2),old_ceiling=round(L,2),new_ceiling=round(c,2)) for a,b,L,c in rows]),open('data/keelson_from_step_v1.json','w'))
fig,axs=plt.subplots(2,1,figsize=(17,12))
for a_,(xl,yl) in zip(axs,(((470,545),(10,45)),((380,445),(4,14)))):
    a_.plot(C[:,0],C[:,1],'k-',lw=.8,label='builder STEP outline'); a_.plot(R[:,0],R[:,1],'r.',ms=5,label='ramp vertices = the spline')
    xx=np.linspace(*xl,600); a_.plot(xx,S0(xx),'r-',lw=1,label='reference spline'); a_.plot(xx,spn(xx),'g-',lw=2,label='new line: offset %.1f mm below'%OFF)
    for a,b,L,c in rows:
        if xl[0]-8<a<xl[1]: a_.plot([a,a,b,b],[float(spn(a)),c,c,float(spn(b))],'g-',lw=2)
    a_.set_xlim(*xl); a_.set_ylim(*yl); a_.grid(alpha=.3); a_.legend(loc='lower right')
axs[0].set_title('Keelson inner line from the STEP')
fig.savefig('qa/keelson_from_step.png',dpi=60,bbox_inches='tight')
