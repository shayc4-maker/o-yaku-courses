import json,numpy as np,sys; sys.path.insert(0,'py')
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import rhino3dm as r3
from p1a_strip import warped
L=json.load(open('data/bulwark_line_v1.json')); A=json.load(open('data/frames_outer_approved_v2.json')); B=json.load(open('data/frames_outer_approved_v3.json')); M=json.load(open('data/p1a_marks_v1.json'))
x0,x1,z0,z1=430,575,90,125
fig,a=plt.subplots(figsize=(15,13)); a.imshow(warped((x0,x1),(z0,z1),0.06),cmap='gray',vmin=0,vmax=255,extent=(x0,x1,z0,z1),aspect='equal',alpha=.6)
for k,v in L.items(): v=np.array(v); a.plot(v[:,0],v[:,1],'-',color='tab:orange' if 'S' in k else 'k',lw=2)
for p in M: 
    if x0<p['X']<x1: a.plot(p['X'],p['Z'],'o',mfc='none',mec='g',ms=6)
for b in range(1,9):
    for nm,c in (('back','tab:blue'),('mid','k'),('front','tab:red')):
        v=B[str(b)][nm]; o=A[str(b)][nm]; C=np.array(v['curve']); zt=v['top'][1][1]; zo=(o['top'][1][1] if o.get('top') else C[-1,1])
        a.plot([v['X']]*2,[C[:,1].max()-8,zt],color=c,lw=1.3); a.plot([v['X']]*2,[zo,zt],color='m',lw=3)
    a.text(B[str(b)]['mid']['X'],B[str(b)]['mid']['top'][1][1]+.8,str(b),ha='center',fontsize=10,color='b')
a.set_xlim(x0,x1);a.set_ylim(z0,z1);a.grid(alpha=.3); a.set_title('bulwark lower line (orange, 10 segments) + bow frames 1-8 faces; magenta = added top length')
fig.savefig('qa/bulwark_bow_frames_v1.png',dpi=70,bbox_inches='tight')
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n): l=r3.Layer(); l.Name=n; return m.Layers.Add(l)
l1=lay('BULWARK_lower_line_Y0'); 
for k,v in L.items():
    pl=r3.PolylineCurve([r3.Point3d(x,0,z) for x,z in v]); at=r3.ObjectAttributes(); at.LayerIndex=l1; at.Name=k; m.Objects.AddCurve(pl,at)
l2=lay('FRAMES_1-8_outer_+Y_v3')
for b in range(1,9):
    for nm in ('back','mid','front'):
        v=B[str(b)][nm]; C=np.array(v['curve']); pts=[r3.Point3d(v['X'],y,z) for y,z in C]+[r3.Point3d(v['X'],y,z) for y,z in v['top'][1:]]
        at=r3.ObjectAttributes(); at.LayerIndex=l2; at.Name='F%02d_%s'%(b,nm); m.Objects.AddCurve(r3.PolylineCurve(pts),at)
m.Write('rhino/RoyalCaroline_bulwark_line_and_bow_tops_v1.3dm',7); print('ok')
