import json,numpy as np,sys
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
O,QA=sys.argv[1],sys.argv[2]
fp=json.load(open(O+'/frame_pieces_v6.json'))['pieces']; parts=json.load(open(O+'/parts_v6.json'))
COL={'floor':(0.27,0.43,0.67,.6),'fut1':(0.9,0.55,0.24,.6),'fut2':(0.31,0.63,0.31,.6),'fut3':(0.78,0.27,0.27,.6),'top':(0.59,0.43,0.75,.6),'topU':(0.59,0.43,0.75,.6),'cant':(0.95,0.8,0.1,.8),'hawse':(0.8,0.6,0.0,.8)}
GC={'backbone':(0.35,0.35,0.6,.9),'stern':(0.65,0.42,0.22,.9),'rudder':(0.45,0.2,0.2,.9),'ports':(0.9,0.1,0.1,1),'clamps':(0.1,0.6,0.6,1),'jig':(0.7,0.7,0.7,.35),'decks':(0.75,0.6,0.35,.95)}
def faces(plane,off,th,P):
    out=[]
    for o in ((off,off+th) if plane!='XZ' else (off-th/2,off+th/2)):
        if plane=='YZ': out.append(np.c_[np.full(len(P),o),P[:,0],P[:,1]])
        elif plane=='XZ': out.append(np.c_[P[:,0],np.full(len(P),o),P[:,1]])
        else: out.append(np.c_[P[:,0],P[:,1],np.full(len(P),o)])
    return out
def view(fn,el,az,xl,yl,zl,jig=True,flip=False,dpi=85,size=(14,7)):
    fig=plt.figure(figsize=size); ax=fig.add_subplot(111,projection='3d'); polys=[];cols=[]
    for p in fp:
        P=np.array(p['poly'])[::2]
        if (p['x1']<xl[0]) or (p['x0']>xl[1]): continue
        for f in faces('YZ',p['x0'],p['x1']-p['x0'],P): polys.append(f); cols.append(COL.get(p['piece'],(.5,.5,.5,.6)))
    for p in parts:
        if p['group']=='jig' and not jig: continue
        P=np.array(p['poly'])
        for f in faces(p['plane'],p['off'],p['th'],P): polys.append(f); cols.append(GC[p['group']])
    if flip: polys=[q*[1,1,-1] for q in polys]
    ax.add_collection3d(Poly3DCollection(polys,facecolors=cols,edgecolors=(0,0,0,0.12),linewidths=0.12))
    ax.set_xlim(*xl); ax.set_ylim(*yl); ax.set_zlim(*zl); ax.set_box_aspect((xl[1]-xl[0],yl[1]-yl[0],zl[1]-zl[0]))
    ax.view_init(el,az); ax.set_axis_off(); fig.tight_layout(); fig.savefig(QA+'/'+fn,dpi=dpi); plt.close(fig)
view('v6_decks.png',28,-60,(-60,615),(-90,90),(-12,150),jig=False)


view('v6_decks_mid.png',35,-70,(200,420),(-80,80),(20,120),jig=False,size=(12,8))
