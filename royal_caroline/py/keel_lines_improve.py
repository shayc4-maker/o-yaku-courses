# keel top surface, keelson underside and keelson top: points + interpolating splines (few points, no waves), compared with the STEP lines; 3dm with the plan_1a side view, original lines, new points/curves
import sys,os,json,zipfile,numpy as np; sys.path.insert(0,'py')
from scipy.interpolate import LSQUnivariateSpline,CubicSpline,splprep,splev
from shapely.geometry import Polygon,LineString
import rhino3dm as r3
from PIL import Image
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from p1a_strip import warped
V=json.load(open('data/keel_keelson_v2.json')); PR=json.load(open('data/step44_profiles.json'))
KS=Polygon(max(PR['Boss-Extrude4[4]'],key=lambda q:Polygon(q).area)).buffer(0)
def envup(x):
    l=KS.intersection(LineString([(x,-50),(x,300)])); return np.nan if l.is_empty else max(c[1] for g in (l.geoms if hasattr(l,'geoms') else [l]) for c in g.coords)
X1=np.arange(46.0,526.01,1.0); top=np.array([envup(x) for x in X1]); ok=~np.isnan(top)
DATA={'keel_top':(np.array(V['keel_surface']['X']),np.array(V['keel_surface']['Z'])),'keelson_under':(np.array(V['keelson_spline']['X']),np.array(V['keelson_spline']['Z'])),'keelson_top':(X1[ok],top[ok])}
KN={'keel_top':(35,35,7,495),'keelson_under':(30,30,15,440),'keelson_top':(40,40,20,440)}
PTX=lambda x0,x1:list(np.arange(x0,440,30.0))+list(np.arange(440,500,15.0))+list(np.arange(500,x1,7.0))+[x1]
def curv(xs,zs):
    s=CubicSpline(xs,zs); d1=s(xs,1); d2=s(xs,2); return d2/(1+d1**2)**1.5
def metr(xs,zs):
    k=curv(xs,zs); sc=int((np.diff(np.sign(k[np.abs(k)>1e-4]))!=0).sum()); dk=np.gradient(k,xs); return sc,int((np.diff(np.sign(dk[np.abs(dk)>2e-6]))!=0).sum()),abs(k).max()
NEW={}
for nm,(xs,zs) in DATA.items():
    far,mid,bow,xb=KN[nm]; kn=list(np.arange(xs[0]+far,400,far))+list(np.arange(400,xb,mid))+list(np.arange(xb,xs[-1]-bow/2,bow)); kn=[k for k in kn if xs[0]<k<xs[-1]]
    f=LSQUnivariateSpline(xs,zs,kn,k=3); px=np.array(PTX(xs[0],xs[-1])); pz=f(px); tck,_=splprep(np.c_[px,pz].T,k=3,s=0)
    xx,zz=splev(np.linspace(0,1,4000),tck); g=np.interp(xs,xx,zz); dev=zs-g; m0=metr(xs,zs); m1=metr(xs,g)
    print('%-14s points %d | max dev %.3f mm rms %.3f | sign changes %d->%d, curvature extrema %d->%d, max|k| %.4f->%.4f'%(nm,len(px),abs(dev).max(),dev.std(),m0[0],m1[0],m0[1],m1[1],m0[2],m1[2]),' worst X',int(xs[np.argmax(abs(dev))]))
    NEW[nm]=dict(px=px,pz=pz,xs=xs,zs=zs,g=g,dev=dev,tck=tck)
json.dump({k:dict(points=[[float(a),float(b)] for a,b in zip(v['px'],v['pz'])]) for k,v in NEW.items()},open('data/keel_keelson_points_v1.json','w'),indent=1)
# figure
fig,axs=plt.subplots(4,1,figsize=(15,20),gridspec_kw={'height_ratios':[1.2,1.2,1,1]}); col={'keel_top':'k','keelson_under':'g','keelson_top':'tab:brown'}
for a,(x0,x1,z0,z1,t) in zip(axs[:2],((40,530,-2,50,'side view, whole length'),(455,530,0,50,'bow'))):
    a.imshow(warped((x0,x1),(z0,z1),0.1),cmap='gray',vmin=0,vmax=255,extent=(x0,x1,z0,z1),aspect='equal',alpha=.5)
    for nm,v in NEW.items(): a.plot(v['xs'],v['zs'],color=col[nm],lw=.8,alpha=.5); xx,zz=splev(np.linspace(0,1,2000),v['tck']); a.plot(xx,zz,'-',color=col[nm],lw=1.6,label=nm); a.plot(v['px'],v['pz'],'o',color=col[nm],ms=4)
    a.set_xlim(x0,x1); a.set_ylim(z0,z1); a.grid(alpha=.3); a.legend(fontsize=8); a.set_title(t)
for nm,v in NEW.items(): axs[2].plot(v['xs'],v['dev'],color=col[nm],label=nm)
axs[2].set_title('STEP line minus new spline (mm)'); axs[2].grid(alpha=.3); axs[2].legend()
from scipy.ndimage import uniform_filter1d
for nm,v in NEW.items(): axs[3].plot(v['xs'],uniform_filter1d(curv(v['xs'],v['zs']),9),color=col[nm],lw=.8,alpha=.5); axs[3].plot(v['xs'],curv(v['xs'],v['g']),color=col[nm],lw=1.6)
axs[3].set_ylim(-0.03,0.06); axs[3].set_title('curvature: thin = STEP line (9 mm mean), thick = new spline'); axs[3].grid(alpha=.3)
fig.savefig('qa/keel_keelson_lines_v1.png',dpi=55,bbox_inches='tight')
# 3dm with the plan picture
OUT='rhino/keel_ref'; os.makedirs(OUT,exist_ok=True); x0,x1,z0,z1=30,545,-12,60
Image.fromarray(warped((x0,x1),(z0,z1),0.1).astype(np.uint8)).save(OUT+'/plan_1a_keel.png',optimize=True)
f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def layer(n,c): l=r3.Layer(); l.Name=n; l.Color=c; return f.Layers.Add(l)
Lp=layer('PLAN_1a_side_image',(150,150,150,255)); m=r3.Mesh()
for p in ((x0,-0.05,z0),(x1,-0.05,z0),(x1,-0.05,z1),(x0,-0.05,z1)): m.Vertices.Add(*p)
m.Faces.AddFace(0,1,2,3); m.Normals.ComputeNormals(); pl=r3.Plane(r3.Point3d(x0,-0.05,z0),r3.Vector3d(1,0,0),r3.Vector3d(0,0,1)); tm=r3.TextureMapping.CreatePlaneMapping(pl,r3.Interval(0,x1-x0),r3.Interval(0,z1-z0),r3.Interval(-1,1)); m.SetTextureCoordinates(tm,r3.Transform(1.0),False)
mat=r3.Material(); mat.Name='plan_1a_keel'; mat.DiffuseColor=(255,255,255,255); cwd=os.getcwd(); os.chdir(OUT); mat.SetBitmapTexture('plan_1a_keel.png'); os.chdir(cwd)
mi=f.Materials.Add(mat); at=r3.ObjectAttributes(); at.LayerIndex=Lp; at.MaterialIndex=mi; at.MaterialSource=r3.ObjectMaterialSource.MaterialFromObject; at.Name='plan_1a_keel'; f.Objects.AddMesh(m,at)
def nurbs(tck):
    t,c,k=tck; n=len(c[0]); cv=r3.NurbsCurve(3,False,k+1,n)
    for i in range(n): cv.Points[i]=r3.Point4d(float(c[0][i]),0.0,float(c[1][i]),1.0)
    for i,v in enumerate(t[1:-1]): cv.Knots[i]=float(v)
    return cv
names={'keel_top':'KEEL_top_surface','keelson_under':'KEELSON_underside_seat','keelson_top':'KEELSON_top'}
for nm,v in NEW.items():
    lo=layer(names[nm]+'_NEW_curve',(0,160,0,255)); a=r3.ObjectAttributes(); a.LayerIndex=lo; a.Name=names[nm]+'_NEW'; f.Objects.AddCurve(nurbs(v['tck']),a)
    lp=layer(names[nm]+'_NEW_points',(0,160,0,255))
    for i,(x,z) in enumerate(zip(v['px'],v['pz'])): a=r3.ObjectAttributes(); a.LayerIndex=lp; a.Name='%s_P%d X%.1f Z%.2f'%(names[nm],i+1,x,z); f.Objects.AddPoint(r3.Point3d(x,0,z),a)
    lr=layer(names[nm]+'_STEP_original',(200,0,0,255)); a=r3.ObjectAttributes(); a.LayerIndex=lr; a.Name=names[nm]+'_STEP'; f.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(x,0,z) for x,z in zip(v['xs'],v['zs'])]),a)
f.Write('rhino/RoyalCaroline_keel_keelson_lines_v1.3dm',7)
with zipfile.ZipFile('rhino/RoyalCaroline_keel_keelson_lines_v1.zip','w',zipfile.ZIP_DEFLATED) as z: z.write('rhino/RoyalCaroline_keel_keelson_lines_v1.3dm','RoyalCaroline_keel_keelson_lines_v1.3dm'); z.write(OUT+'/plan_1a_keel.png','plan_1a_keel.png')
