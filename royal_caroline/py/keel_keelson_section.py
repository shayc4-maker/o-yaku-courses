# 2D section (aft view), builder frame 5 = our 41, X 480.3: keel (below), keelson (above), the frame floor fills the gap and laps both with a 'ח' (about 2.5 mm each)
import sys,io,contextlib,json,numpy as np
src=open('py/keel_connection_2d.py').read().split("# A: floor.")[0]
with contextlib.redirect_stdout(io.StringIO()): exec(src)
from shapely.geometry import Polygon,box,LineString
from scipy.signal import savgol_filter
BB=json.load(open('data/step44_profiles.json'))
def zr(name):
    p=Polygon(max(BB[name],key=lambda q:Polygon(q).area)).buffer(0); g=p.intersection(LineString([(xc,-30),(xc,200)])); return g.bounds[1],g.bounds[3]
keel_top=zr('Boss-Extrude2[2]')[1]; ks_bot,ks_top=zr('Boss-Extrude4[4]'); plan_base=PA[0,1]
KB=5.3/2; PEN_LOW=keel_top-plan_base; PEN_UP=2.5
# outer line of the frame (face at the centre X): tangent into the keel wall, reaching the plan base level
P=C.band(i,xc)[1]; O=outer_to_wall(P,plan_base); O=O[np.argsort(O[:,1])]
sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d_=np.gradient(sm,axis=0); d_/=np.hypot(*d_.T)[:,None]; m=np.c_[-d_[:,1],d_[:,0]]; I=O+m*3.2
# top (inner) boundary: flat shoulder at the keelson bottom, then a tangent spline into the inner line
k=np.where((I[:,0]>8)&(I[:,1]>ks_bot+3))[0][0]; Pj=I[k]; Tj=I[k+2]-I[k-2]; Tj=Tj/np.hypot(*Tj)
Ps=np.array([KB+2.0,ks_bot]); L=np.hypot(*(Pj-Ps)); sp=herm(Ps,np.array([1.0,0.0])*L*0.9,Pj,Tj*L*0.9)
top_pts=np.vstack([[[0,ks_bot+PEN_UP],[KB,ks_bot+PEN_UP],[KB,ks_bot],[KB+2.0,ks_bot]],sp[1:],I[k+1:]])
poly=Polygon(np.vstack([[[0,keel_top],[KB,keel_top],[KB,plan_base]],O,top_pts[::-1]])).buffer(0).intersection(box(0,-10,200,300))
full=unary_union([poly.buffer(0.01),C.mirror(poly).buffer(0.01)]).buffer(-0.01)
fig,ax=plt.subplots(1,2,figsize=(18,9))
for a,(xl,yl) in zip(ax,(((-14,40),(-14,32)),((-8,8),(-2,24)))):
    a.add_patch(plt.Rectangle((-KB,-20),2*KB,keel_top+20,color='#999')); a.add_patch(plt.Rectangle((-KB,ks_bot),2*KB,ks_top-ks_bot,color='#999'))
    for gg in (full.geoms if hasattr(full,'geoms') else [full]): a.fill(*gg.exterior.xy,color='tab:blue',alpha=.3); a.plot(*gg.exterior.xy,color='tab:blue',lw=1.6)
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].set_title(f'builder frame 5 (our 41), X={xc:.1f}: keel top {keel_top:.2f}, keelson {ks_bot:.2f}-{ks_top:.2f}; plan bottom {plan_base:.2f}\nkeel enters the frame {PEN_LOW:.2f} mm (notch from below), frame tenon enters the keelson {PEN_UP} mm',fontsize=10)
ax[1].set_title('zoom: gap between keel and keelson')
plt.savefig('qa/keel_keelson_section_frame5.png',dpi=60,bbox_inches='tight'); print('keel top %.2f, keelson %.2f..%.2f, gap %.2f, plan base %.2f -> low overlap %.2f'%(keel_top,ks_bot,ks_top,ks_bot-keel_top,plan_base,PEN_LOW))
