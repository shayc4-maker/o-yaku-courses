import sys,json,numpy as np, rhino3dm as r3
from scipy.interpolate import splprep, splev, make_lsq_spline
S=sys.argv[1]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
import os; os.makedirs(PK+'/images',exist_ok=True)
meta=json.load(open(O+'/meta.json')); K=meta['K']; WLZ=meta['WLZ_mm']; STX={int(k):v for k,v in meta['STX'].items()}
st=np.load(O+'/stations.npy',allow_pickle=True).item()
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def layer(name,col,parent=None):
    L=r3.Layer(); L.Name=name; L.Color=(*col,255)
    if parent is not None: L.ParentLayerId=m.Layers[parent].Id
    return m.Layers.Add(L)
def attr(li,name=None):
    a=r3.ObjectAttributes(); a.LayerIndex=li
    if name: a.Name=name
    return a
def nurbs_from_tck(t,c,k=3):
    n=len(c[0]); crv=r3.NurbsCurve(3,False,k+1,n)
    for i in range(n): crv.Points[i]=r3.Point4d(float(c[0][i]),float(c[1][i]),float(c[2][i]),1.0)
    kn=t[1:-1]
    for i,v in enumerate(kn): crv.Knots[i]=float(v)
    return crv
def fit_free(P3,tol=0.04,maxcp=40):
    # smoothing spline with increasing CP until max deviation <= tol (mm)
    P3=np.asarray(P3); u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P3,axis=0),axis=1))]; u/=u[-1]
    for ncp in range(8,maxcp+1,2):
        nint=ncp-3; t=np.r_[[0]*4,np.linspace(0,1,nint+1)[1:-1],[1]*4]
        sp=[make_lsq_spline(u,P3[:,j],t,k=3) for j in range(3)]
        Q=np.c_[[s(u) for s in sp]].T; dev=np.linalg.norm(Q-P3,axis=1).max()
        if dev<=tol: break
    return t,[s.c for s in sp],ncp,dev
def fit_uniform(P3,ncp):
    P3=np.asarray(P3); u=np.r_[0,np.cumsum(np.linalg.norm(np.diff(P3,axis=0),axis=1))]; u/=u[-1]
    nint=ncp-3; t=np.r_[[0]*4,np.linspace(0,1,nint+1)[1:-1],[1]*4]
    sp=[make_lsq_spline(u,P3[:,j],t,k=3) for j in range(3)]
    Q=np.c_[[s(u) for s in sp]].T; return t,[s.c for s in sp],np.linalg.norm(Q-P3,axis=1).max()
L_ST=layer('STATIONS_3D_bodyplan',(0,0,200))
L_LO=layer('STATIONS_LOFT_uniform14',(0,140,200))
L_BP=layer('BODYPLAN_2D_as_drawn',(120,0,160))
L_WL=layer('WATERLINES_from_A1-4_plan',(200,0,0))
L_GR=layer('GRID',(150,150,150))
L_TX=layer('LABELS',(60,60,60))
X_BP=-80.0   # body-plan view plane (aft of hull)
rep=[]
for s in range(1,19):
    key=f'{s}_1a' if f'{s}_1a' in st else f'{s}_1b'
    if s==8: key='8_1a'
    P=st[key]; X=STX[s]
    P3=np.c_[np.full(len(P),X),P[:,0],P[:,1]]
    t,c,ncp,dev=fit_free(P3); m.Objects.AddCurve(nurbs_from_tck(t,c),attr(L_ST,f'ST{s:02d}'))
    tu,cu,devu=fit_uniform(P3,14); m.Objects.AddCurve(nurbs_from_tck(tu,cu),attr(L_LO,f'ST{s:02d}_loft'))
    # 2D body plan as drawn: aft stations (9-18 and 8 from A1/2) on -Y, fwd (1-8 from A1/3) on +Y, plane X=X_BP
    for kk in ([key] + (['8_1b'] if s==8 else [])):
        Q=st[kk]; sg=-1 if kk.endswith('1a') else 1
        Q3=np.c_[np.full(len(Q),X_BP),sg*Q[:,0],Q[:,1]]
        t2,c2,_,_=fit_free(Q3); m.Objects.AddCurve(nurbs_from_tck(t2,c2),attr(L_BP,f'BP{s:02d}_{kk[-2:]}'))
    top=P3[np.argmax(P3[:,2])]
    m.Objects.AddTextDot(str(s),r3.Point3d(*top+[0,0,3]),attr(L_TX))
    rep.append((s,ncp,round(dev,3),round(devu,3)))
# grid: baseline & WLs at each station span, centreline
xmax=STX[1]+40; xmin=-40
for n,z in WLZ.items():
    m.Objects.AddLine(r3.Point3d(xmin,0,z),r3.Point3d(xmax,0,z),attr(L_GR,'WL_'+n))
    m.Objects.AddTextDot('WL '+n,r3.Point3d(xmin-10,0,z),attr(L_TX))
    m.Objects.AddLine(r3.Point3d(X_BP,-90,z),r3.Point3d(X_BP,90,z),attr(L_GR,'BP_WL_'+n))
m.Objects.AddLine(r3.Point3d(X_BP,0,-12),r3.Point3d(X_BP,0,150),attr(L_GR,'BP_centreline'))
for s,X in STX.items(): m.Objects.AddLine(r3.Point3d(X,0,-12),r3.Point3d(X,0,145),attr(L_GR,f'station_{s}'))
# plan-view waterlines (A1/4) as 3D curves at their Z
pv=json.load(open(S+'/trpv.json'))
PV=np.array([4250.86,4424.17,4686.11,5073.29,5466.76,5852.96,6249.78,6637.65,7034.05,7429.45,7820.09,8217.85,8616.43,9010.18,9408.80,9805.84,10198.30,10457.28])
PR=np.array([4194.98,4366.72,4627.84,5025.13,5409.92,5795.59,6188.67,6571.02,6964.26,7377.90,7759.91,8142.88,8550.92,8947.17,9341.93,9741.53,10137.89,10397.40])
f=np.polyfit(PV,PR,1); LO=(-0.00716,1271.3)
for n,c in pv.items():
    c=np.array(c); X=(np.polyval(f,c[:,0])-PR[0])*K; Y=(np.polyval(LO,c[:,0])-c[:,1])*K
    if n in ('VI','VII'):
        keep=X<(6500-PR[0])*K; X,Y=X[keep],Y[keep]; nm=f'WL_{n}_plan_stern_part_only'
    else: nm=f'WL_{n}_plan'
    o=np.argsort(X); P3=np.c_[X[o],Y[o],np.full(len(X),WLZ[n])]
    P3=P3[::3]
    t,cc,_,_=fit_free(P3,tol=0.06); m.Objects.AddCurve(nurbs_from_tck(t,cc),attr(L_WL,nm))
m.Write(PK+'/RoyalCaroline_lines_1to48_v1.3dm',8)
print('station fits (st, CPs, max dev mm free, max dev uniform14):'); [print(r) for r in rep]
