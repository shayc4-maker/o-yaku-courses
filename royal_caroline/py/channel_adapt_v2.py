# Adapt the keel/keelson openings to the frames: every frame gets its own seat X-4..X+4 at constant keel-top / keelson-bottom levels (levels read at the frame centre);
# outer lines (keel bottom/outside, keelson top) untouched. Output: new channel polygon + modified profile data.
import sys,json,numpy as np
W=float(sys.argv[1]) if len(sys.argv)>1 else 1.5
sys.argv=[sys.argv[0]]
import frames_batch_2d as F
from shapely.geometry import box as bx,Polygon
from shapely.ops import unary_union
import matplotlib.pyplot as plt
XF=F.XF; 
def lev(X):
    try: kt,(a,b)=F.keel_levels(X); return (kt,a,b) if a is not None else None
    except Exception: return None
xs=np.arange(-5,570,0.25)
# old channel (white) as a polygon: between keel top and keelson bottom wherever both exist
pts_lo=[];pts_hi=[];ok=[]
for X in xs:
    l=lev(X)
    if l and l[1]-l[0]>0.05: ok.append((X,l[0],l[1],l[2]))
ok=np.array(ok)
C_old=unary_union([bx(ok[i,0],ok[i,1],ok[i+1,0],ok[i,2]) for i in range(len(ok)-1) if ok[i+1,0]-ok[i,0]<0.3])
# new seats
seats=[]
for n,X in enumerate(XF,1):
    l=lev(X)
    if l is None or l[1]-l[0]<0.05: print('frame builder %d (X=%.1f): no channel at the centre'%(46-n,X)); continue
    seats.append((46-n,X,l[0],l[1],l[2]))
# build the new channel: plateaus per seat; between seats keep the lower seat's levels (stairs rise to the bow) -> step exactly at X-4 of the next frame
seats.sort(key=lambda s:s[1]); 
pieces=[]; xo=ok[0,0]; xe=ok[-1,0]
for i,(b,X,kt,ks,kte) in enumerate(seats):
    xa=X-4; xb=X+4
    pieces.append(bx(xa,kt,xb,ks))
    if i+1<len(seats):
        nb,Xn,ktn,ksn,_=seats[i+1]
        if Xn-4>xb: pieces.append(bx(xb,kt,Xn-4,ks-W))        # gap: keelson inner line W mm below the seat ceiling -> full pocket walls on both sides
C_new=unary_union(pieces)
E_env=unary_union([bx(ok[i,0],F.UB.bounds[1],ok[i+1,0],ok[i,3]) for i in range(len(ok)-1) if ok[i+1,0]-ok[i,0]<0.3])  # not used for output, only for the check
# material to add / remove (relative to the old channel) within the seat range
rng=bx(seats[0][1]-4,-50,seats[-1][1]+4,200)
add=C_old.intersection(rng).difference(C_new)      # channel that becomes solid (must belong to keel or keelson)
rem=C_new.difference(C_old)                         # solid that gets removed (cut deeper)
print('seats',len(seats),'; solid added %.1f mm2, solid removed %.1f mm2 (side-view area)'%(add.area,rem.area))
json.dump(dict(wall_min_mm=W,seats=[dict(builder=s[0],X=round(s[1],2),face_A=round(s[1]-4,2),face_end=round(s[1]+4,2),keel_top=round(s[2],2),keelson_bottom=round(s[3],2),keelson_top=round(s[4],2)) for s in seats]),open('data/channel_seats_v2.json','w'),indent=1)
fig,axs=plt.subplots(3,1,figsize=(17,17))
for a,(xl,yl) in zip(axs,(((440,530),(-10,45)),((470,530),(5,42)),((380,445),(-3,22)))):
    for k,pg in F.PP.items(): a.fill(*pg.exterior.xy,color='#ddd',lw=0)
    for g in (C_old,):
        for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.plot(*gg.exterior.xy,color='#999',lw=.8,ls='--')
    for g in (C_new,):
        for gg in (g.geoms if hasattr(g,'geoms') else [g]): a.fill(*gg.exterior.xy,color='tab:green',alpha=.35,lw=0); a.plot(*gg.exterior.xy,color='g',lw=1.4)
    for s in seats:
        if xl[0]<s[1]<xl[1]: a.axvline(s[1]-4,color='tab:blue',lw=.5); a.axvline(s[1]+4,color='tab:red',lw=.5); a.text(s[1]-3,yl[1]-1.5,str(s[0]),fontsize=9,clip_on=True)
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.2)
axs[0].set_title('v2 full pockets: green = frame pockets + gaps (keelson inner line W mm below the seat ceiling), dashed = old channel')
fig.savefig('qa/channel_adapt_v2.png',dpi=60,bbox_inches='tight')
