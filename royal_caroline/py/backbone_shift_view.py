# lower line of the backbone (min Z over X, all backbone profiles of the builder) before and after the 0.6 mm drop vs the body plan, over the original sheer-plan drawing (side view) and with the body plan at the keel (centre)
import sys,json,numpy as np
SHIFT=float(sys.argv[1]) if len(sys.argv)>1 else 0.6
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from shapely.geometry import Polygon,LineString
from shapely.ops import unary_union
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
BB=json.load(open('data/step44_profiles.json'))
PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}; UB=unary_union(list(PP.values()))
xs=np.arange(-10,570,1.0); low=[]
for x in xs:
    g=UB.intersection(LineString([(x,-80),(x,200)]))
    low.append(g.bounds[1] if not g.is_empty else np.nan)
low=np.array(low); ok=~np.isnan(low)
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
img=Image.open('plans/plan_1a_aligned.png').convert('RGB')
fig,axs=plt.subplots(3,1,figsize=(18,15),gridspec_kw={'height_ratios':[1,1,1.1]})
for a,(xl,zl) in zip(axs[:2],(((-20,570),(-22,12)),((220,330),(-14,-2)))):
    box=(int((xl[0]-X0)/KX)-5,int(ZR-zl[1]/KZ)-5,int((xl[1]-X0)/KX)+5,int(ZR-zl[0]/KZ)+5); c=img.crop(box)
    ext=(box[0]*KX+X0,box[2]*KX+X0,(ZR-box[3])*KZ,(ZR-box[1])*KZ); a.imshow(c,extent=ext,aspect='auto')
    a.plot(xs[ok],low[ok],color='tab:blue',lw=2.2,label='backbone lower line, before'); a.plot(xs[ok],low[ok]-SHIFT,color='tab:red',lw=2.2,label='after (down %.1f mm)'%SHIFT)
    a.axhline(0,color='g',lw=.5,ls='--'); a.set_xlim(*xl); a.set_ylim(*zl); a.legend(loc='upper right'); a.set_ylabel('Z (mm)')
axs[0].set_title('Side view: sheer plan (original drawing) with the backbone lower line before (blue) and after the shift (red); green = baseline Z=0 of the body plan')
# body plan at the keel: station points near the keel and the keel section
S=json.load(open('data/bodyplan_splines_v1.json')); a=axs[2]
for n in (9,10,11,12,13,14):
    L=np.array(S[str(n)]['curve']); a.plot(L[:,0],L[:,1],lw=1)
    a.plot(-L[:,0],L[:,1],lw=1,color=a.lines[-1].get_color())
kb=2.65; z0=float(np.nanmin(low[(xs>200)&(xs<350)])); 
a.add_patch(plt.Rectangle((-kb,z0),2*kb,8,fill=False,edgecolor='tab:blue',linewidth=2)); a.add_patch(plt.Rectangle((-kb,z0-SHIFT),2*kb,8,fill=False,edgecolor='tab:red',linewidth=2))
a.set_aspect('equal'); a.set_xlim(-30,30); a.set_ylim(z0-4,16); a.grid(alpha=.3); a.set_title('Body plan at the keel (stations 9-14, our splines): keel bottom at Z=%.1f before (blue), %.1f after (red); baseline Z=0'%(z0,z0-SHIFT)); a.axhline(0,color='g',lw=.6,ls='--')
fig.savefig('qa/backbone_shift_view.png',dpi=55,bbox_inches='tight')
print('lowest backbone Z by region: X 0-100 %.2f, 200-350 %.2f, 450-520 %.2f'%(np.nanmin(low[(xs>0)&(xs<100)]),np.nanmin(low[(xs>200)&(xs<350)]),np.nanmin(low[(xs>450)&(xs<520)])))
