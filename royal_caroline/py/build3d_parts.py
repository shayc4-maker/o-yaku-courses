# 3D parts for the render: keel (deadwood) and keelson from the STEP outlines with the new pockets, frame layers A/F as lofts between their exact face outlines, hull surface patch
import sys,json,numpy as np
sys.path.insert(0,'py')
FR=[int(a) for a in sys.argv[1:]] or list(range(1,13))
sys.argv=[sys.argv[0]]
import frames_batch_2d as F
import step_chain as S
from shapely.geometry import Polygon
from shapely.ops import unary_union
from OCP.gp import gp_Pnt,gp_Vec
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon,BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
D=json.load(open('data/keel_keelson_clean_v1.json')); PK={p['builder']:p for p in D['pockets']}
# ---------- levels override (as in frames_on_pockets_2d)
KT0=F.keel_levels
def levels_for(X):
    for p in PK.values():
        if p['a']-0.02<=X<=p['b']+0.02:
            _,(kb,kt)=KT0(p['X']); return p['keel_floor'],(p['keelson_ceiling'],max(kt,p['keelson_ceiling']+5.0))
    return KT0(X)
F.keel_levels=levels_for
def mesh_of(shape,tol=0.08):
    BRepMesh_IncrementalMesh(shape,tol,False,0.3,True); V=[];T=[]; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        f=TopoDS.Face_s(ex.Current()) if hasattr(TopoDS,'Face_s') else TopoDS.Face(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(f,loc)
        if tri is not None:
            tr=loc.Transformation(); base=len(V); rev=(f.Orientation().name=='TopAbs_REVERSED')
            for i in range(1,tri.NbNodes()+1): p=tri.Node(i).Transformed(tr); V.append((p.X(),p.Y(),p.Z()))
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); T.append((base+a-1,base+(c if rev else b)-1,base+(b if rev else c)-1))
        ex.Next()
    return np.array(V,float),np.array(T,int)
def prism(poly,y0,y1):
    pts=list(poly.exterior.coords)[:-1]; mk=BRepBuilderAPI_MakePolygon()
    for x,z in pts: mk.Add(gp_Pnt(x,y0,z))
    mk.Close(); fc=BRepBuilderAPI_MakeFace(mk.Wire()).Face(); return BRepPrimAPI_MakePrism(fc,gp_Vec(0,y1-y0,0)).Shape()
parts={}
# ---------- keel and keelson from the STEP outlines
sh=S.load(); sol=S.solids(sh)
def chains(C):
    i_end=int(np.argmax(C[:,0])); A=C[:i_end+1]; B=C[i_end:]
    nh=lambda ch: sum(1 for k in range(len(ch)-1) if abs(ch[k,1]-ch[k+1,1])<2e-3 and abs(ch[k,0]-ch[k+1,0])>1.0)
    st,sm=(A,B) if nh(A)>=nh(B) else (B,A)
    f=lambda ch: ch if ch[0,0]<ch[-1,0] else ch[::-1]
    return f(st),f(sm)
ks_step,ks_smooth=chains(S.side_chain(sol[15])[0]); kt_step,kt_smooth=chains(S.side_chain(sol[16])[0])
X0,X1=45.0,540.0
kl=lambda x: np.interp(x,D['keel_line']['X'],D['keel_line']['Z']); sl=lambda x: np.interp(x,D['keelson_line']['X'],D['keelson_line']['Z'])
xs=np.arange(X0,X1+0.01,0.5)
def with_pockets(line,pk,key,top):
    # line(x) outside pockets, key level inside (keel floor / keelson ceiling) -> polyline in x order
    out=[]; i=0; pkl=sorted(pk,key=lambda p:p['a'])
    for x in xs:
        inside=[p for p in pkl if p['a']<=x<=p['b']]
        out.append((x,line(x) if not inside else inside[0][key]))
    # make the walls vertical: insert exact pocket corners
    pts=[]
    for p in pkl:
        pass
    res=[]
    allx=sorted(set(list(xs)+[p['a'] for p in pkl]+[p['b'] for p in pkl]))
    for x in allx:
        ins=[p for p in pkl if p['a']<x<p['b']]
        if x in [p['a'] for p in pkl]:
            p=[q for q in pkl if q['a']==x][0]; res+= [(x,float(line(x))),(x,p[key])]
        elif x in [p['b'] for p in pkl]:
            p=[q for q in pkl if q['b']==x][0]; res+= [(x,p[key]),(x,float(line(x)))]
        else: res.append((x,float(line(x)) if not ins else ins[0][key]))
    return np.array(res)
def smooth_between(ch,lo,hi):
    m=(ch[:,0]>=lo)&(ch[:,0]<=hi); return ch[m]
pk=list(PK.values())
# keelson: upper smooth line + lower line with pockets
low=with_pockets(sl,pk,'keelson_ceiling',False); up=smooth_between(ks_smooth,X0,X1)
if up[0,1]<low[0,1]+0.5: print('warn keelson top below bottom at the west end')
ring=np.vstack([up,low[::-1]]); keelson=Polygon(ring).buffer(0)
# keel: lower smooth line (bottom of the deadwood) + upper line with pockets
upk=with_pockets(kl,pk,'keel_floor',True); lowk=smooth_between(kt_smooth,X0,X1)
ringk=np.vstack([lowk,upk[::-1]]); keel=Polygon(ringk).buffer(0)
print('keelson area %.0f, keel area %.0f, valid %s %s'%(keelson.area,keel.area,keelson.is_valid,keel.is_valid))
for nm,pg in (('KEELSON',keelson),('KEEL_DEADWOOD',keel)):
    geoms=pg.geoms if hasattr(pg,'geoms') else [pg]; V=[];T=[]
    for g in geoms:
        if g.area<5: continue
        v,t=mesh_of(prism(g,-2.65,2.65)); T.extend((t+len(V)).tolist()); V.extend(v.tolist())
    parts[nm]=dict(v=np.array(V),t=np.array(T))
# ---------- frames
def ring_full(half):
    g=unary_union([half.buffer(0.01),F.mirror(half).buffer(0.01)]).buffer(-0.01)
    if hasattr(g,'geoms'): g=max(g.geoms,key=lambda q:q.area)
    return g
def resample(g,N=360):
    c=np.array(g.exterior.coords)[:-1]
    # orientation CCW in (Y,Z)
    a=0.5*np.sum(c[:,0]*np.roll(c[:,1],-1)-np.roll(c[:,0],-1)*c[:,1]); c=c if a>0 else c[::-1]
    k=int(np.argmin(c[:,0]+0.001*c[:,1]*0-1000*(c[:,1]<c[:,1].min()+0.5)*0)); k=int(np.argmin(c[:,1]*1.0+0.0*c[:,0]))  # start at the lowest point
    c=np.roll(c,-k,axis=0); c=np.vstack([c,c[:1]]); s=np.r_[0,np.cumsum(np.hypot(*np.diff(c,axis=0).T))]; t=np.linspace(0,s[-1],N,endpoint=False)
    return np.c_[np.interp(t,s,c[:,0]),np.interp(t,s,c[:,1])]
def wire_at(X,pts):
    mk=BRepBuilderAPI_MakePolygon()
    for y,z in pts: mk.Add(gp_Pnt(X,y,z))
    mk.Close(); return mk.Wire()
def loft(Xa,ra,Xb,rb):
    ts=BRepOffsetAPI_ThruSections(True,True,1e-6); ts.AddWire(wire_at(Xa,ra)); ts.AddWire(wire_at(Xb,rb)); ts.Build(); return ts.Shape()
for b in FR:
    OUR=46-b; xc=F.XF[OUR-1]; faces={}
    for nm,X in (('m',xc-4),('c',xc),('p',xc+4)):
        half,_=F.face_poly(X,X); faces[nm]=(X,resample(ring_full(half)))
    for lay,(ka,kb) in (('A',('m','c')),('F',('c','p'))):
        sh_=loft(faces[ka][0],faces[ka][1],faces[kb][0],faces[kb][1]); v,t=mesh_of(sh_)
        parts['FRAME%02d_%s'%(b,lay)]=dict(v=v,t=t)
        print('frame',b,lay,'triangles',len(t))
np.save('/tmp/claude-0/x/parts3d.npy',parts,allow_pickle=True)
print('parts',len(parts))
