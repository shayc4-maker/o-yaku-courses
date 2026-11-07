# proposal: lower line of the bulwark (lower of the thin pair running the full length) on plan_1a, points snapped per column
import sys,json,numpy as np; sys.path.insert(0,'py')
from p1a_strip import warped
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
g={-10:108,40:102,100:97.1,160:92.5,200:90.5,240:90,280:89.5,320:89.4,360:89.9,400:91,430:92.4,460:93.7,490:95.9,510:98.4,528:100.2,545:102.1,559.3:103.35}
def lowest(X,z):
    W=warped((X-0.15,X+0.15),(z-3,z+3),0.05).mean(1); zs=z+3-(np.arange(len(W))+.5)*0.05; d=W<140; runs=[];i=0
    while i<len(d):
        if d[i]:
            j=i
            while j<len(d) and d[j]: j+=1
            if (j-i)*0.05<=0.9: runs.append(float(zs[(i+j-1)//2]))
            i=j
        else: i+=1
    return min(runs,key=lambda r:abs(r-z)) if runs else None
P=[]
for X,z in g.items():
    s=lowest(X,z); P.append({'X':X,'Z':round(s,2) if s else None,'guess':z})
for i,p in enumerate(P): p['id']='L%d'%i; print(p)
json.dump(P,open('data/bulwark_low_points_v1.json','w'),indent=1)
fig,axs=plt.subplots(3,1,figsize=(17,19))
for a,(x0,x1,z0,z1) in zip(axs,((-20,200,85,115),(190,440,84,100),(430,570,88,110))):
    a.imshow(warped((x0,x1),(z0,z1),0.05),cmap='gray',vmin=0,vmax=255,extent=(x0,x1,z0,z1),aspect='equal')
    for p in P:
        if p['Z'] and x0<=p['X']<=x1: a.plot(p['X'],p['Z'],'ro',mfc='none',ms=9); a.text(p['X'],p['Z']-1.4,'%s\n%.1f,%.1f'%(p['id'],p['X'],p['Z']),color='r',fontsize=8,ha='center')
    a.set_xlim(x0,x1);a.set_ylim(z0,z1);a.grid(alpha=.3)
fig.savefig('qa/bulwark_low_points_v1.png',dpi=65,bbox_inches='tight')
