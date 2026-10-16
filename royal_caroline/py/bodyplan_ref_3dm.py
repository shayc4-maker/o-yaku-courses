# Rhino reference file: body plan picture (YZ plane at X=-1) + frame 46-48 outer/inner splines, their control points, stations 16-18
import sys,io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import stern_frames_v4 as M
import rhino3dm as r3
from scipy.interpolate import splev,splprep
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
cx=2385.0; zI=2013.0; k=43.4/521.0; x0,y0,x1,y1=1250,420,3520,2380
Image.open('plans/plan_1a_aligned.png').convert('RGB').crop((x0,y0,x1,y1)).save('rhino/bodyplan_A1-2_aft.png')
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters; LI={}
def layer(n,col=None):
    if n in LI: return LI[n]
    l=r3.Layer(); l.Name=n
    if col: l.Color=col
    LI[n]=f.Layers.Add(l); return LI[n]
XP=-1.0
Yl=(cx-x0)*k; Yr=(cx-x1)*k; Zt=8.7+(zI-y0)*k; Zb=8.7+(zI-y1)*k
m=r3.Mesh()
for y,z in ((Yl,Zb),(Yr,Zb),(Yr,Zt),(Yl,Zt)): m.Vertices.Add(XP-0.05,y,z)
m.Faces.AddFace(0,1,2,3); m.Normals.ComputeNormals()
pl=r3.Plane(r3.Point3d(XP,Yl,Zb),r3.Vector3d(0,-1,0),r3.Vector3d(0,0,1))   # u along -Y (towards Yr), v along Z
tm=r3.TextureMapping.CreatePlaneMapping(pl,r3.Interval(0,Yl-Yr),r3.Interval(0,Zt-Zb),r3.Interval(-1,1))
m.SetTextureCoordinates(tm,r3.Transform(1.0),False)
mat=r3.Material(); mat.Name='bodyplan'; mat.DiffuseColor=(255,255,255,255); import os; _c=os.getcwd(); os.chdir('rhino'); print('tex',mat.SetBitmapTexture('bodyplan_A1-2_aft.png')); os.chdir(_c); mi=f.Materials.Add(mat)
at=r3.ObjectAttributes(); at.LayerIndex=layer('BODYPLAN_IMAGE'); at.MaterialIndex=mi; at.MaterialSource=r3.ObjectMaterialSource.MaterialFromObject; at.Name='bodyplan_image'
f.Objects.AddMesh(m,at)
cols={26:(0,0,255,255),30:(0,0,255,255),15:(0,150,0,255),19:(0,150,0,255),4:(255,0,0,255),8:(255,0,0,255)}
names={26:'F46_aft',30:'F46_fwd',15:'F47_aft',19:'F47_fwd',4:'F48_aft',8:'F48_fwd'}
def crv(pts,ln,nm):
    c=r3.Curve.CreateControlPointCurve([r3.Point3d(*p) for p in pts],3)
    a=r3.ObjectAttributes(); a.LayerIndex=ln; a.Name=nm; f.Objects.AddCurve(c,a)
for X in (30,26,19,15,8,4):
    O,I,tck=M.frame_profile(X); u=np.linspace(0,1,80)
    oy,oz=splev(u,tck); iy,iz=splev(u,splprep(I.T,k=3,s=0)[0])
    for sg in (1,-1):
        crv([(XP,sg*y,z) for y,z in zip(oy,oz)],layer(names[X]+'_outer',cols[X]),f'{names[X]}_outer_X{X}')
        crv([(XP,sg*y,z) for y,z in zip(iy,iz)],layer(names[X]+'_inner',cols[X]),f'{names[X]}_inner_X{X}')
    ap=r3.ObjectAttributes(); ap.LayerIndex=layer(names[X]+'_points',cols[X]); ap.Name=f'{names[X]}_pt'
    for y,z in O: f.Objects.AddPoint(r3.Point3d(XP,y,z),ap)
for kk in M.STX:
    crv([(XP,y,z) for y,z in M.D[kk][::25,1:]],layer('STATIONS_16_17_18',(0,0,0,255)),kk)
f.Write('rhino/RoyalCaroline_bodyplan_with_frames46_48_REF.3dm',7); print('ok',len(f.Objects))
