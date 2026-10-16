import sys,io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import connection_reading as C
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import splev
Ys=np.linspace(2.65,50,300); sm=lambda t:np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
D={}
for fn,X in ((46,26.0),(47,15.0),(48,4.0)):
    O,tck,iy,iz,dy,dz,zf,(ztop,zk0,zk1)=C.build(fn,X); oy,oz=splev(np.linspace(0,1,3000),tck); m=oy<=60
    D[fn]=dict(out=np.interp(Ys,oy[m],oz[m]),I=np.interp(Ys,iy[(iy>=0)&(iy<=60)],iz[(iy>=0)&(iy<=60)]),zf=zf,kb=(ztop,zk0,zk1),O=O,tck=tck,iy=iy,iz=iz,dy=dy,dz=dz)
# anchor: F46 top = tangent spline to its keelson mid-height + offset curve (as in the reading)
d=D[46]; j,c=C.inner(d['iy'],d['iz'],d['dy'],d['dz'],d['zf'],5.0)
ty=np.r_[c[:,0][::-1],d['iy'][j:]]; tz=np.r_[c[:,1][::-1],d['iz'][j:]]; o=np.argsort(ty); top46=np.interp(Ys,ty[o],tz[o])
top={46:top46}
h46=top46-D[46]['out']
def fixkeel(y,z,zf,Y1=14.0):
    Y1=y[np.where((y>=10)&(z>=zf+0.10*(y-2.65)+0.5))[0][0]]      # smooth monotone entry from the keelson mid-height: Hermite (2.65,zf,slope .08) -> (Y1, z(Y1), slope of z there)
    i=np.where(y>=Y1)[0][0]; sl=(z[i+1]-z[i-1])/(y[i+1]-y[i-1]); t=(y[:i+1]-2.65)/(y[i]-2.65); L=y[i]-2.65
    h00=2*t**3-3*t**2+1; h10=t**3-2*t**2+t; h01=-2*t**3+3*t**2; h11=t**3-t**2
    zz=z.copy(); zz[:i+1]=h00*zf+h10*L*0.08+h01*z[i]+h11*L*sl; return zz
for fn in (47,48):       # F46's thickness profile scaled to meet this keelson at mid-height, smooth entry (no dip), fading into the rib offset curve far from the keel
    sc=(D[fn]['zf']-D[fn]['out'][0])/h46[0]; w=sm((Ys-25)/20); zk=D[fn]['kb'][1]; zfm=min(D[fn]['zf'],max(zk+0.6,0)) if fn==48 else D[fn]['zf']; ch=fixkeel(Ys,D[fn]['out']+sc*h46,zfm); top[fn]=(1-w)*ch+w*D[fn]['I']
def pav(v):      # isotonic (non-decreasing) regression of the slopes
    v=list(v); w=[1]*len(v); i=0
    blocks=[[x,1] for x in v]; out=[]
    for b in blocks:
        out.append(b)
        while len(out)>1 and out[-2][0]>out[-1][0]:
            m=(out[-2][0]*out[-2][1]+out[-1][0]*out[-1][1])/(out[-2][1]+out[-1][1]); n=out[-2][1]+out[-1][1]; out[-2:]=[[m,n]]
    return np.concatenate([[m]*n for m,n in out])
def concave_only(y,z,Yend=44.5):      # slope never decreases (z''>=0, 'concave' in the builder's wording); ends keep their values
    m=y<=Yend; yy,zz=y[m],z[m]; sl=np.gradient(zz,yy); si=pav(sl)
    zn=zz[0]+np.concatenate([[0],np.cumsum(0.5*(si[1:]+si[:-1])*np.diff(yy))]); zn=zn+(zz[-1]-zn[-1])*(yy-yy[0])/(yy[-1]-yy[0])
    out=z.copy(); out[m]=zn; return out
for fn in (46,47,48): top[fn]=concave_only(Ys,top[fn])
if __name__=='__main__':
    fig,ax=plt.subplots(figsize=(9,11))
    for fn,col in ((46,'tab:blue'),(47,'tab:green'),(48,'tab:red')):
        d=D[fn]; ax.plot(Ys[Ys<=45],d['out'][Ys<=45],color=col,lw=2,label=f'F{fn}'); ax.plot(Ys[Ys<=45],top[fn][Ys<=45],color=col,lw=1.5)
        zt,k0,k1=d['kb']; ax.fill_between([-2.65,2.65],k0,k1,color=col,alpha=.35); ax.fill_between([-2.65,2.65],-10,zt,color=col,alpha=.2)
        print(fn,'top at keelson wall Z=%.1f keelson %.1f..%.1f'%(top[fn][0],k0,k1))
    ax.set_xlim(-8,45); ax.set_ylim(10,100); ax.set_aspect('equal'); ax.grid(alpha=.3); ax.legend(); ax.set_title('top lines: F46 thickness profile, smooth entry meeting the keelson at its own height, slope never decreases (all concave)')
    plt.savefig('qa/frames_connection_chain_v8.png',dpi=70,bbox_inches='tight')
