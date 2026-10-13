import sys,json,csv,numpy as np, rhino3dm as r3, ezdxf
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
S=sys.argv[1]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
fp=json.load(open(O+'/frame_pieces_v9.json'))['pieces']; parts=json.load(open(O+'/parts_v9.json'))
fx=json.load(open(O+'/frames_X.json'))['X_mm']
m=r3.File3dm.Read(PK+'/RoyalCaroline_lines_1to48_v1.3dm')
def layer(name,col):
    L=r3.Layer(); L.Name=name; L.Color=(*col,255); return m.Layers.Add(L)
COL={'cant':(200,150,40),'hawse':(160,120,30),'topU':(150,110,190),'floor':(70,110,170),'fut1':(230,140,60),'fut2':(80,160,80),'fut3':(200,70,70),'top':(150,110,190)}
LYR={k:layer('FRAMES_'+k,c) for k,c in COL.items()}
LB=layer('BACKBONE',(90,90,160)); LS=layer('STERN',(160,100,60)); LR=layer('RUDDER',(120,60,60)); LP=layer('PORTS_sills_lintels',(200,60,60)); LC=layer('CLAMPS',(60,140,140)); LJ=layer('JIG',(170,170,170)); LD=layer('DECKS',(150,120,80)); LW=layer('BULWARK_cap_rail',(120,80,40)); LK=layer('KNEES',(180,90,30)); LPl=layer('PILLARS',(90,60,30)); LX=layer('FRAME_POSITIONS',(0,120,0))
def attr(li,n):
    a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=n; return a
def to3(plane,off,th,u,v):
    if plane=='YZ': return r3.Point3d(off,u,v)
    if plane=='XZ': return r3.Point3d(u,off-th/2,v)
    return r3.Point3d(u,v,off)
def extr(plane,off,th,poly,holes=()):
    P=orient(Polygon(poly),1.0); co=np.array(P.exterior.coords)
    for flip in (False,True):
        c=co[::-1] if flip else co
        e=r3.Extrusion.Create(r3.PolylineCurve([to3(plane,off,th,u,v) for u,v in c]),th,True)
        g=e.GetBoundingBox(); ax={'YZ':(g.Min.X,off),'XZ':(g.Min.Y,off-th/2),'XY':(g.Min.Z,off)}[plane]
        if abs(ax[0]-ax[1])<0.05: break
    for h in holes:
        hc=np.array(h); e.AddInnerProfile(r3.PolylineCurve([to3(plane,off,th,u,v) for u,v in hc]))
    return e
for p in fp:
    nm=f"F{p['frame']:02d}{p['layer']}-{p['piece']}-{p['side']}"
    m.Objects.AddExtrusion(extr('YZ',p['x0'],p['x1']-p['x0'],p['poly']),attr(LYR[p['piece']],nm))
for p in parts:
    li={'backbone':LB,'stern':LS,'rudder':LR,'ports':LP,'clamps':LC,'jig':LJ,'decks':LD,'bulwark':LW,'knees':LK,'pillars':LPl}[p['group']]
    m.Objects.AddExtrusion(extr(p['plane'],p['off'],p['th'],p['poly'],p.get('holes',[])),attr(li,p['name']))
for i,x in enumerate(fx,1):
    m.Objects.AddTextDot(str(i),r3.Point3d(x,0,-14),attr(LX,f'F{i}'))
m.Write(PK+'/RoyalCaroline_hull_1to48_v8.3dm',8)
# -------- DXF: frame pieces (shelf packing, 1 row-group per frame)
def newdoc():
    d=ezdxf.new('R2010',setup=True); d.units=ezdxf.units.MM
    for n,c in (('CUT',1),('ENGRAVE',5),('INFO',8),('KEEL_STRIP',3)): d.layers.add(n,color=c)
    return d
A=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER
doc=newdoc(); ms=doc.modelspace(); W=600; x=0; y=0; rowh=0
for f in sorted(set(p['frame'] for p in fp)):
    ps=[p for p in fp if p['frame']==f]
    for p in ps:
        P=np.array(p['poly']); P=P-P.min(0); w,h=P.max(0)
        if x+w>W: x=0; y-=rowh+8; rowh=0
        ms.add_lwpolyline([(x+u,y-h+v) for u,v in P],close=True,dxfattribs={'layer':'CUT'})
        c=Polygon(P).representative_point()
        ms.add_text(f"{f}{p['layer']}{p['piece'][0].upper()}{p['piece'][-1] if p['piece'][-1].isdigit() else ''}{p['side']}",height=1.6,dxfattribs={'layer':'ENGRAVE'}).set_placement((x+c.x,y-h+c.y),align=A)
        if 'tab' in p:
            P0=np.array(p['poly']).min(0); yc=p['tab']['y']-P0[0]; zc=p['tab']['z_cut']-P0[1]
            ms.add_line((x+yc-2.5,y-h+zc),(x+yc+2.5,y-h+zc),dxfattribs={'layer':'ENGRAVE'})
        x+=w+4; rowh=max(rowh,h)
    x=0; y-=rowh+12; rowh=0
ky=y-30; ms.add_lwpolyline([(0,ky),(560,ky),(560,ky+12),(0,ky+12)],close=True,dxfattribs={'layer':'KEEL_STRIP'})
for i,xx in enumerate(fx,1):
    ms.add_line((xx,ky),(xx,ky+12),dxfattribs={'layer':'KEEL_STRIP'})
    for q in (xx-4,xx+4): ms.add_line((q,ky),(q,ky+6),dxfattribs={'layer':'KEEL_STRIP'})
    ms.add_text(str(i),height=2.5,dxfattribs={'layer':'KEEL_STRIP'}).set_placement((xx,ky-4),align=A)
ms.add_text('KEEL MARKING STRIP 1:1, X=0 = station 18 / heel. Labels: frame + A/F + piece (F=floor,F1/F2/F3=futtocks,T=top) + side',height=3,dxfattribs={'layer':'KEEL_STRIP'}).set_placement((0,ky+16))
doc.saveas(PK+'/RoyalCaroline_frames_pieces_cut_1to48_v8.dxf')
# -------- DXF: backbone, stern, rudder (grouped by thickness)
doc=newdoc(); ms=doc.modelspace(); y=0
for th in sorted(set(round(p['th'],1) for p in parts)):
    ms.add_text(f'=== stock thickness {th} mm ===',height=4,dxfattribs={'layer':'INFO'}).set_placement((0,y)); y-=10; x=0; rowh=0
    for p in [q for q in parts if round(q['th'],1)==th]:
        P=np.array(p['poly']); mn=P.min(0); P=P-mn; w,h=P.max(0)
        if x+w>W: x=0; y-=rowh+12; rowh=0
        ms.add_lwpolyline([(x+u,y-h+v) for u,v in P],close=True,dxfattribs={'layer':'CUT'})
        for hh in p.get('holes',[]): 
            H=np.array(hh)-mn; ms.add_lwpolyline([(x+u,y-h+v) for u,v in H],close=True,dxfattribs={'layer':'CUT'})
        if 'PLANK' in p['name']:
            from shapely.geometry import LineString
            PP=Polygon(np.array(p['poly'])-mn,[np.array(hh)-mn for hh in p.get('holes',[])])
            y0=-mn[1]
            for kk in range(-40,41):
                yy=y0+kk*5.2
                if kk==0: continue
                seg=PP.intersection(LineString([(-1,yy),(w+1,yy)]))
                for sgm in getattr(seg,'geoms',[seg]):
                    if sgm.is_empty or sgm.geom_type!='LineString': continue
                    (a0,b0),(a1,b1)=sgm.coords[0],sgm.coords[-1]
                    ms.add_line((x+a0,y-h+b0),(x+a1,y-h+b1),dxfattribs={'layer':'ENGRAVE'})
        ms.add_text(p['name'],height=2.2,dxfattribs={'layer':'INFO'}).set_placement((x+w/2,y-h-3),align=A)
        x+=w+8; rowh=max(rowh,h+5)
    y-=rowh+20
doc.saveas(PK+'/RoyalCaroline_backbone_stern_rudder_cut_1to48_v8.dxf')
# -------- parts list
with open(PK+'/parts_list_v8.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['part','group','plane','offset_mm','stock_thickness_mm','size_mm','note'])
    for p in parts:
        P=np.array(p['poly']); w.writerow([p['name'],p['group'],p['plane'],round(p['off'],2),round(p['th'],2),'%.1f x %.1f'%tuple(np.ptp(P,axis=0)),p['note']])
    for p in fp:
        P=np.array(p['poly']); w.writerow([f"F{p['frame']:02d}{p['layer']}-{p['piece']}-{p['side']}",'frame','YZ',round(p['x0'],2),round(p['x1']-p['x0'],2),'%.1f x %.1f'%tuple(np.ptp(P,axis=0)),''])
print('exported',len(fp)+len(parts))
