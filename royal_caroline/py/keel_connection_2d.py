# 2D proposal (builder frame 5 = our 41): connection to the keel as in the Princess Charlotte reference: floor (layer A) = V whose outer lines merge tangentially into the keel wall and end in a flat stub that sits in a notch cut in the keel top; first futtock (layer F) = notched over the keel (an inverted U) with legs along the keel wall.
import sys,io,contextlib,numpy as np,json
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import cutting_plan as C
from shapely.geometry import Polygon,box
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
i=41; xc=C.X[i-1]; KW=2.65
seats=json.load(open('data/backbone_contour_v5.json'))['seats']; s=min(seats,key=lambda q:abs((q[0]+q[1])/2-xc)); zs,d=s[2],s[3]; zk=zs+d     # seat bottom, depth, keel top
bA,PA,QA,mA=C.band(i,xc-4); bF,PF,QF,mF=C.band(i,xc)
def herm(P0,T0,P1,T1,n=40):
    t=np.linspace(0,1,n)[:,None]; return (2*t**3-3*t**2+1)*P0+(t**3-2*t**2+t)*T0+(-2*t**3+3*t**2)*P1+(t**3-t**2)*T1
def outer_to_wall(P,zend,span=8.0):
    """outer line (rising with Z) cut at zend+span, then a Hermite blend that reaches the wall (Y=KW) at height zend with a vertical tangent"""
    k=int(np.argmin(np.abs(P[:,1]-(zend+span)))); p0=P[k]; t0=(P[k+3]-P[k-3]); t0=t0/np.hypot(*t0)*span*1.4
    p1=np.array([KW,zend]); t1=np.array([0.0,-1.0])*span*0.6          # arrives going down, vertical
    return np.vstack([herm(p1,-t1,p0,t0)[::-1][::-1],P[k+1:]])
# A: floor. outer reaches the wall at the keel top zk, stub down to the seat bottom zs
OA=outer_to_wall(PA,zk); OA=OA[np.argsort(OA[:,1])]
# inner of A: parallel offset of the new outer, then V crossing the centre line
from scipy.signal import savgol_filter
def inner_of(O,delta=3.2):
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d_=np.gradient(sm,axis=0); d_/=np.hypot(*d_.T)[:,None]; m=np.c_[-d_[:,1],d_[:,0]]; return O+m*delta
IA=inner_of(OA)
floor=Polygon(np.vstack([[[0,zs],[KW,zs]],OA,IA[::-1]])).buffer(0).intersection(box(0,-10,200,300))
floorS=floor; floor_full=unary_union([floorS.buffer(0.01),C.mirror(floorS).buffer(0.01)]).buffer(-0.01)
# F: first futtock, notched over the keel: outer to the wall at the plan base (zb), legs down the wall; roof of the notch at zk
zb=PF[0,1]; OF=outer_to_wall(PF,zb); OF=OF[np.argsort(OF[:,1])]; IF=inner_of(OF)
futS=Polygon(np.vstack([[[KW,zb],[KW,zk],[0,zk]],IF[IF[:,1]>zk],IF[IF[:,1]>zk][-1:],OF[::-1]])).buffer(0)
futS=Polygon(np.vstack([[[KW,zb]],OF,IF[::-1],[[0,zk],[KW,zk]]])).buffer(0).intersection(box(0,-10,200,300))
fig,ax=plt.subplots(2,2,figsize=(18,15))
for r,(g,c,title,ktop) in enumerate(((floor_full,'tab:blue','A (X %.1f-%.1f): floor 5-1, stub in the keel notch; keel top here lowered to the seat bottom Z %.2f'%(xc-4,xc,zs),zs),(None,'tab:red','F (X %.1f-%.1f): first futtock 5-8 / 5-13 notched over the keel; keel top Z %.2f'%(xc,xc+4,zk),zk))):
    for a,(xl,yl) in zip(ax[r],(((-12,48),(-2,42)),((-9,9),(-2,16)))):
        a.add_patch(plt.Rectangle((-KW,-20),2*KW,ktop+20,color='#999'))
        gs=[floor_full] if r==0 else [futS,C.mirror(futS)]
        for gg0 in gs:
            for gg in (gg0.geoms if hasattr(gg0,'geoms') else [gg0]): a.fill(*gg.exterior.xy,color=c,alpha=.3); a.plot(*gg.exterior.xy,color=c,lw=1.6)
        a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.3)
    ax[r][0].set_title(title,fontsize=10)
plt.savefig('qa/keel_connection_2d_frame5.png',dpi=60,bbox_inches='tight'); print('keel top',round(zk,2),'notch depth',round(d,2),'plan base Z',round(zb,2))
