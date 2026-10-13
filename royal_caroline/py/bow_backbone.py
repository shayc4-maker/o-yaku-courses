# Rebuild forward backbone pieces following the lines actually drawn in plan_5 (A3/3)
import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import section, O
from joints import P as JP, Zb, FX
from shapely.geometry import Polygon, LineString, box, Point
from shapely.ops import split, unary_union, linemerge
from scipy.interpolate import UnivariateSpline
L=json.load(open(O+'/bowlines_raw.json')); pr=json.load(open(O+'/profile1a.json'))
parts=json.load(open(O+'/parts_v4.json'))
def ln(i,smooth=0.15):
    P=np.array(L[i]['pts']); P=P[np.argsort(P[:,1])]
    # smooth X(Z)
    z=P[:,1]; _,u=np.unique(np.round(z,2),return_index=True); P=P[u]
    s=UnivariateSpline(P[:,1],P[:,0],s=len(P)*smooth**2); zz=np.linspace(P[0,1],P[-1,1],60)
    return np.c_[s(zz),zz]
l3,l5,l7,l9,l10,l12,l13,l15=[ln(i) for i in (3,5,7,9,10,12,13,15)]
# l10,l15,l12 are better parametrised along X
def lnx(i,smooth=0.15):
    P=np.array(L[i]['pts']); P=P[np.argsort(P[:,0])]; _,u=np.unique(np.round(P[:,0],2),return_index=True); P=P[u]
    s=UnivariateSpline(P[:,0],P[:,1],s=len(P)*smooth**2); xx=np.linspace(P[0,0],P[-1,0],60); return np.c_[xx,s(xx)]
l10=lnx(10); l15=lnx(15)
def xat(line,z): return float(np.interp(z,line[:,1],line[:,0]))
def ext(Lp,a=30,b=30):
    d0=Lp[0]-Lp[3]; d0/=np.linalg.norm(d0); d1=Lp[-1]-Lp[-4]; d1/=np.linalg.norm(d1)
    return np.r_[[Lp[0]+d0*a],Lp,[Lp[-1]+d1*b]]
BW=2.65; HOG=JP['HOG']
# ---------- forward region outline
old=unary_union([Polygon(p['poly']).buffer(0) for p in parts if p['name'] in ('STEM','GRIPE','KNEE_OF_HEAD','DEADWOOD_FWD','KEEL_FWD')])
x45=FX[-1]+JP['SIDED_FR']+0.5
# inner boundary forward of frame 45: line 3 -> stem aft face (straight to line 13) -> line 13 -> top edge -> line 9 (down to l15) -> l15 -> l12 top
l3c=l3[l3[:,0]>=x45-1]
inner=np.r_[l3c,[[553.9,84.1]],l13[l13[:,1]>84.2],[[l9[-1,0],l9[-1,1]]]]
l9u=l9[l9[:,1]>=l15[0,1]][::-1]                    # from top down to knee-top junction
outer12=np.array(L[12]['pts']); outer12=outer12[np.argsort(-outer12[:,1])]  # from top downwards
# head-top cut: from l15 end to line 12 (connect to nearest point of line 12 with Z>=l15 end)
k=np.argmin(np.hypot(outer12[:,0]-l15[-1,0],outer12[:,1]-l15[-1,1])+ (outer12[:,1]<l15[-1,1])*50)
cap=np.r_[inner,l9u,l15,outer12[k:]]
so=np.array(pr['stem_outer']); so=so[so[:,1]<outer12[-1,1]+0.5]; so=so[np.argsort(-so[:,1])]
so=so[so[:,0]>495]
H=lambda x: float(max(section(min(x,528.0),kind='pchip')[0,1],0))+HOG
hx=np.linspace(461.0,x45,40); hline=np.c_[hx,[H(x) for x in hx]]
reg=Polygon(np.r_[hline,[[x45,H(x45)]],[[x45,float(np.interp(x45,l3[:,0],l3[:,1]))]],cap,so,[[495,-9.37],[461.0,-9.37]]]).buffer(0)
if reg.geom_type!='Polygon': reg=max(reg.geoms,key=lambda g:g.area)
reg=reg.intersection(box(461,-9.37,700,200))
# keep the keel band aft of the scarf in the keel; region above Z=HOG aft of 491.5 is fwd deadwood
# ---------- cut lines
scarf=np.array([[500.2,HOG+4],[504.5,-7.0],[504.8,-9.6]])          # plan_5 keel/gripe scarf (line 19)
gk=np.r_[l7[l7[:,1]<=63.4],[[580.9,64.8]],[[600,66.5]]]             # gripe top: line 7 + boundary to outer edge
stem_fore=np.r_[l7[l7[:,1]<54],l9[l9[:,1]>=54]]
l5x=ext(l5,25,0); stem_aft=np.r_[l5x[l5x[:,1]<=55],[[548.8,60.3]],[[553.9,84.1]],l13[l13[:,1]>84.2]]
def poly_between(a,b,top_close=True):
    return Polygon(np.r_[a,b[::-1]]).buffer(0)
pieces={}
# keel band (Z<HOG) aft of scarf belongs to keel: handled by caller
below_keel_top=box(400,-20,800,HOG)
scarf_side=Polygon(np.r_[scarf,[[800,-20],[800,200],[scarf[0,0],200]]]).buffer(0)  # region forward of scarf
G=reg.intersection(scarf_side)
# gripe = below gk line
gline=ext(gk,40,60); below_g=Polygon(np.r_[gline,[[gline[-1,0],-50],[gline[0,0],-50]]]).buffer(0)
gripe=G.intersection(below_g)
upper=G.difference(below_g)
# stem polygon: between stem_aft and stem_fore, bottom hook scarf (527.1,25.7)->(535.5,27.2)
sf=ext(stem_fore,25,0)
stem_poly=Polygon(np.r_[stem_aft,[[l9[-1,0]+0.3,l9[-1,1]+3]],sf[::-1]]).buffer(0)
stem=upper.intersection(stem_poly)
rest=upper.difference(stem_poly)
# knee of head = rest forward of stem fore face; split by line 10
fore_side=Polygon(np.r_[ext(stem_fore,30,30),[[800,200],[800,-50]]]).buffer(0)
knee=rest.intersection(fore_side); aft_rest=rest.difference(fore_side)
l10e=ext(l10,3,30); above10=Polygon(np.r_[l10e,[[l10e[-1,0],300],[l10e[0,0],300]]]).buffer(0)
knee_lo=knee.difference(above10); knee_up=knee.intersection(above10)
apron=aft_rest
# fwd deadwood: region of reg aft of scarf above HOG
dwf=reg.difference(scarf_side).intersection(box(400,HOG,800,200))
keel_fwd_end=reg.difference(scarf_side).intersection(below_keel_top)
def clean(g,minA=2.0):
    if g.is_empty: return g
    if g.geom_type=='Polygon': return g
    gs=[q for q in g.geoms if q.geom_type=='Polygon' and q.area>minA]
    return max(gs,key=lambda q:q.area) if len(gs)==1 else unary_union(gs)
out=dict(GRIPE=clean(gripe),STEM=clean(stem),KNEE_OF_HEAD_LOWER=clean(knee_lo),KNEE_OF_HEAD_UPPER=clean(knee_up),
         APRON=clean(apron),DEADWOOD_FWD=clean(dwf),KEEL_FWD_TIP=clean(keel_fwd_end))
l5u=ext(l5,0,40); l5u=l5u[l5u[:,1]>=40]
inside=Polygon(np.r_[l5u,[[l5u[-1,0],300],[400,300],[400,l5u[0,1]]]]).buffer(0).intersection(box(0,60,800,300))
out={k:clean(g.difference(inside)) for k,g in out.items()}
tot=sum(g.area for g in out.values()); print('region area %.1f  pieces %.1f'%(reg.area,tot))
for k,g in out.items(): print('%-20s %-12s area %7.1f bounds %s'%(k,g.geom_type,g.area,np.round(g.bounds,1)))
json.dump({k:([np.array(g.exterior.coords).tolist()] if g.geom_type=='Polygon' else [np.array(q.exterior.coords).tolist() for q in g.geoms]) for k,g in out.items()},open(O+'/bow_backbone.json','w'))
json.dump({'scarf':scarf.tolist(),'region':np.array(reg.exterior.coords).tolist()},open(O+'/bow_backbone_meta.json','w'))
