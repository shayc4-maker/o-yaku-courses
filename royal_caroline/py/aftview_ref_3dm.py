# Aft-view picture (the QA image) at an exact scale 10 px/mm, placed on the YZ plane at X=-1 in a Rhino file; curves drawn on it are read back directly from the 3dm
import sys,io,contextlib,numpy as np
with contextlib.redirect_stdout(io.StringIO()):
    sys.argv=['x']; sys.path.insert(0,'py'); import stern_frames_v4 as M
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy.interpolate import splev,splprep
import rhino3dm as r3, os
Y0,Y1,Z0,Z1=-65.0,65.0,10.0,145.0; S=10
fig=plt.figure(figsize=((Y1-Y0)*S/100,(Z1-Z0)*S/100),dpi=100); ax=fig.add_axes([0,0,1,1]); ax.set_xlim(Y0,Y1); ax.set_ylim(Z0,Z1); ax.axis('off')
for y in range(-60,61,10): ax.axvline(y,color='#d8d8d8',lw=.6); 
for z in range(20,141,10): ax.axhline(z,color='#d8d8d8',lw=.6)
for y in range(-60,61,10): ax.text(y,Z0+1.5,str(y),ha='center',fontsize=8,color='#888')
for z in range(20,141,10): ax.text(Y0+1,z+.5,str(z),fontsize=8,color='#888')
ax.axvline(0,color='k',lw=.8,ls='-.')
for z0,z1 in ((53.3,57.6),(61.5,65.5),(71.8,75.8)): ax.axhspan(z0,z1,color='orange',alpha=.3)
for kk in M.STX: ax.plot(M.D[kk][:,1],M.D[kk][:,2],'k:',lw=.9); ax.plot(-M.D[kk][:,1],M.D[kk][:,2],'k:',lw=.9)
col={26:'tab:blue',30:'tab:blue',15:'tab:green',19:'tab:green',4:'tab:red',8:'tab:red'}
for X in (30,26,19,15,8,4):
    O,I,tck=M.frame_profile(X); u=np.linspace(0,1,200); oy,oz=splev(u,tck); iy,iz=splev(u,splprep(I.T,k=3,s=0)[0])
    for sg in (1,-1): ax.plot(sg*oy,oz,col[X],lw=1.2); ax.plot(sg*iy,iz,col[X],lw=.6)
fig.savefig('rhino/aftview_frames46_48_10pxmm.png',dpi=100); print(plt.imread('rhino/aftview_frames46_48_10pxmm.png').shape)
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
l=r3.Layer(); l.Name='AFTVIEW_IMAGE'; li=f.Layers.Add(l)
m=r3.Mesh()
for y,z in ((Y1,Z0),(Y0,Z0),(Y0,Z1),(Y1,Z1)): m.Vertices.Add(-1.05,y,z)     # image x runs towards -Y (matches plotted left=+Y... see note)
m.Faces.AddFace(0,1,2,3); m.Normals.ComputeNormals()
pl=r3.Plane(r3.Point3d(-1.05,Y0,Z0),r3.Vector3d(0,1,0),r3.Vector3d(0,0,1))
m.SetTextureCoordinates(r3.TextureMapping.CreatePlaneMapping(pl,r3.Interval(0,Y1-Y0),r3.Interval(0,Z1-Z0),r3.Interval(-1,1)),r3.Transform(1.0),False)
mat=r3.Material(); mat.Name='aftview'; mat.DiffuseColor=(255,255,255,255); c=os.getcwd(); os.chdir('rhino'); mat.SetBitmapTexture('aftview_frames46_48_10pxmm.png'); os.chdir(c); mi=f.Materials.Add(mat)
a=r3.ObjectAttributes(); a.LayerIndex=li; a.MaterialIndex=mi; a.MaterialSource=r3.ObjectMaterialSource.MaterialFromObject; a.Name='aftview_image'; f.Objects.AddMesh(m,a)
lp=r3.Layer(); lp.Name='CALIBRATION_points'; lpi=f.Layers.Add(lp); ap=r3.ObjectAttributes(); ap.LayerIndex=lpi
for y in (-60,0,60):
    for z in (20,80,140): f.Objects.AddPoint(r3.Point3d(-1.0,y,z),ap)
lb=r3.Layer(); lb.Name='BUILD_HERE'; f.Layers.Add(lb)
f.Write('rhino/RoyalCaroline_aftview_frames46_48_REF.3dm',7); print('ok')
