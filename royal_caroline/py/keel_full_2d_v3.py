# full 2D of the keel group with ALL corrections (bow chains incl. the builder's new #180, keel/keelson lines, aft straightened/parallel lines #181-#190) + a table of what each aft line corrects
import json,numpy as np
from scipy.interpolate import CubicSpline
from shapely.geometry import Polygon
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R=json.load(open('data/builder_ref_curves_keel_v2.json')); byi={r['i']:np.array(r['pts'])[:,[0,2]] for r in R}; PR=json.load(open('data/step44_profiles.json'))
K2=json.load(open('data/keel_keelson_2d_v2.json')); CH=json.load(open('data/keel_bow_chains_2d_v1.json')); KB=json.load(open('data/keel_bow_keelson_2d_v2.json'))
unit=lambda d:d/np.hypot(*d); ang=lambda d:np.degrees(np.arctan2(d[1],d[0]))
# ---- bow: one blue chain = R2 (top) + connector + the builder's #180 (down to (480.58,-0.66))
R2=byi[174]; S180=byi[180]
if np.hypot(*(S180[0]-np.array([480.58,-0.66])))>1: S180=S180[::-1]          # make it run from the bottom (480.58,-0.66) to the top (552.01,47.39)
Ptop=S180[-1]; dS=unit(S180[-1]-S180[-8]); dR=unit(R2[-1]-R2[-8])          # tangent of #180 at its top end (pointing up-forward); R2 end tangent (pointing down)
Pc=R2[-1]; L=np.hypot(*(Ptop-Pc)); Pb=np.array([Pc,Pc+dR*0.38*L,Ptop+dS*0.38*L,Ptop]); t=np.linspace(0,1,150)[:,None]; CON=(1-t)**3*Pb[0]+3*(1-t)**2*t*Pb[1]+3*(1-t)*t**2*Pb[2]+t**3*Pb[3]
print('blue chain: R2 end tangent %.1f deg (pointing down), #180 top end tangent %.1f deg (pointing up -> %.1f pointing down); connector %.1f mm'%(ang(dR),ang(dS),ang(-dS),L))
print('angle between R2 end and #180 top end tangents: %.2f deg (the connector turns the line by this amount)'%abs((ang(dR)-ang(-dS)+180)%360-180))
# how far is #180 from the approved stem line vertices / the previous blue spline
BLold=np.array(json.load(open('data/keel_stem_front_2d_v1.json'))['spline']); dist=[float(np.min(np.hypot(*(BLold-p).T))) for p in S180[::6]]
print('#180 vs my previous blue spline: max distance %.2f mm (on the common stretch)'%max(d for d,p in zip(dist,S180[::6]) if p[0]>500))
# ---- aft: his lines
aft={181:'inclined line',182:'horizontal',183:'horizontal',184:'horizontal',185:'horizontal',186:'parallel group (same slope)',187:'inclined line',188:'parallel group (same slope)',189:'parallel group (same slope)',190:'horizontal (bottom line)'}
NEW={}; rows=[]
for i,kind in aft.items():
    P=byi[i]; a,b=P[0],P[-1]
    if kind.startswith('horizontal'): z=float(np.mean([a[1],b[1]])); n=[(a[0],z),(b[0],z)]; note='made exactly horizontal at Z=%.3f (his ends %.2f / %.2f, tilt %.3f deg)'%(z,a[1],b[1],np.degrees(np.arctan2(b[1]-a[1],b[0]-a[0])))
    elif kind.startswith('parallel'): n=[tuple(a),tuple(b)]; note='slope %.4f (%.2f deg)'%((b[1]-a[1])/(b[0]-a[0]),np.degrees(np.arctan2(b[1]-a[1],b[0]-a[0])))
    else: n=[tuple(a),tuple(b)]; note='as drawn, angle %.2f deg from horizontal'%np.degrees(np.arctan2(b[1]-a[1],b[0]-a[0]))
    NEW[i]=n; rows.append((i,kind,note))
sl=[(NEW[i][1][1]-NEW[i][0][1])/(NEW[i][1][0]-NEW[i][0][0]) for i in (186,188,189)]; print('parallel group slopes:',[round(s,5) for s in sl])
# the approved edge each aft line corresponds to (nearest collinear edge)
edges=[]
for k,v in PR.items():
    for q in v:
        P=np.array(q)
        if P[:,0].min()<20 and np.ptp(P[:,0])<700:
            Pu=P[np.r_[True,np.any(np.diff(P,axis=0)!=0,axis=1)]]
            for a_,b_ in zip(Pu[:-1],Pu[1:]):
                if np.hypot(*(b_-a_))>1.5: edges.append((k,a_,b_))
print('\naft lines vs the nearest approved edge:')
for i,kind,note in rows:
    a,b=map(np.array,NEW[i]); m=(a+b)/2; d=unit(b-a); best=None
    for k,e0,e1 in edges:
        de=unit(e1-e0); dang=abs((ang(d)-ang(de)+90)%180-90); em=(e0+e1)/2; off=abs((em-m)[0]*(-d[1])+(em-m)[1]*d[0])
        if np.hypot(*(em-m))<8 and dang<12 and (best is None or off+0.3*dang<best[0]): best=(off+0.3*dang,k,dang,off,e0,e1)
    print('#%d %-30s %s | nearest approved edge: %s'%(i,kind,note,('%s angle diff %.2f deg, offset %.2f mm'%(best[1],best[2],best[3])) if best else 'none within 8 mm'))
json.dump(dict(blue_chain=dict(R2=R2.tolist(),connector=CON.tolist(),s180=S180.tolist()),aft={str(k):v for k,v in NEW.items()},aft_notes=rows),open('data/keel_full_2d_v3.json','w'))
# ---- figure
def draw(a,x0,x1,z0,z1,aft=False):
    for k,v in PR.items():
        for q in v:
            P=np.array(q)
            if P[:,0].max()>x0 and P[:,0].min()<x1 and np.ptp(P[:,0])<700: a.plot(P[:,0],P[:,1],color='0.8',lw=.7)
    xs=np.linspace(45,432.92,800); 
    kt=np.array(K2['keel_top']); a.plot(kt[:,0],kt[:,1],'r',lw=1.6); r1=byi[173]; a.plot(r1[:,0],r1[:,1],'r',lw=1.6)
    u=np.array(K2['underside']); a.plot(u[:,0],u[:,1],'g',lw=1.6); tp=np.array(K2['keelson_top']); a.plot(tp[:,0],tp[:,1],'k',lw=1.6)
    inn=np.array(CH['inner']); a.plot(inn[:,0],inn[:,1],'m',lw=1.8)
    for key,col in (('underside_end','g'),('top_end','k')): bb=np.array(KB[key]); a.plot(bb[:,0],bb[:,1],col,lw=1.6,ls='--')
    a.plot(R2[:,0],R2[:,1],'b',lw=1.8); a.plot(CON[:,0],CON[:,1],'b',lw=1.8); a.plot(S180[:,0],S180[:,1],'b',lw=1.8)
    for i,n in NEW.items(): n=np.array(n); a.plot(n[:,0],n[:,1],color='tab:orange' if aft_kind(i) else 'tab:cyan',lw=2); 
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.set_aspect('equal'); a.grid(alpha=.3)
aft_kind=lambda i: aft[i].startswith('horizontal')
fig,axs=plt.subplots(3,1,figsize=(18,24),gridspec_kw={'height_ratios':[.7,1.4,1.3]})
draw(axs[0],-40,575,-14,125); axs[0].set_title('keel group, side view: all corrected lines (red keel top, green/black keelson, magenta keel->stem inner line, blue stem front incl. #180, orange = aft horizontals, cyan = aft inclined/parallel)')
draw(axs[1],470,575,-5,118); axs[1].set_title('bow'); draw(axs[2],-40,30,-14,85); axs[2].set_title('stern lines #181-#190')
fig.savefig('qa/keel_full_2d_v3.png',dpi=52,bbox_inches='tight')
