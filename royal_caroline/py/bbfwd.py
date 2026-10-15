import sys,json,numpy as np,cv2
sys.path.insert(0,sys.argv[1]); from p5map import *
from PIL import Image, ImageDraw
S=sys.argv[2]; T=np.load(S+'/out/tex_bow.npz'); coh,dens=T['coh'],T['dens']; u0,v0=int(T['u0']),int(T['v0'])
hatch=((dens>0.22)&(coh>0.55)).astype(np.uint8)
cross=((dens>0.30)&(coh<=0.55)).astype(np.uint8)
k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
h=cv2.morphologyEx(hatch,cv2.MORPH_OPEN,k); h=cv2.morphologyEx(h,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
n,lab=cv2.connectedComponents(h)
su,sv=model_to_p5(470,-5); seed=lab[int(sv)-v0,int(su)-u0]; print('seed label',seed)
M=(lab==seed).astype(np.uint8)
M=cv2.morphologyEx(M,cv2.MORPH_CLOSE,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
cs,_=cv2.findContours(M,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)[:,0,:].astype(float)
c=cv2.approxPolyDP(c.astype(np.float32).reshape(-1,1,2),1.5,True)[:,0,:]
X,Z=p5_to_model(c[:,0]+u0,c[:,1]+v0); P=np.c_[X,Z]
json.dump(P.tolist(),open(S+'/out/bb_fwd_plan5.json','w'))
im=Image.open(S+'/a/plan_5_aligned.png').convert('RGB').point(lambda t:110+t*145//255); d=ImageDraw.Draw(im)
d.line([tuple(p) for p in np.r_[c,c[:1]]+[u0,v0]],fill=(0,170,0),width=4)
cur=json.load(open(S+'/out/backbone_contour.json'))['outer']; cur=np.array(cur)
uu,vv=model_to_p5(cur[:,0],cur[:,1]); d.line(list(zip(uu,vv)),fill=(255,0,0),width=2)
im.crop((u0,v0,u0+M.shape[1],v0+M.shape[0])).resize((M.shape[1]*3//4,M.shape[0]*3//4)).save(S+'/bbfwd_ov.png')
print('X %.1f..%.1f Z %.1f..%.1f'%(X.min(),X.max(),Z.min(),Z.max()),len(P))
