import sys,json; sys.path.insert(0,'py')
import ezdxf, numpy as np
S='/tmp/claude-0/-home-user-o-yaku-courses/9b1663d1-123c-5304-bded-1182034acdbc/scratchpad/ref/ref_final.dxf'
d=ezdxf.readfile(S);m=d.modelspace()
def pts(e):
    t=e.dxftype()
    if t=='SPLINE': return [(p.x,p.z) for p in e.flattening(0.02)]
    if t=='POLYLINE': return [(v.dxf.location.x,v.dxf.location.z) for v in e.vertices]
def curve(layer):
    out=[]
    for e in m:
        if e.dxf.layer==layer and e.dxftype() in('SPLINE','POLYLINE'):
            p=pts(e)
            if p and len(p)>1: out.append(np.array(p))
    return out
for l in ('01_BODY_OUTER','03_STERN_KNEE','02_KEELSON'):
    cs=curve(l); print(l,len(cs),[ (round(c[:,0].min(),1),round(c[:,0].max(),1)) for c in cs][:60])

def zat(cs,x,tol=0.06):
    r=[]
    for c in cs:
        if c[:,0].min()-tol<=x<=c[:,0].max()+tol:
            o=np.argsort(c[:,0]); r.append(float(np.interp(x,c[o,0],c[o,1])))
    return r
seats=json.load(open('data/backbone_contour_v5.json'))['seats']
G=[c for c in curve('01_BODY_OUTER') if c[:,0].min()>-1 and (c[:,0].max()-c[:,0].min())>0.5]
B=[c for c in curve('03_STERN_KNEE') if c[:,0].min()>-1]
def vv(x,lo,hi):
    r=[]
    for e in m:
        if e.dxf.layer in('01_BODY_OUTER','02_KEELSON','03_STERN_KNEE') and e.dxftype()=='LINE':
            a,b=e.dxf.start,e.dxf.end
            if abs(a.x-b.x)<1e-3 and abs(a.x-x)<.06 and min(a.z,b.z)>=lo-6 and max(a.z,b.z)<=hi+6: r.append((round(min(a.z,b.z),2),round(max(a.z,b.z),2)))
    return r
if __name__=='__main__':
    for i,(a,b,z,dp) in enumerate(seats):
        print(i,'seatz',round(z,2),'| gray@a',[round(v,2) for v in zat(G,a)],'gray@b',[round(v,2) for v in zat(G,b)],'| blue@a',[round(v,2) for v in zat(B,a)],'blue@b',[round(v,2) for v in zat(B,b)])
