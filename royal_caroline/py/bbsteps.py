import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
S=sys.argv[2]; T=np.load(S+'/out/tex_bow.npz'); coh,dens=T['coh'],T['dens']; u0,v0=int(T['u0']),int(T['v0'])
hatch=((dens>0.22)&(coh>0.55)).astype(np.uint8)
cross=((dens>0.30)&(coh<=0.55)).astype(np.uint8)
cross=cv2.morphologyEx(cross,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9)))
n,lab,st,cen=cv2.connectedComponentsWithStats(cross)
blocks=[]
for i in range(1,n):
    x,y,w,h,A=st[i]
    if A<600 or w>120 or h>160: continue
    m=(lab[y:y+h,x:x+w]==i)
    X0,Zt=p5_to_model(x+u0,y+v0); X1,Zb_=p5_to_model(x+w+u0,y+h+v0)
    if Zt>70 or X0<435: continue
    # bottom edge: per column lowest pixel -> fit line (blocks are drawn along the frame, bottom may slope)
    cols=np.arange(w); bot=np.array([np.where(m[:,j])[0].max() if m[:,j].any() else -1 for j in cols])
    ok=bot>=0; Xb,Zbb=p5_to_model(cols[ok]+x+u0,bot[ok]+y+v0)
    blocks.append(dict(x0=float(X0),x1=float(X1),ztop=float(Zt),zbot=float(Zb_),bottom=np.c_[Xb,Zbb].tolist()))
blocks.sort(key=lambda b:b['x0'])
for b in blocks: print('block X %.1f-%.1f  Z %.1f-%.1f'%(b['x0'],b['x1'],b['zbot'],b['ztop']))
json.dump(blocks,open(S+'/out/p5_frame_blocks_fwd.json','w'))
