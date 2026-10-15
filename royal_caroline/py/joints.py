# shared joint definitions (model mm)
import json,numpy as np,sys
from scipy.interpolate import PchipInterpolator
O='/tmp/claude-0/-home-user-o-yaku-courses/63728b8f-e365-510d-8e4b-6775a7fec844/scratchpad/out'
P=dict(SIDED_FR=4.0,T_FLOOR=4.8,T_TOP=3.3,KW=2.65,CLR=0.1,NOTCH=1.0,HOG=1.8,KS_T=4.7,ZKB=-9.37,THROAT_W=5.65)
FX=json.load(open(O+'/frames_X.json'))['X_mm']
KB=np.array([(39.0,37.9),(50.0,33.2),(61.25,29.2),(73.0,24.1),(94.74,18.5),(139.7,11.1),(183.7,7.7),(251.4,7.4),(357.4,7.4),(434.5,9.5),(457.8,11.9),(480.3,16.6),(502.2,23.3),(513.6,28.6),(524.0,33.9)])
Zb=PchipInterpolator(KB[:,0],KB[:,1],extrapolate=True)
def footprint(i):
    x=FX[i-1]; return x-P['SIDED_FR']-P['CLR']/2, x+P['SIDED_FR']+P['CLR']/2
def make_T(Zr):
    return lambda x: np.maximum(Zr(x),0.0)+P['HOG']
def frame_joint(i,T):
    x0,x1=footprint(i); xs=np.linspace(x0,x1,21)
    zn=float(T(xs).min())-P['NOTCH']            # notch bottom in backbone = frame slot top
    zt=float(Zb(xs).min())+P['NOTCH']           # floor top under keelson = keelson notch top
    return zn,zt
