# proposal: top line of the bow on plan_5 (side view), points from the builder's green/red marks, snapped to ink centre in the column (+-1.5 mm)
import sys,json,numpy as np; sys.path.insert(0,'py')
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import uniform_filter1d
from p5map import model_to_p5
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
im=np.array(Image.open('plans/plan_5_aligned.png').convert('L')).astype(float)
def snap(X,Z0,w=1.5):
    px,_=model_to_p5(X,Z0); px=int(round(float(px)))
    zs=np.arange(Z0-w,Z0+w,0.05); ys=[float(model_to_p5(X,z)[1]) for z in zs]
    col=np.array([im[int(round(y)),px-2:px+3].mean() for y in ys]); col=uniform_filter1d(col,9)
    return float(zs[np.argmin(col)])
# (id, X, rough Z from the builder's marks)
upper=[('T1',480.0,117.2),('T2',500.0,118.0),('T3',520.0,119.0),('T4',528.03,119.2),('T5',537.4,119.6)]
lower=[('T7',545.0,102.0),('T8',552.0,102.8),('T9',559.8,103.4)]
P=[(n,X,round(snap(X,z),2),z) for n,X,z in upper+lower]
for p in P: print(p)
json.dump([{'id':n,'X':X,'Z':z} for n,X,z,_ in P]+[{'id':'T6 step bottom','X':537.6,'Z':100.8,'note':'from builder mark, not snapped'}],open('data/top_line_bow_points_v1.json','w'),indent=1)
xl,zl=(480,570),(85,130)
x0,z0=model_to_p5(xl[0],zl[0]); x1,z1=model_to_p5(xl[1],zl[1])
fig,a=plt.subplots(figsize=(14,9)); a.imshow(im[int(z1):int(z0),int(x0):int(x1)],cmap='gray',extent=(*xl,*zl),aspect='equal')
for n,X,z,_ in P: a.plot(X,z,'ro',ms=6); a.text(X,z+1.3,'%s\n%.1f,%.1f'%(n,X,z),fontsize=8,ha='center',color='r')
a.plot(537.6,100.8,'go'); a.text(537.6,98.5,'T6 537.6,100.8',color='g',fontsize=8,ha='center')
for X,c in ((520.03,'tab:blue'),(524.03,'k'),(528.03,'tab:red')): a.axvline(X,color=c,lw=1)
a.set_xlim(*xl);a.set_ylim(*zl);a.grid(alpha=.3); fig.savefig('qa/top_line_bow_points_v1.png',dpi=75,bbox_inches='tight')
