# fair version of the new waterlines: spline through the station crossings (exact, iron) + only as many guide points from the plan (shifted by the interpolated mismatch) as needed to follow the plan shape within TOL, rejecting any guide point that adds a curvature sign change; reports curvature sign changes of every variant
import json,numpy as np,sys
from scipy.interpolate import CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
TOL=float(sys.argv[1]) if len(sys.argv)>1 else 0.5
D=json.load(open('data/wl_new_points_v1.json')); W=json.load(open('data/wl_top_points_all.json'))
def signchanges(cs,x0,x1):
    t=np.linspace(x0,x1,3000); k=cs(t,2); s=np.sign(k[np.abs(k)>2e-4]); return int((np.diff(s)!=0).sum())
cols=dict(zip(['I','II','III','IV','V','VI','VII'],['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
fig,axs=plt.subplots(2,1,figsize=(20,16),gridspec_kw={'height_ratios':[1,1.2]}); res={}
for k,v in D.items():
    pts=np.array([[p[0],p[1]] for p in v['points']]); typ=[p[2] for p in v['points']]; S=pts[[t=='station' for t in typ]]; G=pts[[t!='station' for t in typ]]
    full=CubicSpline(pts[:,0],pts[:,1]); allx=pts[:,0]
    # ends: keep the first/last plan point (shape of the waterline ends)
    sel=list(S); 
    for e in (G[0],G[-1]):
        if not any(np.allclose(e,s) for s in sel): sel.append(e)
    sel=np.array(sorted(sel,key=lambda r:r[0])); cs=CubicSpline(sel[:,0],sel[:,1]); base=signchanges(cs,sel[0,0],sel[-1,0]); added=0
    for _ in range(60):
        dev=np.abs(cs(G[:,0])-G[:,1]); i=int(np.argmax(dev))
        if dev[i]<TOL: break
        cand=np.array(sorted(list(map(tuple,sel))+[tuple(G[i])],key=lambda r:r[0])); c2=CubicSpline(cand[:,0],cand[:,1])
        if signchanges(c2,cand[0,0],cand[-1,0])>max(base,signchanges(cs,sel[0,0],sel[-1,0])): G=np.delete(G,i,axis=0); continue
        sel=cand; cs=c2; added+=1
    res[k]=dict(z=v['z'],points=[[round(float(a),2),round(float(b),2)] for a,b in sel],sign_changes=signchanges(cs,sel[0,0],sel[-1,0]),sign_changes_previous=signchanges(full,allx[0],allx[-1]),max_dev_to_plan=float(np.abs(cs(np.array([p[0] for p in v['points'] if p[2]!='station']))-np.array([p[1] for p in v['points'] if p[2]!='station'])).max()),n_station=len(S),n_guides=added+2)
    print('WL %-3s stations %2d + guides %2d = %2d points | curvature sign changes: before %2d -> now %d | max distance to the (shifted) plan points %.2f mm'%(k,len(S),added+2,len(sel),res[k]['sign_changes_previous'],res[k]['sign_changes'],res[k]['max_dev_to_plan']))
    for a,(xl,yl) in zip(axs,(((-10,570),(0,80)),((420,570),(0,60)))):
        t=np.linspace(sel[0,0],sel[-1,0],1500); a.plot(t,cs(t),color=cols[k],lw=1.3); a.plot(S[:,0],S[:,1],'o',color=cols[k],mfc='none',ms=7); a.plot(sel[:,0],sel[:,1],'.',color=cols[k],ms=5); a.set_xlim(*xl); a.set_ylim(*yl)
for a in axs: a.set_aspect('equal'); a.grid(alpha=.25)
axs[0].set_title('Fair waterlines (TOL %.2f mm): circles = stations (exact), dots = all points used'%TOL); fig.savefig('qa/wl_new_fair_v1.png',dpi=55,bbox_inches='tight'); json.dump(res,open('data/wl_new_fair_v1.json','w'))
