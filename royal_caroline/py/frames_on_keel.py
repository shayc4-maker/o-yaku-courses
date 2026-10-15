# Reference file: 45 frames (v10 pieces) on the builder's new backbone (STEP 44 profiles, thickness from the plan scale)
import json,numpy as np,rhino3dm as r3
from shapely.geometry import Polygon
TH=5.3
BB=json.load(open('data/step44_profiles.json'))
P=json.load(open('data/frame_pieces_v10.json'))['pieces']
fx=json.load(open('data/frames_X.json'))['X_mm']; seats=json.load(open('data/seat_fix_report.json'))
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def layer(name,rgb):
    l=r3.Layer(); l.Name=name; l.Color=rgb+(255,); return f.Layers.Add(l)
def add(brep_or_curve,idx,name):
    at=r3.ObjectAttributes(); at.LayerIndex=idx; at.Name=name
    if isinstance(brep_or_curve,r3.Brep): f.Objects.AddBrep(brep_or_curve,at)
    else: f.Objects.AddCurve(brep_or_curve,at)
def solid(pts3,axis_len,shift_to):
    pl=r3.Polyline(len(pts3))
    for p in pts3: pl.Add(*p)
    cv=pl.ToPolylineCurve(); ex=r3.Extrusion.Create(cv,axis_len,True)
    if ex is None: return None
    br=ex.ToBrep(True)
    if br is None or not br.IsSolid: return None
    bb=br.GetBoundingBox(); return br,bb
bad=[]
ib=layer('BACKBONE_builder',(150,110,70))
for n,(k,rings) in enumerate(BB.items()):
    out=max(rings,key=lambda p:Polygon(p).area)
    pg=Polygon(out).buffer(0).simplify(0.002); out=list(pg.exterior.coords)
    r=solid([(x,TH/2,z) for x,z in out],TH,None)
    if r is None: bad.append(('bb',k)); continue
    br,bb=r; br.Translate(r3.Vector3d(0,-TH/2-bb.Min.Y,0)); add(br,ib,k)
    if len(rings)>1: bad.append(('holes',k))
rows=[]
for fr in range(1,46):
    il=layer('FRAME_%02d'%fr,(60,120+ (fr%5)*20,200-(fr%7)*15))
    ps=[p for p in P if p['frame']==fr]
    for p in ps:
        pts=[(p['x0'],y,z) for y,z in p['poly']]
        if pts[0]!=pts[-1]: pts.append(pts[0])
        r=solid(pts,4.0,None)
        nm='%s_%s_%s'%(p['layer'],p['piece'],p['side'])
        if r is None: bad.append(('frame',fr,nm)); continue
        br,bb=r; br.Translate(r3.Vector3d(p['x0']-bb.Min.X,0,0)); add(br,il,nm)
    fl=[p for p in ps if p['piece']=='floor'][0]
    zmin=min(z for y,z in fl['poly']); a,b,sz,zu,_=seats[fr-1][1:6]
    rows.append((fr,round(fl['x0']+4,2),round((a+b)/2,2),round(fl['x0']+4-(a+b)/2,2),round(zmin,2),round(sz,2),round(zmin-sz,2)))
f.Write('rhino/RoyalCaroline_frames45_on_new_keel_REF.3dm',7)
json.dump(rows,open('data/frames_vs_seats_v1.json','w'))
print('bad',bad); print(len(f.Objects),'objects')
print('fr, frameX, seatCtr, dX, floorZmin, seatZ, dZ'); 
for r_ in rows[:3]+rows[20:23]+rows[-3:]: print(r_)
d=np.array([r_[3] for r_ in rows]);dz=np.array([r_[6] for r_ in rows]);print('dX max',abs(d).max(),'dZ range',dz.min(),dz.max())
