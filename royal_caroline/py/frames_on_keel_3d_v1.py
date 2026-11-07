# frames 1-5 blanks on the keel (deadwood with pockets) and keelson, 3D, for the builder to judge the seat width vs the slope; keel/keelson from build3d_v2 (STEP outlines + 1 mm pockets), clipped to X>=430
import sys,os,json,numpy as np
sys.argv=['x']; sys.path.insert(0,'py')
src=open('py/build3d_v2.py').read().split("# ---------- frames")[0]
exec(src)
import rhino3dm as r3
from shapely.geometry import box
XC=430.0
for nm,pg in (('KEELSON',keelson),('KEEL_DEADWOOD',keel)):
    g=pg.intersection(box(XC,-50,545,300)); geoms=g.geoms if hasattr(g,'geoms') else [g]; V=[];T=[]
    for q in geoms:
        if q.geom_type!='Polygon' or q.area<5: continue
        v,t=mesh_of(prism(q,-2.65,2.65)); T.extend((t+len(V)).tolist()); V.extend(v.tolist())
    parts[nm]=dict(v=np.array(V),t=np.array(T)); print(nm,len(V),'verts')
N=r3.File3dm.Read('rhino/RoyalCaroline_frames_1_2_3_4_5_blanks_v1.3dm'); f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
for i,l in enumerate(N.Layers): n=r3.Layer(); n.Name=l.Name; n.Color=l.Color; LI[i]=f.Layers.Add(n)
for o in N.Objects: a=o.Attributes; a.LayerIndex=LI[a.LayerIndex]; f.Objects.Add(o.Geometry,a)
for nm,col in (('KEELSON',(150,110,60,255)),('KEEL_DEADWOOD',(110,80,50,255))):
    l=r3.Layer(); l.Name=nm; l.Color=col; li=f.Layers.Add(l); m=r3.Mesh()
    for v in parts[nm]['v']: m.Vertices.Add(*v)
    for t in parts[nm]['t']: m.Faces.AddFace(*t)
    m.Normals.ComputeNormals(); a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=nm; f.Objects.AddMesh(m,a)
B=json.load(open('data/bow_lines_builder_final_v1.json')); l=r3.Layer(); l.Name='RABBET_final'; l.Color=(0,0,0,255); li=f.Layers.Add(l)
a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name='rabbet'; f.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(*p) for p in B['RABBET_final_to_M48']]),a)
f.Write('rhino/RoyalCaroline_frames1-5_on_keel_v1.3dm',7); print('objects',len(f.Objects))
