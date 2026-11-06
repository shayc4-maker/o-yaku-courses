# Side view (X-Z, looking along Y) of frame 1: keel / keelson / stem profiles from the builder's backbone and the two frame layers at the centreline
import sys,numpy as np
sys.argv=[sys.argv[0]]
import frames_batch_2d as F
import matplotlib.pyplot as plt
xc=F.XF[44]; fig,axs=plt.subplots(2,1,figsize=(15,13),gridspec_kw={'height_ratios':[1,1]})
lv={}
for nm,X in (('A0',xc-4),('A1',xc),('F1',xc+4)):
    try: p,i=F.face_poly(X,X); lv[nm]=(X,i)
    except Exception: lv[nm]=(X,None)
print({k:(round(v[0],2),None if v[1] is None else (round(v[1]['keel_top'],2),round(v[1]['ks_bot'],2),round(v[1]['ks_top'],2))) for k,v in lv.items()})
for a,(xl,yl,ttl) in zip(axs,(((470,545),(-12,60),'Side view X-Z: backbone (gray) and frame 1 layers at the centreline'),((505,535),(18,44),'Zoom at the bow end of frame 1'))):
    ttl=''
    for k,pg in F.PP.items():
        x,y=pg.exterior.xy; a.fill(x,y,color='#bbb',alpha=.5,lw=0); a.plot(x,y,color='#777',lw=.5)
    for g in (F.UB,):
        for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color='k',lw=.9)
    (x0,i0),(x1,i1),(x2,i2)=lv['A0'],lv['A1'],lv['F1']
    from shapely.geometry import box as bx
    for (xa,xb,cl) in ((x0,x1,'tab:blue'),(x1,min(x2,526.6),'tab:red')):
        ch=bx(xa,i1['keel_top']-3,xb,i1['ks_top']+3).difference(F.UB)      # the real channel between keel and keelson over this layer
        for gg in (ch.geoms if hasattr(ch,'geoms') else [ch]):
            if gg.area>0.5 and gg.bounds[1]<i1['ks_bot']+1: a.fill(*gg.exterior.xy,color=cl,alpha=.4); a.plot(*gg.exterior.xy,color=cl,lw=1.3)
    for X,cl in ((x0,'tab:blue'),(x1,'k'),(x2,'tab:red')): a.axvline(X,color=cl,lw=.7,ls=':'); a.text(X+.2,yl[1]-1.5,'X=%.1f'%X,color=cl,fontsize=9)
    a.axvline(526.6,color='g',lw=.8,ls='-.'); a.text(526.8,yl[0]+1,'stem starts 526.6',color='g',fontsize=9)
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.25); a.set_title(ttl,fontsize=10)
fig.savefig('qa/frame1_side_view.png',dpi=65,bbox_inches='tight')
