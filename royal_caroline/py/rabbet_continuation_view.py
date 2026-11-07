# side view after the builder's edit: lower ends of the approved faces (frames 1-10) on the recalibrated keel plan + continuation points R1-R12 of the rabbet up the stem from the foremost end (frame 1 front face)
import sys,json,numpy as np
sys.path.insert(0,'py')
exec(open('py/rabbet_stem_view.py').read().split("A=json.load")[0])
BB=json.load(open('data/step44_profiles.json')); A=json.load(open('data/frames_outer_approved_v2.json')); R=json.load(open('data/rabbet_stem_points_v2.json'))
ends=sorted([(A[str(b)][nm]['X'],A[str(b)][nm]['end'][1],b,nm) for b in range(1,11) for nm in ('back','mid','front')])
seq=[(e[0],e[1]) for e in ends]+[(r['X'],r['Z']) for r in R[:7]]
sl=[(seq[i+1][1]-seq[i][1])/(seq[i+1][0]-seq[i][0]) for i in range(len(seq)-1)]
print('slope dZ/dX along the lower ends and the stem points (last 14 segments):',[round(s,2) for s in sl[-14:]])
fig,axs=plt.subplots(2,1,figsize=(18,22),gridspec_kw={'height_ratios':[1,1.25]})
for a,(xl,zl) in zip(axs,(((400,545),(-4,50)),((505,590),(14,112)))):
    a.imshow(warped(xl,zl),extent=(xl[0],xl[1],zl[0],zl[1]),cmap='gray',vmin=0,vmax=255,aspect='equal',alpha=.7)
    for k,v in BB.items():
        pg=Polygon(max(v,key=lambda q:Polygon(q).area))
        if pg.bounds[2]>400: a.plot(*pg.exterior.xy,color='gray',lw=.7)
    cols={'back':'tab:blue','mid':'k','front':'tab:red'}
    a.plot([e[0] for e in ends],[e[1] for e in ends],'-',color='orange',lw=.8,label='through the lower ends of the approved faces (polyline, not a spline)')
    for X,Z,b,nm in ends:
        a.plot(X,Z,'o',color=cols[nm],ms=5)
        if nm=='mid' and b<=10: a.text(X,Z-2.6,str(b),fontsize=8,ha='center',clip_on=True)
    for i,r in enumerate(R):
        c='red' if i<7 else ('darkorange' if r['id']!='E' else 'blue'); a.plot(r['X'],r['Z'],'+',color=c,ms=14,mew=2); a.text(r['X']+1.2,r['Z']+.6,r['id'],color=c,fontsize=10,clip_on=True)
    a.set_xlim(*xl); a.set_ylim(*zl); a.grid(alpha=.25)
axs[0].legend(fontsize=8,loc='upper left'); axs[0].set_title('after the builder edit: lower ends of the approved faces (blue back, black mid, red front; frame numbers below the mid face) on the keel plan')
axs[1].set_title('continuation of the rabbet up the stem: R1-R7 (red), R10 (orange), E = end of the ship on the lower bulwark line at the light vertical line (blue)')
fig.savefig('qa/rabbet_continuation_v3.png',dpi=55,bbox_inches='tight')
