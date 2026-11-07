import sys,json,numpy as np
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import map_coordinates
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
KX,X0,KZ,ZR=0.08511,-357.14,0.0850,2110.0
cal=json.load(open('data/plan_calibration_v2.json'))['sheer_1a']; ax_,bx_,cx_=cal['dX']; az,bz,cz=cal['dZ']
ink=lambda X,Z:(X+ax_+bx_*(X-270)+cx_*Z, Z+az+bz*(X-270)+cz*Z)
im=np.array(Image.open('plans/plan_1a_aligned.png').convert('L')).astype(float)
def warped(xl,zl,res=0.085):
    nx=int((xl[1]-xl[0])/res); nz=int((zl[1]-zl[0])/res); Xg=xl[0]+(np.arange(nx)+.5)*res; Zg=zl[1]-(np.arange(nz)+.5)*res; XX,ZZ=np.meshgrid(Xg,Zg); xi,zi=ink(XX,ZZ)
    return map_coordinates(im,[ZR-zi/KZ,(xi-X0)/KX],order=1,cval=255)
if __name__=='__main__':
    x0,x1,z0,z1=map(float,sys.argv[1:5]); W=warped((x0,x1),(z0,z1))
    fig,a=plt.subplots(figsize=(16,16*(z1-z0)/(x1-x0)+.6)); a.imshow(W,cmap='gray',vmin=0,vmax=255,extent=(x0,x1,z0,z1),aspect='equal')
    a.set_xticks(np.arange(x0,x1+1,10)); a.set_yticks(np.arange(z0,z1+1,10)); a.grid(alpha=.35); fig.savefig(sys.argv[5],dpi=70,bbox_inches='tight')
