# FAIRING of the body plan stations 1-18 and the waterlines I-VII together. Waterlines = smooth least-squares splines (8 interior knots) through the plan waterline points (weight 1) and the current station crossings (weight 3); every station is then moved by a smooth displacement d_n(Z) (PCHIP through the waterline-minus-station differences at the WL heights, zero below the 2nd point and above Z_VII+25, per-pass cap 0.7 mm, total cap 1.5 mm) applied to the approved points (first 2 points fixed); curves rebuilt with the same interpolating cubic splines as before. 3 passes. Outputs: data/bodyplan_faired_v1.json (same format as bodyplan_splines_v1.json), data/wl_faired_v1.json
import json,numpy as np
from scipy.interpolate import make_lsq_spline,PchipInterpolator,splprep,splev
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
C0=json.load(open('data/bodyplan_splines_v1.json')); W=json.load(open('data/wl_top_points_all.json'))
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
WL={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}; STR={1:2,2:2}; NK=8; CAP_PASS=0.7; CAP_TOT=1.5
def curve_of(P,n):
    P=np.array(P,float); k=STR.get(n,0); q=P[:-1] if k else P; keep=[0]+[i for i in range(1,len(q)) if np.hypot(*(q[i]-q[i-1]))>1e-6]; q=q[keep]; tck,u=splprep(q.T,k=3,s=0); y,z=splev(np.linspace(0,1,600),tck); line=np.c_[y,z]
    return np.r_[line,[P[-1]]] if k else line
def cross(L,z):
    i=np.where((L[:-1,1]-z)*(L[1:,1]-z)<=0)[0]
    if len(i)==0: return None
    j=i[0]; t=(z-L[j,1])/(L[j+1,1]-L[j,1]) if L[j+1,1]!=L[j,1] else 0; return float(L[j,0]+t*(L[j+1,0]-L[j,0]))
def sc(f,x0,x1,thr=1e-3):
    t=np.linspace(x0,x1,4000); k=f(t); s=np.sign(k[np.abs(k)>thr]); return int((np.diff(s)!=0).sum())
pts={n:np.array(C0[str(n)]['points'],float) for n in XST}; orig={n:p.copy() for n,p in pts.items()}; curves={n:curve_of(pts[n],n) for n in XST}
wlsp={}
def fit_wl():
    for k,z in WL.items():
        P=np.array(W[k]['points_XY']); P=P[np.argsort(P[:,0])]; xs=[];ys=[];ws=[]
        for x,y in P: xs.append(x);ys.append(y);ws.append(1.0)
        for n in XST:
            c=cross(curves[n],z)
            if c is not None: xs.append(XST[n]);ys.append(c);ws.append(3.0)
        o=np.argsort(xs); xs=np.array(xs)[o]; ys=np.array(ys)[o]; ws=np.array(ws)[o]
        # merge duplicate x
        for i in range(1,len(xs)):
            if xs[i]<=xs[i-1]: xs[i]=xs[i-1]+1e-4
        ki=np.linspace(xs[0],xs[-1],NK+2)[1:-1]; t=np.r_[[xs[0]]*4,ki,[xs[-1]]*4]; wlsp[k]=make_lsq_spline(xs,ys,t,k=3,w=ws)
def taper(z,z0,z1,z2,z3):      # 0 below z0, smoothstep up to 1 at z1, 1 until z2, smoothstep down to 0 at z3
    up=np.clip((z-z0)/max(z1-z0,1e-6),0,1); dn=np.clip((z3-z)/max(z3-z2,1e-6),0,1); f=lambda u:u*u*(3-2*u); return f(up)*f(dn)
def station_sc(L):
    d1=np.gradient(L,axis=0); d2=np.gradient(d1,axis=0); k=(d1[:,0]*d2[:,1]-d1[:,1]*d2[:,0])/np.maximum((d1**2).sum(1),1e-9)**1.5; s=np.sign(k[5:-5][np.abs(k[5:-5])>1e-3]); return int((np.diff(s)!=0).sum())
SC0={n:station_sc(curve_of(orig[n],n)) for n in XST}
for it in range(3):
    fit_wl()
    for n in XST:
        z2=pts[n][1,1]; Zs=[];Ds=[]
        for k,z in WL.items():
            c=cross(curves[n],z); sp=wlsp[k]
            if c is None or z<=z2+0.5 or not (sp.t[0]<=XST[n]<=sp.t[-1]): continue
            Zs.append(z); Ds.append(float(np.clip(float(sp(XST[n]))-c,-CAP_PASS,CAP_PASS)))
        if len(Zs)<2: continue
        Zs=np.array(Zs); Ds=np.array(Ds); base=pts[n].copy(); chosen=None
        for deg in (2,1,0):          # low-order smooth displacement field: fewest wiggles first reduced if the curvature sign changes grow
            for scale in (1.0,0.75,0.5,0.25):
                co=np.polyfit(Zs,Ds,min(deg,len(Zs)-1)); P=base.copy()
                for i in range(2,len(P)):
                    z=P[i,1]; dz=float(np.polyval(co,z))*taper(z,z2,z2+8,WL['VII'],WL['VII']+25)*scale; new=P[i,0]+dz; P[i,0]=orig[n][i,0]+float(np.clip(new-orig[n][i,0],-CAP_TOT,CAP_TOT))
                L=curve_of(P,n)
                if station_sc(L)<=SC0[n]: chosen=(P,L); break
            if chosen: break
        if chosen: pts[n],curves[n]=chosen
fit_wl()
# metrics
dev={};shift={}
for n in XST:
    sh=np.abs(pts[n][:,0]-orig[n][:,0]); shift[n]=(float(sh.max()),float(sh.mean()))
    d=[]
    for k,z in WL.items():
        c=cross(curves[n],z); sp=wlsp[k]
        if c is not None and sp.t[0]<=XST[n]<=sp.t[-1]: d.append(abs(float(sp(XST[n]))-c))
    dev[n]=max(d) if d else 0.0
print('station: max point shift / mean shift (mm) | max distance to the faired waterlines | curvature sign changes old -> new')
for n in XST: print(' st %2d: %.2f / %.2f | %.2f | %d -> %d'%(n,*shift[n],dev[n],station_sc(np.array(C0[str(n)]['curve'])),station_sc(curves[n])))
print('waterlines: curvature sign changes (|k|>1e-3): old plan WL -> faired')
for k,z in WL.items():
    P=np.array(W[k]['points_XY']); P=P[np.argsort(P[:,0])]
    from scipy.interpolate import CubicSpline
    old=CubicSpline(P[:,0],P[:,1]); print(' WL %-3s %d -> %d'%(k,sc(lambda t:old(t,2),P[0,0],P[-1,0]),sc(lambda t:wlsp[k](t,2),wlsp[k].t[0],wlsp[k].t[-1])))
out={str(n):dict(points=[[round(float(a),3),round(float(b),3)] for a,b in pts[n]],curve=curves[n].round(3).tolist(),curvature_sign_changes=station_sc(curves[n])) for n in XST}; json.dump(out,open('data/bodyplan_faired_v1.json','w'))
json.dump({k:dict(z=z,knots=[float(v) for v in wlsp[k].t],coef=[float(v) for v in wlsp[k].c]) for k,z in WL.items()},open('data/wl_faired_v1.json','w'))
np.save('/tmp/claude-0/x/fair_state.npy',dict(curves=curves,orig={n:np.array(C0[str(n)]['curve']) for n in XST}),allow_pickle=True)
