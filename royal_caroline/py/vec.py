import numpy as np, json, sys
sys.path.insert(0,'py'); from p5map import *
from scipy import ndimage as ndi
from skimage.morphology import skeletonize, binary_closing, disk, remove_small_objects
from shapely.geometry import Polygon, LineString, Point
P=np.load('scan/blue_model.npy')
V=Polygon(json.load(open('out/backbone_contour_v5.json'))['outer'])
R=0.1; X0,Z0=436,-12; W,H=int((614-X0)/R),int((124-Z0)/R)
g=np.zeros((H,W),bool)
c=np.round((P[:,0]-X0)/R).astype(int); r=np.round((P[:,1]-Z0)/R).astype(int)
k=(c>=0)&(c<W)&(r>=0)&(r<H); g[r[k],c[k]]=True
g=binary_closing(g,disk(2)); g=remove_small_objects(g,60)
sk=skeletonize(g)
# remove skeleton near contour
yy,xx=np.nonzero(sk); pts=np.c_[X0+xx*R,Z0+yy*R]
from shapely import distance, points
d=distance(points(pts),V.exterior)
inside=np.array([V.contains(Point(p)) for p in pts[::1]]) if False else None
keep=d>0.45
sk2=np.zeros_like(sk); sk2[yy[keep],xx[keep]]=True
sk2=remove_small_objects(sk2,15,connectivity=2)
# trace into paths
nb=ndi.convolve(sk2.astype(int),np.ones((3,3),int),mode='constant')-1
nb=np.where(sk2,nb,0)
ys,xs=np.nonzero(sk2); S=set(zip(ys,xs))
def nbrs(p):
    y,x=p; return [(y+dy,x+dx) for dy in (-1,0,1) for dx in (-1,0,1) if (dy or dx) and (y+dy,x+dx) in S]
nodes={p for p in S if len(nbrs(p))!=2}
used=set(); paths=[]
def walk(a,b):
    path=[a,b]; prev,cur=a,b
    while cur not in nodes:
        nx=[q for q in nbrs(cur) if q!=prev and (min(cur,q),max(cur,q)) not in used]
        if not nx: break
        used.add((min(cur,nx[0]),max(cur,nx[0]))); prev,cur=cur,nx[0]; path.append(cur)
    return path
for n in nodes:
    for q in nbrs(n):
        e=(min(n,q),max(n,q))
        if e in used: continue
        used.add(e); paths.append(walk(n,q))
# loops without nodes
rem=S-{p for pa in paths for p in pa}
while rem:
    p=rem.pop(); q=nbrs(p)
    if not q: continue
    pa=walk(p,q[0]); paths.append(pa); rem-=set(pa)
lines=[]
for pa in paths:
    a=np.array([(X0+x*R,Z0+y*R) for y,x in pa])
    L=np.hypot(*np.diff(a,axis=0).T).sum()
    if L>0.8: lines.append(LineString(a).simplify(0.05))
print(len(lines),'segments')
json.dump([np.array(l.coords).tolist() for l in lines],open('scan/raw_lines.json','w'))
from PIL import Image, ImageDraw
im=Image.open('a/plan_5_aligned.png').convert('RGB').point(lambda t:140+t*115//255); dr=ImageDraw.Draw(im)
e=np.array(V.exterior.coords); u,v=model_to_p5(e[:,0],e[:,1]); dr.line(list(zip(u,v)),fill=(0,170,0),width=2)
import colorsys
for i,l in enumerate(lines):
    a=np.array(l.coords); u,v=model_to_p5(a[:,0],a[:,1]); col=tuple(int(255*t) for t in colorsys.hsv_to_rgb((i*0.137)%1,1,0.85))
    dr.line(list(zip(u,v)),fill=col,width=3); dr.text((float(u[len(u)//2])+3,float(v[len(v)//2])),str(i),fill=(0,0,0))
u0,v1=model_to_p5(436,-12); u1,v0=model_to_p5(614,124); im.crop((int(u0),int(v0),int(u1),int(v1))).save('scan/vec_ov.png')
