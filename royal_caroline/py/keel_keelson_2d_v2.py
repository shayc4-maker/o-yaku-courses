# 2D: new keel top / keelson underside / keelson top as tangent-continuous splines that start and end exactly on the builder's reference curves (R1..R7 in his 3dm), every join G1
import json,numpy as np
from scipy.interpolate import CubicSpline,splprep,splev
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=[np.array(c['pts'])[:,[0,2]] for c in json.load(open('data/builder_ref_curves_keel_v1.json'))]; NP=json.load(open('data/keel_keelson_points_v1.json')); PR=json.load(open('data/step44_profiles.json')); V2=json.load(open('data/keel_keelson_v2.json'))
R1,R2,R3,R4,R5,R6,R7=R
def tan_end(P,end,k=6):   # unit tangent at an end of a dense polyline, pointing away from the curve (outward)
    d=(P[-1]-P[-1-k]) if end==1 else (P[0]-P[k]); return d/np.hypot(*d)
ang=lambda d:np.degrees(np.arctan2(d[1],d[0]))
def slope_of(d): return d[1]/d[0]
rep=[]
def join(name,a,b):
    d=abs((ang(a)-ang(b)+180)%360-180); rep.append((name,round(ang(a),1),round(ang(b),1),round(d,2))); return d
# ---- keel top: stern part (approved points, X<=425) + R1 end at (432.92,3.68); tangent clamped to R1 at 432.92
K=np.array(NP['keel_top']['points']); Kp=K[K[:,0]<=425]; xs=np.r_[Kp[:,0],R1[-1,0]]; zs=np.r_[Kp[:,1],R1[-1,1]]
tR1=tan_end(R1,1); s_end=slope_of(-tR1)         # R1 is traversed from the stem to the stern, the tangent at its stern end points toward -X
kk=np.polyval(np.polyfit(np.arange(45,60),np.array(V2['keel_surface']['Z'])[:15],1),0)
s0=np.polyfit(np.array(V2['keel_surface']['X'])[:10],np.array(V2['keel_surface']['Z'])[:10],1)[0]
keel=CubicSpline(xs,zs,bc_type=((1,s0),(1,s_end)))
print('keel top: point at 432.92 given %.2f vs approved line %.2f'%(R1[-1,1],float(np.interp(432.92,V2['keel_surface']['X'],V2['keel_surface']['Z']))))
# ---- underside: starts on R6 end (43.68,33.75) with R6 tangent, ends at (526.6,33.62) with R4's start tangent
U=np.array(NP['keelson_under']['points']); Up=U[(U[:,0]>52)&(U[:,0]<515)]
x0,z0=R6[-1]; tR6=tan_end(R6,1); s_u0=slope_of(tR6)
x1,z1=R4[0]; tR4=-tan_end(R4,0); s_u1=slope_of(R4[min(6,len(R4)-1)]-R4[0])
under=CubicSpline(np.r_[x0,Up[:,0],x1],np.r_[z0,Up[:,1],z1],bc_type=((1,s_u0),(1,s_u1)))
join('underside start vs R6 end (tangent angle of the spline)',tR6,np.array([1,under(x0+0.01,1)])/np.hypot(1,under(x0+0.01,1)))
# ---- keelson top: from the aft cap top (41.25,38.06) to R3 end (526.68,38.59); points = offset of the underside by a smooth thickness
t_of=lambda x:np.interp(x,[41.25,120,210,400,526.7],[3.2,4.5,6.0,6.0,5.0])
xt=np.r_[41.25,np.arange(60,515,20.0),R3[-1,0]]
def top_pt(x):
    d1=under(x,1); n=np.array([-d1,1.0]); n/=np.hypot(*n); return np.array([x,float(under(x))])+n*t_of(x)
Tp=np.array([top_pt(x) for x in xt[1:-1]]); 
tR3=tan_end(R3,1); s_t1=slope_of(-tR3)
s_t0=-0.455
top=CubicSpline(np.r_[41.25,Tp[:,0],R3[-1,0]],np.r_[38.06,Tp[:,1],R3[-1,1]],bc_type=((1,s_t0),(1,s_t1)))
# ---- R4 rebuilt: same end points and start tangent, end tangent = R3's tangent at the junction (a wedge that closes tangent into the stem line)
i3=int(np.argmin(np.hypot(*(R3-R4[-1]).T))); dR3=R3[max(i3-3,0)]-R3[min(i3+3,len(R3)-1)]; dR3=dR3/np.hypot(*dR3)     # R3 runs top->bottom: this points up along the stem
P0=R4[0]; P3=R3[i3]; d0=-tan_end(R4,0); L=np.hypot(*(P3-P0)); Pb=np.array([P0,P0+d0*0.38*L,P3-dR3*0.38*L,P3]); tb=np.linspace(0,1,200)[:,None]
R4n=(1-tb)**3*Pb[0]+3*(1-tb)**2*tb*Pb[1]+3*(1-tb)*tb**2*Pb[2]+tb**3*Pb[3]
print('R4: end point moved from (%.2f,%.2f) to the point of R3 (%.2f,%.2f), %.2f mm'%(R4[-1,0],R4[-1,1],P3[0],P3[1],np.hypot(*(P3-R4[-1]))))
R4_old=R4; R4=R4n
d_r4_end=tan_end(R4,1); i=int(np.argmin(np.hypot(*(R3-R4[-1]).T))); d_r3=R3[min(i+3,len(R3)-1)]-R3[max(i-3,0)]; d_r3=-d_r3/np.hypot(*d_r3)   # R3 runs top->bottom, flip
join('R4 (rebuilt) end vs R3 at the junction (%.1f,%.1f)'%tuple(R4[-1]),tan_end(R4,1),dR3)
join('keelson top end vs R3 end tangent',np.array([1,top(R3[-1,0],1)])/np.hypot(1,top(R3[-1,0],1)),-tan_end(R3,1))
join('keel top end vs R1 stern end',np.array([1,keel(R1[-1,0],1)])/np.hypot(1,keel(R1[-1,0],1)),-tan_end(R1,1))
join('underside end vs R4 start',np.array([1,under(x1,1)])/np.hypot(1,under(x1,1)),-tan_end(R4,0))
print('keelson top at X=51.08: %.2f (R5 starts at 33.98); at 41.25: %.2f'%(top(51.08),top(41.25)))
for r in rep: print('JOIN %-62s angle A %7.1f  angle B %7.1f  difference %.2f deg'%r)
def curv(f,xs): d1=f(xs,1); d2=f(xs,2); return d2/(1+d1**2)**1.5
for nm,f,xa,xb in (('keel top',keel,45,432.9),('underside',under,x0,x1),('keelson top',top,41.25,R3[-1,0])):
    xx=np.linspace(xa,xb,3000); k=curv(f,xx); sc=int((np.diff(np.sign(k[np.abs(k)>1e-4]))!=0).sum()); print('%-12s X %.1f..%.1f curvature sign changes %d, min radius %.0f mm'%(nm,xa,xb,sc,1/abs(k).max()))
xx=np.linspace(45,515,500); tn=[]
for x in xx:
    d1=under(x,1); n=np.array([-d1,1.0]); n/=np.hypot(*n); s=np.linspace(0,12,1201); q=np.array([x,float(under(x))])[None,:]+s[:,None]*n[None,:]; r=q[:,1]-top(np.clip(q[:,0],41.25,526.68)); j=np.where(np.diff(np.sign(r))!=0)[0]; tn.append(s[j[0]] if len(j) else np.nan)
tn=np.array(tn); print('keelson normal thickness: stern %.2f, min %.2f, max %.2f, bow %.2f'%(tn[0],np.nanmin(tn),np.nanmax(tn),tn[-1]))
json.dump(dict(R4_rebuilt=R4.tolist(),keel_top=[[float(x),float(keel(x))] for x in np.linspace(45,432.92,400)],underside=[[float(x),float(under(x))] for x in np.linspace(x0,x1,500)],keelson_top=[[float(x),float(top(x))] for x in np.linspace(41.25,R3[-1,0],500)],joins=rep),open('data/keel_keelson_2d_v2.json','w'))
# ---- figure
fig,axs=plt.subplots(3,1,figsize=(18,20),gridspec_kw={'height_ratios':[1,1.3,1.3]})
def draw(a,x0_,x1_,z0_,z1_):
    for k,v in PR.items():
        for q in v:
            P=np.array(q)
            if P[:,0].max()>x0_ and P[:,0].min()<x1_ and np.ptp(P[:,0])<700: a.plot(P[:,0],P[:,1],color='0.75',lw=.7)
    xs_=np.linspace(45,432.92,800); a.plot(xs_,keel(xs_),'r',lw=1.6)
    xs_=np.linspace(x0,x1,800); a.plot(xs_,under(xs_),'g',lw=1.6)
    xs_=np.linspace(41.25,R3[-1,0],800); a.plot(xs_,top(xs_),'k',lw=1.6)
    for c,col in zip(R,('r','b','m','c','orange','brown','k')): a.plot(c[:,0],c[:,1],color=col,lw=1.6,ls='--')
    a.set_xlim(x0_,x1_); a.set_ylim(z0_,z1_); a.set_aspect('equal'); a.grid(alpha=.3)
draw(axs[0],40,570,-5,60); axs[0].set_title('keel top (red), keelson underside (green), keelson top (black); dashed = the builder\'s reference curves R1-R7')
draw(axs[1],425,575,-2,115); axs[1].set_title('bow'); draw(axs[2],15,80,25,52); axs[2].set_title('stern joint')
fig.savefig('qa/keel_keelson_2d_v2.png',dpi=55,bbox_inches='tight')
