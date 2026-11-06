# Clean 2D of keel and keelson from the builder STEP: reference splines (ramp vertices), constant offsets, 8 mm pockets centred on the frames, walls >= W both sides
import sys,json,numpy as np
OFF=float(sys.argv[1]) if len(sys.argv)>1 else 1.0; W=float(sys.argv[2]) if len(sys.argv)>2 else 1.0
sys.path.insert(0,'py'); import step_chain as S
from scipy.interpolate import UnivariateSpline
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
XF=json.load(open('data/frames_X.json'))['X_mm']
sh=S.load(); sol=S.solids(sh)
def split_chain(C,top):
    i_end=int(np.argmax(C[:,0])); A=C[:i_end+1]; B=C[i_end:]
    nh=lambda ch: sum(1 for k in range(len(ch)-1) if abs(ch[k,1]-ch[k+1,1])<2e-3 and abs(ch[k,0]-ch[k+1,0])>1.0)
    ch=A if nh(A)>=nh(B) else B          # the side of the solid that carries the pockets / teeth
    return ch if ch[0,0]<ch[-1,0] else ch[::-1]
def ramp_and_plateaus(ch,xr):
    ramp=[];plat=[]
    for k in range(len(ch)):
        p=ch[k]; h=any(q is not None and abs(q[1]-p[1])<2e-3 and abs(q[0]-p[0])>1.0 for q in (ch[k-1] if k>0 else None, ch[k+1] if k+1<len(ch) else None))
        (plat if h else ramp).append(p)
    ramp=np.array(ramp); plat=np.array(plat).reshape(-1,2)
    R=[p for p in ramp if not(len(plat[np.abs(plat[:,0]-p[0])<1e-3]) and p[1]>=plat[np.abs(plat[:,0]-p[0])<1e-3][:,1].min()-1e-3 and False)]
    R=np.array(R); R=R[(R[:,0]>=xr[0])&(R[:,0]<=xr[1])]; R=R[np.argsort(R[:,0])]
    pl=plat[np.argsort(plat[:,0])]; pk=[]
    for k in range(len(pl)-1):
        if abs(pl[k,1]-pl[k+1,1])<1e-3 and 1.0<pl[k+1,0]-pl[k,0]<12 and not any(abs(pl[k,0]-q[0])<1e-3 for q in pk): pk.append((pl[k,0],pl[k+1,0],pl[k,1]))
    return R,pk
ks_ch=split_chain(S.side_chain(sol[15])[0],top=False); kt_ch=split_chain(S.side_chain(sol[16])[0],top=True)
Rs,pks=ramp_and_plateaus(ks_ch,(45,540)); Rk,pkk=ramp_and_plateaus(kt_ch,(45,540))
# keep only ramp vertices that lie on the smooth line (reject the stair-top vertices): iterative spline fit
def fit(R,rej):
    sp=UnivariateSpline(R[:,0],R[:,1],k=3,s=len(R)*0.004)
    for _ in range(4):
        r=R[:,1]-sp(R[:,0]); m=abs(r)<rej; sp=UnivariateSpline(R[m,0],R[m,1],k=3,s=m.sum()*0.004)
    return sp,R[m],R[~m]
spS,Rs_ok,Rs_bad=fit(Rs,0.25); spK,Rk_ok,Rk_bad=fit(Rk,0.25)
print('keelson reference spline: %d vertices used, %d rejected; keel reference spline: %d used, %d rejected'%(len(Rs_ok),len(Rs_bad),len(Rk_ok),len(Rk_bad)))
xs=np.arange(45,540,0.25)
# pockets: one per frame, X-4..X+4; floor / ceiling = his plateau level at that frame (nearest plateau centre)
def plateau_at(pk,X):
    c=[(abs((a+b)/2-X),L) for a,b,L in pk]; d,L=min(c); return (L if d<3 else None)
rows=[]
for n,X in enumerate(XF,1):
    if X<50 or X>528: continue
    Lc=plateau_at(pks,X); Lf=plateau_at(pkk,X)
    if Lc is None or Lf is None: continue
    rows.append((46-n,X,Lf,Lc))
a_=lambda X:X-4; b_=lambda X:X+4
# constant offsets (mm): keelson line down by OFF, keel line up by e (smallest constant giving walls>=W at every frame)
XJ=526.6
ks=lambda x: spS(x)-OFF
need_e=max(Lf+W-float(min(spK(a_(X)),spK(b_(X)))) for _,X,Lf,Lc in rows); e=max(need_e,0.0); kt0=lambda x: spK(x)+e
# bow: keel line may not pass the keelson line; the gap tapers to 0 exactly at the stem start (X=526.6) and the two lines are one line beyond
def kt(x):
    x=np.asarray(x,float); g=np.where(x>=XJ,0.0,np.clip((XJ-x)/12.0,0,1)*1e9)   # taper window 12 mm: allowed gap = distance to junction / 12 * 1.0 (mm)
    allowed=np.clip((XJ-x)/12.0,0,1)*1.0
    return np.minimum(kt0(x),ks(x)-allowed)
print('keel line raised by constant e = %.2f mm (needed %.2f); keelson line lowered by %.2f mm'%(e,need_e,OFF))
pk_out=[]; walls=[]
for b,X,Lf,Lc in rows:
    ce=max(Lc,float(ks(a_(X)))+W,float(ks(b_(X)))+W); pk_out.append(dict(builder=b,X=round(X,2),a=round(X-4,2),b=round(X+4,2),keel_floor=round(Lf,2),keelson_ceiling=round(ce,2),keelson_ceiling_his=round(Lc,2)))
    walls.append((b,min(float(kt(a_(X)))-Lf,float(kt(b_(X)))-Lf),ce-max(float(ks(a_(X))),float(ks(b_(X)))), ce-Lf))
print('min wall keel %.2f, min wall keelson %.2f, pocket height (ceiling-floor) min %.2f max %.2f'%(min(w[1] for w in walls),min(w[2] for w in walls),min(w[3] for w in walls),max(w[3] for w in walls)))
clear=min(float(min(ks(np.linspace(X-4,X+4,20))-kt(np.linspace(X-4,X+4,20)))) for _,X,_,_ in rows); print('minimum gap between the two lines at the frames (outside pocket walls) %.2f mm'%clear)
json.dump(dict(offset=OFF,wall=W,keel_raise=e,pockets=pk_out,keel_line=dict(X=xs[::8].round(2).tolist(),Z=kt(xs[::8]).round(3).tolist()),keelson_line=dict(X=xs[::8].round(2).tolist(),Z=ks(xs[::8]).round(3).tolist())),open('data/keel_keelson_clean_v1.json','w'))
fig,axs=plt.subplots(3,1,figsize=(18,17),gridspec_kw={'height_ratios':[1,1,.7]})
def draw(a,xl,yl,lab):
    a.plot(ks_ch[:,0],ks_ch[:,1],color='#aaa',lw=.8,ls='--'); a.plot(kt_ch[:,0],kt_ch[:,1],color='#aaa',lw=.8,ls='--')
    xx=np.linspace(*xl,900); a.plot(xx,ks(xx),'g',lw=2); a.plot(xx,kt(xx),color='tab:brown',lw=2)
    for p in pk_out:
        if xl[0]-6<p['X']<xl[1]+6:
            for (x0,x1,fl,ln,col) in ((p['a'],p['b'],p['keel_floor'],kt,'tab:brown'),(p['a'],p['b'],p['keelson_ceiling'],ks,'g')): a.plot([x0,x0,x1,x1],[float(ln(x0)),fl,fl,float(ln(x1))],color=col,lw=2)
            a.text(p['X'],yl[1]-(yl[1]-yl[0])*.04,str(p['builder']),ha='center',fontsize=8)
    a.set_xlim(*xl); a.set_ylim(*yl); a.grid(alpha=.3); a.set_ylabel('Z (mm)')
draw(axs[0],(470,545),(-2,45),''); draw(axs[1],(380,445),(0,12),''); draw(axs[2],(45,545),(-2,60),'')
axs[0].set_title('Keel top (brown) and keelson inner line (green): reference spline from the STEP, constant offset, a full 8 mm pocket at every frame; dashed gray = builder STEP outline')
fig.savefig('qa/keel_keelson_clean_2d.png',dpi=55,bbox_inches='tight')
