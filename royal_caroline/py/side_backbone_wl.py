# side view: backbone (STEP profiles, not moved) + rabbet spline + waterlines I-VII (model Z) in colours, bow ends from the top view, on the original sheer plan
import json,numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
from shapely.geometry import Polygon
from scipy.interpolate import CubicSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
BB=json.load(open('data/step44_profiles.json')); PP={k:Polygon(max(v,key=lambda q:Polygon(q).area)).buffer(0) for k,v in BB.items() if k not in('Split1[1]','Split1[2]','Boss-Extrude4[2]')}
W=json.load(open('data/wl_top_points_all.json')); pts=json.load(open('data/rabbet_points_v1.json'))['points']; R=CubicSpline([p[0] for p in pts],[p[1] for p in pts],bc_type='natural')
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0; img=Image.open('plans/plan_1a_aligned.png').convert('RGB')
cols=dict(zip(['I','II','III','IV','V','VI','VII'],['#e6194b','#f58231','#3cb44b','#4363d8','#911eb4','#008080','#9a6324']))
fig,axs=plt.subplots(3,1,figsize=(19,22),gridspec_kw={'height_ratios':[0.5,1.1,0.8]})
for a,(xl,zl) in zip(axs,(((-20,570),(-14,75)),((440,545),(-12,45)),((220,330),(-12,14)))):
    box=(int((xl[0]-X0)/KX)-5,int(ZR-zl[1]/KZ)-5,int((xl[1]-X0)/KX)+5,int(ZR-zl[0]/KZ)+5); c=img.crop(box)
    a.imshow(c,extent=(box[0]*KX+X0,box[2]*KX+X0,(ZR-box[3])*KZ,(ZR-box[1])*KZ),aspect='equal'); a.imshow(np.ones((2,2,4))*[1,1,1,0.4],extent=(box[0]*KX+X0,box[2]*KX+X0,(ZR-box[3])*KZ,(ZR-box[1])*KZ),aspect='equal')
    for k,pg in PP.items(): a.plot(*pg.exterior.xy,color='gray',lw=1.0)
    t=np.linspace(30,528,1500); a.plot(t,R(t),color='k',lw=1.6,ls='--',label='rabbet (spline)')
    for n,v in W.items():
        z=v['z']; P=np.array(v['points_XY']); xe=float(P[:,0].max())
        a.axhline(z,color=cols[n],lw=1.3,label='WL %s  Z=%.1f  (bow end X=%.1f)'%(n,z,xe)); a.plot([xe],[z],'o',color=cols[n],ms=7)
        if xl[0]<xe<xl[1] and zl[0]<z<zl[1]: a.text(xe+1,z+0.8,'%s %.1f'%(n,xe),color=cols[n],fontsize=9,weight='bold')
    a.set_xlim(*xl); a.set_ylim(*zl); a.set_ylabel('Z (mm)')
axs[0].legend(fontsize=8,ncol=4,loc='upper center'); axs[0].set_title('Side view: backbone (grey, STEP, not moved), rabbet (black dashed), waterlines I-VII (colours, body plan Z) with the bow end X from the top view; original sheer plan behind')
fig.savefig('qa/side_backbone_wl.png',dpi=55,bbox_inches='tight')
