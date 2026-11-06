import numpy as np, rhino3dm as r3, collections
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
f=r3.File3dm.Read('rhino/RoyalCaroline_lines_v2.3dm'); L={i:f.Layers[i].Name for i in range(len(f.Layers))}
def samp(c,n=300):
    d=c.Domain; return np.array([[p.X,p.Y,p.Z] for p in (c.PointAt(d.T0+(d.T1-d.T0)*u) for u in np.linspace(0,1,n))])
ST={};WLc={}
for o in f.Objects:
    n=L[o.Attributes.LayerIndex]; nm=o.Attributes.Name; g=o.Geometry
    if n=='STATIONS_3D_bodyplan_NEW' and not nm.endswith('straight_top'): ST[int(nm[2:4])]=samp(g)
    if n=='WATERLINES_NEW_from_plan': WLc[nm[3:]]=samp(g,700)
XST={1:527.8,2:505.8,3:472.0,4:438.0,5:404.4,6:370.7,7:336.0,8:303.4,9:270.9,10:235.7,11:202.2,12:169.7,13:136.2,14:103.4,15:70.6,16:36.8,17:14.6,18:0.0}
ZW={'I':8.7,'II':17.4,'III':26.1,'IV':34.8,'V':43.4,'VI':52.1,'VII':69.5}; rows=[]
for k,Z in ZW.items():
    w=WLc[k]
    for n,X in XST.items():
        s=ST[n]; i=np.where((s[:-1,2]-Z)*(s[1:,2]-Z)<=0)[0]
        for ii in i:
            t=(Z-s[ii,2])/(s[ii+1,2]-s[ii,2]) if s[ii+1,2]!=s[ii,2] else 0; ys=s[ii,1]+t*(s[ii+1,1]-s[ii,1])
            j=np.argmin(abs(w[:,0]-X))
            if abs(w[j,0]-X)>1.5 or abs(w[j,1]-ys)>12: continue
            rows.append((k,n,ys,w[j,1],w[j,1]-ys))
R=np.array([r[4] for r in rows]); print('crossings',len(rows),'mismatch WL-station: mean %.2f std %.2f max abs %.2f mm'%(R.mean(),R.std(),abs(R).max()),'; within 1 mm: %d%%, within 2 mm: %d%%'%(100*(abs(R)<1).mean(),100*(abs(R)<2).mean()))
for r in sorted(rows,key=lambda r:-abs(r[4]))[:6]: print('  WL',r[0],'ST',r[1],'station Y %.2f  WL Y %.2f  diff %+.2f'%(r[2],r[3],r[4]))
fig,ax=plt.subplots(3,1,figsize=(16,15),dpi=80,gridspec_kw={'height_ratios':[1,1,1.25]})
for n,s in ST.items():
    ax[2].plot(s[:,1]*(1 if n>=9 else -1),s[:,2],lw=1); ax[0].plot(s[:,0],s[:,1],'-',lw=.6,color='r'); ax[1].plot(s[:,0],s[:,2],'-',lw=.6,color='r')
for k,w in WLc.items(): ax[0].plot(w[:,0],w[:,1],lw=1,color='#e08000'); ax[1].plot([w[0,0],w[-1,0]],[ZW[k]]*2,lw=.6,color='#e08000')
ax[0].set_aspect('equal'); ax[0].set_title('Top view XY: new waterlines I-VII (orange) + stations (red)'); ax[1].set_aspect('equal'); ax[1].set_title('Side view XZ: stations (red), waterline levels (orange)')
ax[2].set_aspect('equal'); ax[2].set_title('Body plan YZ: stations 9-18 on +Y (right), 1-8 on -Y (left)')
fig.savefig('qa/lines_v2_check.png',bbox_inches='tight')
