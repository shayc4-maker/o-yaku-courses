# ref_final.dxf -> seats completed: per frame two full verticals from keel seat floor to keelson notch top,
# old vertical stubs replaced, keelson-underside curve (03) trimmed inside each seat pocket.
import sys,json,math
import ezdxf, numpy as np
src,dst=sys.argv[1],sys.argv[2]
d=ezdxf.readfile(src); m=d.modelspace()
seats=json.load(open('data/backbone_contour_v5.json'))['seats']
TOL=.06
def hlines(layers,a,b):
    r=[]
    for e in m:
        if e.dxftype()=='LINE' and e.dxf.layer in layers:
            p,q=e.dxf.start,e.dxf.end
            if abs(p.z-q.z)<1e-3 and abs(min(p.x,q.x)-a)<.15 and abs(max(p.x,q.x)-b)<.15: r.append(p.z)
    return r
if not d.layers.has_entry('10_FRAME_SEATS'): d.layers.add('10_FRAME_SEATS',color=1)
rep=[]; delete=[]
for i,(a,b,z,dp) in enumerate(seats):
    cand=[v for v in hlines(('01_BODY_OUTER','02_KEELSON','03_STERN_KNEE'),a,b) if v>z+3]
    src_l='02/03'
    if not cand: cand=[v for v in hlines(('98_JOINED_REVIEW_CURVES',),a,b) if v>z+3]; src_l='98'
    zu=max(cand); 
    for x in (a,b):
        for e in m:
            if e.dxftype()=='LINE' and e.dxf.layer in('01_BODY_OUTER','02_KEELSON','03_STERN_KNEE'):
                p,q=e.dxf.start,e.dxf.end
                if abs(p.x-q.x)<1e-3 and abs(p.x-x)<TOL and min(p.z,q.z)>=z-0.2 and max(p.z,q.z)<=zu+0.2: delete.append(e)
        m.add_line((x,0,z),(x,0,zu),dxfattribs={'layer':'10_FRAME_SEATS'})
    for zz in (z,zu): m.add_line((a,0,zz),(b,0,zz),dxfattribs={'layer':'10_FRAME_SEATS'})
    rep.append((i,round(a,2),round(b,2),round(z,2),round(zu,2),src_l))
for e in set(map(id,delete)) and {id(e):e for e in delete}.values():
    try: m.delete_entity(e)
    except Exception: pass
# trim keelson underside curve (03) inside pockets
def sample(e):
    if e.dxftype()=='SPLINE':
        pts=np.array([(p.x,p.z) for p in e.flattening(0.01)])
    else: pts=np.array([(v.dxf.location.x,v.dxf.location.z) for v in e.vertices])
    return pts
trimmed=0
for e in list(m.query('SPLINE POLYLINE')):
    if e.dxf.layer!='03_STERN_KNEE': continue
    pts=sample(e)
    if len(pts)<2 or pts[:,0].min()<30: 
        pass
    o=pts[np.argsort(pts[:,0])] if e.dxftype()=='SPLINE' else pts
    lo,hi=o[:,0].min(),o[:,0].max()
    ints=[(a,b) for a,b,*_ in seats if a<hi-TOL and b>lo+TOL and lo>=36.0]
    if not ints: continue
    xs=np.linspace(lo,hi,max(int((hi-lo)/0.4),20)); zs=np.interp(xs,o[:,0],o[:,1])
    xs=np.unique(np.r_[xs,[v for ab in ints for v in ab if lo<v<hi]]); zs=np.interp(xs,o[:,0],o[:,1])
    keep=np.ones(len(xs),bool)
    for a,b in ints: keep&=~((xs>a+1e-6)&(xs<b-1e-6))
    runs=[];cur=[]
    for k,(x,z_) in enumerate(zip(xs,zs)):
        if keep[k]: cur.append((x,z_))
        else:
            if len(cur)>1: runs.append(cur)
            cur=[]
    if len(cur)>1: runs.append(cur)
    lay=e.dxf.layer; m.delete_entity(e); trimmed+=1
    for r in runs:
        m.add_spline(fit_points=[(x,0,z_) for x,z_ in r],dxfattribs={'layer':lay}) if len(r)>=4 else m.add_polyline3d([(x,0,z_) for x,z_ in r],dxfattribs={'layer':lay})
d.saveas(dst)
json.dump(rep,open('data/seat_fix_report.json','w'))
print('deleted stubs',len(delete),'trimmed 03 curves',trimmed)
print([r for r in rep if r[5]=='98'])
