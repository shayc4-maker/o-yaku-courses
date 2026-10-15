import sys,json,csv,numpy as np, rhino3dm as r3, ezdxf
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
S=sys.argv[1]; O=S+'/out'; PK=O+'/RoyalCaroline_Rhino'
d=json.load(open(O+'/frame_parts.json')); parts=d['parts']; SID=d['SIDED']
meta=json.load(open(O+'/meta.json')); WLZ=meta['WLZ_mm']
fx=json.load(open(O+'/frames_X.json'))['X_mm']
# ---------- 3dm v2 (start from v1)
m=r3.File3dm.Read(PK+'/RoyalCaroline_lines_1to48_v1.3dm')
def layer(name,col):
    L=r3.Layer(); L.Name=name; L.Color=(*col,255); return m.Layers.Add(L)
LA=layer('FRAMES_timber_A_aft',(170,110,40)); LF=layer('FRAMES_timber_F_fore',(210,160,80)); LX=layer('FRAME_POSITIONS',(0,120,0))
def attr(li,n):
    a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=n; return a
for p in parts:
    P=orient(Polygon(p['poly']),1.0); co=np.array(P.exterior.coords)
    crv=r3.PolylineCurve([r3.Point3d(p['x0'],float(y),float(z)) for y,z in co])
    e=r3.Extrusion.Create(crv,p['x1']-p['x0'],True)
    m.Objects.AddExtrusion(e,attr(LA if p['layer']=='A' else LF,f"F{p['frame']:02d}{p['layer']}"))
for i,x in enumerate(fx,1):
    m.Objects.AddLine(r3.Point3d(x,0,-10),r3.Point3d(x,0,-3),attr(LX,f'frame_{i}_centre'))
    m.Objects.AddTextDot(str(i),r3.Point3d(x,0,-14),attr(LX,f'F{i}'))
bb=json.load(open(O+'/backbone.json')); BW=bb['params']['SIDED_BB']/2
LB=layer('BACKBONE',(90,90,160))
for k,polys in bb['pieces'].items():
    for poly in polys:
        P=orient(Polygon(poly),1.0); co=np.array(P.exterior.coords)
        crv=r3.PolylineCurve([r3.Point3d(float(x),-BW,float(z)) for x,z in co])
        e=r3.Extrusion.Create(crv,2*BW,True)
        g=e.GetBoundingBox()
        if g.Max.Y<0.1:
            crv=r3.PolylineCurve([r3.Point3d(float(x),-BW,float(z)) for x,z in co[::-1]]); e=r3.Extrusion.Create(crv,2*BW,True); g=e.GetBoundingBox()
        print(k,'Y',round(g.Min.Y,2),round(g.Max.Y,2))
        m.Objects.AddExtrusion(e,attr(LB,k))
m.Write(PK+'/RoyalCaroline_hull_1to48_v3.3dm',8)
# backbone DXF
db=ezdxf.new('R2010',setup=True); db.units=ezdxf.units.MM; mb=db.modelspace()
for n,c in (('CUT',1),('ENGRAVE',5),('INFO',8)): db.layers.add(n,color=c)
oy=0
for k,polys in bb['pieces'].items():
    for poly in polys:
        P=np.array(poly); minx,minz=P.min(0); maxx,maxz=P.max(0)
        mb.add_lwpolyline([(x-minx+10,z-minz+oy) for x,z in P],close=True,dxfattribs={'layer':'CUT'})
        mb.add_text(f"{k}  sided {2*BW:.1f} mm  (X {minx:.1f}..{maxx:.1f})",height=3,dxfattribs={'layer':'INFO'}).set_placement((10,oy-6))
        # engrave frame centre marks on pieces carrying frame notches
        for i,x in enumerate(fx,1):
            if minx<x<maxx and k!='STERNPOST':
                zs=[z for (xx,z) in P if abs(xx-x)<SID+0.3]
                if zs and k!='KEELSON':
                    zt=max(zs); mb.add_line((x-minx+10,zt-minz+oy-0.2),(x-minx+10,zt-minz+oy-2.2),dxfattribs={'layer':'ENGRAVE'})
                if k=='KEELSON':
                    zb=min(z for (xx,z) in P if abs(xx-x)<SID+0.3); mb.add_line((x-minx+10,zb-minz+oy+0.2),(x-minx+10,zb-minz+oy+2.2),dxfattribs={'layer':'ENGRAVE'})
        oy+=(maxz-minz)+25
db.saveas(PK+'/RoyalCaroline_backbone_cut_1to48_v3.dxf')
# ---------- DXF cut sheet
doc=ezdxf.new('R2010',setup=True); doc.units=ezdxf.units.MM; msp=doc.modelspace()
for n,c in (('CUT',1),('ENGRAVE',5),('INFO',8),('KEEL_STRIP',3)): doc.layers.add(n,color=c)
COLS=6; DX=170; DY=150; WLmarks=['II','IV','VI']
for k,p in enumerate(parts):
    r,c=divmod(k,COLS); ox=c*DX+85; oy=-r*DY-20
    P=np.array(p['poly']); zr=p['zr']
    msp.add_lwpolyline([(ox+y,oy+z) for y,z in P],close=True,dxfattribs={'layer':'CUT'})
    for h in p['holes']: msp.add_lwpolyline([(ox+y,oy+z) for y,z in h],close=True,dxfattribs={'layer':'CUT'})
    # centreline tick on the floor and WL ticks on both arms (engrave, 2 mm)
    pol=Polygon(p['poly'])
    msp.add_line((ox,oy+zr+0.3),(ox,oy+zr+2.3),dxfattribs={'layer':'ENGRAVE'})
    for w in WLmarks:
        z=WLZ[w]
        if z<zr+6 or z>p['ztop']-3: continue
        xs=[x for x in np.linspace(0,90,1801) if pol.contains(Polygon([(x-.01,z-.01),(x+.01,z-.01),(x+.01,z+.01)]))]
        if xs:
            xo=max(xs)
            for sg in (1,-1): msp.add_line((ox+sg*(xo-2.0),oy+z),(ox+sg*xo,oy+z),dxfattribs={'layer':'ENGRAVE'})
    msp.add_text(f"F{p['frame']:02d}{p['layer']}",height=3.5,dxfattribs={'layer':'ENGRAVE'}).set_placement((ox,oy+zr+8),align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text(f"F{p['frame']:02d}-{p['layer']}  X {p['x0']:.2f}-{p['x1']:.2f}  sided {SID} mm",height=2.2,dxfattribs={'layer':'INFO'}).set_placement((ox,oy-6),align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
# keel marking strip: X from station 18 (heel), ticks at each timber face, 1:1
ky=-(len(parts)//COLS+1)*DY-60
L=560; msp.add_lwpolyline([(0,ky),(L,ky),(L,ky+12),(0,ky+12)],close=True,dxfattribs={'layer':'KEEL_STRIP'})
msp.add_text('KEEL MARKING STRIP 1:1 - X=0 at station 18 / heel of sternpost - ticks = timber faces, long tick = frame centre',height=3,dxfattribs={'layer':'KEEL_STRIP'}).set_placement((0,ky+16))
for i,x in enumerate(fx,1):
    msp.add_line((x,ky),(x,ky+12),dxfattribs={'layer':'KEEL_STRIP'})
    for xx in (x-SID,x+SID): msp.add_line((xx,ky),(xx,ky+6),dxfattribs={'layer':'KEEL_STRIP'})
    msp.add_text(str(i),height=2.5,dxfattribs={'layer':'KEEL_STRIP'}).set_placement((x,ky-4),align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
from_meta=json.load(open(O+'/meta.json'))['STX']
for s,x in from_meta.items():
    msp.add_line((x,ky+12),(x,ky+20),dxfattribs={'layer':'INFO'})
    msp.add_text('st'+s,height=2,dxfattribs={'layer':'INFO'}).set_placement((x,ky+22),align=ezdxf.enums.TextEntityAlignment.MIDDLE_CENTER)
doc.saveas(PK+'/RoyalCaroline_frames_cut_1to48_v3.dxf')
# ---------- table
with open(PK+'/frames_table_1to48.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['frame','X_centre_mm','X_centre_real_m','aft_timber_X','fore_timber_X','heel_Z_mm','top_Z_mm','max_width_mm','source'])
    for i,x in enumerate(fx,1):
        pa=[p for p in parts if p['frame']==i]
        w.writerow([i,round(x,2),round(x*48/1000,3),f"{x-SID:.2f}-{x:.2f}",f"{x:.2f}-{x+SID:.2f}",round(min(p['zr'] for p in pa),2),round(max(p['ztop'] for p in pa),2),round(max(p['bbox'][2]-p['bbox'][0] for p in pa),2),'plan_5 (A3/3) frame drawn; X via heel/stem homologous points'])
print('ok', len(parts),'parts')
