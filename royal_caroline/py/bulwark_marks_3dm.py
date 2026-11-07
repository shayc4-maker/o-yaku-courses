# file for the builder: plan_1a side view (calibrated, picture plane at Y=-0.05) + his points M0-M48 + NURBS through them per segment (interpolating) to be arranged by him
import sys,os,json,numpy as np,zipfile; sys.path.insert(0,'py')
import rhino3dm as r3
from PIL import Image
from scipy.interpolate import splprep
from p1a_strip import warped
OUT='rhino/bulwark_ref'; os.makedirs(OUT,exist_ok=True)
x0,x1,z0,z1=-40,575,-5,145
W=warped((x0,x1),(z0,z1),0.1); Image.fromarray(W.astype(np.uint8)).save(OUT+'/plan_1a_side.png',optimize=True)
P={p['id']:p for p in json.load(open('data/p1a_marks_v1.json'))}
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def layer(n,col):
    l=r3.Layer(); l.Name=n; l.Color=col; return f.Layers.Add(l)
Lp=layer('PLAN_1a_side_image',(150,150,150,255)); Lm=layer('MARKS_M0-M48',(0,160,0,255)); Lc=layer('CURVES_through_marks',(255,120,0,255))
m=r3.Mesh()
for p in ((x0,-0.05,z0),(x1,-0.05,z0),(x1,-0.05,z1),(x0,-0.05,z1)): m.Vertices.Add(*p)
m.Faces.AddFace(0,1,2,3); m.Normals.ComputeNormals()
pl=r3.Plane(r3.Point3d(x0,-0.05,z0),r3.Vector3d(1,0,0),r3.Vector3d(0,0,1))
tm=r3.TextureMapping.CreatePlaneMapping(pl,r3.Interval(0,x1-x0),r3.Interval(0,z1-z0),r3.Interval(-1,1)); m.SetTextureCoordinates(tm,r3.Transform(1.0),False)
mat=r3.Material(); mat.Name='plan_1a_side'; mat.DiffuseColor=(255,255,255,255); cwd=os.getcwd(); os.chdir(OUT); mat.SetBitmapTexture('plan_1a_side.png'); os.chdir(cwd)
mi=f.Materials.Add(mat); at=r3.ObjectAttributes(); at.LayerIndex=Lp; at.MaterialIndex=mi; at.MaterialSource=r3.ObjectMaterialSource.MaterialFromObject; at.Name='plan_1a_side'; f.Objects.AddMesh(m,at)
for k,p in P.items():
    at=r3.ObjectAttributes(); at.LayerIndex=Lm; at.Name='%s_%s'%(k,p['g']); f.Objects.AddPoint(r3.Point3d(p['X'],0,p['Z']),at)
def nurbs(Q):
    Q=np.array(Q); k=min(3,len(Q)-1); tck,_=splprep(Q.T,k=k,s=0); t,c,deg=tck; n=len(c[0])
    cv=r3.NurbsCurve(3,False,deg+1,n)
    for i in range(n): cv.Points[i]=r3.Point4d(float(c[0][i]),0.0,float(c[1][i]),1.0)
    for i,v in enumerate(t[1:-1]): cv.Knots[i]=float(v)
    return cv
pt=lambda a,b:[(P['M%d'%i]['X'],P['M%d'%i]['Z']) for i in range(a,b+1)]
segs=[('S1_spline_M0-M13',pt(0,13)),('S2_line_M13-M16',[pt(13,13)[0],pt(16,16)[0]]),('S3_spline_M16-M23',pt(16,23)),('S4_line_M23-M24',pt(23,24)),('S5_step_M24-M25',pt(24,25)),
('S6_spline_M25-M33',pt(25,33)),('S7_spline_M33-M37',pt(33,37)),('S8_spline_M37-M42',pt(37,42)),('S9_step_M42-M45',[pt(42,42)[0],pt(45,45)[0]]),('S10_line_M45-M48',[pt(45,45)[0],pt(48,48)[0]])]
for nm,Q in segs:
    straight=('_line_' in nm) or ('_step_' in nm)
    cv=r3.LineCurve(r3.Point3d(Q[0][0],0,Q[0][1]),r3.Point3d(Q[-1][0],0,Q[-1][1])) if straight else nurbs(Q)
    at=r3.ObjectAttributes(); at.LayerIndex=Lc; at.Name=nm; f.Objects.AddCurve(cv,at)
f.Write('rhino/RoyalCaroline_bulwark_marks_side_v1.3dm',7)
with zipfile.ZipFile('rhino/RoyalCaroline_bulwark_marks_side_v1.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write('rhino/RoyalCaroline_bulwark_marks_side_v1.3dm','RoyalCaroline_bulwark_marks_side_v1.3dm'); z.write(OUT+'/plan_1a_side.png','plan_1a_side.png')
print(os.path.getsize('rhino/RoyalCaroline_bulwark_marks_side_v1.zip')/1e6,'MB')
