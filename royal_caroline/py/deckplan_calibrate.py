# calibrate the deck plans over the FULL length: the silhouette (outermost outline) of a deck plan = maximum half-breadth over Z of the hull; the model gives it from the approved frames (max Y of each face curve). Fit px->X (offset, scale), centre row (offset + tilt) and report residuals. Bow right, stern left.
import sys,json,numpy as np
sys.path.insert(0,'py')
from deckplan_outline import *
from scipy.optimize import least_squares
from scipy.ndimage import median_filter
A=json.load(open('data/frames_outer_approved_v1.json')); mx=[]
for b,fr in A.items():
    for nm,v in fr.items(): C=np.array(v['curve']); mx.append((v['X'],float(C[:,0].max())))
mx=np.array(sorted(mx)); Ymax=lambda X: np.interp(X,mx[:,0],mx[:,1])
out={}
for k in ('4a','2b','4b'):
    ink=load(k); m,top,bot=outline(ink); xs=np.where(~np.isnan(top))[0]; x0_,x1_=xs.min(),xs.max()
    hw=(bot-top)/2; mid=(top+bot)/2
    sel=xs[(xs>x0_+150)&(xs<x1_-150)]; cols=sel[::8]
    results=[]
    for sc in (11.70,11.75,11.81):
        def res(p,sc=sc):
            xo,d=p; X=(cols-xo)/sc; ok=(X>45)&(X<510); r=np.zeros(len(cols)); r[ok]=hw[cols][ok]/sc-d-Ymax(X[ok]); return r
        best=None
        for xo0 in np.arange(x0_-300,x0_+1500,50):
            r=least_squares(res,[xo0,2.0],bounds=([-3000,-6.0],[3000,10.0]),loss='soft_l1',f_scale=1.5); X=(cols-r.x[0])/sc; okm=(X>45)&(X<510)
            if okm.sum()<150: continue
            c=np.sqrt(np.mean(r.fun[okm]**2))
            if best is None or c<best[0]: best=(c,r.x,np.median(np.abs(r.fun[okm])))
        results.append((sc,)+best)
    for sc,c,(xo,d),md in results: print('plan %s scale %.2f px/mm: x offset %.1f px, plan outline wider than the model max half-breadth by %.2f mm; rms %.2f median |d| %.2f mm'%(k,sc,xo,d,c,md))
    sc,c,(xo,d),md=min(results,key=lambda r:r[1]); X=(sel-xo)/sc; ok=(X>45)&(X<510); xx=sel[ok]; mm=mid[xx]; p=np.polyfit(xx,mm,1)
    for _ in range(4): rr=mm-np.polyval(p,xx); g=np.abs(rr)<2*np.median(np.abs(rr))+1; p=np.polyfit(xx[g],mm[g],1)
    out[k]=dict(x_offset_px=float(xo),px_per_mm=float(sc),width_excess_mm=float(d),rms_mm=float(c),median_abs_mm=float(md),centre_row0=float(p[1]),centre_slope=float(p[0]),hull_x_mm=[float((x0_-xo)/sc),float((x1_-xo)/sc)])
    print('   -> best scale %.2f: centre row = %.1f + %.5f x (tilt %.3f deg); hull extent X %.1f .. %.1f mm'%(sc,p[1],p[0],np.degrees(np.arctan(p[0])),(x0_-xo)/sc,(x1_-xo)/sc))
json.dump(out,open('data/deckplans_calibration_v1.json','w'),indent=1)
