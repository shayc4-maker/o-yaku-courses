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
def face_poly(Xf):
    P=C.band(i,Xf)[1]; O=outer_to_wall(P,plan_base); O=O[np.argsort(O[:,1])]
    sm=np.c_[savgol_filter(O[:,0],11,3),savgol_filter(O[:,1],11,3)]; d_=np.gradient(sm,axis=0); d_/=np.hypot(*d_.T)[:,None]; m=np.c_[-d_[:,1],d_[:,0]]; I=O+m*3.2
    zt=ks_bot+PEN_UP                                    # leg tops: the keelson sits in an inverted U whose legs rise PEN_UP beside it (mirror of the keel at the bottom)
    k=int(np.where((I[:,0]>8)&(I[:,1]>zt+2.5))[0][0]); Pj=I[k]; Tj=I[k+2]-I[k-2]; Tj=Tj/np.hypot(*Tj)
    Ps=np.array([KB+0.01,zt]); L=np.hypot(*(Pj-Ps)); sp=herm(Ps,np.array([1.0,0.0])*L*0.9,Pj,Tj*L*0.9)
    top=np.vstack([[[KB,ks_bot],[KB,zt]],sp[1:],I[k+1:]])
    poly=Polygon(np.vstack([[[0,keel_top],[KB,keel_top],[KB,plan_base]],O,top[::-1],[[0,ks_bot]]])).buffer(0).intersection(box(0,-10,200,300))
    return poly,O,top
faces={xf:face_poly(xf) for xf in (xc-4,xc)}
block=unary_union([faces[x][0].buffer(0.01) for x in faces]).buffer(-0.01)
full=unary_union([block.buffer(0.01),C.mirror(block).buffer(0.01)]).buffer(-0.01)
fig,ax=plt.subplots(1,2,figsize=(18,9))
for a,(xl,yl) in zip(ax,(((-14,40),(-14,32)),((-9,12),(-2,24)))):
    a.add_patch(plt.Rectangle((-KB,-20),2*KB,keel_top+20,color='#999')); a.add_patch(plt.Rectangle((-KB,ks_bot),2*KB,ks_top-ks_bot,color='#999'))
    for gg in (full.geoms if hasattr(full,'geoms') else [full]): a.fill(*gg.exterior.xy,color='tab:blue',alpha=.25); a.plot(*gg.exterior.xy,color='tab:blue',lw=1.8,label='block (envelope of the two faces)')
    for xf,col in zip(faces,('tab:green','tab:red')):
        p=faces[xf][0]
        for gg in (p.geoms if hasattr(p,'geoms') else [p]): a.plot(*gg.exterior.xy,color=col,lw=.9,ls='--',label=f'exact lines, face X={xf:.1f}')
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.3)
h,l=ax[0].get_legend_handles_labels(); ax[0].legend(h[:3],l[:3],fontsize=8,loc='upper left')
ax[0].set_title(f'builder frame 5 (our 41), layer A, X {xc-4:.1f}-{xc:.1f}: keel top {keel_top:.2f}, keelson {ks_bot:.2f}-{ks_top:.2f}, plan bottom {plan_base:.2f}\nbottom: inverted U receives the keel ({PEN_LOW:.2f} mm); top: inverted U receives the keelson ({PEN_UP} mm); dashed = the exact lines of the two faces (sanding)',fontsize=9)
ax[1].set_title('zoom: gap between keel and keelson')
plt.savefig('qa/keel_keelson_section_frame5.png',dpi=60,bbox_inches='tight'); print('valid',all(faces[x][0].is_valid for x in faces),'overlap bottom %.2f top %.2f'%(PEN_LOW,PEN_UP))
