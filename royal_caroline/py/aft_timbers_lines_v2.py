# lines file: builder's arranged aft lines (9038055e) + aft tops to S1 (approved) + counter timbers (PREVIOUS approved dims v5: strip 2.5, sided 3.0) as lines + PROPOSAL of continuing frames F49-F51 (mid face, extrapolated, for approval)
import json,glob,math,numpy as np,rhino3dm as r3
from scipy.interpolate import splprep,BSpline
SRC=glob.glob('/root/.claude/uploads/*/9038055e-*.3dm')[0]
N=r3.File3dm.Read(SRC); f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; M={}
for i,l in enumerate(N.Layers): n=r3.Layer(); n.Name=l.Name; n.Color=l.Color; M[i]=f.Layers.Add(n)
for o in N.Objects: a=o.Attributes; a.LayerIndex=M[a.LayerIndex]; f.Objects.Add(o.Geometry,a)
def layer(n,c): l=r3.Layer(); l.Name=n; l.Color=c; return f.Layers.Add(l)
def nurbs(P,tol=0.02):
    P=np.array(P); kk=min(3,len(P)-1); tck,u=splprep(P.T,k=kk,s=len(P)*tol**2); t,c,k=tck; m=len(c[0]); cv=r3.NurbsCurve(3,False,k+1,m)
    for i in range(m): cv.Points[i]=r3.Point4d(float(c[0][i]),float(c[1][i]),float(c[2][i]),1.0)
    for i,v in enumerate(t[1:-1]): cv.Knots[i]=float(v)
    return cv
def add(cv,L,name): a=r3.ObjectAttributes(); a.LayerIndex=L; a.Name=name; f.Objects.AddCurve(cv,a)
S=np.array(json.load(open('data/bulwark_line_v3.json'))['S1']); T=json.load(open('data/aft_frames_tops_v1.json'))
# 1 approved tops (tangent extension to S1)
L1=layer('APPROVED_aft_frames_46_48_with_tops_on_S1 (+Y)',(0,0,0,255))
for k,v in T.items(): P=np.array(v['pts']); add(nurbs(np.c_[np.full(len(P),v['X']),P]),L1,k+' X=%g'%v['X'])
Ls=layer('REF_bulwark_lower_line_S1',(0,150,0,255)); m=S[:,0]<45; Q=S[m][::6]; add(nurbs(np.c_[Q[:,0],np.zeros(len(Q)),Q[:,1]]),Ls,'S1 (X-Z, Y=0)')
# 2 counter timbers, previous dims (v5)
exec(open('py/stern_v5.py').read().split("# ---- placement")[0].split("S=json.load")[0].split("from OCP")[0])  # imports only
Sd=json.load(open('data/stern_side_points_v3.json')); tp=json.load(open('data/stern_timber_profile_closed_v1.json')); D=np.array(tp['closed_dense'])
Yc=[7.5,23.2,40.2]; Zd=[120.0,119.7,118.6]; SPL=[1.8,5.5,8.9]; kp=4.7/40.2**2; kz=5.85e-3; Z0=147.3
L2=layer('PROPOSED_counter_timbers_side_profile_at_Y_centre (prev dims 2.5 strip)',(200,80,0,255)); L3=layer('PROPOSED_counter_timbers_centre_paths (3D)',(200,0,200,255)); L4=layer('PROPOSED_counter_timbers_top_points',(200,0,200,255))
idx=np.r_[0,np.arange(1,len(D),max(1,len(D)//40)),len(D)-1]
for i in range(3):
    yc=lambda z,i=i: Yc[i]+math.tan(math.radians(SPL[i]))*(Zd[i]-z); dx=kp*(Yc[i]**2-Yc[0]**2)
    for sgn,s in ((1,'S'),(-1,'P')):
        if sgn<0 and i>=0 and False: pass
        P=np.array([[x+dx,sgn*yc(z),z] for x,z in D[idx]]); P=np.vstack([P,P[0]])
        if sgn>0: add(nurbs(P[:-1],0.05),L2,'T%d%s side profile (sample spline, closed outline from approved v5)'%(i+1,s))
        cz=np.array([75.75,100,Z0]); cx=np.array([-6.6,-39.0,-48.5])+dx  # strip centre: foot (knee end), mid, top (approved strip edges mid)
        add(nurbs(np.c_[[ (np.interp(z,[75.75,99.5,Z0],[-6.6,-31.2,-48.5])+dx) for z in cz],[sgn*yc(z) for z in cz],cz],0.5),L3,'T%d%s centre path'%(i+1,s))
        ztop=Z0-kz*(yc(Z0)**2-(Yc[0]+math.tan(math.radians(SPL[0]))*(Zd[0]-Z0))**2); a=r3.ObjectAttributes(); a.LayerIndex=L4; a.Name='T%d%s top Z%.2f'%(i+1,s,ztop); f.Objects.AddPoint(r3.Point3d(-48.5+dx,sgn*yc(ztop),ztop),a)
# 3 PROPOSAL: continuing frames F49-F51 (mid face) extrapolated quadratically in X from F46-48 mid curves, from wing transom top Z 75.75 to S1
L5=layer('PROPOSED_frames_F49_F51_mid_faces_extrapolated (+Y) FOR APPROVAL',(220,0,0,255))
mids={}
for nm,x in (('F46',28.0),('F47',17.0),('F48',6.0)): P=np.array(T[nm+'_mid']['pts']); mids[x]=P
zs=np.linspace(75.75,134,10)
def Yat(P,z): o=np.argsort(P[:,1]); return np.interp(z,P[o,1],P[o,0])
for nm,xc in (('F49',-5.0),('F50',-16.0),('F51',-27.0)):
    zt=float(np.interp(xc,S[:,0],S[:,1])); zz=np.r_[zs[zs<zt-2],zt]
    pts=[]
    for z in zz:
        ys=[Yat(mids[x],z) for x in (28.0,17.0,6.0)]; c=np.polyfit([28.0,17.0,6.0],ys,2); pts.append([xc,max(np.polyval(c,xc),0),z])
    add(nurbs(pts,0.05),L5,'%s mid X=%g (proposal, quad. extrapolation of F46-48 mid)'%(nm,xc)); print(nm,'Y at Z top %.1f'%pts[-1][1],'Zt %.1f'%zt)
f.Write('rhino/RoyalCaroline_aft_timbers_lines_v2.3dm',7); print('objects',len(f.Objects))
