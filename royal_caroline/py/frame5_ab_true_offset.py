# same as frame5_ab_overlay but the inner lines are offset by the TRUE in-plane distance delta = t*sqrt(1+(dZ*dY/dX)^2) so that the thickness is 3.2 mm normal to the hull surface (surface tangents: section line + vector from line A to line B at equal Z)
import numpy as np,sys,io,contextlib
with contextlib.redirect_stdout(io.StringIO()):
    exec(open('py/frame5_ab_overlay.py').read().split("A=outer_line(41)")[0])
from scipy.signal import savgol_filter
t=3.2; XA,XB=X[40],X[39]; dX=XB-XA
A=outer_line(41); B=outer_line(40)
def resample(L,n=500):
    s=np.r_[0,np.cumsum(np.hypot(*np.diff(L,axis=0).T))]; u=np.linspace(0,s[-1],n); return np.c_[np.interp(u,s,L[:,0]),np.interp(u,s,L[:,1])]
A=resample(A); B=resample(B)
def Yat_at_Z(L,z):                    # outer Y of line L at height z (max over crossings)
    ys=[l0[0]+(l1[0]-l0[0])*(z-l0[1])/(l1[1]-l0[1]) for l0,l1 in zip(L[:-1],L[1:]) if (l0[1]-z)*(l1[1]-z)<=0 and l0[1]!=l1[1]]; return max(ys) if ys else np.nan
def true_inner(L,other,t,sign):
    sm=np.c_[savgol_filter(L[:,0],31,3),savgol_filter(L[:,1],31,3)]; d=np.gradient(sm,axis=0); d/=np.hypot(*d.T)[:,None]
    m=np.c_[-d[:,1],d[:,0]]
    if m[len(m)//2,0]>0: m=-m                      # inward = towards smaller Y
    dY=np.array([sign*(Yat_at_Z(other,z)-Yat_at_Z(L,z)) for z in L[:,1]]); dY=np.where(np.isnan(dY),0,dY)
    delta=t*np.sqrt(1+(d[:,1]*dY/dX)**2); return L+m*delta[:,None],delta
Ain,dA=true_inner(A,B,t,+1); Bin,dB=true_inner(B,A,t,-1)
Ain3=A+( -(np.c_[-np.gradient(A,axis=0)[:,1],np.gradient(A,axis=0)[:,0]]/np.hypot(*np.gradient(A,axis=0).T)[:,None]) *0)   # placeholder
print('true in-plane offset: A %.2f..%.2f mm, B %.2f..%.2f mm (normal thickness %.1f)'%(dA.min(),dA.max(),dB.min(),dB.max(),t))
# crossing check: does B inner pass outside A outer?
for z in (6,10,15,20,25,30):
    ya,yb,ybi=Yat_at_Z(A,z),Yat_at_Z(B,z),Yat_at_Z(Bin,z); print(f'Z {z}: A outer {ya:.1f}  B outer {yb:.1f}  B inner {ybi:.1f}  -> B inner minus A outer {ybi-ya:+.1f}')
fig,ax=plt.subplots(1,3,figsize=(21,9))
for a,(xl,yl) in zip(ax,(((0,70),(0,150)),((30,70),(40,110)),((0,40),(0,45)))):
    a.plot(*A.T,'b',lw=2,label='A outer (frame 5)'); a.plot(*Ain.T,'b--',lw=1.3,label='A inner: normal thickness 3.2 (true in-plane offset)')
    a.plot(*B.T,'r',lw=2,label='B outer (frame 6)'); a.plot(*Bin.T,'r--',lw=1.3,label='B inner: same')
    a.set_xlim(*xl); a.set_ylim(*yl); a.set_aspect('equal'); a.grid(alpha=.3)
ax[0].legend(fontsize=8); ax[0].set_title('with true in-plane offsets'); plt.savefig('qa/frame5_AB_true_offset_2d.png',dpi=65,bbox_inches='tight')
