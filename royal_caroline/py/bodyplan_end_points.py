# true ends of the forward station lines in the ORIGINAL body plan (plan_1b): follow the ink from the approved first point towards the keel wall until it meets the vertical keel/stem outline; Z also expressed relative to the ink row of the nearest WL line
import sys,json,numpy as np
sys.path.insert(0,'py')
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
import bodyplan_points_all as B, line_follow as LF
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
cf=B.CFG['fwd']; g=B.GB; C=json.load(open('data/bodyplan_splines_v1.json')); out={}
fig,axs=plt.subplots(2,4,figsize=(20,12)); im=Image.open('plans/plan_1b_aligned.png').convert('RGB')
for n in range(1,9):
    p0=np.array(C[str(n)]['points'][0]); p1=np.array(C[str(n)]['points'][1])
    a=np.array([B.px(cf,p0[0],p0[1])]).ravel(); b=np.array([B.px(cf,p1[0],p1[1])]).ravel()
    d=a-b                                                  # towards the keel (px)
    pts=LF.follow(g,float(a[0]),float(a[1]),d[0],d[1],max_steps=140,hw=3,miss_max=4,stop_wide=9)
    e=pts[-1]; Y=(e[0]-cf['cx'])*cf['k']/cf['side']; Z=8.7+(cf['zI']-e[1])*cf['k']
    out[n]=dict(first=[float(p0[0]),float(p0[1])],end_px=[float(e[0]),float(e[1])],end_YZ=[round(float(Y),2),round(float(Z),2)])
    print('station %d: first (%.2f,%.2f) -> ink end (Y %.2f, Z %.2f)  drop %.2f mm'%(n,p0[0],p0[1],Y,Z,p0[1]-Z))
    ax=axs.ravel()[n-1]; box=(int(a[0])-120,int(a[1])-90,int(a[0])+60,int(a[1])+110); ax.imshow(im.crop(box),extent=(box[0],box[2],box[3],box[1])); ax.plot(pts[:,0],pts[:,1],'r-',lw=.8); ax.plot([a[0]],[a[1]],'o',mfc='none',mec='b',ms=8); ax.plot([e[0]],[e[1]],'x',color='lime',ms=10,mew=2); ax.set_title('st %d  end Y %.2f Z %.2f'%(n,Y,Z)); ax.axis('off')
json.dump(out,open('data/bodyplan_ends_v1.json','w')); fig.savefig('qa/bodyplan_ends_v1.png',dpi=60,bbox_inches='tight')
