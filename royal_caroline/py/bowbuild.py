import sys,json,numpy as np, rhino3dm as r3
sys.path.insert(0,sys.argv[1]); from bowsurf import *
from PIL import Image, ImageDraw
S=sys.argv[2]; PK=O+'/RoyalCaroline_Rhino'
XS=np.r_[np.arange(518,XS1,2.0),[XS1],np.arange(529,560,1.0)]
SEC={}
for x in XS:
    if Zr(x)>=ZTOPB-0.5: continue
    s=section_fit(x)
    if s is not None and len(s)>3: SEC[float(x)]=s
print('sections',len(SEC),'X',min(SEC),max(SEC))
def ycont(z):
    out=[]
    for x,s in sorted(SEC.items()):
        if s[0,1]<=z<=s[-1,1]: out.append((x,float(np.interp(z,s[:,1],s[:,0]))))
    out.append((Xr(z),YR)) if z<=ZTOPB else None
    return np.array(sorted(out))
json.dump({str(k):v.tolist() for k,v in SEC.items()},open(O+'/bow_sections.json','w'))
# ---------- 3dm ----------
m=r3.File3dm(); m.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
def lay(n,c): L=r3.Layer(); L.Name=n; L.Color=(*c,255); return m.Layers.Add(L)
LS=lay('BOW_SECTIONS_every_mm',(0,90,200)); LW=lay('BOW_WATERLINES_check',(200,0,0)); LR=lay('REF_A1-4_waterlines_traced',(255,140,0)); LB=lay('REF_rabbet_A1-1',(0,150,0)); LM=lay('BOW_SURFACE_mesh',(170,170,200)); LST=lay('REF_station1_bodyplan',(120,0,160))
def att(li,n): a=r3.ObjectAttributes(); a.LayerIndex=li; a.Name=n; return a
def pl(pts,li,n):
    m.Objects.AddCurve(r3.PolylineCurve([r3.Point3d(*map(float,p)) for p in pts]),att(li,n))
for x,s in SEC.items():
    for sg in (1,-1): pl([(x,sg*y,z) for y,z in s],LS,f'bowsec_X{x:.1f}')
for n,z in WLZ.items():
    if n=='BASE': continue
    c=ycont(z)
    if len(c)>1:
        for sg in (1,-1): pl([(x,sg*y,z) for x,y in c],LW,f'bowWL_{n}')
for z in (50,60,80,86):
    c=ycont(z)
    if len(c)>1:
        for sg in (1,-1): pl([(x,sg*y,z) for x,y in c],LW,f'bow_Z{z}')
for n,c in wl.items():
    c=c[c[:,0]>500]; pl([(x,y,WLZ[n]) for x,y in c],LR,f'A14_{n}')
zz=np.linspace(ra[0,1],ZTOPB,80); pl([(Xr(z),0,z) for z in zz],LB,'rabbet')
pl([(XS1,y,z) for y,z in S1],LST,'station1')
# mesh (starboard)
xs=sorted(SEC); nz=len(SEC[xs[0]])
mesh=r3.Mesh()
for x in xs:
    for y,z in SEC[x]: mesh.Vertices.Add(float(x),float(y),float(z))
for i in range(len(xs)-1):
    for j in range(nz-1):
        a=i*nz+j; b=(i+1)*nz+j; mesh.Faces.AddFace(a,b,b+1,a+1)
mesh.Normals.ComputeNormals(); m.Objects.AddMesh(mesh,att(LM,'bow_surface_starboard'))
m.Write(PK+'/RoyalCaroline_bow_surface_v1.3dm',8)
json.dump({'Z86':ycont(86).tolist(),'Z50':ycont(50).tolist(),'Z70':ycont(69.5).tolist(),'Z80':ycont(80).tolist()},open(O+'/bow_contours.json','w'))
print('3dm written')
