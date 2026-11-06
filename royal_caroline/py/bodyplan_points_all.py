# Reference points on every body-plan station (fwd A1/3: ST01-08, aft A1/2: ST09-18): every 10 mm of arc on the ink centre, a corner point where the top is a straight vertical, a top end point
import numpy as np, json
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
ST=np.load('data/hull_stations_all.npz')
GA=255-np.array(Image.open('plans/plan_1a_aligned.png').convert('L')).astype(float)
GB=255-np.array(Image.open('plans/plan_1b_aligned.png').convert('L')).astype(float)
CFG={'fwd':dict(g=GB,cx=2433.0,zI=1903.0,k=8.65/103.3,side=+1),'aft':dict(g=GA,cx=2385.0,zI=2013.0,k=43.4/521,side=-1)}
def which(n): return 'fwd' if n<=8 else 'aft'
def px(c,Y,Z): return c['cx']+c['side']*np.asarray(Y)/c['k'], c['zI']-(np.asarray(Z)-8.7)/c['k']
def mm(c,x,y): return (x-c['cx'])*c['side']*c['k'], 8.7+(c['zI']-y)*c['k']
def runs_at(c,pc,Np,Tp,half=24,w=6,thr=0.35):
    g=c['g']; off=np.arange(-half,half+1); prof=np.array([np.mean([g[int(round(pc[1]+Np[1]*o+Tp[1]*t)),int(round(pc[0]+Np[0]*o+Tp[0]*t))] for t in range(-w,w+1)]) for o in off])
    if prof.max()<60: return [],off,prof
    idx=np.where(prof>thr*prof.max())[0]; rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1)
    return [ (off[r]*prof[r]).sum()/prof[r].sum() for r in rs],off,prof
def station(n):
    c=CFG[which(n)]; v=ST[f'ST{n:02d}'][:,1:]; s=np.r_[0,np.cumsum(np.hypot(*np.diff(v,axis=0).T))]
    X,Y=px(c,v[:,0],v[:,1]); P=np.c_[X,Y]
    # corner: trace the ink downward from the top end
    x0,y0=X[-1],Y[-1]; xs=[];prev=x0; rows=range(int(y0)+4,int(y0)+4+700)
    for r in rows:
        row=c['g'][r,int(prev)-7:int(prev)+8]
        if row.max()<60: xs.append(prev); continue
        m=row>0.5*row.max(); idx=np.where(m)[0]; rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); rr=min(rs,key=lambda q:abs(q.mean()-7))
        if len(rr)<=8: prev=int(prev)-7+(rr*row[rr]).sum()/row[rr].sum() if False else (int(prev)-7+(rr*row[rr]).sum()/row[rr].sum())
        xs.append(prev)
    xs=np.array(xs); ref=np.median(xs[:12]); dev=np.abs(xs-ref)>1.5
    first=np.argmax(dev) if dev.any() else len(xs); vlen=first*c['k']
    corner=None
    if vlen>=3.0 and n<=4:   # stations 5-8 run too close together to trace; they are slanted at the top anyway
        rc=list(rows)[first]; corner=(ref,rc)
    return c,v,s,P,corner,x0,y0
def points(n):
    c,v,s,P,corner,x0,y0=station(n); g=c['g']
    if corner: # arc where the spline reaches the corner row
        jc=np.argmin(abs(P[:,1]-corner[1])); sc=s[jc]; tgt=[t for t in np.arange(0,sc,10.0) if sc-t>3.0]
    else: sc=s[-1]; tgt=[t for t in np.arange(0,sc-3.0,10.0)]+[sc-1.5]
    res=[]
    for t in tgt:
        j=min(np.searchsorted(s,t),len(s)-1); a=max(j-30,0); b=min(j+30,len(s)-1)
        T=P[b]-P[a]; T/=np.linalg.norm(T); N=np.array([-T[1],T[0]]); cand,_,_=runs_at(c,P[j],N,T)
        res.append((j,N,cand))
    singles=[cd[0] for _,_,cd in res if len(cd)==1]; med=np.median(singles) if singles else 0.0
    out=[]
    for j,N,cand in res:
        o=min(cand,key=lambda q:abs(q-med)) if cand else med
        out.append(P[j]+N*o)
    out=np.array(out); Ym,Zm=mm(c,out[:,0],out[:,1]); pts=list(zip(Ym,Zm))
    if corner:
        yc,zc=mm(c,corner[0],corner[1]); pts.append((yc,zc)); r=int(y0)+4
        while c['g'][r-1,int(corner[0])-3:int(corner[0])+4].max()>60 and r>int(y0)-80: r-=1
        ye,ze=mm(c,corner[0],r+1); pts.append((yc,ze))
    return pts,bool(corner),med*c['k']
if __name__=='__main__':
    allp={}
    for n in range(1,19):
        pts,cr,med=points(n); allp[n]=dict(points=[[round(a,2),round(b,2)] for a,b in pts],straight_top=cr)
        print(f'ST{n:02d}: {len(pts)} pts, straight top={cr}, bias {med:+.2f} mm, Z {pts[0][1]:.1f}..{pts[-1][1]:.1f}')
    # station 6 must stay inside station 7 (min 0.3 mm)
    from shapely.geometry import LineString,Point
    L7=LineString(allp[7]['points']); inside=Point(0,60); fixed=0
    for q in allp[6]['points']:
        pass
    p6=[]
    for y,z in allp[6]['points']:
        P=Point(y,z); d=L7.distance(P)
        if d<0.3 or LineString([(0,60),(y,z)]).crosses(L7):
            n0=L7.interpolate(L7.project(P)); vx,vz=y-n0.x,z-n0.y; nn=np.hypot(vx,vz)
            ux,uz=(-(vx)/nn,-(vz)/nn) if nn>1e-6 else (-1,0)
            if LineString([(0,60),(y,z)]).crosses(L7) or nn<1e-6: ux,uz=(-(vx)/nn,-(vz)/nn) if nn>1e-6 else (-1,0)
            y,z=n0.x+ux*0.3,n0.y+uz*0.3; fixed+=1
        p6.append([round(y,2),round(z,2)])
    allp[6]['points']=p6; print('ST06 points moved inward of ST07:',fixed)
    json.dump(allp,open('data/bodyplan_points_v1.json','w'),indent=0)
