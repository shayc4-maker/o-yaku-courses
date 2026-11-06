# frame 1 split into its two 4 mm parts, shown separately BEFORE union: part A (faces X-4=520 and X=524, back) and part F (faces X=524 and X+4=528, front). The face at 528 lies in the stem region (X>526.6, keel+keelson one solid): no floor/seat there, so the face is a plain band: station 1 line (approved) up to the rabbet, inner = 3.2 mm offset, closed by a straight end cut at the rabbet (butts against the stem).
import sys,json,numpy as np
sys.path.insert(0,'py')
from frame_arm_v2 import *
from shapely.geometry import Polygon
from shapely.ops import unary_union
from shapely import affinity
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
mir=lambda g: affinity.scale(g,xfact=-1,yfact=1,origin=(0,0))
def full(h):
    g=unary_union([h.buffer(0.005),mir(h).buffer(0.005)]).buffer(-0.005); return g          # may be two separate bands (stem face)
def outline_xy(g):
    return [q.exterior.xy for q in (g.geoms if hasattr(g,'geoms') else [g])]
def stem_face(X):
    P=hull_line_v2(X); zr=float(R3(X))
    if P[0,1]<zr: i=int(np.argmax(P[:,1]>=zr)); y0=float(np.interp(zr,[P[i-1,1],P[i,1]],[P[i-1,0],P[i,0]])); L=np.vstack([[y0,zr],P[i:]])
    else: L=np.vstack([[P[0,0],zr],P[1:]])
    sm=np.c_[savgol_filter(L[:,0],11,3),savgol_filter(L[:,1],11,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]; N=np.c_[-d[:,1],d[:,0]]; I=L+N*T
    return Polygon(np.vstack([L,I[::-1]])).buffer(0),L,I
ar={520.0:arm(520.0)[0],524.0:arm(524.0)[0],526.6:arm(526.6)[0]}; sp,L,I=stem_face(528.0); ar[528.0]=sp
print('stem face 528: valid',sp.is_valid,'area %.0f'%sp.area,'outer end (%.2f, %.2f) inner end (%.2f, %.2f)'%(L[0,0],L[0,1],I[0,0],I[0,1]))
F={k:full(v) for k,v in ar.items()}; parts={'A (back, X-4=520 .. X=524)':(520.0,524.0),'F (front, X=524 .. X+4=528, front face = stem band)':(524.0,528.0),'F2 (front, X=524 .. 526.6, front face keeps floor/seat)':(524.0,526.6)}
cols={520.0:'tab:blue',524.0:'k',528.0:'tab:red',526.6:'tab:red'}
out={}
with PdfPages('qa/frame1_parts_AF.pdf') as pdf:
    for nm,(xa,xb) in parts.items():
        env=unary_union([F[xa].buffer(0.01),F[xb].buffer(0.01)]).buffer(-0.01); env=unary_union([Polygon(q.exterior) for q in (env.geoms if hasattr(env,'geoms') else [env])])
        out[nm]=dict(area=env.area,face_areas=[F[xa].area,F[xb].area]); print(nm,'blank area %.0f; face areas %.0f / %.0f'%(env.area,F[xa].area,F[xb].area))
        fig,axs=plt.subplots(2,2,figsize=(16,16)); axs=axs.ravel()
        for a,(xl,yl,t) in zip(axs,(((-85,85),(-5,125),'whole'),((-16,16),(15,45),'bottom'),((-40,40),(15,65),'inner lines into the offset'),((20,85),(60,125),'upper part'))):
            [a.fill(*q.exterior.xy,color='gold',alpha=.35,label='cut outline of the part') for q in (env.geoms if hasattr(env,'geoms') else [env])]
            [a.plot(*xy,color=cols[x],lw=1,label=('face X=%.1f'%x) if i==0 else None) for x in (xa,xb) for i,xy in enumerate(outline_xy(F[x]))]
            a.set_aspect('equal'); a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_title('frame 1 part %s  %s'%(nm,t),fontsize=10)
        axs[0].legend(fontsize=9); pdf.savefig(fig); fig.savefig('qa/frame1_part_%s.png'%nm.split(' ')[0],dpi=60); plt.close(fig)
print({k:{kk:(round(vv,0) if not isinstance(vv,list) else [round(x) for x in vv]) for kk,vv in v.items()} for k,v in out.items()})
