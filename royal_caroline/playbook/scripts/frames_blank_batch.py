# frames (builder numbers) from the APPROVED outer lines v5 with the final arm rule; tops cut straight along the bulwark line (horizontal per face, sloped per layer); common blank for A/F; 2D sheet + 3dm (A/F valid solids + laser lines)
import sys,os,json,numpy as np
BL=[int(a) for a in sys.argv[1:]] or [1,2,3,4,5]; sys.argv=[sys.argv[0]]
sys.path.insert(0,'py')
import frames_batch_2d as F
A5=json.load(open('data/frames_outer_approved_v5.json')); LN=json.load(open('data/bulwark_line_v3.json'))
segs=[np.array(v) for v in LN.values() if abs(v[-1][0]-v[0][0])>1]
def zline(X):
    for a in segs:
        if a[:,0].min()<=X<=a[:,0].max(): o=np.argsort(a[:,0]); return float(np.interp(X,a[o,0],a[o,1]))
CUR={'b':None}
def hull_approved(X):
    b=CUR['b']
    for nm in ('back','mid','front'):
        v=A5[str(b)][nm]
        if abs(v['X']-X)<0.01:
            C=np.array(v['curve']); C=C[C[:,0]>=3.2]
            if v.get('top'):
                t=np.array(v['top']); C=np.vstack([C,t[1:]]); d=t[1]-t[0]; d=d/np.hypot(*d); C=np.vstack([C,t[1]+d*6.0,t[1]+d*8.0])   # extended 8 mm past the line, cut back to the line below
            else:
                d=C[-1]-C[-6]; d=d/np.hypot(*d); C=np.vstack([C,C[-1]+d*6.0,C[-1]+d*8.0])
            return C
    raise KeyError(X)
F.hull_line=hull_approved
import frame_arm as FA
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import shapely.affinity as sa
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
mir=lambda g: sa.scale(g,xfact=-1,yfact=1,origin=(0,0))
def big(u): return max(u.geoms,key=lambda q:q.area) if hasattr(u,'geoms') else u
def full(g): return big(unary_union([g.buffer(0.01),mir(g).buffer(0.01)]).buffer(-0.01))
R={}
for b in BL:
    CUR['b']=b; xc=A5[str(b)]['mid']['X']; FP={}; info={}
    for nm,X in (('back',xc-4),('mid',xc),('front',xc+4)):
        poly,inf=FA.arm(X); zt=zline(X); poly=big(poly.intersection(box(-1,-50,300,zt))); FP[nm]=full(poly); info[nm]=dict(floor=inf['floor'],seat=inf['seat'],ztop=zt)
    env=big(unary_union([FP[k].buffer(0.01) for k in FP]).buffer(-0.01))
    R[b]=dict(xc=xc,FP=FP,env=env,info=info)
    print('frame %d X=%.1f valid %s areas %s common %.0f; floor %.2f seat %.2f; Ztop %.2f/%.2f/%.2f'%(b,xc,all(p.is_valid for p in FP.values()),'/'.join('%.0f'%p.area for p in FP.values()),env.area,info['mid']['floor'],info['mid']['seat'],info['back']['ztop'],info['mid']['ztop'],info['front']['ztop']))
NOFIG=os.environ.get('NOFIG')=='1'
n=len(BL); cols={'back':'tab:blue','mid':'k','front':'tab:red'}
if not NOFIG:
    fig,axs=plt.subplots(3,n,figsize=(5*n,15),gridspec_kw={'height_ratios':[1.5,1,1]}); axs=np.atleast_2d(axs).reshape(3,n)
    for j,b in enumerate(BL):
        r=R[b]; f0=r['info']['mid']['floor']; s0=r['info']['mid']['seat']; zmax=max(i['ztop'] for i in r['info'].values())
        for row,(xl,yl,t) in enumerate((((-90,90),(f0-8,zmax+6),'frame %d X=%.1f'%(b,r['xc'])),((-14,14),(f0-5,s0+5),'centre: wall, floor, seat'),((-60,60),(zmax-18,zmax+3),'top (cut along the bulwark line)'))):
            a=axs[row,j]; a.fill(*r['env'].exterior.xy,color='0.85')
            for k,p in r['FP'].items(): a.plot(*p.exterior.xy,color=cols[k],lw=1.2)
            a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.25); a.set_title(t,fontsize=9)
    fig.savefig('qa/frames_blank_%s_2d.png'%('_'.join(map(str,BL))),dpi=50,bbox_inches='tight')
np.save(os.environ.get('NPY','/tmp/blank_batch.npy'),{b:dict(xc=R[b]['xc'],env=np.array(R[b]['env'].exterior.coords),FP={k:np.array(v.exterior.coords) for k,v in R[b]['FP'].items()},z={k:v['ztop'] for k,v in R[b]['info'].items()}) for b in BL},allow_pickle=True)
