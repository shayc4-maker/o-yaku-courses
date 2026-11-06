# generic ink-line follower: steps along the tangent and re-centres the ink perpendicular to it
import numpy as np
def follow(g,x,y,dx,dy,max_steps=12000,hw=4,thr=90,step=1.0,stop_wide=14,miss_max=10):
    pts=[(x,y)]; d=np.array([dx,dy],float); d/=np.linalg.norm(d); miss=0
    for _ in range(max_steps):
        p=np.array([x,y])+d*step; n=np.array([-d[1],d[0]])
        prof=[]
        for o in range(-hw,hw+1):
            q=p+n*o; xi,yi=int(round(q[0])),int(round(q[1]))
            if not(0<=yi<g.shape[0] and 0<=xi<g.shape[1]): return np.array(pts)
            prof.append(g[yi,xi])
        prof=np.array(prof,float); idx=np.where(prof>thr)[0]
        if len(idx)==0:
            miss+=1; x,y=p
            if miss>miss_max: break
            pts.append((x,y)); continue
        # run closest to the centre
        runs=np.split(idx,np.where(np.diff(idx)>1)[0]+1); r=min(runs,key=lambda q:abs(q.mean()-hw))
        if len(r)>stop_wide: miss+=1; x,y=p; pts.append((x,y)); 
        else:
            c=(r*prof[r]).sum()/prof[r].sum()-hw; q=p+n*c*0.5; nd=q-np.array([x,y]); nd/=np.linalg.norm(nd); d=0.9*d+0.1*nd; d/=np.linalg.norm(d); x,y=q; miss=0; pts.append((x,y))
        if miss>miss_max: break
    return np.array(pts)
