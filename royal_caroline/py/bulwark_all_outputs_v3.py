import json,numpy as np,sys; sys.path.insert(0,'py')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import rhino3dm as r3
from p1a_strip import warped
L=json.load(open('data/bulwark_line_v3.json')); A=json.load(open('data/frames_outer_approved_v2.json')); B=json.load(open('data/frames_outer_approved_v5.json'))
fig,axs=plt.subplots(3,1,figsize=(17,19))
for a,(x0,x1,z0,z1) in zip(axs,((-35,215,95,140),(205,450,92,125),(425,575,90,125))):
    a.imshow(warped((x0,x1),(z0,z1),0.08),cmap='gray',vmin=0,vmax=255,extent=(x0,x1,z0,z1),aspect='equal',alpha=.5)
    for k,v in L.items(): v=np.array(v); a.plot(v[:,0],v[:,1],'-',color='tab:orange',lw=2)
    for b in range(1,46):
        for nm in ('back','mid','front'):
            v=B[str(b)][nm]; o=A[str(b)][nm]
            if not(x0<=v['X']<=x1): continue
            C=np.array(v['curve']); zt=v['top'][1][1] if v.get('top') else C[-1,1]; zo=o['top'][1][1] if o.get('top') else C[-1,1]
            a.plot([v['X']]*2,[zo-3,zo],color='k',lw=.8); a.plot([v['X']]*2,[zo,zt],color='m',lw=2.5)
    a.set_xlim(x0,x1);a.set_ylim(z0,z1);a.grid(alpha=.3)
fig.suptitle('bulwark lower line v2 (builder final) + frame tops: black = approved, magenta = added up to the line')
fig.savefig('qa/bulwark_all_frames_v2.png',dpi=62,bbox_inches='tight')
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n): l=r3.Layer(); l.Name=n; return m.Layers.Add(l)
l1=lay('BULWARK_lower_line_v3_Y0')
for k,v in L.items():
    at=r3.ObjectAttributes(); at.LayerIndex=l1; at.Name=k; m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(x,0,z) for x,z in v]),at)
l2=lay('FRAMES_1-45_outer_+Y_v5')
for b in range(1,46):
    for nm in ('back','mid','front'):
        v=B[str(b)][nm]; C=np.array(v['curve'])[::4]; pts=[r3.Point3d(v['X'],y,z) for y,z in C]+[r3.Point3d(v['X'],*v['curve'][-1])]
        if v.get('top'): pts+= [r3.Point3d(v['X'],y,z) for y,z in v['top']]
        at=r3.ObjectAttributes(); at.LayerIndex=l2; at.Name='F%02d_%s'%(b,nm); m.Objects.AddCurve(r3.PolylineCurve(pts),at)
m.Write('rhino/RoyalCaroline_bulwark_line_and_frame_tops_v3.3dm',7)
