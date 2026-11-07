# 3dm for the builder: plan_4a top view as a horizontal picture plane at deck level (Z=101) registered as before (C=555.0 at px 7424, scale 11.75 px/mm, centre line ym), with the 5 plane splines, rabbet, frame 1 front, to draw the top line
import os,json,zipfile,numpy as np,rhino3dm as r3
from PIL import Image; Image.MAX_IMAGE_PIXELS=None
from scipy.ndimage import map_coordinates
B='/root/.claude/uploads/db230f8a-8640-51de-bf4e-53423595c88f/'; S=11.75; ym=lambda x:1061.7-0.00136*x
im=np.array(Image.open(B+'d86cb433-plan_4a.tif').convert('L')).astype(float)
x0,x1,y0,y1=500,575,-3,62; res=0.085
Xg=x0+(np.arange(int((x1-x0)/res))+.5)*res; Yg=y1-(np.arange(int((y1-y0)/res))+.5)*res; XX,YY=np.meshgrid(Xg,Yg)
px=7424+(XX-555.0)*S; py=ym(px)-YY*S
W=map_coordinates(im,[py,px],order=1,cval=255); os.makedirs('rhino/deckplan_ref',exist_ok=True)
Image.fromarray(W.astype(np.uint8)).save('rhino/deckplan_ref/plan_4a_deck.png',optimize=True)
src=r3.File3dm.Read('rhino/RoyalCaroline_bow_rabbet_and_plane_sketch_v3.3dm'); f=r3.File3dm(); f.Settings.ModelUnitSystem=r3.UnitSystem.Millimeters
LI={}
for i,l in enumerate(src.Layers):
    n=r3.Layer(); n.Name=l.Name; n.Color=l.Color; n.Visible=l.Visible; LI[i]=f.Layers.Add(n)
for o in src.Objects:
    a=o.Attributes; a.LayerIndex=LI[a.LayerIndex]; f.Objects.Add(o.Geometry,a)
l=r3.Layer(); l.Name='DECK_PLAN_4a_top_view_Z101'; l.Color=(120,120,120,255); Lp=f.Layers.Add(l)
Z=101.0; m=r3.Mesh()
for p in ((x0,y0,Z),(x1,y0,Z),(x1,y1,Z),(x0,y1,Z)): m.Vertices.Add(*p)
m.Faces.AddFace(0,1,2,3); m.Normals.ComputeNormals()
pl=r3.Plane(r3.Point3d(x0,y0,Z),r3.Vector3d(1,0,0),r3.Vector3d(0,1,0)); tm=r3.TextureMapping.CreatePlaneMapping(pl,r3.Interval(0,x1-x0),r3.Interval(0,y1-y0),r3.Interval(-1,1)); m.SetTextureCoordinates(tm,r3.Transform(1.0),False)
mat=r3.Material(); mat.Name='plan_4a_deck'; mat.DiffuseColor=(255,255,255,255); cwd=os.getcwd(); os.chdir('rhino/deckplan_ref'); mat.SetBitmapTexture('plan_4a_deck.png'); os.chdir(cwd)
mi=f.Materials.Add(mat); at=r3.ObjectAttributes(); at.LayerIndex=Lp; at.MaterialIndex=mi; at.MaterialSource=r3.ObjectMaterialSource.MaterialFromObject; at.Name='plan_4a_deck'; f.Objects.AddMesh(m,at)
f.Write('rhino/RoyalCaroline_bow_planes_with_deck_plan_v1.3dm',7)
with zipfile.ZipFile('rhino/RoyalCaroline_bow_planes_with_deck_plan_v1.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.write('rhino/RoyalCaroline_bow_planes_with_deck_plan_v1.3dm','RoyalCaroline_bow_planes_with_deck_plan_v1.3dm'); z.write('rhino/deckplan_ref/plan_4a_deck.png','plan_4a_deck.png')
print(os.path.getsize('rhino/RoyalCaroline_bow_planes_with_deck_plan_v1.zip')/1e6,'MB',len(f.Objects))
