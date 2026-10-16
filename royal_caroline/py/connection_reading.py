import sys,io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import stern_frames_v8 as M
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import splev,splprep
from shapely.geometry import LineString
U=M._U
def ks(X):
    g=U.intersection(LineString([(X,-20),(X,160)])); sg=sorted((l.bounds[1],l.bounds[3]) for l in getattr(g,'geoms',[g])); return sg[1][1],sg[2][0],sg[2][1]
def hermite(P0,T0,P1,T1,n=60):
    t=np.linspace(0,1,n)[:,None]; h00=2*t**3-3*t**2+1; h10=t**3-2*t**2+t; h01=-2*t**3+3*t**2; h11=t**3-t**2
    return h00*P0+h10*T0+h01*P1+h11*T1
def build(fn,X):
    ztop,zk0,zk1=ks(X); O,I,tck=M.frame_profile(X); fy,fz=O[0]
    if not abs(O[0,1]-(ztop-M.OVER))<1e-6:
        zb=37.0 if fn==48 else ztop-M.OVER; ext=[[M.YB,zb],[M.YB+0.25,zb+1.0],[M.YB+0.35*(fy-M.YB),zb+0.45*(fz-zb)],[M.YB+0.8*(fy-M.YB),zb+0.8*(fz-zb)]]; O=np.vstack([ext,O]); tck,u=splprep(O.T,k=3,s=0)
        dy,dz=splev(u,tck,der=1); n=np.c_[dz,-dy]; n/=np.hypot(*n.T)[:,None]; I=O-M.W*n
    zf=zk0+0.5*(zk1-zk0)
    itck=splprep(I.T,k=3,s=0)[0]; uu=np.linspace(0,1,2000); iy,iz=splev(uu,itck); dy,dz=splev(uu,itck,der=1)
    return O,tck,iy,iz,dy,dz,zf,(ztop,zk0,zk1)
def inner(iy,iz,dy,dz,zf,Yj,slope_end=-0.12):
    ok=np.where((iy>=Yj)&(iz-zf>=0.12*(iy-M.YB)+2.0))[0]; j=ok[0]; P0=np.array([iy[j],iz[j]]); T=np.array([dy[j],dz[j]]); T=-T/np.hypot(*T)         # towards the keelson
    P1=np.array([M.YB,zf]); L=np.hypot(*(P0-P1)); T1=np.array([-1.0,-slope_end*-1.0])*0+np.array([-1.0,slope_end]) ; T1=T1/np.hypot(*T1)
    c=hermite(P0,T*L*0.45,P1,T1*L*0.45); return j,c
if __name__=='__main__':
    fig,ax=plt.subplots(1,3,figsize=(21,9))
    for a,(fn,X) in zip(ax,((46,26.0),(47,15.0),(48,4.0))):
        O,tck,iy,iz,dy,dz,zf,(ztop,zk0,zk1)=build(fn,X)
        a.fill_between([-2.65,2.65],-10,ztop,color='#999'); a.fill_between([-2.65,2.65],zk0,zk1,color='#999')
        oy,oz=splev(np.linspace(0,1,800),tck); a.plot(oy,oz,'b',lw=2)
        j,c=inner(iy,iz,dy,dz,zf,5.0); a.plot(c[:,0],c[:,1],'r',lw=2); a.plot(iy[j:],iz[j:],'r',lw=2)
        a.plot([-2.65,-2.65,2.65,2.65],[zf,zk0,zk0,zf],'r--',lw=1)
        a.set_xlim(-8,50); a.set_ylim(max(0,O[0,1]-8),min(100,zk1+25)); a.set_aspect('equal'); a.grid(alpha=.3); a.set_title(f'F{fn} X={X}: inner = tangent spline down to keelson mid-height')
    plt.savefig('qa/frames_connection_reading_v2.png',dpi=60,bbox_inches='tight')
