# continue the RABBET up the stem: points for approval on the heavy aft line of the stem in the recalibrated sheer plan (model X,Z); the points are located by the ink run centre nearest to a coarse prediction (plane-1 points / STEP stem aft face) at chosen Z levels; no splines
import sys,json,numpy as np
sys.path.insert(0,'py')
exec(open('py/rabbet_stem_view.py').read().split("A=json.load")[0])
PL=json.load(open('data/bow_plank_splines_v1.json'))['0']['points']
pred=lambda z: float(np.interp(z,[27.46,34.8,43.4,52.1,69.5,84.0,100.0],[528.03,534.5,541.2,547.4,551.5,554.6,555.5]))
xl,zl=(500,620),(20,125); res=0.04; nx=int((xl[1]-xl[0])/res); nz=int((zl[1]-zl[0])/res)
Xg=xl[0]+(np.arange(nx)+.5)*res; Zg=zl[1]-(np.arange(nz)+.5)*res; XX,ZZ=np.meshgrid(Xg,Zg); xi,zi=ink(XX,ZZ); IMG=map_coordinates(im,[ZR-zi/KZ,(xi-X0)/KX],order=1,cval=255)<120
rows=[]
for z in (30,36,42,48,54,60,66,72,78,84,90,96):
    r=int((zl[1]-z)/res); band=IMG[r-3:r+4,:].any(axis=0); p=pred(z); lo=int((p-9-xl[0])/res); hi=int((p+9-xl[0])/res); idx=np.where(band[lo:hi])[0]+lo
    if len(idx)==0: rows.append(dict(Z=z,X=None,pred=round(p,1),runs=[])); continue
    g=np.split(idx,np.where(np.diff(idx)>1)[0]+1); runs=[(round(float(xl[0]+(a[0]+a[-1])/2*res),2),round(len(a)*res,2)) for a in g]
    thick=[q for q in runs if q[1]>=0.35] or runs; best=min(thick,key=lambda q:abs(q[0]-p)); rows.append(dict(Z=z,X=best[0],width=best[1],pred=round(p,1),runs=runs))
# above Z=70 the stem line merges with the head rails (several heavy lines cross): points taken as the continuation line through the thin run / heavy run that continues R7 smoothly (checked on the picture); uncertain
FIX={72:555.8,78:557.4,84:557.9,90:559.9,96:560.0}
for r in rows:
    if r['Z'] in FIX: r['X']=FIX[r['Z']]; r['note']='continuation of the stem line in the crowded head zone (uncertain)'
for r in rows: print(r)
json.dump(rows,open('data/rabbet_stem_points_v1.json','w'),indent=1)
fig,ax=plt.subplots(figsize=(14,16)); ax.imshow(warped(xl,zl),extent=(xl[0],xl[1],zl[0],zl[1]),cmap='gray',vmin=0,vmax=255,aspect='equal',alpha=.75)
for i,r in enumerate(rows):
    if r['X'] is not None: ax.plot(r['X'],r['Z'],'+',color='red',ms=14,mew=1.8); ax.text(r['X']+1.2,r['Z']+.8,'R%d (%.1f, %d)'%(i+1,r['X'],r['Z']),color='red',fontsize=9)
ax.plot([p[1] for p in PL],[p[2] for p in PL],'m+',ms=9); ax.set_xlim(*xl); ax.set_ylim(*zl); ax.grid(alpha=.25); ax.set_title('rabbet continued up the stem: points R1-R12 for approval (red); magenta = plane-1 points')
fig.savefig('qa/rabbet_stem_points_v1.png',dpi=55,bbox_inches='tight')
