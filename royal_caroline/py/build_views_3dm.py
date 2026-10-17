# Calibrated plan views (body plan, sheer elevation, half-breadth plan) as picture planes + the builder's lines.dxf geometry + calibration points
import numpy as np, ezdxf, os, rhino3dm as r3
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
DXF='/root/.claude/uploads/9b1663d1-123c-5304-bded-1182034acdbc/e536660c-lines.dxf'
OUT='rhino/views_ref'; os.makedirs(OUT,exist_ok=True)
A=Image.open('plans/plan_1a_aligned.png').convert('L'); B=Image.open('plans/plan_1b_aligned.png').convert('L')
# image -> model fits
KX_E,X0_E,KZ_E,ZR_E=0.08511,-357.14,0.0850,2110.0      # elevation (plan_1a): X=KX*px+X0, Z=(ZR-row)*KZ
KX_P,X0_P,KY_P,YR_P=0.08499,-361.43,0.0833,1238.0       # half-breadth plan (plan_1b): Y=(YR-row)*KY
BP=dict(aft=(A,(1250,420,2390,2300),2385.0,2013.0,43.4/521.0), fwd=(B,(2433,500,3700,2150),2433.0,1903.0,8.65/103.3))
VIEWS={}
def save(im,box,name,ds):
    c=im.crop(box); c=c.resize((c.size[0]//ds,c.size[1]//ds),Image.LANCZOS); c.save(f'{OUT}/{name}.png',optimize=True)
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col=None,vis=True):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n
    if col: l.Color=col
    l.Visible=vis; LI[n]=f.Layers.Add(l); return LI[n]
def quad(name,lay,P0,P1,P2,P3,tex,umax,vmax):
    # P0 origin, P1 along u, P3 along v
    m=r3.Mesh()
    for p in (P0,P1,P2,P3): m.Vertices.Add(*p)
    m.Faces.AddFace(0,1,2,3); m.Normals.ComputeNormals()
    o=np.array(P0); u=np.array(P1)-o; v=np.array(P3)-o
    pl=r3.Plane(r3.Point3d(*o),r3.Vector3d(*(u/np.linalg.norm(u))),r3.Vector3d(*(v/np.linalg.norm(v))))
    tm=r3.TextureMapping.CreatePlaneMapping(pl,r3.Interval(0,np.linalg.norm(u)),r3.Interval(0,np.linalg.norm(v)),r3.Interval(-1,1))
    m.SetTextureCoordinates(tm,r3.Transform(1.0),False)
    mat=r3.Material(); mat.Name=name; mat.DiffuseColor=(255,255,255,255)
    cwd=os.getcwd(); os.chdir(OUT); mat.SetBitmapTexture(tex); os.chdir(cwd)
    mi=f.Materials.Add(mat); at=r3.ObjectAttributes(); at.LayerIndex=lay; at.MaterialIndex=mi
    at.MaterialSource=r3.ObjectMaterialSource.MaterialFromObject; at.Name=name; f.Objects.AddMesh(m,at)
# 1 body plan (plane X=-80, same as BODYPLAN_2D_as_drawn): u along -Y, v along +Z
XB=-80.05
for nm,(im,box,cx,zI,k) in BP.items():
    save(im,box,f'bodyplan_{nm}',2)
    x0,y0,x1,y1=box
    Yl=(cx-x0)*k; Yr=(cx-x1)*k; Zt=8.7+(zI-y0)*k; Zb=8.7+(zI-y1)*k
    quad(f'bodyplan_{nm}',layer('VIEW_bodyplan_image'),(XB,Yl,Zb),(XB,Yr,Zb),(XB,Yr,Zt),(XB,Yl,Zt),f'bodyplan_{nm}.png',Yl-Yr,Zt-Zb)
# 2 sheer elevation (plane Y=0 behind the half hull, i.e. Y=-0.05)
box=(3300,0,11372,2476); save(A,box,'elevation',2)
x0,y0,x1,y1=box; Xa=KX_E*x0+X0_E; Xb=KX_E*x1+X0_E; Zt=(ZR_E-y0)*KZ_E; Zb=(ZR_E-y1)*KZ_E
quad('elevation',layer('VIEW_elevation_image'),(Xa,-0.05,Zb),(Xb,-0.05,Zb),(Xb,-0.05,Zt),(Xa,-0.05,Zt),'elevation.png',Xb-Xa,Zt-Zb)
# 3 half-breadth plan (plane Z=-0.05)
box=(3650,0,11325,2485); save(B,box,'halfbreadth_plan',2)
x0,y0,x1,y1=box; Xa=KX_P*x0+X0_P; Xb=KX_P*x1+X0_P; Yt=(YR_P-y0)*KY_P; Yb=(YR_P-y1)*KY_P
quad('halfbreadth_plan',layer('VIEW_plan_image'),(Xa,Yb,-0.05),(Xb,Yb,-0.05),(Xb,Yt,-0.05),(Xa,Yt,-0.05),'halfbreadth_plan.png',Xb-Xa,Yt-Yb)
# lines from the dxf
cols={'STATIONS_3D_bodyplan':(220,0,0,255),'STATIONS_LOFT_uniform14':(0,0,0,255),'BODYPLAN_2D_as_drawn':(0,0,220,255),'GRID':(0,150,0,255),'WATERLINES_from_A1-4_plan':(230,120,0,255)}
d=ezdxf.readfile(DXF); n=0
for e in d.modelspace():
    if e.dxftype()!='LINE': continue
    ln=e.dxf.layer; vis=ln!='STATIONS_LOFT_uniform14'
    at=r3.ObjectAttributes(); at.LayerIndex=layer(ln,cols.get(ln),vis)
    f.Objects.AddLine(r3.Point3d(*e.dxf.start),r3.Point3d(*e.dxf.end),at); n+=1
# calibration points
st=[527.8,505.8]  # placeholder, replaced below
ST=np.load('data/hull_stations_all.npz'); Xs=sorted({round(float(ST[k][0,0]),1) for k in ST.keys() if k.startswith('ST')},reverse=True)
def pt(p,ln,nm):
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=nm; f.Objects.AddPoint(r3.Point3d(*p),a)
lE=layer('CAL_elevation_points',(200,0,200,255)); lP=layer('CAL_plan_points',(200,0,200,255)); lB=layer('CAL_bodyplan_points',(200,0,200,255))
WLZ=[0,8.7,17.4,26.1,34.8,43.4,52.1,69.5]
for X in Xs:
    for z in WLZ: pt((X,0,z),lE,f'E X{X} Z{z}')
    for y in (0,20,40,60,80): pt((X,y,0),lP,f'P X{X} Y{y}')
for y in (-60,-40,-20,0,20,40,60):
    for z in (8.7,17.4,26.1,34.8,43.4,52.1,69.5,100,140): pt((-80,y,z),lB,f'B Y{y} Z{z}')
f.Write(f'{OUT}/RoyalCaroline_views_ref.3dm',7); print('lines',n,'stations X',Xs)
