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
    # straight vertical top (ST01-03): trace the ink centre down from the ink top, corner = where it leaves the straight line
    corner=None; top=None; x0,y0=X[-1],Y[-1]
    if n<=2:
        g=c['g']; rows=np.arange(int(y0)-60,int(y0)+260); prev=None; cs=[]; XG={1:3014.0,2:3087.0}[n]; x0=XG
        for r in rows:
            ref=prev if prev is not None else x0
            w=g[r,int(ref)-9:int(ref)+10]; idx=np.where(w>90)[0]
            if len(idx)==0: cs.append(np.nan); continue
            rs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); rr=min(rs,key=lambda q:abs(q.mean()-9))
            if len(rr)>9 or (prev is None and abs(rr.mean()-9)>7): cs.append(np.nan); continue
            cc=int(ref)-9+(rr*w[rr]).sum()/w[rr].sum(); cs.append(cc); prev=cc
        cs=np.array(cs); ok=np.where(~np.isnan(cs))[0]; i0=ok[0]; seg=ok[(ok>=i0+25)&(ok<i0+90)]
        fit=np.array([0.0,np.median(cs[seg])]); dev=np.abs(cs-np.polyval(fit,rows))>1.5
        first=next(i for i in ok if i>i0+30 and dev[ok[ok>=i][:10]].all()); corner=(float(np.polyval(fit,rows[first])),int(rows[first])); top=(float(np.polyval(fit,rows[i0])),int(rows[i0]))
    return c,v,s,P,corner,x0,y0,top
def points(n):
    c,v,s,P,corner,x0,y0,top=station(n); g=c['g']
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
        yc,zc=mm(c,corner[0],corner[1]); pts.append((yc,zc)); ye,ze=mm(c,top[0],top[1]); pts.append((ye,ze))
    return pts,bool(corner),med*c['k']
if __name__=='__main__':
    allp={}
    for n in range(1,19):
        pts,cr,med=points(n)
        if n==1: pts=[tuple(r) for r in np.loadtxt('data/st01_points_20mm.csv',delimiter=',',skiprows=1)[:,1:]]   # approved version
        allp[n]=dict(points=[[round(a,2),round(b,2)] for a,b in pts],straight_top=cr)
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
