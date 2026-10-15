import sys,json,numpy as np
sys.path.insert(0,sys.argv[1]); from hull import section, O
from shapely.geometry import Polygon, LineString, box
from shapely.ops import split
d=json.load(open(O+'/frame_parts.json'))
JOINTS={'A':[0.33,0.66],'F':[0.50,0.83]}
NAMES={'A':['floor','fut2','top'],'F':['fut1','fut3','top']}
def cutline(P,s,t=9.0):
    u=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]; u/=u[-1]
    p=np.array([np.interp(s,u,P[:,0]),np.interp(s,u,P[:,1])])
    j=np.searchsorted(u,s); a,b=P[max(j-3,0)],P[min(j+3,len(P)-1)]; tg=(b-a)/np.linalg.norm(b-a)
    n=np.array([tg[1],-tg[0]]); 
    if n[0]<0: n=-n
    return LineString([p+n*4,p-n*t])
out=[]; problems=[]
for prt in d['parts']:
    F=Polygon(prt['poly']).buffer(0); xm=(prt['x0']+prt['x1'])/2; P=section(xm,kind='pchip')
    geoms=[F]
    lines=[]
    for s in JOINTS[prt['layer']]:
        L=cutline(P,s); lines+= [L, LineString(np.array(L.coords)*[-1,1])]
    if prt['layer']=='F': lines.append(LineString([(0,-50),(0,400)]))
    for L in lines:
        new=[]
        for g in geoms:
            r=split(g,L); new+=list(r.geoms)
        geoms=new
    geoms=[g for g in geoms if g.area>0.5]
    # classify by side and girth position
    def key(g):
        c=g.representative_point(); side='S' if c.x>0 else 'P'
        # girth fraction of nearest outer point
        u=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]; u/=u[-1]
        dd=np.hypot(P[:,0]-abs(c.x),P[:,1]-c.y); return side,u[np.argmin(dd)]
    exp=3 if prt['layer']=='A' else 4   # A: floor + 2 arms*2 =5 ; F: 6
    nexp=5 if prt['layer']=='A' else 6
    if len(geoms)!=nexp: problems.append((prt['frame'],prt['layer'],len(geoms)))
    for g in geoms:
        side,s=key(g); js=JOINTS[prt['layer']]
        idx=0 if s<js[0] else (1 if s<js[1] else 2)
        nm=NAMES[prt['layer']][idx]
        if nm=='floor': side='C'
        out.append(dict(frame=prt['frame'],layer=prt['layer'],piece=nm,side=side,x0=prt['x0'],x1=prt['x1'],
                        poly=np.array(g.exterior.coords).tolist(),area=g.area))
print('pieces',len(out),'problems',problems[:10],len(problems))
# max piece length
L=[max(np.ptp(np.array(o['poly']),axis=0)) for o in out]; print('max piece extent %.1f mm, min %.1f'%(max(L),min(L)))
json.dump(dict(pieces=out,joints=JOINTS),open(O+'/frame_pieces.json','w'))
